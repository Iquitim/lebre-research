from abc import ABC, abstractmethod
from typing import Set, List

class BaseProbePolicy(ABC):
    """
    Abstract interface for candidate probing policies.
    """
    @abstractmethod
    def select_candidates(self, d: int, active_support: Set[int], q: int) -> List[int]:
        """
        Select q candidates to probe from outside the active support.
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset internal state if any."""
        pass
