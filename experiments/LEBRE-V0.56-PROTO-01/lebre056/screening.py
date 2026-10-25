"""M5b da v0.54 (em desenho): parte da triagem com custo quadrático em d sem efeito em previsões nem decisões.

Os grupos de entradas equivalentes (só relatório, `equivalent_inputs`) passam a ser atualizados a cada SE_EQ passos em vez
de SCREEN_EVERY, com o peso escalado (1e-3 × SE_EQ) para manter a mesma janela de tempo. O resto da triagem é o do núcleo
copiado sem alteração (_core.py), e o método abaixo é cópia literal do original com essa única mudança. Previsões e
decisões são idênticas às do núcleo original; só o relatório de equivalentes pode diferir.

Desenho explorado e descartado antes de qualquer medição: dormência de entradas inativas na triagem. Com o limiar de sono
abaixo do de candidatura quase nenhuma entrada dormia; no limiar de candidatura, a entrada relevante de sinal fraco
dormia antes de ser descoberta e a detecção atrasava ou falhava (triar menos é detectar mais devagar).

Rascunho 1 (depois da medição M5B_E1): passo 31 em vez de 32. Com 32 e ciclo diário de 24 passos (mdc 8), a covariância
era estimada em só 3 das 24 fases do dia e as correlações mudavam de forma sistemática em séries solares (aliasing).

Rascunho 2 (errata 01 da v0.54, depois da auditoria de estresse): a amostra de cada ciclo é a mesma do rascunho 1 (no
passo de fase, a média é atualizada e o vetor centrado é guardado), mas a matriz é atualizada com ela uma linha por vez
nos passos seguintes (até ceil(d/30) linhas por passo; a linha i atualiza as colunas j >= i e é espelhada). Ao fim de cada
ciclo, a matriz é bit a bit a do rascunho 1; a consulta de equivalentes aplica antes as linhas pendentes, então o
relatório é o do rascunho 1 em qualquer momento. O custo total é o mesmo (2d + soma de 3(d - i) = 3d(d+1)/2 + 2d por
ciclo), mas o pico por passo cai: no rascunho 1, a atualização inteira (4.080 operações com d = 51) coincidia
periodicamente com a regressão da camada M1, quebrando o escalonamento do núcleo e elevando o pico em 50% com 50 entradas.
Estado novo: o vetor centrado do ciclo (d números). Previsões e decisões continuam idênticas às do núcleo original.
Explorado e descartado: atualizar cada linha com a amostra do seu próprio turno (amostras diferentes por linha pioravam
muito as correlações perto de 1).
"""
import numpy as np

from ._core import BANDS, POLES, SCREEN_EVERY, SCREEN_W, Core, halves

SE_EQ = 31                   # primo: as atualizações percorrem todas as fases de ciclos como 24, 168, 7 e 12 (rascunho 1)


class Core054(Core):
    def __init__(self, d, season=None, season2=None):
        super().__init__(d, season=season, season2=season2)
        self._eq_xc = None; self._eq_next = 0                        # vetor centrado do ciclo e próxima linha a aplicar

    def _eq_rows(self, n):
        """aplica a amostra do ciclo às próximas n linhas (linha i: colunas j >= i, espelhadas); a matriz ao fim do
        ciclo é bit a bit a do rascunho 1 (mesma amostra e mesma aritmética por elemento)"""
        if self._eq_xc is None:
            return
        gw, xc = 1e-3 * SE_EQ, self._eq_xc
        for i in range(self._eq_next, min(self._eq_next + n, self.d)):
            row = self.g_c[i, i:] + gw * (np.outer(xc[i:i + 1], xc[i:])[0] - self.g_c[i, i:])
            self.g_c[i, i:] = row; self.g_c[i:, i] = row
            self.fp["screening"] += 3 * (self.d - i)
        self._eq_next = min(self._eq_next + n, self.d)
        if self._eq_next >= self.d:
            self._eq_xc = None

    def _eq_flush(self):
        self._eq_rows(self.d)

    def equivalents(self, unit, thr=0.95):
        self._eq_flush()                                             # a consulta vê a matriz com o ciclo completo
        return super().equivalents(unit, thr)

    def _screen_spread(self, res):
        w, se, t = SCREEN_W, SCREEN_EVERY, self.t
        act = {u[1] for u in self.active if u[0] == "in"}
        due = [i for i in range(self.d) if (t + i) % se == 0]
        x, x1, ra = self.H[0], self.H[1], 1e-3 * se
        for i in due:
            self.a_c0[i] += ra * (x[i] * x[i] - self.a_c0[i]); self.a_c1[i] += ra * (x[i] * x1[i] - self.a_c1[i])
            self.fp["screening"] += 6
            if i in act:
                continue
            a = float(self._a()[i]); pres = res - a * self.res_prev
            for b, (lo, hi) in enumerate(BANDS):
                ub = (self.bs[b, i] - a * (self.bs[b, i] - self.H[lo, i] + self.H[hi + 1, i])) / (hi - lo + 1)
                self.sc_xy[b, i] += w * (pres * ub - self.sc_xy[b, i]); self.sc_xx[b, i] += w * (ub * ub - self.sc_xx[b, i])
            self.sc_yy[i] += w * (pres * pres - self.sc_yy[i])
            self.fp["screening"] += 11 * len(BANDS) + 5
        if t % se == self.d % se:                                   # residual latent unit
            self.sr_xy += w * (res * self.r - self.sr_xy); self.sr_xx += w * (self.r * self.r - self.sr_xx)
            self.sr_yy += w * (res * res - self.sr_yy); self.fp["screening"] += 12 * len(POLES)
        if t % SE_EQ == (self.d + 1) % SE_EQ:                       # equivalence groups (reporting only), M5b
            self._eq_flush()                                         # rascunho 2: termina o ciclo anterior, se faltou
            gw = 1e-3 * SE_EQ
            self.g_m += gw * (x - self.g_m); self._eq_xc = x - self.g_m; self._eq_next = 0
            self.fp["screening"] += 2 * self.d
        self._eq_rows(-(-self.d // (SE_EQ - 1)))                     # linhas por passo: termina em até 30 chamadas
        for j, key in enumerate(self.split_keys()):
            if (t + j) % se:
                continue
            i, sg = key[1], key[2:]
            l_, r_ = halves(sg); dv = self._mean(i, l_) - self._mean(i, r_)
            st = self.sp.setdefault(key, [0.0, 1e-3, 1.0])
            st[0] += w * (res * dv - st[0]); st[1] += w * (dv * dv - st[1]); st[2] += w * (res * res - st[2])
            self.fp["screening"] += 14
