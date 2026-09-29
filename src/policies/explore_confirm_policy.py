from typing import Set, List, Dict, Optional, Any
import numpy as np
from .base import BaseProbePolicy

class PersistenceProbePolicy(BaseProbePolicy):
    """
    F2 Persistence Score Policy:
    Candidates are prioritized only if they demonstrate consistent directional
    correlation over at least n_priority_min probes.
    Lazy scoring updates only probed candidates, keeping compute < 25% of Dense.
    """
    def __init__(
        self,
        d: int = 100,
        priority_fraction: float = 0.60,
        n_priority_min: int = 3,
        c_conf: float = 2.0
    ):
        self.d = d
        self.priority_fraction = priority_fraction
        self.n_priority_min = n_priority_min
        self.c_conf = c_conf
        self.coverage_pointer = 0
        self.cached_scores = np.zeros(d, dtype=np.float64)

    def on_probes_evaluated(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        """
        Lazy update: only update cached scores for candidates that were just probed.
        """
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        for c in candidates:
            if c in active_support:
                self.cached_scores[c] = 0.0
                continue
            n_c = cand_n[c]
            if n_c >= self.n_priority_min and cand_pos is not None and cand_neg is not None:
                pos = cand_pos[c]
                neg = cand_neg[c]
                sign_consistency = max(pos, neg) / float(n_c)
                conf_factor = n_c / (n_c + self.c_conf)
                score = abs(cand_mean[c]) * conf_factor * sign_consistency
                self.cached_scores[c] = float(score)
            else:
                self.cached_scores[c] = 0.0

    def on_promotion(self, feat: int) -> None:
        self.cached_scores[feat] = 0.0

    def on_eviction(self, feat: int) -> None:
        self.cached_scores[feat] = 0.0

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

        inactive = [j for j in range(d) if j not in active_support]
        if len(inactive) <= q:
            return inactive

        q_prio_target = int(round(q * self.priority_fraction))
        selected: List[int] = []

        # 1. Select top candidates with non-zero cached persistence scores
        scored_cands = [(j, self.cached_scores[j]) for j in inactive if self.cached_scores[j] > 0.0]
        if scored_cands:
            # Sort only the subset of scored candidates
            scored_cands.sort(key=lambda x: x[1], reverse=True)
            for cand, _ in scored_cands[:q_prio_target]:
                selected.append(cand)

        # 2. Fill remaining capacity via circular Round-Robin coverage
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
        self.cached_scores.fill(0.0)


class ExploreConfirmPolicy(BaseProbePolicy):
    """
    F3 / F4 Explore-Confirm Screening Policy:
    - EXPLORE: Low-frequency broad coverage of inactive candidates.
    - CONFIRM: Dedicated confirmation state capped at C_max candidates.
    - Entry condition: n >= n_screen, |mean| >= theta_screen, sign_consistency >= gamma_screen.
    - Exit conditions:
      * Promotion (handled by learner -> on_promotion)
      * Weakening: |mean| < theta_drop or sign_consistency < gamma_drop
      * Timeout: confirm_probes >= confirm_max_probes without promotion.
    - F4 adds forced coverage reservation (confirm_fraction + coverage_fraction = 1.0).
    """
    def __init__(
        self,
        d: int = 100,
        c_max: int = 3,
        n_screen: int = 3,
        theta_screen: float = 0.20,
        gamma_screen: float = 0.75,
        theta_drop: float = 0.10,
        gamma_drop: float = 0.60,
        confirm_max_probes: int = 12,
        confirm_fraction: Optional[float] = None, # None for F3 (pure priority to confirm)
        coverage_fraction: Optional[float] = None # None for F3, 0.40 for F4
    ):
        self.d = d
        self.c_max = c_max
        self.n_screen = n_screen
        self.theta_screen = theta_screen
        self.gamma_screen = gamma_screen
        self.theta_drop = theta_drop
        self.gamma_drop = gamma_drop
        self.confirm_max_probes = confirm_max_probes
        self.confirm_fraction = confirm_fraction
        self.coverage_fraction = coverage_fraction

        self.coverage_pointer = 0
        self.confirm_set: List[int] = []
        self.confirm_probes_count: Dict[int, int] = {}
        
        # Diagnostics and tracking logs
        self.confirm_events_log: List[Dict[str, Any]] = []
        self.noise_confirm_locks = 0
        self.false_confirm_probes = 0
        self.true_confirm_probes = 0
        self.current_step = 0
        self.true_support_ref: Optional[Set[int]] = None

    def on_probes_evaluated(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        self.current_step = cand_stats.get("current_step", self.current_step + 1)
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        # Track probes delivered while in CONFIRM
        for c in candidates:
            if c in self.confirm_set:
                self.confirm_probes_count[c] = self.confirm_probes_count.get(c, 0) + 1
                if self.true_support_ref is not None:
                    if c in self.true_support_ref:
                        self.true_confirm_probes += 1
                    else:
                        self.false_confirm_probes += 1

        # 1. Check Exit / Drop / Timeout for confirmed candidates
        dropped_cands = []
        for c in list(self.confirm_set):
            if c in active_support:
                # Promoted already
                dropped_cands.append((c, "promoted"))
                continue

            n_c = cand_n[c]
            c_probes = self.confirm_probes_count.get(c, 0)
            mean_val = abs(cand_mean[c])
            pos = cand_pos[c] if cand_pos is not None else 0
            neg = cand_neg[c] if cand_neg is not None else 0
            sign_consistency = max(pos, neg) / float(n_c) if n_c > 0 else 0.0

            exit_reason = None
            if mean_val < self.theta_drop:
                exit_reason = "mean_drop"
            elif c_probes >= 3 and sign_consistency < self.gamma_drop:
                exit_reason = "sign_drop"
            elif c_probes >= self.confirm_max_probes:
                exit_reason = "timeout"

            if exit_reason is not None:
                dropped_cands.append((c, exit_reason))
                # Check noise lock diagnostic: if consumed >= 8 confirm probes without promotion
                if c_probes >= 8 and (self.true_support_ref is not None and c not in self.true_support_ref):
                    self.noise_confirm_locks += 1

                self.confirm_events_log.append({
                    "step": self.current_step,
                    "candidate": c,
                    "is_true": 1 if (self.true_support_ref is not None and c in self.true_support_ref) else 0,
                    "event": f"exit_{exit_reason}",
                    "confirm_probes": c_probes,
                    "mean_corr": float(cand_mean[c]),
                    "sign_consistency": float(sign_consistency)
                })

                # Reset stats in cand_stats to clear stale noisy evidence
                cand_stats["n"][c] = 0
                cand_stats["mean"][c] = 0.0
                cand_stats["m2"][c] = 0.0
                if cand_pos is not None:
                    cand_stats["pos"][c] = 0
                if cand_neg is not None:
                    cand_stats["neg"][c] = 0

        for c, _ in dropped_cands:
            if c in self.confirm_set:
                self.confirm_set.remove(c)
            self.confirm_probes_count.pop(c, None)

        # 2. Check Entry for EXPLORE candidates that were probed
        for c in candidates:
            if c in active_support or c in self.confirm_set:
                continue

            n_c = cand_n[c]
            if n_c >= self.n_screen:
                pos = cand_pos[c] if cand_pos is not None else 0
                neg = cand_neg[c] if cand_neg is not None else 0
                sign_consistency = max(pos, neg) / float(n_c) if n_c > 0 else 0.0
                mean_val = abs(cand_mean[c])

                if mean_val >= self.theta_screen and sign_consistency >= self.gamma_screen:
                    if len(self.confirm_set) < self.c_max:
                        self.confirm_set.append(c)
                        self.confirm_probes_count[c] = 0
                        self.confirm_events_log.append({
                            "step": self.current_step,
                            "candidate": c,
                            "is_true": 1 if (self.true_support_ref is not None and c in self.true_support_ref) else 0,
                            "event": "entry",
                            "confirm_probes": 0,
                            "mean_corr": float(cand_mean[c]),
                            "sign_consistency": float(sign_consistency)
                        })

    def on_promotion(self, feat: int) -> None:
        if feat in self.confirm_set:
            c_probes = self.confirm_probes_count.get(feat, 0)
            self.confirm_events_log.append({
                "step": self.current_step,
                "candidate": feat,
                "is_true": 1 if (self.true_support_ref is not None and feat in self.true_support_ref) else 0,
                "event": "exit_promotion",
                "confirm_probes": c_probes,
                "mean_corr": 0.0,
                "sign_consistency": 1.0
            })
            self.confirm_set.remove(feat)
            self.confirm_probes_count.pop(feat, None)

    def on_eviction(self, feat: int) -> None:
        if feat in self.confirm_set:
            self.confirm_set.remove(feat)
            self.confirm_probes_count.pop(feat, None)

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

        self.true_support_ref = true_support

        # Remove any active features from confirm_set
        self.confirm_set = [c for c in self.confirm_set if c not in active_support]

        inactive = [j for j in range(d) if j not in active_support]
        if len(inactive) <= q:
            return inactive

        selected: List[int] = []

        # Allocation policy:
        if self.confirm_fraction is not None and self.coverage_fraction is not None:
            # F4 Forced Coverage Reservation
            q_conf_max = int(np.floor(q * self.confirm_fraction))
            for cand in self.confirm_set[:q_conf_max]:
                if len(selected) < q:
                    selected.append(cand)
        else:
            # F3 Pure Confirm Priority (up to q)
            for cand in self.confirm_set:
                if len(selected) < q:
                    selected.append(cand)

        # Fill remaining slots with EXPLORE candidates via circular Round-Robin
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
        self.confirm_set.clear()
        self.confirm_probes_count.clear()
        self.confirm_events_log.clear()
        self.noise_confirm_locks = 0
        self.false_confirm_probes = 0
        self.true_confirm_probes = 0
        self.current_step = 0
