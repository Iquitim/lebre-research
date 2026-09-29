import numpy as np
from typing import Dict, Any, Set, List, Optional, Tuple
from .stabilized_learner import StabilizedSparseLearner
from ..policies.base import BaseProbePolicy
from ..utils.accounting import ResourceTracker

class AdaptiveEvidenceLearner(StabilizedSparseLearner):
    """
    AdaptiveEvidenceLearner for EXP-0005:
    Evaluates adaptive evidence accumulation rules to reduce screening latency
    without reopening false promotions caused by noise.

    Evidence rules:
    - 'fixed_baseline' (H0): Fixed n >= n_min (EXP-0004 baseline, n_min=5).
    - 'lower_fixed' (H1): Fixed lower n >= n_fast globally (e.g. n_fast=2).
    - 'strength_adaptive' (H2): n >= n_fast if |mean| >= theta_strong else n_min.
    - 'strength_consistency' (H3): n >= n_fast if |mean| >= theta_strong AND sign_consistency >= gamma_strong else n_min.
    - 'early_accept' (H4): Two-boundary decision: Early accept if strong, consistent, and Wald SE bound > 0; else continue to n_min.
    - 'oracle_stopping' (H5): n >= n_fast for true features, n >= n_min for noise features.
    """
    def __init__(
        self,
        d: int,
        initial_support: List[int],
        probe_policy: BaseProbePolicy,
        q: int = 5,
        mu: float = 0.5,
        eps: float = 1e-6,
        n_min: int = 5,
        theta_promote: float = 0.10,
        grace_period: int = 15,
        swap_threshold: float = 0.05,
        victim_strategy: str = "age_normalized",
        tau_mature: int = 50,
        cooldown_steps: int = 0,
        evidence_rule: str = "fixed_baseline",
        n_fast: int = 2,
        theta_strong: float = 0.30,
        gamma_strong: float = 0.80
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
            cooldown_steps=cooldown_steps
        )
        self.evidence_rule = evidence_rule
        self.n_fast = n_fast
        self.theta_strong = theta_strong
        self.gamma_strong = gamma_strong

        # Additional promotion and evidence logs
        self.evidence_events_log: List[Dict[str, Any]] = []
        self.total_promotions = 0
        self.true_promotions = 0
        self.false_promotions = 0
        self.early_promotions = 0
        self.true_early_promotions = 0
        self.false_early_promotions = 0

    def evaluate_candidate_readiness(
        self,
        c: int,
        true_support: Optional[Set[int]] = None
    ) -> Tuple[bool, bool, int, float, float]:
        """
        Evaluate if candidate c meets the evidence criteria under self.evidence_rule.
        Returns: (is_eligible, used_early_stop, required_n, mean_val, sign_consistency)
        """
        n_c = int(self.cand_n[c])
        if n_c == 0:
            return False, False, self.n_min, 0.0, 0.0

        mean_val = float(abs(self.cand_mean[c]))
        pos = int(self.cand_pos[c])
        neg = int(self.cand_neg[c])
        sign_consistency = float(max(pos, neg) / n_c)

        is_true = 1 if (true_support is not None and c in true_support) else 0

        if self.evidence_rule == "fixed_baseline":
            required_n = self.n_min
            is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
            used_early_stop = False

        elif self.evidence_rule == "lower_fixed":
            required_n = self.n_fast
            is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
            used_early_stop = bool(is_eligible and n_c < self.n_min)

        elif self.evidence_rule == "strength_adaptive":
            if mean_val >= self.theta_strong:
                required_n = self.n_fast
            else:
                required_n = self.n_min
            is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
            used_early_stop = bool(is_eligible and n_c < self.n_min)

        elif self.evidence_rule == "strength_consistency":
            if mean_val >= self.theta_strong and sign_consistency >= self.gamma_strong:
                required_n = self.n_fast
            else:
                required_n = self.n_min
            is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
            used_early_stop = bool(is_eligible and n_c < self.n_min)

        elif self.evidence_rule == "early_accept":
            # Two-boundary sequential rule:
            # Boundary 1: Early accept if n >= n_fast, strong mean, high consistency, and positive Wald bound
            se = 0.0
            if n_c > 1:
                var_c = self.cand_m2[c] / float(n_c - 1)
                se = float(np.sqrt(max(0.0, var_c) / n_c))
            wald_bound = mean_val - 1.645 * se  # 90% one-sided confidence lower bound

            if n_c >= self.n_fast and mean_val >= self.theta_strong and sign_consistency >= self.gamma_strong and wald_bound > 0.0:
                required_n = self.n_fast
                is_eligible = True
                used_early_stop = bool(n_c < self.n_min)
            else:
                required_n = self.n_min
                is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
                used_early_stop = False

        elif self.evidence_rule == "oracle_stopping":
            # Oracle: true candidate can use n_fast; noise requires n_min
            if is_true == 1:
                required_n = self.n_fast
            else:
                required_n = self.n_min
            is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
            used_early_stop = bool(is_eligible and n_c < self.n_min)

        else:
            required_n = self.n_min
            is_eligible = (n_c >= required_n and mean_val >= self.theta_promote)
            used_early_stop = False

        return is_eligible, used_early_stop, required_n, mean_val, sign_consistency

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
            contrib_flops = 4 * curr_active_k
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
        readiness_flops = 4 * num_probed  # Sign consistency & threshold checks
        best_early = False
        best_req_n = self.n_min
        best_sign_c = 0.0
        
        # Check promotion cooldown (frozen = 0)
        in_cooldown = (self.current_step - self.last_promotion_step) < self.cooldown_steps
        
        if num_probed > 0 and not in_cooldown:
            # Evaluate readiness using the adaptive evidence rule
            eligible_candidates_info = []
            for c in candidates:
                eligible, early, req_n, m_val, sign_c = self.evaluate_candidate_readiness(c, true_support=true_support)
                if eligible:
                    eligible_candidates_info.append((c, early, req_n, m_val, sign_c))

            if eligible_candidates_info:
                # Select best candidate by correlation magnitude
                best_cand, best_early, best_req_n, best_m_val, best_sign_c = max(
                    eligible_candidates_info, key=lambda item: item[3]
                )
                cand_score = best_m_val
                cand_evidence_count = int(self.cand_n[best_cand])
                is_p_true = 1 if (true_support is not None and best_cand in true_support) else 0
                
                if len(self.support) < self.k_max:
                    # Growth slot available
                    self.support.append(best_cand)
                    self.weights = np.append(self.weights, 0.0)
                    self.ages = np.append(self.ages, 0)
                    self.updates = np.append(self.updates, 0)
                    self.contrib = np.append(self.contrib, 0.0)
                    promoted_feat = best_cand
                    self.last_promotion_step = self.current_step

                    # Log promotion counts
                    self.total_promotions += 1
                    if is_p_true == 1:
                        self.true_promotions += 1
                    else:
                        self.false_promotions += 1

                    if best_early:
                        self.early_promotions += 1
                        if is_p_true == 1:
                            self.true_early_promotions += 1
                        else:
                            self.false_early_promotions += 1

                    # Log evidence event
                    self.evidence_events_log.append({
                        "step": self.current_step,
                        "candidate_id": best_cand,
                        "is_true": is_p_true,
                        "n_at_promotion": cand_evidence_count,
                        "mean_corr": cand_score,
                        "sign_consistency": best_sign_c,
                        "required_n": best_req_n,
                        "used_early_stop": 1 if best_early else 0,
                        "decision": "growth_slot",
                        "victim_id": None,
                        "victim_is_true": None,
                        "victim_age": None,
                        "victim_score": None
                    })

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

                            is_v_true = 1 if (true_support is not None and victim_feat in true_support) else 0

                            # Log promotion counts
                            self.total_promotions += 1
                            if is_p_true == 1:
                                self.true_promotions += 1
                            else:
                                self.false_promotions += 1

                            if best_early:
                                self.early_promotions += 1
                                if is_p_true == 1:
                                    self.true_early_promotions += 1
                                else:
                                    self.false_early_promotions += 1

                            # Log victim event
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

                            # Log evidence event
                            self.evidence_events_log.append({
                                "step": self.current_step,
                                "candidate_id": best_cand,
                                "is_true": is_p_true,
                                "n_at_promotion": cand_evidence_count,
                                "mean_corr": cand_score,
                                "sign_consistency": best_sign_c,
                                "required_n": best_req_n,
                                "used_early_stop": 1 if best_early else 0,
                                "decision": "swap",
                                "victim_id": victim_feat,
                                "victim_is_true": is_v_true,
                                "victim_age": victim_age,
                                "victim_score": victim_score_val
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

        total_flops = pred_flops + norm_flops + update_flops + contrib_flops + screening_flops + victim_scoring_flops + readiness_flops
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
            "used_early_stop": 1 if best_early else 0,
            "required_n": best_req_n,
            "sign_consistency": best_sign_c,
            "in_cooldown": 1 if in_cooldown else 0,
            "active_params": len(self.support),
            "memory_bytes": mem_bytes
        }
