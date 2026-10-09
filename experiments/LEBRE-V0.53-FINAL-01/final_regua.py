"""final_regua.py — peças da régua por decidibilidade, copiadas sem mudança de comportamento do LEBRE Lab (commit 0d00941):
referências triviais (lab/baselines.py: Zero, Naive, SeasonalNaive), bootstrap de blocos pareado (analises/m2_dev.py:
par_bootstrap, B = 2000), contagem de entradas externas aceitas (analises/m2_dev.py: externas) e estrutura sem a porta
(analises/m2_dev_r1.py: estrutura). Regras: experiments/LEBRE-V0.53-DESIGN-NOTE-01/M2_CANDIDATA_D.md (com os adendos 1 a 3).
"""
import math

import numpy as np

B = 2000


class _Base:
    def __init__(self, n_inputs):
        self.d = n_inputs
        self.hist = []

    def _last(self, k=1):
        seen = 0
        for v in reversed(self.hist):
            if not math.isnan(v):
                seen += 1
                if seen == k:
                    return v
        return math.nan

    def observe(self, y):
        self.hist.append(math.nan if y is None or (isinstance(y, float) and math.isnan(y)) else float(y))


class Zero(_Base):
    def predict(self, x):
        return 0.0


class Naive(_Base):
    def predict(self, x):
        return self._last()


class SeasonalNaive(_Base):
    def __init__(self, n_inputs, season):
        super().__init__(n_inputs)
        self.s = int(season)

    def predict(self, x):
        if len(self.hist) >= self.s and not math.isnan(self.hist[-self.s]):
            return self.hist[-self.s]
        return self._last()


def ref_modelo(nome, d, season):
    return Zero(d) if nome == "zero" else (SeasonalNaive(d, season) if nome == "sazonal" else Naive(d))


def rodar_ref(r, X, y):
    T = len(y)
    f = np.full(T, np.nan)
    for t in range(T):
        f[t] = r.predict(X[t])
        r.observe(None if not math.isfinite(y[t]) else float(y[t]))
    return f


def par_bootstrap(y, a, b, ini, L, rng):
    ok = np.isfinite(y) & np.isfinite(a) & np.isfinite(b)
    ok[:ini] = False
    la, lb = np.where(ok, (y - a) ** 2, 0.0), np.where(ok, (y - b) ** 2, 0.0)
    ponto = la[ok].sum() / lb[ok].sum()
    ca, cb = np.r_[0, np.cumsum(la[ini:])], np.r_[0, np.cumsum(lb[ini:])]
    n = len(la) - ini
    m = n // L
    st = rng.integers(0, n - L + 1, size=(B, m))
    with np.errstate(divide="ignore", invalid="ignore"):
        rep = np.log((ca[st + L] - ca[st]).sum(1) / (cb[st + L] - cb[st]).sum(1))
    return float(ponto), rep


def ic(rep):
    rep = rep[np.isfinite(rep)]
    return [float(np.exp(np.quantile(rep, 0.025))), float(np.exp(np.quantile(rep, 0.975)))]


def externas(events):
    return sum(1 for e in events if e.outcome == "accepted" and e.added and e.added.startswith("x"))


def estrutura(m):
    return [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.events if e.change != "gate"]


def limite_choque(n):
    """Adendo 3: máx(5%, 5 × 2 ln(n)/n), n = passos avaliados com erro da referência finito."""
    return max(0.05, 5 * 2 * math.log(n) / n) if n > 1 else 1.0
