#!/usr/bin/env python3
"""run_dev.py — prequential evaluation of the v0.52 prototype on DEVELOPMENT data only.

Models: v0.51 (frozen code, imported read-only), M only (v0.52 memory), v0.52 option I, v0.52 option II.
Inputs are standardised causally (same scaler as the v0.51 harness) for real data; synthetic tasks are already standardised.
Metric: NMSE on the last 70% of steps with an observed target; FP/step; structural events.
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
V51 = os.path.join(ROOT, "experiments", "LEBRE-V0.51-LEAN-01")
FOR = os.path.join(ROOT, "experiments", "LEBRE-V0.51-EXTERNAL-CRITIQUE-FORENSIC-INVESTIGATION-01")
for p in (HERE, V51, FOR, ROOT):
    sys.path.insert(0, p)
from lebre_v052 import LebreV052, Memory  # noqa: E402

TEST_FRAC = 0.30


def synth(task, seed, T=20000):
    import forensic_runs as F
    X, y = F.generate(task, seed)
    return {"X": X[:T], "y": y[:T], "quarantine": np.zeros(min(T, len(y)), bool), "season": None, "task": f"synth:{task}:{seed}"}


def run_model(kind, data, **kw):
    from experiments.bench01.streams import CausalStandardScaler
    X, y, qu, s = data["X"], data["y"], data["quarantine"], data["season"]
    T, d = X.shape
    scale = not data["task"].startswith("synth")
    sc = CausalStandardScaler(d=d) if scale else None
    pred = np.full(T, np.nan)
    t0 = time.time()
    if kind == "v051":
        from lebre_v051 import LebreV051
        m = LebreV051(d=d, season=s)
    elif kind == "M":
        m = Memory(s)
    else:
        m = LebreV052(d=d, season=s, option=kind.split("-")[1], **kw)
    for t in range(T):
        xs = sc.transform(X[t]) if scale else X[t]
        yt = y[t]
        if kind == "v051":
            if np.isfinite(yt) and not qu[t]:
                pred[t] = m.step(xs, float(yt))
        elif kind == "M":
            p = m.predict(); pred[t] = p; m.update(yt if np.isfinite(yt) else None, p, learn=np.isfinite(yt) and not qu[t])
        else:
            pred[t] = m.step(xs, float(yt) if np.isfinite(yt) else None, quarantine=bool(qu[t]))
        if scale:
            sc.update(X[t])
    ts = int(TEST_FRAC * T)
    ok = np.isfinite(y[ts:]) & np.isfinite(pred[ts:])
    e = y[ts:][ok] - pred[ts:][ok]
    nmse = float(np.mean(e ** 2) / np.var(y[ts:][ok]))
    out = {"task": data["task"], "model": kind, "nmse": nmse, "sec": round(time.time() - t0, 1)}
    if kind.startswith("v052"):
        out.update(fp=m.fp_total() / T, n_active=len(m.active), structure=str(m.structure()), coverage=m.coverage(),
                   accepted=sum(1 for e in m.events if e[1] == "accepted"), experiments=m.k_started,
                   events=str([e for e in m.events if e[1] == "accepted"][:12]))
    return out


def job(args):
    kind, loader, key = args
    data = loader(key)
    return run_model(kind, data)


# structural truth of the synthetic tasks, in v0.52 keys (B3: z_t = 0.8 z_{t-1} + x0_t + w_t, so the drive is x0 low-passed
# with pole 0.8 plus the current x0 in the dense base, and the w-part is a residual latent state with pole 0.8)
TRUTH = {"N1": set(), "N2": set(), "T1": {("lag", 1, 3)}, "B1": {("lag", 1, 12)},
         "B2": {("lag", 0, 3), ("lag", 2, 7), ("lag", 4, 20)}, "B3": {("lag", 3, 12), ("lp", 0, 0.8), ("res", 0.8)}}


def synth_job(args):
    kind, task, seed = args
    import lebre_v052
    data = synth(task, seed)
    r = run_model(kind, data)
    if kind.startswith("v052"):
        ev = [e for e in eval(r["events"]) if e[1] == "accepted"] if r["events"] != "[]" else []
        truth = TRUTH[task]
        false_add = sum(1 for e in ev if e[3] is not None and e[3] not in truth)
        false_rem = sum(1 for e in ev if e[4] is not None and e[4] in truth and e[3] is None)
        final = set(eval(r["structure"]))
        r.update(false_changes=false_add + false_rem, true_found=len(final & truth), n_truth=len(truth),
                 exact_final=int(final == truth),
                 first_true_t=min([e[0] for e in ev if e[3] in truth], default=None))
    return r


def real_job(args):
    kind, task = args
    import data_v052 as D
    return run_model(kind, D.load(task))


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if mode == "dev":
        kinds = ["v051", "M", "v052-IIb"]
        sj = [(k, t, s) for t in TRUTH for s in (9101, 9102, 9103, 9104, 9105) for k in kinds]
        import data_v052 as D
        rj = [(k, t) for t in D.dev_tasks() for k in kinds]
        with ProcessPoolExecutor(14) as ex:
            S = pd.DataFrame(list(ex.map(synth_job, sj, chunksize=1)))
            S.to_csv(os.path.join(HERE, "DEV_SYNTH.csv"), index=False)
            R = pd.DataFrame(list(ex.map(real_job, rj, chunksize=1)))
            R.to_csv(os.path.join(HERE, "DEV_REAL.csv"), index=False)
        print("done")
    if mode == "smoke":
        jobs = [(k, lambda a: synth(*a), a) for a in [("N1", 9101), ("T1", 9101)] for k in ("v052-I", "v052-II")]
        for j in jobs:
            r = job(j); print({k: r[k] for k in r if k != "events"}); print("   ", r.get("events"))
