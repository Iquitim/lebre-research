#!/usr/bin/env python3
"""
verify_properties.py — empirical verification of the claims made for frozen LEBRE v0.3 (iter4).
Seeds 5031..5230 (verified unused). Model file is verified against FREEZE_ITER4_SHA256.txt.
Outputs: PROPERTY_TESTS.csv and printed summary.
"""
import copy
import hashlib
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)
MODEL = os.environ.get("LEBRE_MODEL", "v03")
if MODEL == "v045":
    sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.45-ROBUST-GUARD-01"))
    from lebre_v045 import LebreV045 as LebreV03  # noqa: E402
elif MODEL == "v042":
    sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"))
    from lebre_v042 import LebreV042 as LebreV03  # noqa: E402
elif MODEL == "v041":
    sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"))
    from lebre_v041 import LebreV041 as LebreV03  # noqa: E402
elif MODEL == "v04":
    sys.path.insert(0, os.path.join(ROOT, "experiments", "LEBRE-V0.4-PROMOTION-01"))
    from lebre_v04 import LebreV04 as LebreV03  # noqa: E402
elif MODEL == "v032":
    from lebre_v032 import LebreV032 as LebreV03  # noqa: E402
elif MODEL == "v031":
    from lebre_v031 import LebreV031 as LebreV03  # noqa: E402
else:
    from lebre_v03 import LebreV03  # noqa: E402
from scratch.bench_v02_integration import generate_v02_stream  # noqa: E402

SEEDS = list(range(5031, 5231))
W = np.array([0.8, -0.6, 0.4, -0.3, 0.2])


def run(model, X, y):
    yh = np.empty(len(y))
    for t in range(len(y)):
        yh[t] = model.step(X[t], float(y[t]))
    return yh


def lag_keys(m):
    return {a["key"][1:] for a in m.active if a["key"][0] == "lag"}


# ---------------------------------------------------------------- T1 causality
def t1(seed):
    X, y, _ = generate_v02_stream("I9_Hybrid_Delay_Plus_Latent_State", seed=seed)
    y2 = y.copy(); X2 = X.copy()
    t0 = 3000
    y2[t0:] += 5.0; X2[t0 + 1:] += 3.0
    a, b = run(LebreV03(), X, y), run(LebreV03(), X2, y2)
    return {"test": "T1_causality", "seed": seed,
            "max_abs_diff_upto_t0": float(np.max(np.abs(a[: t0 + 1] - b[: t0 + 1]))),
            "diff_after": float(np.max(np.abs(a[t0 + 1:] - b[t0 + 1:])))}


# ---------------------------------------------------------------- T2 lag alignment
def t2(args):
    seed, i, k = args
    rng = np.random.RandomState(seed)
    X = rng.normal(size=(6000, 5))
    y = X @ W + 0.1 * rng.normal(size=6000)
    y[k:] += 0.8 * X[:-k, i]
    m = LebreV03(); run(m, X, y)
    return {"test": "T2_lag_alignment", "seed": seed, "true": f"({i},{k})",
            "found": str(sorted(lag_keys(m))), "exact": lag_keys(m) == {(i, k)},
            "latent": any(a["key"][0] != "lag" for a in m.active)}


