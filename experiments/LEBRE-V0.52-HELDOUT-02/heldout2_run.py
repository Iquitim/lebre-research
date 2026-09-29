#!/usr/bin/env python3
"""heldout2_run.py — PRE-REGISTERED single run on RESERVA 2 (RESERVA2.json: 20 CAMELS-BR basins + 20 BDG2 meters never
used). See PREREG_V052_RESERVA2.md. Models are frozen; protocols are those of the development comparison.
  V052_CORRIGIDA  measurement-#7 configuration + gap fix (gap_hold, out_contract) — the candidate
  V052_CONGELADA  the configuration evaluated on the first reserve (no gap fix) — to measure the fix on new data
  budget class    V051, NLINEAR_ONLINE, DLINEAR_ONLINE, HOLT_WINTERS, ARX_NLMS, LASSO_ONLINE
  references      AIRLINE_X (SARIMAX with inputs), ARX_RLS_PLS; Chronos-2 with covariates in heldout2_chronos.py"""
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
V052 = {"V052_CORRIGIDA": dict(F7.PADRAO, gap_hold=True, out_contract=True), "V052_CONGELADA": dict(F7.PADRAO)}
ONLINE = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "ARX_NLMS"]


def tasks():
    R = json.load(open(os.path.join(HERE, "RESERVA2.json"), encoding="utf-8"))
    return [f"camels:{g}" for g in R["camels_br"]] + [f"bdg2:{m}" for m in R["bdg2"]]


def fname(task):
    return os.path.join(OUT, task.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")


def run_v052(task, X, Xs, y, qu, s, kw):
    from lebre_v052h import LebreV052H
    kw = dict(kw)
    if task.startswith("bdg2"):
        kw["season2"] = 168
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    pred = np.empty(len(y)); c = np.empty(len(y)); prev = 0.0
    for t in range(len(y)):
        pred[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
        tot = m.fp_total(); c[t] = tot - prev; prev = tot
    return pred, {"fp": m.fp_total() / len(y), "p999": float(np.percentile(c, 99.9)), "max": float(c.max()),
                  "structure": str(m.structure()), "accepted": str([(e[0], e[2], e[3]) for e in m.events if e[1] == "accepted"]),
                  "groups": str({str(u): sorted(m.equivalents(u)) for u in m.active if u[0] == "in"}),
                  "coverage": m.coverage(), "clipped": getattr(m, "n_clipped", 0)}


def job(task):
    f = fname(task)
    if os.path.exists(f):
        return task, "skipped"
    try:
        t0 = time.time()
        d = D.load(task, final=True)
        X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
        preds, info = {}, {}
        for name, kw in V052.items():
            preds[name], info[name] = run_v052(task, X, Xs, y, qu, s, kw)
        p, fp = C.run_lebre("v051", X, Xs, y, qu, s); preds["V051"] = p; info["V051"] = {"fp": fp}
        for mid in ONLINE:
            cfg = C.calibrate(mid, Xs, y, s); p, fp, ok = C.run_online(mid, Xs, y, s, cfg, 0)
            preds[mid] = p; info[mid] = {"fp": fp, "ok": ok, "cfg": cfg}
        idx = C._calib_n(y); best, bm = None, float("inf")
        for mu in (0.01, 0.05, 0.2):
            for lam in (1e-4, 1e-3, 1e-2):
                pc, _, okc = SB.run(SB.LassoOnline(X.shape[1], mu, lam), Xs[idx], y[idx])
                mm = float(np.nanmean((y[idx] - pc) ** 2)) if okc else float("inf")
                if mm < bm:
                    best, bm = (mu, lam), mm
        p, fp, ok = SB.run(SB.LassoOnline(X.shape[1], *best), Xs, y); preds["LASSO_ONLINE"] = p
        info["LASSO_ONLINE"] = {"fp": fp, "ok": ok, "cfg": best}
        p, ok, inf = C.run_airline_x(y, Xs, s); preds["AIRLINE_X"] = p; info["AIRLINE_X"] = {"ok": ok, "info": inf}
        p, fp, ok = SB.run(SB.ArxRlsPls(X.shape[1]), Xs, y); preds["ARX_RLS_PLS"] = p; info["ARX_RLS_PLS"] = {"fp": fp, "ok": ok}
        np.savez_compressed(f, y=y, gapfrac=np.array(float(np.mean(~np.isfinite(y)))), **preds)
        with open(f.replace(".npz", ".json"), "w", encoding="utf-8") as fh:
            json.dump({"task": task, "T": len(y), "d": int(X.shape[1]), "season": s, "sec": round(time.time() - t0),
                       "info": info}, fh, default=str)
        return task, f"ok {round(time.time() - t0)}s"
    except Exception:
        return task, "ERROR " + traceback.format_exc()[-600:]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ts = tasks(); print(len(ts), "series (reserve 2)", flush=True)
    with ProcessPoolExecutor(15) as ex:
        for task, st in ex.map(job, ts, chunksize=1):
            print(task, st, flush=True)
