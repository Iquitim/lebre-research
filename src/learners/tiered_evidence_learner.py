from typing import Dict, Any, Set, List, Optional, Tuple
import numpy as np
from .stabilized_learner import StabilizedSparseLearner
from ..policies.base import BaseProbePolicy
from ..utils.accounting import ResourceTracker

class TieredEvidenceLearner(StabilizedSparseLearner):
    """
    TieredEvidenceLearner for EXP-0006:
    Evaluates tiered candidate evidence-rate allocation under matched budget (10,000 probes)
    and compute <= 25% of Dense.

    Frozen components:
    - Sparse NLMS (mu=0.5, eps=1e-6)
    - K_max = 10 (structural slack = 5)
    - n_min = 8, theta_promote = 0.40 (safe fixed evidence rule)
    - Age-normalized victim scoring (tau_mature = 50, grace = 15, swap = 0.05)
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
        victim_strategy: str = "age_normalized",
        tau_mature: int = 50,
        cooldown_steps: int = 0,
        g_starve: int = 100,
        k_max: Optional[int] = None
    ):
        super().__init__(
            d=d,
            initial_support=initial_support,
            probe_policy=probe_policy,
            q=q,
            mu=mu,
            eps=eps,
            n_min=n_min,
            theta_promote=theta_promote,
            grace_period=grace_period,
            swap_threshold=swap_threshold,
            victim_strategy=victim_strategy,
            tau_mature=tau_mature,
            cooldown_steps=cooldown_steps,
            k_max=k_max
        )
        self.g_starve = g_starve
        self.total_flops = 0

        # Candidate probe timing and gap tracking
        self.last_probed_step: Dict[int, int] = {}
        self.true_interprobe_gaps: List[int] = []
        self.noise_interprobe_gaps: List[int] = []
        self.true_starvation_events = 0

        # Regime 2 true candidate detailed tracking
        self.r2_probes_count: Dict[int, int] = {}
        self.r2_time_to_n: Dict[int, Dict[int, int]] = {} # feat -> {N: step}
        self.r2_first_probe_step: Dict[int, int] = {}
        self.r2_promotion_step: Dict[int, int] = {}
        self.r2_mature_step: Dict[int, int] = {}

        # Aggregate counts
        self.probes_to_omitted_true = 0
        self.probes_to_noise = 0
        self.steps_with_omitted_true = 0
        self.steps_with_noise_candidates = 0

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
        
        self.ages += 1
        self.updates += 1
        
        curr_active_k = len(self.support)
        self.current_step += 1
        
        # Check feature maturation for R2 tracking
        if true_support is not None:
            for idx, feat in enumerate(self.support):
                if feat in true_support and self.current_step > 1000:
                    if feat not in self.r2_mature_step:
                        # Consider feature matured if weight magnitude >= 0.50 or updates >= 50
                        if abs(self.weights[idx]) >= 0.50 or self.updates[idx] >= self.tau_mature:
                            self.r2_mature_step[feat] = self.current_step

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
        
        # Track omitted true candidates vs noise
        omitted_true = set()
        if true_support is not None:
            omitted_true = set(true_support) - active_set
            if len(omitted_true) > 0:
                self.steps_with_omitted_true += 1
            if (self.d - len(active_set) - len(omitted_true)) > 0:
                self.steps_with_noise_candidates += 1

        # 4. Correlation updates (Welford) & Inter-Probe Gap Accounting
        for c in candidates:
            # Check inter-probe gap
            if c in self.last_probed_step:
                gap = self.current_step - self.last_probed_step[c]
                if c in omitted_true:
                    self.true_interprobe_gaps.append(gap)
                    if gap > self.g_starve:
                        self.true_starvation_events += 1
                else:
                    self.noise_interprobe_gaps.append(gap)
            self.last_probed_step[c] = self.current_step

            if c in omitted_true:
                self.probes_to_omitted_true += 1
            else:
                self.probes_to_noise += 1

            # R2 true feature observation tracking
            if true_support is not None and c in true_support and self.current_step > 1000:
                if c not in self.r2_first_probe_step:
                    self.r2_first_probe_step[c] = self.current_step
                self.r2_probes_count[c] = self.r2_probes_count.get(c, 0) + 1
                obs_n = self.r2_probes_count[c]
                if obs_n in (1, 2, 3, 4, 5):
                    if c not in self.r2_time_to_n:
                        self.r2_time_to_n[c] = {}
                    if obs_n not in self.r2_time_to_n[c]:
                        self.r2_time_to_n[c][obs_n] = self.current_step - 1000

            # Welford update
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
        # Accounting for tier policy event updates: ~4 FLOPs per probed candidate
        policy_flops = 4 * num_probed
        
        if hasattr(self.probe_policy, "on_probes_evaluated"):
            self.probe_policy.on_probes_evaluated(candidates, cand_stats, active_set)
            
        # 5. Structural Promotion / Swap Evaluation (Frozen baseline n_min=8, theta=0.40)
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
        readiness_flops = 4 * num_probed
        
        if num_probed > 0:
            # Check eligibility: n >= n_min and |mean| >= theta_promote
            eligible_cands = [c for c in candidates if self.cand_n[c] >= self.n_min and abs(self.cand_mean[c]) >= self.theta_promote]
            
            if eligible_cands:
                best_cand = max(eligible_cands, key=lambda c: abs(self.cand_mean[c]))
                cand_score = float(abs(self.cand_mean[best_cand]))
                cand_evidence_count = int(self.cand_n[best_cand])
                
                if len(self.support) < self.k_max:
                    # Growth promotion
                    self.support.append(best_cand)
                    self.weights = np.append(self.weights, 0.0)
                    self.ages = np.append(self.ages, 0)
                    self.updates = np.append(self.updates, 0)
                    self.contrib = np.append(self.contrib, 0.0)
                    promoted_feat = best_cand
                    self.last_promotion_step = self.current_step
                    if hasattr(self.probe_policy, "on_promotion"):
                        self.probe_policy.on_promotion(best_cand)
                    if true_support is not None and best_cand in true_support and self.current_step > 1000:
                        self.r2_promotion_step[best_cand] = self.current_step

                else:
                    # Full capacity (K=10): evaluate victim selection
                    tau_evict = max(self.grace_period, self.t_protect)
                    eligible_drops = [idx for idx, age in enumerate(self.ages) if age >= tau_evict]
                    if eligible_drops:
                        victim_scoring_flops = 2 * len(eligible_drops)
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

                            if hasattr(self.probe_policy, "on_eviction"):
                                self.probe_policy.on_eviction(victim_feat)
                            if hasattr(self.probe_policy, "on_promotion"):
                                self.probe_policy.on_promotion(best_cand)
                            if true_support is not None and best_cand in true_support and self.current_step > 1000:
                                self.r2_promotion_step[best_cand] = self.current_step

        total_step_flops = (
            pred_flops
            + norm_flops
            + update_flops
            + screening_flops
            + policy_flops
            + readiness_flops
            + victim_scoring_flops
        )
        self.total_flops += total_step_flops
        
        return {
            "y_hat": y_hat,
            "error": error,
            "flops": total_step_flops,
            "promoted": promoted_feat,
            "promoted_feat": promoted_feat,
            "victim": victim_feat,
            "victim_feat": victim_feat,
            "candidates": candidates,
            "victim_age": victim_age,
            "victim_weight": victim_weight,
            "victim_updates": victim_updates,
            "victim_contrib": victim_contrib,
            "victim_score": victim_score_val,
            "cand_evidence_count": cand_evidence_count,
            "cand_score": cand_score,
            "num_probed": num_probed
        }
