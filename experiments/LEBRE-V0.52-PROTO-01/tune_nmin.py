"""tune_nmin.py — dev-only: minimum episode length (n_min) of the scan rule on semi-synthetic tasks (real Grande inputs)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import semi_synth as SS  # noqa: E402


def job(a):
    task, seed, n_min = a
    from lebre_v052 import LebreV052
    X = SS.inputs(); y = SS.generate(task, seed, X); Xs = C._scaled_inputs(X)
    m = LebreV052(d=X.shape[1], season=8 if task == "SS4" else None, n_min=n_min)
    pred = np.array([m.step(Xs[t], float(y[t])) for t in range(len(y))])
    ts = int(0.3 * len(y)); truth = SS.TRUTH[task]; final = set(m.structure())
    acc = [e for e in m.events if e[1] == "accepted"]
    return {"task": task, "seed": seed, "n_min": n_min, "nmse": float(np.mean((y[ts:] - pred[ts:]) ** 2) / np.var(y[ts:])),
            "accepted": len(acc), "true_found": len(final & truth), "n_truth": len(truth),
            "false_exog": sum(1 for e in acc if e[3] and e[3] not in truth and e[3][1] != X.shape[1]),
            "experiments": m.k_started, "structure": str(sorted(final))}


if __name__ == "__main__":
    jobs = [(t, s, n) for t in ("SS0", "SS1", "SS2", "SS3") for s in (6101, 6102, 6103) for n in (100, 400, 1000)]
    with ProcessPoolExecutor(14) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    R.to_csv(os.path.join(HERE, "TUNE_NMIN.csv"), index=False)
    pd.set_option("display.width", 200)
    print(R.groupby(["task", "n_min"])[["nmse", "accepted", "true_found", "n_truth", "false_exog", "experiments"]].mean().round(3))
