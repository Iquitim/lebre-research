"""v055_data.py — every empirical number of the LEBRE v0.55 documents, read from the result files at build time (the
documents never cite local paths). Sources, all public:
  lebre-research (this repository): the v0.55 final pre-registered evaluation, the real-data validation, the external
  comparison, the formal note F1 sanity check and, through v054_data.py (imported, not changed), every earlier number;
  lebre-lab (github.com/Iquitim/lebre-lab): the v0.55 development rounds D1 to D4, the fixed bench (round D5) and the
  confirmation C1. Located by LEBRE_LAB, as in v053_data.py.
Only reads; nothing is written to either repository."""
import json
import math

import numpy as np

import v054_data as D54

ROOT, LAB, gm, _j = D54.ROOT, D54.LAB, D54.gm, D54._j
E = ROOT / "experiments"
AN = LAB / "analises"
FAMS55 = ["camels", "bdg2", "eolica", "solar", "niveis_ecb"]
COMP_MODELS = ["V054", "REF", "ARX_NLMS", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "ARX_RLS", "SARIMAX_X", "GBM",
               "CHRONOS2_COV", "CHRONOS2", "CHRONOS_BOLT_SMALL", "TTM_ZS", "TTM_FT_EXOG"]


def final55():
    R = _j(E / "LEBRE-V0.55-FINAL-01" / "FINAL_RESULTADO.json")
    S = R["series"]
    fam = {}
    for f in FAMS55:
        s = [x for x in S if x["familia"] == f]
        fam[f] = dict(R["familias"][f], ratios=[x["razao"] for x in s], cost_ratios=[x["custo_razao"] for x in s],
                      cost_ratio=float(np.median([x["custo_razao"] for x in s])))
    worst = sorted(S, key=lambda x: -x["razao"])[:3]; best = sorted(S, key=lambda x: x["razao"])[:3]
    return dict(R=R, fam=fam, n=len(S), crit=R["criterios"], series=S, worst=worst, best=best,
                cost_all=[x["custo_razao"] for x in S])


def val55():
    R = _j(E / "LEBRE-V0.55-VAL-01" / "VAL_RESULTADO.json")
    S = R["series"]
    ext = {f: (sum(bool(x["externas_A"]) for x in S if x["familia"] == f), sum(bool(x["externas_B10"]) for x in S if x["familia"] == f),
               sum(1 for x in S if x["familia"] == f)) for f in ("camels", "bdg2")}
    return dict(R=R, fam=R["familias"], crit=R["criterios"], ext=ext, n=len(S))


def comp55():
    R = _j(E / "LEBRE-V0.55-COMP-01" / "COMP_RESULTADO.json")
    med = _j(E / "LEBRE-V0.55-COMP-01" / "COMP_MEDIANAS_1000PTS.json")
    return dict(full=R["completa"], pts=R["pontos1000"], med=med)


def bench55():
    out = {}
    for rod in ("D5", "C1"):
        out[rod] = _j(AN / f"banco_v055_{rod}" / "resumo.json")
    dev = {}
    for k in ("d1", "d2", "d3", "d4"):
        dev[k] = _j(AN / f"{k}_v055" / "resumo.json")
    out["dev"] = dev
    c = out["C1"]["celulas"]
    integ = out["C1"]["criterios"]["B10"]
    out["C1_summary"] = dict(
        N1=(c["N1"]["A"]["ext_final"], c["N1"]["B10"]["ext_final"], c["N1"]["A"]["n"]),
        Q7=(c["Q7"]["A"]["passeios_final"], c["Q7"]["B10"]["passeios_final"], c["Q7"]["A"]["n"]),
        P6=(c["P6"]["A"]["retencao"], c["P6"]["B10"]["retencao"], c["P6"]["A"]["n"]),
        Q5=(c["Q5"]["A"]["retencao"], c["Q5"]["B10"]["retencao"], 2 * c["Q5"]["A"]["n"]),
        integ=(integ["C-h_conjunto"], integ["C-h_conjunto_ic95"]), cost=integ["C-g_mediana"],
        worst_f=max(c[k]["B10"]["razao_ic95"][1] for k in c),
        q={k: c[k]["B10"]["razao_geo"] for k in c if k.startswith("Q")})
    return out


def f1_check():
    """the formal note's numerical sanity check is a script; the document only states that it passes"""
    return dict(script_present=(E / "LEBRE-V0.55-DESIGN-NOTE-01" / "check_inequalities.py").exists())


def load():
    N = D54.load()
    N.update(final55=final55(), val55=val55(), comp55=comp55(), bench55=bench55(), f1=f1_check())
    return N


if __name__ == "__main__":
    N = load()
    F = N["final55"]
    print("final55", F["n"], {k: round(v["geo"], 3) for k, v in F["fam"].items()}, F["crit"]["R2_placebo"], round(F["crit"]["R4_mediana"], 3))
    print("val55", {k: round(v["geo"], 3) for k, v in N["val55"]["fam"].items()}, N["val55"]["ext"])
    print("C1", N["bench55"]["C1_summary"])
    print("comp keys", len(N["comp55"]["full"]), len(N["comp55"]["pts"]))
