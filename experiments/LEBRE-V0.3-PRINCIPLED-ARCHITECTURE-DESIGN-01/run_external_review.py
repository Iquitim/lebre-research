#!/usr/bin/env python3
"""
run_external_review.py — Parts II and III of PREREG_V03_REVIEW_BENCHMARKS.md.

Part II : BENCH-01 synthetic tasks A1..A8, H1, H2 with fresh seeds 131..160. The 15 BENCH-01B models use
          their ORIGINAL calibrated configurations (BENCH_01B_CALIBRATION_LOG.csv).
Part III: three new UCI datasets (data/external_v03). The baselines are calibrated with their own grids on the
          first 15% of each stream (calibration seeds 42..44), exactly as in BENCH-01B phase E2.
LEBRE V03, V031 and the controls are never calibrated. The harness function run_full_stream is reused unchanged.
"""
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
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
os.chdir(ROOT)

from experiments.bench01.streams import get_stream, CausalStandardScaler  # noqa: E402
from experiments.bench01 import runner as R  # noqa: E402
from lebre_v03 import LebreV03  # noqa: E402
from lebre_v031 import LebreV031  # noqa: E402

PART2_TASKS = R.TASKS[:10]
PART2_SEEDS = list(range(131, 161))
PART3_TASKS = ["X1_UCI_Appliances_Energy", "X2_UCI_Beijing_PM25", "X3_UCI_Metro_Traffic"]
PART3_SEEDS = list(range(101, 106))
CALIB_SEEDS = [42, 43, 44]
BASELINES = ["Track_B"] + R.PRIMARY_MODELS[1:] + R.SUPP_MODELS
OURS = ["LEBRE_V03", "LEBRE_V031", "CTRL_ARX_NLMS", "CTRL_PERSISTENCE"]


def load_new(task_id):
    d = os.path.join(ROOT, "data", "external_v03")
    if task_id == "X1_UCI_Appliances_Energy":
        df = pd.read_csv(os.path.join(d, "energydata_complete.csv"))
        feats = ["lights"] + [f"T{i}" for i in range(1, 10)] + [f"RH_{i}" for i in range(1, 10)] + \
                ["T_out", "Press_mm_hg", "RH_out", "Windspeed", "Visibility", "Tdewpoint"]
        return df[feats].values.astype(float), df["Appliances"].values.astype(float)
    if task_id == "X2_UCI_Beijing_PM25":
        df = pd.read_csv(os.path.join(d, "PRSA_data_2010.1.1-2014.12.31.csv"))
        df = df[df["pm2.5"].notna()]
        feats = ["DEWP", "TEMP", "PRES", "Iws", "Is", "Ir", "hour"]
        return df[feats].values.astype(float), df["pm2.5"].values.astype(float)
    df = pd.read_csv(os.path.join(d, "Metro_Interstate_Traffic_Volume.csv.gz"))
    df["hour"] = pd.to_datetime(df["date_time"]).dt.hour
    feats = ["temp", "rain_1h", "snow_1h", "clouds_all", "hour"]
    return df[feats].values.astype(float), df["traffic_volume"].values.astype(float)


def stream(task_id, seed):
    return load_new(task_id) if task_id.startswith("X") else get_stream(task_id, seed=seed)


class StepAdapter:
    def __init__(self, m):
        self.m = m

    def step(self, x, y):
        b = sum(self.m.fp.values())
        p = self.m.step(np.asarray(x, dtype=float), float(y))
        return p, sum(self.m.fp.values()) - b

    def get_memory_bytes(self):
        return self.m.memory_bytes()

    def get_active_params(self):
        return self.m.d + 1 + len(self.m.active)


class ArxNlms:
    def __init__(self, d, mu=0.1):
        self.w = np.zeros(d + 2); self.y_prev = 0.0; self.mu = mu; self.d = d

    def step(self, x, y):
        phi = np.concatenate([x, [1.0, self.y_prev]]); n = len(phi)
        pred = float(self.w @ phi); e = float(y) - pred
        self.w += self.mu * e / (1e-6 + float(phi @ phi)) * phi
        self.y_prev = float(y)
        return pred, float((2 * n - 1) + 1 + (2 * n - 1) + 3 + 2 * n)

    def get_memory_bytes(self):
        return 4 * (self.d + 3)

    def get_active_params(self):
        return self.d + 2


class Persistence:
    def __init__(self, d):
        self.y_prev = 0.0

    def step(self, x, y):
        p = self.y_prev; self.y_prev = float(y); return p, 0.0

    def get_memory_bytes(self):
        return 4

    def get_active_params(self):
        return 0


