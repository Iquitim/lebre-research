"""dev_m1.py — variantes da M1 da etapa LEBRE-V0.56-DEV-01 (PLANO_DEV_M1_BARATA.md, §2).

PrecDiag reescreve predict, _select e observe da PrecisionExpert congelada (lebre055/_precision.py, commit b0522a0), como
em LEBRE-V0.56-DIAG-02/diag_m1.py, com uma chave a mais, o número de bandas de defasagem das entradas (as primeiras
`nbands` de [0], [1], [2-3], [4-7], [8-15]). Com as chaves no padrão (every 8, recorte, 2 defasagens do alvo, 5 bandas),
a ordem de cada operação de ponto flutuante é a da original. M1Dev = DormantPrecisionExpert sobre PrecDiag (a M1 da v0.55,
com dormência; no modo dormente, exatamente a original).

Teste de fumaça (python dev_m1.py): com as chaves no padrão, previsões idênticas, bit a bit, às da v0.55 (B10) numa bacia
de fumaça e numa série sintética com 8 entradas.
Uso: LEBRE055_PROTO=<pasta LEBRE-V0.55-PROTO-01 no commit b0522a0> python dev_m1.py"""
import math
import os
import sys
from collections import deque

import numpy as np

VARIANTES = {"A": None,
             "C0": dict(every=1, nbands=5), "C1": dict(every=2, nbands=5), "C2": dict(every=4, nbands=5),
             "C3": dict(every=1, nbands=3), "C4": dict(every=2, nbands=3), "C5": dict(every=4, nbands=3),
             "C6": dict(every=8, nbands=3)}
COMUM = dict(clip=False, ylags=3)                                 # §2: em todas as variantes C


