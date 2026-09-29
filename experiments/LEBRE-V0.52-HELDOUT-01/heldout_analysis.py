#!/usr/bin/env python3
"""heldout_analysis.py — PRE-REGISTERED analysis of the held-out run (written before any held-out access).

Metric: per series, MSE relative to NLINEAR_ONLINE on the common mask (test region = last 70% of the series; observed
target; every model with >= 95% finite predictions there must be finite; a model below 95% is counted as FAILED on that
series and left out of its aggregates). Aggregates: geometric mean per group (ONS, CAMELS, BDG2) and over all series
(each series weight 1); secondary: mean of the three group log-means. 95% CIs: stratified bootstrap over series (within
groups), 2000 resamples, seed 8001, for each model and for the paired ratio COMPLETA / other.
1000-point protocol (with the Chronos models): same points and rule, NMSE / NMSE of NLinear on those points.
Robustness: worst-group geometric mean; share of series with relative MSE > 1.5. Cost: mean FP/step; per-step p99.9 and
maximum of COMPLETA. Structure: accepted input units per series, first acceptance time, reported groups."""
import glob
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = ["V052_COMPLETA", "V052_SEM_DIVISOES", "V052_TUDO_LIGADO", "V052_TUDO_LIGADO_RLS", "V052_ATOMICA", "V051", "SO_MEMORIA",
        "ARX_RLS_PLS", "LASSO_ONLINE", "ARX_NLMS", "AIRLINE_X", "AIRLINE", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS",
        "RIVER_AMRULES"]
CHRON = ["CHRONOS2_COV", "CHRONOS2", "CHRONOS_BOLT_SMALL"]
REF = "NLINEAR_ONLINE"


def group(task):
    return task.split(":")[0]


