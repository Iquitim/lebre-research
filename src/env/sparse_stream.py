import numpy as np
from typing import Dict, Any, Tuple, Set

class DynamicSparseLinearStream:
    """
    Synthetic streaming environment for dynamic sparse linear regression:
    y_t = x_t^T beta_t + epsilon_t
    where x_t ~ N(0, I_D), epsilon_t ~ N(0, sigma^2).
    """
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.d = config["d_features"]
        self.k_star = config["k_star"]
        self.noise_std = config["noise_std"]
        self.total_steps = config["total_steps"]
        self.shift_step = config.get("shift_step", 1000)
        self.regime_1 = config.get("regime_1")
        self.regime_2 = config.get("regime_2")
        self.shifts = config.get("shifts", None)
        self.beta_scale = config.get("beta_scale", 1.0)
        self.feature_correlation = config.get("feature_correlation", 0.0)
        self.rng = np.random.RandomState(seed)
        
        self.t = 0

        # Multi-regime shift support if explicitly configured
        if self.shifts is not None:
            self._regime_betas = []
            self._regime_supports = []
            self._shift_steps = []
            
            starts_at_zero = any(sh.get("step", 0) == 0 for sh in self.shifts)
            if not starts_at_zero and self.regime_1 is not None:
                b_init = np.zeros(self.d)
                for idx, val in zip(self.regime_1["indices"], self.regime_1["weights"]):
                    b_init[idx] = val * self.beta_scale
                self._regime_betas.append(b_init)
                self._regime_supports.append(set(self.regime_1["indices"]))
                self._shift_steps.append(0)

            for sh in self.shifts:
                self._shift_steps.append(sh["step"])
                b = np.zeros(self.d)
                for idx, val in zip(sh["indices"], sh["weights"]):
                    b[idx] = val * self.beta_scale
                self._regime_betas.append(b)
                self._regime_supports.append(set(sh["indices"]))
        else:
            self._beta_1 = np.zeros(self.d)
            if self.regime_1 is not None:
                for idx, val in zip(self.regime_1["indices"], self.regime_1["weights"]):
                    self._beta_1[idx] = val * self.beta_scale
                
            self._beta_2 = np.zeros(self.d)
            if self.regime_2 is not None:
                for idx, val in zip(self.regime_2["indices"], self.regime_2["weights"]):
                    self._beta_2[idx] = val * self.beta_scale

    def step(self) -> Tuple[np.ndarray, float, Set[int], np.ndarray]:
        """
        Returns:
            x_t: feature vector (D,)
            y_t: scalar target
            true_support: set of active indices in ground truth
            true_beta: full ground truth vector beta_t (D,)
        """
        self.t += 1
        if self.shifts is not None:
            # Multi-shift regime lookup
            regime_idx = 0
            for i, s_step in enumerate(self._shift_steps):
                if self.t > s_step:
                    regime_idx = i
            beta = self._regime_betas[regime_idx]
            true_support = self._regime_supports[regime_idx]
        else:
            if self.t <= self.shift_step:
                beta = self._beta_1
                true_support = set(self.regime_1["indices"]) if self.regime_1 else set()
            else:
                beta = self._beta_2
                true_support = set(self.regime_2["indices"]) if self.regime_2 else set()
            
        x = self.rng.randn(self.d)
        if self.feature_correlation > 0.0:
            rho = self.feature_correlation
            shared = self.rng.randn()
            x = np.sqrt(1.0 - rho) * x + np.sqrt(rho) * shared

        noise = self.rng.randn() * self.noise_std
        y = float(np.dot(x, beta) + noise)
        
        return x, y, true_support, beta

    def has_next(self) -> bool:
        return self.t < self.total_steps

