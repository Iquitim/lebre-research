from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import numpy as np

class BaseProbeController(ABC):
    """Abstract base class for temporal probe controllers."""
    def __init__(self, total_steps: int = 2000, target_budget: int = 10000):
        self.total_steps = total_steps
        self.target_budget = target_budget
        self.cumulative_probes = 0
        self.history: List[int] = []
        self.smoothed_error_history: List[float] = []

    @abstractmethod
    def get_q(self, error: float, step: int) -> int:
        """
        Determine number of probes to perform at current step.
        Args:
            error: causal prediction error y_t - y_hat_t
            step: 1-indexed current step (1 <= step <= total_steps)
        Returns:
            q_t: integer number of probes
        """
        pass

    def reset(self) -> None:
        self.cumulative_probes = 0
        self.history = []
        self.smoothed_error_history = []

class FixedProbeController(BaseProbeController):
    """D0: Fixed baseline probe controller (uniform q=5)."""
    def __init__(self, q: int = 5, total_steps: int = 2000, target_budget: int = 10000):
        super().__init__(total_steps, target_budget)
        self.q = q

    def get_q(self, error: float, step: int) -> int:
        q_t = self.q
        self.cumulative_probes += q_t
        self.history.append(q_t)
        self.smoothed_error_history.append(float(error ** 2))
        return q_t

class ErrorAdaptiveGovernorController(BaseProbeController):
    """
    D1: Error-adaptive controller with causal budget governor.
    Uses causal smoothed squared error: S_t = alpha * S_{t-1} + (1 - alpha) * e_t^2.
    Thresholds:
      if S_t > tau_high: q_desired = q_max
      elif S_t < tau_low: q_desired = q_min
      else: q_desired = q_base
    Governor clamps q_desired into causal feasible bounds [f_min, f_max] guaranteeing
    cumulative budget equals target_budget exactly with zero future leakage.
    """
    def __init__(
        self,
        q_min: int = 2,
        q_base: int = 5,
        q_max: int = 15,
        tau_low: float = 0.08,
        tau_high: float = 0.25,
        alpha: float = 0.85,
        total_steps: int = 2000,
        target_budget: int = 10000
    ):
        super().__init__(total_steps, target_budget)
        self.q_min = q_min
        self.q_base = q_base
        self.q_max = q_max
        self.tau_low = tau_low
        self.tau_high = tau_high
        self.alpha = alpha
        self.smoothed_error = 1.0  # Initial high uncertainty

    def reset(self) -> None:
        super().reset()
        self.smoothed_error = 1.0

    def get_q(self, error: float, step: int) -> int:
        # 1. Update causal smoothed squared error
        sq_err = float(error ** 2)
        self.smoothed_error = self.alpha * self.smoothed_error + (1.0 - self.alpha) * sq_err
        self.smoothed_error_history.append(self.smoothed_error)

        # 2. Desired probes from deterministic rule
        if self.smoothed_error > self.tau_high:
            q_desired = self.q_max
        elif self.smoothed_error < self.tau_low:
            q_desired = self.q_min
        else:
            q_desired = self.q_base

        # 3. Budget Governor: Feasible interval for step t
        rem_steps = self.total_steps - step + 1
        rem_budget = self.target_budget - self.cumulative_probes

        if rem_steps <= 1:
            q_t = rem_budget
        else:
            f_min = max(self.q_min, rem_budget - self.q_max * (rem_steps - 1))
            f_max = min(self.q_max, rem_budget - self.q_min * (rem_steps - 1))
            q_t = int(np.clip(q_desired, f_min, f_max))

        self.cumulative_probes += q_t
        self.history.append(q_t)
        return q_t

