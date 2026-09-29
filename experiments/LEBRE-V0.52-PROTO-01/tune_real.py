"""tune_real.py — dev-only: hierarchical v0.52 configurations on the real DEVELOPMENT tasks (COMP_DEV common mask,
relative to NLinear), against the atomic v0.52; geometric means per group, FP/step."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, data_v052 as D  # noqa: E402
CFGS = eval(open(sys.argv[1], encoding="utf-8").read()) if len(sys.argv) > 1 else {"meas2": {}}
OUT = sys.argv[2] if len(sys.argv) > 2 else "TUNE_REAL.csv"


def job(a):
    task, name, kw = a
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    kw = dict(kw); weekly = kw.pop("weekly", False)
    if weekly and task.startswith("bdg2"):
        kw["season2"] = 168                                          # hourly buildings: the week, declared like the day
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pred = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(len(y))])
    return task, name, pred, m.fp_total() / len(y), str(m.structure())


if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        res = list(ex.map(job, [(t, n, kw) for t in tasks for n, kw in CFGS.items()], chunksize=1))
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); rows = []; ys = {t: D.load(t)["y"] for t in tasks}
    for task, name, pred, fp, st in res:
        y = ys[task]; ts = int(0.3 * len(y)); mask = np.isfinite(y); mask[:ts] = False
        for k in comp.files:
            if k.split("|")[0] == task and np.isfinite(comp[k][mask]).mean() > 0.95:
                mask &= np.isfinite(comp[k])
        mask &= np.isfinite(pred)
        mse = lambda p: float(np.mean((y[mask] - p[mask]) ** 2))
        nl = mse(comp[f"{task}|NLINEAR_ONLINE"])
        rows.append({"task": task, "cfg": name, "rel": mse(pred) / nl, "atom": mse(comp[f"{task}|v052"]) / nl, "fp": fp, "structure": st})
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, OUT), index=False)
    np.savez_compressed(os.path.join(HERE, OUT.replace(".csv", "_PREDS.npz")), **{f"{t}|{n}": p for t, n, p, _, _ in res})
    for grp in ("ons", "camels", "bdg2", ""):
        q = df[df.task.str.startswith(grp)]
        g = {n: round(float(np.exp(np.log(v.rel).mean())), 3) for n, v in q.groupby("cfg")}
        a = round(float(np.exp(np.log(q[q.cfg == q.cfg.iloc[0]].atom).mean())), 3)
        print(f"{grp or 'ALL':7s} atom {a}", g, "fp", {n: round(v.fp.mean()) for n, v in q.groupby("cfg")})
