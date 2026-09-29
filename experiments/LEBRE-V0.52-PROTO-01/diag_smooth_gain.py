"""diag_smooth_gain.py — dev-only: identifiability of a smooth-input lag. Offline OLS on the whole series:
gain (% of the base MSE) of adding input i's block (octave-band means + the true lag + x_i(t) re-fit) on top of the
base (bias + current value of all inputs + y_{t-1}), for y = 0.6 x_i(t-k) + e, several i and k. Dev seed 7101."""
import numpy as np, semi_synth as SS
BANDS = ((1, 1), (2, 3), (4, 7), (8, 15), (16, 31))
X = SS.inputs(); Z = (X - X.mean(0)) / X.std(0); T = len(Z); rng = np.random.default_rng(7101)
lag = lambda v, k: np.r_[np.zeros(k), v[:-k]]
def mse(F, y):
    F = np.column_stack([np.ones(len(y)), F]); b = np.linalg.lstsq(F, y, rcond=None)[0]; return float(np.mean((y - F @ b) ** 2))
ac = lambda v, k: float(np.corrcoef(v[k:], v[:-k])[0, 1])
print("i  k  autocorr(x_i,k)  gain_block%  gain_oracle_lag%  (n* samples, rough)")
for i in (1, 2, 3, 4):
    for k in (2, 5, 9, 16, 25):
        y = 0.6 * lag(Z[:, i], k) + rng.standard_normal(T)
        base = np.column_stack([Z, lag(y, 1)]); mb = mse(base, y)
        blk = np.column_stack([np.mean([lag(Z[:, i], j) for j in range(lo, hi + 1)], axis=0) for lo, hi in BANDS])
        g = 100 * (1 - mse(np.column_stack([base, blk, lag(Z[:, i], k)]), y) / mb)
        go = 100 * (1 - mse(np.column_stack([base, lag(Z[:, i], k)]), y) / mb)
        # rough evidence samples for a relative MSE gain g (clipped-loss units ~ g/4 per sample, sd ~ 0.1): n ~ 2*6.3*0.01/(g/400)^2
        n = 2 * 6.3 * 0.01 / (g / 400) ** 2 if g > 0 else float("inf")
        print(f"{i}  {k:2d}  {ac(Z[:, i], k):.3f}           {g:6.2f}       {go:6.2f}           {n:8.0f}")
