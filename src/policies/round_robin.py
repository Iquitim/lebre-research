from typing import Set, List
from .base import BaseProbePolicy

class RoundRobinProbePolicy(BaseProbePolicy):
    """
    Deterministic circular scanning of inactive candidates.
    Guarantees that every candidate feature is probed periodically.
    """
    def __init__(self):
        self.pointer = 0

    def select_candidates(self, d: int, active_support: Set[int], q: int, **kwargs) -> List[int]:
        selected = []
        candidates_checked = 0
        
        while len(selected) < q and candidates_checked < d:
            candidate = self.pointer
            self.pointer = (self.pointer + 1) % d
            candidates_checked += 1
            
            if candidate not in active_support:
                selected.append(candidate)
                
        return selected

    def reset(self) -> None:
        self.pointer = 0