class ProbeBankController(BaseProbeController):
    """
    D2: Error-adaptive controller with hard probe credit bank.
    Maintains causal bank B_t >= 0.
    Inflow: B_t^avail = B_{t-1} + q_base.
    Spends up to q_max when error is high, saves down to q_min when error is low.
    No future borrowing: q_t <= B_t^avail.
    No negative bank: B_t >= 0.
    Horizon governor ensures B_T = 0, matching target budget exactly.
    """
    def __init__(
        self,
        q_min: int = 2,
        q_base: int = 5,
        q_max: int = 15,
        tau_low: float = 0.08,
        tau_high: float = 0.25,
        alpha: float = 0.85,
        total_steps: int = 2000,
        target_budget: int = 10000
    ):
        super().__init__(total_steps, target_budget)
        self.q_min = q_min
        self.q_base = q_base
        self.q_max = q_max
        self.tau_low = tau_low
        self.tau_high = tau_high
        self.alpha = alpha
        self.smoothed_error = 1.0
        self.bank = 0
        self.bank_history: List[int] = []

    def reset(self) -> None:
        super().reset()
        self.smoothed_error = 1.0
        self.bank = 0
        self.bank_history = []

    def get_q(self, error: float, step: int) -> int:
        # 1. Bank inflow from base allotment
        avail_bank = self.bank + self.q_base

        # 2. Update causal smoothed squared error
        sq_err = float(error ** 2)
        self.smoothed_error = self.alpha * self.smoothed_error + (1.0 - self.alpha) * sq_err
        self.smoothed_error_history.append(self.smoothed_error)

        # 3. Desired probes
        if self.smoothed_error > self.tau_high:
            q_desired = self.q_max
        elif self.smoothed_error < self.tau_low:
            q_desired = self.q_min
        else:
            q_desired = self.q_base

        # 4. Bank constraints & governor
        rem_steps = self.total_steps - step + 1
        rem_budget = avail_bank + (rem_steps - 1) * self.q_base

        if rem_steps <= 1:
            q_t = avail_bank  # spend remaining bank completely
        else:
            f_min = max(self.q_min, rem_budget - self.q_max * (rem_steps - 1))
            f_max = min(self.q_max, avail_bank, rem_budget - self.q_min * (rem_steps - 1))
            # Ensure f_max >= f_min
            f_max = max(f_min, f_max)
            q_t = int(np.clip(q_desired, f_min, f_max))

        # 5. Deduct from bank
        self.bank = avail_bank - q_t
        self.bank_history.append(self.bank)
        self.cumulative_probes += q_t
        self.history.append(q_t)
        return q_t

class RandomPermutationController(BaseProbeController):
    """
    D3: Random budget redistribution control.
    Takes the exact sequence of q_t produced by D2 (or D1), and permutes its order.
    Matches the exact probe distribution, mean, peak, and total, but timing is uncorrelated with error.
    """
    def __init__(self, q_schedule: List[int], total_steps: int = 2000, target_budget: int = 10000):
        super().__init__(total_steps, target_budget)
        self.q_schedule = list(q_schedule)
        assert len(self.q_schedule) == self.total_steps
        assert sum(self.q_schedule) == self.target_budget

    def get_q(self, error: float, step: int) -> int:
        q_t = self.q_schedule[step - 1]
        self.cumulative_probes += q_t
        self.history.append(q_t)
        self.smoothed_error_history.append(float(error ** 2))
        return q_t

class OracleTimingController(BaseProbeController):
    """
    D4: Oracle change-timing control (diagnostic bound).
    Knows the timing of structural shift (t = shift_step).
    Concentrates q_max probes for burst_len steps immediately post-shift,
    then runs at a lower balanced rate to match target_budget exactly.
    Does NOT use any knowledge about which features changed.
    """
    def __init__(
        self,
        shift_step: int = 1000,
        burst_len: int = 200,
        q_max: int = 15,
        total_steps: int = 2000,
        target_budget: int = 10000
    ):
        super().__init__(total_steps, target_budget)
        self.shift_step = shift_step
        self.burst_len = burst_len
        self.q_max = q_max
        self._build_schedule()

    def _build_schedule(self) -> None:
        self.schedule: List[int] = []
        # Regime 1 (t=1 to shift_step): uniform q=5 (5000 probes)
        for _ in range(self.shift_step):
            self.schedule.append(5)
        
        # Regime 2 post-shift burst: burst_len steps at q_max (e.g. 200 * 15 = 3000 probes)
        for _ in range(self.burst_len):
            self.schedule.append(self.q_max)
            
        # Remaining steps in Regime 2: 800 steps with 2000 probes (alternating 2 and 3)
        rem_steps = self.total_steps - self.shift_step - self.burst_len
        rem_budget = self.target_budget - sum(self.schedule)
        # We need rem_budget across rem_steps steps.
        # e.g. 2000 across 800 steps = 400 of 2, 400 of 3.
        n_threes = rem_budget - 2 * rem_steps
        n_twos = rem_steps - n_threes
        
        rem_pattern = [3] * n_threes + [2] * n_twos
        # Interleave evenly
        interleaved = []
        t3 = n_threes
        t2 = n_twos
        for i in range(rem_steps):
            if (i % 2 == 0 and t3 > 0) or t2 == 0:
                interleaved.append(3)
                t3 -= 1
            else:
                interleaved.append(2)
                t2 -= 1
        self.schedule.extend(interleaved)
        assert len(self.schedule) == self.total_steps
        assert sum(self.schedule) == self.target_budget

    def get_q(self, error: float, step: int) -> int:
        q_t = self.schedule[step - 1]
        self.cumulative_probes += q_t
        self.history.append(q_t)
        self.smoothed_error_history.append(float(error ** 2))
        return q_t
