#!/usr/bin/env python3
"""heldout_run.py — PRE-REGISTERED single run of the frozen LEBRE v0.52 and all comparators on the HELD-OUT series of
SPLIT_V052.json (45 ONS plants on 10 rivers other than the development one, 50 CAMELS-BR basins, 30 BDG2 meters).
See PREREG_V052_HELDOUT.md. No model is changed; protocols are exactly those of the development comparison.

Per series and model the prediction array is saved (preds/<series>.npz) with the mean FP/step; the v0.52 COMPLETA run
also records the per-step cost (p99.9 and max) and its structural events. Series are processed in parallel; a series
already saved is skipped (resumable after an infrastructure crash only)."""
import json
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
import final7 as F7  # noqa: E402
import strong_baselines as SB  # noqa: E402

OUT = os.path.join(HERE, "preds")
COMPLETA = dict(F7.PADRAO)                  # frozen configuration of measurement #7
VARIANTS = {"V052_COMPLETA": {}, "V052_SEM_DIVISOES": dict(splits=False), "V052_TUDO_LIGADO": dict(all_on=True),
            "V052_TUDO_LIGADO_RLS": dict(all_on=True, rls_live=True)}
ONLINE = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "RIVER_AMRULES", "ARX_NLMS"]


def heldout_tasks():
    S = D.SPLIT
    return ([f"ons:{x['target']}" for x in S["ons"]["held_out"]] + [f"camels:{g}" for g in S["camels_br"]["held_out"]]
            + [f"bdg2:{m}" for m in S["bdg2"]["held_out"]])


def fname(task):
    return os.path.join(OUT, task.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")


def run_v052h(task, X, Xs, y, qu, s, extra, profile=False):
    from lebre_v052h import LebreV052H
    kw = dict(COMPLETA, **extra)
    if task.startswith("bdg2"):
        kw["season2"] = 168                                          # hourly buildings: the week, declared like the day
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pred = np.empty(len(y)); c = np.empty(len(y)) if profile else None; prev = 0.0
    for t in range(len(y)):
        pred[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
        if profile:
            tot = m.fp_total(); c[t] = tot - prev; prev = tot
    info = {"fp": m.fp_total() / len(y), "structure": str(m.structure()),
            "accepted": str([(e[0], e[2], e[3]) for e in m.events if e[1] == "accepted"]),
            "groups": str({str(u): sorted(m.equivalents(u)) for u in m.active if u[0] == "in"}), "coverage": m.coverage()}
    if profile:
        info.update(p999=float(np.percentile(c, 99.9)), max=float(c.max()))
    return pred, info


def job(task):
    f = fname(task)
    if os.path.exists(f):
        return task, "skipped"
    try:
        t0 = time.time()
        d = D.load(task, final=True)
        X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
        preds, info = {}, {}
        for name, extra in VARIANTS.items():
            preds[name], info[name] = run_v052h(task, X, Xs, y, qu, s, extra, profile=(name == "V052_COMPLETA"))
        for kind, name in (("v052", "V052_ATOMICA"), ("v051", "V051"), ("M", "SO_MEMORIA_V051")):
            p, fp = C.run_lebre(kind, X, Xs, y, qu, s); preds[name] = p; info[name] = {"fp": fp}
        from abl_analysis import memory_only                         # memory expert alone, weekly cycle on buildings
        p, fp = memory_only(task, y, s); preds["SO_MEMORIA"] = p; info["SO_MEMORIA"] = {"fp": fp}
        p, ok, inf = C.run_airline(y, s); preds["AIRLINE"] = p; info["AIRLINE"] = {"ok": ok, "info": inf}
        p, ok, inf = C.run_airline_x(y, Xs, s); preds["AIRLINE_X"] = p; info["AIRLINE_X"] = {"ok": ok, "info": inf}
        for mid in ONLINE:
            cfg = C.calibrate(mid, Xs, y, s); p, fp, ok = C.run_online(mid, Xs, y, s, cfg, 0)
            preds[mid] = p; info[mid] = {"fp": fp, "ok": ok, "cfg": cfg}
        p, fp, ok = SB.run(SB.ArxRlsPls(X.shape[1]), Xs, y); preds["ARX_RLS_PLS"] = p; info["ARX_RLS_PLS"] = {"fp": fp, "ok": ok}
        idx = C._calib_n(y); best, bm = None, float("inf")
        for mu in (0.01, 0.05, 0.2):
            for lam in (1e-4, 1e-3, 1e-2):
                pc, _, okc = SB.run(SB.LassoOnline(X.shape[1], mu, lam), Xs[idx], y[idx])
                mm = float(np.nanmean((y[idx] - pc) ** 2)) if okc else float("inf")
                if mm < bm:
                    best, bm = (mu, lam), mm
        p, fp, ok = SB.run(SB.LassoOnline(X.shape[1], *best), Xs, y); preds["LASSO_ONLINE"] = p
        info["LASSO_ONLINE"] = {"fp": fp, "ok": ok, "cfg": best}
        np.savez_compressed(f, y=y, d=np.array(X.shape[1]), **preds)
        with open(f.replace(".npz", ".json"), "w", encoding="utf-8") as fh:
            json.dump({"task": task, "T": len(y), "d": int(X.shape[1]), "season": s, "sec": round(time.time() - t0),
                       "info": info}, fh, default=str)
        return task, f"ok {round(time.time() - t0)}s"
    except Exception:
        return task, "ERROR " + traceback.format_exc()[-600:]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    tasks = heldout_tasks()
    print(len(tasks), "held-out series", flush=True)
    with ProcessPoolExecutor(15) as ex:
        for task, st in ex.map(job, tasks, chunksize=1):
            print(task, st, flush=True)
