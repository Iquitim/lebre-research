"""v054_data.py — every empirical number of the LEBRE v0.54 documents, read from the result files at build time (the
documents never cite local paths). Sources, all public:
  lebre-research (this repository): the v0.54 final pre-registered evaluation (experiments/LEBRE-V0.54-FINAL-01/), the
  post-promotion stress audit (experiments/LEBRE-V0.54-AUDIT-01/) and, through v053_data.py (imported, not changed), the
  v0.53 final evaluation, the M1/M2 development and the structural-core evidence;
  lebre-lab (github.com/Iquitim/lebre-lab): the v0.54 development (M5a, M5b, M4, M6), validations 6 and 7, the full
  combination on the bench (audit T10) and the errata 01 measurements. Located by LEBRE_LAB, as in v053_data.py.
Only reads; nothing is written to either repository."""
import glob
import json
from pathlib import Path

import numpy as np

import v053_data as D53

ROOT, LAB, gm, _j = D53.ROOT, D53.LAB, D53.gm, D53._j
FINAL54 = ROOT / "experiments" / "LEBRE-V0.54-FINAL-01"
AUDIT = ROOT / "experiments" / "LEBRE-V0.54-AUDIT-01"
AN = LAB / "analises"
FAMS54 = ["camels", "bdg2", "eolica", "solar", "niveis"]


def final54():
    R = _j(FINAL54 / "final_resultado.json")
    S = R["series"]
    fam = {}
    for f in FAMS54:
        s = [x for x in S if x["familia"] == f]
        fam[f] = dict(n=len(s), ratio=gm([x["v054_sobre_v053"] for x in s]), ratios=[x["v054_sobre_v053"] for x in s],
                      cost_ratio=float(np.median([x["razao_custo"] for x in s])), cost_ratios=[x["razao_custo"] for x in s],
                      cost53=float(np.median([x["custo_v053"] for x in s])), cost54=float(np.median([x["custo_v054"] for x in s])),
                      chronos54=gm([x.get("v054_sobre_chronos_1000") for x in s]),
                      chronos53=gm([x.get("v053_sobre_chronos_1000") for x in s]),
                      sarimax=gm([x.get("sarimax_sobre_v054") for x in s]),
                      removals=sum(len(x["remocoes"]) for x in s), slept=sum(1 for x in s if (x["m1"] or {}).get("sleeps", 0) > 0),
                      classes=R["resumo"][f]["classes"], c1=R["resumo"][f]["c1"], c2=R["resumo"][f]["c2"],
                      ext=R["resumo"][f]["externas"])
    return dict(R=R, fam=fam, n=len(S), promoted=R["promovida"], cost_median=R["custo_razao_mediana"],
                cost_ci=R["custo_razao_mediana_ic95"], short=R["curtas"], ram=R["ram_estimada_bytes"], ram_info=R["ram_info"],
                cost53_all=[x["custo_v053"] for x in S], cost54_all=[x["custo_v054"] for x in S],
                removals=sum(len(x["remocoes"]) for x in S), slept=sum(1 for x in S if (x["m1"] or {}).get("sleeps", 0) > 0))


def _resumos(pasta):
    out = {}
    for p in glob.glob(str(AN / pasta / "*.json")):
        d = _j(p)
        if "resumo" in d:                                             # custo.json e cenarios.json não têm resumo
            out[Path(p).stem] = d["resumo"]
    return out


