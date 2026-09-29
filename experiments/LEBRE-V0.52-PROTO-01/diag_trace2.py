"""diag_trace2.py — dev-only trace of one input unit on y = c * x_i(t-k) + e (real inputs): screen statistic over time
(vs the opening threshold and the best other unit), every episode of the unit (warm-up, evidence, peak chosen, end)."""
import os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, semi_synth as SS, final6 as F6  # noqa: E402
from lebre_v052h import LebreV052H  # noqa: E402
i, k, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]); kw = dict(F6.PADRAO, **(eval(sys.argv[4]) if len(sys.argv) > 4 else {}))
X = SS.inputs(); Z = (X - X.mean(0)) / X.std(0); rng = np.random.default_rng(seed)
y = 0.6 * np.r_[np.zeros(k), Z[:-k, i]] + rng.standard_normal(len(Z)); Xs = C._scaled_inputs(X)
m = LebreV052H(d=X.shape[1], **kw); U = ("in", i); eps = []; st = []
orig = m.engine.review
def review():
    out = orig()
    for dec, ex, le in out:
        if ex.add_key == U:
            eps.append((ex.t0, m.t, ex.n, round(ex.S, 2), round(le, 2), getattr(ex, "kstar", None), dec))
    return out
m.engine.review = review
for t in range(len(y)):
    m.step(Xs[t], float(y[t]))
    if t % 2000 == 1999:
        others = [(round(m.screen_stat(u), 1), u) for u in m.units if u != U and u not in m.active]
        st.append((t + 1, round(m.screen_stat(U), 1), max(others) if others else None, U in m.active))
print(f"x{i} lag {k} seed {seed}; screen threshold {m.screen_q}")
print("screen (t, stat unit, best other, active):"); [print("  ", s) for s in st]
print("episodes (t0, end, evidence n, sum, log_e, peak, end):"); [print("  ", e) for e in eps]
print("final structure", m.structure(), "events", [e[:4] for e in m.events if e[1] == "accepted"])
