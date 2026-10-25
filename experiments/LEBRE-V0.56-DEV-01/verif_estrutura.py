"""verif_estrutura.py — verificação pós-escolha (pedido do responsável pelo projeto, 25/10/2026): a troca da M1 pela C5
não muda nenhuma decisão de estrutura do núcleo. Compara, entre A (v0.55) e C5, os eventos do núcleo, a estrutura final
e a previsão do próprio núcleo, passo a passo, em séries que exercitam mudanças de estrutura. Os eventos do portão da M2
(change="gate") podem mudar, porque o portão compara a referência com a saída da M1; eles são contados à parte.
Uso (ambiente do Lab): LEBRE055_PROTO=... LEBRE053_PROTO=... <python do Lab> verif_estrutura.py"""
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import dev_m1 as M  # noqa: E402
import dev_run as R  # noqa: E402

CASOS = [("e20", ("A05", 0)), ("e20", ("A05", 1)), ("e20", ("A07", 0)), ("e20", ("A01", 0)), ("e20", ("A04", 0)),
         ("e20", ("B03", 0)), ("e20", ("C03", 0))]


def rodar(m, s):
    y, X, q = s["y"], s["X"], s["q"]
    nuc = np.full(len(y), np.nan)
    for t in range(len(y)):
        m.predict(X[t]); nuc[t] = m._L_core
        m.observe(None if not math.isfinite(y[t]) else float(y[t]), bool(q[t]) if q is not None else False)
    ev = [(e.t, e.outcome, e.change, e.added, e.removed) for e in m.core.events]
    gate = [(e.t, e.outcome) for e in m.events if e.change == "gate"]
    return ev, m.structure, nuc, gate


if __name__ == "__main__":
    import dev_dados as DD
    P = DD.predios(); C, _ = DD.bacias().conjuntos()
    casos = CASOS + [("P", P["P"][0]), ("P", P["P"][1]), ("DA", C["A"][0]), ("DA", C["A"][1])]
    novo = M.classes()
    tudo_ok = True
    for parte, ident in casos:
        s = R._serie(parte, ident)
        kw = dict(season=s["season"], season2=s["season2"], reference=s["ref"])
        a = rodar(novo("A", s["X"].shape[1], **kw), s); c = rodar(novo("C5", s["X"].shape[1], **kw), s)
        ok = a[0] == c[0] and a[1] == c[1] and np.array_equal(a[2], c[2], equal_nan=True)
        tudo_ok &= ok
        print(f"{parte} {ident}: eventos do núcleo {len(a[0])} iguais={a[0] == c[0]}; estrutura {a[1]} igual={a[1] == c[1]}; "
              f"previsão do núcleo igual={np.array_equal(a[2], c[2], equal_nan=True)}; portão A/C5 {len(a[3])}/{len(c[3])}")
    print("TODOS IGUAIS" if tudo_ok else "DIFERENÇA ENCONTRADA")
