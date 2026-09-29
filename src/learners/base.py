from abc import ABC, abstractmethod
from typing import Dict, Any, Set
import numpy as np

class BaseOnlineLearner(ABC):
    """
    Abstract interface for online continuous learners.
    """
    @abstractmethod
    def predict(self, x: np.ndarray) -> float:
        """Compute scalar prediction y_hat for input x."""
        pass

    @abstractmethod
    def update(self, x: np.ndarray, y: float) -> Dict[str, Any]:
        """
        Perform online update given true target y.
        Returns a dictionary with step statistics (flops, probes, swaps, etc.).
        """
        pass

    @abstractmethod
    def get_active_support(self) -> Set[int]:
        """Return the set of currently active feature indices."""
        pass

    @abstractmethod
    def get_parameter_count(self) -> int:
        """Return count of active parameters."""
        pass
