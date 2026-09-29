import numpy as np
from typing import Dict, Any, Set, List
from .base import BaseOnlineLearner
from ..policies.base import BaseProbePolicy
from ..utils.accounting import ResourceTracker

class SparseNLMS(BaseOnlineLearner):
    """
    Model C & D: Active Support NLMS with Candidate Screening.
    Maintains |S_t| <= K active features and probes q candidates per step.
    """
    def __init__(
        self,
        d: int,
        k: int,
        initial_support: List[int],
        probe_policy: BaseProbePolicy,
        q: int = 5,
        mu: float = 0.5,
        eps: float = 1e-6,
        ema_lambda: float = 0.1,
        grace_period: int = 15,
        swap_threshold: float = 0.05
    ):
        self.d = d
        self.k = k
        self.support = list(initial_support[:k])
        self.weights = np.zeros(len(self.support), dtype=np.float64)
        self.ages = np.zeros(len(self.support), dtype=np.int32)
        
        self.probe_policy = probe_policy
        self.q = q
        self.mu = mu
        self.eps = eps
        self.ema_lambda = ema_lambda
        self.grace_period = grace_period
        self.swap_threshold = swap_threshold
        
        # Candidate correlation score EMA over all features
        self.candidate_scores = np.zeros(d, dtype=np.float64)
        self.total_swaps = 0

    def predict(self, x: np.ndarray) -> float:
        x_sub = x[self.support]
        return float(np.dot(self.weights, x_sub))

    def update(self, x: np.ndarray, y: float) -> Dict[str, Any]:
        # 1. Prediction & Residual
        x_sub = x[self.support]
        y_hat = float(np.dot(self.weights, x_sub))
        error = y - y_hat
        
        pred_flops = ResourceTracker.dot_product_flops(len(self.support))
        
        # 2. NLMS update on active weights
        norm_sq = float(np.dot(x_sub, x_sub))
        norm_flops = ResourceTracker.norm_sq_flops(len(self.support))
        
        step_factor = (self.mu / (self.eps + norm_sq)) * error
        self.weights += step_factor * x_sub
        update_flops = ResourceTracker.vector_update_flops(len(self.support)) + 3
        
        # Age active features
        self.ages += 1
        
        # 3. Candidate Screening
        active_set = set(self.support)
        candidates = self.probe_policy.select_candidates(self.d, active_set, self.q)
        num_probed = len(candidates)
        
        for c in candidates:
            # Signed instantaneous correlation with residual error (e_t * x_{t, c})
            inst_corr = error * x[c]
            self.candidate_scores[c] = (1.0 - self.ema_lambda) * self.candidate_scores[c] + self.ema_lambda * inst_corr
            
        screening_flops = ResourceTracker.candidate_probe_flops(num_probed)
        
        # 4. Structural Swap Evaluation
        swap_occurred = False
        if num_probed > 0 and len(self.support) > 0:
            # Best candidate among probed ones based on magnitude of signed correlation
            best_candidate = max(candidates, key=lambda c: abs(self.candidate_scores[c]))
            best_cand_score = abs(self.candidate_scores[best_candidate])
            
            # Find candidate for dropping among active features older than grace period
            eligible_to_drop = [idx for idx, age in enumerate(self.ages) if age >= self.grace_period]
            
            if eligible_to_drop:
                drop_idx = min(eligible_to_drop, key=lambda idx: abs(self.weights[idx]))
                drop_feature = self.support[drop_idx]
                drop_weight_mag = abs(self.weights[drop_idx])
                
                # Swap condition: candidate score is significantly larger than dropped weight magnitude
                if best_cand_score > drop_weight_mag + self.swap_threshold:
                    # Execute swap
                    self.support[drop_idx] = best_candidate
                    self.weights[drop_idx] = 0.0  # Initialize new weight cleanly
                    self.ages[drop_idx] = 0        # Reset age / grant grace period
                    self.candidate_scores[best_candidate] = 0.0  # Reset candidate score
                    self.candidate_scores[drop_feature] = 0.0    # Reset dropped feature score
                    self.total_swaps += 1
                    swap_occurred = True
                    
        total_flops = pred_flops + norm_flops + update_flops + screening_flops
        mem_bytes = ResourceTracker.estimate_memory_bytes(len(self.support), self.d, self.d)
        
        return {
            "prediction": y_hat,
            "error": error,
            "loss": error ** 2,
            "flops": total_flops,
            "probes": num_probed,
            "swaps": 1 if swap_occurred else 0,
            "active_params": len(self.support),
            "memory_bytes": mem_bytes
        }

    def get_active_support(self) -> Set[int]:
        return set(self.support)

    def get_parameter_count(self) -> int:
        return len(self.support)
