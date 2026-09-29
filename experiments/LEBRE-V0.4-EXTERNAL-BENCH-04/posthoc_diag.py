"""posthoc_diag.py — POST-HOC diagnostic (not pre-registered; does not enter the BENCH-04 decision).

Question: is LEBRE v0.4's gap on BENCH-04 caused by the target representation (large level, slow drift) rather than by
the structure it can express? Environment-side transforms only, the frozen model is unchanged:
  RAW     : as in BENCH-04;
  DELTA   : model predicts d[t] = y[t] - y[t-1]; forecast = y[t-1] + d_hat;
  ZSCORE  : model predicts (y[t] - m)/s with causal running mean/std of the past target; forecast inverted.
  *_SL    : seasonal lag y[t-s] added as input (as in the S7 arm).
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"), os.path.join(ROOT, "data", "external_bench04"), ROOT):
    sys.path.insert(0, p)
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v042 import LebreV042  # noqa: E402
from load04 import TASKS, load  # noqa: E402


def run(args):
    task, mode, sl = args
    X, y, _, _, s, j = load(task)
    if sl:
        if not s:
            return None
        X = np.column_stack([X, np.r_[np.full(s, X[0, j]), y[:-s]]])
    ts = int(0.30 * len(X)); m = LebreV042(d=X.shape[1]); sc = CausalStandardScaler(d=X.shape[1])
    n = 0; mu = 0.0; ss = 0.0; err = []
    for t in range(len(X)):
        prev = X[t, j]; sd = np.sqrt(ss / n) if n > 1 and ss > 0 else 1.0
        tgt = {"RAW": y[t], "DELTA": y[t] - prev, "ZSCORE": (y[t] - mu) / sd}[mode]
        p = m.step(sc.transform(X[t]), float(tgt)); sc.update(X[t])
        yh = {"RAW": p, "DELTA": prev + p, "ZSCORE": mu + sd * p}[mode]
        if t >= ts:
            err.append((y[t] - yh) ** 2)
        n += 1; d = y[t] - mu; mu += d / n; ss += d * (y[t] - mu)
    return {"task_id": task, "variant": mode + ("_SL" if sl else ""),
            "nmse": float(np.mean(err) / (np.var(y[ts:]) + 1e-6)), "coverage": m.cover_hits / max(m.cover_n, 1)}


if __name__ == "__main__":
    jobs = [(t, md, sl) for t in TASKS for md in ("RAW", "DELTA", "ZSCORE") for sl in (False, True)]
    with ProcessPoolExecutor(8) as ex:
        rows = [r for r in ex.map(run, jobs) if r]
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "POSTHOC_DIAG.csv"), index=False)
    pd.set_option("display.width", 200)
    print(df.pivot(index="task_id", columns="variant", values="nmse").round(4).to_string())
    print(df.pivot(index="task_id", columns="variant", values="coverage").round(3).to_string())
