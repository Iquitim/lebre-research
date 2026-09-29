#!/usr/bin/env python3
"""fdr_sim.py — EXT-02 item 1 (PLAN_EXT02.md): empirical false-change control of the FROZEN LEBRE v0.52 (canonical
configuration, imported) on synthetic scenarios with dependence. 7 scenarios x 2 input persistences x 50 seeds.
Output: FDR_SIM_RUNS.csv (one row per run) and FDR_SIM_SUMMARY.csv."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
for p in (ROOT, os.path.join(ROOT, "experiments", "LEBRE-V0.52-PROTO-01"), os.path.join(ROOT, "experiments", "LEBRE-V0.52-EXT-01")):
    sys.path.insert(0, p)

SCEN = ["N1", "N2", "N3", "N4", "P1", "P2", "P3"]
RHOS = [0.5, 0.95]
T, D = 30000, 4
TRUTH = {"N1": set(), "N2": set(), "N3": set(), "N4": set(), "P1": {0}, "P2": {0}, "P3": {0}}
ANY_FALSE = {"N1", "N4"}                      # every accepted change is false there


def ar1(rng, rho, n):
    e = rng.standard_normal(n) * np.sqrt(1 - rho ** 2); z = np.empty(n); z[0] = rng.standard_normal()
    for t in range(1, n):
        z[t] = rho * z[t - 1] + e[t]
    return z


def generate(scen, rho, seed):
    rng = np.random.default_rng(seed)
    f = ar1(rng, rho, T)
    X = np.column_stack([0.7 * f + 0.71 * ar1(rng, rho, T) for _ in range(D)])
    if scen == "P2":
        X[:, 1] = 0.7 * X[:, 0] + 0.71 * ar1(rng, rho, T)
    e = rng.standard_normal(T)
    lag = lambda i, k: np.r_[np.zeros(k), X[:-k, i]]
    if scen in ("N1",):
        y = e
    elif scen == "N2":
        y = np.zeros(T)
        for t in range(1, T):
            y[t] = 0.9 * y[t - 1] + np.sqrt(0.19) * e[t]
    elif scen == "N3":
        y = np.exp(0.5 * X[:, 1]) / np.exp(0.25) * e
    elif scen == "N4":
        y = e * np.where(np.arange(T) < T // 2, 1.0, 2.0)
    elif scen in ("P1", "P2"):
        y = 0.5 * lag(0, 6) + e
    else:
        v = np.zeros(T); h = rng.standard_t(3, size=T) / np.sqrt(3.0)
        for t in range(1, T):
            v[t] = 0.8 * v[t - 1] + 0.6 * h[t]
        y = 0.5 * lag(0, 6) + v
    return X, y


def job(a):
    scen, rho, seed = a
    import comp_dev as C
    import heldout2_cfg as CFG
    from lebre_v052h import LebreV052H
    X, y = generate(scen, rho, seed); Xs = C._scaled_inputs(X)
    m = LebreV052H(d=D, season=None, **dict(CFG.CANONICAL, season2=None))
    for t in range(T):
        m.step(Xs[t], float(y[t]))
    truth = TRUTH[scen]; V = R = S = 0; tp = False; log = []
    for ev in m.events:
        if ev[1] != "accepted":
            continue
        kind, add, rem = ev[2], ev[3], ev[4]
        if kind == "split":
            S += 1; continue
        R += 1; false = False
        if scen in ANY_FALSE:
            false = True
        else:
            if add and add[0] == "in" and add[1] < D and add[1] not in truth:
                false = True
            if rem and rem[0] == "in" and rem[1] < D and rem[1] in truth:
                false = True
        if add and add[0] == "in" and add[1] in truth:
            tp = True
        V += false; log.append((ev[0], kind, str(add), str(rem), false))
    return {"scen": scen, "rho": rho, "seed": seed, "V": V, "R": R, "splits": S, "FDP": V / max(R, 1),
            "found_truth": tp if truth else None, "final": str(sorted(m.active)), "events": str(log), "fp": m.fp_total() / T}


if __name__ == "__main__":
    jobs = [(s, r, 8201 + 1000 * i + 100 * j + k) for i, s in enumerate(SCEN) for j, r in enumerate(RHOS) for k in range(50)]
    with ProcessPoolExecutor(15) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=2)))
    R.to_csv(os.path.join(HERE, "FDR_SIM_RUNS.csv"), index=False)
    from scipy.stats import beta
    rng = np.random.default_rng(8003); rows = []
    for (s, r), g in list(R.groupby(["scen", "rho"])) + [((s, "all"), R[R.scen == s]) for s in SCEN]:
        n = len(g); k = int((g.V > 0).sum())
        lo = float(beta.ppf(0.025, k, n - k + 1)) if k else 0.0; hi = float(beta.ppf(0.975, k + 1, n - k))
        bs = [rng.choice(g.FDP.values, n).mean() for _ in range(2000)]
        rows.append({"scen": s, "rho": r, "n": n, "runs_V>0": k, "frac_V>0": k / n, "cp_lo": lo, "cp_hi": hi,
                     "FDR": float(g.FDP.mean()), "FDR_hi": float(np.percentile(bs, 97.5)), "mean_R": float(g.R.mean()),
                     "found_truth": float(g.found_truth.mean()) if g.found_truth.notna().any() else None,
                     "consistent": bool(g.FDP.mean() <= 0.05 and np.percentile(bs, 97.5) <= 0.10)})
    S = pd.DataFrame(rows); S.to_csv(os.path.join(HERE, "FDR_SIM_SUMMARY.csv"), index=False)
    pd.set_option("display.width", 200); print(S.round(3).to_string(index=False))
    print(R[R.V > 0][["scen", "rho", "seed", "V", "R", "events"]].to_string(index=False))
