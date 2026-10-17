#!/usr/bin/env python3
"""make_split_v055val.py — séries reais da VALIDAÇÃO da v0.55 (núcleo ancorado), nunca usadas por nenhuma avaliação.

Usa só metadados, cobertura e as permutações sorteadas na v0.52 (sementes 5202 e 5203). Os valores das séries não são
inspecionados. Confere que as posições já consumidas são as registradas (v0.52, reservas 2 e 3, reservas finais da v0.53
e da v0.54) e toma as **seguintes**:
- CAMELS-BR: as próximas 20 bacias presentes no arquivo de vazões, a partir da posição 170;
- BDG2: os próximos 30 medidores, posições 145 a 174.
O restante das permutações fica para a avaliação final da v0.55.
Requer data/external_v052 (CAMELS-BR, BDG2) e pandas 2.2.3.
"""
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
D52 = ROOT / "data" / "external_v052"
E = ROOT / "experiments"
SEED_CAMELS, SEED_BDG2, MIN_COV = 5202, 5203, 0.9
N_CAMELS, N_BDG2 = 20, 30


def _json(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def camels():
    z = zipfile.ZipFile(D52 / "camels_br" / "01_CAMELS_BR_attributes.zip")
    rd = lambda f: pd.read_csv(io.BytesIO(z.read("01_CAMELS_BR_attributes/" + f)), sep=r"\s+")  # noqa: E731
    a = rd("camels_br_human_intervention.txt").merge(rd("camels_br_quality_check.txt"), on="gauge_id")
    elig = a[(a.consumptive_use_perc < 1.0) & (a.regulation_degree < 0.05) & (a.q_quality_control_perc >= 95.0)]
    pick = [int(x) for x in np.random.default_rng(SEED_CAMELS).permutation(sorted(elig.gauge_id.astype(int).tolist()))]
    v54 = _json(E / "LEBRE-V0.54-DATA-01" / "SPLIT_V054.json")["camels_br"]
    assert v54["posicoes"] == "140-169" and set(pick[140:170]) == set(v54["reservadas"]), "reserva v0.54 CAMELS diferente"
    zq = zipfile.ZipFile(D52 / "camels_br" / "03_CAMELS_BR_streamflow_selected_catchments.zip")
    no_arquivo = {int(Path(n).name.split("_")[0]) for n in zq.namelist() if n.endswith(".txt") and Path(n).name[0].isdigit()}
    res, subst, pos = [], [], 170
    while len(res) < N_CAMELS:
        g = pick[pos]
        (res if g in no_arquivo else subst).append(g); pos += 1
    return dict(semente=SEED_CAMELS, n_elegiveis=len(pick), posicoes=f"170-{pos - 1}", validacao=sorted(res),
                substituidas_por_ausencia=subst, restantes_para_a_final=len(pick) - pos,
                conferencia="posições 140-169 = reserva final da v0.54 (as anteriores foram conferidas no split da v0.54)")


def bdg2():
    z = zipfile.ZipFile(D52 / "bdg2" / "building-data-genome-project-2-v1.0.zip")
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    meters = []
    for kind in ("chilledwater", "hotwater", "steam"):
        m = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
        cov, nz = m.notna().mean(), (m.fillna(0) != 0).mean()
        meters += [f"{kind}:{b}" for b in cov[(cov >= MIN_COV) & (nz >= 0.5)].index]
    pick = [str(x) for x in np.random.default_rng(SEED_BDG2).permutation(sorted(meters))]
    v54 = _json(E / "LEBRE-V0.54-DATA-01" / "SPLIT_V054.json")["bdg2"]
    assert v54["posicoes"] == "115-144" and set(pick[115:145]) == set(v54["reservadas"]), "reserva v0.54 BDG2 diferente"
    res = pick[145:145 + N_BDG2]
    return dict(semente=SEED_BDG2, n_elegiveis=len(pick), posicoes=f"145-{145 + N_BDG2 - 1}", validacao=sorted(res),
                restantes_para_a_final=len(pick) - 145 - N_BDG2,
                conferencia="posições 115-144 = reserva final da v0.54 (as anteriores foram conferidas no split da v0.54)")


def main():
    split = dict(criado=pd.Timestamp.now().isoformat(timespec="seconds"), uso="validação da v0.55 (uma única vez)",
                 camels_br=camels(), bdg2=bdg2())
    p = HERE / "SPLIT_V055_VAL.json"
    p.write_text(json.dumps(split, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "SPLIT_V055_VAL_SHA256.txt").write_text(f"{h} *SPLIT_V055_VAL.json\n", encoding="utf-8", newline="\n")
    print("CAMELS", split["camels_br"]["posicoes"], "substituídas", split["camels_br"]["substituidas_por_ausencia"],
          "restantes", split["camels_br"]["restantes_para_a_final"], "| BDG2", split["bdg2"]["posicoes"],
          "restantes", split["bdg2"]["restantes_para_a_final"], "| SHA-256", h)


if __name__ == "__main__":
    main()
