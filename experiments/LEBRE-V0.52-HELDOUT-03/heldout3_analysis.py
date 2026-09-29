#!/usr/bin/env python3
"""heldout3_analysis.py — PRE-REGISTERED analysis of RESERVA 3 (written before any access to its series).

Metric: per series, MSE relative to NLINEAR_ONLINE on the common mask (last 70%, observed target; every model with >= 95%
finite predictions there must be finite; below 95% = FAILED on that series). Geometric means per group (CAMELS, BDG2) and
over all series; 95% CIs by stratified bootstrap over series (2000 resamples, seed 8003).
CATASTROPHIC: relative MSE > 10, OR max |forecast - median(y)| > 10 x the observed range of y in the test region, OR a
non-finite forecast at an observed test step.
BUDGET CLASS (<= ~10^4 FLOPs per forecast): V052_PY, V052_C32, V051, NLINEAR_ONLINE, DLINEAR_ONLINE, HOLT_WINTERS, ARX_NLMS,
LASSO_ONLINE, FITS, SPARSETSF. REFERENCES: AIRLINE_X, ARX_RLS_PLS, TTM_ZS, TTM_FT_EXOG, CHRONOS2_COV (1000-point protocol for
the last three).
Q1 catastrophic series of V052_PY (expected 0); Q2 rank of V052_PY in the budget class; Q3 fraction of the ceilings
(V052_PY / CHRONOS2_COV, / TTM_ZS, / TTM_FT_EXOG on the 1000 points; / AIRLINE_X, / ARX_RLS_PLS on the full mask);
Q4 robustness (worst group, share > 1.5, catastrophic counts); Q5 C float32 port on unseen data (identical accepted-change
sequences in >= 90% of the series and median |relative NMSE difference| < 1e-4); Q6 cost (analytic FP mean <= 400 and per-step
maximum <= 1000; microcontroller instructions per step on 4 series from mcu/*.txt)."""
import glob
import json
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BUDGET = ["V052_PY", "V052_C32", "V051", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "ARX_NLMS", "LASSO_ONLINE", "FITS", "SPARSETSF"]
REFS = ["AIRLINE_X", "ARX_RLS_PLS"]
FM = ["TTM_ZS", "TTM_FT_EXOG", "CHRONOS2_COV"]
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
        yt = y[ts:][np.isfinite(y[ts:])]; rng_ = float(yt.max() - yt.min()) or 1.0; med = float(np.median(yt)); obs = np.isfinite(y[ts:])
        r = {"task": task, "group": grp}
        for m in MAIN:
            r[m] = float("nan") if m in failed else float(np.mean((y[mask] - Z[m][mask]) ** 2)) / nl
            pm = Z[m][ts:]
            cat.append({"task": task, "model": m, "catastrophic": bool((np.isfinite(r[m]) and r[m] > 10) or (~np.isfinite(pm[obs])).any()
                                                                       or np.nanmax(np.abs(pm - med)) > 10 * rng_)})
        rows.append(r)
        iv, ic = info["info"]["V052_PY"], info["info"]["V052_C32"]
        meta.append({"task": task, "group": grp, "d": info["d"], "fp": iv["fp"], "fp_p999": iv["fp_p999"], "fp_max": iv["fp_max"],
                     "n_acc": iv["n_accepted"], "coverage": iv["coverage"], "clipped": iv["clipped"],
                     "c32_events_equal": ic["events_equal"], "c32_overflow": ic["overflow"],
                     "rel_nmse_c32": r["V052_C32"] / r["V052_PY"] - 1 if np.isfinite(r["V052_C32"]) else float("nan"),
                     **{f"flops_{m}": info["info"][m].get("fp") for m in MAIN if m in info["info"]}})
        ff = os.path.join(HERE, "fm", os.path.basename(f))
        if os.path.exists(ff):
            Fz = np.load(ff); idx = Fz["idx"]; yp = y[idx]; ok = np.ones(len(idx), bool)
            cand = {m: Z[m][idx] for m in MAIN if m not in failed}; cand.update({m: Fz[m] for m in FM})
            for v in cand.values():
                if np.isfinite(v).mean() > 0.95:
                    ok &= np.isfinite(v)
            nlp = float(np.mean((yp[ok] - cand[REF][ok]) ** 2))
            pts.append({"task": task, "group": grp, **{m: float(np.mean((yp[ok] - v[ok]) ** 2)) / nlp for m, v in cand.items()},
                        **{f"flops_{m}": float(Fz[f"flops_{m}"]) for m in ("TTM_ZS", "TTM_FT_EXOG")}})
    R, M, P, K = pd.DataFrame(rows), pd.DataFrame(meta), pd.DataFrame(pts), pd.DataFrame(cat)
    for n, df in (("FULLMASK", R), ("META", M), ("1000PTS", P), ("CATASTROPHIC", K)):
        df.to_csv(os.path.join(HERE, f"RESERVA3_{n}.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(f"series {len(R)} (CAMELS {sum(R.group == 'camels')}, BDG2 {sum(R.group == 'bdg2')}); with foundation models {len(P)}")
    rng = np.random.default_rng(8003); gi = {g: np.flatnonzero(R.group.values == g) for g in R.group.unique()}
    L = np.log(R[MAIN]); bs = {m: [] for m in MAIN}; bp = {m: [] for m in MAIN if m != "V052_PY"}
    for _ in range(2000):
        s = np.concatenate([rng.choice(ix, len(ix)) for ix in gi.values()]); Ls = L.iloc[s]
        for m in MAIN:
            bs[m].append(np.exp(np.nanmean(Ls[m])))
        for m in bp:
            bp[m].append(np.exp((Ls["V052_PY"] - Ls[m]).dropna().mean()))
    tab = []
    for m in MAIN:
        g = {k: gm(R[R.group == k][m]) for k in ("camels", "bdg2")}
        tab.append({"model": m, "class": "orçamento" if m in BUDGET else "referência", "CAMELS": g["camels"], "BDG2": g["bdg2"],
                    "ALL": gm(R[m]), "CI95": f"[{np.percentile(bs[m], 2.5):.3f}, {np.percentile(bs[m], 97.5):.3f}]",
                    "worst_group": max(g.values()), "share>1.5": float(np.mean(R[m].dropna() > 1.5)),
                    "catastrophic": int(K[K.model == m].catastrophic.sum()), "failed": int(R[m].isna().sum()),
                    "FLOPs": M[f"flops_{m}"].astype(float).mean() if f"flops_{m}" in M else float("nan")})
    T1 = pd.DataFrame(tab); T1.to_csv(os.path.join(HERE, "RESERVA3_TABLE.csv"), index=False)
    print("\nFULL MASK — geometric mean of MSE relative to NLinear:"); print(T1.round(3).to_string(index=False))
    print("\nPAIRED V052_PY / other (<1 = V052 better), 95% CI, wins:")
    for m in bp:
        dd = (np.log(R.V052_PY) - np.log(R[m])).dropna()
        print(f"  vs {m:15s} {np.exp(dd.mean()):.3f} [{np.percentile(bp[m], 2.5):.3f}, {np.percentile(bp[m], 97.5):.3f}]  wins {int((dd < 0).sum())}/{len(dd)}")
    bud = T1[T1["class"] == "orçamento"].sort_values("ALL")
    print("\nQ2 budget-class ranking:", [(r_.model, round(r_.ALL, 3)) for r_ in bud.itertuples()])
    if len(P):
        print("\n1000 POINTS (relative to NLinear):")
        for m in ["V052_PY", "V052_C32", "AIRLINE_X", "ARX_RLS_PLS", "DLINEAR_ONLINE", "FITS"] + FM:
            print(f"  {m:15s}", {k: round(gm(P[P.group == k][m]), 3) for k in ("camels", "bdg2")}, "ALL", round(gm(P[m]), 3))
        for m in FM:
            dd = (np.log(P.V052_PY) - np.log(P[m])).dropna()
            print(f"  Q3 V052_PY / {m}: {np.exp(dd.mean()):.3f}, wins {int((dd < 0).sum())}/{len(dd)}")
        print("  FLOPs per forecast TTM_ZS", round(P.flops_TTM_ZS.mean()), "TTM_FT_EXOG", round(P.flops_TTM_FT_EXOG.mean()))
    eq = M.c32_events_equal.astype(bool)
    print(f"\nQ5 C float32 port: identical accepted-change sequences {int(eq.sum())}/{len(M)} ({eq.mean():.0%}); "
          f"median |rel NMSE diff| {M.rel_nmse_c32.abs().median():.2e} (max {M.rel_nmse_c32.abs().max():.2e}); overflow {int((M.c32_overflow > 0).sum())}")
    print(f"Q6 analytic FP: mean {M.fp.mean():.0f} | max per-step {M.fp_max.max():.0f} | p99.9 max {M.fp_p999.max():.0f} | "
          f"accepted changes per series {M.n_acc.mean():.2f} | coverage {M.coverage.mean():.3f}")
    for fm in sorted(glob.glob(os.path.join(HERE, "mcu", "*.txt"))):
        kv = dict(re.findall(r"^(\w+)=(.+)$", open(fm, encoding="utf-8", errors="replace").read(), re.M))
        if "STEP_SUM" in kv:
            T = int(kv["T"]); print(f"  MCU {kv['TASK']}: instr/step mean {int(kv['STEP_SUM']) / T:.0f}, p50 {kv['STEP_P50']}, "
                                    f"p99.9 {kv['STEP_P999']}, max {kv['STEP_MAX']}, scaler {int(kv['SCALER_SUM']) / T:.0f}, NMSE {kv['NMSE']}, "
                                    f"events {kv['EVENTS']}, RAM state {kv['STRUCT_BYTES']} B")
