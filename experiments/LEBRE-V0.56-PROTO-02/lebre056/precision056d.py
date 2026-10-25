"""M1 da v0.56, candidata D4 (experiments/LEBRE-V0.56-DEV-02): a M1 da v0.55 com estudo sob demanda.

Representação: três defasagens do alvo, bandas de defasagem das entradas [0], [1], [2-3], sem o recorte de E. A regressão
(RLS) é atualizada quando o alvo surpreende: a surpresa é e²/σ̂²_E, com e = y − w·z o erro a priori da regressão e σ̂²_E a
média exponencial (taxa 0,01) de e², atualizada depois da decisão. Há atualização se a surpresa passa de um limiar q̂
ajustado online para que, em média, RHO = 1/4 dos alvos atualize (q̂ ← máx(q̂ + 0,01·(1{surpresa > q̂} − RHO), 1e-6)).
Guardas: atualização obrigatória enquanto n_RLS < k + 100 (regressão indeterminada e aquecimento depois de cada troca das
entradas escolhidas) e quando já se passaram 7 alvos sem atualização (nunca mais de 8). Com σ̂²_E = 0, qualquer erro
diferente de zero conta como surpresa. A triagem e a escolha das entradas seguem a cada 8 alvos; a dormência é a da
v0.55 (dormancy.py, sem alteração). Tudo usa só o passado.

Transcrito de experiments/LEBRE-V0.56-DEV-02/dev2_modelos.py (PrecisionDyn, regra "orcamento", rho 0,25, com a correção
de σ̂²_E = 0 do commit e0196d0), mantendo a ordem das operações e a contagem de operações."""
import math

from . import _precision as P_
from ._core import EVERY, N_MIN, T_MAX
from .dormancy import DormantPrecisionExpert
from .precision056 import PrecisionParam

RHO, TAXA_Q, TAXA_S2, AQUECIMENTO, MAX_SEM = 0.25, 0.01, 0.01, 100, 7
REPRESENTACAO = dict(ylags=3, clip=False, nbands=3)


class PrecisionOnDemand(PrecisionParam):
    def __init__(self, d, rho=RHO):
        super().__init__(d, every=1, **REPRESENTACAO)
        self.rho = float(rho)
        self.se2 = None; self.q = 1.0; self.gap = 0; self.n_dec = 0; self.n_upd = 0

    def _decidir(self, y):
        z = self.z; k = len(z)
        e = float(y) - float(self.w @ z); self.fp += 2 * k + 1                 # erro a priori da regressão
        forcar = self.n_rls < k + AQUECIMENTO or self.gap >= MAX_SEM
        if self.se2 is None:
            dec = True
        elif self.se2 <= 0.0:                                                   # erro esperado zero: qualquer erro surpreende
            dec = e != 0.0; self.fp += 1
        else:                                                                   # orçamento médio RHO
            u = e * e / self.se2; acima = u > self.q
            self.q = max(self.q + TAXA_Q * ((1.0 if acima else 0.0) - self.rho), 1e-6); dec = acima; self.fp += 6
        self.se2 = e * e if self.se2 is None else self.se2 + TAXA_S2 * (e * e - self.se2); self.fp += 3
        return dec or forcar

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
            if self.z is not None:
                self.n_dec += 1
                if self._decidir(y):
                    self._rls(self.z, y); self.n_upd += 1; self.gap = 0
                else:
                    self.gap += 1
            if self.n_obs >= N_MIN and (self.sel is None or self.n_obs - self.n_sel >= T_MAX):
                self._select()
        self.yobs.append(float(y))


class DormantPrecisionOnDemand(DormantPrecisionExpert, PrecisionOnDemand):
    """a M1 sob demanda com a dormência da v0.55"""

    def __init__(self, d, **kw):
        PrecisionOnDemand.__init__(self, d, **kw)
        self.dormant = False; self.trial = False; self.trials = 0; self.low = 0
        self.sleeps = 0; self.wakes = 0; self.dormant_steps = 0
        self._sampled = False; self._last_sample = -1
        self.ema_g = None; self.ema_s = None; self.n_samples = 0
