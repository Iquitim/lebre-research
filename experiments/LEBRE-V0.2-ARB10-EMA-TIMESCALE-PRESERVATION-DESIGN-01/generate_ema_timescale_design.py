#!/usr/bin/env python3
"""
generate_ema_timescale_design.py

Deterministic design + audit generator for:
LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01

NO STOCHASTIC STREAMS ARE GENERATED OR EXECUTED BY THIS SCRIPT.
It only:
  - hashes parent artifacts (Phase A);
  - verifies the pole-matching algebra (Phases B, C);
  - replays SEALED EMA telemetry from trans_windows_cache.json (Phase D);
  - scans the repository for seed usage (Phase F11);
  - asserts the future B2/B3 single-intervention invariant (Phase F7).

Pre-declared D7 decision rule (fixed before first execution of this script):
  For I11 and I12, for each K5 arm with telemetry (A0, A1), compute
    R = mean|MEOE_max| over POST_EARLY blocks / mean|MEOE_max| over PRE blocks
  where MEOE_max is the block-wise max over the available gains {G_D|B, G_R|B},
  PRE = blocks ending at step_count 2910..3000, POST_EARLY = 3010..3100.
  SUPPORTED_DIAGNOSTICALLY  if R >= 2.0 in all four (task, arm) cells;
  NOT_SUPPORTED             if R <  2.0 in all four cells;
  MIXED                     otherwise.
  Scope: single seed (1971), 10 blocks per window. Descriptive only.
"""

import hashlib
import json
import math
import os
import re

import numpy as np
import pandas as pd
import sympy as sp

STAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(STAGE_DIR, "..", ".."))
EXP = os.path.join(ROOT, "experiments")
SEAL = os.path.join(EXP, "LEBRE-V0.2-K2-ARB10-COMPOSITION-SEAL-AUDIT-01")
COMP = os.path.join(EXP, "LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01")


def out(name):
    return os.path.join(STAGE_DIR, name)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ----------------------------------------------------------------------
