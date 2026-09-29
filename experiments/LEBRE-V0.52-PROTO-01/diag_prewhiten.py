"""diag_prewhiten.py — dev-only: does Box-Jenkins prewhitening rank the TRUE lags first on the semi-synthetics?
Rank of each true (input, lag) among all 5 x 32 by |cross-correlation|: raw residual screen vs prewhitened (AR(8) per input)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import semi_synth as SS

def ar_filter(v, p=8):
    V = np.column_stack([np.r_[np.zeros(k), v[:-k]] for k in range(1, p + 1)])
    a = np.linalg.lstsq(V[p:], v[p:], rcond=None)[0]
    return lambda u: u - np.column_stack([np.r_[np.zeros(k), u[:-k]] for k in range(1, p + 1)]) @ a

X = SS.inputs(); Z = (X - X.mean(0)) / X.std(0)
lag = lambda v, k: np.r_[np.zeros(k), v[:-k]]
for task in ("SS1", "SS2", "SS3"):
    y = SS.generate(task, 6101, X); yc = y - y.mean()
    raw, pw = {}, {}
    for i in range(5):
        f = ar_filter(Z[:, i]); xi = f(Z[:, i]); yi = f(yc)
        for k in range(1, 33):
            raw[(i, k)] = abs(np.corrcoef(lag(Z[:, i], k)[40:], yc[40:])[0, 1])
            pw[(i, k)] = abs(np.corrcoef(lag(xi, k)[40:], yi[40:])[0, 1])
    rr = sorted(raw, key=raw.get, reverse=True); rp = sorted(pw, key=pw.get, reverse=True)
    print(task, "top5 prewhitened:", rp[:5])
    for k in SS.TRUTH[task]:
        if k[0] == "lag":
            print(f"   true {k[1:]}: rank raw {rr.index(k[1:]) + 1:3d}/160   rank prewhitened {rp.index(k[1:]) + 1:3d}/160")
