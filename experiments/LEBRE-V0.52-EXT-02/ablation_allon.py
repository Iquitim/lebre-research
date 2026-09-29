#!/usr/bin/env python3
"""ablation_allon.py — EXT-02 item 2 (PLAN_EXT02.md), EXPLORATORY: the frozen canonical LEBRE v0.52 with all_on=True
(every unit active from the start, no experiments) on the already-consumed reserves 2 (40 series) and 3 (60 series).
Compared with the canonical predictions saved by the pre-registered runs, on the same test mask (last 70%, observed
target, finite for LEBRE, ALL_ON and NLinear). Output: ABL_ALLON_RUNS.csv, ABL_ALLON_SUMMARY.csv."""
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
E = os.path.join(ROOT, "experiments")
for p in (ROOT, os.path.join(E, "LEBRE-V0.52-PROTO-01"), os.path.join(E, "LEBRE-V0.52-EXT-01")):
    sys.path.insert(0, p)
RES = {"r2": (os.path.join(E, "LEBRE-V0.52-HELDOUT-02"), "RESERVA2.json", "V052_CORRIGIDA"),
       "r3": (os.path.join(E, "LEBRE-V0.52-HELDOUT-03"), "RESERVA3.json", "V052_PY")}


def fname(folder, task):
    return os.path.join(folder, "preds", task.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")


def job(a):
    res, task = a
    import comp_dev as C
    import data_v052 as D
    import heldout2_cfg as CFG
    from lebre_v052h import LebreV052H
    folder, _, key = RES[res]
    d = D.load(task, final=True)          # consumed reserve, exploratory run (PLAN_EXT02.md §2)
    X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    s2 = 168 if task.startswith("bdg2") else None
    m = LebreV052H(d=X.shape[1], season=s, **dict(CFG.CANONICAL, season2=s2, all_on=True))
    p = np.empty(len(y))
    for t in range(len(y)):
        p[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
    Z = np.load(fname(folder, task)); yz = Z["y"]
    assert np.array_equal(np.isfinite(yz), np.isfinite(y)) and np.allclose(yz[np.isfinite(yz)], y[np.isfinite(y)])
    ts = int(0.3 * len(y)); msk = np.isfinite(y); msk[:ts] = False
    msk &= np.isfinite(Z[key]) & np.isfinite(p) & np.isfinite(Z["NLINEAR_ONLINE"])
    nl = float(np.mean((y[msk] - Z["NLINEAR_ONLINE"][msk]) ** 2))
    return {"res": res, "task": task, "group": task.split(":")[0], "LEBRE": float(np.mean((y[msk] - Z[key][msk]) ** 2)) / nl,
            "ALL_ON": float(np.mean((y[msk] - p[msk]) ** 2)) / nl, "fp_allon": m.fp_total() / len(y), "n_active": len(m.active)}


if __name__ == "__main__":
    jobs = []
    for res, (folder, js, _) in RES.items():
        R = json.load(open(os.path.join(folder, js), encoding="utf-8"))
        jobs += [(res, f"camels:{g}") for g in R["camels_br"]] + [(res, f"bdg2:{m}") for m in R["bdg2"]]
    with ProcessPoolExecutor(15) as ex:
        df = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    df.to_csv(os.path.join(HERE, "ABL_ALLON_RUNS.csv"), index=False)
    rng = np.random.default_rng(8003); rows = []
    for res, g in list(df.groupby("res")) + [("r2+r3", df)]:
        dd = np.log(g.LEBRE) - np.log(g.ALL_ON); gi = [np.flatnonzero((g.res + g.group).values == k) for k in np.unique(g.res + g.group)]
        bs = [np.exp(dd.values[np.concatenate([rng.choice(ix, len(ix)) for ix in gi])].mean()) for _ in range(2000)]
        rows.append({"res": res, "n": len(g), "LEBRE_gm": float(np.exp(np.log(g.LEBRE).mean())), "ALL_ON_gm": float(np.exp(np.log(g.ALL_ON).mean())),
                     "ratio": float(np.exp(dd.mean())), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
                     "LEBRE_wins": int((dd < 0).sum()), "ALL_ON_share>1.5": float((g.ALL_ON > 1.5).mean()), "ALL_ON_cat": int((g.ALL_ON > 10).sum()),
                     "fp_allon": float(g.fp_allon.mean())})
    S = pd.DataFrame(rows); S.to_csv(os.path.join(HERE, "ABL_ALLON_SUMMARY.csv"), index=False)
    pd.set_option("display.width", 200); print(S.round(3).to_string(index=False))
