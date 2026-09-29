"""dev_comparators.py — DEVELOPMENT-ONLY check of the new comparators (FITS, SparseTSF, TTM zero-shot, TTM fine-tuned
with exogenous inputs) against the frozen canonical LEBRE v0.52 and the existing comparators, on the 29 development
series. Full mask (FITS/SparseTSF) and the 1000-point protocol (all, with Chronos rows from COMP_DEV_1000PTS.csv).
Purpose: verify that the comparators run, are sane and are fairly configured BEFORE the reserve-3 pre-registration."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO); sys.path.insert(0, HERE)
import heldout2_cfg as CFG  # noqa: E402
import chronos_dev as CH  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402


def job(task):
    import torch
    torch.set_num_threads(3)
    import ttm_run as TT
    import ultralight as UL
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    kw = dict(CFG.CANONICAL)
    if task.startswith("bdg2"):
        kw["season2"] = 168
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pv = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(len(y))])
    idx = C._calib_n(y)
    ul = UL.run(task, y, idx)
    pts = CH.points(y)
    tt = TT.run(Xs, y, idx, pts)
    return task, pv, m.fp_total() / len(y), ul, pts, tt


def gm(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]
    return float(np.exp(np.log(v).mean()))


if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(5) as ex:
        res = list(ex.map(job, tasks, chunksize=1))
    comp = np.load(os.path.join(PROTO, "COMP_DEV_PREDS.npz")); P = pd.read_csv(os.path.join(PROTO, "COMP_DEV_1000PTS.csv"))
    rows, prow, cost = [], [], []
    for task, pv, fp, ul, pts, tt in res:
        y = D.load(task)["y"]; ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        cand = {"V052": pv, "FITS": ul["FITS"][0], "SPARSETSF": ul["SPARSETSF"][0]}
        for k in ("NLINEAR_ONLINE", "DLINEAR_ONLINE", "AIRLINE_X", "ARX_NLMS", "v051"):
            cand[k] = comp[f"{task}|{k}"]
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        for v in cand.values():
            mask &= np.isfinite(v)
        nl = float(np.mean((y[mask] - cand["NLINEAR_ONLINE"][mask]) ** 2))
        rows.append({"task": task, **{k: float(np.mean((y[mask] - v[mask]) ** 2)) / nl for k, v in cand.items()}})
        yt = y[pts]; ok = np.ones(len(pts), bool)
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][pts]).mean() > 0.95:
                ok &= np.isfinite(comp[k][pts])
        var = float(np.var(yt[ok])); nlp = float(np.mean((yt[ok] - comp[f"{task}|NLINEAR_ONLINE"][pts][ok]) ** 2)) / var
        pr = {"task": task, "n_ok": int(ok.sum()), "n_ref": int(P[P.task == task].n_points.iloc[0])}
        for k, v in list(cand.items()) + [("TTM_ZS", None), ("TTM_FT_EXOG", None)]:
            vv = v[pts] if v is not None else tt[k][0]
            pr[k] = float(np.mean((yt[ok] - vv[ok]) ** 2)) / var / nlp
        for k in ("CHRONOS2_COV", "CHRONOS2"):
            pr[k] = float(P[(P.task == task) & (P.model == k)].nmse.iloc[0]) / nlp
        prow.append(pr)
        cost.append({"task": task, "V052": fp, "FITS": ul["FITS"][1], "SPARSETSF": ul["SPARSETSF"][1], "FITS_params": ul["FITS"][2],
                     "SPARSETSF_params": ul["SPARSETSF"][2], "TTM_ZS": tt["TTM_ZS"][1], "TTM_FT_EXOG": tt["TTM_FT_EXOG"][1]})
    R, Pp, K = pd.DataFrame(rows), pd.DataFrame(prow), pd.DataFrame(cost)
    for n, df in (("FULLMASK", R), ("1000PTS", Pp), ("COST", K)):
        df.to_csv(os.path.join(HERE, f"DEV_COMP_{n}.csv"), index=False)
    np.savez_compressed(os.path.join(HERE, "DEV_COMP_PREDS.npz"), **{f"{t}|{k}": v[0] for t, _, _, ul, _, tt in res for k, v in {**ul, **tt}.items()})
    print("1000-pt mask check (n_ok == stored):", bool((Pp.n_ok == Pp.n_ref).all()))
    pd.set_option("display.width", 220)
    for name, df, cols in (("FULL MASK", R, ["V052", "FITS", "SPARSETSF", "DLINEAR_ONLINE", "NLINEAR_ONLINE", "AIRLINE_X", "ARX_NLMS", "v051"]),
                           ("1000 POINTS", Pp, ["V052", "FITS", "SPARSETSF", "TTM_ZS", "TTM_FT_EXOG", "CHRONOS2_COV", "CHRONOS2", "AIRLINE_X", "DLINEAR_ONLINE"])):
        print(name); print(pd.DataFrame([{"model": c, **{g or "ALL": round(gm(df[df.task.str.startswith(g)][c]), 3) for g in ("ons", "camels", "bdg2", "")}}
                                          for c in cols]).to_string(index=False))
    print("mean FLOPs per forecast:", K.drop(columns="task").mean().round(0).to_dict())
