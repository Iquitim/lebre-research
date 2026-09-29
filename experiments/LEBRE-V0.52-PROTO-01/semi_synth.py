#!/usr/bin/env python3
"""semi_synth.py — semi-synthetic tasks: REAL inputs (outflows of 5 plants of the DEVELOPMENT river Grande, 3-h, 2015-2025)
passed through DECLARED structures plus Gaussian noise. Structures fixed before running (26/09/2026):

  SS0 null        y = e                                         (real inputs, no relation)
  SS1 one lag     y = 0.8 x1(t-3) + e
  SS2 multi       y = 0.8 x0(t-3) + 0.6 x2(t-7) + 0.5 x4(t-20) + e
  SS3 storage     z = 0.8 z(t-1) + x0(t) + w ;  y = x3(t-12) + z + e      (x0 low-passed, pole 0.8)
  SS4 seasonal    y = 1.5 sin(2 pi t / 8) + 0.8 x1(t-2) + e    (daily cycle at 3-h resolution; season 8 declared)

Inputs are standardised with their own full-sample mean/sd for GENERATION only; the models receive the raw inputs through
the same causal scaler as everywhere else. e, w ~ N(0, 1); 5 noise seeds (6101-6105, checked unused).
Truth keys use the v0.52 dictionary (x index = column below); with self_input the target's own past is index 5.
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402

PLANTS = ["CAMARGOS", "ITUTINGA", "FUNIL-MG", "FURNAS", "M. MORAES"]      # outflows (x0..x4), development river only
SEEDS = [6101, 6102, 6103, 6104, 6105]
TRUTH = {"SS0": set(), "SS1": {("lag", 1, 3)}, "SS2": {("lag", 0, 3), ("lag", 2, 7), ("lag", 4, 20)},
         "SS3": {("lag", 3, 12), ("lp", 0, 0.8), ("res", 0.8)}, "SS4": {("lag", 1, 2)}}


def inputs():
    df = D._ons_hourly(PLANTS)
    idx = pd.date_range("2015-01-01", "2025-12-31 23:00", freq="h")
    piv = df.pivot_table(index="din_instante", columns="nom_reservatorio", values="val_vazaodefluente")
    X = np.column_stack([D._spike_filter(D._agg3h(piv[p], idx), 56) for p in PLANTS])
    X = pd.DataFrame(X).ffill().bfill().to_numpy()
    return X


def generate(task, seed, X):
    rng = np.random.default_rng(seed)
    Z = (X - X.mean(0)) / X.std(0)
    T = len(Z); e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), Z[:-k, i]]
    if task == "SS0":
        y = e
    elif task == "SS1":
        y = 0.8 * lag(1, 3) + e
    elif task == "SS2":
        y = 0.8 * lag(0, 3) + 0.6 * lag(2, 7) + 0.5 * lag(4, 20) + e
    elif task == "SS3":
        w = rng.standard_normal(T); z = np.zeros(T)
        for t in range(1, T):
            z[t] = 0.8 * z[t - 1] + Z[t, 0] + w[t]
        y = lag(3, 12) + z + e
    else:
        y = 1.5 * np.sin(2 * np.pi * np.arange(T) / 8) + 0.8 * lag(1, 2) + e
    return y


def job(a):
    task, seed, model = a
    X = inputs(); y = generate(task, seed, X)
    season = 8 if task == "SS4" else None
    Xs = C._scaled_inputs(X); qu = np.zeros(len(y), bool)
    out = {"task": task, "seed": seed, "model": model}
    if model == "v052":
        from lebre_v052 import LebreV052
        m = LebreV052(d=X.shape[1], season=season); pred = np.empty(len(y))
        for t in range(len(y)):
            pred[t] = m.step(Xs[t], float(y[t]))
        ev = [e for e in m.events if e[1] == "accepted"]; truth = TRUTH[task]
        is_self = lambda k: k is not None and k[0] in ("lag", "lp") and k[1] == X.shape[1]
        final = set(m.structure())
        out.update(fp=m.fp_total() / len(y), structure=str(sorted(final)), true_found=len(final & truth), n_truth=len(truth),
                   exact_final=int({k for k in final if not is_self(k)} == truth),
                   false_exog_adds=sum(1 for e in ev if e[3] and e[3] not in truth and not is_self(e[3])),
                   first_true=min([e[0] for e in ev if e[3] in truth], default=None))
    elif model == "v051":
        pred, fp = C.run_lebre("v051", X, Xs, y, qu, season); out["fp"] = fp
    else:
        cfg = C.calibrate(model, Xs, y, season); pred, fp, ok = C.run_online(model, Xs, y, season, cfg, 0); out["fp"] = fp
    ts = int(0.3 * len(y)); ok = np.isfinite(pred[ts:])
    out["nmse"] = float(np.mean((y[ts:][ok] - pred[ts:][ok]) ** 2) / np.var(y[ts:][ok]))
    return out


if __name__ == "__main__":
    jobs = [(t, s, m) for t in TRUTH for s in SEEDS for m in ("v052", "v051", "ARX_NLMS", "NLINEAR_ONLINE")]
    with ProcessPoolExecutor(14) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    R.to_csv(os.path.join(HERE, "SEMI_SYNTH.csv"), index=False)
    pd.set_option("display.width", 220)
    print(R.pivot_table(index="task", columns="model", values="nmse", aggfunc="mean").round(3))
    v = R[R.model == "v052"]
    print(v.groupby("task")[["true_found", "n_truth", "exact_final", "false_exog_adds", "first_true", "fp"]].mean().round(2))
