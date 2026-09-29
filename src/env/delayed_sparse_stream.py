import numpy as np
from typing import Dict, Any, Tuple, Optional, List, Union
from ..utils.temporal_buffer import pair_to_cand

class DelayedSparseLinearStream:
    """
    Streaming environment for delayed sparse linear regression (Milestones M2-EXP-0001 and M2-EXP-0002):
        y_t = sum_{m=1}^M beta_m * x_{j*_m, t - d*_m} + epsilon_t
    where x_t may be white N(0, I_D) or AR(1) with parameter rho,
    and epsilon_t ~ N(0, sigma^2).
    
    Supports:
    - Single delayed dependency (M=1, backward compatible with M2-EXP-0001)
    - Multiple delayed dependencies (M in {1, 2, 3, 5, ...})
    - Same feature at multiple lags (e.g. j1 = j2 = j*)
    - AR(1) correlated input processes with parameter rho in [0, 1)
    - Dynamic multi-delay / multi-feature transitions (regime switches at step s)
    """
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.d = config["d_features"]
        self.l_max = config.get("l_max", 10)
        self.noise_std = config["noise_std"]
        self.total_steps = config["total_steps"]
        self.beta_scale = config.get("beta_scale", 1.0)
        self.rho = float(config.get("rho", 0.0))
        self.rng = np.random.RandomState(seed)
        
        # Ground truth regimes
        self.shifts = config.get("shifts", None)
        self.shift_step = config.get("shift_step", 1000)
        self.is_multi_pair = False
        
        if self.shifts is not None:
            self._shift_steps = [sh["step"] for sh in self.shifts]
            self._regime_pairs: List[List[Tuple[int, int]]] = []
            self._regime_betas: List[List[float]] = []
            
            for sh in self.shifts:
                if "true_pairs" in sh:
                    self.is_multi_pair = True
                    pairs = [(int(f), int(l)) for f, l in sh["true_pairs"]]
                    betas = [float(b) * self.beta_scale for b in sh.get("betas", [1.0] * len(pairs))]
                else:
                    pairs = [(int(sh["true_feature"]), int(sh["true_delay"]))]
                    betas = [float(sh.get("beta", 1.0)) * self.beta_scale]
                self._regime_pairs.append(pairs)
                self._regime_betas.append(betas)
        else:
            # Check if multi-pair is specified directly in config
            if "true_pairs" in config:
                self.is_multi_pair = True
                pairs_1 = [(int(f), int(l)) for f, l in config["true_pairs"]]
                betas_1 = [float(b) * self.beta_scale for b in config.get("betas", [1.0] * len(pairs_1))]
                
                # Check optional regime 2
                if "regime_2_pairs" in config:
                    pairs_2 = [(int(f), int(l)) for f, l in config["regime_2_pairs"]]
                    betas_2 = [float(b) * self.beta_scale for b in config.get("regime_2_betas", [1.0] * len(pairs_2))]
                else:
                    pairs_2 = pairs_1
                    betas_2 = betas_1
                    
                self._shift_steps = [0, self.shift_step]
                self._regime_pairs = [pairs_1, pairs_2]
                self._regime_betas = [betas_1, betas_2]
            else:
                # Single pair configuration (M2-EXP-0001 compatible)
                self.is_multi_pair = False
                f1 = int(config.get("true_feature", 0))
                d1 = int(config.get("true_delay", 0))
                b1 = float(config.get("beta", 1.0)) * self.beta_scale
                
                f2 = int(config.get("regime_2_feature", f1))
                d2 = int(config.get("regime_2_delay", d1))
                b2 = float(config.get("regime_2_beta", config.get("beta", 1.0))) * self.beta_scale
                
                self._shift_steps = [0, self.shift_step]
                self._regime_pairs = [[(f1, d1)], [(f2, d2)]]
                self._regime_betas = [[b1], [b2]]

        self.t = 0
        self._prev_x = np.zeros(self.d, dtype=np.float64)
        
        # History ring buffer strictly internal to the stream generator for computing delayed y_t
        self._hist_capacity = self.l_max + 2
        self._hist_buffer = np.zeros((self._hist_capacity, self.d), dtype=np.float64)
        self._hist_head = -1

    def step(self) -> Tuple[np.ndarray, float, Any, Any]:
        """
        Generates one step of the delayed linear stream.
        
        Returns:
            x_t: current observation vector of shape (D,)
            y_t: scalar response computed from delayed input
            true_pair: (true_feature, true_delay) tuple OR list of tuples if is_multi_pair
            true_cand: single integer index c* OR list of candidate indices if is_multi_pair
        """
        self.t += 1
        
        # Determine active regime parameters
        regime_idx = 0
        for i, s_step in enumerate(self._shift_steps):
            if self.t > s_step:
                regime_idx = i
                
        current_pairs = self._regime_pairs[regime_idx]
        current_betas = self._regime_betas[regime_idx]
        
        # Generate x_t (White or AR(1))
        if self.rho == 0.0 or self.t == 1:
            x_t = self.rng.randn(self.d)
        else:
            eta_t = self.rng.randn(self.d)
            x_t = self.rho * self._prev_x + np.sqrt(1.0 - self.rho**2) * eta_t
            
        self._prev_x = x_t.copy()
        
        # Push into internal history
        self._hist_head = (self._hist_head + 1) % self._hist_capacity
        self._hist_buffer[self._hist_head] = x_t
        
        # Compute target signal as sum over all active delayed dependencies
        signal = 0.0
        for (feat, delay), beta in zip(current_pairs, current_betas):
            if self.t <= delay:
                delayed_val = 0.0
            else:
                slot = (self._hist_head - delay) % self._hist_capacity
                delayed_val = float(self._hist_buffer[slot, feat])
            signal += beta * delayed_val
            
        noise = float(self.rng.randn() * self.noise_std)
        y_t = float(signal + noise)
        
        current_cands = [pair_to_cand(f, d, self.d) for f, d in current_pairs]
        
        if self.is_multi_pair:
            return x_t, y_t, current_pairs, current_cands
        else:
            return x_t, y_t, current_pairs[0], current_cands[0]

    def has_next(self) -> bool:
        return self.t < self.total_steps
