"""diag_dados.py — conjuntos e carregador do diagnóstico das bacias (PLANO_DIAG_BACIAS.md, §2).

A permutação do CAMELS-BR é reconstruída só com metadados (atributos de intervenção humana e de qualidade) e a semente
5202, como em LEBRE-V0.52-DATA-01/make_split_v052.py. Cada conjunto é conferido contra o arquivo de sorteio registrado.
O carregador recusa qualquer bacia fora dos conjuntos declarados e qualquer posição >= 170 (validação e reserva final da
v0.55, e as 17 bacias nunca usadas)."""
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
E = RAIZ / "experiments"
D52 = RAIZ / "data" / "external_v052"
LIMITE = 170                                                     # nenhuma posição >= 170 pode ser carregada


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def permutacao():
    z = zipfile.ZipFile(D52 / "camels_br" / "01_CAMELS_BR_attributes.zip")
    rd = lambda f: pd.read_csv(io.BytesIO(z.read("01_CAMELS_BR_attributes/" + f)), sep=r"\s+")  # noqa: E731
    a = rd("camels_br_human_intervention.txt").merge(rd("camels_br_quality_check.txt"), on="gauge_id")
    elig = a[(a.consumptive_use_perc < 1.0) & (a.regulation_degree < 0.05) & (a.q_quality_control_perc >= 95.0)]
    return [int(x) for x in np.random.default_rng(5202).permutation(sorted(elig.gauge_id.astype(int).tolist()))]


def conjuntos():
    pick = permutacao()
    assert len(pick) == 237
    s52 = _json(E / "LEBRE-V0.52-DATA-01" / "SPLIT_V052.json")["camels_br"]
    s53 = _json(E / "LEBRE-V0.53-DATA-01" / "SPLIT_V053.json")["camels_br"]
    s54 = _json(E / "LEBRE-V0.54-DATA-01" / "SPLIT_V054.json")["camels_br"]
    assert s53["posicoes"] == "110-139" and not s53["substituidas_por_ausencia"]
    assert s54["posicoes"] == "140-169" and not s54["substituidas_por_ausencia"]
    C = {"fumaca": pick[0:10], "B": pick[110:140], "A": pick[140:170]}
    assert set(C["fumaca"]) == set(s52["development"]), "desenvolvimento da v0.52 diferente"
    assert set(C["B"]) == set(s53["reservadas"]), "reserva da v0.53 diferente"
    assert set(C["A"]) == set(s54["reservadas"]), "reserva da v0.54 diferente"
    proibidas = set(pick[LIMITE:])
    v55 = set(_json(E / "LEBRE-V0.55-DATA-01" / "SPLIT_V055_VAL.json")["camels_br"]["validacao"])
    v55 |= set(_json(E / "LEBRE-V0.55-DATA-02" / "SPLIT_V055.json")["camels_br"]["reservadas"])
    assert v55 <= proibidas
    for k, ids in C.items():
        assert not (set(ids) & proibidas), k
    return C, {g: i for i, g in enumerate(pick)}


def carregar(gid, C=None, pos=None):
    """bacia de um conjunto declarado; nunca uma posição >= 170"""
    if C is None:
        C, pos = conjuntos()
    gid = int(gid)
    assert pos[gid] < LIMITE and any(gid in v for v in C.values()), f"bacia {gid} fora dos conjuntos declarados"
    sys.path.insert(0, str(E / "LEBRE-V0.52-PROTO-01"))
    import data_v052 as D
    d = D.load_camels(gid, final=True)                          # reserva já consumida (PLANO_DIAG_BACIAS.md, §2)
    assert d["season"] is None and d["X"].shape[1] == 3
    return dict(nome=d["task"], y=np.asarray(d["y"], float), X=np.asarray(d["X"], float),
                q=np.asarray(d["quarantine"], bool), pos=pos[gid])


if __name__ == "__main__":
    C, pos = conjuntos()
    for k, v in C.items():
        print(k, len(v), "posições", min(pos[g] for g in v), "a", max(pos[g] for g in v))
