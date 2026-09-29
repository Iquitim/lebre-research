import numpy as np
from typing import Dict, Any, Tuple, Optional, List

class MixedRegimeStream:
    """
    Mixed-Regime Environment for M2-EXP-0005.
    Sequentially concatenates temporal regimes without delivering phase IDs or regime labels:
    - R_A: STATE_FREE (sparse regression on current features)
    - R_B: LINEAR_USEFUL (continuous exponential integration: s_t* = lambda * s_{t-1}* + x_{0, t})
    - R_C: GATED_NECESSARY (SET/RESET persistent memory with sparse events)
    - R_D: RETURN_STATE_FREE (state-free task to test eviction of obsolete memory)
    
    The learner receives only causal (x_t, y_t).
    The environment internally tracks ground-truth metadata for evaluation.
    """
    def __init__(self, phases: List[Dict[str, Any]], d_features: int = 10, noise_std: float = 0.05, seed: int = 7001):
        self.phases = phases
        self.d = d_features
        self.noise_std = noise_std
        self.rng = np.random.RandomState(seed)
        
        self.current_phase_idx = 0
        self.step_in_phase = 0
        self.global_step = 0
        
        # Latent state trackers
        self.s_linear = 0.0
        self.s_gated = 0.0
        
        # Coefficients for state-free linear regression (features 2 and 3)
        self.beta_state_free = np.zeros(self.d, dtype=np.float64)
        if self.d >= 4:
            self.beta_state_free[2] = 1.0
            self.beta_state_free[3] = -1.0
        else:
            self.beta_state_free[0] = 1.0
            
        self.total_steps = sum(p["duration"] for p in self.phases)

    def has_next(self) -> bool:
        return self.global_step < self.total_steps

    def step(self) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """
        Advances by one step.
        Returns:
            x_t: input vector (d,)
            y_t: target scalar
            info: metadata dictionary (for evaluation only; learner must NOT access this!)
        """
        assert self.has_next(), "Stream exhausted"
        self.global_step += 1
        self.step_in_phase += 1
        
        # Check phase transition
        curr_phase = self.phases[self.current_phase_idx]
        if self.step_in_phase > curr_phase["duration"]:
            self.current_phase_idx += 1
            self.step_in_phase = 1
            curr_phase = self.phases[self.current_phase_idx]
            
        regime_type = curr_phase["type"] # "STATE_FREE", "LINEAR_USEFUL", "GATED_NECESSARY"
        x_t = self.rng.randn(self.d) * 0.5 # background baseline
        noise = float(self.rng.randn() * self.noise_std)
        oracle_state_type = "NONE"
        oracle_s = 0.0
        
        if regime_type == "STATE_FREE":
            # Feature 0 and 1 are inactive; features 2 and 3 carry clean static signal
            x_t[0] = 0.0
            x_t[1] = 0.0
            y_t = float(np.dot(self.beta_state_free, x_t) + noise)
            oracle_state_type = "NONE"
            oracle_s = 0.0
            
        elif regime_type == "LINEAR_USEFUL":
            # Feature 0 drives continuous exponential integration
            decay = curr_phase.get("decay", 0.80)
            x_drive = float(self.rng.randn())
            x_t[0] = x_drive
            x_t[1] = 0.0 # reset inactive
            self.s_linear = float(decay * self.s_linear + x_drive)
            y_t = float(self.s_linear + noise)
            oracle_state_type = "LINEAR"
            oracle_s = self.s_linear
            
        elif regime_type == "GATED_NECESSARY":
            # SET/RESET events on features 0 and 1
            p_event = curr_phase.get("p_event", 0.02)
            event_occurred = (self.rng.rand() < p_event)
            x_t[0] = 0.0
            x_t[1] = 0.0
            if event_occurred:
                if self.rng.rand() < 0.5:
                    x_t[0] = 1.0 # SET
                    self.s_gated = 1.0
                else:
                    x_t[1] = 1.0 # RESET
                    self.s_gated = 0.0
            # else retain s_gated
            y_t = float(self.s_gated + noise)
            oracle_state_type = "GATED"
            oracle_s = self.s_gated
        else:
            raise ValueError(f"Unknown regime type: {regime_type}")
            
        info = {
            "global_step": self.global_step,
            "phase_idx": self.current_phase_idx,
            "regime_type": regime_type,
            "oracle_state_type": oracle_state_type,
            "oracle_s": oracle_s
        }
        
        return x_t, y_t, info

def create_primary_stream(seed: int = 7001, noise_std: float = 0.05) -> MixedRegimeStream:
    """
    Primary Stream (Section 26):
    Phase 1: STATE-FREE (1000 steps)
    Phase 2: LINEAR-INTEGRATION (1500 steps, decay=0.80)
    Phase 3: STATE-FREE (1000 steps)
    Phase 4: SET/RESET (1500 steps, p_event=0.02)
    Phase 5: STATE-FREE (1000 steps)
    Total = 6000 steps.
    """
    phases = [
        {"type": "STATE_FREE", "duration": 1000},
        {"type": "LINEAR_USEFUL", "duration": 1500, "decay": 0.80},
        {"type": "STATE_FREE", "duration": 1000},
        {"type": "GATED_NECESSARY", "duration": 1500, "p_event": 0.02},
        {"type": "STATE_FREE", "duration": 1000}
    ]
    return MixedRegimeStream(phases=phases, d_features=10, noise_std=noise_std, seed=seed)

def create_second_stream(seed: int = 7001, noise_std: float = 0.05) -> MixedRegimeStream:
    """
    Second Stream - Reordered Phases (Section 27):
    Phase 1: SET/RESET (1500 steps, p_event=0.02)
    Phase 2: STATE-FREE (1000 steps)
    Phase 3: LINEAR-INTEGRATION (1500 steps, decay=0.80)
    Phase 4: STATE-FREE (1000 steps)
    Total = 5000 steps.
    """
    phases = [
        {"type": "GATED_NECESSARY", "duration": 1500, "p_event": 0.02},
        {"type": "STATE_FREE", "duration": 1000},
        {"type": "LINEAR_USEFUL", "duration": 1500, "decay": 0.80},
        {"type": "STATE_FREE", "duration": 1000}
    ]
    return MixedRegimeStream(phases=phases, d_features=10, noise_std=noise_std, seed=seed)

def create_holdout_stream(seed: int = 7001, noise_std: float = 0.05) -> MixedRegimeStream:
    """
    Holdout Stream - Unseen Order & Parameters (Section 28, 100):
    Phase 1: STATE-FREE (800 steps)
    Phase 2: SET/RESET (1200 steps, unseen p_event=0.015)
    Phase 3: LINEAR-INTEGRATION (1400 steps, unseen decay=0.90)
    Phase 4: STATE-FREE (800 steps)
    Total = 4200 steps.
    """
    phases = [
        {"type": "STATE_FREE", "duration": 800},
        {"type": "GATED_NECESSARY", "duration": 1200, "p_event": 0.015},
        {"type": "LINEAR_USEFUL", "duration": 1400, "decay": 0.90},
        {"type": "STATE_FREE", "duration": 800}
    ]
    return MixedRegimeStream(phases=phases, d_features=10, noise_std=noise_std, seed=seed)
