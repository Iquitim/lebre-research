#!/usr/bin/env python3
"""
dev_eval_v04.py — DEV ablation of LEBRE v0.4 variants vs v0.3.2.
  internal: I1..I14, DEV seeds 3301..3310 (same seeds used for v0.3 development)
  external: the 25 BENCH-02 tasks (declared DEV here: BENCH-02 results are already known)
Usage: python dev_eval_v04.py <tag> [internal|external|both]
"""
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V03 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01")
B02 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02")
for p in (ROOT, HERE, V03, B02):
    sys.path.insert(0, p)

from lebre_v04 import LebreV04  # noqa: E402
from lebre_v032 import LebreV032  # noqa: E402
from lebre_v041 import LebreV041  # noqa: E402

VARIANTS = {
    "V032": None,
    "V04_ALL": {},
    "V041": "v041",
    "V04_withC1_anchor": {"anchor": True},
    "V04_withC3_prune": {"prune_base": True},
    "V04_ipalpha_m05": {"ip_alpha": -0.5},
    "V04_ipalpha_m1": {"ip_alpha": -1.0},
    "V04_noC1_anchor": {"anchor": False},
    "V04_noC2_ipnlms": {"ipnlms": False},
    "V04_noC3_prune": {"prune_base": False},
    "V04_noC4_mature": {"mature": False},
    "V04_noC5_clip": {"clip": False},
    "V04_onlyC1": {"ipnlms": False, "prune_base": False, "mature": False, "clip": False},
    "V04_onlyC2": {"anchor": False, "prune_base": False, "mature": False, "clip": False},
    "V04_onlyC3C4": {"anchor": False, "ipnlms": False, "clip": False},
}


def make(variant, d):
    kw = VARIANTS[variant]
    if kw == "v041":
        return LebreV041(d=d)
    return LebreV032(d=d) if kw is None else LebreV04(d=d, **kw)


def fp_total(m):
    return sum(m.fp.values())


# ------------------------------------------------------------------ internal
def internal_one(args):
    from scratch.bench_v02_integration import generate_v02_stream
    from run_dev_eval import GT, SWITCH_TASKS, struct_score
    task, seed, variant = args
    X, y, _ = generate_v02_stream(task, seed=seed, total_steps=6000)
    m = make(variant, 5)
    checks = {c[0]: c for c in GT.get(task, [])}
    err, fps, snaps = np.empty(6000), np.empty(6000), []
    for t in range(6000):
        b = fp_total(m); err[t] = y[t] - m.step(X[t], float(y[t])); fps[t] = fp_total(m) - b
        if t in checks:
            lags = {(a["key"][1], a["key"][2]) for a in m.active if a["key"][0] == "lag" and a["key"][2] >= 1}
            lat = any(a["key"][0] == "res" for a in m.active)
            extra_anchor = any(a["key"][0] == "anc" for a in m.active) and task != "I10_Redundant_Temporal_Structure"
            ex = struct_score(lags, lat, checks[t][1], checks[t][2])[0] and not extra_anchor
            snaps.append(ex)
    sw = np.nan
    if task in SWITCH_TASKS:
        roll = np.convolve(err[3000:] ** 2, np.ones(100) / 100, mode="valid")
        idx = np.where(roll <= 0.15 * np.var(y[3000:]))[0]
        sw = float(idx[0] + 100) if len(idx) else 3000.0
    out = {"set": "internal", "task_id": task, "seed": seed, "variant": variant,
           "nmse": float(np.mean(err ** 2) / np.var(y)), "fp": float(fps.mean()), "switch": sw,
           "struct_checks": len(snaps), "struct_exact": int(sum(snaps))}
    if hasattr(m, "cover_n") and m.cover_n:
        out["coverage"] = m.cover_hits / m.cover_n
    return out


# ------------------------------------------------------------------ external (BENCH-02 as DEV)
def external_one(args):
    import bench02 as B
    task, seed, variant = args
    X, y, split = B.load(task, seed)
    D = X.shape[1]
    test_start = split if split is not None else int(0.30 * len(X))

    class Step:
        def __init__(s):
            s.m = make(variant, D)

        def step(s, x, yy):
            b = fp_total(s.m); p = s.m.step(np.asarray(x, float), float(yy)); return p, fp_total(s.m) - b

        def get_memory_bytes(s):
            return s.m.memory_bytes()

        def get_active_params(s):
            return -1
    st = Step()
    r = B.R.run_full_stream(st, X, y, test_start, is_track_b=True)
    r.pop("trace", None)
    out = {"set": "external", "track": B.TASKS[task][0], "task_id": task, "seed": seed, "variant": variant,
           "nmse": r["nmse"], "mse": r["mse"], "fp": r["mean_flops"], "status": r["status"],
           "mem": r["memory_bytes"]}
    if hasattr(st.m, "cover_n") and st.m.cover_n:
        out["coverage"] = st.m.cover_hits / st.m.cover_n
    return out


def main():
    tag = sys.argv[1]
    which = sys.argv[2] if len(sys.argv) > 2 else "both"
    variants = sys.argv[3].split(",") if len(sys.argv) > 3 else list(VARIANTS)
    jobs_i, jobs_e = [], []
    if which in ("internal", "both"):
        from scratch.bench_v02_integration import BENCHMARK_TASKS
        jobs_i = [(t, s, v) for s in range(3301, 3311) for t in BENCHMARK_TASKS for v in variants]
    if which in ("external", "both"):
        import bench02 as B
        for t, (track, syn) in B.TASKS.items():
            seeds = (B.SYN_B if t.startswith("B_") else B.SYN_D) if syn else B.REAL_SEEDS[:1]
            for s in seeds[:5]:
                for v in variants:
                    jobs_e.append((t, s, v))
    t0 = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        rows += list(ex.map(internal_one, jobs_i, chunksize=4))
        rows += list(ex.map(external_one, jobs_e, chunksize=1))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, f"DEV_{tag}.csv"), index=False)
    print(f"{len(df)} runs in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
