#!/usr/bin/env python3
"""
run_bench01_controls.py — simplicity controls that isolate target autoregression on BENCH-01.
  C5_PERSISTENCE : y_hat_t = y_{t-1}                                      (0 FLOPs)
  C6_ARX_NLMS    : NLMS(mu=0.1, same as LEBRE v0.3) on [x_t, 1, y_{t-1}]  (no lifecycle, no lags)
Uncalibrated, like LEBRE v0.3. Same harness, seeds and split as BENCH-01B.
"""
import os, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
from experiments.bench01.streams import get_stream  # noqa: E402
from experiments.bench01.runner import run_full_stream, TASKS  # noqa: E402


class Persistence:
    def __init__(self, d): self.y_prev = 0.0
    def step(self, x, y):
        p = self.y_prev; self.y_prev = float(y); return p, 0.0
    def get_memory_bytes(self): return 4
    def get_active_params(self): return 0


class ArxNlms:
    def __init__(self, d, mu=0.1):
        self.w = np.zeros(d + 2); self.y_prev = 0.0; self.mu = mu; self.d = d
    def step(self, x, y):
        phi = np.concatenate([x, [1.0, self.y_prev]])
        n = len(phi)
        pred = float(self.w @ phi)
        e = float(y) - pred
        self.w += self.mu * e / (1e-6 + float(phi @ phi)) * phi
        self.y_prev = float(y)
        return pred, float((2 * n - 1) + 1 + (2 * n - 1) + 3 + 2 * n)
    def get_memory_bytes(self): return 4 * (self.d + 3)
    def get_active_params(self): return self.d + 2


MODELS = {"C5_PERSISTENCE": Persistence, "C6_ARX_NLMS": ArxNlms}


def run_one(args):
    task_id, seed, mid = args
    X, y = get_stream(task_id, seed=seed)
    r = run_full_stream(MODELS[mid](X.shape[1]), X, y, int(0.30 * len(X)), is_track_b=True)
    r.pop("trace", None)
    return {"task_id": task_id, "model_id": mid, "seed": seed, **r}


if __name__ == "__main__":
    jobs = [(t, s, m) for t in TASKS for s in range(101, 131) for m in MODELS]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(run_one, jobs, chunksize=2)))
    df.to_csv(os.path.join(HERE, "BENCH01_CONTROLS_RESULTS.csv"), index=False)
    print(df.status.value_counts().to_string(), f"{time.time()-t0:.0f}s")
