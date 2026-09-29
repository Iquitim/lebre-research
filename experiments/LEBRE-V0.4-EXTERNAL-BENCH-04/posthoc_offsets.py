"""posthoc_offsets.py — POST-HOC: v0.4 vs v0.3.2 on BENCH-04 with 10 start offsets (0, 50, ..., 450 steps dropped).
LEBRE is deterministic, so BENCH-04 seeds give one realisation per task; offsets expose sensitivity to initial conditions.
Test window fixed (same absolute steps, from 0.30 T) for every offset."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02"), os.path.join(ROOT, "data", "external_bench04"),
          os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"), ROOT):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v042 import LebreV042  # noqa: E402
from load04 import TASKS, load  # noqa: E402

OFFSETS = list(range(0, 500, 50))
ARMS = {"V042": lambda d: LebreV042(d=d), "V042_NOCLIP": lambda d: LebreV042(d=d, clip=False),
        "V032": lambda d: B.LebreStep(d).m}


def run(args):
    task, arm, off = args
    X, y, _, _, _, _ = load(task); T = len(X); ts = int(0.30 * T)
    sc = CausalStandardScaler(d=X.shape[1]); m = ARMS[arm](X.shape[1]); e = []
    for i in range(off, T):
        p = m.step(sc.transform(X[i]), float(y[i])); sc.update(X[i])
        if i >= ts:
            e.append((y[i] - p) ** 2)
    return {"task_id": task, "arm": arm, "offset": off, "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6))}


if __name__ == "__main__":
    jobs = [(t, a, o) for t in TASKS for a in ARMS for o in OFFSETS]
    with ProcessPoolExecutor(16) as ex:
        df = pd.DataFrame(list(ex.map(run, jobs, chunksize=2)))
    df.to_csv(os.path.join(HERE, "POSTHOC_OFFSETS.csv"), index=False)
    med = df.groupby(["task_id", "arm"]).nmse.median().unstack()
    q = df.groupby(["task_id", "arm"]).nmse.agg(lambda s: f"{s.quantile(.1):.3f}-{s.quantile(.9):.3f}").unstack()
    w = df.pivot_table(index=["task_id", "offset"], columns="arm", values="nmse")
    wins = (w.V042 < w.V032).groupby(level=0).sum()
    pd.set_option("display.width", 220)
    print("mediana sobre 10 offsets:\n" + med.round(4).to_string())
    print("\nfaixa p10-p90:\n" + q.to_string())
    print("\noffsets em que V042 < V032 (de 10):\n" + wins.to_string())
    for a in ("V042", "V042_NOCLIP"):
        print(f"\nrazao geometrica {a}/V032 (medianas): {np.exp(np.log(med[a] / med.V032).mean()):.3f};"
              f" pareada por offset: {np.exp(np.log(w[a] / w.V032).mean()):.3f}")
