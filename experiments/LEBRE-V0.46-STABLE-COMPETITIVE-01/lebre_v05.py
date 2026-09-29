#!/usr/bin/env python3
"""
lebre_v05.py — LEBRE v0.5: three online experts combined by exponentially weighted aggregation.

Why (DEV evidence, previously used data only; see V05_DEV_REPORT.md):
  * On real seasonal series the decisive ingredient is DENSE, LONG memory of the target expressed RELATIVE TO THE LAST
    VALUE (NLinear normalisation, Zeng et al. AAAI 2023). The sparse structural hypothesis of v0.2-v0.4 (<= 4 lag atoms up
    to lag 32) does not match those series, and learning the level through the bias makes early structural decisions
    start-point dependent (instability).
  * On input-driven systems (internal suite I1-I14) target memory is useless or harmful and the structural LEBRE wins.
  * No single representation wins both; an online combination does, with a regret guarantee.

Experts (all predict before seeing y_t; none depends on the combination -> no feedback loop):
  A  structural LEBRE (lebre_v045.LebreV045) on the target in levels: sparse lags, latent state, change alarms.
  W  target-memory window: y_hat = y_{t-1} + s_y * sum_k w_k (y_{t-k} - y_{t-1}) / s_y, k = 1..Lw, Lw = max(96, 2 s)
     (s = sampling period declared by the environment, like the look-back of DLinear/NLinear/Chronos; 96 if unknown),
     trained online by NLMS (mu_w = 0.05). s_y = causal running std of the target (scale-free features).
  B  W + evidence-gated structural LEBRE on W's residual (LebreV045 with prune_base=True: even the current inputs must
     pass the mixture-martingale test before contributing, so B adds covariate structure only with evidence).
Aggregation (Vovk 1990; Cesa-Bianchi & Lugosi 2006, exponentially weighted average forecaster, exp-concave loss):
  w_k ∝ exp(-eta L_k),  L_k <- lam L_k + (y - y_hat_k)^2 / m,  m = running mean expert loss (scale-free);
  eta = 1, lam = 0.99 (memory ~100 steps: tracking the best expert under regime change, cf. fixed-share).
Interval: online quantile tracking of |e| of the COMBINED forecast (as C6 of v0.4; Angelopoulos et al. 2023).
Explanation: exact additive decomposition, y_hat = sum_k w_k y_hat_k with every y_hat_k decomposed exactly
  (A and B's residual through LebreV045.explain_prediction; W into last value + recent memory + seasonal memory).
Cost: O(Lw + cost(A) + cost(B)) per step; accounted in fp (~1000-2000 FP for Lw 96-288), i.e. v0.5 trades the
  <=100 FP budget of v0.4 for competitiveness. FP is not energy.
"""
import math
import os
import sys
from typing import List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lebre_v045 import LebreV045  # noqa: E402  (frozen copy, SHA-256 97af0482...)


class _TargetWindow:
    """NLinear-type window on the target, relative to the last value, NLMS-trained, scale-free."""
    def __init__(self, L: int, mu: float):
        self.L, self.mu = L, mu
        self.buf = np.zeros(0); self.w = np.zeros(L)
        self.n = 0; self.m = 0.0; self.s = 0.0
        self.last_phi = None; self.last_sd = 1.0; self.last_off = 0.0

    @property
    def sd(self):
        return math.sqrt(self.s / self.n) if self.n > 1 and self.s > 0 else 1.0

    def predict(self) -> float:
        if len(self.buf) < self.L:
            self.last_phi = None
            self.last_off = float(self.buf[-1]) if len(self.buf) else 0.0
            return self.last_off
        sd = self.sd; last = float(self.buf[-1])
        self.last_phi = (self.buf - last) / sd; self.last_sd = sd; self.last_off = last
        return last + sd * float(self.w @ self.last_phi)

    def update(self, y: float, y_hat: float):
        if self.last_phi is not None:
            e = (y - y_hat) / self.last_sd
            self.w += self.mu * e * self.last_phi / (1e-6 + float(self.last_phi @ self.last_phi))
        self.buf = np.append(self.buf, y)[-self.L:]
        self.n += 1; d = y - self.m; self.m += d / self.n; self.s += d * (y - self.m)

    def parts(self, season) -> List[Tuple[str, float]]:
        if self.last_phi is None:
            return [("memória do alvo: último valor", self.last_off)]
        c = self.last_sd * self.w * self.last_phi            # c[j] for lag k = L - j
        lag = np.arange(self.L, 0, -1)
        cut = season if season else self.L // 2
        return [("memória do alvo: último valor y(t-1)", self.last_off),
                (f"memória do alvo: defasagens 1..{cut}", float(c[lag <= cut].sum())),
                (f"memória do alvo: defasagens {cut + 1}..{self.L} (ciclo)", float(c[lag > cut].sum()))]


