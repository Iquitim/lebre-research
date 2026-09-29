#!/usr/bin/env python3
"""external_v045.py — Parts 3-5 of PREREG_V045.md.
Part 3: BENCH-04 rerun of LEBRE_V045 (same harness, tasks, seeds; baselines taken from BENCH04_RESULTS.csv) — semi-held-out.
Part 4: HELD-OUT Brazilian series never used (ONS carga S and NE; ONS eolica S; ONS solar SE/CO), V032/V042/V045 +
        persistence, 10 start offsets.  Also BENCH-04 tasks with 10 offsets (semi-held-out).
Part 5: X3 outlier guard (Metro traffic, external_v03), 10 offsets."""
import hashlib
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
B04 = os.path.join(ROOT, "experiments", "LEBRE-V0.4-EXTERNAL-BENCH-04")
for p in (os.path.join(ROOT, "experiments", "LEBRE-V0.3-EXTERNAL-BENCH-02"), os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"),
          os.path.join(ROOT, "data", "external_bench04"), B04, HERE, ROOT):
    sys.path.insert(0, p)
import bench02 as B  # noqa: E402
import load04  # noqa: E402
from experiments.bench01.streams import CausalStandardScaler  # noqa: E402
from lebre_v042 import LebreV042  # noqa: E402
from lebre_v045 import LebreV045  # noqa: E402

OFFSETS = list(range(0, 500, 50))
HELDOUT = {"H1_ONS_Carga_S": lambda: load04._frame_to_task(load04._ons_carga("S"), "carga", 24),
           "H2_ONS_Carga_NE": lambda: load04._frame_to_task(load04._ons_carga("NE"), "carga", 24),
           "H3_ONS_Eolica_S": lambda: load04._frame_to_task(load04._ons_balanco("S"), "gereolica", 24),
           "H4_ONS_Solar_SECO": lambda: load04._frame_to_task(load04._ons_balanco("SE"), "gersolar", 24)}
ARMS = {"V032": lambda d: B.LebreStep(d).m, "V042": lambda d: LebreV042(d=d), "V045": lambda d: LebreV045(d=d)}


def load_any(task):
    if task in HELDOUT:
        X, y, *_ = HELDOUT[task]()
        return X, y
    if task == "X3_MetroTraffic":
        df = pd.read_csv(os.path.join(ROOT, "data", "external_v03", "Metro_Interstate_Traffic_Volume.csv.gz"))
        df["hour"] = pd.to_datetime(df["date_time"]).dt.hour
        return df[["temp", "rain_1h", "snow_1h", "clouds_all", "hour"]].values.astype(float), df["traffic_volume"].values.astype(float)
    X, y, *_ = load04.load(task)
    return X, y


class V045Step(B.Step):
    def __init__(self, d, ts):
        self.m = LebreV045(d=d); self.t = 0; self.ts = ts; self.w = []; self.hit = 0

    def step(self, x, y):
        q = self.m.interval()
        b = sum(self.m.fp.values()); p = self.m.step(np.asarray(x, float), float(y))
        if self.t >= self.ts and np.isfinite(q):
            self.w.append(q); self.hit += int(abs(float(y) - p) <= q)
        self.t += 1
        return p, sum(self.m.fp.values()) - b

    def get_memory_bytes(self):
        return self.m.memory_bytes()


def bench04_one(args):
    task, seed = args
    X, y, _, _, _, _ = load04.load(task); ts = int(0.30 * len(X))
    m = V045Step(X.shape[1], ts); t0 = time.time()
    r = B.R.run_full_stream(m, X, y, ts, is_track_b=True); r.pop("trace", None)
    sd = float(np.std(y[ts:]))
    return {"group": "BR" if task.startswith("BR") else "INTL", "task_id": task, "model_id": "LEBRE_V045", "seed": seed,
            "config": "{}", "T": len(X), "D": X.shape[1], **r, "wall": time.time() - t0,
            "ms_per_step": 1000.0 * (time.time() - t0) / len(X), "coverage": m.hit / max(len(m.w), 1),
            "interval_width_rel": 2.0 * float(np.mean(m.w)) / sd if m.w else float("nan"),
            "n_active_final": len(m.m.active), "n_events": len(m.m.events), "n_quarantined": m.m.n_quarantined}


def offset_one(args):
    task, arm, off = args
    X, y = load_any(task); T = len(X); ts = int(0.30 * T)
    sc = CausalStandardScaler(d=X.shape[1]); e = []
    if arm == "PERSISTENCE":
        yp = None
        for i in range(off, T):
            if i >= ts:
                e.append((y[i] - (yp if yp is not None else 0.0)) ** 2)
            yp = y[i]
    else:
        m = ARMS[arm](X.shape[1])
        for i in range(off, T):
            p = m.step(sc.transform(X[i]), float(y[i])); sc.update(X[i])
            if i >= ts:
                e.append((y[i] - p) ** 2)
    ok = bool(np.all(np.isfinite(e)))
    return {"task_id": task, "arm": arm, "offset": off, "nmse": float(np.mean(e) / (np.var(y[ts:]) + 1e-6)) if ok else np.inf}


def main():
    assert hashlib.sha256(open(os.path.join(HERE, "PREREG_V045.md"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "PREREG_V045_SHA256.txt")).read().split()[0]
    assert hashlib.sha256(open(os.path.join(HERE, "lebre_v045.py"), "rb").read()).hexdigest() == \
        open(os.path.join(HERE, "FREEZE_V045_SHA256.txt")).read().split()[0]
    t0 = time.time()
    with ProcessPoolExecutor(16) as ex:
        b = pd.DataFrame(list(ex.map(bench04_one, [(t, s) for t in load04.TASKS for s in (7611, 7612, 7613)])))
    b.to_csv(os.path.join(HERE, "BENCH04_V045_RESULTS.csv"), index=False)
    print(f"part 3 done {time.time() - t0:.0f}s", flush=True)
    tasks = list(HELDOUT) + list(load04.TASKS) + ["X3_MetroTraffic"]
    jobs = [(t, a, o) for t in tasks for a in list(ARMS) + ["PERSISTENCE"] for o in OFFSETS
            if not (a == "PERSISTENCE" and o > 0)]
    with ProcessPoolExecutor(16) as ex:
        o = pd.DataFrame(list(ex.map(offset_one, jobs, chunksize=2)))
    o.to_csv(os.path.join(HERE, "OFFSETS_V045.csv"), index=False)
    print(f"parts 4-5 done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
