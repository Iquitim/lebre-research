"""newmodels.py — comparators added in BENCH-04 (all step(x_norm, y_raw) -> (pred, flops)).

Online DLinear / NLinear   Zeng et al., AAAI 2023 ("Are Transformers Effective for Time Series Forecasting?");
                           here trained online by normalised LMS on the target's own look-back window (channel-independent).
QKLMS                      Chen, Zhao, Zhu & Principe, IEEE TNNLS 2012 (quantized kernel LMS, Gaussian kernel), dictionary budget.
RFF-NLMS                   random Fourier features (Rahimi & Recht 2007) + NLMS (Bouboulis et al. 2018, "online RFF kernel filters").
Holt-Winters (additive)    classic exponential smoothing, online, fixed smoothing constants (calibrated).
River AMRules / PA         Almeida et al. 2013 (adaptive model rules); Crammer et al. 2006 (passive-aggressive regression).
"""
import math

import numpy as np


class _Z:
    """causal running mean / std of the raw target (Welford), used only to put targets on unit scale."""
    def __init__(self):
        self.n = 0; self.m = 0.0; self.s = 0.0

    def upd(self, v):
        self.n += 1; d = v - self.m; self.m += d / self.n; self.s += d * (v - self.m)

    @property
    def sd(self):
        return math.sqrt(self.s / self.n) if self.n > 1 and self.s > 0 else 1.0


class OnlineLTSF:
    """kind='dlinear': series decomposition (moving average, kernel 25) + one linear map on [trend, remainder];
       kind='nlinear': subtract the last value, linear map, add it back. Look-back L on the target only."""
    def __init__(self, L, kind, mu=0.05, kernel=25):
        self.L, self.kind, self.mu, self.k = L, kind, mu, kernel
        self.buf = np.zeros(0); self.z = _Z()
        self.w = np.zeros(2 * L if kind == "dlinear" else L)
        self.phi = None

    def _feat(self):
        sd = self.z.sd
        if self.kind == "nlinear":
            last = self.buf[-1]
            return (self.buf - last) / sd, last, sd
        h = self.k // 2
        pad = np.concatenate([np.full(h, self.buf[0]), self.buf, np.full(h, self.buf[-1])])
        c = np.cumsum(np.insert(pad, 0, 0.0))
        trend = (c[self.k:] - c[:-self.k]) / self.k
        mu = self.z.m
        return np.concatenate([(trend - mu) / sd, (self.buf - trend) / sd]), mu, sd

    def step(self, x, y):
        y = float(y)
        if len(self.buf) < self.L:
            p = self.buf[-1] if len(self.buf) else 0.0
            self.buf = np.append(self.buf, y); self.z.upd(y)
            return float(p), 0.0
        phi, off, sd = self._feat()
        p = off + sd * float(self.w @ phi)
        e = (y - p) / sd
        self.w += self.mu * e * phi / (1e-6 + float(phi @ phi))
        self.buf = np.append(self.buf[1:], y); self.z.upd(y)
        n = len(self.w)
        return float(p), float(6 * n + (4 * self.L if self.kind == "dlinear" else self.L) + 6)

    def get_memory_bytes(self):
        return 4 * (len(self.w) + self.L)

    def get_active_params(self):
        return len(self.w)


class QKLMS:
    def __init__(self, d, eta=0.5, width=1.0, eps_rel=0.5, budget=500):
        self.g = 1.0 / (2.0 * width * width * d)
        self.eps2 = (eps_rel * width) ** 2 * d
        self.eta, self.budget, self.d = eta, budget, d
        self.C = np.zeros((0, d)); self.a = np.zeros(0); self.z = _Z()

    def step(self, x, y):
        x = np.asarray(x, float); y = float(y); sd = self.z.sd; mu = self.z.m
        n = len(self.a)
        if n:
            d2 = ((self.C - x) ** 2).sum(1)
            f = float(self.a @ np.exp(-self.g * d2))
        else:
            d2 = np.zeros(0); f = 0.0
        p = mu + sd * f
        e = (y - p) / sd
        if n and (d2.min() <= self.eps2 or n >= self.budget):
            j = int(d2.argmin()); self.a[j] += self.eta * e
        else:
            self.C = np.vstack([self.C, x]); self.a = np.append(self.a, self.eta * e)
        self.z.upd(y)
        return float(p), float(n * (3 * self.d + 25) + 10)

    def get_memory_bytes(self):
        return 4 * len(self.a) * (self.d + 1)

    def get_active_params(self):
        return len(self.a)


