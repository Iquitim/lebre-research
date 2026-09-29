"""real_unit.py — dev-only: input-level v0.52 (lebre_v052u) vs atomic v0.52 on the real DEVELOPMENT tasks,
scored on the COMP_DEV common mask, relative to NLinear (criterion 3 of the reformulation)."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, data_v052 as D  # noqa: E402

MODEL = sys.argv[1] if len(sys.argv) > 1 else "unit"
TAG = {"unit": "UNIT", "hier": "HIER"}[MODEL]


def job(task):
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    if MODEL == "hier":
        from lebre_v052h import LebreV052H
        m = LebreV052H(d=X.shape[1], season=s)
    else:
        from lebre_v052u import LebreV052U
        m = LebreV052U(d=X.shape[1], season=s)
    pred = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(len(y))])
    return task, pred, m.fp_total() / len(y), str(m.structure())

if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        res = list(ex.map(job, tasks, chunksize=1))
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); rows = []
    for task, pred, fp, st in res:
        y = D.load(task)["y"]; ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        mask &= np.isfinite(pred)
        mse = lambda p: float(np.mean((y[mask] - p[mask]) ** 2))
        nl = mse(comp[f"{task}|NLINEAR_ONLINE"])
        rows.append({"task": task, "unit": mse(pred) / nl, "atom": mse(comp[f"{task}|v052"]) / nl if f"{task}|v052" in comp.files else np.nan,
                     "fp_unit": fp, "structure": st})
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, f"REAL_{TAG}.csv"), index=False)
    np.savez_compressed(os.path.join(HERE, f"REAL_{TAG}_PREDS.npz"), **{t: p for t, p, _, _ in res})
    for grp in ("ons", "camels", "bdg2", ""):
        q = df[df.task.str.startswith(grp)]
        print(grp or "ALL", {c: round(float(np.exp(np.log(q[c]).mean())), 3) for c in ("unit", "atom")}, "fp", round(q.fp_unit.mean()))
    print(df[["task", "unit", "atom", "structure"]].to_string())
