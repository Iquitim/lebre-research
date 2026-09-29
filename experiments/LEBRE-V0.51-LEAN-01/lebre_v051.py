#!/usr/bin/env python3
"""
lebre_v051.py — LEBRE v0.51 (lean): two online experts and one aggregator. Nothing else.

  S  structural expert: LEBRE v0.4.5 (lebre_v045.LebreV045; sparse lags, latent state, change alarms, input guard),
     run with plain NLMS (IPNLMS off: in the aggregate it bought nothing and cost ~10 FP/step).
  M  memory expert: y_hat_M = y_{t-1} + w . phi, with
       phi = [ m - y_{t-1},                 mean reversion (lets M switch the anchor off),
               y_{t-1} - y_{t-2},           recent increment,
               y_{t-s} - y_{t-1},           seasonal-naive information,
               y_{t-s+1} - y_{t-s},         the increment that followed one cycle ago,
               G[t mod s] ]                 seasonal profile of increments: exponential smoothing per phase
                                            (the seasonal state of Holt-Winters; Box-Jenkins airline intuition),
     w by NLMS on the RAW differences (NLMS is scale-invariant: no standardisation needed).
     Without a declared period s: only mean reversion and recent increment.
     All features are relative to the last value (NLinear normalisation: no level to learn -> no start-point instability).
  Aggregation: exponentially weighted forecaster over two experts (Vovk 1990; Cesa-Bianchi & Lugosi 2006),
     w_S = 1 / (1 + exp(eta D)), D <- lam D + ((y - y_S)^2 - (y - y_M)^2) / m, m = EMA of the combined squared error
     (shared with the interval); inverse, sqrt and exp refreshed every 8 steps (rate preserved, as C6 of v0.4).
  Interval: quantile tracking of |e| of the combined forecast (Angelopoulos et al. 2023).
  Explanation: exact additive decomposition y_hat = w_S * (S parts) + (1 - w_S) * (M parts).

DEV evidence (previously used data only, dev_lean.py): M alone (~55 FP) matches/beats a dense NLinear window of 96-288
lags; the aggregate keeps the structural expert's result on the internal suite.
"""
import math
import os
import sys
from typing import List, Tuple

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lebre_s051 import StructuralExpert  # noqa: E402  (v0.4.5 + cold-start drive + dormancy gate)


class MemoryExpert:
    def __init__(self, season=None, mu=0.05, a_prof=0.1, a_mean=0.01, feats=("mean", "d1", "sn", "si", "prof"), every=8):
        self.s, self.mu, self.ap, self.am = season, mu, a_prof, a_mean
        self.feats = feats if season else tuple(f for f in ("mean", "d1", "struct") if f in feats or f in ("mean", "d1"))
        self.struct = 0.0
        self.every = every
        self.Lb = 2 * season + 2 if season else 3
        self.buf = np.zeros(self.Lb); self.n = 0
        self.mew = None
        self.G = np.zeros(season) if season else None
        self.w = np.zeros(len(self.feats))
        self.phi = None; self.last = 0.0; self.fp = 0.0

    def _b(self, k):                       # y_{t-k}
        return self.buf[(self.n - k) % self.Lb]

    def names(self):
        lab = {"mean": "reversão à média", "d1": "incremento recente", "sn": f"sazonal: y(t-{self.s})",
               "si": "incremento de um ciclo atrás", "prof": "perfil sazonal de incrementos", "l4": "y(t-4)", "l8": "y(t-8)",
               "struct": "previsão estrutural"}
        return [lab[f] for f in self.feats]

    def predict(self) -> float:
        if self.n < self.Lb:
            self.phi = None; self.last = self._b(1) if self.n else 0.0
            return self.last
        last = self._b(1)
        s = self.s
        val = {"mean": lambda: self.mew - last, "d1": lambda: last - self._b(2), "sn": lambda: self._b(s) - last,
               "si": lambda: self._b(s - 1) - self._b(s), "prof": lambda: self.G[self.n % s],
               "l4": lambda: self._b(4) - last, "l8": lambda: self._b(8) - last, "struct": lambda: self.struct - last}
        self.phi = np.array([val[k]() for k in self.feats]); self.last = last   # raw differences: NLMS is scale-invariant
        k = len(self.phi); self.fp += k + 2 * k + 1                      # differences, dot, output
        return last + float(self.w @ self.phi)

    def update(self, y: float, y_hat: float):
        k = len(self.w)
        if self.phi is not None:
            pp = float(self.phi @ self.phi)
            if pp > 0.0:
                self.w += (self.mu * (y - y_hat) / pp) * self.phi; self.fp += 1 + 2 * k + 3 + 2 * k
        if self.s and self.n >= 1:
            ph = self.n % self.s; self.G[ph] += self.ap * ((y - self._b(1)) - self.G[ph]); self.fp += 4
        self.mew = y if self.mew is None else self.mew + self.am * (y - self.mew); self.fp += 3
        self.buf[self.n % self.Lb] = y; self.n += 1

    def parts(self) -> List[Tuple[str, float]]:
        if self.phi is None:
            return [("memória: último valor", self.last)]
        c = self.w * self.phi
        return [("memória: último valor y(t-1)", self.last)] + [(f"memória: {n}", float(v)) for n, v in zip(self.names(), c)]


