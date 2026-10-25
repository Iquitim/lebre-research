"""diag_allon.py — modelo L3 do diagnóstico (PLANO_DIAG_BACIAS.md, §3.2): a v0.55 (B10) com todas as unidades ativas
desde o início e nenhum experimento ("tudo ligado"), na mesma definição da ablação da v0.52 (LEBRE-V0.52-EXT-02): cada
entrada e o passado do alvo com as bandas de oitava e pesos zero, o estado residual com pesos zero, e nenhuma vaga de
experimento (m_slots = 0, o que também impede as remoções disparadas). Na v0.55, a estrutura de inovação recebe as mesmas
unidades, com pesos zero.

Teste de fumaça (python diag_allon.py): com all_on=False, a subclasse dá previsões idênticas, bit a bit, às da B10 numa
bacia de fumaça; com all_on=True, nenhum evento de estrutura é registrado.
Uso: LEBRE055_PROTO=<pasta LEBRE-V0.55-PROTO-01 no commit b0522a0> python diag_allon.py"""
import math
import os
import sys

import numpy as np


def classes():
    p = os.environ["LEBRE055_PROTO"]
    if p not in sys.path:
        sys.path.insert(0, p)
    from lebre055._core import BANDS, POLES
    from lebre055.model055 import CoreB10, Lebre055

    class CoreAllOn(CoreB10):
        def __init__(self, d, season=None, season2=None, all_on=True):
            super().__init__(d, season=season, season2=season2)
            if all_on:
                for u in self.units:
                    n = len(BANDS) if u[0] == "in" else len(POLES)
                    self.active[u] = {"segs": list(BANDS) if u[0] == "in" else None, "w": np.zeros(n)}
                    self.inn_w[u] = np.zeros(n)
                self.engine.m_slots = 0; self._retrack()

    def novo(d, season, season2, reference, all_on=True, core_only=False):
        m = Lebre055(d, season=season, season2=season2, reference=reference, core_only=core_only, variant="B10")
        m.core._core = CoreAllOn(m.n_inputs, season=season, season2=season2, all_on=all_on)
        return m

    return Lebre055, novo


def _rodar(m, s):
    f = np.full(len(s["y"]), np.nan)
    for t in range(len(s["y"])):
        f[t] = m.predict(s["X"][t]).value
        y = s["y"][t]
        m.observe(None if not math.isfinite(y) else float(y), bool(s["q"][t]))
    return f


if __name__ == "__main__":
    import diag_dados as DD
    C, pos = DD.conjuntos()
    s = DD.carregar(C["fumaca"][0], C, pos)
    L, novo = classes()
    a = _rodar(L(3, reference="persistence", variant="B10"), s)
    m_off = novo(3, None, None, "persistence", all_on=False)
    b = _rodar(m_off, s)
    assert np.array_equal(a, b, equal_nan=True), "all_on=False difere da B10"
    m_on = novo(3, None, None, "persistence", all_on=True)
    c = _rodar(m_on, s)
    ev = [e for e in m_on.events if e.change != "gate"]
    assert not ev, ev[:3]
    print("fumaça ok:", s["nome"], "identidade bit a bit com all_on=False;", "tudo ligado: estrutura", m_on.structure,
          "sem eventos de estrutura; finitas", bool(np.isfinite(c[200:]).all()))