def classes():
    p = os.environ["LEBRE055_PROTO"]
    if p not in sys.path:
        sys.path.insert(0, p)
    from lebre055._core import CLIP_K, EVERY, N_MIN, T_MAX
    from lebre055._precision import BANDS, DELTA_RLS, PrecisionExpert
    from lebre055.dormancy import DormantPrecisionExpert
    from lebre055.model055 import Lebre055
    import lebre055._precision as P_

    class PrecDiag(PrecisionExpert):
        def __init__(self, d, every=EVERY, clip=True, ylags=2, nbands=5):
            super().__init__(d)
            self.every, self.clip, self.K = int(every), bool(clip), int(ylags)
            self.bands = BANDS[:int(nbands)]
            self.yobs = deque(maxlen=self.K)

        def predict(self, x, L):
            x = self._fill(x)
            self._x = x
            self.buf.append(x)
            if self.sel is None:
                self.z = None; self.e = None
                return L
            self.bufz.append((x[self.sel] - self.mu) / self.sd)
            H = np.asfortranarray(list(reversed(self.bufz)))
            bands = [H[a:b + 1].mean(0) if len(H) > a else np.zeros(len(self.sel)) for a, b in self.bands]
            ys = list(self.yobs)[::-1] + [self.muy] * (self.K - len(self.yobs))
            z = np.concatenate([[1.0], (np.array(ys[:self.K]) - self.muy) / self.sdy, np.ravel(np.array(bands).T)])
            self.z = z
            k = len(z)
            self.fp += 2 * k + (2 + sum(b - a + 1 for a, b in self.bands)) * len(self.sel) + 4   # nova linha 2m; médias
            if self.n_rls < k:
                self.e = None
                return L
            self.e = float(self.w @ z)
            if self.e2_core is None:
                self.e = None
                return L
            if self.clip:
                B = CLIP_K * max(math.sqrt(self.e2_core), self._floor)
                self.e = min(max(self.e, L - B), L + B)
                self.fp += 4
            if self.ag.n < N_MIN:
                return L
            w = self.ag.weights()
            return float(w[0] * L + w[1] * self.e)

        def _select(self):
            vx = np.maximum(self.m[1] - self.m[0] ** 2, 0.0)
            vy = max(self.my2 - self.my ** 2, 0.0)
            cov = self.m[2] - self.m[0] * self.my
            with np.errstate(divide="ignore", invalid="ignore"):
                r = np.where((vx > 0) & (vy > 0), np.abs(cov) / np.sqrt(vx * vy), 0.0)
            sel = np.sort(np.argsort(-r, kind="stable")[:min(P_.M_MAX, self.d)])
            if self.sel is None or not np.array_equal(sel, self.sel):
                self.sel = sel
                self.mu = self.m[0][sel].copy(); self.sd = np.sqrt(np.maximum(vx[sel], 1e-24))
                self.muy = self.my; self.sdy = math.sqrt(max(vy, 1e-24))
                k = 1 + self.K + len(self.bands) * len(sel)
                self.w = np.zeros(k); self.P = np.eye(k) * DELTA_RLS; self.n_rls = 0
                self.ag = P_.AdaHedge(2)
                self.bufz = deque(((row[sel] - self.mu) / self.sd for row in self.buf), maxlen=16)
                self.fp += 2 * len(self.buf) * len(sel)
            self.n_sel = self.n_obs
            self.fp += 6 * self.d

        def observe(self, y, L_core, learn, floor):
            e_core = (y - L_core) ** 2
            if self.e is not None:
                le = (y - self.e) ** 2
                if math.isfinite(e_core) and math.isfinite(le):
                    self.ag.update((e_core, le))
                self.fp += P_.FP_ADAHEDGE_STEP
            self.e2_core = e_core if self.e2_core is None else self.e2_core + (1 - P_.LAM) * (e_core - self.e2_core)
            self._floor = floor
            if learn:
                self.n_obs += 1
                if self.n_obs % EVERY == 0:
                    self._screen(self._x, y)
                if self.n_obs % self.every == 0 and self.z is not None:
                    self._rls(self.z, y)
                if self.n_obs >= N_MIN and (self.sel is None or self.n_obs - self.n_sel >= T_MAX):
                    self._select()
            self.yobs.append(float(y))

    class M1Dev(DormantPrecisionExpert, PrecDiag):
        def __init__(self, d, **kw):
            PrecDiag.__init__(self, d, **kw)
            self.dormant = False; self.trial = False; self.trials = 0; self.low = 0
            self.sleeps = 0; self.wakes = 0; self.dormant_steps = 0
            self._sampled = False; self._last_sample = -1
            self.ema_g = None; self.ema_s = None; self.n_samples = 0

    def novo(var, d, season=None, season2=None, reference="persistence", padrao=False):
        """padrao=True: M1Dev com as chaves no padrão (só para o teste de fumaça)"""
        m = Lebre055(d, season=season, season2=season2, reference=reference, variant="B10")
        if padrao:
            m._m1 = M1Dev(m.n_inputs)
        elif VARIANTES[var] is not None:
            m._m1 = M1Dev(m.n_inputs, **COMUM, **VARIANTES[var])
        return m

    return novo


def rodar(m, y, X, q=None):
    f = np.full(len(y), np.nan)
    for t in range(len(y)):
        f[t] = m.predict(X[t]).value
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]) if q is not None else False)
    return f


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "LEBRE-V0.56-DIAG-01"))
    import diag_dados as DD
    C, pos = DD.conjuntos()
    novo = classes()
    s = DD.carregar(C["fumaca"][0], C, pos)
    a = rodar(novo("A", 3), s["y"], s["X"], s["q"]); b = rodar(novo("A", 3, padrao=True), s["y"], s["X"], s["q"])
    assert np.array_equal(a, b, equal_nan=True)
    rng = np.random.default_rng(12345); T = 6000; X = rng.standard_normal((T, 8))
    y = 0.6 * np.r_[0.0, X[:-1, 2]] + 0.3 * np.r_[0.0, 0.0, X[:-2, 5]] + 0.4 * rng.standard_normal(T)
    ma, mb = novo("A", 8), novo("A", 8, padrao=True)
    a = rodar(ma, y, X); b = rodar(mb, y, X)
    assert np.array_equal(a, b, equal_nan=True) and ma.cost_per_step == mb.cost_per_step, (ma.cost_per_step, mb.cost_per_step)
    m = novo("C5", 8); rodar(m, y, X)
    print("fumaça ok: chaves no padrão = v0.55 bit a bit (bacia e sintética com 8 entradas); C5 roda; custo", round(m.cost_per_step))
