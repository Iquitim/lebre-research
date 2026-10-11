"""LEBRE v0.54 (protótipo de desenvolvimento): a v0.53 de lebre==0.2.0, copiada sem alteração, com a M5a (M1 dormente;
dormancy.py). Os demais arquivos desta pasta são cópias byte a byte da biblioteca (hashes em SHA256_COPIAS.txt) e não
são editados; as mudanças da v0.54 ficam em arquivos novos.
"""
from .dormancy import DormantPrecisionExpert
from .full import Lebre

ALGORITHM_VERSION = "LEBRE v0.54 (protótipo: M5a rascunho 2)"


class Lebre054(Lebre):
    """Mesma interface de lebre.Lebre (0.2.0); m5a=False reproduz a v0.53 sem alteração."""

    def __init__(self, n_inputs, season=None, season2=None, standardize=True, reference=None, core_only=False, m5a=True):
        super().__init__(n_inputs, season=season, season2=season2, standardize=standardize, reference=reference,
                         core_only=core_only)
        self.m5a = bool(m5a) and not self.core_only
        if self.m5a:
            self._m1 = DormantPrecisionExpert(self.n_inputs)

    @property
    def m1_state(self):
        """estado da M5a: dormente, quantas vezes dormiu e despertou, passos dormentes, custo da M1 por passo"""
        if not self.m5a:
            return None
        m = self._m1
        return dict(dormant=m.dormant, sleeps=m.sleeps, wakes=m.wakes, trials=getattr(m, "trials", 0), dormant_steps=m.dormant_steps,
                    m1_fp_per_step=m.fp / self.n_steps if self.n_steps else float("nan"))
