#!/usr/bin/env python3
"""strong_baselines.py — strong input-aware online comparators on the DEVELOPMENT tasks (same protocol as comp_dev:
causally scaled inputs, only steps with an observed target are fed, calibration only on the first min(15%, 5000) steps).

ARX_RLS_PLS  six ARX models fitted by RLS (forgetting 0.9995) on [1, y_{t-1..t-p}, x_{t..t-q} of every input], target
             standardised causally (EMA 1e-4); p in {2, 8}, q in {2, 8, 24}. The forecast is the model with the smallest
             discounted cumulative squared a-priori error so far (predictive least squares: Rissanen 1986; Wei 1992).
             No calibration.
LASSO_ONLINE proximal normalised gradient with soft-thresholding (online L1) on [1, x lags 0..32 of every input,
             y lags 1..32], target standardised causally; step mu and penalty lam calibrated on the first steps.
step(x, y) -> (prediction, FP of the step), as the other comparators.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402


class _Std:
    """causal EMA standardisation of the target (as comp_dev.ArxNlms)"""
    def __init__(self):
        self.m, self.v = 0.0, 1.0

    def sd(self):
        return float(np.sqrt(self.v + 1e-6))

    def upd(self, y):
        dlt = y - self.m; self.m += 1e-4 * dlt; self.v = max((1 - 1e-4) * self.v + 1e-4 * (y - self.m) * dlt, 1e-4)


class ArxRlsPls:
    GRID = [(p, q) for p in (2, 8) for q in (2, 8, 24)]

    def __init__(self, d, lam=0.9995, disc=0.999):
        self.d, self.lam, self.disc = d, lam, disc
        self.Q = max(q for _, q in self.GRID); self.Pm = max(p for p, _ in self.GRID)
        self.H = np.zeros((self.Q + 1, d)); self.Y = np.zeros(self.Pm); self.st = _Std()
        self.models = []
        for p, q in self.GRID:
            n = 1 + p + d * (q + 1)
            self.models.append({"p": p, "q": q, "w": np.zeros(n), "P": 10.0 * np.eye(n), "s": 0.0})

    def _phi(self, mo):
        return np.concatenate(([1.0], self.Y[:mo["p"]], self.H[:mo["q"] + 1].ravel()))

    def step(self, x, y):
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = np.clip(np.nan_to_num(x), -8, 8)
        sd = self.st.sd(); fp = 0.0
        phis = [self._phi(mo) for mo in self.models]
        preds = [float(mo["w"] @ f) for mo, f in zip(self.models, phis)]
        best = int(np.argmin([mo["s"] for mo in self.models]))
        p = self.st.m + sd * preds[best]
        z = (float(y) - self.st.m) / sd
        for mo, f, pr in zip(self.models, phis, preds):
            e = z - pr
            mo["s"] = self.disc * mo["s"] + e * e
            Pf = mo["P"] @ f; k = Pf / (self.lam + f @ Pf)
            mo["w"] = mo["w"] + k * e; mo["P"] = (mo["P"] - np.outer(k, Pf)) / self.lam
            n = len(f); fp += 4 * n * n + 8 * n + 3
        self.st.upd(float(y)); self.Y = np.roll(self.Y, 1); self.Y[0] = (float(y) - self.st.m) / self.st.sd()
        return float(p), fp + len(self.models) + 12


class LassoOnline:
    def __init__(self, d, mu, lam, L=32):
        self.d, self.mu, self.lam, self.L = d, mu, lam, L
        self.H = np.zeros((L + 1, d)); self.Y = np.zeros(L); self.st = _Std()
        self.w = np.zeros(1 + d * (L + 1) + L)

    def step(self, x, y):
        self.H = np.roll(self.H, 1, axis=0); self.H[0] = np.clip(np.nan_to_num(x), -8, 8)
        sd = self.st.sd()
        phi = np.concatenate(([1.0], self.H.ravel(), self.Y))
        p = self.st.m + sd * float(self.w @ phi)
        e = (float(y) - p) / sd
        w = self.w + self.mu * e * phi / (1e-6 + float(phi @ phi))
        thr = self.mu * self.lam
        w[1:] = np.sign(w[1:]) * np.maximum(np.abs(w[1:]) - thr, 0.0)          # no penalty on the intercept
        self.w = w
        self.st.upd(float(y)); self.Y = np.roll(self.Y, 1); self.Y[0] = (float(y) - self.st.m) / self.st.sd()
        n = len(self.w)
        return float(p), float(6 * n + 12)


def run(model, Xs, y):
    pred = np.full(len(y), np.nan); fp = []
    for t in range(len(y)):
        if not np.isfinite(y[t]):
            continue
        p, f = model.step(Xs[t], float(y[t])); pred[t] = p; fp.append(f)
        if not np.isfinite(p) or abs(p) > 1e12:
            return pred, float("nan"), False
    return pred, float(np.mean(fp)), True


def job(task):
    d = D.load(task); X, y = d["X"], d["y"]; Xs = C._scaled_inputs(X)
    out = {}
    pr, fp, ok = run(ArxRlsPls(X.shape[1]), Xs, y); out["ARX_RLS_PLS"] = (pr, fp, ok)
    idx = C._calib_n(y); best, bm = None, float("inf")
    for mu in (0.01, 0.05, 0.2):
        for lam in (1e-4, 1e-3, 1e-2):
            p, _, okc = run(LassoOnline(X.shape[1], mu, lam), Xs[idx], y[idx])
            m = float(np.nanmean((y[idx] - p) ** 2)) if okc else float("inf")
            if m < bm:
                best, bm = (mu, lam), m
    pr, fp, ok = run(LassoOnline(X.shape[1], *best), Xs, y); out["LASSO_ONLINE"] = (pr, fp, ok)
    return task, out, best


if __name__ == "__main__":
    tasks = D.dev_tasks()
    with ProcessPoolExecutor(15) as ex:
        res = list(ex.map(job, tasks, chunksize=1))
    np.savez_compressed(os.path.join(HERE, "STRONG_DEV_PREDS.npz"),
                        **{f"{t}|{m}": v[0] for t, o, _ in res for m, v in o.items()})
    rows = [{"task": t, "model": m, "fp": v[1], "ok": v[2], "cfg": str(b) if m == "LASSO_ONLINE" else ""} for t, o, b in res for m, v in o.items()]
    pd.DataFrame(rows).to_csv(os.path.join(HERE, "STRONG_DEV.csv"), index=False)
    print(pd.DataFrame(rows).groupby("model")[["fp"]].describe().round(0))
