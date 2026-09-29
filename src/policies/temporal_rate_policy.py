from typing import Set, List, Dict, Optional, Any, Tuple
from collections import deque
from .tiered_rate_policy import TieredEvidenceRatePolicy
from ..utils.temporal_buffer import cand_to_pair, pair_to_cand

class TemporalRatePolicy(TieredEvidenceRatePolicy):
    """
    TemporalRatePolicy for Milestone M2 (M2-EXP-0001 and M2-EXP-0002):
    Extends the validated M1 J4 queue_multi_rate policy to (feature, lag) candidate spaces.
    
    Variants supported:
    - 'T0' / 'U0': Current-Time-Only Control (candidates restricted strictly to lag 0: c in [0, D-1]).
    - 'T1' / 'U1': Full Temporal Candidate Space (all D * (L_max + 1) candidates in standard J4 queue).
    - 'T2' / 'U2': Lag-Fair Coverage (cold queue interleaved across lags to guarantee equal lag exploration).
    - 'T3' / 'U3': Lag-Aware Queue Decay (queue decay accounts for lag-specific evidence staleness).
    - 'T4': Oracle Lag Diagnostic for single delay (restricted strictly to oracle_delay).
    - 'T5' / 'U6': Oracle Full Temporal Set (ceiling; zero exploration probes).
    - 'U4': Oracle Feature Diagnostic: Candidate pool restricted strictly to true feature IDs across all lags.
    - 'U5': Oracle Lag-Set Diagnostic: Candidate pool restricted strictly to true lag values across all features.
    """
    def __init__(
        self,
        d_features: int = 20,
        l_max: int = 10,
        variant: str = "T1",
        oracle_delay: Optional[int] = None,
        oracle_features: Optional[Set[int]] = None,
        oracle_lags: Optional[Set[int]] = None,
        # Inherit standard frozen M1 parameters
        c_max: int = 3,
        n_screen: int = 3,
        theta_screen: float = 0.20,
        gamma_screen: float = 0.75,
        theta_drop: float = 0.10,
        gamma_drop: float = 0.60,
        confirm_max_probes: int = 12,
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
        warm_fraction: float = 0.65
    ):
        self.d_features = d_features
        self.l_max = l_max
        self.n_lags = l_max + 1
        self.total_candidates = d_features * self.n_lags
        self.variant = variant.upper()
        self.oracle_delay = oracle_delay
        self.oracle_features = oracle_features
        self.oracle_lags = oracle_lags
        
        # Initialize superclass with total_candidates as dimension d
        super().__init__(
            d=self.total_candidates,
            mode="queue_multi_rate",
            c_max=c_max,
            n_screen=n_screen,
            theta_screen=theta_screen,
            gamma_screen=gamma_screen,
            theta_drop=theta_drop,
            gamma_drop=gamma_drop,
            confirm_max_probes=confirm_max_probes,
            w_max=w_max,
            h_max=h_max,
            n_hint=n_hint,
            theta_hint=theta_hint,
            gamma_hint=gamma_hint,
            theta_decay=theta_decay,
            warm_max_probes=warm_max_probes,
            hot_max_probes=hot_max_probes,
            theta_hot=theta_hot,
            gamma_hot=gamma_hot,
            cold_fraction=cold_fraction,
            warm_fraction=warm_fraction
        )

        # Re-initialize cold_queue based on experimental variant
        self._configure_candidate_pools()

    def _configure_candidate_pools(self) -> None:
        """Configures the cold queue ordering and candidate restrictions based on variant."""
        self.cold_queue.clear()
        self.warm_queue.clear()
        self.hot_queue.clear()
        self.allowed_candidates: Optional[Set[int]] = None

        if self.variant in ("T0", "U0"):
            # Current-time-only: strictly lag 0 candidates c in [0, d_features - 1]
            self.allowed_candidates = set(range(self.d_features))
            for c in range(self.d_features):
                self.cold_queue.append(c)

        elif self.variant in ("T1", "U1"):
            # Full temporal candidate space: standard sequential indexing [0, ..., N-1]
            self.allowed_candidates = set(range(self.total_candidates))
            for c in range(self.total_candidates):
                self.cold_queue.append(c)

        elif self.variant in ("T2", "U2"):
            # Lag-Fair Coverage: Interleave candidate order across lags
            # Lag 0 feat 0, Lag 1 feat 0, ..., Lag L feat 0, Lag 0 feat 1, ...
            self.allowed_candidates = set(range(self.total_candidates))
            for j in range(self.d_features):
                for ell in range(self.n_lags):
                    c = pair_to_cand(j, ell, self.d_features)
                    self.cold_queue.append(c)

        elif self.variant in ("T3", "U3"):
            # Lag-Aware Queue Decay: uses full candidate space, but modifies decay
            self.allowed_candidates = set(range(self.total_candidates))
            for c in range(self.total_candidates):
                self.cold_queue.append(c)

        elif self.variant == "T4":
            # Oracle Lag Diagnostic: restricted strictly to oracle_delay
            d_star = 0 if self.oracle_delay is None else self.oracle_delay
            self.allowed_candidates = set(
                pair_to_cand(j, d_star, self.d_features) for j in range(self.d_features)
            )
            for c in sorted(list(self.allowed_candidates)):
                self.cold_queue.append(c)

        elif self.variant == "U4":
            # Oracle Feature Diagnostic: restricted strictly to oracle_features across all lags
            feats = set() if self.oracle_features is None else self.oracle_features
            self.allowed_candidates = set(
                pair_to_cand(j, ell, self.d_features)
                for j in feats
                for ell in range(self.n_lags)
            )
            for c in sorted(list(self.allowed_candidates)):
                self.cold_queue.append(c)

        elif self.variant == "U5":
            # Oracle Lag-Set Diagnostic: restricted strictly to oracle_lags across all features
            lags = set() if self.oracle_lags is None else self.oracle_lags
            self.allowed_candidates = set(
                pair_to_cand(j, ell, self.d_features)
                for j in range(self.d_features)
                for ell in lags
            )
            for c in sorted(list(self.allowed_candidates)):
                self.cold_queue.append(c)

        elif self.variant in ("T5", "U6"):
            # Oracle Full Temporal Set: ceiling; zero exploration probes
            self.allowed_candidates = set()
            self.cold_queue.clear()

        else:
            raise ValueError(f"Unknown M2 variant: {self.variant}")

    def select_candidates(
        self,
        d: int,
        active_support: Set[int],
        q: int,
        cand_stats: Optional[Dict[str, Any]] = None,
        true_support: Optional[Set[int]] = None,
        **kwargs
    ) -> List[int]:
        if self.variant in ("T5", "U6") or q <= 0:
            return []

        # If T3/U3, apply lag-aware decay adjustments before calling standard update
        if self.variant in ("T3", "U3") and cand_stats is not None:
            self._apply_lag_aware_decay(cand_stats, active_support)

        # Call superclass queue_multi_rate candidate selection
        candidates = super().select_candidates(
            d=d,
            active_support=active_support,
            q=q,
            cand_stats=cand_stats,
            true_support=true_support,
            **kwargs
        )

        # Enforce variant candidate restrictions if applicable
        if self.allowed_candidates is not None:
            filtered = [c for c in candidates if c in self.allowed_candidates]
            return filtered

        return candidates

    def _apply_lag_aware_decay(self, cand_stats: Dict[str, Any], active_support: Set[int]) -> None:
        """
        T3 / U3: Adjusts queue decay for candidates based on lag staleness.
        Older lags experience faster decay when uncorroborated, clearing queue slots.
        """
        cand_n = cand_stats["n"]
        cand_mean = cand_stats["mean"]
        cand_pos = cand_stats.get("pos")
        cand_neg = cand_stats.get("neg")

        for queue in [self.warm_queue, self.hot_queue]:
            demoted = []
            for c in list(queue):
                if c in active_support:
                    continue
                _, ell = cand_to_pair(c, self.d_features)
                # Lag factor: older lags (ell > 2) require tighter evidence retention
                lag_decay_factor = 1.0 + 0.1 * ell
                effective_theta = self.theta_decay * lag_decay_factor
                mean_val = abs(cand_mean[c])

                if mean_val < effective_theta:
                    demoted.append(c)

            for c in demoted:
                if c in queue:
                    queue.remove(c)
                if c not in self.cold_queue:
                    self.cold_queue.append(c)
                cand_stats["n"][c] = 0
                cand_stats["mean"][c] = 0.0
                cand_stats["m2"][c] = 0.0
                if cand_pos is not None: cand_stats["pos"][c] = 0
                if cand_neg is not None: cand_stats["neg"][c] = 0
