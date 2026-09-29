#!/usr/bin/env python3
"""bench03.py — Part 2 of PREREG_BENCH03.md (held-out external benchmark for the LEBRE v0.4 promotion)."""
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
D03 = os.path.join(ROOT, "data", "external_bench03")
for p in (B02, HERE, D03):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402  (sets cwd to ROOT and imports the harness)
from lebre_v04 import LebreV04  # noqa: E402
from tsf import read_tsf  # noqa: E402

SYN_B = list(range(7301, 7311))
SYN_D = list(range(7401, 7411))
REAL = list(range(7501, 7504))
MONASH = {"A_AusElectricity": ("australian_electricity_demand_dataset", 48),
          "A_Sunspot": ("sunspot_dataset_without_missing_values", None),
          "A_SaugeenRiver": ("saugeenday_dataset", None),
          "A_USBirths": ("us_births_dataset", 7),
          "A_Solar10min": ("solar_10_minutes_dataset", 144),
          "A_Pedestrian": ("pedestrian_counts_dataset", 24),
          "A_KDDCup2018": ("kdd_cup_2018_dataset_without_missing_values", 24)}
TASKS = {t: ("A", False) for t in MONASH}
TASKS.update({t: ("B", True) for t in ["B_FriedmanDrift_LEA", "B_FriedmanDrift_GRA", "B_FriedmanDrift_GSG",
                                        "B_Planes2D", "B_Mv"]})
TASKS.update({"C_F16": ("C", False), "C_ParWH": ("C", False)})
TASKS.update({f"D_SparseFIR_K{K}_{c}_SNR10": ("D", True) for K in (2, 6) for c in ("white", "colored")})
SEASON = {t: s for t, (f, s) in MONASH.items() if s}


