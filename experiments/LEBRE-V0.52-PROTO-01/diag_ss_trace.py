"""diag_ss_trace.py — dev-only: trace experiments on the TRUE keys of semi-synthetic tasks (n, mean delta, theta, log_e)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, semi_synth as SS
from lebre_v052 import LebreV052
task = sys.argv[1]
X = SS.inputs(); y = SS.generate(task, 6101, X); Xs = C._scaled_inputs(X)
m = LebreV052(d=X.shape[1], chal=(sys.argv[2] if len(sys.argv) > 2 else "nlms"), screen_norm=(sys.argv[3] if len(sys.argv) > 3 else "analytic")); truth = SS.TRUTH[task]; opened = {}
orig = m.engine.review
def review():
    for ex in m.engine.slots:
        opened.setdefault(ex.add_key, 0)
    out = orig()
    for dec, ex, le in out:
        if ex.add_key in truth:
            print(f"t={m.t:6d} {dec:8s} {ex.add_key} n={ex.n} meanδ={ex.S/max(ex.n,1):+.4f} eps={ex.eps} θ={ex.theta:+.3f} w={getattr(ex,'w',None)} sigr={m.sigr:.3f} log_e={le:.2f} thr={ex.hyp.log_thr:.2f}")
    return out
m.engine.review = review
for t in range(len(y)):
    m.step(Xs[t], float(y[t]))
print("distinct add keys opened:", len(opened), "; true keys ever opened:", [k for k in truth if k in opened])
print("final screen rank of true keys:")
sc = {k: abs(m.screen[k]) / np.sqrt(m.design_power(k)) for k in m.cands}
rk = sorted(sc, key=sc.get, reverse=True)
for k in truth:
    if k in sc: print("  ", k, "rank", rk.index(k) + 1, "of", len(rk))
print("top5:", rk[:5])
