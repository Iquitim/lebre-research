import numpy as np
from typing import Dict, Any, Tuple, Optional, List, Union
from ..utils.temporal_buffer import pair_to_cand

class LongDelayStream:
    """
    Stage A Stream: Long Fixed Delay
        y_t = beta * x_{j*, t - d*} + epsilon_t
    where d* in {10, 25, 50, 100, 200, 500}, D = 10, j* = 0.
    """
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.d = config.get("d_features", 10)
        self.delay = config.get("true_delay", 10)
        self.true_feature = config.get("true_feature", 0)
        self.beta = config.get("beta", 1.0)
        self.noise_std = config.get("noise_std", 0.1)
        self.total_steps = config.get("total_steps", 4000)
        self.rng = np.random.RandomState(seed)
        
        self.t = 0
        self._hist_capacity = self.delay + 2
        self._hist_buffer = np.zeros((self._hist_capacity, self.d), dtype=np.float64)
        self._hist_head = -1

    def step(self) -> Tuple[np.ndarray, float, Tuple[int, int], int]:
        self.t += 1
        x_t = self.rng.randn(self.d)
        
        self._hist_head = (self._hist_head + 1) % self._hist_capacity
        self._hist_buffer[self._hist_head] = x_t
        
        if self.t <= self.delay:
            delayed_val = 0.0
        else:
            slot = (self._hist_head - self.delay) % self._hist_capacity
            delayed_val = float(self._hist_buffer[slot, self.true_feature])
            
        noise = float(self.rng.randn() * self.noise_std)
        y_t = float(self.beta * delayed_val + noise)
        
        true_pair = (self.true_feature, self.delay)
        true_cand = pair_to_cand(self.true_feature, self.delay, self.d)
        return x_t, y_t, true_pair, true_cand

    def has_next(self) -> bool:
        return self.t < self.total_steps


class DistributedIntegrationStream:
    """
    Stage B Stream: Distributed Temporal Integration (Infinite Impulse Response)
        s_t = lambda * s_{t-1} + x_{0, t}
        y_t = s_t + epsilon_t
    where lambda in {0.5, 0.8, 0.95, 0.99}.
    Compact oracle state stores scalar s_t.
    """
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.d = config.get("d_features", 10)
        self.driving_feature = config.get("driving_feature", 0)
        self.decay = float(config.get("decay", 0.8)) # lambda
        self.noise_std = config.get("noise_std", 0.1)
        self.total_steps = config.get("total_steps", 2000)
        self.rng = np.random.RandomState(seed)
        
        self.t = 0
        self.s_t = 0.0 # latent compact state

    def step(self) -> Tuple[np.ndarray, float, float]:
        self.t += 1
        x_t = self.rng.randn(self.d)
        
        # Recursive compact state update
        self.s_t = float(self.decay * self.s_t + x_t[self.driving_feature])
        
        noise = float(self.rng.randn() * self.noise_std)
        y_t = float(self.s_t + noise)
        
        return x_t, y_t, self.s_t

    def has_next(self) -> bool:
        return self.t < self.total_steps


