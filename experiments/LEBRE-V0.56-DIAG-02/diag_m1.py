"""diag_m1.py — variantes da M1 do diagnóstico (PLANO_DIAG_M1.md, §3).

PrecDiag reescreve predict, _select e observe da PrecisionExpert congelada (lebre055/_precision.py, commit b0522a0) com
quatro chaves; com os valores padrão, a ordem de cada operação de ponto flutuante é a mesma da original:
- every: período, em alvos aprendidos, da atualização do RLS (padrão 8 = EVERY; a triagem segue a cada 8);
- clip: recorte de E em L ± CLIP_K·max(σ̂_L, piso) (padrão True);
- ylags: defasagens do alvo em z (padrão 2);
e a dormência é dada pela classe: M1Diag = DormantPrecisionExpert sobre PrecDiag (a M1 da v0.54/v0.55); PrecDiag sozinha
é a M1 da v0.53 (sem dormência). No modo dormente, a M1Diag segue exatamente a DormantPrecisionExpert (as chaves só
mudam o modo ativo). E antes do recorte fica em e_raw.

Teste de fumaça (python diag_m1.py): com as chaves no padrão, previsões idênticas, bit a bit, às da v0.55 (B10) numa bacia
de fumaça.
Uso: LEBRE055_PROTO=<pasta LEBRE-V0.55-PROTO-01 no commit b0522a0> python diag_m1.py"""
import math
import os
import sys
from collections import deque

import numpy as np

VARIANTES = {"M0": dict(), "M1": dict(every=1), "M2": dict(clip=False), "M3": dict(ylags=3), "M4": dict(dormant=False),
             "M5": dict(every=1, clip=False, ylags=3)}


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
        def __init__(self, d, every=EVERY, clip=True, ylags=2):
            super().__init__(d)
            self.every, self.clip, self.K = int(every), bool(clip), int(ylags)
            self.yobs = deque(maxlen=self.K); self.e_raw = None

        def predict(self, x, L):
            x = self._fill(x)
            self._x = x
            self.buf.append(x)
            self.e_raw = None
            if self.sel is None:
                self.z = None; self.e = None
                return L
            self.bufz.append((x[self.sel] - self.mu) / self.sd)
            H = np.asfortranarray(list(reversed(self.bufz)))
            bands = [H[a:b + 1].mean(0) if len(H) > a else np.zeros(len(self.sel)) for a, b in BANDS]
            ys = list(self.yobs)[::-1] + [self.muy] * (self.K - len(self.yobs))
            z = np.concatenate([[1.0], (np.array(ys[:self.K]) - self.muy) / self.sdy, np.ravel(np.array(bands).T)])
            self.z = z
            k = len(z)
            self.fp += 2 * k + 18 * len(self.sel) + 4
            if self.n_rls < k:
                self.e = None
                return L
            self.e = float(self.w @ z)
            if self.e2_core is None:
                self.e = None
                return L
            self.e_raw = self.e
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
                k = 1 + self.K + len(BANDS) * len(sel)
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

    class M1Diag(DormantPrecisionExpert, PrecDiag):
        def __init__(self, d, every=EVERY, clip=True, ylags=2):
            PrecDiag.__init__(self, d, every=every, clip=clip, ylags=ylags)
            self.dormant = False; self.trial = False; self.trials = 0; self.low = 0
            self.sleeps = 0; self.wakes = 0; self.dormant_steps = 0
            self._sampled = False; self._last_sample = -1
            self.ema_g = None; self.ema_s = None; self.n_samples = 0

        def predict(self, x, L):
            if self.dormant:
                self.e_raw = None
            return DormantPrecisionExpert.predict(self, x, L)

    def novo(var, d=3, reference="persistence"):
        kw = dict(VARIANTES[var])
        dormente = kw.pop("dormant", True)
        m = Lebre055(d, season=None, season2=None, reference=reference, variant="B10")
        m._m1 = (M1Diag if dormente else PrecDiag)(m.n_inputs, **kw)
        return m

    return novo, Lebre055


def rodar(m, s, gravar=False):
    y, X, q = s["y"], s["X"], s["q"]
    T = len(y); f = np.full(T, np.nan)
    G = {k: np.full(T, np.nan) for k in ("nucleo", "e_raw", "e", "omega", "Lp", "dorme")} if gravar else None
    for t in range(T):
        f[t] = m.predict(X[t]).value
        if gravar:
            m1 = m._m1
            G["nucleo"][t] = m._L_core; G["Lp"][t] = m._L
            G["e_raw"][t] = np.nan if m1.e_raw is None else m1.e_raw
            G["e"][t] = np.nan if m1.e is None else m1.e
            G["omega"][t] = m1.weight(); G["dorme"][t] = float(getattr(m1, "dormant", False))
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]))
    return f, G


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.join(here, "..", "LEBRE-V0.56-DIAG-01"))
    import diag_dados as DD
    C, pos = DD.conjuntos()
    novo, L = classes()
    for gid in C["fumaca"][:2]:
        s = DD.carregar(gid, C, pos)
        a, _ = rodar(L(3, reference="persistence", variant="B10"), s)
        b, G = rodar(novo("M0"), s, gravar=True)
        assert np.array_equal(a, b, equal_nan=True), f"M0 difere da B10 em {gid}"
        print("fumaça ok:", s["nome"], "M0 = B10 bit a bit; E recortado em",
              round(float(np.mean(G["e"] != G["e_raw"])), 3), "dos passos; dormente em", round(float(np.mean(G["dorme"])), 3))
