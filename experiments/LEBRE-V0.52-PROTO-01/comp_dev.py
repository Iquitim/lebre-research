#!/usr/bin/env python3
"""comp_dev.py — competitive comparison on the DEVELOPMENT tasks (same protocol for every model).

Protocol
  * every model predicts at every step with an observed target; learning only on observed targets (v0.52 and M also
    receive the quarantine flag; the online comparators and v0.51 receive the same forward-filled inputs);
  * inputs standardised causally (same scaler as the v0.51 harness); target raw;
  * NMSE on the COMMON mask: test region (from 30% of the stream) where the target is observed and every model has a
    finite prediction;
  * online comparators (NLinear, DLinear, Holt-Winters, AMRules): configuration chosen per task on the first
    min(15%, 5000) observed steps (mean MSE over the calibration seeds), as in the v0.51 evaluation;
  * airline SARIMA(0,1,1)(0,1,1)_s (ARIMA(0,1,1) without period): MLE on the calibration window, then Kalman filter
    over the whole series (handles missing targets natively), one-step-ahead;
  * FP/step as reported by each model (Chronos is evaluated separately).
"""
import json
import os
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
B04 = os.path.join(ROOT, "experiments", "LEBRE-V0.4-EXTERNAL-BENCH-04")
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02"), B04,
          os.path.join(ROOT, "experiments", "LEBRE-V0.51-LEAN-01"), HERE, ROOT):
    sys.path.insert(0, p)

TEST_FRAC = 0.30
ONLINE = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "RIVER_AMRULES", "ARX_NLMS"]


class ArxNlms:
    """Dense online ARX baseline (fair, input-aware): NLMS on [1, x_t..x_{t-L} for every input, y_{t-1}..y_{t-L}],
    target and target lags standardised causally (EMA, alpha 1e-4). step(x, y) -> (pred, flops), as the other comparators."""

    def __init__(self, d, mu, L=32):
        self.d, self.mu, self.L = d, mu, L
        self.H = np.zeros((L + 1, d)); self.Y = np.zeros(L)
        self.w = np.zeros(1 + d * (L + 1) + L); self.m, self.v = 0.0, 1.0

    def step(self, x, y):
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = np.clip(np.nan_to_num(x), -8, 8)
        sd = np.sqrt(self.v + 1e-6)
        phi = np.concatenate(([1.0], self.H.ravel(), (self.Y - self.m) / sd))
        p = self.m + sd * float(self.w @ phi)
        e = (float(y) - p) / sd
        self.w += self.mu * e * phi / (1e-6 + float(phi @ phi))
        dlt = float(y) - self.m; self.m += 1e-4 * dlt; self.v = max((1 - 1e-4) * self.v + 1e-4 * (float(y) - self.m) * dlt, 1e-4)
        self.Y = np.roll(self.Y, 1); self.Y[0] = float(y)
        n = len(self.w)
        return float(p), float(4 * n + 12)


def run_airline_x(y, Xs, season, K=4):
    """airline SARIMA with exogenous regressors x_t..x_{t-K} (regression with SARIMA errors), MLE on the calibration
    window, Kalman filter over the whole series, one-step-ahead; the current input x_t is known at prediction time."""
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    warnings.filterwarnings("ignore")
    E = np.column_stack([np.roll(Xs, k, axis=0) for k in range(K + 1)]); E[:K] = 0.0
    idx = _calib_n(y); nc = int(idx[-1]) + 1
    order, sorder = (0, 1, 1), ((0, 1, 1, season) if season else (0, 0, 0, 0))
    try:
        fit = SARIMAX(y[:nc], exog=E[:nc], order=order, seasonal_order=sorder, enforce_invertibility=False,
                      enforce_stationarity=False).fit(disp=False, maxiter=200)
        full = SARIMAX(y, exog=E, order=order, seasonal_order=sorder, enforce_invertibility=False,
                       enforce_stationarity=False).filter(fit.params)
        return np.asarray(full.predict(start=0, end=len(y) - 1)), True, f"k_exog={E.shape[1]}"
    except Exception as e:  # noqa: BLE001
        return np.full(len(y), np.nan), False, repr(e)[:100]


def _scaled_inputs(X):
    from experiments.bench01.streams import CausalStandardScaler
    sc = CausalStandardScaler(d=X.shape[1]); out = np.empty_like(X, dtype=float)
    for t in range(len(X)):
        out[t] = sc.transform(X[t]); sc.update(X[t])
    return out


def _calib_n(y):
    obs = np.flatnonzero(np.isfinite(y))
    n = min(int(0.15 * len(y)), 5000)
    return obs[:n]


def run_online(model_id, Xs, y, season, cfg, seed):
    from newmodels import make_new
    m = ArxNlms(Xs.shape[1], **cfg) if model_id == "ARX_NLMS" else make_new(model_id, Xs.shape[1], cfg, seed, season)
    pred = np.full(len(y), np.nan); fp = []
    for t in range(len(y)):
        if not np.isfinite(y[t]):
            continue
        try:
            p, f = m.step(Xs[t], float(y[t]))
        except Exception:
            return pred, float("nan"), False
        pred[t] = p; fp.append(f)
        if not np.isfinite(p) or abs(p) > 1e12:
            return pred, float("nan"), False
    return pred, float(np.mean(fp)) if fp else float("nan"), True


