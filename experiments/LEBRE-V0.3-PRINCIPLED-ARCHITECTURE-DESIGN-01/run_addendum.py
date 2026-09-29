#!/usr/bin/env python3
"""run_addendum.py — Parts IV, V, VI of PREREG_ADDENDUM_V032.md (hash in PREREG_ADDENDUM_SHA256.txt)."""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.argv = sys.argv[:1]
import run_external_review as E  # noqa: E402  (sets cwd to repository root)
import run_internal_confirmation as I  # noqa: E402
from lebre_v032 import LebreV032  # noqa: E402

PART4_SEEDS = list(range(161, 191))
PART5_SEEDS = list(range(2146, 2176))
OURS = ["LEBRE_V03", "LEBRE_V031", "LEBRE_V032", "CTRL_ARX_NLMS", "CTRL_PERSISTENCE"]


def make(model_id, D, cfg, seed):
    if model_id == "LEBRE_V032":
        return E.StepAdapter(LebreV032(d=D)), True
    return E.make(model_id, D, cfg, seed)


def eval_one(args):
    part, task_id, model_id, seed, cfg = args
    X, y = E.stream(task_id, seed)
    if part == "IV":
        X = X[:, np.random.RandomState(seed + 1_000_000).permutation(X.shape[1])]
    m, is_step = make(model_id, X.shape[1], cfg, seed)
    r = E.R.run_full_stream(m, X, y, int(0.30 * len(X)), is_track_b=is_step)
    r.pop("trace", None)
    return {"part": part, "task_id": task_id, "model_id": model_id, "seed": seed, **r}


def internal_one(args):
    task_id, seed, arm = args
    if arm != "V032":
        return I.run_one(args)
    # same loop as run_internal_confirmation.run_one, with the V032 model
    X, y, _ = I.generate_v02_stream(task_id, seed=seed, total_steps=6000)
    m = LebreV032()
    checks = {c[0]: c for c in I.GT.get(task_id, [])}
    err, fps, snaps = np.empty(6000), np.empty(6000), []
    for t in range(6000):
        b = sum(m.fp.values()); err[t] = y[t] - m.step(X[t], float(y[t])); fps[t] = sum(m.fp.values()) - b
        if t in checks:
            lags, lat = I.snapshot_v03(m)
            snaps.append(I.struct_score(lags, lat, checks[t][1], checks[t][2])[0])
    sw = np.nan
    if task_id in I.SWITCH_TASKS:
        roll = np.convolve(err[3000:] ** 2, np.ones(100) / 100, mode="valid")
        idx = np.where(roll <= 0.15 * np.var(y[3000:]))[0]
        sw = float(idx[0] + 100) if len(idx) else 3000.0
    react = np.nan
    if task_id == "I7_Quiescent_Continuous_State":
        roll = np.convolve(err[4000:4500] ** 2, np.ones(50) / 50, mode="valid")
        idx = np.where(roll <= 0.20 * np.var(y[4000:]))[0]
        react = float(idx[0] + 50) if len(idx) else 500.0
    return {"task_id": task_id, "seed": seed, "arm": arm, "nmse": float(np.mean(err ** 2) / np.var(y)),
            "fp": float(fps.mean()), "fp_p99": float(np.percentile(fps, 99)), "switch_latency": sw,
            "i7_reactivation": react, "struct_checks": len(snaps), "struct_exact": int(sum(snaps))}


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_ADDENDUM_V032.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_ADDENDUM_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(HERE, "lebre_v032.py"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "FREEZE_V032_SHA256.txt")).read().split()[0].lstrip("*")
    t0 = time.time()
    cal = pd.read_csv(os.path.join(E.ROOT, "experiments", "BENCH-01B", "BENCH_01B_CALIBRATION_LOG.csv"))
    best = {(t, m): json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])
            for (t, m), g in cal.groupby(["task_id", "model_id"])}
    c3 = pd.read_csv(os.path.join(HERE, "EXTERNAL_PART3_CALIBRATION_LOG.csv"))
    for (t, m), g in c3.groupby(["task_id", "model_id"]):
        best[(t, m)] = json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])

    jobs = [("VI", t, "LEBRE_V032", s, {}) for t in E.PART3_TASKS for s in E.PART3_SEEDS]
    jobs += [("IV", t, m, s, best.get((t, m), {})) for t in E.PART2_TASKS for s in PART4_SEEDS
             for m in E.BASELINES + OURS]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(eval_one, jobs, chunksize=1)))
    df.to_csv(os.path.join(HERE, "ADDENDUM_EXTERNAL_RESULTS.csv"), index=False)
    print(f"external: {len(df)} runs, {time.time() - t0:.0f}s", flush=True)

    ijobs = [(t, s, a) for s in PART5_SEEDS for t in I.BENCHMARK_TASKS for a in ["V02_A0", "V031", "V032", "CTRL_ARX"]]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        idf = pd.DataFrame(list(ex.map(internal_one, ijobs, chunksize=4)))
    idf.to_csv(os.path.join(HERE, "ADDENDUM_INTERNAL_RESULTS.csv"), index=False)
    print(f"internal: {len(idf)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