# ---------------------------------------------------------------- T3 type-I (null: no structure)
def t3(args):
    seed, noise = args
    rng = np.random.RandomState(seed)
    X = rng.normal(size=(6000, 5))
    if noise == "gauss":
        eps = 0.4 * rng.normal(size=6000)
    elif noise == "student_t3":
        eps = 0.4 * rng.standard_t(3, size=6000) / math.sqrt(3.0)
    else:  # heteroscedastic: variance jumps x9 on alternate blocks of 500
        eps = 0.4 * rng.normal(size=6000) * np.where((np.arange(6000) // 500) % 2 == 0, 1.0, 3.0)
    y = X @ W + eps
    m = LebreV03(); run(m, X, y)
    promos = [e for e in m.events if e[1] == "PROVISIONAL->ACTIVE"]
    episodes = m.n_provisional + m.n_futility  # lower bound on test episodes opened (lag + restarts)
    return {"test": "T3_type_I", "seed": seed, "noise": noise, "false_promotions": len(promos),
            "lag_episodes_opened": m.n_provisional, "futility_restarts": m.n_futility,
            "bound_expected_false": (m.n_provisional + m.n_futility + len(m.poles)) * 0.05 / m.p_dict}


# ---------------------------------------------------------------- T4 false eviction (ARL)
def t4(seed):
    rng = np.random.RandomState(seed)
    T = 30000
    X = rng.normal(size=(T, 5))
    y = X @ W + 0.4 * rng.normal(size=T)
    y[6:] += 0.85 * X[:-6, 1]
    m = LebreV03(); run(m, X, y)
    ev = [e for e in m.events if "EVICTED" in e[1] and "x1 atrasado 6" in e[2]]
    first = next((e[0] for e in m.events if e[1] == "PROVISIONAL->ACTIVE" and "x1 atrasado 6" in e[2]), None)
    return {"test": "T4_false_eviction", "seed": seed, "steps_monitored": (T - first) if first else 0,
            "false_evictions": len(ev), "t_first_promotion": first}


# ---------------------------------------------------------------- T5 Kalman optimality of latent pathway
def kalman_pred_mse(a, b, c, q, r):
    # z_t = a z_{t-1} + b x_t + nu (var q); y_t = w x_t + c z_t + e (var r). One-step predictor of y_t given
    # past y, past and current x: error var = c^2 P_pred + r, P_pred from steady-state Riccati.
    P = 1.0
    for _ in range(10000):
        Pp = a * a * P + q
        K = Pp * c / (c * c * Pp + r)
        P = (1 - K * c) * Pp
    Pp = a * a * P + q
    return c * c * Pp + r


def t5(seed):
    X, y, _ = generate_v02_stream("I6_Continuous_Latent_State", seed=seed)
    m = LebreV03(); yh = run(m, X, y)
    mse = float(np.mean((y[3000:] - yh[3000:]) ** 2))
    opt = kalman_pred_mse(0.88, 0.40, 0.90, 0.1 ** 2, 0.4 ** 2)
    return {"test": "T5_kalman", "seed": seed, "mse_last3000": mse, "kalman_optimal_mse": opt,
            "excess_ratio": mse / opt,
            "pole_selected": next((a["key"][1] for a in m.active if a["key"][0] == "res"), None)}


# ---------------------------------------------------------------- T6 quiescent retention (I7)
class Probe(LebreV03):
    pass


def t6(seed):
    X, y, _ = generate_v02_stream("I7_Quiescent_Continuous_State", seed=seed)
    m = LebreV03(); lat = {}
    for t in range(6000):
        m.step(X[t], float(y[t]))
        if t in (1999, 3999):
            lat[t] = m.latent_atom() is not None
    ev_in_silence = [e for e in m.events if 2000 <= e[0] < 4000]
    return {"test": "T6_quiescence", "seed": seed, "latent_at_1999": lat[1999], "latent_at_3999": lat[3999],
            "lifecycle_events_during_silence": len(ev_in_silence)}


# ---------------------------------------------------------------- T7 scale invariance / robustness
def t7(seed):
    X, y, _ = generate_v02_stream("I9_Hybrid_Delay_Plus_Latent_State", seed=seed)
    out = {"test": "T7_scale", "seed": seed}
    for s in (1e-3, 1.0, 1e3):
        m = LebreV03(); yh = run(m, X, s * y)
        out[f"nmse_scale_{s:g}"] = float(np.mean((s * y - yh) ** 2) / np.var(s * y))
        out[f"promos_scale_{s:g}"] = sum(1 for e in m.events if e[1] == "PROVISIONAL->ACTIVE")
    m = LebreV03()
    yh = run(m, np.zeros((3000, 5)), np.zeros(3000))
    out["zero_stream_finite"] = bool(np.all(np.isfinite(yh))) and math.isfinite(m.sigma2)
    out["zero_stream_sigma2"] = m.sigma2
    return out


# ---------------------------------------------------------------- T8 hidden-cost accounting
def t8(seed):
    X, y, _ = generate_v02_stream("I4_Multi_Sparse_Delay", seed=seed)
    m = LebreV03()
    n_sorts = 0
    orig = m._decide

    def counted():
        nonlocal n_sorts
        before = m.n_provisional
        orig()
        if m.n_provisional > before:          # a refill (full ranking of the dictionary) happened
            n_sorts += 1
    m._decide = counted
    run(m, X, y)
    n = len(m.lag_cands)
    cmp_per_sort = n * math.log2(n)
    return {"test": "T8_hidden_cost", "seed": seed, "fp_per_step": sum(m.fp.values()) / 6000,
            "sorts": n_sorts, "est_float_compares_per_step_from_sorts": n_sorts * cmp_per_sort / 6000,
            "log_calls_per_step": m.transcendental / 6000}


def main():
    want = open(os.path.join(HERE, "FREEZE_ITER4_SHA256.txt")).read().split()[0]
    if MODEL == "v03":
        assert hashlib.sha256(open(os.path.join(HERE, "lebre_v03.py"), "rb").read()).hexdigest() == want
    jobs = []
    jobs += [(t1, s) for s in SEEDS[:10]]
    jobs += [(t2, (s, i, k)) for j, s in enumerate(SEEDS[:30]) for (i, k) in [((j % 5), (1, 7, 32)[j % 3])]]
    jobs += [(t3, (s, n)) for s in SEEDS for n in ("gauss",)]
    jobs += [(t3, (s, n)) for s in SEEDS[:100] for n in ("student_t3", "hetero")]
    jobs += [(t4, s) for s in SEEDS[:40]]
    jobs += [(t5, s) for s in SEEDS[:30]]
    jobs += [(t6, s) for s in SEEDS[:30]]
    jobs += [(t7, s) for s in SEEDS[:10]]
    jobs += [(t8, s) for s in SEEDS[:5]]
    with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 4)) as ex:
        rows = list(ex.map(_call, jobs, chunksize=2))
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(HERE, "PROPERTY_TESTS.csv" if MODEL == "v03" else f"PROPERTY_TESTS_{MODEL}.csv"), index=False)
    pd.set_option("display.width", 220)
    for name, g in df.groupby("test"):
        print("=" * 20, name)
        print(g.dropna(axis=1, how="all").drop(columns=["test"]).describe(include="all").T
              .iloc[:, :7].to_string())


def _call(job):
    f, a = job
    return f(a)


if __name__ == "__main__":
    main()
