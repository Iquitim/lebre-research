#!/usr/bin/env python3
"""
run_dev_eval.py — EXPLORATORY DEV comparison: LEBRE v0.2 references vs LEBRE v0.3 candidate.

Status: DEV (non-confirmatory). Seeds 3301..3310 (verified unused by repository scan).
Parameters of v0.3 may still change after this evaluation; any confirmatory claim needs
a fresh preregistered cohort.

Metric definitions (NMSE, switching latency, I7 reactivation) are copied verbatim from
LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01/run_k2_arb10_composition.py.
"""

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
sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01"))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream  # noqa: E402
from run_k2_arb10_composition import CompositionSparseModel  # noqa: E402
MODEL = os.environ.get("LEBRE_MODEL", "v03")
if MODEL == "v031":
    from lebre_v031 import LebreV031 as LebreV03  # noqa: E402
else:
    from lebre_v03 import LebreV03  # noqa: E402

DEV_SEEDS = list(range(3301, 3311))
ARMS = ["V02_A0_K1_KARB5", "V02_B1_K2_KARB5", "V03_CANDIDATE"] if MODEL == "v03" else ["V03_CANDIDATE"]
SWITCH_TASKS = ["I11_Regime_Switch_Delay_To_Latent", "I12_Regime_Switch_Latent_To_Delay",
                "I13_Regime_Switch_Hybrid_To_Memoryless", "I14_Intermittent_Hybrid"]

# Ground-truth structure at regime ends: (checkpoint step, true lags, latent present)
GT = {
    "I1_Memoryless_Linear": [(5999, set(), False)],
    "I2_Static_Nonlinear_Negative_Control": [(5999, set(), False)],
    "I3_Single_Exact_Delay": [(5999, {(1, 6)}, False)],
    "I4_Multi_Sparse_Delay": [(5999, {(0, 3), (2, 14), (4, 27)}, False)],
    "I5_Moving_Delay_Support": [(2999, {(1, 4)}, False), (5999, {(3, 18)}, False)],
    "I6_Continuous_Latent_State": [(5999, set(), True)],
    "I7_Quiescent_Continuous_State": [(1999, set(), True), (5999, set(), True)],
    "I8_Quiescent_Discrete_Delay": [(1999, {(1, 6)}, False), (5999, {(1, 6)}, False)],
    "I9_Hybrid_Delay_Plus_Latent_State": [(5999, {(3, 12)}, True)],
    "I11_Regime_Switch_Delay_To_Latent": [(2999, {(1, 8)}, False), (5999, set(), True)],
    "I12_Regime_Switch_Latent_To_Delay": [(2999, set(), True), (5999, {(2, 10)}, False)],
    "I13_Regime_Switch_Hybrid_To_Memoryless": [(2999, {(3, 12)}, True), (5999, set(), False)],
    "I14_Intermittent_Hybrid": [(1499, {(0, 5)}, False), (2999, set(), True),
                                (4499, {(0, 5)}, True), (5999, set(), False)],
}
# In innovations form, a latent state driven by input x0 implies an x0 lag-1 atom
# (coefficient a*c*b; see design note). It is structurally consistent, not spurious.
LATENT_IMPLIED = {(0, 1)}


def snapshot_v02(m):
    return {(t["i"], t["k"]) for t in m.active_taps}, m.active_rec is not None


def snapshot_v03(m):
    lags = {(a["key"][1], a["key"][2]) for a in m.active if a["key"][0] == "lag"}
    lat = any(a["key"][0] == "res" for a in m.active)
    return lags, lat


def struct_score(lags, lat, gt_lags, gt_lat):
    extra = lags - gt_lags - (LATENT_IMPLIED if gt_lat else set())
    missing = gt_lags - lags
    exact = (not extra) and (not missing) and (lat == gt_lat)
    return exact, len(extra), len(missing), lat == gt_lat


