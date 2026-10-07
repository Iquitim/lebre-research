"""Agregação de especialistas para a saída da M2, rascunho 2: AdaHedge e FlipFlop.

Fonte: de Rooij, van Erven, Grünwald e Koolen (2014), "Follow the leader if you can, hedge if you must", JMLR
15(37):1281-1316. Transcrição direta das Figuras 1 (AdaHedge) e 2 (FlipFlop) do artigo, incluindo a forma numericamente
estável de mix (subtrai o mínimo antes da exponencial). Parâmetros do FlipFlop: os do Corolário 16 (phi = 2,37,
alpha = 1,243), sem ajuste. Prioridade uniforme. As perdas não precisam de escala conhecida: o algoritmo é invariante a
translação e escala das perdas (seção 4 do artigo).
"""
import math

import numpy as np

PHI_FF, ALPHA_FF = 2.37, 1.243          # Corolário 16
FP_AGREGACAO_PASSO = 30                 # duas avaliações de mix (exponenciais, somas, log) e o incremento (aproximado)


def _mix(eta, L):
    """Pesos e perda de mistura acumulada para a taxa eta e as perdas acumuladas L (Figura 1, função mix)."""
    mn = L.min()
    if math.isinf(eta):                                       # limite: seguir o líder, empates com peso igual
        w = (L == mn).astype(float)
        s = w.sum()
        return w / s, mn
    w = np.exp(-eta * (L - mn))
    s = w.sum()
    return w / s, mn - math.log(s / len(L)) / eta


class Agregador:
    """AdaHedge (flipflop=False) ou FlipFlop (flipflop=True) para K especialistas."""

    def __init__(self, K=2, flipflop=False, phi=PHI_FF, alpha=ALPHA_FF):
        if flipflop and not (phi > 1 and alpha > 0):
            raise ValueError("FlipFlop exige phi > 1 e alpha > 0")
        self.K, self.flipflop = int(K), bool(flipflop)
        self.L = np.zeros(self.K)
        self.Delta = [0.0, 0.0]                               # [0] regime "flip" (seguir o líder), [1] "flop" (AdaHedge)
        self.escala = [phi / alpha, alpha]
        self.regime = 0 if self.flipflop else 1
        self.n = 0; self.trocas_regime = 0

    def eta(self):
        if self.regime == 0 or self.Delta[1] == 0.0:
            return math.inf
        return math.log(self.K) / self.Delta[1]

    def pesos(self):
        return _mix(self.eta(), self.L)[0]

    def atualizar(self, perdas):
        l = np.asarray(perdas, float)
        eta = self.eta()
        w, M0 = _mix(eta, self.L)
        h = float(w @ l)
        self.L = self.L + l
        _, M1 = _mix(eta, self.L)
        delta = max(0.0, h - (M1 - M0))                       # max corta violações numéricas de Jensen
        self.Delta[self.regime] += delta
        if self.flipflop and self.Delta[self.regime] > self.escala[self.regime] * self.Delta[1 - self.regime]:
            self.regime = 1 - self.regime; self.trocas_regime += 1
        self.n += 1
