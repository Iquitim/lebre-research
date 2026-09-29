"""equiv_test.py — DEVELOPMENT-ONLY equivalence test of the C port against the frozen Python LEBRE v0.52 (canonical
configuration). For every development series: forecasts and accepted structural changes of (a) the frozen Python,
(b) the C port in double precision (checks the LOGIC of the port), (c) the C port in single precision (the
microcontroller build: effect of float32). The same causally scaled inputs feed all three.
Reported: max |difference| / s.d.(y), relative NMSE difference on the test region, and whether the accepted-change
sequences (time, kind, keys) are identical."""
import ctypes
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROTO = os.path.abspath(os.path.join(HERE, "..", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, PROTO); sys.path.insert(0, HERE)
import heldout2_cfg as CFG  # noqa: E402
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402

KIND = {"add": 0, "swap": 1, "rem": 2, "split": 3}


def key_c(k):
    if k is None:
        return (0, 0, 0, 0)
    if k[0] == "in":
        return (1, k[1], 0, 0)
    if k[0] == "res":
        return (2, 0, 0, 0)
    return (3, k[1], k[2], k[3])


def run_c(dll, Xs, y, q, season, season2):
    lib = ctypes.CDLL(os.path.join(HERE, "lebre_c", dll))
    T, dx = Xs.shape
    X = np.ascontiguousarray(Xs, dtype=np.float64); yy = np.ascontiguousarray(y, dtype=np.float64)
    qq = np.ascontiguousarray(q, dtype=np.int32); out = np.zeros(T); ev = np.zeros(8 * 512, dtype=np.int32); cl = ctypes.c_long(0)
    lib.lebre052_run.restype = ctypes.c_int
    n = lib.lebre052_run(ctypes.c_int(T), ctypes.c_int(dx), ctypes.c_int(season or 0), ctypes.c_int(season2 or 0),
                         X.ctypes.data_as(ctypes.c_void_p), yy.ctypes.data_as(ctypes.c_void_p), qq.ctypes.data_as(ctypes.c_void_p),
                         out.ctypes.data_as(ctypes.c_void_p), ev.ctypes.data_as(ctypes.c_void_p), ctypes.c_int(512), ctypes.byref(cl))
    if n < 0:
        return out, None, -n
    evs = [(int(e[0]), int(e[1]), tuple(int(v) for v in e[2:6]), (int(e[6]), int(e[7]), 0, 0) if e[6] else (0, 0, 0, 0))
           for e in ev[:8 * n].reshape(-1, 8)]
    return out, evs, 0


def job(task):
    from lebre_v052h import LebreV052H
    d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
    s2 = 168 if task.startswith("bdg2") else None
    kw = dict(CFG.CANONICAL); kw["season2"] = s2
    m = LebreV052H(d=X.shape[1], season=s, **kw)
    py = np.array([m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])) for t in range(len(y))])
    ev_py = [(e[0], KIND[e[2]], key_c(e[3]), key_c(e[4])[:2] + (0, 0) if e[4] else (0, 0, 0, 0))
             for e in m.events if e[1] == "accepted"]
    ev_py = [(t, k, a, (r[0], r[1], 0, 0)) for t, k, a, r in ev_py]
    out = {"task": task, "T": len(y), "n_acc_py": len(ev_py)}
    ts = int(0.3 * len(y)); ok = np.isfinite(y); ok[:ts] = False; sd = float(np.nanstd(y)) or 1.0
    nm = lambda p: float(np.mean((y[ok] - p[ok]) ** 2) / np.var(y[ok]))
    out["nmse_py"] = nm(py)
    for tag, dll in (("f64", "lebre052_f64.dll"), ("f32", "lebre052_f32.dll")):
        pc, evc, ov = run_c(dll, Xs, np.where(np.isfinite(y), y, np.nan), qu.astype(int), s, s2)
        out[f"maxdiff_{tag}"] = float(np.nanmax(np.abs(pc - py)) / sd)
        out[f"nmse_{tag}"] = nm(pc); out[f"rel_nmse_{tag}"] = out[f"nmse_{tag}"] / out["nmse_py"] - 1
        out[f"events_equal_{tag}"] = evc == ev_py; out[f"n_acc_{tag}"] = len(evc) if evc is not None else -1
        out[f"overflow_{tag}"] = ov
        if evc != ev_py:
            out[f"first_diff_{tag}"] = str(next(((a, b) for a, b in zip(ev_py + [None] * 9, (evc or []) + [None] * 9) if a != b), None))
    return out


if __name__ == "__main__":
    tasks = sys.argv[1:] or D.dev_tasks()
    with ProcessPoolExecutor(min(15, len(tasks))) as ex:
        R = pd.DataFrame(list(ex.map(job, tasks, chunksize=1)))
    R.to_csv(os.path.join(HERE, "EQUIV_TEST.csv"), index=False)
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
    cols = ["task", "n_acc_py", "events_equal_f64", "maxdiff_f64", "rel_nmse_f64", "events_equal_f32", "n_acc_f32", "maxdiff_f32", "rel_nmse_f32"]
    print(R[cols].to_string(index=False))
    for tag in ("f64", "f32"):
        print(f"{tag}: identical event sequences {int(R[f'events_equal_{tag}'].sum())}/{len(R)}; |rel NMSE diff| median "
              f"{R[f'rel_nmse_{tag}'].abs().median():.2e}, max {R[f'rel_nmse_{tag}'].abs().max():.2e}; overflow {int((R[f'overflow_{tag}'] > 0).sum())}")
    for c in [c for c in R.columns if c.startswith("first_diff")]:
        print(R[["task", c]].dropna().to_string(index=False))
