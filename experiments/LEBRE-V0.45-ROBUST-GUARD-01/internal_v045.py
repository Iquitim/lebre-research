#!/usr/bin/env python3
"""internal_v045.py — Part 1 of PREREG_V045.md (copy of internal_v04.py with the V045 and V042 arms)."""
import hashlib
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V03 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01")
for p in (ROOT, HERE, os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"), V03, os.path.join(ROOT, "experiments", "LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01")):
    sys.path.insert(0, p)
from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream  # noqa: E402
from run_k2_arb10_composition import CompositionSparseModel  # noqa: E402
from run_dev_eval import GT, SWITCH_TASKS, struct_score  # noqa: E402
from lebre_v032 import LebreV032  # noqa: E402
from lebre_v04 import LebreV04  # noqa: E402
from lebre_v041 import LebreV041  # noqa: E402
from lebre_v042 import LebreV042  # noqa: E402
from lebre_v045 import LebreV045  # noqa: E402

SEEDS = list(range(2401, 2431))
TARGET = "V045"
ARMS = ["V02_A0", "V032", "V042", TARGET, "CTRL_ARX"]
OUT = "INTERNAL_V045"
CHANGES = {"I5_Moving_Delay_Support": [3000], "I11_Regime_Switch_Delay_To_Latent": [3000],
           "I12_Regime_Switch_Latent_To_Delay": [3000], "I13_Regime_Switch_Hybrid_To_Memoryless": [3000],
           "I14_Intermittent_Hybrid": [1500, 3000, 4500]}
STATIONARY = ["I1_Memoryless_Linear", "I3_Single_Exact_Delay", "I4_Multi_Sparse_Delay",
              "I6_Continuous_Latent_State", "I9_Hybrid_Delay_Plus_Latent_State"]


class Arx:
    def __init__(self):
        self.w = np.zeros(7); self.yp = 0.0

    def step(self, x, y):
        phi = np.concatenate([x, [1.0, self.yp]]); p = float(self.w @ phi); e = y - p
        self.w += 0.1 * e / (1e-6 + float(phi @ phi)) * phi; self.yp = y
        return p, 44.0


def run_one(args):
    task, seed, arm = args
    X, y, _ = generate_v02_stream(task, seed=seed, total_steps=6000)
    lebre = arm in ("V032", "V04", "V041", "V042", "V045")
    if arm == "V02_A0":
        m = CompositionSparseModel(task_id=task, H_capacity=32, B_batch=4, K_rec_forward=1, K_rec_learn=10, K_arbitration=5)
    elif arm == "V032":
        m = LebreV032(d=5)
    elif arm == "V04":
        m = LebreV04(d=5)
    elif arm == "V041":
        m = LebreV041(d=5)
    elif arm == "V042":
        m = LebreV042(d=5)
    elif arm == "V045":
        m = LebreV045(d=5)
    else:
        m = Arx()
    checks = {c[0]: c for c in GT.get(task, [])}
    err, fps, snaps, n_struct, faith = np.empty(6000), np.empty(6000), [], [], 0.0
    for t in range(6000):
        if arm == "V02_A0":
            o = m.step(X[t], float(y[t])); err[t] = o["y_true"] - o["y_hat"]; fps[t] = o["total_fp"]
        elif arm == "CTRL_ARX":
            p, f = m.step(X[t], float(y[t])); err[t] = y[t] - p; fps[t] = f
        else:
            b = sum(m.fp.values()); p = m.step(X[t], float(y[t])); err[t] = y[t] - p; fps[t] = sum(m.fp.values()) - b
            if arm in ("V04", "V041", "V042", "V045"):
                yh, parts = m.explain_prediction(); faith = max(faith, abs(yh - sum(c for _, c in parts)), abs(yh - p))
            if t % 50 == 0:
                n_struct.append(sum(1 for a in m.active if not (a["key"][0] == "lag" and a["key"][2] == 0)))
        if t in checks and arm != "CTRL_ARX":
            if arm == "V02_A0":
                lags, lat = {(tp["i"], tp["k"]) for tp in m.active_taps}, m.active_rec is not None
            else:
                lags = {(a["key"][1], a["key"][2]) for a in m.active if a["key"][0] == "lag" and a["key"][2] >= 1}
                lat = any(a["key"][0] == "res" for a in m.active)
            snaps.append(struct_score(lags, lat, checks[t][1], checks[t][2])[0])
    out = {"task_id": task, "seed": seed, "arm": arm, "nmse": float(np.mean(err ** 2) / np.var(y)),
           "fp": float(fps.mean()), "struct_checks": len(snaps), "struct_exact": int(sum(snaps))}
    if task in SWITCH_TASKS:
        roll = np.convolve(err[3000:] ** 2, np.ones(100) / 100, mode="valid")
        idx = np.where(roll <= 0.15 * np.var(y[3000:]))[0]
        out["switch_latency"] = float(idx[0] + 100) if len(idx) else 3000.0
    if task == "I7_Quiescent_Continuous_State":
        roll = np.convolve(err[4000:4500] ** 2, np.ones(50) / 50, mode="valid")
        idx = np.where(roll <= 0.20 * np.var(y[4000:]))[0]
        out["i7_reactivation"] = float(idx[0] + 50) if len(idx) else 500.0
    if lebre:
        ev = [e[0] for e in m.events]
        out["mean_struct_atoms"] = float(np.mean(n_struct))
        if task in STATIONARY:
            out["events_per_1000_stationary"] = 1000.0 * sum(1 for t in ev if t >= 2000) / 4000.0
        if task in CHANGES:
            delays = []
            for c in CHANGES[task]:
                after = [t - c for t in ev if t >= c]
                delays.append(min(after) if after else 3000)
            out["detection_delay"] = float(np.mean(delays))
        if arm in ("V04", "V041", "V042", "V045"):
            out["coverage"] = m.cover_hits / m.cover_n
            out["faithfulness_gap"] = faith
    return out


def one_sided(d, alt):
    n = len(d); m = d.mean(); se = d.std(ddof=1) / np.sqrt(n); tq = stats.t.ppf(0.95, n - 1)
    return {"N": n, "mean": m, "upper95": m + tq * se, "lower95": m - tq * se,
            "favourable": int((d < 0).sum() if alt == "less" else (d > 0).sum())}


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_V045.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_V045_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(HERE, "lebre_v045.py"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "FREEZE_V045_SHA256.txt")).read().split()[0].lstrip("*")
    t0 = time.time()
    jobs = [(t, s, a) for s in SEEDS for t in BENCHMARK_TASKS for a in ARMS]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(run_one, jobs, chunksize=4)))
    df.to_csv(os.path.join(HERE, OUT + "_RESULTS.csv"), index=False)
    sn = df.groupby(["seed", "arm"]).nmse.mean().unstack()
    sub = df[df.task_id != "I10_Redundant_Temporal_Structure"]
    sx = (sub.groupby(["seed", "arm"]).struct_exact.sum() / sub.groupby(["seed", "arm"]).struct_checks.sum()).unstack()
    res = {"G1 NI V04-V032 NMSE (upper<+0.010)": one_sided(sn[TARGET] - sn.V032, "less"),
           "G3 NI V04-V032 struct (lower>-0.02)": one_sided(sx[TARGET] - sx.V032, "greater"),
           "G4 V04-V02_A0 NMSE (upper<0)": one_sided(sn[TARGET] - sn.V02_A0, "less"),
           "info V04-CTRL_ARX NMSE": one_sided(sn[TARGET] - sn.CTRL_ARX, "less")}
    r = pd.DataFrame(res).T
    v = df[df.arm == TARGET]
    gates = {"G1": r.iloc[0].upper95 < 0.010, "G2": v.fp.mean() <= 100.0, "G3": r.iloc[1].lower95 > -0.02,
             "G4": r.iloc[2].upper95 < 0, "G5": 0.88 <= v.coverage.mean() <= 0.92, "G6": v.faithfulness_gap.max() <= 1e-9}
    arms = df.groupby("arm").agg(nmse=("nmse", "mean"), fp=("fp", "mean"))
    arms["struct"] = sub.groupby("arm").struct_exact.sum() / sub.groupby("arm").struct_checks.sum()
    obs = df[df.arm.isin(["V032", "V042", TARGET])].groupby("arm")[
        ["mean_struct_atoms", "events_per_1000_stationary", "detection_delay"]].mean()
    tasks = df.pivot_table(index="task_id", columns="arm", values=["nmse", "switch_latency", "i7_reactivation"], aggfunc="mean")
    r.to_csv(os.path.join(HERE, OUT + "_CONTRASTS.csv")); arms.to_csv(os.path.join(HERE, OUT + "_ARMS.csv"))
    obs.to_csv(os.path.join(HERE, OUT + "_OBSERVABILITY.csv")); tasks.to_csv(os.path.join(HERE, OUT + "_TASKS.csv"))
    pd.set_option("display.width", 220)
    print(arms.round(4).to_string()); print(r.round(5).to_string()); print(gates)
    print(f"coverage {v.coverage.mean():.4f} [{v.coverage.min():.3f},{v.coverage.max():.3f}], faith max {v.faithfulness_gap.max():.2e}")
    print(obs.round(3).to_string()); print(tasks.round(4).to_string())
    print(f"{len(df)} runs {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
