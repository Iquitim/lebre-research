import numpy as np
from typing import Dict, Any, Set, List
from .base import BaseOnlineLearner
from ..utils.accounting import ResourceTracker

class FixedNLMS(BaseOnlineLearner):
    """
    Model B: Fixed-Support NLMS.
    Maintains a fixed subset of K features initialized at step 0.
    Zero structural adaptation, zero candidate probes.
    """
    def __init__(self, d: int, k: int, initial_support: List[int], mu: float = 0.5, eps: float = 1e-6):
        self.d = d
        self.k = k
        self.support = list(initial_support)
        self.support_set = set(self.support)
        self.weights = np.zeros(self.k, dtype=np.float64)
        self.mu = mu
        self.eps = eps

    def predict(self, x: np.ndarray) -> float:
        x_sub = x[self.support]
        return float(np.dot(self.weights, x_sub))

    def update(self, x: np.ndarray, y: float) -> Dict[str, Any]:
        x_sub = x[self.support]
        y_hat = float(np.dot(self.weights, x_sub))
        error = y - y_hat
        
        pred_flops = ResourceTracker.dot_product_flops(self.k)
        norm_sq = float(np.dot(x_sub, x_sub))
        norm_flops = ResourceTracker.norm_sq_flops(self.k)
        
        step_factor = (self.mu / (self.eps + norm_sq)) * error
        self.weights += step_factor * x_sub
        update_flops = ResourceTracker.vector_update_flops(self.k) + 3
        
        total_flops = pred_flops + norm_flops + update_flops
        mem_bytes = ResourceTracker.estimate_memory_bytes(self.k, 0, self.d)
        
        return {
            "prediction": y_hat,
            "error": error,
            "loss": error ** 2,
            "flops": total_flops,
            "probes": 0,
            "swaps": 0,
            "active_params": self.k,
            "memory_bytes": mem_bytes
        }

    def get_active_support(self) -> Set[int]:
        return self.support_set

    def get_parameter_count(self) -> int:
        return self.k
