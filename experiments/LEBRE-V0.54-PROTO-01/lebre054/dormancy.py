"""M5a da v0.54 (rascunho 0, experiments/LEBRE-V0.54-DESIGN-NOTE-01/ALGORITHM_SPEC_DRAFT_M5a.md): a M1 dormente enquanto
não pesa.

Modo ativo = exatamente a M1 da v0.53 (PrecisionExpert, copiado sem alteração de lebre==0.2.0). Depois da sombra, se o peso
ω do especialista ficar abaixo de OMEGA_MIN em D alvos aprendidos seguidos, a M1 dorme: a saída é L' = L; E é calculado só
num passo de amostra a cada J alvos aprendidos; a regressão é atualizada a cada J_RLS alvos aprendidos (num passo de
amostra); a triagem e a nova seleção seguem como na v0.53; o AdaHedge fica congelado. Ela desperta quando a média
exponencial (taxa RATE) da melhora de E sobre L nas amostras, normalizada pela média exponencial de (y − L)², passa de
G_MIN com pelo menos N_WAKE amostras; ao despertar, o AdaHedge recomeça com nova sombra de N_MIN atualizações. Tudo usa
só o passado.

Rascunho 1 (ALGORITHM_SPEC_DRAFT_M5a_r1.md): uma troca das entradas escolhidas durante o sono reinicia o AdaHedge (como na
v0.53) e a estatística de despertar, mas **não** desperta a M1 (o protótipo do rascunho 0 despertava, desvio declarado no
resultado do M5A_E1).
"""
import math

from ._aggregation import AdaHedge
from ._core import EVERY, LAM, N_MIN, T_MAX
from ._precision import PrecisionExpert

OMEGA_MIN, D_SLEEP, J, J_RLS = 1e-3, 2000, 8, 64
RATE, G_MIN, N_WAKE = 0.01, 0.05, 100
FP_WEIGHT_CHECK = 15        # pesos depois da atualização (mistura, 14) e comparação (1)
FP_WAKE_SAMPLE = 11         # perda de E (2), melhora (1), duas médias exponenciais (6), razão e comparação (2)


class DormantPrecisionExpert(PrecisionExpert):
    def __init__(self, d):
        super().__init__(d)
        self.dormant = False
        self.low = 0
        self.sleeps = 0; self.wakes = 0; self.dormant_steps = 0
        self._sampled = False; self._last_sample = -1
        self.ema_g = None; self.ema_s = None; self.n_samples = 0

    # ----------------------------------------------------------------- previsão
    def predict(self, x, L):
        if not self.dormant:
            self._sampled = False
            return super().predict(x, L)
        self.dormant_steps += 1
        sample = self.n_obs % J == J - 1 and self.n_obs != self._last_sample
        if sample:
            self._last_sample = self.n_obs
            self._sampled = True
            super().predict(x, L)                                   # calcula z e E (recortado); a saída ignora E
            return L
        self._sampled = False
        x = self._fill(x)                                           # mantém o histórico das bandas em dia
        self._x = x
        self.buf.append(x)
        if self.sel is not None:
            self.bufz.append((x[self.sel] - self.mu) / self.sd)
            self.fp += 2 * len(self.sel)
        self.z = None; self.e = None
        return L

    # ----------------------------------------------------------------- aprendizado
    def _wake(self):
        self.dormant = False
        self.ag = AdaHedge(2)                                       # recomeça com nova sombra de N_MIN atualizações
        self.low = 0; self.wakes += 1

    def _select(self):
        antes = None if self.sel is None else tuple(self.sel)
        super()._select()
        if antes is not None and tuple(self.sel) != antes:
            self.low = 0
            if self.dormant:                                        # rascunho 1: continua dormindo, estatística recomeça
                self.ema_g = None; self.ema_s = None; self.n_samples = 0

    def observe(self, y, L_core, learn, floor):
        if not self.dormant:
            super().observe(y, L_core, learn, floor)
            if learn and self.e is not None and self.ag.n >= N_MIN and not self.dormant:
                self.fp += FP_WEIGHT_CHECK
                if self.ag.weights()[1] < OMEGA_MIN:
                    self.low += 1
                    if self.low >= D_SLEEP:
                        self.dormant = True; self.sleeps += 1; self.low = 0
                        self.ema_g = None; self.ema_s = None; self.n_samples = 0
                else:
                    self.low = 0
            return
        e_core = (y - L_core) ** 2
        if self._sampled and self.e is not None:
            le = (y - self.e) ** 2
            if math.isfinite(e_core) and math.isfinite(le):
                g = e_core - le
                if self.ema_g is None:
                    self.ema_g, self.ema_s = g, e_core
                else:
                    self.ema_g += RATE * (g - self.ema_g); self.ema_s += RATE * (e_core - self.ema_s)
                self.n_samples += 1
            self.fp += FP_WAKE_SAMPLE
        self.e2_core = e_core if self.e2_core is None else self.e2_core + (1 - LAM) * (e_core - self.e2_core)
        self._floor = floor
        if learn:
            self.n_obs += 1
            if self.n_obs % EVERY == 0:
                self._screen(self._x, y)
                if self._sampled and self.z is not None and self.n_obs % J_RLS == 0:
                    self._rls(self.z, y)
            if self.n_obs >= N_MIN and (self.sel is None or self.n_obs - self.n_sel >= T_MAX):
                self._select()
        self.yobs.append(float(y))
        if self.dormant and self.n_samples >= N_WAKE and self.ema_s and self.ema_g / self.ema_s > G_MIN:
            self._wake()
