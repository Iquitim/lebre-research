"""abl_analysis.py — dev-only: ablations and strong comparators on the real development tasks.
Full common mask (all models finite, test region from 30%) and the 1000-point protocol (same points and mask as
COMP_DEV_1000PTS, with the Chronos rows). Geometric mean of NMSE relative to NLinear per group; mean FP/step.
SO_MEMORIA is computed here (memory expert alone, weekly cycle on hourly buildings)."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import chronos_dev as CH  # noqa: E402
import data_v052 as D  # noqa: E402
from lebre_v052 import Memory  # noqa: E402
from lebre_v052h import MemoryW  # noqa: E402


def memory_only(task, y, s):
    M = MemoryW(s, 168) if task.startswith("bdg2") else Memory(s)
    pred = np.full(len(y), np.nan)
    for t in range(len(y)):
        p = M.predict(); pred[t] = p
        M.update(float(y[t]) if np.isfinite(y[t]) else None, p, learn=bool(np.isfinite(y[t])))
    return pred, M.fp / len(y)


def gmean(v):
    return float(np.exp(np.log(np.asarray(v, float)).mean()))


if __name__ == "__main__":
    tasks = D.dev_tasks()
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); strong = np.load(os.path.join(HERE, "STRONG_DEV_PREDS.npz"))
    abl = np.load(os.path.join(HERE, "ABL_REAL_PREDS.npz"))
    cfp = pd.read_csv(os.path.join(HERE, "COMP_DEV.csv")); sfp = pd.read_csv(os.path.join(HERE, "STRONG_DEV.csv"))
    afp = pd.read_csv(os.path.join(HERE, "ABL_REAL.csv"))
    P = pd.read_csv(os.path.join(HERE, "COMP_DEV_1000PTS.csv"))
    rows, pts, fps = [], [], []
    for t in tasks:
        d = D.load(t); y = d["y"]
        preds = {"NLINEAR": comp[f"{t}|NLINEAR_ONLINE"], "ATOMICA": comp[f"{t}|v052"], "ARX_NLMS": comp[f"{t}|ARX_NLMS"],
                 "SARIMAX_X": comp[f"{t}|AIRLINE_X"], "ARX_RLS_PLS": strong[f"{t}|ARX_RLS_PLS"], "LASSO_ONLINE": strong[f"{t}|LASSO_ONLINE"]}
        for c in ("COMPLETA", "TUDO_LIGADO", "TUDO_LIGADO_RLS", "SEM_DIVISOES"):
            preds[c] = abl[f"{t}|{c}"]
        pm, fm = memory_only(t, y, d["season"]); preds["SO_MEMORIA"] = pm
        # full mask: test region, all models finite (a model that failed entirely would be excluded; none did)
        ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == t and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        for v in preds.values():
            mask &= np.isfinite(v)
        nl = float(np.mean((y[mask] - preds["NLINEAR"][mask]) ** 2))
        rows += [{"task": t, "model": m, "rel": float(np.mean((y[mask] - v[mask]) ** 2)) / nl} for m, v in preds.items()]
        # 1000-point protocol
        idx = CH.points(y); yt = y[idx]; ok = np.ones(len(idx), bool)
        for k in comp.files:
            if k.split("|")[0] == t and np.isfinite(comp[k][idx]).mean() > 0.95:
                ok &= np.isfinite(comp[k][idx])
        n_ref = int(P[P.task == t].n_points.iloc[0])
        var = float(np.var(yt[ok]))
        for m, v in preds.items():
            if m in ("NLINEAR", "ATOMICA", "ARX_NLMS", "SARIMAX_X"):
                continue
            okm = ok & np.isfinite(v[idx])
            pts.append({"task": t, "model": m, "nmse": float(np.mean((yt[okm] - v[idx][okm]) ** 2) / var), "n_points": int(okm.sum()), "n_ref": n_ref})
        fps.append({"task": t, "SO_MEMORIA": fm})
    R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, "ABL_FULLMASK.csv"), index=False)
    Q = pd.DataFrame(pts); A = pd.concat([P, Q[["task", "model", "nmse", "n_points"]]]); A.to_csv(os.path.join(HERE, "ABL_1000PTS.csv"), index=False)
    print("1000-pt mask check: rows with n != stored n:", int((Q.n_points != Q.n_ref).sum()))
    # cost per model (mean over tasks)
    cost = {"NLINEAR": cfp[cfp.model == "NLINEAR_ONLINE"].fp.mean(), "ATOMICA": cfp[cfp.model == "v052"].fp.mean(),
            "ARX_NLMS": cfp[cfp.model == "ARX_NLMS"].fp.mean(), "SARIMAX_X": cfp[cfp.model == "AIRLINE_X"].fp.mean(),
            "ARX_RLS_PLS": sfp[sfp.model == "ARX_RLS_PLS"].fp.mean(), "LASSO_ONLINE": sfp[sfp.model == "LASSO_ONLINE"].fp.mean(),
            "SO_MEMORIA": pd.DataFrame(fps).SO_MEMORIA.mean()}
    for c in ("COMPLETA", "TUDO_LIGADO", "TUDO_LIGADO_RLS", "SEM_DIVISOES"):
        cost[c] = afp[afp.cfg == c].fp.mean()
    order = ["COMPLETA", "TUDO_LIGADO", "TUDO_LIGADO_RLS", "SEM_DIVISOES", "SO_MEMORIA", "ATOMICA", "ARX_RLS_PLS", "LASSO_ONLINE",
             "ARX_NLMS", "SARIMAX_X"]
    print("\nFULL MASK (geometric mean, relative to NLinear):")
    out = []
    for m in order:
        q = R[R.model == m]
        out.append({"model": m, **{g or "TODAS": round(gmean(q[q.task.str.startswith(g)].rel), 3) for g in ("ons", "camels", "bdg2", "")},
                    "FP": round(cost[m]) if np.isfinite(cost[m]) else "n/d"})
    print(pd.DataFrame(out).to_string(index=False))
    pv = A.pivot_table(index="task", columns="model", values="nmse")
    print("\n1000 POINTS (relative to NLinear):")
    out = []
    for m in order[:5] + ["ARX_RLS_PLS", "LASSO_ONLINE", "CHRONOS2_COV", "CHRONOS2", "v052", "AIRLINE_X"]:
        out.append({"model": m, **{g or "TODAS": round(gmean(pv[pv.index.str.startswith(g)][m] / pv[pv.index.str.startswith(g)]["NLINEAR_ONLINE"]), 3)
                                   for g in ("ons", "camels", "bdg2", "")}})
    print(pd.DataFrame(out).to_string(index=False))
    print("\nCOMPLETA beats (1000 pts):", {m: int((pv.COMPLETA < pv[m]).sum()) for m in ("TUDO_LIGADO", "TUDO_LIGADO_RLS", "ARX_RLS_PLS", "LASSO_ONLINE", "CHRONOS2_COV")}, "of", len(pv))
