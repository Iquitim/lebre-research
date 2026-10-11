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
"""
import numpy as np

from ._core import BANDS, POLES, SCREEN_EVERY, SCREEN_W, Core, halves

SE_EQ = 31                   # primo: as atualizações percorrem todas as fases de ciclos como 24, 168, 7 e 12 (rascunho 1)


class Core054(Core):
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
            gw = 1e-3 * SE_EQ
            self.g_m += gw * (x - self.g_m); xc = x - self.g_m
            self.g_c += gw * (np.outer(xc, xc) - self.g_c)
            self.fp["screening"] += 3 * self.d * (self.d + 1) // 2 + 2 * self.d
        for j, key in enumerate(self.split_keys()):
            if (t + j) % se:
                continue
            i, sg = key[1], key[2:]
            l_, r_ = halves(sg); dv = self._mean(i, l_) - self._mean(i, r_)
            st = self.sp.setdefault(key, [0.0, 1e-3, 1.0])
            st[0] += w * (res * dv - st[0]); st[1] += w * (dv * dv - st[1]); st[2] += w * (res * res - st[2])
            self.fp["screening"] += 14
