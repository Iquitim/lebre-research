"""M1 da v0.56 (candidata C5 de experiments/LEBRE-V0.56-DEV-01): a M1 da v0.55 com quatro parâmetros mudados.

A M1 é a de _precision.py (copiada sem alteração da v0.55) com:
- regressão (RLS) atualizada a cada EVERY_RLS = 4 alvos aprendidos, em vez de a cada 8 (a triagem e a escolha das
  entradas seguem a cada 8);
- bandas de defasagem das entradas [0], [1], [2-3] (as três primeiras das cinco da v0.55: defasagens 0 a 3);
- três defasagens do alvo em z, em vez de duas;
- sem o recorte de E em L ± CLIP_K·max(σ̂_L, piso).
A dormência é a da v0.55 (dormancy.py, sem alteração): no modo dormente, a M1 segue exatamente a original.

M1Param aceita os quatro parâmetros; com os valores da v0.55 (every 8, 5 bandas, 2 defasagens, recorte), a ordem de cada
operação de ponto flutuante e a contagem de operações são as da original (conferido nos testes). Transcrito de
experiments/LEBRE-V0.56-DEV-01/dev_m1.py (PrecDiag), mantendo a ordem das operações."""
import math
from collections import deque

import numpy as np

from . import _precision as P_
from ._core import CLIP_K, EVERY, N_MIN, T_MAX
from ._precision import BANDS, DELTA_RLS, PrecisionExpert
from .dormancy import DormantPrecisionExpert

V056 = dict(every=4, clip=False, ylags=3, nbands=3)              # a candidata C5
V055 = dict(every=EVERY, clip=True, ylags=2, nbands=5)           # a M1 da v0.55


class PrecisionParam(PrecisionExpert):
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


class DormantPrecisionParam(DormantPrecisionExpert, PrecisionParam):
    """a M1 com dormência (v0.55) sobre PrecisionParam"""

    def __init__(self, d, **kw):
        PrecisionParam.__init__(self, d, **kw)
        self.dormant = False; self.trial = False; self.trials = 0; self.low = 0
        self.sleeps = 0; self.wakes = 0; self.dormant_steps = 0
        self._sampled = False; self._last_sample = -1
        self.ema_g = None; self.ema_s = None; self.n_samples = 0