class RffNlms:
    def __init__(self, d, width=1.0, mu=0.5, nf=256, seed=0):
        rng = np.random.RandomState(seed)
        self.W = rng.normal(scale=1.0 / (width * math.sqrt(d)), size=(nf, d))
        self.b = rng.uniform(0, 2 * math.pi, nf); self.s = math.sqrt(2.0 / nf)
        self.w = np.zeros(nf + 1); self.mu = mu; self.z = _Z(); self.d = d

    def step(self, x, y):
        phi = np.append(self.s * np.cos(self.W @ np.asarray(x, float) + self.b), 1.0)
        sd, mu = self.z.sd, self.z.m
        p = mu + sd * float(self.w @ phi); e = (float(y) - p) / sd
        self.w += self.mu * e * phi / (1e-6 + float(phi @ phi)); self.z.upd(float(y))
        n = len(self.w)
        return float(p), float(2 * (n - 1) * self.d + 20 * (n - 1) + 6 * n)

    def get_memory_bytes(self):
        return 4 * (len(self.w) + self.W.size + len(self.b))

    def get_active_params(self):
        return len(self.w)


class HoltWinters:
    """additive Holt-Winters (seasonal) or Holt linear (s=None), updated online on the raw target."""
    def __init__(self, s, alpha=0.3, beta=0.01, gamma=0.1):
        self.s, self.a, self.b, self.g = s, alpha, beta, gamma
        self.hist = []; self.l = None; self.tr = 0.0; self.S = None; self.t = 0

    def step(self, x, y):
        y = float(y); s = self.s
        if self.l is None:
            self.hist.append(y)
            need = 2 * s if s else 2
            if len(self.hist) < need:
                return (self.hist[-2] if len(self.hist) > 1 else 0.0), 0.0
            h = np.array(self.hist)
            if s:
                self.l = h[s:].mean(); self.tr = (h[s:].mean() - h[:s].mean()) / s
                self.S = list(h[s:] - h[s:].mean())
            else:
                self.l = h[-1]; self.tr = h[-1] - h[-2]
            return float(h[-1]), 0.0
        seas = self.S[self.t % s] if s else 0.0
        p = self.l + self.tr + seas
        l_old = self.l
        self.l = self.a * (y - seas) + (1 - self.a) * (self.l + self.tr)
        self.tr = self.b * (self.l - l_old) + (1 - self.b) * self.tr
        if s:
            self.S[self.t % s] = self.g * (y - self.l) + (1 - self.g) * seas
        self.t += 1
        return float(p), 20.0

    def get_memory_bytes(self):
        return 4 * ((self.s or 0) + 3)

    def get_active_params(self):
        return (self.s or 0) + 2


class RiverNew:
    def __init__(self, kind, seed, C=0.1):
        from river import compose, linear_model, preprocessing, rules
        self.m = {"RIVER_AMRULES": lambda: compose.Pipeline(preprocessing.StandardScaler(), rules.AMRules()),
                  "RIVER_PA": lambda: compose.Pipeline(preprocessing.StandardScaler(), linear_model.PARegressor(C=C))}[kind]()
        self.z = _Z()

    def step(self, x, y):
        xi = {i: float(v) for i, v in enumerate(x)}
        sd, mu = self.z.sd, self.z.m
        p = self.m.predict_one(xi)
        p = mu + sd * float(p) if p is not None and np.isfinite(p) else mu
        self.m.learn_one(xi, (float(y) - mu) / sd); self.z.upd(float(y))
        return float(p), float("nan")

    def get_memory_bytes(self):
        return -1

    def get_active_params(self):
        return -1


def lookback(season):
    return max(96, 2 * season) if season else 96


GRIDS = {
    "DLINEAR_ONLINE": [{"mu": m} for m in (0.01, 0.05, 0.2)],
    "NLINEAR_ONLINE": [{"mu": m} for m in (0.01, 0.05, 0.2)],
    "QKLMS": [{"eta": e, "width": w} for e in (0.2, 0.5) for w in (0.5, 1.0, 2.0)],
    "RFF_NLMS": [{"mu": m, "width": w} for m in (0.1, 0.5) for w in (0.5, 1.0, 2.0)],
    "RIVER_PA": [{"C": c} for c in (0.001, 0.01, 0.1)],
    "HOLT_WINTERS": [{"alpha": a, "beta": b, "gamma": g} for a in (0.1, 0.3, 0.6) for b in (0.0, 0.01) for g in (0.05, 0.2)],
}
NEW_ONLINE = ["DLINEAR_ONLINE", "NLINEAR_ONLINE", "QKLMS", "RFF_NLMS", "HOLT_WINTERS", "RIVER_AMRULES", "RIVER_PA"]


def make_new(model_id, D, cfg, seed, season):
    if model_id == "DLINEAR_ONLINE":
        return OnlineLTSF(lookback(season), "dlinear", **cfg)
    if model_id == "NLINEAR_ONLINE":
        return OnlineLTSF(lookback(season), "nlinear", **cfg)
    if model_id == "QKLMS":
        return QKLMS(D, **cfg)
    if model_id == "RFF_NLMS":
        return RffNlms(D, seed=seed, **cfg)
    if model_id == "HOLT_WINTERS":
        return HoltWinters(season, **cfg)
    return RiverNew(model_id, seed, **cfg)
