"""posthoc_feedback.py — POST-HOC checks requested by an external reviewer (not pre-registered).

A. Held-out sets (v0.51 held-out Q1..Q10 and v0.5 held-out N1..N10):
   M_ONLY      memory expert alone (same code as inside v0.51)
   V051        full v0.51, with the trajectory of the structural weight w_S on the test segment
   RLS5        recursive least squares with forgetting (lambda 0.999) on the same 5 features, relative to the last value
   AIRLINE     SARIMA(0,1,1)(0,1,1)s — ARIMA(0,1,1) without period — MLE on the calibration window
               (first min(15% T, 5000) points), then Kalman one-step forecasts with fixed parameters (causal)
   ETS         statsmodels ETS, additive error, seasonal additive, trend none or additive damped chosen by AIC on the
               calibration window; one-step forecasts with fixed parameters
   Metrics: NMSE, skill vs persistence (1 - MSE/MSE_pers), relative MAE vs persistence, MASE (seasonal-naive
   in-sample scale on the pre-test segment).
B. Long null streams: false promotions of the structural expert over 100 000 steps (inputs independent of y), and
   false evictions of a true atom in a stationary stream (the parsimony rent is active, as in the model).
"""
import math
import os
import sys
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (HERE, ROOT, os.path.join(ROOT, "data", "external_v051"), os.path.join(ROOT, "data", "external_v05"),
          os.path.join(ROOT, "data", "external_bench04")):
    sys.path.insert(0, p)
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_s051 import StructuralExpert  # noqa: E402
from lebre_v051 import LebreV051, MemoryExpert  # noqa: E402
import load05  # noqa: E402
import load051  # noqa: E402


def series(src, task):
    X, y, _, _, s, j = (load051 if src == "held" else load05).load(task)
    return X, y, s, j


def calib_n(T):
    return min(int(0.15 * T), 5000)


class RLS5:
    def __init__(self, s, lam=0.999):
        self.M = MemoryExpert(s)                     # reuse its buffer / features / profile bookkeeping
        self.lam = lam; self.P = None; self.w = np.zeros(len(self.M.w)); self.ms = []; self.fp = 0.0

    def step(self, y):
        M = self.M
        p = M.predict()
        if M.phi is not None:
            phi = M.phi
            if self.P is None:
                self.ms.append(float(phi @ phi) / len(phi))
                if len(self.ms) >= 50:
                    self.P = np.eye(len(phi)) * 100.0 / (np.mean(self.ms) + 1e-300)
                yhat = M.last
            else:
                yhat = M.last + float(self.w @ phi)
                Pp = self.P @ phi; k = Pp / (self.lam + phi @ Pp)
                self.w += k * (y - yhat); self.P = (self.P - np.outer(k, Pp)) / self.lam
                self.fp += 4 * len(phi) ** 2 + 6 * len(phi)
        else:
            yhat = p
        M.w[:] = 0.0                                  # M's own NLMS weights unused (features, profile, mean only)
        M.update(y, M.last if M.phi is not None else p)
        return yhat


def run_online(a):
    src, task, arm = a
    X, y, s, j = series(src, task); T = len(y); ts = int(0.30 * T)
    pred = np.empty(T); wS = []
    if arm == "M_ONLY":
        m = MemoryExpert(s)
        for t in range(T):
            p = m.predict(); m.update(float(y[t]), p); pred[t] = p
    elif arm == "RLS5":
        m = RLS5(s)
        for t in range(T):
            pred[t] = m.step(float(y[t]))
    elif arm == "V051":
        m = LebreV051(d=X.shape[1], season=s); sc = CausalStandardScaler(d=X.shape[1])
        for t in range(T):
            pred[t] = m.step(sc.transform(X[t]), float(y[t])); sc.update(X[t])
            if t >= ts:
                wS.append(m.wS)
    return {"src": src, "task": task, "arm": arm, "pred": pred, "wS": np.array(wS)}


def run_stat(a):
    src, task, arm = a
    warnings.filterwarnings("ignore")
    X, y, s, j = series(src, task)
    v = np.concatenate([[X[0, j]], y]); T = len(y); nc = calib_n(T)
    try:
        if arm == "AIRLINE":
            from statsmodels.tsa.statespace.sarimax import SARIMAX
            order, sorder = (0, 1, 1), ((0, 1, 1, s) if s else (0, 0, 0, 0))
            fit = SARIMAX(v[:nc + 1], order=order, seasonal_order=sorder, enforce_invertibility=False,
                          enforce_stationarity=False).fit(disp=False, maxiter=200)
            full = SARIMAX(v, order=order, seasonal_order=sorder, enforce_invertibility=False,
                           enforce_stationarity=False).filter(fit.params)
            fv = np.asarray(full.predict(start=1, end=len(v) - 1))      # one-step-ahead, causal
            info = f"theta={fit.params[0]:.3f}" + (f", Theta={fit.params[1]:.3f}" if s else "")
        else:
            from statsmodels.tsa.exponential_smoothing.ets import ETSModel
            best = None
            for trend, damped in ((None, False), ("add", True)):
                mdl = ETSModel(v[:nc + 1], error="add", trend=trend, damped_trend=damped,
                               seasonal="add" if s else None, seasonal_periods=s if s else None)
                r = mdl.fit(disp=False, maxiter=300)
                if best is None or r.aic < best[0]:
                    best = (r.aic, trend, damped, r)
            _, trend, damped, r = best
            mdl = ETSModel(v, error="add", trend=trend, damped_trend=damped, seasonal="add" if s else None,
                           seasonal_periods=s if s else None)
            full = mdl.smooth(r.params)
            fv = np.asarray(full.fittedvalues)[1:]
            info = f"trend={trend}, damped={damped}"
        ok = bool(np.all(np.isfinite(fv)))
    except Exception as e:  # noqa: BLE001
        fv = np.full(T, np.nan); ok = False; info = repr(e)[:120]
    return {"src": src, "task": task, "arm": arm, "pred": fv, "wS": np.array([]), "info": info, "ok": ok}