def gm(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return float(np.exp(np.log(v).mean())) if len(v) else float("nan")


def boot(df, models, pairs, n=2000, seed=8001):
    """stratified bootstrap over series: CI of each model's all-series geometric mean and of paired ratios"""
    rng = np.random.default_rng(seed); L = np.log(df[models]); groups = df.group.values
    idx_g = {g: np.flatnonzero(groups == g) for g in np.unique(groups)}
    res = {m: [] for m in models}; rp = {p: [] for p in pairs}
    for _ in range(n):
        s = np.concatenate([rng.choice(ix, len(ix)) for ix in idx_g.values()]); Ls = L.iloc[s]
        for m in models:
            res[m].append(np.exp(np.nanmean(Ls[m])))
        for a, b in pairs:
            dd = (Ls[a] - Ls[b]).dropna(); rp[(a, b)].append(np.exp(dd.mean()))
    ci = {m: (np.percentile(v, 2.5), np.percentile(v, 97.5)) for m, v in res.items()}
    cp = {p: (np.percentile(v, 2.5), np.percentile(v, 97.5)) for p, v in rp.items()}
    return ci, cp


if __name__ == "__main__":
    rows, pts, meta = [], [], []
    for f in sorted(glob.glob(os.path.join(HERE, "preds", "*.npz"))):
        Z = np.load(f); info = json.load(open(f.replace(".npz", ".json"), encoding="utf-8")); task = info["task"]
        y = Z["y"]; T = len(y); ts = int(0.3 * T)
        mask = np.isfinite(y); mask[:ts] = False
        failed = {m for m in MAIN if m in Z.files and np.isfinite(Z[m][mask]).mean() < 0.95}
        for m in MAIN:
            if m in Z.files and m not in failed:
                mask &= np.isfinite(Z[m])
        nl = float(np.mean((y[mask] - Z[REF][mask]) ** 2))
        r = {"task": task, "group": group(task), "n_eval": int(mask.sum())}
        for m in MAIN:
            r[m] = float("nan") if (m not in Z.files or m in failed) else float(np.mean((y[mask] - Z[m][mask]) ** 2)) / nl
        rows.append(r)
        ic = info["info"]["V052_COMPLETA"]
        acc = eval(ic["accepted"]) if ic.get("accepted") else []
        meta.append({"task": task, "group": group(task), "d": info["d"], "failed": ",".join(sorted(failed)),
                     "fp_completa": ic["fp"], "p999": ic.get("p999"), "max": ic.get("max"), "coverage": ic.get("coverage"),
                     "n_in_units": sum(1 for u in eval(ic["structure"]) if u[0] == "in"), "first_acc": acc[0][0] if acc else None,
                     "groups": ic.get("groups"), **{f"fp_{m}": info["info"].get(m, {}).get("fp") for m in MAIN}})
        cf = os.path.join(HERE, "chronos", os.path.basename(f))
        if os.path.exists(cf):
            Cz = np.load(cf); idx = Cz["idx"]; yt = y[idx]; ok = np.ones(len(idx), bool)
            cand = {m: Z[m][idx] for m in MAIN if m in Z.files and m not in failed}
            cand.update({m: Cz[m] for m in CHRON if m in Cz.files})
            for v in cand.values():
                if np.isfinite(v).mean() > 0.95:
                    ok &= np.isfinite(v)
            nlp = float(np.mean((yt[ok] - cand[REF][ok]) ** 2))
            pr = {"task": task, "group": group(task), "n_points": int(ok.sum())}
            for m, v in cand.items():
                pr[m] = float(np.mean((yt[ok] - v[ok]) ** 2)) / nlp if np.isfinite(v[ok]).all() else float("nan")
            pts.append(pr)
    R = pd.DataFrame(rows); M = pd.DataFrame(meta); Pp = pd.DataFrame(pts)
    R.to_csv(os.path.join(HERE, "HELDOUT_FULLMASK.csv"), index=False); M.to_csv(os.path.join(HERE, "HELDOUT_META.csv"), index=False)
    Pp.to_csv(os.path.join(HERE, "HELDOUT_1000PTS.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(f"series: {len(R)} (ONS {sum(R.group == 'ons')}, CAMELS {sum(R.group == 'camels')}, BDG2 {sum(R.group == 'bdg2')}); "
          f"with Chronos: {len(Pp)}")
    print("failed models per series:", M[M.failed != ""][["task", "failed"]].to_string(index=False) if (M.failed != "").any() else "none")
    pairs = [("V052_COMPLETA", m) for m in MAIN if m != "V052_COMPLETA"]
    ci, cp = boot(R, MAIN, pairs)
    tab = []
    for m in MAIN:
        g = {k: gm(R[R.group == k][m]) for k in ("ons", "camels", "bdg2")}
        tab.append({"model": m, "ONS": g["ons"], "CAMELS": g["camels"], "BDG2": g["bdg2"], "ALL": gm(R[m]),
                    "CI95": f"[{ci[m][0]:.3f}, {ci[m][1]:.3f}]", "groups_eq": float(np.exp(np.mean(np.log(list(g.values()))))),
                    "worst_group": max(g.values()), "share>1.5": float(np.mean(R[m].dropna() > 1.5)),
                    "n_failed": int(R[m].isna().sum()), "FP": M[f"fp_{m}"].astype(float).mean()})
    T1 = pd.DataFrame(tab); T1.to_csv(os.path.join(HERE, "HELDOUT_TABLE_FULLMASK.csv"), index=False)
    print("\nFULL MASK — geometric mean of MSE relative to NLinear:"); print(T1.round(3).to_string(index=False))
    print("\nPAIRED RATIO COMPLETA / other (all series; <1 = COMPLETA better), 95% CI, wins of COMPLETA:")
    for a, b in pairs:
        dd = (np.log(R[a]) - np.log(R[b])).dropna()
        print(f"  vs {b:22s} {np.exp(dd.mean()):.3f}  [{cp[(a, b)][0]:.3f}, {cp[(a, b)][1]:.3f}]  wins {int((dd < 0).sum())}/{len(dd)}")
    if len(Pp):
        cols = ["V052_COMPLETA", "V052_SEM_DIVISOES", "V052_TUDO_LIGADO", "ARX_RLS_PLS", "AIRLINE_X", "V051"] + CHRON
        print("\n1000 POINTS — relative to NLinear:")
        t2 = [{"model": m, **{k: gm(Pp[Pp.group == k][m]) for k in ("ons", "camels", "bdg2")}, "ALL": gm(Pp[m]),
               "worst_group": max(gm(Pp[Pp.group == k][m]) for k in ("ons", "camels", "bdg2"))} for m in cols if m in Pp.columns]
        T2 = pd.DataFrame(t2); T2.to_csv(os.path.join(HERE, "HELDOUT_TABLE_1000PTS.csv"), index=False); print(T2.round(3).to_string(index=False))
        for m in CHRON + ["ARX_RLS_PLS"]:
            if m in Pp.columns:
                dd = (np.log(Pp.V052_COMPLETA) - np.log(Pp[m])).dropna()
                print(f"  COMPLETA / {m}: {np.exp(dd.mean()):.3f}, wins {int((dd < 0).sum())}/{len(dd)}")
    print("\nCOST (COMPLETA): mean FP", round(M.fp_completa.mean()), "| per-series mean max", round(M.fp_completa.max()),
          "| p99.9 max", round(M.p999.max()), "| per-step max", round(M["max"].max()))
    print("STRUCTURE (COMPLETA): series with >= 1 input unit accepted", int((M.n_in_units > 0).sum()), "of", len(M),
          "| mean input units", round(M.n_in_units.mean(), 2), "| median first acceptance", M.first_acc.median(),
          "| interval coverage mean", round(M.coverage.mean(), 3))