# PHASE A — parent hashes
# ----------------------------------------------------------------------
def phase_a():
    targets = []
    for d in (SEAL, COMP):
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if os.path.isfile(p):
                targets.append(p)
    for rel in ("scratch/run_v02_correlation_search_compaction.py",
                "scratch/bench_v02_integration.py",
                "scratch/run_v02_corrective_confirmation.py"):
        targets.append(os.path.join(ROOT, rel))
    lines = ["# SHA-256 of parent artifacts consulted by "
             "LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01",
             "# format: sha256  size_bytes  repo_relative_path"]
    for p in targets:
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        lines.append(f"{sha256(p)}  {os.path.getsize(p)}  {rel}")
    with open(out("PARENT_HASHES.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    # Cross-check: the seal's own manifest hashes must still match on disk.
    man = json.load(open(os.path.join(SEAL, "K2_ARB10_SEAL_AUDIT_MANIFEST.json")))
    drift = []
    for fn, meta in man.items():
        p = os.path.join(SEAL, fn)
        now = sha256(p) if os.path.exists(p) else "MISSING"
        if now != meta["sha256"]:
            drift.append((fn, meta["sha256"], now))
    return len(targets), drift


# ----------------------------------------------------------------------
# PHASE B — pole equivalence
# ----------------------------------------------------------------------
def phase_b():
    a5 = 0.02
    q5 = 1.0 - a5
    q10 = q5 ** (10 / 5)
    a10 = 1.0 - q10
    q10_b2 = q5  # B2 keeps alpha=.02 at K=10

    def row(label, K, alpha):
        q = 1.0 - alpha
        tau_ev = -1.0 / math.log(q)
        hl_ev = math.log(0.5) / math.log(q)
        n_eff = (2.0 - alpha) / alpha              # 1 / sum(w^2), iid inputs
        mean_age = K * q / (1.0 - q)               # centre of mass of weights (stream steps)
        return {
            "config": label, "K_arb": K, "alpha": alpha, "q_event": q,
            "q_per_stream_step": q ** (1.0 / K),
            "tau_events": tau_ev, "tau_stream_steps": K * tau_ev,
            "half_life_events": hl_ev, "half_life_stream_steps": K * hl_ev,
            "settling_3tau_stream_steps": 3 * K * tau_ev,
            "weight_centre_of_mass_age_stream_steps": mean_age,
            "effective_samples_iid": n_eff,
            "stationary_var_factor_iid": alpha / (2.0 - alpha),
            "evidence_samples_per_tau_stream": (K * tau_ev) / K,
        }

    rows = [row("K5_alpha_0.020000 (B0/B1 reference)", 5, a5),
            row("K10_alpha_0.020000 (B2 negative control)", 10, a5),
            row("K10_alpha_0.039600 (B3 pole-preserved)", 10, a10)]
    df = pd.DataFrame(rows)
    df.to_csv(out("EMA_OPERATING_POINT_COMPARISON.csv"), index=False, float_format="%.9f")

    ref, b3 = rows[0], rows[2]
    tol = 1e-9
    checks = [
        ("B1_alpha5", a5, 0.02, abs(a5 - 0.02) < 1e-15),
        ("B1_q5", q5, 0.98, abs(q5 - 0.98) < 1e-15),
        ("B2_tau_event_5", ref["tau_events"], 49.498316, abs(ref["tau_events"] - 49.498316) < 5e-7),
        ("B2_tau_stream_5", ref["tau_stream_steps"], 247.491582, abs(ref["tau_stream_steps"] - 247.491582) < 5e-7),
        ("B3_q10", q10, 0.9604, abs(q10 - 0.9604) < 1e-12),
        ("B4_alpha10", a10, 0.0396, abs(a10 - 0.0396) < 1e-12),
        ("B4_alpha10_exact_repr", a10, 0.0396,
         f"{a10!r} vs float literal 0.0396 = {0.0396!r}; abs diff {abs(a10-0.0396):.3e}"),
        ("B5_tau_stream_10_vs_5", b3["tau_stream_steps"], ref["tau_stream_steps"],
         abs(b3["tau_stream_steps"] - ref["tau_stream_steps"]) < tol),
        ("B6_half_life_stream_10_vs_5", b3["half_life_stream_steps"], ref["half_life_stream_steps"],
         abs(b3["half_life_stream_steps"] - ref["half_life_stream_steps"]) < tol),
        ("B6_half_life_events_5", ref["half_life_events"], 34.309618, abs(ref["half_life_events"] - 34.309618) < 5e-7),
        ("B6_half_life_events_10", b3["half_life_events"], 17.154809, abs(b3["half_life_events"] - 17.154809) < 5e-7),
        ("B6_B2_tau_stream_ratio", rows[1]["tau_stream_steps"] / ref["tau_stream_steps"], 2.0,
         abs(rows[1]["tau_stream_steps"] / ref["tau_stream_steps"] - 2.0) < 1e-12),
    ]
    ck = pd.DataFrame(checks, columns=["check_id", "computed", "expected", "pass_or_note"])
    ck.to_csv(out("POLE_EQUIVALENCE_VERIFICATION.csv"), index=False, float_format="%.12f")
    return df, ck, a10


# ----------------------------------------------------------------------
# PHASE C — symbolic ten-step mismatch
# ----------------------------------------------------------------------
def phase_c():
    E0, g5, g10, a = sp.symbols("E0 g5 g10 alpha", real=True)
    q = 1 - a
    e5 = q * E0 + a * g5
    e10_k5 = sp.expand(q * e5 + a * g10)
    a10 = 1 - q ** 2
    e10_pp = sp.expand(q ** 2 * E0 + a10 * g10)
    e10_b2 = sp.expand(q * E0 + a * g10)
    diff = sp.factor(sp.simplify(e10_pp - e10_k5))
    target = a * q * (g10 - g5)
    ok_diff = sp.simplify(diff - target) == 0
    ok_alpha = sp.simplify(a10 - a * (1 + q)) == 0
    ok_equal = sp.simplify((e10_pp - e10_k5).subs(g10, g5)) == 0
    coeff = float((a * q).subs(a, sp.Rational(2, 100)))
    # B2 comparison for context (not required, but shows what B3 removes)
    diff_b2 = sp.factor(sp.simplify(e10_b2 - e10_k5))

    # Deterministic numerical spot-check with fixed, non-random values.
    fixed = [(0.10, 0.02, 0.05), (0.0, 0.3, -0.1), (0.015, 0.015, 0.015), (-0.2, 1.0, 0.0)]
    num = []
    for E, G5, G10 in fixed:
        al, qq = 0.02, 0.98
        k5 = qq * (qq * E + al * G5) + al * G10
        pp = (qq ** 2) * E + (1 - qq ** 2) * G10
        num.append({"E0": E, "g5": G5, "g10": G10, "E_K5": k5, "E_K10_PP": pp,
                    "diff": pp - k5, "alpha_q_(g10-g5)": 0.0196 * (G10 - G5),
                    "abs_residual": abs((pp - k5) - 0.0196 * (G10 - G5))})
    num_df = pd.DataFrame(num)

    md = f"""# Ten-Step Mismatch Derivation (Phase C)

Generated by `generate_ema_timescale_design.py` using SymPy {sp.__version__}. Deterministic algebra only.

## C1. Block recursions (E0 = EMA state at an aligned 10-step boundary)

K5 reference (updates at t+5 and t+10, alpha, q = 1 - alpha):

    E_K5(t+10) = {sp.expand(e10_k5)}
               = q^2 E0 + alpha q g5 + alpha g10

K10 pole-preserved (one update at t+10, alpha10 = 1 - q^2):

    E_K10_PP(t+10) = {sp.expand(e10_pp)}
                   = q^2 E0 + alpha (1+q) g10

Identity alpha10 = 1 - q^2 = alpha (1 + q): **{'VERIFIED' if ok_alpha else 'FAILED'}**.

## C2. Difference

    E_K10_PP - E_K5 = {diff}

Equals alpha q (g10 - g5): **{'VERIFIED' if ok_diff else 'FAILED'}** (symbolic simplification to zero).

## C3. Coefficient

alpha q at alpha = 0.02: **{coeff:.6f}** (= 0.02 x 0.98).

## C4. Exact-match condition

Substituting g10 = g5 gives difference 0: **{'VERIFIED' if ok_equal else 'FAILED'}**.

## C5. Interpretation (binding wording)

Pole-preserving K10 is endpoint-equivalent to K5 **only** under constant gain across the two K5 sampling
instants of a ten-step block. It is not generally endpoint-equivalent when the gain differs between the
midpoint (t+5) and the endpoint (t+10). The residual is a **sparse-evidence mismatch** driven by
**midpoint-evidence omission** (E2), not by the pole (E3).

Context: for B2 (K10, alpha = 0.02) the same block difference is

    E_B2 - E_K5 = {diff_b2}

which contains a term proportional to E0 (the pole distortion, E3) in addition to the evidence terms.
B3 removes exactly the E0-proportional term and rebalances the evidence weight; it does not restore g5.

## C6. Terminology

No frequency-domain analysis of the gain signal was performed. This mismatch is **not** called aliasing.
Labels used: GAIN-EVIDENCE SUBSAMPLING, MIDPOINT-EVIDENCE OMISSION, SPARSE-EVIDENCE MISMATCH.

## Consequence not stated in the prompt: noise-equivalence is NOT preserved

Pole matching fixes the *mean* stream-time memory but halves the number of gain samples inside that memory.
For serially uncorrelated gains with variance s^2, the stationary EMA variance is alpha/(2-alpha) s^2:

| Config | alpha | effective samples (2-alpha)/alpha | stationary var factor |
|---|---|---|---|
| K5 (B0/B1) | 0.020000 | 99.000 | 0.010101 |
| K10 (B2) | 0.020000 | 99.000 | 0.010101 |
| K10 (B3) | 0.039600 | 49.505 | 0.020200 |

B3 therefore runs with ~2.0x the EMA variance of K5 (~1.414x the SD) under iid gains, smaller if midpoint and
endpoint gains are positively correlated. B2 had K5-level noise but 2x lag; B3 has K5-level lag but ~2x noise.
Because promotion and eviction are hard threshold tests on these EMAs (theta_tol = 0.015, eviction 0.005 / 0.008
per executable code), B3 carries a preregistrable risk of **threshold-noise churn** (spurious crossings), which
is the variance face of E2. This is a LEBRE_SPECIFIC_HYPOTHESIS, not an established result.

## Deterministic numerical spot-check (fixed inputs, no RNG)

{num_df.to_markdown(index=False, floatfmt='.10f')}
"""
    with open(out("TEN_STEP_MISMATCH_DERIVATION.md"), "w", encoding="utf-8") as f:
        f.write(md)
    return ok_alpha and ok_diff and ok_equal, coeff, float(num_df.abs_residual.max())


# ----------------------------------------------------------------------
# PHASE D — MEOE from sealed telemetry
# ----------------------------------------------------------------------
def phase_d():
    tw = json.load(open(os.path.join(COMP, "trans_windows_cache.json")))
    K5_ARMS = ("A0_K1_KARB5", "A1_K2_KARB5")
    alpha, q = 0.02, 0.98
    block_rows, integrity = [], []
    replay_rows = []
    for rec in tw:
        if rec["arm_code"] not in K5_ARMS:
            continue
        t_idx = np.array(rec["steps"])
        sc = t_idx + 1                               # step_count = loop index + 1 (live_step increments first)
        gains = {}
        for key, name in (("g_d", "G_D|B"), ("g_r", "G_R|B")):
            E = np.array(rec[key], dtype=np.float64)
            upd = (sc % 5 == 0)
            # Integrity: between arbitration events the EMA must be held exactly.
            held = np.all(E[1:][~upd[1:]] == E[:-1][~upd[1:]])
            g = np.full_like(E, np.nan)
            g[1:] = (E[1:] - q * E[:-1]) / alpha
            g[~upd] = np.nan
            g[0] = np.nan
            gains[name] = (E, g)
            integrity.append({"task_id": rec["task_id"], "arm_code": rec["arm_code"], "gain": name,
                              "update_steps_in_window": int(upd[1:].sum()),
                              "hold_between_events_exact": bool(held)})
        # ten-step blocks: midpoint sc%10==5, endpoint sc%10==0
        for i in range(len(sc)):
            if sc[i] % 10 != 0 or i < 5:
                continue
            j = i - 5
            row = {"task_id": rec["task_id"], "arm_code": rec["arm_code"], "block_end_step": int(sc[i])}
            for name, (E, g) in gains.items():
                g10, g5 = g[i], g[j]
                row[f"{name}_g5"] = g5
                row[f"{name}_g10"] = g10
                row[f"{name}_MEOE"] = 0.0196 * (g10 - g5)
                row[f"{name}_ABS_MEOE"] = abs(0.0196 * (g10 - g5))
            s = row["block_end_step"]
            row["window"] = ("PRE_TRANSITION_STEADY" if s <= 3000 else
                             "POST_TRANSITION_EARLY_0_100" if s <= 3100 else
                             "POST_TRANSITION_LATE_100_300")
            row["MEOE_MAX_ABS"] = max(row["G_D|B_ABS_MEOE"], row["G_R|B_ABS_MEOE"])
            block_rows.append(row)

        # Open-loop filter replay on the frozen K5 gain sequence (NOT a counterfactual trajectory).
        start = next(i for i in range(len(sc)) if sc[i] % 10 == 0)
        for name, (E, g) in gains.items():
            e_b2 = e_b3 = E[start]
            dev_b2, dev_b3 = [], []
            # Decision-side agreement with K5 at the code thresholds (theta_tol, and eviction level).
            evict_thr = 0.005 if name == "G_D|B" else 0.008
            dis_b2 = dis_b3 = 0
            for i in range(start + 1, len(sc)):
                if sc[i] % 10 == 0:
                    e_b2 = 0.98 * e_b2 + 0.02 * g[i]
                    e_b3 = 0.9604 * e_b3 + 0.0396 * g[i]
                    dev_b2.append(e_b2 - E[i])
                    dev_b3.append(e_b3 - E[i])
                    for thr in (0.015, evict_thr):
                        dis_b2 += (e_b2 > thr) != (E[i] > thr)
                        dis_b3 += (e_b3 > thr) != (E[i] > thr)
            dev_b2, dev_b3 = np.array(dev_b2), np.array(dev_b3)
            replay_rows.append({
                "task_id": rec["task_id"], "arm_code": rec["arm_code"], "gain": name,
                "n_block_endpoints": len(dev_b2),
                "B2_filter_mean_abs_dev_from_K5": float(np.mean(np.abs(dev_b2))),
                "B3_filter_mean_abs_dev_from_K5": float(np.mean(np.abs(dev_b3))),
                "B2_filter_max_abs_dev": float(np.max(np.abs(dev_b2))),
                "B3_filter_max_abs_dev": float(np.max(np.abs(dev_b3))),
                "B3_over_B2_mean_abs_dev_ratio": float(np.mean(np.abs(dev_b3)) / np.mean(np.abs(dev_b2)))
                if np.mean(np.abs(dev_b2)) > 0 else float("nan"),
                "K5_EMA_range_in_window": float(E.max() - E.min()),
                "B2_threshold_side_disagreements": int(dis_b2),
                "B3_threshold_side_disagreements": int(dis_b3),
                "threshold_side_comparisons": 2 * len(dev_b2),
            })

    blocks = pd.DataFrame(block_rows)
    blocks.to_csv(out("MEOE_BLOCK_LEVEL.csv"), index=False, float_format="%.10g")
    pd.DataFrame(integrity).to_csv(out("MEOE_TELEMETRY_INTEGRITY.csv"), index=False)
    pd.DataFrame(replay_rows).to_csv(out("OPEN_LOOP_FILTER_REPLAY.csv"), index=False, float_format="%.10g")

    def stats(x):
        x = np.asarray(x, dtype=float)
        x = x[~np.isnan(x)]
        return {"n_blocks": len(x), "mean": x.mean(), "median": np.median(x), "sd": x.std(ddof=1) if len(x) > 1 else np.nan,
                "p90": np.percentile(x, 90), "p95": np.percentile(x, 95), "p99": np.percentile(x, 99), "max": x.max()}

    srows = []
    for (task, arm, win), g in list(blocks.groupby(["task_id", "arm_code", "window"])) + \
            [((t, a, "ALL_WINDOW_2900_3300"), g) for (t, a), g in blocks.groupby(["task_id", "arm_code"])]:
        for name in ("G_D|B", "G_R|B"):
            for col, lab in ((f"{name}_MEOE", "MEOE"), (f"{name}_ABS_MEOE", "ABS_MEOE")):
                srows.append({"task_id": task, "arm_code": arm, "window": win, "gain": name, "metric": lab,
                              **stats(g[col])})
    summ = pd.DataFrame(srows).sort_values(["task_id", "arm_code", "gain", "metric", "window"])
    summ.to_csv(out("MEOE_BY_TASK_AND_WINDOW.csv"), index=False, float_format="%.10g")

    # D7 rule (pre-declared in module docstring)
    d7 = []
    for task in ("I11_Regime_Switch_Delay_To_Latent", "I12_Regime_Switch_Latent_To_Delay"):
        for arm in K5_ARMS:
            g = blocks[(blocks.task_id == task) & (blocks.arm_code == arm)]
            pre = g[g.window == "PRE_TRANSITION_STEADY"].MEOE_MAX_ABS
            post = g[g.window == "POST_TRANSITION_EARLY_0_100"].MEOE_MAX_ABS
            r = post.mean() / pre.mean() if pre.mean() > 0 else float("inf")
            d7.append({"task_id": task, "arm_code": arm, "n_pre": len(pre), "n_post_early": len(post),
                       "mean_abs_pre": pre.mean(), "mean_abs_post_early": post.mean(), "ratio": r,
                       "ratio_ge_2": bool(r >= 2.0)})
    d7 = pd.DataFrame(d7)
    if d7.ratio_ge_2.all():
        verdict = "SUPPORTED_DIAGNOSTICALLY"
    elif not d7.ratio_ge_2.any():
        verdict = "NOT_SUPPORTED"
    else:
        verdict = "MIXED"
    d7.to_csv(out("MEOE_CHANGEPOINT_RISK.csv"), index=False, float_format="%.10g")
    return blocks, summ, d7, verdict, pd.DataFrame(integrity), pd.DataFrame(replay_rows)


# ----------------------------------------------------------------------
# PHASE F11 — seed scan
# ----------------------------------------------------------------------
def seed_scan():
    used, sources = set(), {}
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__", ".pytest_cache")]
        if os.path.abspath(root).startswith(STAGE_DIR):
            continue
        for fn in files:
            p = os.path.join(root, fn)
            found = set()
            if fn.endswith(".csv"):
                try:
                    df = pd.read_csv(p, usecols=lambda c: "seed" in c.lower(), low_memory=False)
                except Exception:
                    continue
                for c in df.columns:
                    found |= set(pd.to_numeric(df[c], errors="coerce").dropna().astype(int))
            elif fn.endswith((".py", ".md", ".json", ".txt")):
                t = open(p, encoding="utf-8", errors="ignore").read()
                for a, b in re.findall(r"range\(\s*(\d{3,5})\s*,\s*(\d{3,5})\s*\)", t):
                    a, b = int(a), int(b)
                    if 100 <= a < 10000 and 0 < b - a <= 500:
                        found |= set(range(a, b))
                for a, b in re.findall(r"\b(\d{3,5})\s*\.\.\s*(\d{3,5})\b", t):
                    a, b = int(a), int(b)
                    if 100 <= a < 10000 and 0 < b - a <= 500:
                        found |= set(range(a, b + 1))
                for a in re.findall(r"seed\s*[=:]\s*(\d{3,5})\b", t):
                    found.add(int(a))
            if found:
                used |= found
                for s in found:
                    sources.setdefault(s, set()).add(os.path.relpath(p, ROOT).replace("\\", "/"))
    proposed = range(2001, 2031)
    overlap = sorted(s for s in proposed if s in used)
    lo = 2001
    while any(s in used for s in range(lo, lo + 30)):
        lo += 1
    rows = [{"seed": s, "sources": ";".join(sorted(sources[s]))} for s in overlap]
    return overlap, rows, (lo, lo + 29), sorted(s for s in used if 1900 <= s <= 2100)


# ----------------------------------------------------------------------
# PHASE F7 — future arm config + invariant
# ----------------------------------------------------------------------
FROZEN_COMMON = {
    "search_H": 32, "search_B": 4, "K_probe": 2,
    "K_cand_obs": 5, "K_cand_learn": 10,
    "candidate_min_obs_for_promotion (T_prob)": 15,
    "candidate_evidence_promote_threshold": 0.02,
    "candidate_evidence_ema": "0.95/0.05 (unchanged)",
    "candidate_prune_rule": "stream_age>150 and evidence<0.02",
    "theta_tol (code)": 0.015,
    "conditional_pair_threshold G_D|BR,G_R|BD": 0.015,
    "lag_eviction_threshold G_D|B": 0.005,
    "rec_eviction_threshold G_R|B": 0.008,
    "eviction_warmup_guard_step_count": 300,
    "tap_R_ema": "0.999/0.001 (unchanged)",
    "tap_lr": 0.08,
    "frontier_corr_ema": "0.95/0.05 fp16 (unchanged)",
    "K_rec_learn": 10,
    "rec_evidence_ema": "0.98/0.02 at K_rec_learn (UNCHANGED; not an arbitration EMA)",
    "recurrent_state_semantics": "HOLD_STATE",
    "arbitration_fp_per_event": 28.0,
    "stream_length": 6000,
    "tasks": "I1..I14 (scratch/bench_v02_integration.BENCHMARK_TASKS)",
}
ARMS = {
    "B0": {"K_rec_forward": 1, "K_arbitration": 5, "alpha_gain_EMA": 0.02},
    "B1": {"K_rec_forward": 2, "K_arbitration": 5, "alpha_gain_EMA": 0.02},
    "B2": {"K_rec_forward": 2, "K_arbitration": 10, "alpha_gain_EMA": 0.02},
    "B3": {"K_rec_forward": 2, "K_arbitration": 10, "alpha_gain_EMA": 1.0 - 0.98 ** 2},
}


def arm_config():
    full = {a: {**FROZEN_COMMON, **v} for a, v in ARMS.items()}
    diff = [k for k in full["B2"] if full["B2"][k] != full["B3"][k]]
    assert diff == ["alpha_gain_EMA"], diff
    assert set(full["B2"]) == set(full["B3"])
    b1b2 = [k for k in full["B1"] if full["B1"][k] != full["B2"][k]]
    assert b1b2 == ["K_arbitration"], b1b2
    rows = []
    for k in full["B0"]:
        vals = [full[a][k] for a in ARMS]
        rows.append({"parameter": k, **{a: full[a][k] for a in ARMS},
                     "B3_vs_B2": "INTERVENTION" if full["B2"][k] != full["B3"][k] else "IDENTICAL",
                     "B2_vs_B1": "INTERVENTION" if full["B1"][k] != full["B2"][k] else "IDENTICAL"})
    df = pd.DataFrame(rows)
    df.to_csv(out("FUTURE_ARM_CONFIG_DIFF.csv"), index=False, float_format="%.17g")
    return df, diff


def main():
    n_hashed, drift = phase_a()
    ops, checks, a10 = phase_b()
    c_ok, coeff, c_resid = phase_c()
    blocks, summ, d7, d7_verdict, integ, replay = phase_d()
    overlap, overlap_rows, block, used_near = seed_scan()
    cfg, diff = arm_config()

    pd.DataFrame(overlap_rows).to_csv(out("SEED_BLOCK_OVERLAP_2001_2030.csv"), index=False)

    summary = {
        "stage": "LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01",
        "stochastic_streams_executed": 0,
        "parent_files_hashed": n_hashed,
        "seal_manifest_hash_drift": drift,
        "alpha10_computed_repr": repr(a10),
        "phase_b_all_pass": bool(all(v is True for v in checks.pass_or_note if isinstance(v, bool))),
        "phase_c_symbolic_pass": bool(c_ok),
        "phase_c_coeff": coeff,
        "phase_c_numeric_max_residual": c_resid,
        "telemetry_integrity_all_hold_exact": bool(integ.hold_between_events_exact.all()),
        "meoe_blocks": int(len(blocks)),
        "d7_verdict": d7_verdict,
        "open_loop_replay_B3_over_B2_ratio_median": float(replay.B3_over_B2_mean_abs_dev_ratio.median()),
        "seed_block_2001_2030_overlap": overlap,
        "next_unused_block": list(block),
        "used_seeds_1900_2100": used_near,
        "B2_B3_diff_params": diff,
    }
    with open(out("DESIGN_COMPUTATION_SUMMARY.json"), "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
