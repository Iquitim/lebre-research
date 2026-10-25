"""LEBRE v0.54 (protótipo de desenvolvimento): a v0.53 de lebre==0.2.0, copiada sem alteração, com a M5a (M1 dormente;
dormancy.py). Os demais arquivos desta pasta são cópias byte a byte da biblioteca (hashes em SHA256_COPIAS.txt) e não
são editados; as mudanças da v0.54 ficam em arquivos novos.
"""
import math
from collections import deque

from .dormancy import DormantPrecisionExpert
from ._core import Core
from .cycle import CycleMixin
from .removal import RemovalMixin
from .screening import Core054
from .full import Lebre

ALGORITHM_VERSION = "LEBRE v0.54 (protótipo: M5a rascunho 2)"


class Lebre054(Lebre):
    """Mesma interface de lebre.Lebre (0.2.0); m5a=False reproduz a v0.53 sem alteração."""

    def __init__(self, n_inputs, season=None, season2=None, standardize=True, reference=None, core_only=False, m5a=True,
                 m5b=False, m4=False, m6=False):
        super().__init__(n_inputs, season=season, season2=season2, standardize=standardize, reference=reference,
                         core_only=core_only)
        self.m5b, self.m4, self.m6 = bool(m5b), bool(m4), bool(m6)
        base = Core054 if self.m5b else Core                        # M5b: grupos de equivalentes a cada 31 passos
        mix = ((CycleMixin,) if self.m6 else ()) + ((RemovalMixin,) if self.m4 else ())   # M6: ciclo como hipótese; M4: remoção
        cls = type("CoreV054", mix + (base,), {}) if mix else base
        if cls is not Core:
            self.core._core = cls(self.n_inputs, season=season, season2=season2)
        self.m5a = bool(m5a) and not self.core_only
        if self.m5a:
            self._m1 = DormantPrecisionExpert(self.n_inputs)
        # M6: sem ciclo declarado e sem referência escolhida, a referência da M2 vira a sazonal do menor ciclo aceito
        self._ref_auto = self.m6 and reference is None and not season and not self.core_only
        self._yh = deque(maxlen=168) if self._ref_auto else None

    def observe(self, y, quarantine=False):
        super().observe(y, quarantine)
        if self._yh is None:
            return
        y_ok = y is not None and math.isfinite(y)
        self._yh.append(float(y) if y_ok else (self._last_y if self._last_y is not None else math.nan))
        cyc = self.core._core.cycles
        if cyc and self.reference == "persistence":
            s = min(cyc)
            self.reference, self.season = "seasonal", s
            self._hist = deque(list(self._yh)[-s:], maxlen=s)
            self._yh = None

    @property
    def m1_state(self):
        """estado da M5a: dormente, quantas vezes dormiu e despertou, passos dormentes, custo da M1 por passo"""
        if not self.m5a:
            return None
        m = self._m1
        return dict(dormant=m.dormant, sleeps=m.sleeps, wakes=m.wakes, trials=getattr(m, "trials", 0), dormant_steps=m.dormant_steps,
                    m1_fp_per_step=m.fp / self.n_steps if self.n_steps else float("nan"))
