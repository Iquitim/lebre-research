#!/usr/bin/env python3
"""bench04.py — PREREG_BENCH04.md, online models (LEBRE v0.4, v0.3.2, controls, classic filters, BENCH-01B, River, new online)."""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
B02 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02")
V04 = os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01")
D04 = os.path.join(ROOT, "data", "external_bench04")
for p in (B02, V04, D04, HERE):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402  (sets cwd to ROOT and imports the harness)
from lebre_v042 import LebreV042  # noqa: E402
from load04 import TASKS, load  # noqa: E402
from newmodels import GRIDS, NEW_ONLINE, make_new  # noqa: E402

SEEDS = [7611, 7612, 7613]
BR = [t for t in TASKS if t.startswith("BR")]


class LebreV04Step(B.Step):
    """LEBRE v0.4 (lebre_v042.py, frozen) + record of the 90 % interval half-width used at each prediction."""
    def __init__(self, d, test_start):
        self.m = LebreV042(d=d); self.t = 0; self.ts = test_start; self.w = []; self.hit = 0

    def step(self, x, y):
        q = self.m.interval()
        b = sum(self.m.fp.values()); p = self.m.step(np.asarray(x, float), float(y))
        if self.t >= self.ts and np.isfinite(q):
            self.w.append(q); self.hit += int(abs(float(y) - p) <= q)
        self.t += 1
        return p, sum(self.m.fp.values()) - b

    def get_memory_bytes(self):
        return self.m.memory_bytes()


def season(task):
    return load(task)[4]


def models_for(task, T):
    ms = ["LEBRE_V042", "LEBRE_V032", "CTRL_PERSISTENCE", "CTRL_ARX_NLMS", "IPNLMS", "RIVER_SGD_LINREG", "RIVER_HATR"]
    if season(task):
        ms.append("CTRL_SEASONAL_NAIVE")
    if T <= 25000:
        ms.append("RIVER_ARF")
    return ms + B.BENCH_MODELS + NEW_ONLINE + (["LEBRE_V042_SL", "IPNLMS_SL"] if season(task) else [])


def make(model_id, D, cfg, seed, task, test_start):
    if model_id in ("LEBRE_V042", "LEBRE_V042_SL"):
        return LebreV04Step(D, test_start), True
    if model_id == "IPNLMS_SL":
        return B.Ipnlms(D, mu=cfg.get("mu", 0.5)), True
    if model_id == "LEBRE_V032":
        return B.LebreStep(D), True
    if model_id == "CTRL_SEASONAL_NAIVE":
        return B.SeasonalNaive(D, season(task)), True
    if model_id in NEW_ONLINE:
        return make_new(model_id, D, cfg, seed, season(task)), True
    return B.make(model_id, D, cfg, seed, task)


def all_grids():
    g = B.grids(); g.update(GRIDS)
    return g


def calib_one(args):
    task, model_id, idx, cfg = args
    X, y, _, _, s_, _ = load(task)
    n = min(int(0.15 * len(X)), 5000); D = X.shape[1]
    mses = []
    for s in B.CALIB_SEEDS:
        sc = B.CausalStandardScaler(d=D)
        if model_id == "IPNLMS":
            m, step = B.Ipnlms(D, mu=cfg["mu"]), True
        elif model_id in GRIDS:
            m, step = make_new(model_id, D, cfg, s, s_), True
        else:
            m, step = B.R.instantiate_model(model_id, D, cfg, seed=s), False
        errs, bad = [], False
        for t in range(n):
            xn = sc.transform(X[t])
            try:
                if step:
                    p, _ = m.step(xn, y[t])
                else:
                    p = m.predict(xn); m.update(xn, y[t])
                sc.update(X[t])
                if not np.isfinite(p) or abs(p) > 1e8:
                    bad = True; break
                errs.append(float((y[t] - p) ** 2))
            except Exception:
                bad = True; break
        mses.append(float("inf") if bad or not errs else float(np.mean(errs)))
    return {"task_id": task, "model_id": model_id, "config_id": idx, "config_params": json.dumps(cfg),
            "mean_calibration_mse": float(np.mean(mses))}


def eval_one(args):
    task, model_id, seed, cfg = args
    X, y, split, _, s_, j = load(task)
    if model_id.endswith("_SL"):                      # secondary arm: environment adds the seasonal lag y[t-s]
        X = np.column_stack([X, np.r_[np.full(s_, X[0, j]), y[:-s_]]])
    D = X.shape[1]
    test_start = split if split is not None else int(0.30 * len(X))
    m, step = make(model_id, D, cfg, seed, task, test_start)
    t0 = time.time()
    r = B.R.run_full_stream(m, X, y, test_start, is_track_b=step)
    r.pop("trace", None)
    out = {"group": "BR" if task in BR else "INTL", "task_id": task, "model_id": model_id, "seed": seed,
           "config": json.dumps(cfg), "T": len(X), "D": D, **r, "wall": time.time() - t0,
           "ms_per_step": 1000.0 * (time.time() - t0) / len(X)}
    if model_id in ("LEBRE_V042", "LEBRE_V042_SL"):
        sd = float(np.std(y[test_start:]))
        out["coverage"] = m.hit / max(len(m.w), 1)
        out["coverage_internal"] = m.m.cover_hits / max(m.m.cover_n, 1)
        out["interval_width_rel"] = 2.0 * float(np.mean(m.w)) / sd if m.w else float("nan")
        out["n_active_final"] = len(m.m.active)
        out["n_struct_final"] = sum(1 for a in m.m.active if not (a["key"][0] == "lag" and a["key"][2] == 0))
        out["n_events"] = len(m.m.events)
    return out


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_BENCH04.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_BENCH04_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(V04, "lebre_v042.py"), "rb").read()).hexdigest() == \
        open(os.path.join(V04, "FREEZE_V042_SHA256.txt")).read().split()[0].lstrip("*")
    t0 = time.time()
    sp = all_grids()
    cjobs = [(t, m, i, c) for t in TASKS for m, g in sp.items() for i, c in enumerate(g)
             if not (m == "HOLT_WINTERS" and season(t) is None and c["gamma"] != 0.05)]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        cdf = pd.DataFrame(list(ex.map(calib_one, cjobs, chunksize=1)))
    cdf.to_csv(os.path.join(HERE, "BENCH04_CALIBRATION_LOG.csv"), index=False)
    best = {(t, m): json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])
            for (t, m), g in cdf.groupby(["task_id", "model_id"])}
    print(f"calibration: {len(cdf)} rows, {time.time() - t0:.0f}s", flush=True)
    jobs, size = [], {}
    for t in TASKS:
        T = len(load(t)[1]); size[t] = T
        for s in SEEDS:
            for m in models_for(t, T):
                jobs.append((t, m, s, best.get((t, m.replace("_SL", "")), {})))
    heavy = {"RIVER_ARF": 50, "B5_ONLINE_ESN": 20, "S4_ACESN": 30, "C3_RLS": 10, "B3_MUSE_RNN": 5, "QKLMS": 8,
             "RIVER_AMRULES": 5}
    jobs.sort(key=lambda j: -size[j[0]] * heavy.get(j[1], 1))
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(eval_one, jobs, chunksize=1)))
    df.to_csv(os.path.join(HERE, "BENCH04_RESULTS.csv"), index=False)
    print(df.groupby("model_id").status.value_counts().unstack(fill_value=0).to_string())
    print(f"{len(df)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
