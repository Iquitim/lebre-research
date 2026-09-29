import numpy as np
from typing import Tuple

def pair_to_cand(feature_id: int, lag: int, d: int) -> int:
    """
    Bijective mapping from (feature_id, lag) to candidate index c.
    Mapping convention: c = lag * d + feature_id.
    Ensures lag 0 corresponds to [0, d-1] identical to static feature indices.
    """
    return lag * d + feature_id

def cand_to_pair(cand: int, d: int) -> Tuple[int, int]:
    """
    Inverse mapping from candidate index c to (feature_id, lag).
    feature_id = c % d
    lag = c // d
    """
    feature_id = cand % d
    lag = cand // d
    return feature_id, lag

class TemporalRingBuffer:
    """
    Bounded explicit ring buffer storing recent raw inputs up to L_max.
    Memory cost: D * (L_max + 1) * 8 bytes (float64).
    
    CRITICAL CONSTRAINTS:
    - Purely representational; performs no learning.
    - Zero future leakage: only accesses inputs pushed at or before current time t.
    """
    def __init__(self, d: int, l_max: int):
        self.d = d
        self.l_max = l_max
        self.capacity = l_max + 1
        self.buffer = np.zeros((self.capacity, d), dtype=np.float64)
        self.head = -1
        self.total_pushed = 0

    def push(self, x: np.ndarray) -> None:
        """
        Pushes new input x_t into the buffer.
        """
        assert x.shape == (self.d,), f"Expected input shape ({self.d},), got {x.shape}"
        self.head = (self.head + 1) % self.capacity
        self.buffer[self.head] = x
        self.total_pushed += 1

    def get_lag(self, lag: int) -> np.ndarray:
        """
        Retrieves x_{t - lag}.
        If the stream has not yet reached step lag (t <= lag), returns zeros (zero-padding).
        """
        if lag < 0 or lag > self.l_max:
            raise ValueError(f"Lag {lag} out of allowed bounds [0, {self.l_max}]")
        if self.total_pushed <= lag:
            return np.zeros(self.d, dtype=np.float64)
        
        slot = (self.head - lag) % self.capacity
        return self.buffer[slot]

    def get_feature_lag(self, feature_id: int, lag: int) -> float:
        """
        Retrieves scalar x_{feature_id, t - lag}.
        """
        if feature_id < 0 or feature_id >= self.d:
            raise ValueError(f"Feature {feature_id} out of bounds [0, {self.d - 1}]")
        vec = self.get_lag(lag)
        return float(vec[feature_id])

    def get_flat_vector(self) -> np.ndarray:
        """
        Returns full flattened candidate vector z_t of shape (D * (L_max + 1),).
        Candidate c = lag * D + feature_id.
        """
        z = np.empty(self.d * self.capacity, dtype=np.float64)
        for lag in range(self.capacity):
            start = lag * self.d
            end = start + self.d
            z[start:end] = self.get_lag(lag)
        return z

    def get_memory_bytes(self) -> int:
        """
        Returns exact memory size of the ring buffer array in bytes.
        """
        return self.capacity * self.d * 8
