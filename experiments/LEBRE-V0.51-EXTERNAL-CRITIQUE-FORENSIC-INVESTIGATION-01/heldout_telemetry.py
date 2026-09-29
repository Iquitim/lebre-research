#!/usr/bin/env python3
"""heldout_telemetry.py — Phase Q and N on real data: structural activity of S inside v0.51 on both held-out sets, and the
interval operators (code A vs accumulated B vs every-step C) applied offline to the model's own combined errors.
Same harness as the original evaluation (causal EMA scaler on inputs, test from 0.30 T)."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import forensic_runs as F  # noqa: E402
from deterministic_audits import quantile_ops  # noqa: E402
from lebre_v051 import LebreV051  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
import load05  # noqa: E402
import load051  # noqa: E402


def one(a):
    src, task = a
    F.check_frozen()
    X, y, _, _, s, j = (load051 if src == "held" else load05).load(task)
    T = len(y); ts = int(0.30 * T)
    m = LebreV051(d=X.shape[1], season=s); sc = CausalStandardScaler(d=X.shape[1])
    e = np.empty(T); contrib = np.empty(T); wS = np.empty(T); hit = np.empty(T, bool); q_prev = np.nan
    for t in range(T):
        q_prev = m.interval()
        p = m.step(sc.transform(X[t]), float(y[t])); sc.update(X[t])
        e[t] = y[t] - p; yh, w, sp, mp = m._last
        contrib[t] = w * (sum(c for _, c in sp) - sum(c for _, c in mp)); wS[t] = w
        hit[t] = np.isfinite(q_prev) and abs(e[t]) <= q_prev
    ev = m.S.events
    promos = [x for x in ev if x[1] == "PROVISIONAL->ACTIVE"]
    struct_promos = [x for x in promos if "atual" not in x[2]]
    st = slice(ts, T)
    out = {"src": src, "task": task, "d": X.shape[1], "s": s, "mean_wS": float(wS[st].mean()), "max_wS": float(wS[st].max()),
           "frac_wS_gt_0.5": float((wS[st] > 0.5).mean()), "S_promotions_total": len(promos), "S_structural_promotions": len(struct_promos),
           "S_removals": sum(1 for x in ev if x[1].startswith("ACTIVE->EVICTED")),
           "S_contribution_rms_rel": float(np.sqrt(np.mean(contrib[st] ** 2)) / (np.std(y[st]) + 1e-12)),
           "coverage_model": float(hit[st].mean())}
    if s:
        ops = quantile_ops(e)
        ph = np.arange(T) % s
        for k, h in ops.items():
            hh = h[st]; per = pd.Series(hh).groupby(ph[st]).mean()
            out[f"cov_{k[:1]}"] = float(hh.mean()); out[f"phase_min_{k[:1]}"] = float(per.min()); out[f"phase_max_{k[:1]}"] = float(per.max())
    return out


if __name__ == "__main__":
    jobs = [("held", t) for t in load051.TASKS] + [("held05", t) for t in load05.TASKS]
    with ProcessPoolExecutor(16) as ex:
        df = pd.DataFrame(list(ex.map(one, jobs, chunksize=1)))
    df.to_csv(os.path.join(HERE, "AUDIT_HELDOUT_TELEMETRY.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(df.round(4).to_string())
