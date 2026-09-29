#!/usr/bin/env python3
"""chronos_dev.py — foundation-model comparators on the DEVELOPMENT tasks (protocol of the v0.51 evaluation).

Chronos-Bolt tiny, Chronos-Bolt small and Chronos-2, zero-shot, context = the last 512 targets before t (missing values
forward-filled causally), one-step median forecast, on 1000 evenly spaced test points with an observed target
(test region from 30% of the stream). Every other model (from COMP_DEV_PREDS.npz) is scored on exactly the same points.
FP/step estimated as 2 x parameters x context tokens (order of magnitude only, as in the v0.51 documents).
"""
import os
import sys
import time

import numpy as np
import pandas as pd
import torch

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import data_v052 as D  # noqa: E402

MODELS = {"CHRONOS_BOLT_TINY": ("amazon/chronos-bolt-tiny", 9e6), "CHRONOS_BOLT_SMALL": ("amazon/chronos-bolt-small", 48e6),
          "CHRONOS2": ("amazon/chronos-2", 120e6), "CHRONOS2_COV": ("amazon/chronos-2", 120e6)}
CTX, NPTS = 512, 1000


def points(y):
    T = len(y); ts = int(0.30 * T)
    obs = np.flatnonzero(np.isfinite(y[ts:])) + ts
    return obs[np.unique(np.linspace(0, len(obs) - 1, min(NPTS, len(obs))).astype(int))]


def contexts(y, idx, X=None):
    """univariate context; with X (Chronos-2 with covariates) every input is a past covariate over the same window and
    its CURRENT value x_t is a known future covariate — exactly the information the online models have at time t."""
    yf = pd.Series(y).ffill().to_numpy()
    Xf = pd.DataFrame(X).ffill().fillna(0.0).to_numpy() if X is not None else None
    out = []
    for t in idx:
        a = max(0, t - CTX)
        c = yf[a:t]; keep = np.isfinite(c)
        if X is None:
            out.append(torch.tensor(c[keep], dtype=torch.float32)); continue
        out.append({"target": c[keep].astype(np.float32),
                    "past_covariates": {f"x{k}": Xf[a:t, k][keep].astype(np.float32) for k in range(X.shape[1])},
                    "future_covariates": {f"x{k}": Xf[t:t + 1, k].astype(np.float32) for k in range(X.shape[1])}})
    return out


if __name__ == "__main__":
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    tasks = D.dev_tasks()
    dd = {t: D.load(t) for t in tasks}; ys = {t: dd[t]["y"] for t in tasks}
    idxs = {t: points(ys[t]) for t in tasks}
    preds = {}
    for mid, (name, nparam) in MODELS.items():
        pipe = BaseChronosPipeline.from_pretrained(name, device_map="cpu")
        for t in tasks:
            t0 = time.time(); inp = contexts(ys[t], idxs[t], dd[t]["X"] if mid == "CHRONOS2_COV" else None); out = []
            for b in range(0, len(inp), 256):
                q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[0.5])
                q = torch.stack([qq.reshape(-1)[0] for qq in q]) if isinstance(q, list) else q.reshape(len(inp[b:b + 256]), -1)[:, 0]
                out.append(q.float().numpy())
            preds[(t, mid)] = np.concatenate(out)
            print(f"{mid:20s} {t:42s} {time.time() - t0:5.0f}s", flush=True)
    comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz"))
    rows = []
    for t in tasks:
        idx = idxs[t]; yt = ys[t][idx]
        cand = {k.split("|")[1]: comp[k][idx] for k in comp.files if k.split("|")[0] == t}
        cand.update({mid: preds[(t, mid)] for mid in MODELS})
        ok = np.ones(len(idx), bool)
        for v in cand.values():
            if np.isfinite(v).mean() > 0.95:      # a model that failed entirely is reported as NaN, not used for the mask
                ok &= np.isfinite(v)
        var = float(np.var(yt[ok]))
        for m, v in cand.items():
            good = np.isfinite(v[ok]).all()
            rows.append({"task": t, "model": m, "nmse": float(np.mean((yt[ok] - v[ok]) ** 2) / var) if good else float("nan"),
                         "n_points": int(ok.sum())})
    df = pd.DataFrame(rows); df.to_csv(os.path.join(HERE, "COMP_DEV_1000PTS.csv"), index=False)
    p = df.pivot_table(index="task", columns="model", values="nmse")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20)
    print(p.round(4))
    for grp in ("ons", "camels", "bdg2", ""):
        q = p[p.index.str.startswith(grp)].dropna(axis=1, how="any")
        print(grp or "ALL", {m: round(float(np.exp(np.log(q[m] / q["NLINEAR_ONLINE"]).mean())), 3) for m in q.columns})
