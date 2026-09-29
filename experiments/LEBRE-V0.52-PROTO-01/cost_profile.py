"""cost_profile.py — dev-only: per-step cost (FP) of the frozen v0.52 (measurement #4 configuration) on the real
development tasks: mean, p99, p99.9, max, against the dense online ARX with the same inputs, 144 + 132 d FP/step
(comp_dev.ArxNlms: 4 (1 + 33 d + 32) + 12)."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, data_v052 as D  # noqa: E402
import final4 as F4  # noqa: E402


def job(task):
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    kw = dict(F4.PADRAO, **(eval(os.environ["CFG"]) if os.environ.get("CFG") else {}))
    if task.startswith("bdg2"):
        kw["season2"] = 168
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    c = np.empty(len(y)); prev = 0.0
    for t in range(len(y)):
        m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
        tot = m.fp_total(); c[t] = tot - prev; prev = tot
    arx = 144 + 132 * X.shape[1]
    return {"task": task, "d": X.shape[1], "arx": arx, "mean": c.mean(), "p99": np.percentile(c, 99),
            "p999": np.percentile(c, 99.9), "max": c.max(), "mean/arx": c.mean() / arx, "p999/arx": np.percentile(c, 99.9) / arx}


if __name__ == "__main__":
    with ProcessPoolExecutor(15) as ex:
        R = pd.DataFrame(list(ex.map(job, D.dev_tasks(), chunksize=1)))
    R.to_csv(os.path.join(HERE, os.environ.get("OUT", "COST_PROFILE_DEV.csv")), index=False)
    pd.set_option("display.width", 200)
    print(R.round(2).to_string(index=False))
    print("\nmean over tasks: v052", round(R["mean"].mean()), "ARX", round(R.arx.mean()),
          "| tasks with mean > ARX:", int((R["mean/arx"] > 1).sum()), "of", len(R),
          "| max p99.9/ARX", round(R["p999/arx"].max(), 2), "| max peak", round(R["max"].max()))
