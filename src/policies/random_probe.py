import numpy as np
from typing import Set, List
from .base import BaseProbePolicy

class RandomProbePolicy(BaseProbePolicy):
    """
    Uniform random candidate selection outside active support.
    """
    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def select_candidates(self, d: int, active_support: Set[int], q: int, **kwargs) -> List[int]:
        candidates = [i for i in range(d) if i not in active_support]
        if not candidates:
            return []
        q_eff = min(q, len(candidates))
        return list(self.rng.choice(candidates, size=q_eff, replace=False))

    def reset(self) -> None:
        pass