def calibrate(model_id, Xs, y, season):
    import bench02 as B
    from newmodels import GRIDS
    idx = _calib_n(y)
    grid = [{"mu": m} for m in (0.01, 0.05, 0.2)] if model_id == "ARX_NLMS" else GRIDS.get(model_id, [{}])
    if model_id == "HOLT_WINTERS" and not season:
        grid = [g for g in grid if g["gamma"] == 0.05]
    best, best_mse = grid[0], float("inf")
    for cfg in grid:
        mses = []
        for s in B.CALIB_SEEDS:
            p, _, ok = run_online(model_id, Xs[idx], y[idx], season, cfg, s)
            e = y[idx] - p
            mses.append(float(np.nanmean(e ** 2)) if ok else float("inf"))
        if np.mean(mses) < best_mse:
            best, best_mse = cfg, float(np.mean(mses))
    return best


def run_airline(y, season):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    warnings.filterwarnings("ignore")
    idx = _calib_n(y); nc = int(idx[-1]) + 1
    order, sorder = (0, 1, 1), ((0, 1, 1, season) if season else (0, 0, 0, 0))
    try:
        fit = SARIMAX(y[:nc], order=order, seasonal_order=sorder, enforce_invertibility=False,
                      enforce_stationarity=False).fit(disp=False, maxiter=200)
        full = SARIMAX(y, order=order, seasonal_order=sorder, enforce_invertibility=False,
                       enforce_stationarity=False).filter(fit.params)
        pred = np.asarray(full.predict(start=0, end=len(y) - 1))
        return pred, True, str(np.round(fit.params, 3).tolist())
    except Exception as e:  # noqa: BLE001
        return np.full(len(y), np.nan), False, repr(e)[:100]


def run_lebre(kind, X, Xs, y, qu, season):
    from lebre_v052 import LebreV052, Memory
    pred = np.full(len(y), np.nan)
    if kind == "v051":
        from lebre_v051 import LebreV051
        m = LebreV051(d=X.shape[1], season=season)
        fp0 = 0.0
        for t in range(len(y)):
            if np.isfinite(y[t]):
                pred[t] = m.step(Xs[t], float(y[t]))
        return pred, sum(m.fp.values()) / max(1, int(np.isfinite(y).sum()))
    if kind == "M":
        m = Memory(season)
        for t in range(len(y)):
            p = m.predict(); pred[t] = p
            ok = np.isfinite(y[t]); m.update(y[t] if ok else None, p, learn=ok and not qu[t])
        return pred, m.fp / len(y)
    m = LebreV052(d=X.shape[1], season=season)
    for t in range(len(y)):
        pred[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
    return pred, m.fp_total() / len(y)


def job(args):
    task, model = args
    import data_v052 as D
    d = D.load(task)
    X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]
    Xs = _scaled_inputs(X)
    t0 = time.time(); info = ""
    if model in ("v052", "v051", "M"):
        pred, fp = run_lebre(model, X, Xs, y, qu, s); ok = True
    elif model == "AIRLINE":
        pred, ok, info = run_airline(y, s); fp = float("nan")
    elif model == "AIRLINE_X":
        pred, ok, info = run_airline_x(y, Xs, s); fp = float("nan")
    else:
        cfg = calibrate(model, Xs, y, s); info = json.dumps(cfg)
        pred, fp, ok = run_online(model, Xs, y, s, cfg, 0)
    return {"task": task, "model": model, "pred": pred, "fp": fp, "ok": ok, "info": info, "sec": round(time.time() - t0, 1)}


if __name__ == "__main__":
    import data_v052 as D
    tasks = D.dev_tasks()
    models = ["v052", "v051", "M", "AIRLINE", "AIRLINE_X"] + ONLINE
    with ProcessPoolExecutor(14) as ex:
        res = list(ex.map(job, [(t, m) for t in tasks for m in models], chunksize=1))
    rows = []
    for task in tasks:
        rr = {r["model"]: r for r in res if r["task"] == task}
        y = D.load(task)["y"]; T = len(y); ts = int(TEST_FRAC * T)
        mask = np.isfinite(y); mask[:ts] = False
        for r in rr.values():
            if r["ok"]:
                mask &= np.isfinite(r["pred"])
        var = float(np.var(y[mask]))
        for m, r in rr.items():
            nmse = float(np.mean((y[mask] - r["pred"][mask]) ** 2) / var) if r["ok"] else float("nan")
            rows.append({"task": task, "model": m, "nmse": nmse, "fp": r["fp"], "ok": r["ok"], "info": r["info"],
                         "n_eval": int(mask.sum()), "sec": r["sec"]})
    np.savez_compressed(os.path.join(HERE, "COMP_DEV_PREDS.npz"),
                        **{f"{r['task']}|{r['model']}": r["pred"] for r in res})
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "COMP_DEV.csv"), index=False)
    p = df.pivot_table(index="task", columns="model", values="nmse")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
    print(p.round(4))
    ref = "NLINEAR_ONLINE"
    for grp in ("ons", "camels", "bdg2", ""):
        q = p[p.index.str.startswith(grp)].dropna(axis=1, how="any")
        print(grp or "ALL", {m: round(float(np.exp(np.log(q[m] / q[ref]).mean())), 3) for m in q.columns})
    print(df.groupby("model").fp.mean().round(1))
