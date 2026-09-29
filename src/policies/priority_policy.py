from typing import Set, List, Dict, Optional, Any
import numpy as np
from .base import BaseProbePolicy

class PriorityProbePolicy(BaseProbePolicy):
    """
    E1/E3 Candidate Targeting Policy:
    Combines priority scoring based on causal candidate correlation evidence
    with forced circular Round-Robin coverage to guarantee zero candidate starvation.
    """
    def __init__(self, priority_fraction: float = 0.60):
        self.priority_fraction = priority_fraction
        self.coverage_pointer = 0

    def select_candidates(
        self,
        d: int,
        active_support: Set[int],
        q: int,
        cand_stats: Optional[Dict[str, np.ndarray]] = None,
        true_support: Optional[Set[int]] = None,
        **kwargs
    ) -> List[int]:
        if q <= 0:
            return []

        # All currently inactive candidates
        inactive = [j for j in range(d) if j not in active_support]
        if len(inactive) <= q:
            return inactive

        q_prio_target = int(round(q * self.priority_fraction))
        selected: List[int] = []

        # 1. Priority Selection (up to q_prio_target)
        if cand_stats is not None and "n" in cand_stats and "mean" in cand_stats:
            cand_n = cand_stats["n"]
            cand_mean = cand_stats["mean"]

            # Compute priority score: |mean| * (n / (n + 2))
            scored_cands = []
            for j in inactive:
                n_j = cand_n[j]
                if n_j >= 1:
                    score = float(abs(cand_mean[j]) * (n_j / (n_j + 2.0)))
                    if score > 0.0:
                        scored_cands.append((j, score))

            # Sort descending by score
            scored_cands.sort(key=lambda x: x[1], reverse=True)
            for cand, _ in scored_cands[:q_prio_target]:
                selected.append(cand)

        # 2. Forced Coverage Selection via circular Round-Robin
        q_needed = q - len(selected)
        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)

        return selected

    def reset(self) -> None:
        self.coverage_pointer = 0

class OracleTargetingPolicy(BaseProbePolicy):
    """
    E4 Oracle Candidate Targeting Diagnostic:
    Directs candidate probes preferentially to currently omitted true features.
    Fills remaining probe capacity via circular Round-Robin coverage.
    Truth is used ONLY for candidate targeting.
    """
    def __init__(self):
        self.coverage_pointer = 0

    def select_candidates(
        self,
        d: int,
        active_support: Set[int],
        q: int,
        cand_stats: Optional[Dict[str, np.ndarray]] = None,
        true_support: Optional[Set[int]] = None,
        **kwargs
    ) -> List[int]:
        if q <= 0:
            return []

        selected: List[int] = []

        # 1. Direct probes to omitted true features first
        if true_support is not None:
            omitted_true = [j for j in sorted(list(true_support)) if j not in active_support]
            for cand in omitted_true[:q]:
                selected.append(cand)

        # 2. Fill remaining capacity with circular Round-Robin coverage
        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)

        return selected

    def reset(self) -> None:
        self.coverage_pointer = 0
