"""tune_selfinput.py — dev-only: add the target's own past (y_{t-1}, forward-filled causally) as one more dictionary input
of the structural expert. Scored on the same common mask as COMP_DEV.csv."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402


def augment(X, y):
    ylag = pd.Series(y).ffill().shift(1).to_numpy()
    ylag[~np.isfinite(ylag)] = 0.0
    return np.column_stack([X, ylag])


def job(task):
    from lebre_v052 import LebreV052
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]
    Xa = augment(X, y); Xs = C._scaled_inputs(Xa)
    m = LebreV052(d=Xa.shape[1], season=s); pred = np.empty(len(y))
    for t in range(len(y)):
        pred[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
    return task, pred, m.fp_total() / len(y), str(m.structure())


if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(14) as ex:
        res = list(ex.map(job, tasks, chunksize=1))
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz"))
    rows = []
    for task, pred, fp, st in res:
        y = D.load(task)["y"]; T = len(y); ts = int(0.3 * T)
        cand = {k.split("|")[1]: comp[k] for k in comp.files if k.split("|")[0] == task}
        cand["v052_self"] = pred
        mask = np.isfinite(y); mask[:ts] = False
        for k, v in cand.items():
            if np.isfinite(v[mask]).mean() > 0.95:
                mask &= np.isfinite(v)
        var = float(np.var(y[mask]))
        for k, v in cand.items():
            rows.append({"task": task, "model": k, "nmse": float(np.mean((y[mask] - v[mask]) ** 2) / var)})
        rows.append({"task": task, "model": "fp_v052_self", "nmse": fp}); rows.append({"task": task, "model": "struct_v052_self", "nmse": np.nan, "s": st})
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "TUNE_SELFINPUT.csv"), index=False)
    p = df[~df.model.str.startswith(("fp_", "struct_"))].pivot_table(index="task", columns="model", values="nmse")
    pd.set_option("display.width", 250)
    print(p[["v052", "v052_self", "NLINEAR_ONLINE", "AIRLINE"]].round(4))
    for grp in ("ons", "camels", "bdg2", ""):
        q = p[p.index.str.startswith(grp)]
        print(grp or "ALL", {m: round(float(np.exp(np.log(q[m] / q["NLINEAR_ONLINE"]).mean())), 3) for m in ("v052", "v052_self", "AIRLINE")})
    print("FP v052_self mean", round(df[df.model == "fp_v052_self"].nmse.mean(), 1))