def make(model_id, D, cfg, seed):
    if model_id == "LEBRE_V03":
        return StepAdapter(LebreV03(d=D)), True
    if model_id == "LEBRE_V031":
        return StepAdapter(LebreV031(d=D)), True
    if model_id == "CTRL_ARX_NLMS":
        return ArxNlms(D), True
    if model_id == "CTRL_PERSISTENCE":
        return Persistence(D), True
    return R.instantiate_model(model_id, D, cfg, seed=seed), model_id == "Track_B"


def search_spaces():
    pcfg = json.load(open(R.PRIMARY_CFG_PATH, encoding="utf-8"))
    scfg = json.load(open(R.SUPP_CFG_PATH, encoding="utf-8"))
    sp = {}
    for b in pcfg["baselines"]["competitive_baselines"]:
        if b["id"] in R.PRIMARY_MODELS:
            sp[b["id"]] = R.build_grid(b["search_grid"])
    for s in scfg["supplementary_challengers"]:
        if s["max_configs"] > 0:
            sp[s["id"]] = R.build_grid(s["search_grid"])
    for c in scfg["simplicity_controls"]:
        sp[c["id"]] = R.build_grid(c["search_grid"])
    return sp


def calib_one(args):
    task_id, model_id, idx, cfg = args
    X, y = stream(task_id, 0)
    n = int(0.15 * len(X)); D = X.shape[1]
    mses = []
    for s in CALIB_SEEDS:
        sc = CausalStandardScaler(d=D); m = R.instantiate_model(model_id, D, cfg, seed=s)
        errs, bad = [], False
        for t in range(n):
            xn = sc.transform(X[t])
            try:
                p = m.predict(xn); m.update(xn, y[t]); sc.update(X[t])
                if not np.isfinite(p) or abs(p) > 1e8:
                    bad = True; break
                errs.append(float((y[t] - p) ** 2))
            except Exception:
                bad = True; break
        mses.append(float("inf") if bad or not errs else float(np.mean(errs)))
    return {"task_id": task_id, "model_id": model_id, "config_id": idx, "config_params": json.dumps(cfg),
            "mean_calibration_mse": float(np.mean(mses))}


def eval_one(args):
    task_id, model_id, seed, cfg = args
    X, y = stream(task_id, seed)
    m, is_step = make(model_id, X.shape[1], cfg, seed)
    r = R.run_full_stream(m, X, y, int(0.30 * len(X)), is_track_b=is_step)
    r.pop("trace", None)
    return {"part": "III" if task_id.startswith("X") else "II", "task_id": task_id, "model_id": model_id,
            "seed": seed, "config": json.dumps(cfg), **r}


def main():
    pre = open(os.path.join(HERE, "PREREG_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_V03_REVIEW_BENCHMARKS.md"), "rb").read()).hexdigest() == pre
    t0 = time.time()
    # calibrated configs for Part II: exactly the BENCH-01B choice
    cal = pd.read_csv(os.path.join(ROOT, "experiments", "BENCH-01B", "BENCH_01B_CALIBRATION_LOG.csv"))
    best = {}
    for (t, m), g in cal.groupby(["task_id", "model_id"]):
        best[(t, m)] = json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])
    # Part III calibration (BENCH-01B phase E2 protocol)
    sp = search_spaces()
    cjobs = [(t, m, i, c) for t in PART3_TASKS for m, grid in sp.items() for i, c in enumerate(grid)]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        crow = list(ex.map(calib_one, cjobs, chunksize=1))
    cdf = pd.DataFrame(crow)
    cdf.to_csv(os.path.join(HERE, "EXTERNAL_PART3_CALIBRATION_LOG.csv"), index=False)
    for (t, m), g in cdf.groupby(["task_id", "model_id"]):
        best[(t, m)] = json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])
    print(f"calibration done: {len(cdf)} configs, {time.time() - t0:.0f}s", flush=True)

    jobs = [(t, m, s, best.get((t, m), {})) for t in PART2_TASKS for s in PART2_SEEDS for m in BASELINES + OURS]
    jobs += [(t, m, s, best.get((t, m), {})) for t in PART3_TASKS for s in PART3_SEEDS for m in BASELINES + OURS]
    jobs.sort(key=lambda j: 0 if j[0].startswith("X") else 1)       # long streams first
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        rows = list(ex.map(eval_one, jobs, chunksize=1))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "EXTERNAL_REVIEW_RESULTS.csv"), index=False)
    print(df.groupby(["part", "model_id"]).status.value_counts().unstack(fill_value=0).to_string())
    print(f"{len(df)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
