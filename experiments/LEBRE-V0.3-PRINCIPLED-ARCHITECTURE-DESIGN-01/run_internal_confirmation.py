#!/usr/bin/env python3
"""
run_internal_confirmation.py — Part I of PREREG_V03_REVIEW_BENCHMARKS.md (hash in PREREG_SHA256.txt).
Seeds 2116..2145, tasks I1..I14, arms V02_A0, V02_B1, V03, V031, CTRL_ARX.
"""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01"))

from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream  # noqa: E402
from run_k2_arb10_composition import CompositionSparseModel  # noqa: E402
from lebre_v03 import LebreV03  # noqa: E402
from lebre_v031 import LebreV031  # noqa: E402
from run_dev_eval import GT, SWITCH_TASKS, snapshot_v02, snapshot_v03, struct_score  # noqa: E402

SEEDS = list(range(2116, 2146))
ARMS = ["V02_A0", "V02_B1", "V03", "V031", "CTRL_ARX"]


class ArxNlms:
    def __init__(self, d=5, mu=0.1):
        self.w = np.zeros(d + 2); self.y_prev = 0.0; self.mu = mu

    def step(self, x, y):
        phi = np.concatenate([x, [1.0, self.y_prev]])
        n = len(phi)
        pred = float(self.w @ phi)
        e = float(y) - pred
        self.w += self.mu * e / (1e-6 + float(phi @ phi)) * phi
        self.y_prev = float(y)
        return pred, float((2 * n - 1) + 1 + (2 * n - 1) + 3 + 2 * n)


def run_one(args):
    task_id, seed, arm = args
    X, y, _ = generate_v02_stream(task_id, seed=seed, total_steps=6000)
    if arm.startswith("V02"):
        m = CompositionSparseModel(task_id=task_id, H_capacity=32, B_batch=4,
                                   K_rec_forward=1 if arm == "V02_A0" else 2, K_rec_learn=10, K_arbitration=5)
    elif arm == "V03":
        m = LebreV03()
    elif arm == "V031":
        m = LebreV031()
    else:
        m = ArxNlms()
    checks = {c[0]: c for c in GT.get(task_id, [])}
    err, fps, snaps = np.empty(6000), np.empty(6000), []
    for t in range(6000):
        if arm.startswith("V02"):
            o = m.step(X[t], float(y[t])); err[t] = o["y_true"] - o["y_hat"]; fps[t] = o["total_fp"]
        elif arm == "CTRL_ARX":
            p, f = m.step(X[t], float(y[t])); err[t] = y[t] - p; fps[t] = f
        else:
            b = sum(m.fp.values()); err[t] = y[t] - m.step(X[t], float(y[t])); fps[t] = sum(m.fp.values()) - b
        if t in checks and arm != "CTRL_ARX":
            lags, lat = snapshot_v02(m) if arm.startswith("V02") else snapshot_v03(m)
            ex, ne, nm, lok = struct_score(lags, lat, checks[t][1], checks[t][2])
            snaps.append(ex)
    sw = np.nan
    if task_id in SWITCH_TASKS:
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


def one_sided(d, alt):
    n = len(d); m = d.mean(); se = d.std(ddof=1) / np.sqrt(n); tq = stats.t.ppf(0.95, n - 1)
    t = m / se
    p = stats.t.cdf(t, n - 1) if alt == "less" else stats.t.sf(t, n - 1)
    return {"N": n, "mean": m, "sd": d.std(ddof=1), "se": se, "one_sided_upper": m + tq * se,
            "one_sided_lower": m - tq * se, "t": t, "p_one_sided": p,
            "wins": int((d < 0).sum()) if alt == "less" else int((d > 0).sum()),
            "losses": int((d > 0).sum()) if alt == "less" else int((d < 0).sum())}


def main():
    pre = open(os.path.join(HERE, "PREREG_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_V03_REVIEW_BENCHMARKS.md"), "rb").read()).hexdigest() == pre
    for f, h in (("lebre_v03.py", "FREEZE_ITER4_SHA256.txt"), ("lebre_v031.py", "FREEZE_V031_SHA256.txt")):
        assert hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest() == \
            open(os.path.join(HERE, h)).read().split()[0].lstrip("*"), f
    jobs = [(t, s, a) for s in SEEDS for t in BENCHMARK_TASKS for a in ARMS]
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(run_one, jobs, chunksize=4)))
    df.to_csv(os.path.join(HERE, "INTERNAL_CONFIRMATION_RESULTS.csv"), index=False)

    seed_nmse = df.groupby(["seed", "arm"]).nmse.mean().unstack()
    sub = df[df.task_id != "I10_Redundant_Temporal_Structure"]
    sx = sub.groupby(["seed", "arm"]).apply(lambda g: g.struct_exact.sum() / g.struct_checks.sum()).unstack()
    rows = []
    for name, d, alt in [("H1 V031-V02_A0 NMSE", seed_nmse.V031 - seed_nmse.V02_A0, "less"),
                         ("H3 V031-CTRL_ARX NMSE", seed_nmse.V031 - seed_nmse.CTRL_ARX, "less"),
                         ("H4 V031-V02_A0 struct_exact", sx.V031 - sx.V02_A0, "greater"),
                         ("S V03-V02_A0 NMSE", seed_nmse.V03 - seed_nmse.V02_A0, "less"),
                         ("S V03-CTRL_ARX NMSE", seed_nmse.V03 - seed_nmse.CTRL_ARX, "less"),
                         ("S V03-V02_A0 struct_exact", sx.V03 - sx.V02_A0, "greater"),
                         ("S V031-V03 NMSE", seed_nmse.V031 - seed_nmse.V03, "less"),
                         ("S V02_B1-V02_A0 NMSE", seed_nmse.V02_B1 - seed_nmse.V02_A0, "less")]:
        rows.append({"contrast": name, **one_sided(d, alt)})
    res = pd.DataFrame(rows)
    fam = res.iloc[:3].copy().sort_values("p_one_sided")
    k = len(fam)
    holm, running = [], 0.0
    for i, p in enumerate(fam.p_one_sided):
        running = max(running, min(1.0, (k - i) * p)); holm.append(running)
    fam["p_holm"] = holm
    res = res.merge(fam[["contrast", "p_holm"]], on="contrast", how="left")
    res.to_csv(os.path.join(HERE, "INTERNAL_CONFIRMATION_CONTRASTS.csv"), index=False)

    arm_sum = df.groupby("arm").agg(nmse=("nmse", "mean"), fp=("fp", "mean"), fp_p99=("fp_p99", "mean"))
    arm_sum["struct_exact_rate"] = sub.groupby("arm").struct_exact.sum() / sub.groupby("arm").struct_checks.sum()
    arm_sum.to_csv(os.path.join(HERE, "INTERNAL_CONFIRMATION_ARMS.csv"))
    task = df.pivot_table(index="task_id", columns="arm", values=["nmse", "fp", "switch_latency", "i7_reactivation"],
                          aggfunc="mean")
    task.to_csv(os.path.join(HERE, "INTERNAL_CONFIRMATION_TASKS.csv"))
    pd.set_option("display.width", 250)
    print(arm_sum.round(4).to_string())
    print(res.round(5).to_string(index=False))
    print(task["nmse"].round(4).to_string())
    print(task["switch_latency"].dropna(how="all").round(1).to_string())
    print(task["i7_reactivation"].dropna(how="all").round(1).to_string())
    print(f"{len(df)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
