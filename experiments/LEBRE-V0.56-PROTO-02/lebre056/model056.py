"""LEBRE v0.56 (protótipo, candidata): a v0.55 canônica (núcleo B10 + M1 com dormência + M2), copiada sem alteração do
commit b0522a0 (hashes em SHA256_COPIAS.txt), com a M1 da candidata C5 (precision056.py).

Variantes:
- "C5": a v0.56 (a candidata de experiments/LEBRE-V0.56-DEV-01);
- "A": a v0.55 canônica, sem nenhuma mudança (classe de M1 original);
- "A0": a M1 reescrita (precision056.PrecisionParam) com os parâmetros da v0.55; deve ser idêntica a "A" bit a bit.
O núcleo e a M2 não mudam em nenhuma variante."""
from .model055 import Lebre055
from .precision056 import V055, V056, DormantPrecisionParam

ALGORITHM_VERSION = "LEBRE v0.56 (protótipo: M1 da candidata C5 sobre a v0.55)"
VARIANTS = ("C5", "A", "A0")


class Lebre056(Lebre055):
    """Mesma interface de Lebre055; `variant` escolhe a M1 (ver o docstring do módulo)."""

    def __init__(self, n_inputs, season=None, season2=None, standardize=True, reference=None, core_only=False, variant="C5"):
        if variant not in VARIANTS:
            raise ValueError(f"variant must be one of {VARIANTS}")
        super().__init__(n_inputs, season=season, season2=season2, standardize=standardize, reference=reference,
                         core_only=core_only, variant="B10")
        self.variant056 = variant
        if not self.core_only and variant != "A":
            self._m1 = DormantPrecisionParam(self.n_inputs, **(V056 if variant == "C5" else V055))
