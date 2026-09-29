#!/usr/bin/env python3
"""
bench02.py — BENCH-02 runner (PREREG_BENCH02.md; hash in PREREG_BENCH02_SHA256.txt).
Frozen LEBRE v0.3.2 vs literature-grounded baselines on four tracks (A online forecasting, B streaming regression
with drift, C nonlinear system identification, D sparse system identification).
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
V03 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01")
sys.path.insert(0, ROOT)
sys.path.insert(0, V03)
os.chdir(ROOT)

from experiments.bench01 import runner as R  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v032 import LebreV032  # noqa: E402

DATA = os.path.join(ROOT, "data", "external_bench02")
SYN_B = list(range(7051, 7061))
SYN_D = list(range(7101, 7111))
REAL_SEEDS = list(range(7201, 7204))
CALIB_SEEDS = [42, 43, 44]
BENCH_MODELS = ["Track_B"] + R.PRIMARY_MODELS[1:] + R.SUPP_MODELS

TASKS = {  # task -> (track, synthetic?)
    "A_ETTh1": ("A", False), "A_ETTh2": ("A", False), "A_ETTm1": ("A", False), "A_ETTm2": ("A", False),
    "A_Exchange": ("A", False), "A_JenaWeather": ("A", False), "A_ECL": ("A", False), "A_Traffic": ("A", False),
    "B_FriedmanDrift_LEA": ("B", True), "B_FriedmanDrift_GRA": ("B", True), "B_FriedmanDrift_GSG": ("B", True),
    "B_Planes2D": ("B", True), "B_Mv": ("B", True),
    "B_Bikes": ("B", False), "B_WaterFlow": ("B", False), "B_TrumpApproval": ("B", False),
    "C_WienerHammerstein": ("C", False), "C_CascadedTanks": ("C", False), "C_EMPS": ("C", False),
}
for K in (1, 4, 8):
    for col in ("white", "colored"):
        TASKS[f"D_SparseFIR_K{K}_{col}"] = ("D", True)
SEASON = {"A_ETTh1": 24, "A_ETTh2": 24, "A_ETTm1": 96, "A_ETTm2": 96, "A_JenaWeather": 144, "A_ECL": 24, "A_Traffic": 24}


# ------------------------------------------------------------------------------------------------ data
def _forecast(V, target_col):
    """Track A information set: all variables at t-1 predict the target at t."""
    V = np.asarray(V, dtype=float)
    return V[:-1], V[1:, target_col], None


def _river_synth(name, seed, T=20000):
    from river.datasets import synth
    gen = {"B_FriedmanDrift_LEA": lambda: synth.FriedmanDrift("lea", (5000, 10000, 15000), seed=seed),
           "B_FriedmanDrift_GRA": lambda: synth.FriedmanDrift("gra", (7000, 14000), seed=seed),
           "B_FriedmanDrift_GSG": lambda: synth.FriedmanDrift("gsg", (7000, 14000), 1000, seed=seed),
           "B_Planes2D": lambda: synth.Planes2D(seed=seed), "B_Mv": lambda: synth.Mv(seed=seed)}[name]()
    rows = list(gen.take(T))
    keys = sorted(rows[0][0].keys())
    cats = {k: sorted({str(r[0][k]) for r in rows}) for k in keys if isinstance(rows[0][0][k], str)}
    X = []
    for x, _ in rows:
        v = []
        for k in keys:
            if k in cats:                               # deterministic one-hot for categorical attributes
                v += [1.0 if str(x[k]) == c else 0.0 for c in cats[k]]
            else:
                v.append(float(x[k]))
        X.append(v)
    return np.array(X), np.array([float(r[1]) for r in rows]), None


def _sparse_fir(name, seed, T=10000, L=32):
    K = int(name.split("_K")[1].split("_")[0]); colored = name.endswith("colored")
    rng = np.random.RandomState(seed)
    w = rng.normal(size=T)
    x = np.zeros(T)
    for t in range(T):
        x[t] = (0.8 * x[t - 1] + np.sqrt(1 - 0.64) * w[t]) if (colored and t > 0) else w[t]

    def sys_h():
        h = np.zeros(L); h[rng.choice(L, K, replace=False)] = rng.normal(size=K); return h
    h1, h2 = sys_h(), sys_h()
    TDL = np.zeros((T, L))
    for k in range(L):
        TDL[k:, k] = x[: T - k]
    clean = np.where(np.arange(T) < T // 2, TDL @ h1, TDL @ h2)
    noise = rng.normal(size=T) * np.sqrt(np.var(clean) / 100.0)      # SNR 20 dB
    return TDL, clean + noise, None


def _sysid(name):
    import nonlinear_benchmarks as nb
    fn = {"C_WienerHammerstein": nb.WienerHammerBenchMark, "C_CascadedTanks": nb.Cascaded_Tanks, "C_EMPS": nb.EMPS}[name]
    tr, te = fn()
    u = np.concatenate([np.asarray(tr.u, float).ravel(), np.asarray(te.u, float).ravel()])
    y = np.concatenate([np.asarray(tr.y, float).ravel(), np.asarray(te.y, float).ravel()])
    yprev = np.concatenate([[0.0], y[:-1]])
    return np.column_stack([u, yprev]), y, len(np.asarray(tr.u).ravel())


def load(task, seed):
    if task.startswith("A_ETT"):
        d = pd.read_csv(os.path.join(DATA, task[2:] + ".csv"))
        return _forecast(d.drop(columns=["date"]).values, 6)
    if task == "A_Exchange":
        return _forecast(pd.read_csv(os.path.join(DATA, "exchange_rate.txt.gz"), header=None).values, 7)
    if task == "A_JenaWeather":
        d = pd.read_csv(os.path.join(ROOT, "data", "external", "jena_climate_2014_2016.csv")).drop(columns=["Date Time"])
        return _forecast(d.values, list(d.columns).index("T (degC)"))
    if task in ("A_ECL", "A_Traffic"):
        f = "electricity.txt.gz" if task == "A_ECL" else "traffic.txt.gz"
        v = pd.read_csv(os.path.join(DATA, f), header=None).values[:, -1:]
        return _forecast(v, 0)
    if task in ("B_Bikes", "B_WaterFlow", "B_TrumpApproval"):
        from river import datasets
        if task == "B_Bikes":
            rows = list(datasets.Bikes())
            X = [[float(x["clouds"]), float(x["humidity"]), float(x["pressure"]), float(x["temperature"]),
                  float(x["wind"]), float(x["moment"].hour)] for x, _ in rows]
            return np.array(X), np.array([float(y) for _, y in rows]), None
        if task == "B_WaterFlow":
            rows = list(datasets.WaterFlow())
            y = np.array([float(v) for _, v in rows])
            X = np.column_stack([np.concatenate([[0.0], y[:-1]]), [float(x["Time"].hour) for x, _ in rows]])
            return X, y, None
        rows = list(datasets.TrumpApproval())
        keys = sorted(rows[0][0].keys())
        return np.array([[float(x[k]) for k in keys] for x, _ in rows]), np.array([float(y) for _, y in rows]), None
    if task.startswith("B_"):
        return _river_synth(task, seed)
    if task.startswith("C_"):
        return _sysid(task)
    return _sparse_fir(task, seed)


# ------------------------------------------------------------------------------------------------ models
class Step:
    """step(x, y) -> (pred, flops) adapter; FLOPs = NaN when the model is not instrumented."""
    def get_memory_bytes(self):
        return -1

    def get_active_params(self):
        return -1


class LebreStep(Step):
    def __init__(self, d):
        self.m = LebreV032(d=d)

    def step(self, x, y):
        b = sum(self.m.fp.values()); p = self.m.step(np.asarray(x, float), float(y))
        return p, sum(self.m.fp.values()) - b

    def get_memory_bytes(self):
        return self.m.memory_bytes()


class Persistence(Step):
    def __init__(self, d):
        self.p = 0.0

    def step(self, x, y):
        out = self.p; self.p = float(y); return out, 0.0

    def get_memory_bytes(self):
        return 4


class SeasonalNaive(Step):
    def __init__(self, d, s):
        self.buf = []; self.s = s

    def step(self, x, y):
        out = self.buf[-self.s] if len(self.buf) >= self.s else (self.buf[-1] if self.buf else 0.0)
        self.buf.append(float(y)); self.buf = self.buf[-self.s:]
        return out, 0.0

    def get_memory_bytes(self):
        return 4 * self.s


class ArxNlms(Step):
    def __init__(self, d, mu=0.1):
        self.w = np.zeros(d + 2); self.yp = 0.0; self.mu = mu; self.d = d

    def step(self, x, y):
        phi = np.concatenate([x, [1.0, self.yp]]); n = len(phi)
        p = float(self.w @ phi); e = float(y) - p
        self.w += self.mu * e / (1e-6 + float(phi @ phi)) * phi; self.yp = float(y)
        return p, float(6 * n + 2)

    def get_memory_bytes(self):
        return 4 * (self.d + 3)


class Ipnlms(Step):
    """IPNLMS (Benesty & Gay 2002), alpha = 0, with a bias input."""
    def __init__(self, d, mu=0.5, alpha=0.0):
        self.w = np.zeros(d + 1); self.mu = mu; self.a = alpha; self.n = d + 1

    def step(self, x, y):
        phi = np.append(x, 1.0)
        p = float(self.w @ phi); e = float(y) - p
        g = (1 - self.a) / (2 * self.n) + (1 + self.a) * np.abs(self.w) / (2 * np.abs(self.w).sum() + 1e-8)
        gx = g * phi
        self.w += self.mu * e * gx / (float(phi @ gx) + 1e-6)
        return p, float(10 * self.n + 6)

    def get_memory_bytes(self):
        return 8 * self.n


class RiverStep(Step):
    def __init__(self, d, kind, seed):
        from river import linear_model, tree, forest, preprocessing, compose
        self.m = {"RIVER_SGD_LINREG": lambda: compose.Pipeline(preprocessing.StandardScaler(),
                                                                linear_model.LinearRegression()),
                  "RIVER_HATR": lambda: tree.HoeffdingAdaptiveTreeRegressor(seed=seed),
                  "RIVER_ARF": lambda: forest.ARFRegressor(seed=seed)}[kind]()

    def step(self, x, y):
        xi = {i: float(v) for i, v in enumerate(x)}
        p = self.m.predict_one(xi)
        p = float(p) if p is not None and np.isfinite(p) else 0.0
        self.m.learn_one(xi, float(y))
        return p, float("nan")


OURS = ["LEBRE_V032", "CTRL_PERSISTENCE", "CTRL_SEASONAL_NAIVE", "CTRL_ARX_NLMS", "IPNLMS",
        "RIVER_SGD_LINREG", "RIVER_HATR", "RIVER_ARF"]


def models_for(task):
    ms = [m for m in OURS if m != "CTRL_SEASONAL_NAIVE" or task in SEASON] + BENCH_MODELS
    if task.startswith("D_"):
        ms = ["LEBRE_V032_NATIVE"] + ms
    return ms


def make(model_id, D, cfg, seed, task):
    if model_id in ("LEBRE_V032", "LEBRE_V032_NATIVE"):
        return LebreStep(D), True
    if model_id == "CTRL_PERSISTENCE":
        return Persistence(D), True
    if model_id == "CTRL_SEASONAL_NAIVE":
        return SeasonalNaive(D, SEASON[task]), True
    if model_id == "CTRL_ARX_NLMS":
        return ArxNlms(D), True
    if model_id == "IPNLMS":
        return Ipnlms(D, mu=cfg.get("mu", 0.5)), True
    if model_id.startswith("RIVER_"):
        return RiverStep(D, model_id, seed), True
    return R.instantiate_model(model_id, D, cfg, seed=seed), model_id == "Track_B"


# ------------------------------------------------------------------------------------------------ calibration
def grids():
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
    sp["IPNLMS"] = [{"mu": 0.1}, {"mu": 0.5}]
    return sp


def calib_one(args):
    task, model_id, idx, cfg = args
    mses = []
    for s in CALIB_SEEDS:
        X, y, _ = load(task, s)
        X = X[:, :] if not task.startswith("D_") else X
        n = min(int(0.15 * len(X)), 5000); D = X.shape[1]
        sc = CausalStandardScaler(d=D)
        if model_id == "IPNLMS":
            m, step = Ipnlms(D, mu=cfg["mu"]), True
        else:
            m, step = R.instantiate_model(model_id, D, cfg, seed=s), False
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


# ------------------------------------------------------------------------------------------------ evaluation
def eval_one(args):
    task, model_id, seed, cfg = args
    X, y, split = load(task, seed)
    if model_id == "LEBRE_V032_NATIVE":
        X = X[:, :1]
    D = X.shape[1]
    test_start = split if split is not None else int(0.30 * len(X))
    m, step = make(model_id, D, cfg, seed, task)
    t0 = time.time()
    r = R.run_full_stream(m, X, y, test_start, is_track_b=step, collect_trace=False)
    r.pop("trace", None)
    return {"track": TASKS[task][0], "task_id": task, "model_id": model_id, "seed": seed, "config": json.dumps(cfg),
            "T": len(X), "D": D, "test_start": test_start, **r, "wall": time.time() - t0}


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_BENCH02.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_BENCH02_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(V03, "lebre_v032.py"), "rb").read()).hexdigest() == \
        open(os.path.join(V03, "FREEZE_V032_SHA256.txt")).read().split()[0].lstrip("*")
    only = os.environ.get("BENCH02_ONLY")
    tasks = [t for t in TASKS if not only or t.startswith(only)]
    t0 = time.time()
    sp = grids()
    cal_path = os.path.join(HERE, "BENCH02_CALIBRATION_LOG.csv")
    cjobs = [(t, m, i, c) for t in tasks for m, g in sp.items() for i, c in enumerate(g)]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        cdf = pd.DataFrame(list(ex.map(calib_one, cjobs, chunksize=1)))
    if os.path.exists(cal_path) and only:
        cdf = pd.concat([pd.read_csv(cal_path), cdf]).drop_duplicates(["task_id", "model_id", "config_id"], keep="last")
    cdf.to_csv(cal_path, index=False)
    best = {(t, m): json.loads(g.sort_values("mean_calibration_mse").iloc[0]["config_params"])
            for (t, m), g in cdf.groupby(["task_id", "model_id"])}
    print(f"calibration: {len(cdf)} rows, {time.time() - t0:.0f}s", flush=True)

    jobs = []
    for t in tasks:
        seeds = (SYN_B if t.startswith("B_") else SYN_D) if TASKS[t][1] else REAL_SEEDS
        for s in seeds:
            for m in models_for(t):
                jobs.append((t, m, s, best.get((t, m), {})))
    # longest first
    size = {t: len(load(t, 7201 if not TASKS[t][1] else 7051 if t.startswith("B_") else 7101)[1]) for t in tasks}
    heavy = {"RIVER_ARF": 50, "B5_ONLINE_ESN": 20, "S4_ACESN": 30, "C3_RLS": 10, "B3_MUSE_RNN": 5}
    jobs.sort(key=lambda j: -size[j[0]] * heavy.get(j[1], 1))
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        rows = list(ex.map(eval_one, jobs, chunksize=1))
    df = pd.DataFrame(rows)
    out = os.path.join(HERE, "BENCH02_RESULTS.csv" if not only else f"BENCH02_RESULTS_{only}.csv")
    df.to_csv(out, index=False)
    print(df.groupby("model_id").status.value_counts().unstack(fill_value=0).to_string())
    print(f"{len(df)} runs, {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
