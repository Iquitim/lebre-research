"""tune_kappa.py — dev-only: target-contract threshold kappa (8, 16, 32, off), scored on the COMP_DEV common mask."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402

KAPPAS = [8.0, 16.0, 32.0, None]


def job(a):
    task, kappa = a
    from lebre_v052 import LebreV052
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    m = LebreV052(d=X.shape[1], season=s, target_contract=kappa is not None, kappa=kappa or 8.0)
    pred = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(len(y))])
    return task, kappa, pred, m.n_target_out


if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(10) as ex:
        res = list(ex.map(job, [(t, k) for t in tasks for k in KAPPAS], chunksize=1))
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz"))
    rows = []
    for task, kappa, pred, nout in res:
        y = D.load(task)["y"]; ts = int(0.3 * len(y))
        mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        mask &= np.isfinite(pred)
        nl = comp[f"{task}|NLINEAR_ONLINE"]
        rows.append({"task": task, "kappa": str(kappa), "rel_nlinear": float(np.mean((y[mask] - pred[mask]) ** 2) / np.mean((y[mask] - nl[mask]) ** 2)),
                     "n_out": nout})
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "TUNE_KAPPA.csv"), index=False)
    for grp in ("ons", "camels", "bdg2", ""):
        q = df[df.task.str.startswith(grp)]
        print(grp or "ALL", {k: round(float(np.exp(np.log(g.rel_nlinear).mean())), 3) for k, g in q.groupby("kappa")},
              "n_out", {k: int(g.n_out.sum()) for k, g in q.groupby("kappa")})
