#!/usr/bin/env python3
"""eval_v051.py — PREREG_V051.md (online models). Usage: python eval_v051.py internal|heldout|heldout_v05|bench04"""
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
B04 = os.path.join(ROOT, "experiments", "LEBRE-V0.4-EXTERNAL-BENCH-04")
V03 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01")
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02"), os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"),
          os.path.join(ROOT, "data", "external_bench04"), os.path.join(ROOT, "data", "external_v05"),
          os.path.join(ROOT, "data", "external_v051"), os.path.join(ROOT, "experiments", "LEBRE-V0.46-STABLE-COMPETITIVE-01"),
          B04, V03, HERE, ROOT):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402  (chdir ROOT)
import bench04 as K4  # noqa: E402
import load04  # noqa: E402
import load05  # noqa: E402
import load051  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v045 import LebreV045  # noqa: E402
from lebre_v05 import LebreV05  # noqa: E402
from lebre_v051 import LebreV051  # noqa: E402

SEEDS_INT = list(range(2561, 2591))
SEEDS_EXT = [7611, 7612, 7613]
OFFSETS = list(range(0, 500, 50))


def check():
    for f, h in (("PREREG_V051.md", "PREREG_V051_SHA256.txt"), ("lebre_v051.py", "FREEZE_V051_SHA256.txt"),
                 ("lebre_s051.py", "FREEZE_S051_SHA256.txt")):
        assert hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest() == \
            open(os.path.join(HERE, h)).read().split()[0].lstrip("*"), f


# ------------------------------------------------------------------ part 1: internal
def internal_one(a):
    from scratch.bench_v02_integration import generate_v02_stream
    from run_dev_eval import GT, struct_score
    task, seed, arm = a
    X, y, _ = generate_v02_stream(task, seed=seed, total_steps=6000)
    m = {"V045": lambda: LebreV045(d=5), "V05": lambda: LebreV05(d=5), "V051": lambda: LebreV051(d=5)}[arm]()
    checks = {c[0]: c for c in GT.get(task, [])}
    err = np.empty(6000); fps = np.empty(6000); faith = 0.0; snaps = []
    for t in range(6000):
        b = sum(m.fp.values()); p = m.step(X[t], float(y[t])); err[t] = y[t] - p; fps[t] = sum(m.fp.values()) - b
        if arm in ("V05", "V051"):
            yh, parts = m.explain_prediction(); faith = max(faith, abs(yh - sum(c for _, c in parts)) / max(1.0, abs(yh)))
        if t in checks:
            s = m.A if arm == "V05" else (m.S if arm == "V051" else m)
            lags = {(q["key"][1], q["key"][2]) for q in s.active if q["key"][0] == "lag" and q["key"][2] >= 1}
            snaps.append(struct_score(lags, any(q["key"][0] == "res" for q in s.active), checks[t][1], checks[t][2])[0])
    out = {"task_id": task, "seed": seed, "arm": arm, "nmse": float(np.mean(err ** 2) / np.var(y)), "fp": float(fps.mean()), "fp_peak": float(fps.max()),
           "struct_checks": len(snaps), "struct_exact": int(sum(snaps))}
    out["coverage"] = m.cover_hits / m.cover_n
    if arm in ("V05", "V051"):
        out["faith_rel"] = faith; out["w_structural_final"] = float(m.wts[0])
    return out


# ------------------------------------------------------------------ parts 2-3: external online
class V05Step(B.Step):
    def __init__(self, d, season, ts, cls=LebreV05):
        self.m = cls(d=d, season=season); self.t = 0; self.ts = ts; self.w = []; self.hit = 0; self.faith = 0.0

    def step(self, x, y):
        q = self.m.interval()
        b = sum(self.m.fp.values()); p = self.m.step(np.asarray(x, float), float(y))
        yh, parts = self.m.explain_prediction()
        self.faith = max(self.faith, abs(yh - sum(c for _, c in parts)) / max(1.0, abs(yh)))
        if self.t >= self.ts and np.isfinite(q):
            self.w.append(q); self.hit += int(abs(float(y) - p) <= q)
        self.t += 1
        return p, sum(self.m.fp.values()) - b

    def get_memory_bytes(self):
        return self.m.memory_bytes()


HELD_MODELS = ["LEBRE_V051", "LEBRE_V05", "LEBRE_V045", "LEBRE_V032", "CTRL_PERSISTENCE", "CTRL_ARX_NLMS", "IPNLMS",
               "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS"]


def ext_one(a):
    src, task, model_id, seed, cfg = a
    L = {"held": load051, "held05": load05, "b04": load04}[src]
    X, y, _, _, s, _ = L.load(task); ts = int(0.30 * len(X))
    if model_id == "LEBRE_V051":
        m, step = V05Step(X.shape[1], s, ts, LebreV051), True
    elif model_id == "LEBRE_V05":
        m, step = V05Step(X.shape[1], s, ts), True
    elif model_id == "LEBRE_V045":
        m, step = K4.LebreV04Step(X.shape[1], ts), True
        m.m = LebreV045(d=X.shape[1])
    elif model_id == "CTRL_SEASONAL_NAIVE":
        m, step = B.SeasonalNaive(X.shape[1], s), True
    elif model_id in K4.NEW_ONLINE:
        m, step = K4.make_new(model_id, X.shape[1], cfg, seed, s), True
    else:
        m, step = B.make(model_id, X.shape[1], cfg, seed, task)
    t0 = time.time()
    r = B.R.run_full_stream(m, X, y, ts, is_track_b=step); r.pop("trace", None)
    out = {"src": src, "task_id": task, "model_id": model_id, "seed": seed, "config": json.dumps(cfg), "T": len(X),
           "D": X.shape[1], **r, "wall": time.time() - t0, "ms_per_step": 1000 * (time.time() - t0) / len(X)}
    if model_id in ("LEBRE_V051", "LEBRE_V05", "LEBRE_V045"):
        sd = float(np.std(y[ts:]))
        out["coverage"] = m.hit / max(len(m.w), 1)
        out["interval_width_rel"] = 2 * float(np.mean(m.w)) / sd if m.w else np.nan
    if model_id in ("LEBRE_V051", "LEBRE_V05"):
        out["faith_rel"] = m.faith; out["w_final"] = json.dumps([round(float(v), 3) for v in m.m.wts])
    return out