class LebreV05:
    def __init__(self, d: int, season: int = None, mu_w: float = 0.05, eta: float = 1.0, lam: float = 0.99,
                 alpha_cov: float = 0.1, gamma_q: float = 0.1, n_warm: int = 20):
        self.d, self.season = d, season
        self.Lw = max(96, 2 * season) if season else 96
        self.A = LebreV045(d=d)
        self.W = _TargetWindow(self.Lw, mu_w)
        self.R = LebreV045(d=d, prune_base=True)
        self.eta, self.lam = eta, lam
        self.Lk = np.zeros(3); self.mloss = None; self.wts = np.ones(3) / 3
        self.alpha_cov, self.gamma_q, self.n_warm = alpha_cov, gamma_q, n_warm
        self.qhat = None; self.e2 = None; self.cover_hits = 0; self.cover_n = 0
        self.t = 0
        self.fp = {"expert_A": 0.0, "expert_W": 0.0, "expert_B_residual": 0.0, "aggregation": 0.0, "observability": 0.0}
        self._last = None

    # ------------------------------------------------------------------ step
    def step(self, x: np.ndarray, y: float) -> float:
        fp = self.fp
        a0 = sum(self.A.fp.values()); r0 = sum(self.R.fp.values())
        pw = self.W.predict(); fp["expert_W"] += 2 * self.Lw + 4
        pa = self.A.step(x, y)
        pr = self.R.step(x, y - pw)
        pb = pw + pr
        P = np.array([pa, pb, pw])
        z = -self.eta * (self.Lk - self.Lk.min()); w = np.exp(z); w /= w.sum()
        self.wts = w
        y_hat = float(w @ P); fp["aggregation"] += 3 * 3 + 3 * 5          # 3 exp counted as 5 FP each

        # explanation frozen at prediction time
        _, pa_parts = self.A.explain_prediction(); _, pr_parts = self.R.explain_prediction()
        self._last = (y_hat, w.copy(), pa_parts, pr_parts, self.W.parts(self.season))

        # learning (each expert on its own error; no dependence on the combination)
        self.W.update(y, pw); fp["expert_W"] += 5 * self.Lw + 8
        fp["expert_A"] += sum(self.A.fp.values()) - a0
        fp["expert_B_residual"] += sum(self.R.fp.values()) - r0
        l = (y - P) ** 2
        self.mloss = float(l.mean()) if self.mloss is None else self.mloss + (1 - self.lam) * (float(l.mean()) - self.mloss)
        self.Lk = self.lam * self.Lk + l / (self.mloss + 1e-300); fp["aggregation"] += 3 * 5 + 4

        # interval on the combined forecast (quantile tracking of |e|, scale-equivariant step)
        e = y - y_hat
        self.e2 = e * e if self.e2 is None else self.e2 + (1 - self.lam) * (e * e - self.e2)
        sig = math.sqrt(max(self.e2, 1e-300))
        if self.qhat is None:
            self.qhat = 1.645 * sig
        miss = 1.0 if abs(e) > self.qhat else 0.0
        if self.t >= self.n_warm:
            self.cover_n += 1; self.cover_hits += int(miss == 0.0)
        self.qhat = max(0.0, self.qhat + self.gamma_q * sig * (miss - self.alpha_cov)); fp["observability"] += 8
        self.t += 1
        return y_hat

    # ------------------------------------------------------------------ explanation / observability
    def explain_prediction(self):
        """Exact additive decomposition: sum of parts == y_hat."""
        y_hat, w, pa_parts, pr_parts, w_parts = self._last
        parts = [(f"[estrutural, peso {w[0]:.2f}] {k}", w[0] * c) for k, c in pa_parts]
        parts += [(f"[memória, peso {w[1] + w[2]:.2f}] {k}", (w[1] + w[2]) * c) for k, c in w_parts]
        parts += [(f"[covariáveis sobre a memória, peso {w[1]:.2f}] {k}", w[1] * c) for k, c in pr_parts]
        return y_hat, parts

    def interval(self):
        return self.qhat if self.qhat is not None else float("nan")

    @property
    def events(self):
        return [(t, "A:" + a, b, c) for t, a, b, c in self.A.events] + [(t, "B:" + a, b, c) for t, a, b, c in self.R.events]

    def explain(self) -> List[str]:
        out = [f"pesos: estrutural {self.wts[0]:.2f} | memória+covariáveis {self.wts[1]:.2f} | memória pura {self.wts[2]:.2f}"]
        out += ["[A] " + s for s in self.A.explain()] + ["[B] " + s for s in self.R.explain()]
        return out

    def memory_bytes(self) -> int:
        return self.A.memory_bytes() + self.R.memory_bytes() + 8 * self.Lw + 64
