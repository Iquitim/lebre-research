"""M1 da v0.53 (rascunho 0, ALGORITHM_SPEC_DRAFT_M1.md): especialista de precisão enxuto.

RLS com esquecimento sobre [1, 3 entradas no instante t de maior correlação absoluta com o alvo, padronizadas], atualizada
a cada EVERY passos; triagem por médias exponenciais a cada EVERY passos; seleção depois de N_MIN alvos e refeita a cada
T_MAX passos. Combinado com a v0.52 pelo (A,B)-Prod anytime (A = especialista, B = v0.52), perdas recortadas da v0.52.
"""
import math

import numpy as np

from ._core import CLIP_K, EVERY, LAM, N_MIN, T_MAX
from .agregacao import ProdAnytime

K_PRECISAO = 3
LAMBDA_RLS, DELTA_RLS = 0.999, 100.0          # os do comparador linear online do LEBRE Lab (declarados, não derivados)
# Contagem com a regra da v0.52 (ver especificação, seção 4), sem a triagem (contada à parte, 5 FP por entrada a cada
# EVERY passos): RLS com 4 variáveis 180 por atualização (a cada EVERY), previsão 13, Prod 31, mistura 3, escala 3.
FP_RLS_ATUALIZACAO = 180
FP_PRECISAO_PASSO = 13 + 31 + 3 + 3


class EspecialistaPrecisao:
    def __init__(self, d):
        self.d = int(d)
        self.m = np.zeros(5 * self.d).reshape(5, self.d)    # médias exponenciais de x, x^2, x*y (por entrada), y, y^2
        self.my = 0.0; self.my2 = 0.0; self.iniciado = False
        self.sel = None; self.mu = None; self.sd = None
        self.w = None; self.P = None
        self.ult_x = np.zeros(self.d); self.tem_x = np.zeros(self.d, bool)
        self.n_obs = 0; self.n_sel = 0; self.n_rls = 0
        self.prod = ProdAnytime(); self.e2_52 = None
        self.fp = 0.0; self.z = None; self.e = None

    # ----------------------------------------------------------------- entradas
    def _preencher(self, x):
        x = np.asarray(x, float).copy()
        ok = np.isfinite(x)
        self.ult_x[ok] = x[ok]; self.tem_x |= ok
        x[~ok] = self.ult_x[~ok]
        x[~self.tem_x] = 0.0
        return x

    def prever(self, x, L):
        """Previsão de E (ou None) e a combinação L' = s E + (1 - s) L."""
        x = self._preencher(x)
        self._x = x
        self.fp += FP_PRECISAO_PASSO
        if self.sel is None:
            self.z = None; self.e = None
            return L
        z = np.concatenate([[1.0], (x[self.sel] - self.mu) / self.sd])
        self.z = z
        if self.n_rls < len(self.w):                 # RLS ainda indeterminada (menos observações que variáveis)
            self.e = None
            return L
        self.e = float(self.w @ z)
        s = self.prod.s()
        return s * self.e + (1.0 - s) * L

    # ----------------------------------------------------------------- aprendizado
    def _triagem(self, x, y):
        a = 1.0 - LAM
        if not self.iniciado:
            self.m[0] = x; self.m[1] = x * x; self.m[2] = x * y; self.my = y; self.my2 = y * y; self.iniciado = True
        else:
            self.m[0] += a * (x - self.m[0]); self.m[1] += a * (x * x - self.m[1]); self.m[2] += a * (x * y - self.m[2])
            self.my += a * (y - self.my); self.my2 += a * (y * y - self.my2)
        self.fp += 5 * self.d + 4

    def _selecionar(self):
        vx = np.maximum(self.m[1] - self.m[0] ** 2, 0.0)
        vy = max(self.my2 - self.my ** 2, 0.0)
        cov = self.m[2] - self.m[0] * self.my
        with np.errstate(divide="ignore", invalid="ignore"):
            r = np.where((vx > 0) & (vy > 0), np.abs(cov) / np.sqrt(vx * vy), 0.0)
        k = min(K_PRECISAO, self.d)
        sel = np.sort(np.argsort(-r, kind="stable")[:k])
        if self.sel is None or not np.array_equal(sel, self.sel):
            self.sel = sel
            self.mu = self.m[0][sel].copy()
            self.sd = np.sqrt(np.maximum(vx[sel], 1e-24))
            self.w = np.zeros(k + 1); self.P = np.eye(k + 1) * DELTA_RLS; self.n_rls = 0
            self.prod = ProdAnytime()                    # especialista novo: o Prod recomeça
        self.n_sel = self.n_obs
        self.fp += 6 * self.d

    def _rls(self, z, y):
        Pz = self.P @ z
        g = Pz / (LAMBDA_RLS + z @ Pz)
        self.w = self.w + g * (y - self.w @ z)
        P = (self.P - np.outer(g, Pz)) / LAMBDA_RLS
        self.P = (P + P.T) / 2
        if not np.isfinite(self.P).all() or np.diag(self.P).min() <= 0:
            self.P = np.eye(len(z)) * DELTA_RLS
        self.n_rls += 1
        self.fp += FP_RLS_ATUALIZACAO

    def observar(self, y, L52, aprende, piso):
        """y observado (float); L52 = previsão da v0.52 neste passo; aprende = passo fora de quarentena."""
        e52 = (y - L52) ** 2
        if self.e is not None and self.e2_52 is not None:                       # Prod: escala só do passado
            B2 = CLIP_K * CLIP_K * max(self.e2_52, piso * piso, 1e-300)
            self.prod.atualizar(min(e52 / B2, 1.0), min((y - self.e) ** 2 / B2, 1.0))
        self.e2_52 = e52 if self.e2_52 is None else self.e2_52 + (1 - LAM) * (e52 - self.e2_52)
        if not aprende:
            return
        self.n_obs += 1
        if self.n_obs % EVERY == 0:
            self._triagem(self._x, y)
            if self.z is not None:
                self._rls(self.z, y)
        if self.n_obs >= N_MIN and (self.sel is None or self.n_obs - self.n_sel >= T_MAX):
            self._selecionar()
