"""LEBRE v0.56 (protótipo, candidata D4): a v0.55 canônica (núcleo B10 + M1 com dormência + M2), copiada sem alteração
(SHA256_COPIAS.txt), com a M1 de estudo sob demanda (precision056d.py).

Variantes: "D4" (a candidata) e "A" (a v0.55 canônica, sem nenhuma mudança). O núcleo e a M2 não mudam."""
from .model055 import Lebre055
from .precision056d import DormantPrecisionOnDemand

ALGORITHM_VERSION = "LEBRE v0.56 (protótipo: M1 com estudo sob demanda, candidata D4, sobre a v0.55)"
VARIANTS = ("D4", "A")


class Lebre056D(Lebre055):
    def __init__(self, n_inputs, season=None, season2=None, standardize=True, reference=None, core_only=False, variant="D4"):
        if variant not in VARIANTS:
            raise ValueError(f"variant must be one of {VARIANTS}")
        super().__init__(n_inputs, season=season, season2=season2, standardize=standardize, reference=reference,
                         core_only=core_only, variant="B10")
        self.variant056 = variant
        if not self.core_only and variant == "D4":
            self._m1 = DormantPrecisionOnDemand(self.n_inputs)