class LebreV051:
    def __init__(self, d: int, season: int = None, eta: float = 0.5, lam: float = 0.99,
                 alpha_cov: float = 0.1, gamma_q: float = 0.1, n_warm: int = 20, every: int = 8,
                 mem_feats=("mean", "d1", "sn", "si", "prof"), eps_dormant=0.01, **struct_kw):
        kw = {"ipnlms": False, "intervals": False}
        kw.update(struct_kw)
        self.S = StructuralExpert(d=d, **kw)
        self.M = MemoryExpert(season, feats=mem_feats, every=every); self.every = every; self.inv = None
        self.eta, self.lam = eta, lam
        self.D = 0.0; self.wS = 0.5; self.eps = eps_dormant          # D = L_S - L_M: with two experts the weights depend only on the loss difference
        self.alpha_cov, self.gamma_q, self.n_warm = alpha_cov, gamma_q, n_warm
        self.qhat = None; self.e2 = None; self.cover_hits = 0; self.cover_n = 0; self.t = 0
        self.fp_agg = 0.0; self.fp_obs = 0.0
        self._last = None

    @property
    def fp(self):
        return {"structural": sum(self.S.fp.values()), "memory": self.M.fp, "aggregation": self.fp_agg, "interval": self.fp_obs}

    def step(self, x: np.ndarray, y: float) -> float:
        pm = self.M.predict()
        ps = self.S.step(x, y)
        wS = self.wS
        y_hat = pm + wS * (ps - pm); self.fp_agg += 3
        _, s_parts = self.S.explain_prediction()
        self._last = (y_hat, wS, s_parts, self.M.parts())
        self.M.update(y, pm)
        es, em, e = y - ps, y - pm, y - y_hat
        self.e2 = e * e if self.e2 is None else self.e2 + (1 - self.lam) * (e * e - self.e2)   # shared: loss scale + interval
        refresh = self.t % self.every == 0 or self.inv is None
        if refresh:
            self.inv = 1.0 / (self.e2 + 1e-300); self.sig = math.sqrt(max(self.e2, 1e-300)); self.fp_agg += 2
        self.D = self.lam * self.D + (es - em) * (es + em) * self.inv     # ls - lm = (es - em)(es + em)
        self.fp_agg += 3 + 4 + 6                                       # errors, e2 EMA, loss-difference EMA
        if refresh:                                                   # weight: one exp every `every` steps
            z = self.eta * self.D
            self.wS = 1.0 / (1.0 + math.exp(z)) if z < 700 else 0.0; self.fp_agg += 4
            self.S.dormant = self.wS < self.eps                        # structural evidence pauses while S is negligible
        if self.qhat is None:
            self.qhat = 1.645 * self.sig
        miss = 1.0 if abs(e) > self.qhat else 0.0
        if self.t >= self.n_warm:
            self.cover_n += 1; self.cover_hits += int(miss == 0.0)
        if refresh:                                                   # step x every keeps the stream-time rate (as C6)
            self.qhat = max(0.0, self.qhat + self.every * self.gamma_q * self.sig * (miss - self.alpha_cov)); self.fp_obs += 3
        self.fp_obs += 2
        self.t += 1
        return y_hat

    def explain_prediction(self):
        y_hat, wS, s_parts, m_parts = self._last
        parts = [(f"[estrutural, peso {wS:.2f}] {k}", wS * c) for k, c in s_parts]
        parts += [(f"[memória, peso {1 - wS:.2f}] {k}", (1 - wS) * c) for k, c in m_parts]
        return y_hat, parts

    def interval(self):
        return self.qhat if self.qhat is not None else float("nan")

    @property
    def events(self):
        return self.S.events

    @property
    def wts(self):
        return np.array([self.wS, 1 - self.wS])

    def explain(self) -> List[str]:
        out = [f"peso: estrutural {self.wS:.2f} | memória {1 - self.wS:.2f}",
               "memória: " + ", ".join(f"{n} {w:+.3f}" for n, w in zip(self.M.names(), self.M.w))]
        return out + ["[estrutural] " + s for s in self.S.explain()]

    def memory_bytes(self) -> int:
        return self.S.memory_bytes() + 4 * (self.M.Lb + (self.M.s or 0) + len(self.M.w) + 6) + 40
