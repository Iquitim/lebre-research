import numpy as np
from typing import Dict, Any, Set
from .base import BaseOnlineLearner
from ..utils.accounting import ResourceTracker

class DenseNLMS(BaseOnlineLearner):
    """
    Model A: Full-feature Normalized Least Mean Squares (Dense reference).
    Updates all D parameters at every step.
    """
    def __init__(self, d: int, mu: float = 0.5, eps: float = 1e-6):
        self.d = d
        self.mu = mu
        self.eps = eps
        self.weights = np.zeros(d, dtype=np.float64)
        self.all_indices = set(range(d))

    def predict(self, x: np.ndarray) -> float:
        return float(np.dot(self.weights, x))

    def update(self, x: np.ndarray, y: float) -> Dict[str, Any]:
        y_hat = self.predict(x)
        error = y - y_hat
        
        # FLOPs accounting
        pred_flops = ResourceTracker.dot_product_flops(self.d)
        norm_sq = float(np.dot(x, x))
        norm_flops = ResourceTracker.norm_sq_flops(self.d)
        
        # NLMS update step
        step_factor = (self.mu / (self.eps + norm_sq)) * error
        self.weights += step_factor * x
        update_flops = ResourceTracker.vector_update_flops(self.d) + 3  # divide, mul, add
        
        total_flops = pred_flops + norm_flops + update_flops
        mem_bytes = ResourceTracker.estimate_memory_bytes(self.d, 0, self.d)
        
        return {
            "prediction": y_hat,
            "error": error,
            "loss": error ** 2,
            "flops": total_flops,
            "probes": 0,
            "swaps": 0,
            "active_params": self.d,
            "memory_bytes": mem_bytes
        }

    def get_active_support(self) -> Set[int]:
        # Consider features with non-negligible weight for support metric
        # but capacity-wise all d are active
        return self.all_indices

    def get_parameter_count(self) -> int:
        return self.d
