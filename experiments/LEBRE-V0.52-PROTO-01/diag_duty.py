"""diag_duty.py — dev-only diagnosis (no model change): how much of the time is the TRUE input actually under test?
Frozen lebre_v052h on the development semi-synthetic SS3 (seed 6101; true input x3 accepted late, at t = 11290).
Records every episode of the true unit (start, end, warm-up samples, evidence samples, sum, log_e, how it ended) and the
per-sample evidence increments, from which the theoretical number of evidence samples n* = 2 log_thr sigma^2 / mu^2 is
estimated (drift approximation, ignores the mixture's penalty: a lower bound)."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C  # noqa: E402
import semi_synth as SS  # noqa: E402
from lebre_v052h import LebreV052H  # noqa: E402

TASK, SEED, UNIT = sys.argv[1] if len(sys.argv) > 1 else "SS3", int(sys.argv[2]) if len(sys.argv) > 2 else 6101, ("in", 3)
if len(sys.argv) > 3:
    UNIT = ("in", int(sys.argv[3]))

X = SS.inputs(); y = SS.generate(TASK, SEED, X); Xs = C._scaled_inputs(X)
m = LebreV052H(d=X.shape[1])
episodes, incs, busy_by = [], [], {}

orig_open, orig_review = m.engine.open, m.engine.review


def open_(kind, add_key, rem_key, hkey, eps, t):
    ex = orig_open(kind, add_key, rem_key, hkey, eps, t)
    if add_key == UNIT:
        obs = ex.observe
        def observe(d, ex=ex, obs=obs):
            incs.append(d); obs(d)
        ex.observe = observe
    return ex


def review():
    before = {id(ex): ex for ex in m.engine.slots}
    out = orig_review()
    for dec, ex, le in out:
        if ex.add_key == UNIT:
            episodes.append({"start": ex.t0, "end": m.t, "warm": min(getattr(ex, "k", 0), m.chal_warm), "evidence_n": ex.n,
                             "sum": round(ex.S, 3), "log_e": round(le, 2), "thr": round(ex.hyp.log_thr, 2), "end_reason": dec,
                             "peak": getattr(ex, "kstar", None)})
    return out


m.engine.open, m.engine.review = open_, review
occupancy = []                                   # what occupies the slots, sampled every 10 steps
for t in range(len(y)):
    m.step(Xs[t], float(y[t]))
    if t % 10 == 0:
        occupancy.append(tuple(sorted(str(ex.add_key or ex.rem_key) for ex in m.engine.slots)))
    if UNIT in m.active:
        t_acc = t; break
else:
    t_acc = None
for ev in m.events:                              # episodes of the unit stopped because another change was accepted
    if ev[1] == "superseded" and ev[3] == UNIT:
        episodes.append({"start": None, "end": ev[0], "warm": None, "evidence_n": ev[6], "sum": None, "log_e": None,
                         "thr": None, "end_reason": "superseded", "peak": None})

E = pd.DataFrame(episodes).sort_values("end")
pd.set_option("display.width", 200)
print(f"{TASK} seed {SEED}, unit {UNIT}: accepted at t = {t_acc}")
print(E.to_string(index=False))
T = t_acc if t_acc is not None else len(y)
tested = float((E.end - E.start).fillna(0).sum()); ev_n = int(E.evidence_n.sum())
print(f"\nsteps elapsed until acceptance: {T}")
print(f"steps with the unit in a slot: {tested:.0f}  ({100 * tested / T:.1f}% of the time)")
print(f"evidence samples: {ev_n}  ({100 * ev_n / T:.1f}% of the time); warm-up samples: {int(E.warm.fillna(0).sum())}")
d = np.array(incs)
if len(d) > 10:
    mu, sd = d.mean(), d.std(); thr = float(E.thr.dropna().iloc[-1])
    n_star = 2 * thr * sd ** 2 / mu ** 2 if mu > 0 else float("inf")
    print(f"evidence increments: mean {mu:+.5f}  sd {sd:.4f}  (n = {len(d)})")
    print(f"theoretical evidence samples n* ~ 2*{thr:.2f}*sd^2/mu^2 = {n_star:.0f}")
    if n_star < float("inf") and ev_n:
        print(f"predicted time to acceptance at the observed fraction: n*/(fraction) = {n_star / (ev_n / T):.0f} steps (observed {T})")
occ = pd.Series(occupancy[: T // 10])
share = {}
for o in occ:
    for k in o:
        share[k] = share.get(k, 0) + 1
print("\nslot occupancy until acceptance (% of samples, per key):")
for k, v in sorted(share.items(), key=lambda kv: -kv[1]):
    print(f"   {k:28s} {100 * v / len(occ):5.1f}%")
print(f"   empty slots: {100 * sum(2 - len(o) for o in occ) / (2 * len(occ)):.1f}% of slot-time")
