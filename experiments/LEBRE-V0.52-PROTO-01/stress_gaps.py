"""stress_gaps.py — dev-only stress test of the target-gap fix (27/09/2026).
On the 29 real DEVELOPMENT series, the target is erased (NaN) in four artificial gaps inside the test region
(lengths 24, 100, 400, 1500 steps, starting at 35%, 50%, 65%, 80% of the series); inputs are kept. Configurations:
FROZEN (the held-out configuration), HOLD (gap_hold), HOLD_CLIP (gap_hold + out_contract). Scenarios: 'gaps' and 'none'
(the original series, to measure the cost of the fix where nothing is injected).
Per run: NMSE on the observed test points, explosion flags (|forecast| beyond 10 x the observed range, or NMSE > 1.5 x
the same configuration without injected gaps), max |forecast| / observed range, clipped steps."""
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
import final7 as F7  # noqa: E402

CFGS = {"FROZEN": {}, "HOLD": dict(gap_hold=True), "HOLD_CLIP": dict(gap_hold=True, out_contract=True)}
GAPS = [(0.35, 24), (0.50, 100), (0.65, 400), (0.80, 1500)]


def job(a):
    task, scen, cfg = a
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"].copy(), d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    T = len(y); gap = np.zeros(T, bool)
    if scen == "gaps":
        for frac, L in GAPS:
            a0 = int(frac * T); gap[a0:min(T, a0 + L)] = True
        y[gap] = np.nan
    kw = dict(F7.PADRAO, **CFGS[cfg])
    if task.startswith("bdg2"):
        kw["season2"] = 168
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pred = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(T)])
    ts = int(0.3 * T); ok = np.isfinite(y) & np.isfinite(pred); ok[:ts] = False
    yo = d["y"][np.isfinite(d["y"])]; rng_ = float(yo.max() - yo.min()) or 1.0
    return {"task": task, "scen": scen, "cfg": cfg, "nmse": float(np.mean((y[ok] - pred[ok]) ** 2) / np.var(y[ok])),
            "max_dev_over_range": float(np.nanmax(np.abs(pred[ts:] - np.nanmedian(yo))) / rng_),
            "nonfinite": int((~np.isfinite(pred)).sum()), "clipped": getattr(m, "n_clipped", 0), "fp": m.fp_total() / T}


if __name__ == "__main__":
    tasks = D.dev_tasks()
    jobs = [(t, sc, c) for t in tasks for sc in ("gaps", "none") for c in CFGS]
    with ProcessPoolExecutor(15) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    base = R[R.scen == "none"].set_index(["task", "cfg"]).nmse
    R["ratio_vs_nogap"] = [r.nmse / base[(r.task, r.cfg)] for r in R.itertuples()]
    R["explode"] = (R.max_dev_over_range > 10) | (R.ratio_vs_nogap > 1.5) | (R.nonfinite > 0)
    R.to_csv(os.path.join(HERE, "STRESS_GAPS.csv"), index=False)
    pd.set_option("display.width", 220)
    g = R.groupby(["scen", "cfg"])
    print(pd.DataFrame({"explosions": g.explode.sum(), "max_dev/range (max)": g.max_dev_over_range.max().round(2),
                        "nmse_gmean": g.nmse.apply(lambda v: float(np.exp(np.log(v).mean()))).round(4),
                        "clipped_steps": g.clipped.sum(), "fp": g.fp.mean().round(0)}))
    print(R[R["explode"]][["task", "scen", "cfg", "nmse", "ratio_vs_nogap", "max_dev_over_range"]].round(3).to_string(index=False))
    w = R[R.scen == "none"].pivot_table(index="task", columns="cfg", values="nmse")
    print("no injected gaps — HOLD_CLIP / FROZEN nmse: gmean", round(float(np.exp(np.log(w.HOLD_CLIP / w.FROZEN).mean())), 4),
          "max", round(float((w.HOLD_CLIP / w.FROZEN).max()), 4), "min", round(float((w.HOLD_CLIP / w.FROZEN).min()), 4))