def run_one(args):
    task_id, seed, arm = args
    X, y, _ = generate_v02_stream(task_id, seed=seed, total_steps=6000)
    if arm.startswith("V02"):
        K = 1 if "K1" in arm else 2
        m = CompositionSparseModel(task_id=task_id, H_capacity=32, B_batch=4,
                                   K_rec_forward=K, K_rec_learn=10, K_arbitration=5)
    else:
        m = LebreV03()
    checks = {c[0]: c for c in GT.get(task_id, [])}
    errors, fps, snaps = np.empty(6000), [], []
    for t in range(6000):
        if arm.startswith("V02"):
            out = m.step(X[t], float(y[t]))
            errors[t] = out["y_true"] - out["y_hat"]
            fps.append(out["total_fp"])
        else:
            before = sum(m.fp.values())
            errors[t] = y[t] - m.step(X[t], float(y[t]))
            fps.append(sum(m.fp.values()) - before)
        if t in checks:
            lags, lat = snapshot_v02(m) if arm.startswith("V02") else snapshot_v03(m)
            _, gl, gla = checks[t]
            ex, n_extra, n_miss, lat_ok = struct_score(lags, lat, gl, gla)
            snaps.append({"t": t, "exact": ex, "extra": n_extra, "missing": n_miss, "latent_ok": lat_ok,
                          "lags": sorted(lags), "latent": lat})

    nmse = float(np.mean(errors ** 2) / np.var(y))
    switch_latency = np.nan
    if task_id in SWITCH_TASKS:
        post_err = errors[3000:] ** 2
        win = 100
        roll = np.convolve(post_err, np.ones(win) / win, mode="valid")
        target = 0.15 * np.var(y[3000:])
        idx = np.where(roll <= target)[0]
        switch_latency = float(idx[0] + win) if len(idx) > 0 else 3000.0
    react = np.nan
    if task_id == "I7_Quiescent_Continuous_State":
        post = errors[4000:4500] ** 2
        roll = np.convolve(post, np.ones(50) / 50, mode="valid")
        idx = np.where(roll <= 0.20 * np.var(y[4000:]))[0]
        react = float(idx[0] + 50) if len(idx) > 0 else 500.0

    row = {"task_id": task_id, "seed": seed, "arm": arm, "nmse": nmse,
           "total_fp_mean": float(np.mean(fps)), "total_fp_p99": float(np.percentile(fps, 99)),
           "switch_latency": switch_latency, "i7_reactivation": react,
           "struct_checks": len(snaps), "struct_exact": sum(s["exact"] for s in snaps),
           "struct_extra": sum(s["extra"] for s in snaps), "struct_missing": sum(s["missing"] for s in snaps),
           "struct_latent_ok": sum(s["latent_ok"] for s in snaps),
           "snapshots": json.dumps(snaps)}
    if arm == "V03_CANDIDATE":
        for k, v in m.fp.items():
            row[f"fp_{k}"] = v / 6000.0
        row["n_events"] = len(m.events)
        row["promotions"] = sum(1 for e in m.events if e[1] == "PROVISIONAL->ACTIVE")
        row["evictions"] = sum(1 for e in m.events if e[1].startswith("ACTIVE->EVICTED"))
        row["memory_bytes_final"] = m.memory_bytes()
        row["events"] = json.dumps([(int(a), b, c, round(float(d), 2)) for a, b, c, d in m.events])
    else:
        row["promotions"] = m.promotions_lag + m.promotions_rec
        row["evictions"] = m.evictions_lag + m.evictions_rec
    return row


def paired(df, a, b):
    s = df.groupby(["seed", "arm"]).nmse.mean().unstack()
    d = s[a] - s[b]
    n = len(d)
    from scipy import stats
    se = d.std(ddof=1) / np.sqrt(n)
    return {"contrast": f"{a} - {b}", "N_seeds": n, "mean": d.mean(), "sd": d.std(ddof=1),
            "two_sided_95_lo": d.mean() - stats.t.ppf(.975, n - 1) * se,
            "two_sided_95_hi": d.mean() + stats.t.ppf(.975, n - 1) * se,
            "wins_a": int((d < 0).sum()), "losses_a": int((d > 0).sum())}


def main():
    jobs = [(t, s, a) for s in DEV_SEEDS for t in BENCHMARK_TASKS for a in ARMS]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        rows = list(ex.map(run_one, jobs, chunksize=4))
    df = pd.DataFrame(rows)
    tag = os.environ.get("DEV_TAG", "dev")
    df.to_csv(os.path.join(HERE, f"DEV_RESULTS_{tag}.csv"), index=False)

    task = df.groupby(["task_id", "arm"]).agg(nmse=("nmse", "mean"), fp=("total_fp_mean", "mean"),
                                              switch=("switch_latency", "mean"),
                                              struct_exact=("struct_exact", "sum"),
                                              struct_checks=("struct_checks", "sum")).unstack("arm")
    overall = df.groupby("arm").agg(nmse=("nmse", "mean"), fp=("total_fp_mean", "mean"),
                                    fp_p99=("total_fp_p99", "mean"),
                                    struct_exact=("struct_exact", "sum"), struct_checks=("struct_checks", "sum"),
                                    extra=("struct_extra", "sum"), missing=("struct_missing", "sum"))
    if MODEL != "v03":
        print(df.groupby("arm").agg(nmse=("nmse", "mean"), fp=("total_fp_mean", "mean"), sx=("struct_exact", "sum")))
        df.to_csv(os.path.join(HERE, f"DEV_RESULTS_{tag}.csv"), index=False)
        return
    contrasts = pd.DataFrame([paired(df, "V03_CANDIDATE", "V02_A0_K1_KARB5"),
                              paired(df, "V03_CANDIDATE", "V02_B1_K2_KARB5")])
    pd.set_option("display.width", 250)
    print(overall.to_string())
    print(contrasts.to_string(index=False))
    print(task.round(4).to_string())
    task.to_csv(os.path.join(HERE, f"DEV_TASK_SUMMARY_{tag}.csv"))
    contrasts.to_csv(os.path.join(HERE, f"DEV_CONTRASTS_{tag}.csv"), index=False)
    overall.to_csv(os.path.join(HERE, f"DEV_OVERALL_{tag}.csv"))
    print(f"{len(df)} runs in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