def metrics(src, task, pred):
    X, y, s, j = series(src, task); T = len(y); ts = int(0.30 * T)
    yp = np.concatenate([[X[0, j]], y[:-1]])                             # persistence forecast
    e, ep = y[ts:] - pred[ts:], y[ts:] - yp[ts:]
    v = np.concatenate([[X[0, j]], y]); lag = s or 1
    scale = np.mean(np.abs(v[lag:ts + 1] - v[:ts + 1 - lag]))
    return {"nmse": float(np.mean(e ** 2) / (np.var(y[ts:]) + 1e-6)), "skill": float(1 - np.mean(e ** 2) / np.mean(ep ** 2)),
            "rel_mae": float(np.mean(np.abs(e)) / np.mean(np.abs(ep))), "mase": float(np.mean(np.abs(e)) / scale),
            "pers_mase": float(np.mean(np.abs(ep)) / scale)}


# ---------------------------------------------------------------- B: long null streams
def null_one(a):
    seed, kind = a
    rng = np.random.RandomState(seed); T, d = 100_000, 5
    X = rng.normal(size=(T, d))
    if kind == "null_gauss":
        y = rng.normal(size=T)
    elif kind == "null_t3":
        y = rng.standard_t(3, size=T) / math.sqrt(3.0)
    else:                                                               # stationary true structure: y = 0.8 x1(t-3) + noise
        y = np.zeros(T); y[3:] = 0.8 * X[:-3, 1]; y += 0.5 * rng.normal(size=T)
    m = StructuralExpert(d=d, ipnlms=False, intervals=False)
    for t in range(T):
        m.step(X[t], float(y[t]))
    promos = [ev for ev in m.events if ev[1] == "PROVISIONAL->ACTIVE" and ev[0] >= 20]
    true_key = "x1 atrasado 3 passos"
    ev_true = [ev for ev in m.events if ev[1].startswith("ACTIVE->EVICTED") and ev[2] == true_key]
    ev_all = [ev for ev in m.events if ev[1].startswith("ACTIVE->EVICTED")]
    return {"seed": seed, "kind": kind, "promotions": len(promos), "evictions_all": len(ev_all),
            "evictions_true_atom": len(ev_true), "steps": T}


if __name__ == "__main__":
    sets = [("held", t) for t in load051.TASKS] + [("held05", t) for t in load05.TASKS]
    with ProcessPoolExecutor(16) as ex:
        on = list(ex.map(run_online, [(s_, t, a) for s_, t in sets for a in ("M_ONLY", "RLS5", "V051")], chunksize=1))
        st = list(ex.map(run_stat, [(s_, t, a) for s_, t in sets for a in ("AIRLINE", "ETS")], chunksize=1))
        nl = list(ex.map(null_one, [(s, k) for s in range(8801, 8811) for k in ("null_gauss", "null_t3", "true_atom")], chunksize=1))
    rows, wrows = [], []
    for r in on + st:
        if r.get("ok", True):
            rows.append({"src": r["src"], "task": r["task"], "arm": r["arm"], "info": r.get("info", ""), **metrics(r["src"], r["task"], r["pred"])})
        else:
            rows.append({"src": r["src"], "task": r["task"], "arm": r["arm"], "info": r.get("info", ""), "nmse": np.nan})
        if r["arm"] == "V051":
            w = r["wS"]
            wrows.append({"src": r["src"], "task": r["task"], "wS_mean": float(w.mean()), "wS_max": float(w.max()),
                          "frac_wS_gt_0.5": float((w > 0.5).mean()), "frac_wS_gt_0.01": float((w > 0.01).mean()),
                          "wS_final": float(w[-1])})
    df = pd.DataFrame(rows); wdf = pd.DataFrame(wrows); ndf = pd.DataFrame(nl)
    df.to_csv(os.path.join(HERE, "POSTHOC_FEEDBACK_METRICS.csv"), index=False)
    wdf.to_csv(os.path.join(HERE, "POSTHOC_FEEDBACK_WS.csv"), index=False)
    ndf.to_csv(os.path.join(HERE, "POSTHOC_FEEDBACK_NULL.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(df.pivot_table(index=["src", "task"], columns="arm", values="nmse").round(4).to_string())
    print(df[df.arm.isin(["AIRLINE", "ETS"])][["src", "task", "arm", "info"]].to_string())
    print(wdf.round(3).to_string())
    print(ndf.groupby("kind")[["promotions", "evictions_all", "evictions_true_atom"]].agg(["sum", "mean"]).to_string())