def offset_one(a):
    src, task, arm, off, cfg = a
    L = {"held": load051, "held05": load05, "b04": load04}[src]
    X, y, _, _, s, _ = L.load(task); T = len(X); ts = int(0.30 * T)
    sc = CausalStandardScaler(d=X.shape[1])
    m = {"V051": lambda: LebreV051(d=X.shape[1], season=s), "V05": lambda: LebreV05(d=X.shape[1], season=s), "V045": lambda: LebreV045(d=X.shape[1]),
         "V032": lambda: B.LebreStep(X.shape[1]).m,
         "NLIN": lambda: K4.make_new("NLINEAR_ONLINE", X.shape[1], cfg, 0, s)}[arm]()
    e = []
    for i in range(off, T):
        xn = sc.transform(X[i])
        p = m.step(xn, float(y[i])); sc.update(X[i])
        p = p[0] if isinstance(p, tuple) else p
        if i >= ts:
            e.append((y[i] - p) ** 2)
    ok = bool(np.all(np.isfinite(e)))
    return {"src": src, "task_id": task, "arm": arm, "offset": off, "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6)) if ok else np.inf}


def calib_held(a):
    K4.load = load051.load           # set inside each worker (spawned processes re-import modules)
    return K4.calib_one(a)


def calib(tasks):
    K4.load = load051.load
    sp = {m: g for m, g in K4.all_grids().items() if m in ("IPNLMS", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS")}
    jobs = [(t, m, i, c) for t in tasks for m, g in sp.items() for i, c in enumerate(g)
            if not (m == "HOLT_WINTERS" and load051.load(t)[4] is None and c["gamma"] != 0.05)]
    with ProcessPoolExecutor(16) as ex:
        cdf = pd.DataFrame(list(ex.map(calib_held, jobs, chunksize=1)))
    cdf.to_csv(os.path.join(HERE, "HELDOUT_CALIBRATION_LOG.csv"), index=False)
    return {(t, m): json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"]) for (t, m), g in cdf.groupby(["task_id", "model_id"])}


def main(part):
    check()
    t0 = time.time()
    if part == "internal":
        from scratch.bench_v02_integration import BENCHMARK_TASKS
        jobs = [(t, s, a) for s in SEEDS_INT for t in BENCHMARK_TASKS for a in ("V045", "V05", "V051")]
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(internal_one, jobs, chunksize=4))).to_csv(os.path.join(HERE, "INTERNAL_V051_RESULTS.csv"), index=False)
    elif part == "heldout":
        tasks = list(load051.TASKS)
        best = calib(tasks)
        jobs = []
        for t in tasks:
            ms = HELD_MODELS + (["CTRL_SEASONAL_NAIVE"] if load051.load(t)[4] else [])
            for m in ms:
                for s in SEEDS_EXT:
                    jobs.append(("held", t, m, s, best.get((t, m), {})))
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(ext_one, jobs, chunksize=1))).to_csv(os.path.join(HERE, "HELDOUT_V051_RESULTS.csv"), index=False)
        ojobs = [("held", t, a, o, best.get((t, "NLINEAR_ONLINE"), {})) for t in tasks for a in ("V051", "V05", "NLIN") for o in OFFSETS]
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(offset_one, ojobs, chunksize=1))).to_csv(os.path.join(HERE, "HELDOUT_V051_OFFSETS.csv"), index=False)
    elif part == "heldout_v05":
        jobs = [("held05", t, "LEBRE_V051", s, {}) for t in load05.TASKS for s in SEEDS_EXT]
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(ext_one, jobs, chunksize=1))).to_csv(os.path.join(HERE, "HELDOUT05_V051_RESULTS.csv"), index=False)
    elif part == "bench04":
        jobs = [("b04", t, "LEBRE_V051", s, {}) for t in load04.TASKS for s in SEEDS_EXT]
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(ext_one, jobs, chunksize=1))).to_csv(os.path.join(HERE, "BENCH04_V051_RESULTS.csv"), index=False)
        cal = pd.read_csv(os.path.join(B04, "BENCH04_CALIBRATION_LOG.csv"))
        cal = cal[cal.model_id == "NLINEAR_ONLINE"]
        bn = {t: json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"]) for t, g in cal.groupby("task_id")}
        ojobs = [("b04", t, a, o, bn.get(t, {})) for t in load04.TASKS for a in ("V051",) for o in OFFSETS]
        with ProcessPoolExecutor(16) as ex:
            pd.DataFrame(list(ex.map(offset_one, ojobs, chunksize=1))).to_csv(os.path.join(HERE, "BENCH04_V051_OFFSETS.csv"), index=False)
    print(f"{part} done {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
