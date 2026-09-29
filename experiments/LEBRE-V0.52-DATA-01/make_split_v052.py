#!/usr/bin/env python3
"""make_split_v052.py — fixes the development / held-out partition of the v0.52 real input-driven datasets.

Rules (written before any modelling; see SPLIT_RULES.md):
  * only metadata and data COVERAGE (fraction of non-missing values) are used; series values are never inspected;
  * ONS: tasks = (downstream plant inflow <- direct upstream plant outflow(s)) from the public cascade topology below;
    the split unit is the whole RIVER (no cascade appears in both sets); one development river drawn by seed;
  * CAMELS-BR: eligibility from published attributes (low human intervention, high quality control); random draw by seed;
  * BDG2: heating/cooling meters with enough coverage; random draw by seed.
Seeds 5201-5203 were checked against every seed used so far in the project (none overlap).
"""
import hashlib
import io
import json
import os
import zipfile

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
D = os.path.join(ROOT, "data", "external_v052")
HERE = os.path.dirname(os.path.abspath(__file__))
SEED_ONS, SEED_CAMELS, SEED_BDG2 = 5201, 5202, 5203

# ------------------------------------------------------------------ ONS cascade topology (direct upstream plants)
# Main-stem sequences of the SIN cascades; to be cross-checked against the ONS schematic diagram before pre-registration.
TOPOLOGY = {
    "TIETE": [("BARIRI", ["B. BONITA"]), ("IBITINGA", ["BARIRI"]), ("PROMISSÃO", ["IBITINGA"]),
              ("N. AVANHANDAVA", ["PROMISSÃO"]), ("TRÊS IRMÃOS", ["N. AVANHANDAVA"])],
    "PARANAPANEMA": [("PIRAJU", ["JURUMIRIM"]), ("CHAVANTES", ["PIRAJU"]), ("OURINHOS", ["CHAVANTES"]),
                     ("SALTO GRANDE CS", ["OURINHOS"]), ("CANOAS II", ["SALTO GRANDE CS"]), ("CANOAS I", ["CANOAS II"]),
                     ("CAPIVARA", ["CANOAS I", "GOV JAYME CANET JR"]), ("TAQUARUÇU", ["CAPIVARA"]), ("ROSANA", ["TAQUARUÇU"])],
    "IGUACU": [("SEGREDO", ["G. B. MUNHOZ"]), ("SALTO SANTIAGO", ["SEGREDO"]), ("SALTO OSORIO", ["SALTO SANTIAGO"]),
               ("SALTO CAXIAS", ["SALTO OSORIO"]), ("BAIXO IGUACU", ["SALTO CAXIAS"])],
    "GRANDE": [("ITUTINGA", ["CAMARGOS"]), ("FUNIL-MG", ["ITUTINGA"]), ("FURNAS", ["FUNIL-MG"]), ("M. MORAES", ["FURNAS"]),
               ("L. C. BARRETO", ["M. MORAES"]), ("JAGUARA", ["L. C. BARRETO"]), ("IGARAPAVA", ["JAGUARA"]),
               ("VOLTA GRANDE", ["IGARAPAVA"]), ("P. COLOMBIA", ["VOLTA GRANDE"]), ("MARIMBONDO", ["P. COLOMBIA"]),
               ("A. VERMELHA", ["MARIMBONDO"])],
    "PARANAIBA": [("MIRANDA", ["NOVA PONTE"]), ("C.BRANCO-1", ["MIRANDA"]), ("C.BRANCO-2", ["C.BRANCO-1"]),
                  ("CORUMBA-3", ["CORUMBA-4"]), ("CORUMBA", ["CORUMBA-3"]),
                  ("ITUMBIARA", ["EMBORCAÇÃO", "C.BRANCO-2", "CORUMBA"]), ("C. DOURADA", ["ITUMBIARA"]), ("SÃO SIMÃO", ["C. DOURADA"])],
    "SAO FRANCISCO": [("LUIZ GONZAGA", ["SOBRADINHO"]), ("APOLONIO SALES", ["LUIZ GONZAGA"])],
    "TOCANTINS": [("CANA BRAVA", ["SERRA DA MESA"]), ("SAO SALVADOR", ["CANA BRAVA"]), ("PEIXE ANGICAL", ["SAO SALVADOR"]),
                  ("LAJEADO", ["PEIXE ANGICAL"]), ("ESTREITO", ["LAJEADO"]), ("TUCURUI", ["ESTREITO"])],
    "URUGUAI": [("MACHADINHO", ["BARRA GRANDE", "CAMPOS NOVOS"]), ("ITÁ", ["MACHADINHO"]), ("FOZ CHAPECO", ["ITÁ"])],
    "PARANA": [("JUPIA", ["I. SOLTEIRA", "TRÊS IRMÃOS"]), ("PORTO PRIMAVERA", ["JUPIA"])],
    "JACUI": [("JACUI", ["PASSO REAL"]), ("ITAUBA", ["JACUI"]), ("D. FRANCISCA", ["ITAUBA"])],
    "DOCE": [("BAGUARI", ["CANDONGA"]), ("AIMORES", ["BAGUARI"]), ("MASCARENHAS", ["AIMORES"])],
}
ONS_WINDOW = ("2015-01-01", "2025-12-31 23:00")
MIN_COV = 0.90


