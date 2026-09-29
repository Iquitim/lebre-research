#!/usr/bin/env python3
"""
run_bench01_external.py — one-shot external evaluation of the FROZEN LEBRE v0.3 (iter4) on BENCH-01.

Rules (fixed before execution):
  * lebre_v03.py is frozen (SHA-256 in FREEZE_ITER4_SHA256.txt); verified at start-up.
  * No calibration: default parameters for every task (baselines had per-task grid calibration).
  * Only d is set to the task's input dimension. L = 32 as inherited from LEBRE v0.2.
  * Harness function run_full_stream (experiments/bench01/runner.py) is reused unchanged:
    same scaler, same 30 evaluation seeds, same test split (t >= 0.30 T), same NMSE definition.
  * Results are written to this stage directory only; BENCH-01B artifacts are not modified.
"""
import hashlib
import os
import sys
import json
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
os.chdir(ROOT)  # dataset loaders use repository-relative paths

from experiments.bench01.streams import get_stream  # noqa: E402
from experiments.bench01.runner import run_full_stream, TASKS  # noqa: E402
from lebre_v03 import LebreV03  # noqa: E402

EVAL_SEEDS = list(range(101, 131))


class LebreV03Bench:
    def __init__(self, d):
        self.m = LebreV03(d=d)
        self.d = d

    def step(self, x, y):
        before = sum(self.m.fp.values())
        pred = self.m.step(np.asarray(x, dtype=float), float(y))
        return pred, sum(self.m.fp.values()) - before

    def get_memory_bytes(self):
        return self.m.memory_bytes()

    def get_active_params(self):
        return self.d + 1 + len(self.m.active)


def run_one(args):
    task_id, seed = args
    X, y = get_stream(task_id, seed=seed)
    res = run_full_stream(LebreV03Bench(X.shape[1]), X, y, int(0.30 * len(X)), is_track_b=True)
    res.pop("trace", None)
    return {"task_id": task_id, "model_id": "LEBRE_V03_FROZEN_ITER4", "seed": seed, **res}


def main():
    want = open(os.path.join(HERE, "FREEZE_ITER4_SHA256.txt")).read().split()[0]
    have = hashlib.sha256(open(os.path.join(HERE, "lebre_v03.py"), "rb").read()).hexdigest()
    assert want == have, "lebre_v03.py changed after freeze"
    jobs = [(t, s) for t in TASKS for s in EVAL_SEEDS]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        rows = list(ex.map(run_one, jobs, chunksize=2))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "BENCH01_LEBRE_V03_RESULTS.csv"), index=False)
    print(df.groupby("task_id")[["nmse", "mean_flops", "memory_bytes"]].mean().round(4).to_string())
    print(df.status.value_counts().to_string())
    print(f"{len(df)} runs in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
