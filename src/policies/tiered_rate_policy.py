from typing import Set, List, Dict, Optional, Any, Tuple
import numpy as np
from collections import deque
from .base import BaseProbePolicy

class TieredEvidenceRatePolicy(BaseProbePolicy):
    """
    TieredEvidenceRatePolicy for EXP-0006:
    Allocates probe frequency across candidate tiers (COLD, WARM, HOT)
    to increase per-candidate evidence arrival rate for promising candidates
    without losing global coverage, without increasing total probes, and
    without exceeding 25% of Dense compute.

    Modes:
    - 'uniform_baseline' (J0): Exact accepted EXP-0005 baseline (Explore/Confirm + 40% circular coverage).
    - 'two_tier' (J1): COLD (broad circular coverage) + WARM (elevated probe rate on hint, W_max capacity).
    - 'two_tier_decay' (J2): J1 + demotion back to COLD on weakening or probe timeout.
    - 'three_tier' (J3): COLD (30%), WARM (30%), and HOT (40%) with progressive evidence thresholds.
    - 'queue_multi_rate' (J4): Explicit FIFO queues (cold_queue, warm_queue, hot_queue) with fixed service schedule.
    - 'oracle_rate' (J5): Currently omitted true features get elevated rate priority; noise remain COLD. Causal confirmation.
    """
    def __init__(
        self,
        d: int = 100,
        mode: str = "uniform_baseline",
        # J0 baseline Explore/Confirm params
        c_max: int = 3,
        n_screen: int = 3,
        theta_screen: float = 0.20,
        gamma_screen: float = 0.75,
        theta_drop: float = 0.10,
        gamma_drop: float = 0.60,
        confirm_max_probes: int = 12,
        confirm_fraction: float = 0.60,
        coverage_fraction: float = 0.40,
        # Tiered / hint params (J1-J4)
        w_max: int = 5,
        h_max: int = 2,
        n_hint: int = 2,
        theta_hint: float = 0.15,
        gamma_hint: float = 0.60,
        theta_decay: float = 0.10,
        warm_max_probes: int = 10,
        hot_max_probes: int = 12,
        theta_hot: float = 0.25,
        gamma_hot: float = 0.75,
        cold_fraction: float = 0.35,
        warm_fraction: float = 0.65,
        # J3 fractions
        cold_fraction_j3: float = 0.30,
        warm_fraction_j3: float = 0.30,
        hot_fraction_j3: float = 0.40,
    ):
        self.d = d
        self.mode = mode
        self.c_max = c_max
        self.n_screen = n_screen
        self.theta_screen = theta_screen
        self.gamma_screen = gamma_screen
        self.theta_drop = theta_drop
        self.gamma_drop = gamma_drop
        self.confirm_max_probes = confirm_max_probes
        self.confirm_fraction = confirm_fraction
        self.coverage_fraction = coverage_fraction

        # Tiered params
        self.w_max = w_max
        self.h_max = h_max
        self.n_hint = n_hint
        self.theta_hint = theta_hint
        self.gamma_hint = gamma_hint
        self.theta_decay = theta_decay
        self.warm_max_probes = warm_max_probes
        self.hot_max_probes = hot_max_probes
        self.theta_hot = theta_hot
        self.gamma_hot = gamma_hot
        self.cold_fraction = cold_fraction
        self.warm_fraction = warm_fraction
        self.cold_fraction_j3 = cold_fraction_j3
        self.warm_fraction_j3 = warm_fraction_j3
        self.hot_fraction_j3 = hot_fraction_j3

        # State tracking
        self.coverage_pointer = 0
        self.warm_pointer = 0
        self.hot_pointer = 0
        self.current_step = 0
        self.true_support_ref: Optional[Set[int]] = None

        # J0 structures
        self.confirm_set: List[int] = []
        self.confirm_probes_count: Dict[int, int] = {}
        self.confirm_events_log: List[Dict[str, Any]] = []

        # Tier structures (J1, J2, J3, J5)
        self.warm_set: List[int] = []
        self.hot_set: List[int] = []
        self.warm_probes_count: Dict[int, int] = {}
        self.hot_probes_count: Dict[int, int] = {}

        # J4 Queues
        self.cold_queue: deque = deque()
        self.warm_queue: deque = deque()
        self.hot_queue: deque = deque()
        self._init_queues()

        # Diagnostic metrics
        self.tier_events_log: List[Dict[str, Any]] = []
        self.probes_by_tier = {"COLD": 0, "WARM": 0, "HOT": 0, "CONFIRM": 0}
        self.useful_elevated_probes = 0
        self.false_elevated_probes = 0
        self.tier_entry_counts = {"WARM_TRUE": 0, "WARM_NOISE": 0, "HOT_TRUE": 0, "HOT_NOISE": 0}

    def _init_queues(self):
        self.cold_queue.clear()
        self.warm_queue.clear()
        self.hot_queue.clear()
        for j in range(self.d):
            self.cold_queue.append(j)

    def reset(self) -> None:
        self.coverage_pointer = 0
        self.warm_pointer = 0
        self.hot_pointer = 0
        self.current_step = 0
        self.confirm_set.clear()
        self.confirm_probes_count.clear()
        self.confirm_events_log.clear()
        self.warm_set.clear()
        self.hot_set.clear()
        self.warm_probes_count.clear()
        self.hot_probes_count.clear()
        self._init_queues()
        self.tier_events_log.clear()
        self.probes_by_tier = {"COLD": 0, "WARM": 0, "HOT": 0, "CONFIRM": 0}
        self.useful_elevated_probes = 0
        self.false_elevated_probes = 0
    def get_candidate_tier(self, c: int) -> str:
        if self.mode == "queue_multi_rate":
            if c in self.hot_queue:
                return "HOT"
            elif c in self.warm_queue:
                return "WARM"
            return "COLD"
        elif self.mode in ("two_tier", "two_tier_decay"):
            return "WARM" if c in self.warm_set else "COLD"
        elif self.mode == "three_tier":
            if c in self.hot_set:
                return "HOT"
            elif c in self.warm_set:
                return "WARM"
            return "COLD"
        elif self.mode == "uniform_baseline":
            return "CONFIRM" if c in self.confirm_set else "COLD"
        elif self.mode == "oracle_rate":
            return "WARM" if (self.true_support_ref and c in self.true_support_ref) else "COLD"
        return "COLD"

    def on_promotion(self, feat: int) -> None:
        # Candidate promoted to active support
        if feat in self.confirm_set:
            self.confirm_set.remove(feat)
            self.confirm_probes_count.pop(feat, None)
        if feat in self.warm_set:
            self.warm_set.remove(feat)
            self.warm_probes_count.pop(feat, None)
        if feat in self.hot_set:
            self.hot_set.remove(feat)
            self.hot_probes_count.pop(feat, None)
        # J4 remove from queues
        try:
            self.cold_queue.remove(feat)
        except ValueError:
            pass
        try:
            self.warm_queue.remove(feat)
        except ValueError:
            pass
        try:
            self.hot_queue.remove(feat)
        except ValueError:
            pass

    def on_eviction(self, feat: int) -> None:
        # Demoted from active support back to inactive candidates (enters COLD)
        if feat in self.confirm_set:
            self.confirm_set.remove(feat)
            self.confirm_probes_count.pop(feat, None)
        if feat in self.warm_set:
            self.warm_set.remove(feat)
            self.warm_probes_count.pop(feat, None)
        if feat in self.hot_set:
            self.hot_set.remove(feat)
            self.hot_probes_count.pop(feat, None)
        if feat not in self.cold_queue and feat not in self.warm_queue and feat not in self.hot_queue:
            self.cold_queue.append(feat)

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

        if self.mode == "uniform_baseline":
            self._update_uniform_baseline(candidates, cand_stats, active_support)
        elif self.mode in ("two_tier", "two_tier_decay"):
            self._update_two_tier(candidates, cand_stats, active_support)
        elif self.mode == "three_tier":
            self._update_three_tier(candidates, cand_stats, active_support)
        elif self.mode == "queue_multi_rate":
            self._update_queue_multi_rate(candidates, cand_stats, active_support)
        elif self.mode == "oracle_rate":
            self._update_oracle_rate(candidates, cand_stats, active_support)

    def _update_uniform_baseline(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        for c in candidates:
            if c in self.confirm_set:
                self.confirm_probes_count[c] = self.confirm_probes_count.get(c, 0) + 1

        # 1. Exit / Drop / Timeout for confirmed candidates
        dropped = []
        for c in list(self.confirm_set):
            if c in active_support:
                dropped.append((c, "promoted"))
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
                dropped.append((c, exit_reason))
                # Reset stats on drop
                cand_stats["n"][c] = 0
                cand_stats["mean"][c] = 0.0
                cand_stats["m2"][c] = 0.0
                if cand_pos is not None:
                    cand_stats["pos"][c] = 0
                if cand_neg is not None:
                    cand_stats["neg"][c] = 0

        for c, reason in dropped:
            if c in self.confirm_set:
                self.confirm_set.remove(c)
            self.confirm_probes_count.pop(c, None)

        # 2. Check Entry for EXPLORE candidates
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

    def _update_two_tier(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        # Track probes delivered to WARM
        for c in candidates:
            if c in self.warm_set:
                self.warm_probes_count[c] = self.warm_probes_count.get(c, 0) + 1

        # Check decay/demotion if mode == 'two_tier_decay'
        if self.mode == "two_tier_decay":
            demoted = []
            for c in list(self.warm_set):
                if c in active_support:
                    demoted.append((c, "promoted"))
                    continue
                n_c = cand_n[c]
                w_probes = self.warm_probes_count.get(c, 0)
                mean_val = abs(cand_mean[c])
                pos = cand_pos[c] if cand_pos is not None else 0
                neg = cand_neg[c] if cand_neg is not None else 0
                sign_c = max(pos, neg) / float(n_c) if n_c > 0 else 0.0

                exit_reason = None
                if mean_val < self.theta_decay:
                    exit_reason = "mean_decay"
                elif w_probes >= 3 and sign_c < self.gamma_hint:
                    exit_reason = "sign_decay"
                elif w_probes >= self.warm_max_probes:
                    exit_reason = "timeout"

                if exit_reason is not None:
                    demoted.append((c, exit_reason))
                    self.tier_events_log.append({
                        "step": self.current_step,
                        "candidate": c,
                        "is_true": 1 if (self.true_support_ref and c in self.true_support_ref) else 0,
                        "old_tier": "WARM",
                        "new_tier": "COLD",
                        "reason": exit_reason,
                        "n": n_c,
                        "mean_corr": float(mean_val),
                        "sign_consistency": float(sign_c)
                    })
                    # Soft reset stats
                    cand_stats["n"][c] = 0
                    cand_stats["mean"][c] = 0.0
                    cand_stats["m2"][c] = 0.0
                    if cand_pos is not None:
                        cand_stats["pos"][c] = 0
                    if cand_neg is not None:
                        cand_stats["neg"][c] = 0

            for c, _ in demoted:
                if c in self.warm_set:
                    self.warm_set.remove(c)
                self.warm_probes_count.pop(c, None)

        # Check WARM entry for probed candidates
        for c in candidates:
            if c in active_support or c in self.warm_set:
                continue
            n_c = cand_n[c]
            if n_c >= self.n_hint:
                pos = cand_pos[c] if cand_pos is not None else 0
                neg = cand_neg[c] if cand_neg is not None else 0
                sign_c = max(pos, neg) / float(n_c) if n_c > 0 else 0.0
                mean_val = abs(cand_mean[c])

                if mean_val >= self.theta_hint and sign_c >= self.gamma_hint:
                    if len(self.warm_set) < self.w_max:
                        self.warm_set.append(c)
                        self.warm_probes_count[c] = 0
                        is_true = 1 if (self.true_support_ref and c in self.true_support_ref) else 0
                        if is_true == 1:
                            self.tier_entry_counts["WARM_TRUE"] += 1
                        else:
                            self.tier_entry_counts["WARM_NOISE"] += 1
                        self.tier_events_log.append({
                            "step": self.current_step,
                            "candidate": c,
                            "is_true": is_true,
                            "old_tier": "COLD",
                            "new_tier": "WARM",
                            "reason": "hint_entry",
                            "n": n_c,
                            "mean_corr": float(mean_val),
                            "sign_consistency": float(sign_c)
                        })

    def _update_three_tier(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        # Track probes delivered
        for c in candidates:
            if c in self.hot_set:
                self.hot_probes_count[c] = self.hot_probes_count.get(c, 0) + 1
            elif c in self.warm_set:
                self.warm_probes_count[c] = self.warm_probes_count.get(c, 0) + 1

        # Check demotions from HOT -> WARM or COLD
        dropped_hot = []
        for c in list(self.hot_set):
            if c in active_support:
                dropped_hot.append((c, "promoted"))
                continue
            n_c = cand_n[c]
            h_probes = self.hot_probes_count.get(c, 0)
            mean_val = abs(cand_mean[c])
            pos = cand_pos[c] if cand_pos is not None else 0
            neg = cand_neg[c] if cand_neg is not None else 0
            sign_c = max(pos, neg) / float(n_c) if n_c > 0 else 0.0

            if mean_val < self.theta_drop or (h_probes >= 3 and sign_c < self.gamma_drop) or h_probes >= self.hot_max_probes:
                dropped_hot.append((c, "hot_decay"))
                self.tier_events_log.append({
                    "step": self.current_step, "candidate": c,
                    "is_true": 1 if (self.true_support_ref and c in self.true_support_ref) else 0,
                    "old_tier": "HOT", "new_tier": "COLD", "reason": "decay",
                    "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                })
                cand_stats["n"][c] = 0
                cand_stats["mean"][c] = 0.0
                cand_stats["m2"][c] = 0.0
                if cand_pos is not None: cand_stats["pos"][c] = 0
                if cand_neg is not None: cand_stats["neg"][c] = 0

        for c, _ in dropped_hot:
            if c in self.hot_set: self.hot_set.remove(c)
            self.hot_probes_count.pop(c, None)

        # Check demotions from WARM -> COLD
        dropped_warm = []
        for c in list(self.warm_set):
            if c in active_support:
                dropped_warm.append((c, "promoted"))
                continue
            n_c = cand_n[c]
            w_probes = self.warm_probes_count.get(c, 0)
            mean_val = abs(cand_mean[c])
            pos = cand_pos[c] if cand_pos is not None else 0
            neg = cand_neg[c] if cand_neg is not None else 0
            sign_c = max(pos, neg) / float(n_c) if n_c > 0 else 0.0

            if mean_val < self.theta_decay or (w_probes >= 3 and sign_c < self.gamma_hint) or w_probes >= self.warm_max_probes:
                dropped_warm.append((c, "warm_decay"))
                self.tier_events_log.append({
                    "step": self.current_step, "candidate": c,
                    "is_true": 1 if (self.true_support_ref and c in self.true_support_ref) else 0,
                    "old_tier": "WARM", "new_tier": "COLD", "reason": "decay",
                    "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                })
                cand_stats["n"][c] = 0
                cand_stats["mean"][c] = 0.0
                cand_stats["m2"][c] = 0.0
                if cand_pos is not None: cand_stats["pos"][c] = 0
                if cand_neg is not None: cand_stats["neg"][c] = 0

        for c, _ in dropped_warm:
            if c in self.warm_set: self.warm_set.remove(c)
            self.warm_probes_count.pop(c, None)

        # Check promotions from WARM -> HOT or COLD -> WARM
        for c in candidates:
            if c in active_support:
                continue
            n_c = cand_n[c]
            pos = cand_pos[c] if cand_pos is not None else 0
            neg = cand_neg[c] if cand_neg is not None else 0
            sign_c = max(pos, neg) / float(n_c) if n_c > 0 else 0.0
            mean_val = abs(cand_mean[c])
            is_true = 1 if (self.true_support_ref and c in self.true_support_ref) else 0

            # Promote to HOT
            if n_c >= self.n_screen and mean_val >= self.theta_hot and sign_c >= self.gamma_hot:
                if c in self.warm_set:
                    self.warm_set.remove(c)
                    self.warm_probes_count.pop(c, None)
                if c not in self.hot_set and len(self.hot_set) < self.h_max:
                    self.hot_set.append(c)
                    self.hot_probes_count[c] = 0
                    if is_true == 1: self.tier_entry_counts["HOT_TRUE"] += 1
                    else: self.tier_entry_counts["HOT_NOISE"] += 1
                    self.tier_events_log.append({
                        "step": self.current_step, "candidate": c, "is_true": is_true,
                        "old_tier": "WARM", "new_tier": "HOT", "reason": "hot_entry",
                        "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                    })
                    continue

            # Promote to WARM
            if c not in self.hot_set and c not in self.warm_set:
                if n_c >= self.n_hint and mean_val >= self.theta_hint and sign_c >= self.gamma_hint:
                    if len(self.warm_set) < self.w_max:
                        self.warm_set.append(c)
                        self.warm_probes_count[c] = 0
                        if is_true == 1: self.tier_entry_counts["WARM_TRUE"] += 1
                        else: self.tier_entry_counts["WARM_NOISE"] += 1
                        self.tier_events_log.append({
                            "step": self.current_step, "candidate": c, "is_true": is_true,
                            "old_tier": "COLD", "new_tier": "WARM", "reason": "hint_entry",
                            "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                        })

    def _update_queue_multi_rate(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        for c in candidates:
            if c in active_support:
                continue
            n_c = cand_n[c]
            pos = cand_pos[c] if cand_pos is not None else 0
            neg = cand_neg[c] if cand_neg is not None else 0
            sign_c = max(pos, neg) / float(n_c) if n_c > 0 else 0.0
            mean_val = abs(cand_mean[c])
            is_true = 1 if (self.true_support_ref and c in self.true_support_ref) else 0

            # Demotion checks if currently in warm or hot
            in_hot = (c in self.hot_queue)
            in_warm = (c in self.warm_queue)

            if in_hot:
                if mean_val < self.theta_drop or (n_c >= 5 and sign_c < self.gamma_drop):
                    self.hot_queue.remove(c)
                    if c not in self.cold_queue:
                        self.cold_queue.append(c)
                    self.tier_events_log.append({
                        "step": self.current_step, "candidate": c, "is_true": is_true,
                        "old_tier": "HOT", "new_tier": "COLD", "reason": "decay",
                        "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                    })
                    cand_stats["n"][c] = 0
                    cand_stats["mean"][c] = 0.0
                    cand_stats["m2"][c] = 0.0
                    if cand_pos is not None: cand_stats["pos"][c] = 0
                    if cand_neg is not None: cand_stats["neg"][c] = 0
                    continue

            if in_warm:
                if mean_val < self.theta_decay or (n_c >= 4 and sign_c < self.gamma_hint):
                    self.warm_queue.remove(c)
                    if c not in self.cold_queue:
                        self.cold_queue.append(c)
                    self.tier_events_log.append({
                        "step": self.current_step, "candidate": c, "is_true": is_true,
                        "old_tier": "WARM", "new_tier": "COLD", "reason": "decay",
                        "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                    })
                    cand_stats["n"][c] = 0
                    cand_stats["mean"][c] = 0.0
                    cand_stats["m2"][c] = 0.0
                    if cand_pos is not None: cand_stats["pos"][c] = 0
                    if cand_neg is not None: cand_stats["neg"][c] = 0
                    continue

            # Elevation checks (only remove from lower tier if room in target tier!)
            if not in_hot and n_c >= self.n_screen and mean_val >= self.theta_hot and sign_c >= self.gamma_hot:
                if len(self.hot_queue) < self.h_max:
                    if in_warm:
                        self.warm_queue.remove(c)
                    elif c in self.cold_queue:
                        self.cold_queue.remove(c)
                    self.hot_queue.append(c)
                    if is_true == 1: self.tier_entry_counts["HOT_TRUE"] += 1
                    else: self.tier_entry_counts["HOT_NOISE"] += 1
                    self.tier_events_log.append({
                        "step": self.current_step, "candidate": c, "is_true": is_true,
                        "old_tier": "WARM" if in_warm else "COLD", "new_tier": "HOT", "reason": "hot_entry",
                        "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                    })
                    continue

            if not in_hot and not in_warm and n_c >= self.n_hint and mean_val >= self.theta_hint and sign_c >= self.gamma_hint:
                if len(self.warm_queue) < self.w_max:
                    if c in self.cold_queue:
                        self.cold_queue.remove(c)
                    self.warm_queue.append(c)
                    if is_true == 1: self.tier_entry_counts["WARM_TRUE"] += 1
                    else: self.tier_entry_counts["WARM_NOISE"] += 1
                    self.tier_events_log.append({
                        "step": self.current_step, "candidate": c, "is_true": is_true,
                        "old_tier": "COLD", "new_tier": "WARM", "reason": "hint_entry",
                        "n": n_c, "mean_corr": float(mean_val), "sign_consistency": float(sign_c)
                    })

    def _update_oracle_rate(
        self,
        candidates: List[int],
        cand_stats: Dict[str, Any],
        active_support: Set[int]
    ) -> None:
        if self.true_support_ref is not None:
            self.warm_set = [c for c in sorted(self.true_support_ref) if c not in active_support]
            for c in candidates:
                if c in self.warm_set:
                    self.warm_probes_count[c] = self.warm_probes_count.get(c, 0) + 1

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

        inactive = [j for j in range(d) if j not in active_support]
        if len(inactive) <= q:
            return inactive

        if self.mode == "uniform_baseline":
            return self._select_uniform_baseline(d, active_support, q)
        elif self.mode in ("two_tier", "two_tier_decay"):
            return self._select_two_tier(d, active_support, q)
        elif self.mode == "three_tier":
            return self._select_three_tier(d, active_support, q)
        elif self.mode == "queue_multi_rate":
            return self._select_queue_multi_rate(d, active_support, q)
        elif self.mode == "oracle_rate":
            return self._select_oracle_rate(d, active_support, q)
        else:
            return self._select_uniform_baseline(d, active_support, q)

    def _select_uniform_baseline(self, d: int, active_support: Set[int], q: int) -> List[int]:
        self.confirm_set = [c for c in self.confirm_set if c not in active_support]
        selected: List[int] = []

        q_conf_max = int(np.floor(q * self.confirm_fraction))
        for cand in self.confirm_set[:q_conf_max]:
            if len(selected) < q:
                selected.append(cand)
                self.probes_by_tier["CONFIRM"] += 1
                if self.true_support_ref and cand in self.true_support_ref:
                    self.useful_elevated_probes += 1
                else:
                    self.false_elevated_probes += 1

        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)
                self.probes_by_tier["COLD"] += 1

        return selected

    def _select_two_tier(self, d: int, active_support: Set[int], q: int) -> List[int]:
        self.warm_set = [c for c in self.warm_set if c not in active_support]
        selected: List[int] = []

        # Forced COLD coverage reservation (at least 1 probe or cold_fraction)
        q_cold_min = max(1, int(round(q * self.cold_fraction)))
        q_warm_max = max(0, q - q_cold_min)

        # 1. Fill WARM slots using warm_pointer for round-robin fairness
        n_warm = len(self.warm_set)
        if n_warm > 0 and q_warm_max > 0:
            checked = 0
            while len(selected) < q_warm_max and checked < n_warm:
                cand = self.warm_set[self.warm_pointer % n_warm]
                self.warm_pointer = (self.warm_pointer + 1) % n_warm
                checked += 1
                if cand not in selected:
                    selected.append(cand)
                    self.probes_by_tier["WARM"] += 1
                    if self.true_support_ref and cand in self.true_support_ref:
                        self.useful_elevated_probes += 1
                    else:
                        self.false_elevated_probes += 1

        # 2. Fill remaining slots via circular Round-Robin over COLD candidates
        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)
                self.probes_by_tier["COLD"] += 1

        return selected

    def _select_three_tier(self, d: int, active_support: Set[int], q: int) -> List[int]:
        self.hot_set = [c for c in self.hot_set if c not in active_support]
        self.warm_set = [c for c in self.warm_set if c not in active_support and c not in self.hot_set]
        selected: List[int] = []

        # Budget division
        q_cold_min = max(1, int(round(q * self.cold_fraction_j3)))
        q_rem = q - q_cold_min
        q_hot_max = max(0, int(round(q * self.hot_fraction_j3)))
        q_warm_max = max(0, q_rem - q_hot_max)

        # 1. Fill HOT slots
        n_hot = len(self.hot_set)
        if n_hot > 0 and q_hot_max > 0:
            checked = 0
            while len(selected) < q_hot_max and checked < n_hot:
                cand = self.hot_set[self.hot_pointer % n_hot]
                self.hot_pointer = (self.hot_pointer + 1) % n_hot
                checked += 1
                if cand not in selected:
                    selected.append(cand)
                    self.probes_by_tier["HOT"] += 1
                    if self.true_support_ref and cand in self.true_support_ref:
                        self.useful_elevated_probes += 1
                    else:
                        self.false_elevated_probes += 1

        # 2. Fill WARM slots
        n_warm = len(self.warm_set)
        if n_warm > 0 and q_warm_max > 0:
            checked = 0
            while len(selected) < (q_hot_max + q_warm_max) and checked < n_warm:
                cand = self.warm_set[self.warm_pointer % n_warm]
                self.warm_pointer = (self.warm_pointer + 1) % n_warm
                checked += 1
                if cand not in selected:
                    selected.append(cand)
                    self.probes_by_tier["WARM"] += 1
                    if self.true_support_ref and cand in self.true_support_ref:
                        self.useful_elevated_probes += 1
                    else:
                        self.false_elevated_probes += 1

        # 3. Fill remaining slots with COLD via circular Round-Robin
        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)
                self.probes_by_tier["COLD"] += 1

        return selected

    def _select_queue_multi_rate(self, d: int, active_support: Set[int], q: int) -> List[int]:
        selected: List[int] = []

        # Service schedule:
        q_cold = max(1, int(round(q * self.cold_fraction_j3)))
        q_rem = q - q_cold

        # 1. Pop from hot_queue
        hot_checked = 0
        n_hot = len(self.hot_queue)
        while len(selected) < q_rem and hot_checked < n_hot:
            c = self.hot_queue.popleft()
            hot_checked += 1
            if c not in active_support and c not in selected:
                selected.append(c)
                self.probes_by_tier["HOT"] += 1
                if self.true_support_ref and c in self.true_support_ref:
                    self.useful_elevated_probes += 1
                else:
                    self.false_elevated_probes += 1
            self.hot_queue.append(c)

        # 2. Pop from warm_queue
        warm_checked = 0
        n_warm = len(self.warm_queue)
        while len(selected) < q - q_cold and warm_checked < n_warm:
            c = self.warm_queue.popleft()
            warm_checked += 1
            if c not in active_support and c not in selected:
                selected.append(c)
                self.probes_by_tier["WARM"] += 1
                if self.true_support_ref and c in self.true_support_ref:
                    self.useful_elevated_probes += 1
                else:
                    self.false_elevated_probes += 1
            self.warm_queue.append(c)

        # 3. Pop from cold_queue to complete the q allocation
        cold_checked = 0
        n_cold = len(self.cold_queue)
        while len(selected) < q and cold_checked < n_cold:
            c = self.cold_queue.popleft()
            cold_checked += 1
            if c not in active_support and c not in selected:
                selected.append(c)
                self.probes_by_tier["COLD"] += 1
            self.cold_queue.append(c)

        # Fallback if queues didn't have enough inactive elements
        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)
                self.probes_by_tier["COLD"] += 1

        return selected

    def _select_oracle_rate(self, d: int, active_support: Set[int], q: int) -> List[int]:
        selected: List[int] = []
        if self.true_support_ref is not None:
            self.warm_set = [c for c in sorted(self.true_support_ref) if c not in active_support]
        else:
            self.warm_set = []

        q_cold_min = max(1, int(round(q * self.cold_fraction)))
        q_warm_max = max(0, q - q_cold_min)

        for cand in self.warm_set[:q_warm_max]:
            if len(selected) < q:
                selected.append(cand)
                self.probes_by_tier["WARM"] += 1
                self.useful_elevated_probes += 1

        checked = 0
        while len(selected) < q and checked < d:
            cand = self.coverage_pointer
            self.coverage_pointer = (self.coverage_pointer + 1) % d
            checked += 1
            if cand not in active_support and cand not in selected:
                selected.append(cand)
                self.probes_by_tier["COLD"] += 1

        return selected
