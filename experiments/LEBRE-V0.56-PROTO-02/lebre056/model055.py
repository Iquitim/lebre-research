"""LEBRE v0.55 (protótipo de desenvolvimento): a v0.54 canônica (M5a + M5b + M4), copiada sem alteração do commit
f9906c4 (hashes em SHA256_COPIAS.txt), com o núcleo ancorado de anchored.py (rascunho 0 da nota de desenho
experiments/LEBRE-V0.55-DESIGN-NOTE-01/DESIGN_NOTE.md).

Variantes (medição D1):
- A:  v0.54 canônica, sem nenhuma mudança (classe de núcleo original);
- A0: a reescrita de predict/observe com as duas alavancas desligadas; deve ser idêntica a A bit a bit;
- B:  âncora na memória + referência lenta dos testes;
- B1: só a âncora;
- B2: só a referência lenta;
- B4: referência dos testes = previsão combinada do núcleo (rascunho 2), previsão viva da v0.54;
- B5: B4 com a cópia lenta da estrutura dentro da referência;
- B6: rascunho 3: unidades externas testadas contra a previsão do núcleo, internas contra s;
- B7: rascunho 4: B6 + estrutura de inovação como terceiro especialista, aninhado (mesmas unidades, pesos próprios);
- B8: rascunho 5: B7 + nenhum teste novo de unidade interna enquanto wS < 0,05;
- B9: rascunho 6: B7 + portão suave pela triagem (internas triadas pelo resíduo do núcleo) + pesos de cada estrutura
  vindos do resíduo que o desafiante aprendeu;
- B10: rascunho 7: B9 + piso de escala dos testes previsível e na escala de uma passada (min das variâncias do nível e
  de Δy).
"""
from ._core import Core  # noqa: F401  (mantido para leitura: a classe base da hierarquia)
from .anchored import AnchoredMixin
from .model054 import Lebre054
from .removal import RemovalMixin
from .screening import Core054

ALGORITHM_VERSION = "LEBRE v0.55 (protótipo: núcleo ancorado, rascunhos 0 a 7)"


class CoreA0(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW = False, False


class CoreB(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW = True, True


class CoreB1(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW = True, False


class CoreB2(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW = False, True


class CoreB4(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE = False, False, True


class CoreB5(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE = False, True, True


class CoreB6(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE, REF_SPLIT = False, False, False, True


class CoreB7(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE, REF_SPLIT, INNOV = False, False, False, True, True


class CoreB8(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE, REF_SPLIT, INNOV, GATE_INTERNAL = False, False, False, True, True, True


class CoreB9(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE, REF_SPLIT, INNOV = False, False, False, True, True
    SCREEN_CORE_INT, INN_FROM_OWN_RESIDUAL = True, True


class CoreB10(AnchoredMixin, RemovalMixin, Core054):
    ANCHOR, SLOW, REF_CORE, REF_SPLIT, INNOV = False, False, False, True, True
    SCREEN_CORE_INT, INN_FROM_OWN_RESIDUAL, PRED_FLOOR, DIFF_FLOOR = True, True, True, True


VARIANTS = {"A": None, "A0": CoreA0, "B": CoreB, "B1": CoreB1, "B2": CoreB2, "B4": CoreB4, "B5": CoreB5, "B6": CoreB6,
            "B7": CoreB7, "B8": CoreB8, "B9": CoreB9, "B10": CoreB10}
CANONICAL_V054 = dict(m5a=True, m5b=True, m4=True, m6=False)


class Lebre055(Lebre054):
    """Mesma interface de Lebre054 (v0.54 canônica); `variant` escolhe o núcleo (ver o docstring do módulo)."""

    def __init__(self, n_inputs, season=None, season2=None, standardize=True, reference=None, core_only=False, variant="B"):
        if variant not in VARIANTS:
            raise ValueError(f"variant must be one of {sorted(VARIANTS)}")
        super().__init__(n_inputs, season=season, season2=season2, standardize=standardize, reference=reference,
                         core_only=core_only, **CANONICAL_V054)
        self.variant = variant
        cls = VARIANTS[variant]
        if cls is not None:
            self.core._core = cls(self.n_inputs, season=season, season2=season2)
