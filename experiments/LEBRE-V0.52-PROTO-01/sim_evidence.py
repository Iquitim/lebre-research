"""sim_evidence.py — validity (type-I) and power of the e-process variants of change_engine.Hypothesis, by simulation.
Null at the boundary (conditional mean exactly 0), 5000 steps, crossing of log(1/alpha) = log 20 anywhere on the path.
Increment laws: (a) 'clipped' — difference of clipped squared errors, shape as in the model (d.p. ~0.1), centred;
(b) 'two-point' — worst case for the lower bound, d in {-1, +1/19} with mean 0; (c) 'heavy' — clipped diffs with a large
challenger error (d.p. ~0.3). Power: law (a) shifted by +0.0072 (the mean observed on SS3, DEV_LOG)."""
import math
import numpy as np
from change_engine import Hypothesis

rng = np.random.default_rng(20260927)
N_PATHS, T, LOG_THR = 400, 5000, math.log(20)


def law(kind, n):
    if kind == "two-point":
        return np.where(rng.random(n) < 1 / 20, -1.0, 1 / 19)
    s = 0.3 if kind == "clipped" else 1.2
    e = rng.standard_normal(n); dl = rng.standard_normal(n) * s
    d = np.minimum(e ** 2 / 4, 1) - np.minimum((e - dl) ** 2 / 4, 1)
    return d


def centred(kind):
    big = law(kind, 2_000_000); return big.mean(), big.std()


def run(evidence, kind, shift=0.0):
    mu0, sd0 = centred(kind); cross, times = 0, []
    for _ in range(N_PATHS):
        h = Hypothesis(0.0, 0.05, 1, evidence)
        d = law(kind, T) - mu0 + shift
        hit = None
        for t in range(T):
            h.observe(float(d[t]))
            if t % 10 == 9 and h.log_e() >= LOG_THR:
                hit = t + 1; break
        cross += hit is not None; times.append(hit if hit else np.nan)
    return cross / N_PATHS, np.nanmedian(times) if cross else float("nan"), sd0


if __name__ == "__main__":
    for ev in ("psiE2", "psiE1", "bet", "mix"):
        row = [ev]
        for kind in ("clipped", "two-point", "heavy"):
            p, _, sd = run(ev, kind); row.append(f"{kind}: type-I {p:.3f} (d.p. {sd:.2f})")
        p, tm, _ = run(ev, "clipped", 0.0072)
        row.append(f"POWER +0.0072: {p:.2f}, median time {tm:.0f}")
        print(" | ".join(row), flush=True)
