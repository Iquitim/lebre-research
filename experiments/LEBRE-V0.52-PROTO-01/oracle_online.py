"""oracle_online.py — dev-only limit check: the best an online, anytime-valid test can do. Reference S = RLS on the base
(bias + current inputs + y_{t-1}); oracle challenger = RLS on base + the TRUE lagged input x_i(t-k); both from t = 0,
no forgetting, never closed. Evidence = psiE1 e-process on clipped loss differences (B = 2 sigma, eps = 0.002), threshold
log(2P/alpha) = log(14/0.05) = 5.63 (P = 7 units, first hypothesis level). Reports the crossing time, dev seeds."""
import sys, math
import numpy as np
import semi_synth as SS, comp_dev as C
from change_engine import Hypothesis
X = SS.inputs(); Z = (X - X.mean(0)) / X.std(0); Xs = C._scaled_inputs(X); T = len(Z)


class RLS:
    def __init__(self, n):
        self.w = np.zeros(n); self.P = 10 * np.eye(n)
    def pred(self, f):
        return float(self.w @ f)
    def upd(self, f, y):
        Pf = self.P @ f; k = Pf / (1 + f @ Pf); self.w += k * (y - self.w @ f); self.P -= np.outer(k, Pf)


for i, k in [(2, 9), (2, 16), (2, 5), (1, 12), (4, 20)]:
    out = []
    for seed in (7102, 7103, 7104):
        rng = np.random.default_rng(seed); y = 0.6 * np.r_[np.zeros(k), Z[:-k, i]] + rng.standard_normal(T)
        d = X.shape[1]; S = RLS(d + 2); G = RLS(d + 3); h = Hypothesis(0.002, 0.05 / 14, 1, "psiE1"); e2 = 1.0; hit = None
        for t in range(40, T):
            base = np.concatenate(([1.0], Xs[t], [y[t - 1]])); f = np.append(base, Xs[t - k, i])
            ps, pg = S.pred(base), G.pred(f); B = 2 * math.sqrt(e2)
            if t > 240:
                h.observe(min((y[t] - ps) ** 2 / B ** 2, 1) - min((y[t] - pg) ** 2 / B ** 2, 1) - 0.002)
                if hit is None and h.log_e() >= h.log_thr:
                    hit = t
            e2 += 0.01 * ((y[t] - ps) ** 2 - e2); S.upd(base, y[t]); G.upd(f, y[t])
        out.append(hit)
    print(f"x{i} lag {k}: oracle crossing times {out}  (threshold {h.log_thr:.2f})", flush=True)
