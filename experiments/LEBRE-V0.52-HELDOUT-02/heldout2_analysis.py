#!/usr/bin/env python3
"""heldout2_analysis.py — PRE-REGISTERED analysis of RESERVA 2 (written before any access to its series).

Metric: per series, MSE relative to NLINEAR_ONLINE on the common mask (last 70%, observed target, every model with >= 95%
finite predictions must be finite; below 95% = FAILED on that series). Geometric mean per group (CAMELS, BDG2) and over all
series; 95% CIs by stratified bootstrap over series (2000 resamples, seed 8002).
CATASTROPHIC series for a model: relative MSE > 10, OR max |forecast - median(y)| > 10 x the observed range of y in the
test region, OR any non-finite forecast at an observed test step.
BUDGET CLASS (mean FP/step <= 2000): V052_CORRIGIDA, V052_CONGELADA, V051, NLINEAR_ONLINE, DLINEAR_ONLINE, HOLT_WINTERS,
ARX_NLMS, LASSO_ONLINE. REFERENCES (outside the class): AIRLINE_X (SARIMAX with inputs; MLE fit), ARX_RLS_PLS (~4e4 FP),
CHRONOS2_COV (~1e9-1e10 FP; 1000-point protocol).
Questions: Q1 catastrophic series of CORRIGIDA (and CONGELADA); Q2 paired CORRIGIDA / CONGELADA; Q3 rank of CORRIGIDA in the
budget class; Q4 fraction of the ceiling (CORRIGIDA vs CHRONOS2_COV on the 1000 points; also vs AIRLINE_X, ARX_RLS_PLS);
Q5 robustness (worst group, share > 1.5, catastrophic counts); Q6 cost of CORRIGIDA (mean <= 400, max <= 1000 FP)."""
import glob
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = ["V052_CORRIGIDA", "V052_CONGELADA", "V051", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "ARX_NLMS", "LASSO_ONLINE"]
REFS = ["AIRLINE_X", "ARX_RLS_PLS"]
MAIN = BUDGET + REFS
REF = "NLINEAR_ONLINE"


