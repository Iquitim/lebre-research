#!/usr/bin/env python3
"""
verify_v04_observability.py — T9 (explanation faithfulness) and T10 (interval coverage) for LEBRE v0.4.
Seeds 5231..5330 (unused). Coverage target 0.90.
"""
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
from lebre_v042 import LebreV042 as LebreV04  # noqa: E402
from scratch.bench_v02_integration import generate_v02_stream, BENCHMARK_TASKS  # noqa: E402

W = np.array([0.8, -0.6, 0.4, -0.3, 0.2])


def stream(kind, seed, T=6000):
    rng = np.random.RandomState(seed)
    X = rng.normal(size=(T, 5))
    if kind == "gauss":
        eps = 0.4 * rng.normal(size=T)
    elif kind == "student_t3":
        eps = 0.4 * rng.standard_t(3, size=T) / math.sqrt(3.0)
    elif kind == "hetero":
        eps = 0.4 * rng.normal(size=T) * np.where((np.arange(T) // 500) % 2 == 0, 1.0, 3.0)
    else:  # regime: coefficients flip at T/2 and a delay appears
        eps = 0.4 * rng.normal(size=T)
    y = X @ W + eps
    if kind == "regime":
        y[T // 2:] = X[T // 2:] @ (-W) + eps[T // 2:]
        y[T // 2 + 6:] += 0.8 * X[T // 2:-6, 1]
    y[6:] += 0.85 * X[:-6, 1] if kind != "regime" else 0.0
    return X, y


def run(args):
    kind, seed = args
    if kind.startswith("I"):
        X, y, _ = generate_v02_stream(kind, seed=seed)
    else:
        X, y = stream(kind, seed)
    m = LebreV04(d=5)
    max_gap, miss, n, widths = 0.0, 0, 0, []
    for t in range(len(y)):
        yh = m.step(X[t], float(y[t]))
        y_hat, parts = m.explain_prediction()
        max_gap = max(max_gap, abs(y_hat - sum(c for _, c in parts)), abs(y_hat - yh))
    return {"kind": kind, "seed": seed, "T9_max_faithfulness_gap": max_gap,
            "T10_coverage": m.cover_hits / m.cover_n, "target": 0.9, "n_parts_final": len(parts)}


if __name__ == "__main__":
    jobs = [(k, s) for k in ("gauss", "student_t3", "hetero", "regime") for s in range(5231, 5261)]
    jobs += [(t, s) for t in BENCHMARK_TASKS for s in range(5261, 5271)]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(run, jobs, chunksize=2)))
    df.to_csv(os.path.join(HERE, "OBSERVABILITY_TESTS_v042.csv"), index=False)
    g = df.assign(group=df.kind.where(~df.kind.str.startswith("I"), "I1-I14"))
    print(g.groupby("group").agg(n=("seed", "size"), faith_gap_max=("T9_max_faithfulness_gap", "max"),
                                 cov_mean=("T10_coverage", "mean"), cov_min=("T10_coverage", "min"),
                                 cov_max=("T10_coverage", "max")).to_string())
