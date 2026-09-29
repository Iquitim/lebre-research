"""diag_ss_gain.py — dev-only diagnosis: how much can the TRUE lag atom improve on the dense base (x_t of all inputs + own past)
on the semi-synthetic tasks? Offline OLS (upper bound for what a challenger can gain), in units of the base's MSE."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import semi_synth as SS

def ols_mse(F, y):
    F = np.column_stack([np.ones(len(y)), F]); b = np.linalg.lstsq(F, y, rcond=None)[0]; return float(np.mean((y - F @ b) ** 2))

X = SS.inputs(); Z = (X - X.mean(0)) / X.std(0); T = len(Z)
lag = lambda v, k: np.r_[np.zeros(k), v[:-k]]
for task in ("SS1", "SS2", "SS3"):
    y = SS.generate(task, 6101, X); ylag = lag(y, 1)
    base = np.column_stack([Z, ylag]); mb = ols_mse(base, y)
    print(task, "var(y)", round(float(np.var(y)), 3), "MSE base", round(mb, 3))
    for k in sorted(SS.TRUTH[task], key=str):
        if k[0] != "lag": continue
        f = lag(Z[:, k[1]], k[2]); m1 = ols_mse(np.column_stack([base, f]), y)
        # what the challenger sees: atom alone on the residual of the base (base NOT refitted)
        Fb = np.column_stack([np.ones(T), base]); r = y - Fb @ np.linalg.lstsq(Fb, y, rcond=None)[0]
        th = f @ r / (f @ f); m2 = float(np.mean((r - th * f) ** 2))
        print(f"   {k}: joint refit gain {100*(1-m1/mb):5.2f}%   atom-on-residual gain {100*(1-m2/mb):5.2f}%   corr(f, x_t) {np.corrcoef(f, Z[:, k[1]])[0,1]:.3f}")
    allf = np.column_stack([base] + [lag(Z[:, k[1]], k[2]) for k in SS.TRUTH[task] if k[0] == "lag"])
    print("   all true lags jointly:", round(100 * (1 - ols_mse(allf, y) / mb), 2), "%   noise floor gain:", round(100 * (1 - 1 / mb), 2), "%")