def load(task, seed):
    if task in MONASH:
        v = read_tsf(os.path.join(D03, MONASH[task][0] + ".tsf"))[0][1][:50000]
        return v[:-1, None], v[1:], None
    if task.startswith("B_"):
        from river.datasets import synth
        T = 16000
        gen = {"B_FriedmanDrift_LEA": lambda: synth.FriedmanDrift("lea", (4000, 8000, 12000), seed=seed),
               "B_FriedmanDrift_GRA": lambda: synth.FriedmanDrift("gra", (6000, 12000), seed=seed),
               "B_FriedmanDrift_GSG": lambda: synth.FriedmanDrift("gsg", (6000, 12000), 800, seed=seed),
               "B_Planes2D": lambda: synth.Planes2D(seed=seed), "B_Mv": lambda: synth.Mv(seed=seed)}[task]()
        rows = list(gen.take(T))
        keys = sorted(rows[0][0].keys())
        cats = {k: sorted({str(r[0][k]) for r in rows}) for k in keys if isinstance(rows[0][0][k], str)}
        X = [[(1.0 if str(x[k]) == c else 0.0) for k in keys for c in cats[k]] if False else
             sum(([1.0 if str(x[k]) == c else 0.0 for c in cats[k]] if k in cats else [float(x[k])] for k in keys), [])
             for x, _ in rows]
        return np.array(X), np.array([float(r[1]) for r in rows]), None
    if task.startswith("C_"):
        import nonlinear_benchmarks as nb
        if task == "C_F16":
            tr_all, te_all = nb.F16()
            tr = next(d for d in tr_all if "Level3" in d.name); te = next(d for d in te_all if "Level4" in d.name)
        else:
            tr_all, te_all = nb.ParWH()
            tr = next(d for d in tr_all if d.name == "Est-phase-0-amp-2"); te = next(d for d in te_all if d.name == "Val-amp-2")
        u = np.concatenate([np.asarray(tr.u, float).ravel(), np.asarray(te.u, float).ravel()])
        y = np.concatenate([np.asarray(tr.y, float).ravel(), np.asarray(te.y, float).ravel()])
        return np.column_stack([u, np.concatenate([[0.0], y[:-1]])]), y, len(np.asarray(tr.u).ravel())
    # sparse FIR, SNR 10 dB
    K = int(task.split("_K")[1].split("_")[0]); colored = "colored" in task
    rng = np.random.RandomState(seed); T, L = 10000, 32
    w = rng.normal(size=T); x = np.zeros(T)
    for t in range(T):
        x[t] = (0.8 * x[t - 1] + np.sqrt(1 - 0.64) * w[t]) if (colored and t > 0) else w[t]

    def sys_h():
        h = np.zeros(L); h[rng.choice(L, K, replace=False)] = rng.normal(size=K); return h
    h1, h2 = sys_h(), sys_h()
    TDL = np.zeros((T, L))
    for k in range(L):
        TDL[k:, k] = x[: T - k]
    clean = np.where(np.arange(T) < T // 2, TDL @ h1, TDL @ h2)
    return TDL, clean + rng.normal(size=T) * np.sqrt(np.var(clean) / 10.0), None


class LebreV04Step(B.Step):
    def __init__(self, d):
        self.m = LebreV04(d=d)

    def step(self, x, y):
        b = sum(self.m.fp.values()); p = self.m.step(np.asarray(x, float), float(y))
        return p, sum(self.m.fp.values()) - b

    def get_memory_bytes(self):
        return self.m.memory_bytes()


def models_for(task, T):
    ms = ["LEBRE_V04", "LEBRE_V032", "CTRL_PERSISTENCE", "CTRL_ARX_NLMS", "IPNLMS", "RIVER_SGD_LINREG", "RIVER_HATR"]
    if task in SEASON:
        ms.append("CTRL_SEASONAL_NAIVE")
    if T <= 25000:
        ms.append("RIVER_ARF")
    return ms + B.BENCH_MODELS


def make(model_id, D, cfg, seed, task):
    if model_id == "LEBRE_V04":
        return LebreV04Step(D), True
    if model_id == "LEBRE_V032":
        return B.LebreStep(D), True
    if model_id == "CTRL_SEASONAL_NAIVE":
        return B.SeasonalNaive(D, SEASON[task]), True
    return B.make(model_id, D, cfg, seed, task)


def calib_one(args):
    task, model_id, idx, cfg = args
    mses = []
    for s in B.CALIB_SEEDS:
        X, y, _ = load(task, s)
        n = min(int(0.15 * len(X)), 5000); D = X.shape[1]
        sc = B.CausalStandardScaler(d=D)
        m, step = (B.Ipnlms(D, mu=cfg["mu"]), True) if model_id == "IPNLMS" else \
            (B.R.instantiate_model(model_id, D, cfg, seed=s), False)
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
    X, y, split = load(task, seed)
    D = X.shape[1]
    test_start = split if split is not None else int(0.30 * len(X))
    m, step = make(model_id, D, cfg, seed, task)
    t0 = time.time()
    r = B.R.run_full_stream(m, X, y, test_start, is_track_b=step)
    r.pop("trace", None)
    out = {"track": TASKS[task][0], "task_id": task, "model_id": model_id, "seed": seed, "config": json.dumps(cfg),
           "T": len(X), "D": D, **r, "wall": time.time() - t0}
    if model_id == "LEBRE_V04":
        out["coverage"] = m.m.cover_hits / max(m.m.cover_n, 1)
        out["n_active_final"] = len(m.m.active)
        out["n_events"] = len(m.m.events)
    return out


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_BENCH03.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_BENCH03_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(HERE, "lebre_v04.py"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "FREEZE_V04_SHA256.txt")).read().split()[0].lstrip("*")
    t0 = time.time()
    sp = B.grids()
    cjobs = [(t, m, i, c) for t in TASKS for m, g in sp.items() for i, c in enumerate(g)]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        cdf = pd.DataFrame(list(ex.map(calib_one, cjobs, chunksize=1)))
    cdf.to_csv(os.path.join(HERE, "BENCH03_CALIBRATION_LOG.csv"), index=False)
    best = {(t, m): json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])
            for (t, m), g in cdf.groupby(["task_id", "model_id"])}
    print(f"calibration: {len(cdf)} rows, {time.time() - t0:.0f}s", flush=True)
    jobs, size = [], {}
    for t in TASKS:
        seeds = (SYN_B if t.startswith("B_") else SYN_D) if TASKS[t][1] else REAL
        T = len(load(t, seeds[0])[1]); size[t] = T
        for s in seeds:
            for m in models_for(t, T):
                jobs.append((t, m, s, best.get((t, m), {})))
    heavy = {"RIVER_ARF": 50, "B5_ONLINE_ESN": 20, "S4_ACESN": 30, "C3_RLS": 10, "B3_MUSE_RNN": 5}
    jobs.sort(key=lambda j: -size[j[0]] * heavy.get(j[1], 1))
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        df = pd.DataFrame(list(ex.map(eval_one, jobs, chunksize=1)))
    df.to_csv(os.path.join(HERE, "BENCH03_RESULTS.csv"), index=False)
    print(df.groupby("model_id").status.value_counts().unstack(fill_value=0).to_string())
    print(f"{len(df)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
