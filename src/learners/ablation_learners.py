import numpy as np
from typing import Dict, Any, Set, List, Optional
from .base import BaseOnlineLearner
from ..policies.base import BaseProbePolicy
from ..utils.accounting import ResourceTracker

class AblationSparseLearner(BaseOnlineLearner):
    """
    Unified implementation for EXP-0001b variants:
    - B0: Failed Baseline (K_max=5, EMA scoring, immediate swap)
    - B1: Slack Only (K_max=10, EMA scoring, capacity cap, no multi-probe)
    - B2: Evidence Only (K_max=5, Welford multi-probe, immediate swap)
    - B3: Slack + Evidence (K_max=10, Welford multi-probe, capacity cap)
    - B4: Slack + Evidence + Maturity Pruning (K_max=10, Welford, explicit pruning)
    """
    def __init__(
        self,
        d: int,
        variant: str,
        initial_support: List[int],
        probe_policy: BaseProbePolicy,
        q: int = 5,
        mu: float = 0.5,
        eps: float = 1e-6,
        # Baseline EMA params
        ema_lambda: float = 0.1,
        # Multi-probe evidence params
        n_min: int = 8,
        theta_promote: float = 0.40,
        # Pruning params
        tau_min: int = 20,
        theta_prune: float = 0.15,
        # Swap / grace params
        grace_period: int = 15,
        swap_threshold: float = 0.05,
        t_protect: int = 0,
        k_max: Optional[int] = None
    ):
        self.d = d
        self.variant = variant
        self.probe_policy = probe_policy
        self.q = q
        self.mu = mu
        self.eps = eps
        
        self.ema_lambda = ema_lambda
        self.n_min = n_min
        self.theta_promote = theta_promote
        self.tau_min = tau_min
        self.theta_prune = theta_prune
        self.grace_period = grace_period
        self.swap_threshold = swap_threshold
        self.t_protect = t_protect
        
        # Configure capacity based on variant or task-capacity matching
        if k_max is not None:
            self.k_max = int(k_max)
            self.support: List[int] = list(initial_support[:self.k_max])
        else:
            if variant in ["B0", "B2"]:
                self.k_max = 5
            elif variant in ["B1", "B3", "B4"]:
                self.k_max = 10
            else:
                raise ValueError(f"Unknown variant: {variant}")
            self.support: List[int] = list(initial_support[:5])
            
        self.use_welford = variant in ["B2", "B3", "B4"]
        self.use_pruning = variant == "B4"
        
        # Active set state
        self.weights = np.zeros(len(self.support), dtype=np.float64)
        self.ages = np.zeros(len(self.support), dtype=np.int32)
        
        # Candidate evidence state
        # EMA for B0, B1
        self.candidate_scores = np.zeros(d, dtype=np.float64)
        # Welford for B2, B3, B4
        self.cand_n = np.zeros(d, dtype=np.int32)
        self.cand_mean = np.zeros(d, dtype=np.float64)
        self.cand_m2 = np.zeros(d, dtype=np.float64)
        self.cand_pos = np.zeros(d, dtype=np.int32)
        self.cand_neg = np.zeros(d, dtype=np.int32)
        self.cand_last_step = np.zeros(d, dtype=np.int32)
        self.current_step = 0
        
        self.total_swaps = 0

    def predict(self, x: np.ndarray) -> float:
        x_sub = x[self.support]
        return float(np.dot(self.weights, x_sub))

    def update(self, x: np.ndarray, y: float, q: Optional[int] = None, true_support: Optional[Set[int]] = None) -> Dict[str, Any]:
        curr_active_k = len(self.support)
        
        # 1. Prediction & Residual
        x_sub = x[self.support]
        y_hat = float(np.dot(self.weights, x_sub))
        error = y - y_hat
        pred_flops = ResourceTracker.dot_product_flops(curr_active_k)
        
        # 2. NLMS update on active weights
        norm_sq = float(np.dot(x_sub, x_sub))
        norm_flops = ResourceTracker.norm_sq_flops(curr_active_k)
        step_factor = (self.mu / (self.eps + norm_sq)) * error
        self.weights += step_factor * x_sub
        update_flops = ResourceTracker.vector_update_flops(curr_active_k) + 3
        
        # Increment age of active features
        self.ages += 1
        
        # 3. Explicit Maturity Pruning (B4 only)
        pruned_feats: List[int] = []
        pruning_flops = 0
        if self.use_pruning:
            pruning_flops = ResourceTracker.pruning_check_flops(curr_active_k)
            # Find mature features with weight magnitude below threshold
            prune_indices = [
                idx for idx in range(len(self.support))
                if self.ages[idx] >= self.tau_min and abs(self.weights[idx]) < self.theta_prune
            ]
            # Prune while keeping at least 1 feature in support
            if prune_indices and len(self.support) > 1:
                # If all would be pruned, preserve the one with largest weight
                if len(prune_indices) == len(self.support):
                    best_w_idx = int(np.argmax([abs(w) for w in self.weights]))
                    prune_indices = [idx for idx in prune_indices if idx != best_w_idx]
                
                # Execute pruning in reverse index order
                for p_idx in sorted(prune_indices, reverse=True):
                    feat = self.support[p_idx]
                    pruned_feats.append(feat)
                    self.support.pop(p_idx)
                    self.weights = np.delete(self.weights, p_idx)
                    self.ages = np.delete(self.ages, p_idx)
                    # Reset candidate stats for pruned feature
                    self.cand_n[feat] = 0
                    self.cand_mean[feat] = 0.0
                    self.cand_m2[feat] = 0.0
                    self.cand_pos[feat] = 0
                    self.cand_neg[feat] = 0
                    self.cand_last_step[feat] = 0
                    self.candidate_scores[feat] = 0.0

        curr_active_k = len(self.support)
        self.current_step += 1
        
        active_set = set(self.support)
        curr_q = self.q if q is None else int(q)
        cand_stats = {
            "n": self.cand_n,
            "mean": self.cand_mean,
            "m2": self.cand_m2,
            "pos": self.cand_pos,
            "neg": self.cand_neg,
            "last_step": self.cand_last_step,
            "current_step": self.current_step
        }
        candidates = self.probe_policy.select_candidates(
            self.d, active_set, curr_q, cand_stats=cand_stats, true_support=true_support
        )
        num_probed = len(candidates)
        
        if self.use_welford:
            # Welford multi-probe correlation updates
            for c in candidates:
                self.cand_n[c] += 1
                val = error * x[c]
                if val > 0:
                    self.cand_pos[c] += 1
                elif val < 0:
                    self.cand_neg[c] += 1
                self.cand_last_step[c] = self.current_step
                delta = val - self.cand_mean[c]
                self.cand_mean[c] += delta / self.cand_n[c]
                delta2 = val - self.cand_mean[c]
                self.cand_m2[c] += delta * delta2
            screening_flops = ResourceTracker.welford_probe_flops(num_probed)
            if hasattr(self.probe_policy, "on_probes_evaluated"):
                self.probe_policy.on_probes_evaluated(candidates, cand_stats, active_set)
        else:
            # Original EMA correlation updates (B0, B1)
            for c in candidates:
                inst_corr = error * x[c]
                self.candidate_scores[c] = (1.0 - self.ema_lambda) * self.candidate_scores[c] + self.ema_lambda * inst_corr
            screening_flops = ResourceTracker.candidate_probe_flops(num_probed)
            
        # 5. Structural Promotion / Swap Evaluation
        promoted_feat: Optional[int] = None
        victim_feat: Optional[int] = None
        victim_age: Optional[int] = None
        victim_weight: Optional[float] = None
        cand_evidence_count = 0
        cand_score = 0.0
        
        if num_probed > 0:
            if self.use_welford:
                # Eligible candidates: probed >= n_min with |mean| >= theta_promote
                eligible_cands = [
                    c for c in candidates
                    if self.cand_n[c] >= self.n_min and abs(self.cand_mean[c]) >= self.theta_promote
                ]
                if eligible_cands:
                    best_cand = max(eligible_cands, key=lambda c: abs(self.cand_mean[c]))
                    cand_score = float(abs(self.cand_mean[best_cand]))
                    cand_evidence_count = int(self.cand_n[best_cand])
                    
                    if len(self.support) < self.k_max:
                        # Growth (incubation slot available)
                        self.support.append(best_cand)
                        self.weights = np.append(self.weights, 0.0)
                        self.ages = np.append(self.ages, 0)
                        promoted_feat = best_cand
                        self.cand_n[best_cand] = 0
                        self.cand_mean[best_cand] = 0.0
                        self.cand_m2[best_cand] = 0.0
                        self.cand_pos[best_cand] = 0
                        self.cand_neg[best_cand] = 0
                        self.cand_last_step[best_cand] = 0
                        if hasattr(self.probe_policy, "on_promotion"):
                            self.probe_policy.on_promotion(best_cand)
                    else:
                        # Capacity full: requires replacing mature feature with smallest |w|
                        tau_evict = max(self.grace_period, self.t_protect)
                        eligible_drops = [idx for idx, age in enumerate(self.ages) if age >= tau_evict]
                        if eligible_drops:
                            drop_idx = min(eligible_drops, key=lambda idx: abs(self.weights[idx]))
                            drop_weight_mag = abs(self.weights[drop_idx])
                            if cand_score > drop_weight_mag + self.swap_threshold:
                                victim_feat = self.support[drop_idx]
                                victim_age = int(self.ages[drop_idx])
                                victim_weight = float(self.weights[drop_idx])
                                promoted_feat = best_cand
                                self.support[drop_idx] = best_cand
                                self.weights[drop_idx] = 0.0
                                self.ages[drop_idx] = 0
                                # Reset evidence
                                self.cand_n[best_cand] = 0
                                self.cand_mean[best_cand] = 0.0
                                self.cand_m2[best_cand] = 0.0
                                self.cand_pos[best_cand] = 0
                                self.cand_neg[best_cand] = 0
                                self.cand_last_step[best_cand] = 0
                                self.cand_n[victim_feat] = 0
                                self.cand_mean[victim_feat] = 0.0
                                self.cand_m2[victim_feat] = 0.0
                                self.cand_pos[victim_feat] = 0
                                self.cand_neg[victim_feat] = 0
                                self.cand_last_step[victim_feat] = 0
                                self.total_swaps += 1
                                if hasattr(self.probe_policy, "on_promotion"):
                                    self.probe_policy.on_promotion(best_cand)
                                if hasattr(self.probe_policy, "on_eviction"):
                                    self.probe_policy.on_eviction(victim_feat)
            else:
                # Original EMA logic for B0 and B1
                best_cand = max(candidates, key=lambda c: abs(self.candidate_scores[c]))
                cand_score = float(abs(self.candidate_scores[best_cand]))
                cand_evidence_count = 1  # single sample EMA
                
                if len(self.support) < self.k_max:
                    # B1 Growth slot available: promote if score > threshold
                    if cand_score > self.swap_threshold:
                        self.support.append(best_cand)
                        self.weights = np.append(self.weights, 0.0)
                        self.ages = np.append(self.ages, 0)
                        promoted_feat = best_cand
                        self.candidate_scores[best_cand] = 0.0
                else:
                    # B0 / B1 Full capacity: swap mature feature
                    eligible_drops = [idx for idx, age in enumerate(self.ages) if age >= self.grace_period]
                    if eligible_drops:
                        drop_idx = min(eligible_drops, key=lambda idx: abs(self.weights[idx]))
                        drop_weight_mag = abs(self.weights[drop_idx])
                        if cand_score > drop_weight_mag + self.swap_threshold:
                            victim_feat = self.support[drop_idx]
                            promoted_feat = best_cand
                            self.support[drop_idx] = best_cand
                            self.weights[drop_idx] = 0.0
                            self.ages[drop_idx] = 0
                            self.candidate_scores[best_cand] = 0.0
                            self.candidate_scores[victim_feat] = 0.0
                            self.total_swaps += 1

        total_flops = pred_flops + norm_flops + update_flops + pruning_flops + screening_flops
        mem_bytes = ResourceTracker.estimate_memory_bytes(
            len(self.support), self.d, self.d, is_welford=self.use_welford, is_extended=self.use_welford
        )

        
        return {
            "prediction": y_hat,
            "error": error,
            "loss": error ** 2,
            "flops": total_flops,
            "probes": num_probed,
            "candidates": candidates,
            "swaps": 1 if (victim_feat is not None) else 0,
            "promotions": 1 if (promoted_feat is not None) else 0,
            "promoted_feat": promoted_feat,
            "victim_feat": victim_feat,
            "victim_age": victim_age,
            "victim_weight": victim_weight,
            "pruned_feats": pruned_feats,
            "cand_evidence_count": cand_evidence_count,
            "cand_score": cand_score,
            "active_params": len(self.support),
            "memory_bytes": mem_bytes
        }

    def get_active_support(self) -> Set[int]:
        return set(self.support)

    def get_parameter_count(self) -> int:
        return len(self.support)