def ons_coverage():
    cols = ["nom_reservatorio", "din_instante", "val_vazaoafluente", "val_vazaodefluente"]
    parts = []
    for y in range(2015, 2026):
        for m in range(1, 13):
            p = os.path.join(D, "ons_hourly", f"DADOS_HIDROLOGICOS_HO_{y}_{m:02d}.parquet")
            if os.path.exists(p):
                parts.append(pd.read_parquet(p, columns=cols))
    df = pd.concat(parts, ignore_index=True)
    df = df[(df.din_instante >= ONS_WINDOW[0]) & (df.din_instante <= ONS_WINDOW[1])]
    n_hours = int((pd.Timestamp(ONS_WINDOW[1]) - pd.Timestamp(ONS_WINDOW[0])) / pd.Timedelta("1h")) + 1
    g = df.groupby("nom_reservatorio")
    cov_aflu = g.val_vazaoafluente.apply(lambda s: s.notna().sum()) / n_hours
    cov_deflu = g.val_vazaodefluente.apply(lambda s: s.notna().sum()) / n_hours
    return cov_aflu.to_dict(), cov_deflu.to_dict(), n_hours


def ons_split():
    ca, cd, n_hours = ons_coverage()
    tasks, excluded = [], []
    for river, pairs in TOPOLOGY.items():
        for tgt, ups in pairs:
            covs = {"target_inflow": ca.get(tgt, 0.0), **{f"input_outflow:{u}": cd.get(u, 0.0) for u in ups}}
            ok = all(v >= MIN_COV for v in covs.values())
            rec = {"river": river, "target": tgt, "inputs": ups, "coverage": {k: round(float(v), 4) for k, v in covs.items()}}
            (tasks if ok else excluded).append(rec)
    rivers = sorted({t["river"] for t in tasks})
    eligible_dev = [r for r in rivers if sum(t["river"] == r for t in tasks) >= 3]
    dev_river = str(np.random.default_rng(SEED_ONS).choice(eligible_dev))
    return {"window": ONS_WINDOW, "hours_in_window": n_hours, "aggregation": "3-hour means (pre-declared)",
            "min_coverage": MIN_COV, "dev_river": dev_river,
            "development": [t for t in tasks if t["river"] == dev_river],
            "held_out": [t for t in tasks if t["river"] != dev_river], "excluded_low_coverage": excluded}


def camels_split():
    z = zipfile.ZipFile(os.path.join(D, "camels_br", "01_CAMELS_BR_attributes.zip"))
    rd = lambda f: pd.read_csv(io.BytesIO(z.read("01_CAMELS_BR_attributes/" + f)), sep=r"\s+")
    h, q = rd("camels_br_human_intervention.txt"), rd("camels_br_quality_check.txt")
    a = h.merge(q, on="gauge_id")
    elig = a[(a.consumptive_use_perc < 1.0) & (a.regulation_degree < 0.05) & (a.q_quality_control_perc >= 95.0)]
    ids = sorted(elig.gauge_id.astype(int).tolist())
    rng = np.random.default_rng(SEED_CAMELS)
    pick = rng.permutation(ids)
    return {"eligibility": "consumptive_use_perc < 1; regulation_degree < 0.05; q_quality_control_perc >= 95",
            "n_eligible": len(ids), "development": sorted(int(x) for x in pick[:10]),
            "held_out": sorted(int(x) for x in pick[10:60]),
            "target": "daily streamflow", "inputs": ["precipitation", "actual evapotranspiration", "temperature"]}


def bdg2_split():
    z = zipfile.ZipFile(os.path.join(D, "bdg2", "building-data-genome-project-2-v1.0.zip"))
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    meters = []
    for kind in ("chilledwater", "hotwater", "steam"):
        m = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
        cov = m.notna().mean()
        nz = (m.fillna(0) != 0).mean()
        ok = cov[(cov >= MIN_COV) & (nz >= 0.5)].index
        meters += [f"{kind}:{b}" for b in ok]
    meters = sorted(meters)
    pick = np.random.default_rng(SEED_BDG2).permutation(meters)
    return {"eligibility": f"cleaned heating/cooling meters (chilledwater, hotwater, steam) with coverage >= {MIN_COV} and >= 50% non-zero",
            "n_eligible": len(meters), "development": sorted(pick[:5].tolist()), "held_out": sorted(pick[5:35].tolist()),
            "inputs": "site weather (air temperature, dew temperature, etc.)"}


def main():
    split = {"created": pd.Timestamp.now().isoformat(timespec="seconds"),
             "seeds": {"ons": SEED_ONS, "camels_br": SEED_CAMELS, "bdg2": SEED_BDG2},
             "data_checksums_sha256": hashlib.sha256(open(os.path.join(D, "SHA256SUMS.txt"), "rb").read()).hexdigest(),
             "ons": ons_split(), "camels_br": camels_split(), "bdg2": bdg2_split(),
             "synthetic": "pure synthetic (mechanism tests) and semi-synthetic (real inputs through declared structures) are generated later, from DEVELOPMENT inputs only for tuning"}
    p = os.path.join(HERE, "SPLIT_V052.json")
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(split, f, indent=1, ensure_ascii=False)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest()
    with open(os.path.join(HERE, "SPLIT_V052_SHA256.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write(f"{h} *SPLIT_V052.json\n")
    o = split["ons"]
    print("ONS dev river:", o["dev_river"], "| dev tasks", len(o["development"]), "| held-out", len(o["held_out"]),
          "| excluded", len(o["excluded_low_coverage"]))
    print("CAMELS eligible", split["camels_br"]["n_eligible"], "| BDG2 eligible", split["bdg2"]["n_eligible"])
    print("SPLIT sha256", h)


if __name__ == "__main__":
    main()
