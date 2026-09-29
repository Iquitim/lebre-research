#!/usr/bin/env python3
"""deterministic_audits.py — Phases F (H5 exposure), L (NLMS epsilon), M (memory scaling), N (quantile cadence).
Uses the authoritative v0.51 classes unchanged; operator comparisons are re-implemented side by side for analysis only."""
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import forensic_runs as F  # noqa: E402  (verifies frozen hashes)
from lebre_v051 import LebreV051, MemoryExpert  # noqa: E402
from lebre_s051 import StructuralExpert  # noqa: E402


# ------------------------------------------------------------------ F: H5 exposure / utility-removal hazard on T1
def h5_one(seed):
    F.check_frozen()
    X, y = F.generate("T1", seed)
    m = LebreV051(d=5, season=None); S = m.S
    active_steps = 0; spells = []; cur = None; key = ("lag", 1, 3)
    for t in range(len(y)):
        m.step(X[t], float(y[t]))
        on = key in F.struct_set(S)
        if on:
            active_steps += 1
            cur = t if cur is None else cur
        elif cur is not None:
            spells.append((cur, t)); cur = None
    if cur is not None:
        spells.append((cur, len(y)))
    rems = [e for e in S.events if e[1].startswith("ACTIVE->EVICTED") and e[2] == S.label(("lag", 1, 3))]
    gaps = [spells[i + 1][0] - spells[i][1] for i in range(len(spells) - 1)]
    return {"seed": seed, "active_steps": active_steps, "promotion_spells": len(spells), "removals": len(rems),
            "mean_gap_to_rediscovery": float(np.mean(gaps)) if gaps else np.nan, "rediscovered_after_removal": len(gaps)}


# ------------------------------------------------------------------ L: NLMS epsilon stress (memory expert alone)
def nlms_case(name, y, s):
    m = MemoryExpert(s); e = []; wmax = 0.0
    for t in range(len(y)):
        p = m.predict(); m.update(float(y[t]), p); e.append(y[t] - p); wmax = max(wmax, float(np.max(np.abs(m.w))) if len(m.w) else 0.0)
    e = np.array(e[len(e) // 3:]); v = np.var(y[len(y) // 3:])
    return {"case": name, "season": s, "nmse": float(np.mean(e ** 2) / v) if v > 0 else float(np.mean(e ** 2)),
            "mse": float(np.mean(e ** 2)), "max_abs_w": wmax, "finite": bool(np.all(np.isfinite(e)))}


def nlms_audit():
    rng = np.random.RandomState(9201); T = 20000; t = np.arange(T)
    base = 100 + 10 * np.sin(2 * np.pi * t / 24) + np.cumsum(rng.normal(size=T)) * 0.1 + rng.normal(size=T)
    rows = []
    for sc in (1e-6, 1.0, 1e6):
        rows.append(nlms_case(f"scaled x{sc:g}", base * sc, 24))
    rows.append(nlms_case("constant", np.full(T, 5.0), 24))
    near = 5.0 + 1e-9 * rng.normal(size=T); rows.append(nlms_case("near-constant (1e-9 noise)", near, 24))
    # plateaus then jumps (quantised signal): recent increments exactly zero while the target moves
    q = np.round(np.cumsum(rng.normal(size=T)) * 0.2); rows.append(nlms_case("quantised random walk (plateaus)", q, None))
    q2 = np.round(base / 5.0) * 5.0; rows.append(nlms_case("quantised seasonal (plateaus)", q2, 24))
    step = np.r_[np.zeros(T // 2), np.ones(T // 2) * 10.0] + 1e-12 * rng.normal(size=T); rows.append(nlms_case("flat then step", step, None))
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ M: memory scaling (code formula, float32 accounting)
def memory_audit():
    rows = []
    for d in (1, 5, 6):
        for s in (None, 24, 48, 144, 1440, 10080):
            m = LebreV051(d=d, season=s)
            Sb = m.S.memory_bytes()
            Mb = 4 * (m.M.Lb + (m.M.s or 0) + len(m.M.w) + 6)
            rows.append({"d": d, "s": s if s else "none", "S_bytes": Sb, "M_buffer_floats": m.M.Lb, "M_profile_floats": (m.M.s or 0),
                         "M_bytes": Mb, "total_bytes_code_formula": m.memory_bytes(),
                         "python_float64_equivalent_bytes": 2 * m.memory_bytes()})
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ N: quantile cadence (operators on periodic heteroscedastic residuals)
def quantile_ops(e, every=8, alpha=0.1, gamma=0.1, lam=0.99):
    """A: code operator (indicator of the refresh step only, step x every); B: all indicators of the block accumulated;
    C: every step. sigma = sqrt(EMA of e^2), refreshed at the same cadence as in the code."""
    out = {}
    for kind in ("A_code_current_indicator_x8", "B_accumulated_8_indicators", "C_every_step"):
        q = None; e2 = None; sig = None; acc = 0.0; hits = np.zeros(len(e), bool)
        for t, v in enumerate(e):
            e2 = v * v if e2 is None else e2 + (1 - lam) * (v * v - e2)
            refresh = (t % every == 0) or sig is None
            if refresh or kind == "C_every_step":
                sig = math.sqrt(max(e2, 1e-300))
            if q is None:
                q = 1.645 * sig
            miss = 1.0 if abs(v) > q else 0.0
            hits[t] = miss == 0.0
            if kind == "C_every_step":
                q = max(0.0, q + gamma * sig * (miss - alpha))
            elif kind == "B_accumulated_8_indicators":
                acc += miss - alpha
                if refresh:
                    q = max(0.0, q + gamma * sig * acc); acc = 0.0
            elif refresh:
                q = max(0.0, q + every * gamma * sig * (miss - alpha))
        out[kind] = hits
    return out


def cadence_audit():
    rows = []
    for s in (24, 48, 144, 25):
        for amp in (0.8,):
            rng = np.random.RandomState(9300 + s); T = 200 * s
            ph = np.arange(T) % s
            sd = 1 + amp * np.sin(2 * np.pi * ph / s + 0.7)
            e = sd * rng.normal(size=T)
            hs = quantile_ops(e)
            for k, h in hs.items():
                hh = h[T // 5:]; pp = ph[T // 5:]
                per = pd.Series(hh).groupby(pp).mean()
                rows.append({"s": s, "operator": k, "coverage": float(hh.mean()), "phase_cov_min": float(per.min()),
                             "phase_cov_max": float(per.max()), "phases_observed_by_refresh": len(set(np.arange(0, T, 8) % s))})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    F.check_frozen()
    with ProcessPoolExecutor(10) as ex:
        h5 = pd.DataFrame(list(ex.map(h5_one, F.SEEDS)))
    h5.to_csv(os.path.join(HERE, "AUDIT_H5_EXPOSURE.csv"), index=False)
    nl = nlms_audit(); nl.to_csv(os.path.join(HERE, "AUDIT_NLMS_EPSILON.csv"), index=False)
    mm = memory_audit(); mm.to_csv(os.path.join(HERE, "AUDIT_MEMORY_SCALING.csv"), index=False)
    qc = cadence_audit(); qc.to_csv(os.path.join(HERE, "AUDIT_QUANTILE_CADENCE.csv"), index=False)
    pd.set_option("display.width", 220)
    print(h5.to_string()); print(h5.sum(numeric_only=True).to_string())
    print(nl.to_string()); print(mm.to_string()); print(qc.round(4).to_string())