class FiniteStateMemoryStream:
    """
    Stage C Stream: Finite-State Latent Memory
    Supported modes:
    1. 'set_reset':
       x_{0, t} = 1 (SET), x_{1, t} = 1 (RESET), with prob p_event
       s_t = 1 after SET, 0 after RESET, retained indefinitely.
       y_t = s_t + epsilon_t
    2. 'xor_parity':
       x_{0, t} = 1 (TOGGLE), with prob p_event
       s_t = s_{t-1} XOR event_t
       y_t = s_t + epsilon_t
    """
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.d = config.get("d_features", 10)
        self.mode = config.get("mode", "set_reset").lower()
        self.p_event = config.get("p_event", 0.02) # avg interval = 50 steps
        self.noise_std = config.get("noise_std", 0.05)
        self.total_steps = config.get("total_steps", 3000)
        self.rng = np.random.RandomState(seed)
        
        self.t = 0
        self.s_t = 0.0 # latent state in {0, 1}

    def step(self) -> Tuple[np.ndarray, float, float]:
        self.t += 1
        x_t = np.zeros(self.d, dtype=np.float64)
        # Background distractor features x_2..x_{D-1}
        if self.d > 2:
            x_t[2:] = self.rng.randn(self.d - 2)
            
        event_occurred = (self.rng.rand() < self.p_event)
        
        if self.mode == "set_reset":
            if event_occurred:
                if self.rng.rand() < 0.5:
                    x_t[0] = 1.0 # SET
                    self.s_t = 1.0
                else:
                    x_t[1] = 1.0 # RESET
                    self.s_t = 0.0
            # else retain s_t
        elif self.mode == "xor_parity":
            if event_occurred:
                x_t[0] = 1.0 # TOGGLE
                self.s_t = 1.0 - self.s_t
            # else retain s_t
        else:
            raise ValueError(f"Unknown mode {self.mode}")
            
        noise = float(self.rng.randn() * self.noise_std)
        y_t = float(self.s_t + noise)
        
        return x_t, y_t, self.s_t

    def has_next(self) -> bool:
        return self.t < self.total_steps


class ContextDependentRuleStream:
    """
    Stage D Stream: Context-Dependent Temporal Rule
    Latent Mode in {0 (Mode A), 1 (Mode B)}
    Switches on sparse control events:
       x_{0, t} = 1 -> Mode A (delay = delay_a, e.g. 2)
       x_{1, t} = 1 -> Mode B (delay = delay_b, e.g. 7)
    Signal feature: x_{2, t} ~ N(0, 1)
    Target:
       y_t = x_{2, t - delay_mode} + epsilon_t
    """
    def __init__(self, config: Dict[str, Any], seed: int = 42):
        self.d = config.get("d_features", 10)
        self.delay_a = config.get("delay_a", 2)
        self.delay_b = config.get("delay_b", 7)
        self.signal_feature = config.get("signal_feature", 2)
        self.p_switch = config.get("p_switch", 0.02) # avg mode residence = 50 steps
        self.noise_std = config.get("noise_std", 0.1)
        self.total_steps = config.get("total_steps", 3000)
        self.rng = np.random.RandomState(seed)
        
        self.t = 0
        self.mode = 0 # 0 = Mode A, 1 = Mode B
        
        max_delay = max(self.delay_a, self.delay_b)
        self._hist_capacity = max_delay + 2
        self._hist_buffer = np.zeros(self._hist_capacity, dtype=np.float64)
        self._hist_head = -1

    def step(self) -> Tuple[np.ndarray, float, int]:
        self.t += 1
        x_t = np.zeros(self.d, dtype=np.float64)
        
        # Control signals
        switch_event = (self.rng.rand() < self.p_switch)
        if switch_event:
            if self.rng.rand() < 0.5:
                x_t[0] = 1.0 # switch to Mode A
                self.mode = 0
            else:
                x_t[1] = 1.0 # switch to Mode B
                self.mode = 1
                
        # Signal feature
        sig_val = float(self.rng.randn())
        x_t[self.signal_feature] = sig_val
        
        # Noise features
        if self.d > 3:
            x_t[3:] = self.rng.randn(self.d - 3)
            
        # Push signal to history buffer
        self._hist_head = (self._hist_head + 1) % self._hist_capacity
        self._hist_buffer[self._hist_head] = sig_val
        
        active_delay = self.delay_a if self.mode == 0 else self.delay_b
        
        if self.t <= active_delay:
            delayed_val = 0.0
        else:
            slot = (self._hist_head - active_delay) % self._hist_capacity
            delayed_val = float(self._hist_buffer[slot])
            
        noise = float(self.rng.randn() * self.noise_std)
        y_t = float(delayed_val + noise)
        
        return x_t, y_t, self.mode

    def has_next(self) -> bool:
        return self.t < self.total_steps