def gm(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return float(np.exp(np.log(v).mean())) if len(v) else float("nan")


if __name__ == "__main__":
    rows, pts, meta, cat = [], [], [], []
    for f in sorted(glob.glob(os.path.join(HERE, "preds", "*.npz"))):
        Z = np.load(f); info = json.load(open(f.replace(".npz", ".json"), encoding="utf-8")); task = info["task"]; grp = task.split(":")[0]
        y = Z["y"]; T = len(y); ts = int(0.3 * T); mask = np.isfinite(y); mask[:ts] = False
        failed = {m for m in MAIN if np.isfinite(Z[m][mask]).mean() < 0.95}
        for m in MAIN:
            if m not in failed:
                mask &= np.isfinite(Z[m])
        nl = float(np.mean((y[mask] - Z[REF][mask]) ** 2))
        yt = y[ts:][np.isfinite(y[ts:])]; rng_ = float(yt.max() - yt.min()) or 1.0; med = float(np.median(yt))
        r = {"task": task, "group": grp, "gapfrac": float(Z["gapfrac"])}
        for m in MAIN:
            r[m] = float("nan") if m in failed else float(np.mean((y[mask] - Z[m][mask]) ** 2)) / nl
            pm = Z[m][ts:]; obs = np.isfinite(y[ts:])              # models that skip missing-target steps leave NaN there
            cat.append({"task": task, "model": m, "catastrophic": bool((np.isfinite(r[m]) and r[m] > 10) or (~np.isfinite(pm[obs])).any()
                                                                       or np.nanmax(np.abs(pm - med)) > 10 * rng_)})
        rows.append(r)
        ic = info["info"]["V052_CORRIGIDA"]; acc = eval(ic["accepted"]) if ic.get("accepted") else []
        meta.append({"task": task, "group": grp, "fp": ic["fp"], "p999": ic["p999"], "max": ic["max"], "coverage": ic["coverage"],
                     "clipped": ic["clipped"], "n_in": sum(1 for u in eval(ic["structure"]) if u[0] == "in"),
                     "first_acc": acc[0][0] if acc else None, **{f"fp_{m}": info["info"][m].get("fp") for m in MAIN if m in info["info"]}})
        cf = os.path.join(HERE, "chronos", os.path.basename(f))
        if os.path.exists(cf):
            Cz = np.load(cf); idx = Cz["idx"]; yp = y[idx]; ok = np.ones(len(idx), bool)
            cand = {m: Z[m][idx] for m in MAIN if m not in failed}; cand["CHRONOS2_COV"] = Cz["CHRONOS2_COV"]
            for v in cand.values():
                if np.isfinite(v).mean() > 0.95:
                    ok &= np.isfinite(v)
            nlp = float(np.mean((yp[ok] - cand[REF][ok]) ** 2))
            pts.append({"task": task, "group": grp, **{m: float(np.mean((yp[ok] - v[ok]) ** 2)) / nlp for m, v in cand.items()}})
    R, M, Pp, K = pd.DataFrame(rows), pd.DataFrame(meta), pd.DataFrame(pts), pd.DataFrame(cat)
    for n, df in (("FULLMASK", R), ("META", M), ("1000PTS", Pp), ("CATASTROPHIC", K)):
        df.to_csv(os.path.join(HERE, f"RESERVA2_{n}.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(f"series {len(R)} (CAMELS {sum(R.group == 'camels')}, BDG2 {sum(R.group == 'bdg2')}); with Chronos {len(Pp)}; "
          f"mean share of missing target {R.gapfrac.mean():.3f} (max {R.gapfrac.max():.3f})")
    rng = np.random.default_rng(8002); gi = {g: np.flatnonzero(R.group.values == g) for g in R.group.unique()}
    bs = {m: [] for m in MAIN}; bp = {m: [] for m in MAIN if m != "V052_CORRIGIDA"}
    L = np.log(R[MAIN])
    for _ in range(2000):
        s = np.concatenate([rng.choice(ix, len(ix)) for ix in gi.values()]); Ls = L.iloc[s]
        for m in MAIN:
            bs[m].append(np.exp(np.nanmean(Ls[m])))
        for m in bp:
            bp[m].append(np.exp((Ls["V052_CORRIGIDA"] - Ls[m]).dropna().mean()))
    tab = []
    for m in MAIN:
        g = {k: gm(R[R.group == k][m]) for k in ("camels", "bdg2")}
        tab.append({"model": m, "class": "orçamento" if m in BUDGET else "referência", "CAMELS": g["camels"], "BDG2": g["bdg2"],
                    "ALL": gm(R[m]), "CI95": f"[{np.percentile(bs[m], 2.5):.3f}, {np.percentile(bs[m], 97.5):.3f}]",
                    "worst_group": max(g.values()), "share>1.5": float(np.mean(R[m].dropna() > 1.5)),
                    "catastrophic": int(K[K.model == m].catastrophic.sum()), "failed": int(R[m].isna().sum()),
                    "FP": M[f"fp_{m}"].astype(float).mean() if f"fp_{m}" in M else float("nan")})
    T1 = pd.DataFrame(tab); T1.to_csv(os.path.join(HERE, "RESERVA2_TABLE.csv"), index=False)
    print("\nFULL MASK — geometric mean of MSE relative to NLinear:"); print(T1.round(3).to_string(index=False))
    print("\nPAIRED CORRIGIDA / other (<1 = CORRIGIDA better), 95% CI, wins:")
    for m in bp:
        dd = (np.log(R.V052_CORRIGIDA) - np.log(R[m])).dropna()
        print(f"  vs {m:16s} {np.exp(dd.mean()):.3f} [{np.percentile(bp[m], 2.5):.3f}, {np.percentile(bp[m], 97.5):.3f}]  wins {int((dd < 0).sum())}/{len(dd)}")
    bud = T1[T1["class"] == "orçamento"].sort_values("ALL")
    print("\nQ3 budget-class ranking (ALL):", [(r.model, round(r.ALL, 3)) for r in bud.itertuples()])
    if len(Pp):
        print("\n1000 POINTS (relative to NLinear):")
        for m in ["V052_CORRIGIDA", "V052_CONGELADA", "AIRLINE_X", "ARX_RLS_PLS", "CHRONOS2_COV", "V051", "DLINEAR_ONLINE"]:
            print(f"  {m:16s}", {k: round(gm(Pp[Pp.group == k][m]), 3) for k in ("camels", "bdg2")}, "ALL", round(gm(Pp[m]), 3))
        dd = (np.log(Pp.V052_CORRIGIDA) - np.log(Pp.CHRONOS2_COV)).dropna()
        print(f"Q4 CORRIGIDA / CHRONOS2_COV (1000 pts): {np.exp(dd.mean()):.3f}, wins {int((dd < 0).sum())}/{len(dd)}")
    print(f"\nQ6 cost CORRIGIDA: mean {M.fp.mean():.0f} FP | p99.9 max {M.p999.max():.0f} | per-step max {M['max'].max():.0f} | "
          f"contract clips {int(M.clipped.sum())} | series with >= 1 input accepted {int((M.n_in > 0).sum())}/{len(M)} | "
          f"coverage {M.coverage.mean():.3f}")
