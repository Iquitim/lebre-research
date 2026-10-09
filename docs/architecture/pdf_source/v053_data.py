"""v053_data.py — every empirical number of the LEBRE v0.53 documents, read from the result files at build time
(the documents never cite local paths). Two sources, both public:
  lebre-research (this repository): the final pre-registered evaluation (experiments/LEBRE-V0.53-FINAL-01/);
  lebre-lab (github.com/Iquitim/lebre-lab): development, validations 1 to 5 and diagnostics. Its checkout is located by
  the environment variable LEBRE_LAB, or by default as a sibling folder "lebre-lab" of this repository.
Only reads; nothing is written to either repository."""
import glob
import json
import math
import os
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FINAL = ROOT / "experiments" / "LEBRE-V0.53-FINAL-01"
LAB = Path(os.environ.get("LEBRE_LAB", str(ROOT.parent / "lebre-lab")))
FAMS = ["camels", "bdg2", "solar", "eolica", "carga", "fx_ret", "fx_abs", "fx_niv"]


def gm(v):
    v = np.asarray([x for x in v if x is not None], float)
    v = v[np.isfinite(v) & (v > 0)]
    return float(np.exp(np.log(v).mean())) if len(v) else float("nan")


def _j(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def lab_commit():
    r = subprocess.run(["git", "-C", str(LAB), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    return r.stdout.strip()


def final():
    R = _j(FINAL / "final_resultado.json")
    S = R["series"]
    fam = {}
    for f in FAMS:
        s = [x for x in S if x["familia"] == f]
        fam[f] = dict(n=len(s), ratio=gm([x["v053_sobre_v052"] for x in s]),
                      ratios=[x["v053_sobre_v052"] for x in s], inc=[x["acrescimo_custo"] for x in s],
                      inc_max=max(x["acrescimo_custo"] for x in s), cost53=float(np.mean([x["custo_v053"] for x in s])),
                      cost52=float(np.mean([x["custo_v052"] for x in s])),
                      chronos53=gm([x.get("v053_sobre_chronos_1000") for x in s]),
                      chronos52=gm([x.get("v052_sobre_chronos_1000") for x in s]),
                      sarimax=gm([x.get("sarimax_sobre_v053") for x in s]),
                      m1_weight_zero=sum(1 for x in s if (x["peso_m1_final"] or 0) < 1e-3),
                      classes=R["resumo"][f]["classes"], c1=R["resumo"][f]["c1"], c2=R["resumo"][f]["c2"],
                      ext=R["resumo"][f]["externas"])
    ad = _j(FINAL / "adendo_sarimax_fx.json")
    for f, rows in ad.items():
        fam[f]["sarimax_addendum"] = gm([r["v053"] for r in rows if r["ok"]])
        fam[f]["sarimax_addendum_52"] = gm([r["v052"] for r in rows if r["ok"]])
    ens = _j(FINAL / "ensaio_v052.json")
    ens_ok = [e for e in ens if not e["erro"]]
    return dict(R=R, fam=fam, overall=R["geral_v053_sobre_v052"], short=R["curtas"], ties=R["curtas_empates_exatos"],
                ram=R["ram_estimada_bytes"], ram_info=R["ram_info"], n=len(S), promoted=R["promovida"],
                inc_all=[x["acrescimo_custo"] for x in S],
                rehearsal=dict(n=len(ens), errors=len(ens) - len(ens_ok),
                               camels=gm([e["razao"] for e in ens_ok if e["tarefa"].startswith("camels")]),
                               bdg2=gm([e["razao"] for e in ens_ok if e["tarefa"].startswith("bdg2")])))


def f6():
    """F6 frontier: development families (E14 + E20) and validation 5."""
    dev = _j(LAB / "analises" / "e20_alvo.json")["familias"]
    v5 = _j(LAB / "analises" / "m1val5_alvo.json")["familias"]
    rows = []
    for name, src, d in [("B03", "dev", dev["B03"]), ("B07", "dev", dev["B07"]), ("VB07", "dev", dev["VB07"]),
                         ("XB07", "dev", dev["XB07"]), ("Z-B03", "val5", v5["ZB03"]), ("Z-B07", "val5", v5["ZB07"])]:
        rows.append(dict(name=name, src=src, v052=d["erro_v052"], v053=d["erro"], estar=d["e_estrela"],
                         meta=1.05 * d["e_estrela"], cost_ratio=d["custo"] / d["custo_v052"], variant=d["variante"], ok=d["atende"]))
    # E14: is v0.52 below the frontier? (8 families where the full linear comparator beats it by > 5%)
    e14 = {}
    for p in sorted(glob.glob(str(LAB / "diagnosticos" / "e14" / "*.json"))):
        R = _j(p)
        names = list(R[0]["v"])
        geo = {n: gm([x["v"][n][0] for x in R]) for n in names}
        cus = {n: float(np.mean([x["v"][n][1] for x in R])) for n in names}
        c = cus["v0.52"]
        cand = [geo[n] for n in names if n != "v0.52" and cus[n] <= c]
        e14[Path(p).stem] = dict(v052=geo["v0.52"], cost=c, best_same_cost=min(cand), below=geo["v0.52"] > 1.05 * min(cand))
    return dict(rows=rows, e14=e14)


def validations():
    """Validation 4 (M1 r2 + P: failed) and 5 (M1 r5 + Q2: confirmed)."""
    def fails(md):
        t = Path(md).read_text(encoding="utf-8")
        out = {}
        for ln in t.splitlines():
            if ln.startswith("| ") and ln.split("|")[1].strip() in ("1", "2", "4", "5", "6", "7"):
                out[ln.split("|")[1].strip()] = ln.split("|")[2].strip()
        return out
    v4 = fails(LAB / "analises" / "M1_VAL4_RESULTADO.md")
    v5 = fails(LAB / "analises" / "M1_VAL5_RESULTADO.md")
    n5 = sum(len(_j(p)["series"]) for p in glob.glob(str(LAB / "analises" / "m1val5" / "*.json")) if "CURTAS" not in p)
    return dict(v4_fails=v4, v5_fails=v5, v5_series=n5)


def development():
    """Extended development (E20: M1 r5 + Q2 on 64 families) and the cost audit (E21, E22)."""
    fams = [p for p in glob.glob(str(LAB / "analises" / "e20_prod_q2" / "*.json"))]
    nser = sum(len(_j(p)["series"]) for p in fams)
    e22 = [x for p in glob.glob(str(LAB / "diagnosticos" / "e22" / "*.json")) for x in _j(p)]
    e21 = [_j(p) for p in glob.glob(str(LAB / "diagnosticos" / "e21" / "*.json"))]
    med = lambda k: float(np.median([r[k] for r in e21]))
    audit = [x["custo_novo"] / x["custo_antigo"] for x in e22]
    inc = []
    for p in glob.glob(str(LAB / "diagnosticos" / "e22" / "*.json")):
        o, fam = Path(p).stem.split("_", 1)
        reg = _j(LAB / "analises" / ("m1val5" if o == "val5" else "e20_prod_q2") / f"{fam}.json")["series"]
        for x, r in zip(_j(p), reg):
            inc.append((x["custo_novo"] - r["custo_v052"], x["custo_novo"] / r["custo_v052"]))
    return dict(families=len(fams), series=nser, identity=(sum(x["igual"] for x in e22), len(e22)),
                audit_median=float(np.median(audit)), breakdown=dict(v052=med("v052_total"), m2=med("m2"), m1_rls=med("m1_rls"),
                                                                     m1_rest=med("m1_resto"), total=med("total")),
                inc_median=float(np.median([a for a, _ in inc])), inc_max=float(max(a for a, _ in inc)),
                ratio_median=float(np.median([b for _, b in inc])), ratio_max=float(max(b for _, b in inc)))


def shocks():
    """E15: share of the largest single step in the reference squared error (data property)."""
    t = (LAB / "diagnosticos" / "E15_RESULTADO.md").read_text(encoding="utf-8")
    rows = []
    for ln in t.splitlines():
        p = [c.strip() for c in ln.split("|")]
        if len(p) > 4 and p[3].endswith("%") and p[1] not in ("Família",):
            rows.append((p[1], p[2], float(p[3].rstrip("%").replace(",", ".")) / 100))
    big = sorted(rows, key=lambda r: -r[2])
    return dict(n=len(rows), over5=sum(1 for r in rows if r[2] > 0.05), top=big[:6])


def load():
    return dict(final=final(), f6=f6(), val=validations(), dev=development(), shocks=shocks(), lab_commit=lab_commit())


if __name__ == "__main__":
    N = load()
    print("lab", N["lab_commit"], "| final", round(N["final"]["overall"]["geo"], 3), "| f6", [(r["name"], round(r["v053"], 3)) for r in N["f6"]["rows"]])
    print("dev", N["dev"]["families"], N["dev"]["series"], N["dev"]["identity"], round(N["dev"]["inc_median"]), round(N["dev"]["ratio_median"], 2))
    print("val", N["val"]["v4_fails"], N["val"]["v5_series"], "| shocks", N["shocks"]["n"], N["shocks"]["over5"])
    print("e14 below:", [k for k, v in N["f6"]["e14"].items() if v["below"]])
