"""dev_dados.py — partes do banco da etapa LEBRE-V0.56-DEV-01 (PLANO_DEV_M1_BARATA.md, §3), com travas.

- Bacias: o carregador do LEBRE-V0.56-DIAG-01 (D-A = posições 140-169, D-B = 110-139; recusa posições >= 170).
- Prédios: medidores BDG2 das reservas finais consumidas da v0.54 (posições 115-144, escolha) e da v0.53 (85-114,
  replicação), conferidos contra os arquivos de sorteio; recusa qualquer medidor fora delas e confere que nenhum está nas
  séries da v0.55.
- E20: as 64 famílias do LEBRE Lab (`analises/m2_e20.py`), localizado por LEBRE_LAB (padrão: pasta irmã lebre-lab);
  precisa do ambiente do Lab (variável LEBRE053_PROTO e o pacote lebre instalado)."""
import json
import os
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
RAIZ = E.parent
LAB = Path(os.environ.get("LEBRE_LAB", RAIZ.parent / "lebre-lab"))


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def bacias():
    sys.path.insert(0, str(E / "LEBRE-V0.56-DIAG-01"))
    import diag_dados as DD
    return DD


def predios():
    s53 = _json(E / "LEBRE-V0.53-DATA-01" / "SPLIT_V053.json")["bdg2"]
    s54 = _json(E / "LEBRE-V0.54-DATA-01" / "SPLIT_V054.json")["bdg2"]
    assert s53["posicoes"] == "85-114" and s54["posicoes"] == "115-144"
    v55 = set(_json(E / "LEBRE-V0.55-DATA-01" / "SPLIT_V055_VAL.json")["bdg2"]["validacao"])
    v55 |= set(_json(E / "LEBRE-V0.55-DATA-02" / "SPLIT_V055.json")["bdg2"]["reservadas"])
    P = {"P": sorted(s54["reservadas"]), "R": sorted(s53["reservadas"])}
    assert not (set(P["P"]) | set(P["R"])) & v55
    return P


def carregar_predio(meter, P=None):
    P = P or predios()
    assert meter in P["P"] or meter in P["R"], f"medidor {meter} fora das reservas consumidas declaradas"
    sys.path.insert(0, str(E / "LEBRE-V0.52-PROTO-01"))
    import data_v052 as D
    d = D.load(f"bdg2:{meter}", final=True)                    # reserva já consumida (PLANO_DEV_M1_BARATA.md, §3)
    return dict(nome=d["task"], y=np.asarray(d["y"], float), X=np.asarray(d["X"], float),
                q=np.asarray(d["quarantine"], bool), season=d["season"], season2=168)


def e20():
    if str(LAB) not in sys.path:
        sys.path.insert(0, str(LAB))
    from analises import m2_dev, m2_e20
    return m2_e20, m2_dev


if __name__ == "__main__":
    P = predios(); print("prédios", {k: len(v) for k, v in P.items()})
    s = carregar_predio(P["P"][0], P); print(s["nome"], len(s["y"]), s["X"].shape, s["season"])
    try:
        carregar_predio("chilledwater:inexistente", P); print("FALHOU A TRAVA")
    except AssertionError as e:
        print("trava ok:", e)
