#!/usr/bin/env python3
"""heldout3_run.py — PRE-REGISTERED single run on RESERVA 3 (RESERVA3.json: 30 CAMELS-BR basins + 30 BDG2 meters never
used). See PREREG_V052_RESERVA3.md. Frozen models; protocols of the development comparison.
  V052_PY   frozen LEBRE v0.52, canonical configuration (Python)
  V052_C32  the C99 port of the same configuration in single precision (host build of the microcontroller code)
  budget    V051, NLINEAR_ONLINE, DLINEAR_ONLINE, HOLT_WINTERS, ARX_NLMS, LASSO_ONLINE, FITS, SPARSETSF
  refs      AIRLINE_X (SARIMAX with inputs), ARX_RLS_PLS; TTM and Chronos-2 in heldout3_ttm_chronos.py"""
import json
import os
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-EXT-01"))
PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO); sys.path.insert(0, EXT)
import heldout2_cfg as CFG  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402
import equiv_test as EQ  # noqa: E402
import strong_baselines as SB  # noqa: E402

OUT = os.path.join(HERE, "preds")
ONLINE = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "ARX_NLMS"]


def tasks():
    R = json.load(open(os.path.join(HERE, "RESERVA3.json"), encoding="utf-8"))
    return [f"camels:{g}" for g in R["camels_br"]] + [f"bdg2:{m}" for m in R["bdg2"]]


def fname(task):
    return os.path.join(OUT, task.replace(":", "__").replace("/", "_").replace(" ", "_") + ".npz")


def job(task):
    f = fname(task)
    if os.path.exists(f):
        return task, "skipped"
    try:
        import torch
        torch.set_num_threads(1)
        import ultralight as UL
        from lebre_v052h import LebreV052H
        t0 = time.time()
        d = D.load(task, final=True)
        X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
        s2 = 168 if task.startswith("bdg2") else None
        preds, info = {}, {}
        m = LebreV052H(d=X.shape[1], season=s, **dict(CFG.CANONICAL, season2=s2))
        c = np.empty(len(y)); prev = 0.0; p = np.empty(len(y))
        for t in range(len(y)):
            p[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t]))
            tot = m.fp_total(); c[t] = tot - prev; prev = tot
        preds["V052_PY"] = p
        ev_py = [(e[0], EQ.KIND[e[2]], EQ.key_c(e[3]), (EQ.key_c(e[4])[0], EQ.key_c(e[4])[1], 0, 0) if e[4] else (0, 0, 0, 0))
                 for e in m.events if e[1] == "accepted"]
        info["V052_PY"] = {"fp": m.fp_total() / len(y), "fp_p999": float(np.percentile(c, 99.9)), "fp_max": float(c.max()),
                           "structure": str(m.structure()), "n_accepted": len(ev_py), "coverage": m.coverage(), "clipped": int(m.n_clipped)}
        pc, evc, ov = EQ.run_c("lebre052_f32.dll", Xs, np.where(np.isfinite(y), y, np.nan), qu.astype(int), s, s2)
        preds["V052_C32"] = pc
        info["V052_C32"] = {"events_equal": evc == ev_py, "n_accepted": len(evc) if evc is not None else -1, "overflow": ov}
        p, fp = C.run_lebre("v051", X, Xs, y, qu, s); preds["V051"] = p; info["V051"] = {"fp": fp}
        for mid in ONLINE:
            cfg = C.calibrate(mid, Xs, y, s); p, fp, ok = C.run_online(mid, Xs, y, s, cfg, 0)
            preds[mid] = p; info[mid] = {"fp": fp, "ok": ok, "cfg": cfg}
        idx = C._calib_n(y); best, bm = None, float("inf")
        for mu in (0.01, 0.05, 0.2):
            for lam in (1e-4, 1e-3, 1e-2):
                pl, _, okc = SB.run(SB.LassoOnline(X.shape[1], mu, lam), Xs[idx], y[idx])
                mm = float(np.nanmean((y[idx] - pl) ** 2)) if okc else float("inf")
                if mm < bm:
                    best, bm = (mu, lam), mm
        p, fp, ok = SB.run(SB.LassoOnline(X.shape[1], *best), Xs, y); preds["LASSO_ONLINE"] = p
        info["LASSO_ONLINE"] = {"fp": fp, "ok": ok, "cfg": best}
        ul = UL.run(task, y, idx)
        for k, v in ul.items():
            preds[k] = v[0]; info[k] = {"fp": v[1], "params": v[2]}
        p, ok, inf = C.run_airline_x(y, Xs, s); preds["AIRLINE_X"] = p; info["AIRLINE_X"] = {"ok": ok, "info": inf}
        p, fp, ok = SB.run(SB.ArxRlsPls(X.shape[1]), Xs, y); preds["ARX_RLS_PLS"] = p; info["ARX_RLS_PLS"] = {"fp": fp, "ok": ok}
        np.savez_compressed(f, y=y, gapfrac=np.array(float(np.mean(~np.isfinite(y)))), **preds)
        with open(f.replace(".npz", ".json"), "w", encoding="utf-8") as fh:
            json.dump({"task": task, "T": len(y), "d": int(X.shape[1]), "season": s, "sec": round(time.time() - t0), "info": info}, fh, default=str)
        return task, f"ok {round(time.time() - t0)}s"
    except Exception:
        return task, "ERROR " + traceback.format_exc()[-800:]


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    ts = tasks(); print(len(ts), "series (reserve 3)", flush=True)
    with ProcessPoolExecutor(15) as ex:
        for task, st in ex.map(job, ts, chunksize=1):
            print(task, st, flush=True)
