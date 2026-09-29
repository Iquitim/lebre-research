import numpy as np
from typing import Dict, Any, Set, List, Optional
from .ablation_learners import AblationSparseLearner
from ..policies.base import BaseProbePolicy
from ..utils.accounting import ResourceTracker

class StabilizedSparseLearner(AblationSparseLearner):
    """
    StabilizedSparseLearner for EXP-0004:
    Evaluates maturity-aware eviction rules and promotion cooldown to stabilize newly
    promoted features without blind immunity.

    Victim strategies:
    - 'baseline' (G0, G4): Raw |w_i|
    - 'age_normalized' (G1): |w_i| / min(1, age_i / tau_mature)
    - 'update_normalized' (G2): |w_i| / min(1, updates_i / tau_mature)
    - 'contribution_aware' (G3): EMA(|w_i * x_i|)
    - 'oracle_victim' (G5): Oracle picks noise feature if present, else smallest |w_i|
    """
    def __init__(
        self,
        d: int,
        initial_support: List[int],
        probe_policy: BaseProbePolicy,
        q: int = 5,
        mu: float = 0.5,
        eps: float = 1e-6,
        n_min: int = 8,
        theta_promote: float = 0.40,
        grace_period: int = 15,
        swap_threshold: float = 0.05,
        victim_strategy: str = "baseline",
        tau_mature: int = 50,
        cooldown_steps: int = 0,
        contrib_beta: float = 0.05,
        k_max: Optional[int] = None
    ):
        super().__init__(
            d=d, variant="B3", initial_support=initial_support,
            probe_policy=probe_policy, q=q, mu=mu, eps=eps,
            n_min=n_min, theta_promote=theta_promote,
            grace_period=grace_period, swap_threshold=swap_threshold,
            t_protect=0, k_max=k_max
        )
        self.victim_strategy = victim_strategy
        self.tau_mature = tau_mature
        self.cooldown_steps = cooldown_steps
        self.contrib_beta = contrib_beta

        # Active feature update count and contribution tracking
        self.updates = np.zeros(len(self.support), dtype=np.int32)
        self.contrib = np.zeros(len(self.support), dtype=np.float64)
        self.last_promotion_step = -9999

        # Detailed event logging
        self.victim_events_log: List[Dict[str, Any]] = []
        
        # Feature maturation tracking (feature_id -> {update_count -> |w|})
        self.feature_maturation: Dict[int, Dict[int, float]] = {}

    def update(
        self,
        x: np.ndarray,
        y: float,
        q: Optional[int] = None,
        true_support: Optional[Set[int]] = None
    ) -> Dict[str, Any]:
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
        
        # Increment age and update counts
        self.ages += 1
        self.updates += 1

        # Track contribution EMA only if contribution_aware strategy is active
        if self.victim_strategy == "contribution_aware":
            inst_contrib = np.abs(self.weights * x_sub)
            self.contrib = (1.0 - self.contrib_beta) * self.contrib + self.contrib_beta * inst_contrib
            contrib_flops = 4 * curr_active_k  # mul, abs, lerp
        else:
            contrib_flops = 0
        
        # Record feature maturation checkpoints for active features
        target_checkpoints = (1, 5, 10, 20, 50, 100)
        for idx, feat in enumerate(self.support):
            u = int(self.updates[idx])
            if u in target_checkpoints:
                if feat not in self.feature_maturation:
                    self.feature_maturation[feat] = {}
                if u not in self.feature_maturation[feat]:
                    self.feature_maturation[feat][u] = float(abs(self.weights[idx]))

        curr_active_k = len(self.support)
        self.current_step += 1
        
        # 3. Candidate Selection
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
        
        # 4. Correlation updates (Welford)
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
            
        # 5. Structural Promotion / Swap Evaluation
        promoted_feat: Optional[int] = None
        victim_feat: Optional[int] = None
        victim_age: Optional[int] = None
        victim_weight: Optional[float] = None
        victim_updates: Optional[int] = None
        victim_contrib: Optional[float] = None
        victim_score_val: Optional[float] = None
        cand_evidence_count = 0
        cand_score = 0.0
        victim_scoring_flops = 0
        
        # Check promotion cooldown (G4)
        in_cooldown = (self.current_step - self.last_promotion_step) < self.cooldown_steps
        
        if num_probed > 0 and not in_cooldown:
            eligible_cands = [
                c for c in candidates
                if self.cand_n[c] >= self.n_min and abs(self.cand_mean[c]) >= self.theta_promote
            ]
            if eligible_cands:
                best_cand = max(eligible_cands, key=lambda c: abs(self.cand_mean[c]))
                cand_score = float(abs(self.cand_mean[best_cand]))
                cand_evidence_count = int(self.cand_n[best_cand])
                
                if len(self.support) < self.k_max:
                    # Growth slot available
                    self.support.append(best_cand)
                    self.weights = np.append(self.weights, 0.0)
                    self.ages = np.append(self.ages, 0)
                    self.updates = np.append(self.updates, 0)
                    self.contrib = np.append(self.contrib, 0.0)
                    promoted_feat = best_cand
                    self.last_promotion_step = self.current_step
                    # Reset candidate evidence
                    self.cand_n[best_cand] = 0
                    self.cand_mean[best_cand] = 0.0
                    self.cand_m2[best_cand] = 0.0
                    self.cand_pos[best_cand] = 0
                    self.cand_neg[best_cand] = 0
                    self.cand_last_step[best_cand] = 0
                    if hasattr(self.probe_policy, "on_promotion"):
                        self.probe_policy.on_promotion(best_cand)
                else:
                    # Full capacity (K=10): evaluate victim selection
                    tau_evict = max(self.grace_period, self.t_protect)
                    eligible_drops = [idx for idx, age in enumerate(self.ages) if age >= tau_evict]
                    if eligible_drops:
                        victim_scoring_flops = 2 * len(eligible_drops)
                        # Helper score functions
                        def compute_victim_score(idx: int) -> float:
                            if self.victim_strategy == "baseline":
                                return float(abs(self.weights[idx]))
                            elif self.victim_strategy == "age_normalized":
                                mat_factor = min(1.0, max(1, self.ages[idx]) / float(self.tau_mature))
                                return float(abs(self.weights[idx]) / mat_factor)
                            elif self.victim_strategy == "update_normalized":
                                mat_factor = min(1.0, max(1, self.updates[idx]) / float(self.tau_mature))
                                return float(abs(self.weights[idx]) / mat_factor)
                            elif self.victim_strategy == "contribution_aware":
                                return float(self.contrib[idx])
                            elif self.victim_strategy == "oracle_victim":
                                return float(abs(self.weights[idx]))
                            return float(abs(self.weights[idx]))

                        if self.victim_strategy == "oracle_victim":
                            # Oracle selects a noise feature if present among eligible drops
                            noise_drops = [
                                idx for idx in eligible_drops
                                if (true_support is not None and self.support[idx] not in true_support)
                            ]
                            if noise_drops:
                                drop_idx = min(noise_drops, key=lambda idx: abs(self.weights[idx]))
                            else:
                                drop_idx = min(eligible_drops, key=lambda idx: abs(self.weights[idx]))
                            drop_score = float(abs(self.weights[drop_idx]))
                        else:
                            drop_idx = min(eligible_drops, key=compute_victim_score)
                            drop_score = compute_victim_score(drop_idx)

                        if cand_score > drop_score + self.swap_threshold:
                            victim_feat = self.support[drop_idx]
                            victim_age = int(self.ages[drop_idx])
                            victim_weight = float(self.weights[drop_idx])
                            victim_updates = int(self.updates[drop_idx])
                            victim_contrib = float(self.contrib[drop_idx])
                            victim_score_val = drop_score
                            promoted_feat = best_cand
                            self.last_promotion_step = self.current_step

                            # Log victim event
                            is_v_true = 1 if (true_support is not None and victim_feat in true_support) else 0
                            is_p_true = 1 if (true_support is not None and promoted_feat in true_support) else 0
                            self.victim_events_log.append({
                                "step": self.current_step,
                                "promoted_feat": promoted_feat,
                                "promoted_is_true": is_p_true,
                                "candidate_score": cand_score,
                                "victim_feat": victim_feat,
                                "victim_is_true": is_v_true,
                                "victim_age": victim_age,
                                "victim_updates": victim_updates,
                                "victim_weight": victim_weight,
                                "victim_contrib": victim_contrib,
                                "victim_score": victim_score_val,
                                "is_displacement": 1 if (is_v_true == 1 and is_p_true == 0) else 0
                            })

                            # Execute swap
                            self.support[drop_idx] = best_cand
                            self.weights[drop_idx] = 0.0
                            self.ages[drop_idx] = 0
                            self.updates[drop_idx] = 0
                            self.contrib[drop_idx] = 0.0
                            
                            # Reset evidence for promoted and victim
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

        total_flops = pred_flops + norm_flops + update_flops + contrib_flops + screening_flops + victim_scoring_flops
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
            "victim_updates": victim_updates,
            "victim_contrib": victim_contrib,
            "victim_score": victim_score_val,
            "cand_evidence_count": cand_evidence_count,
            "cand_score": cand_score,
            "in_cooldown": 1 if in_cooldown else 0,
            "active_params": len(self.support),
            "memory_bytes": mem_bytes
        }