def development54():
    """M5a (E1 to E3 and validation 6), M5b (E1, E2), M4 (E1, E2), M6 (E1, E2) and validation 7."""
    m5a = {e: {k: v["razao"] for k, v in _j(AN / f"m5a_{e}" / "custo.json").items() if isinstance(v, dict) and "razao" in v}
           for e in ("e1", "e2", "e3")}
    c3 = _j(AN / "m5a_e3" / "cenarios.json")
    e3f = _resumos("m5a_e3")
    v6 = _resumos("m5a_val6")
    v6series = sum(r["n"] for r in v6.values())
    m4 = {e: _resumos(f"m4_{e}") for e in ("e1", "e2")}
    m6 = {e: _resumos(f"m6_{e}") for e in ("e1", "e2")}
    v7 = {Path(p).stem: _j(p) for p in glob.glob(str(AN / "val7" / "*.json"))}
    v7s = [x for r in v7.values() for x in r["series"]]
    a50 = [x for x in v7["T-A01"]["series"] if x["d"] == 50]
    return dict(
        m5a=m5a, m5a_3a=c3["3a"]["geo_pos"], m5a_3b=dict(n=c3["3b"]["n_condicao"], frac=c3["3b"]["fracao_desperta"]),
        m5a_e3_worst=max(v["ic95"][1] for v in e3f.values()),
        v6=v6, v6_series=v6series, v6_worst=max(r["ic95"][1] for r in v6.values()),
        m4=m4, m4_a07=dict(e1=m4["e1"]["A07"]["ic95"][1], e2=m4["e2"]["A07"]["ic95"][1]),
        m4_worst=dict(e1=max(r["ic95"][1] for r in m4["e1"].values()), e2=max(r["ic95"][1] for r in m4["e2"].values())),
        m6=m6, v7=v7, v7_series=len(v7s), v7_m4={k: r["resumo"] for k, r in v7.items()},
        v7_m5b_core50=float(np.mean([x["m5b"]["nucleo_com"] for x in a50]) / np.mean([x["m5b"]["nucleo_sem"] for x in a50])),
        v7_a05_removed=sum(any(e["sai"] == ["in", 0] and 15000 <= e["t"] <= 25000 for e in x["m4"]["remocoes"])
                           for x in v7["T-A05"]["series"]),
        v7_a07_removals=sum(len(x["m4"]["remocoes"]) for x in v7["T-A07"]["series"]))


def audit():
    A = _j(AUDIT / "analise_resultados.json")
    t10 = _resumos("auditoria_v054_e20")
    e01 = [x for p in glob.glob(str(AN / "errata01_v054" / "*.json")) for x in _j(p)["series"]]
    e01_fam = {}
    for p in glob.glob(str(AN / "errata01_v054" / "*.json")):
        ss = _j(p)["series"]
        e01_fam[_j(p)["familia"]] = (max(x["pico_e01"] for x in ss) / max(x["pico_v053"] for x in ss),
                                     max(x["pico_prom"] for x in ss) / max(x["pico_v053"] for x in ss))
    e2 = {Path(p).stem: _j(p)["series"] for p in glob.glob(str(AN / "errata01_v054_e2" / "*.json"))}
    e2_peak = {g: (max(x["pico_e01"] for x in ss) / max(x["pico_v053"] for x in ss),
                   max(x["pico_prom"] for x in ss) / max(x["pico_v053"] for x in ss)) for g, ss in e2.items()}
    return dict(A=A, t10=t10, t10_worst=max(t10.items(), key=lambda kv: kv[1]["ic95"][1]),
                e01_series=len(e01), e01_identical=sum(x["identica"] and x["estrutura_igual"] and x["relatorio_igual"] for x in e01),
                e01_costdiff=sum(abs(x["custo_e01"] - x["custo_prom"]) > 1e-9 * x["custo_prom"] for x in e01),
                e01_peak=max(v[0] for v in e01_fam.values()), e01_peak_prom=max(v[1] for v in e01_fam.values()),
                e2_series=sum(len(v) for v in e2.values()), e2_peak=e2_peak,
                e2_ok=all(abs(x["dif"]) <= 1e-6 and x["identica"] and x["estrutura_igual"] and x["relatorio_igual"]
                          for v in e2.values() for x in v))


def load():
    N = D53.load()
    N.update(final53=N["final"], final54=final54(), dev54=development54(), audit=audit())
    return N


if __name__ == "__main__":
    N = load()
    F = N["final54"]
    print("final54", F["n"], round(F["cost_median"], 3), F["cost_ci"], {k: round(v["ratio"], 3) for k, v in F["fam"].items()})
    d = N["dev54"]
    print("m5a", d["m5a"], "v6", d["v6_series"], round(d["v6_worst"], 4), "m4 A07", d["m4_a07"], "v7", d["v7_series"],
          round(d["v7_m5b_core50"], 3), d["v7_a05_removed"])
    a = N["audit"]
    print("audit alerts", a["A"]["alertas"], "| t10 worst", a["t10_worst"][0], round(a["t10_worst"][1]["ic95"][1], 4),
          "| e01", a["e01_series"], a["e01_identical"], a["e01_costdiff"], round(a["e01_peak"], 3), round(a["e01_peak_prom"], 3),
          "| e2", a["e2_series"], a["e2_ok"], {k: round(v[0], 3) for k, v in a["e2_peak"].items()})
