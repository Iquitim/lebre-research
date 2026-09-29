#!/usr/bin/env python3
"""build_artifacts.py — writes the tabular forensic artifacts (02–07, 18, 20, 23 and the resource ledgers) from the run
outputs in this folder. Narrative artifacts (.md) are written separately."""
import glob
import hashlib
import json
import os

import numpy as np
import pandas as pd

H = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(H, "..", ".."))
V51 = os.path.join(R, "experiments", "LEBRE-V0.51-LEAN-01")
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()

# ------------------------------------------------------------------ 02 provenance
files = [os.path.join(V51, f) for f in ("lebre_v051.py", "lebre_s051.py", "lebre_v045.py", "PREREG_V051.md", "PREREG_V051_SHA256.txt",
                                        "FREEZE_V051_SHA256.txt", "FREEZE_S051_SHA256.txt", "ARQUITETURA_V051.md", "eval_v051.py",
                                        "chronos_v051.py", "analyze_v051.py", "V051_DECISION.json", "INTERNAL_V051_RESULTS.csv",
                                        "HELDOUT_V051_RESULTS.csv", "HELDOUT_V051_OFFSETS.csv", "HELDOUT_V051_CHRONOS_RESULTS.csv",
                                        "POSTHOC_FEEDBACK_METRICS.csv", "POSTHOC_FEEDBACK_WS.csv", "POSTHOC_FEEDBACK_NULL.csv")]
files += [os.path.join(R, "experiments", "bench01", "streams.py"), os.path.join(R, "data", "external_v051", "load051.py"),
          os.path.join(R, "docs", "architecture", "pdf", "LEBRE_ARCHITECTURE_v0.51_SPEC_PTBR.pdf"),
          os.path.join(R, "docs", "architecture", "pdf", "LEBRE_ARCHITECTURE_v0.51_SPEC_EN.pdf"),
          os.path.join(os.path.expanduser("~"), "Downloads", "LEBRE-achados-e-validacoes.pdf"), os.path.join(os.path.expanduser("~"), "Downloads", "LEBRE-achados-e-validacoes-2.pdf")]
files += sorted(glob.glob(os.path.join(H, "*.py"))) + sorted(glob.glob(os.path.join(H, "RUN_*.csv"))) + sorted(glob.glob(os.path.join(H, "AUDIT_*.csv")))
with open(os.path.join(H, "02_PROVENANCE_HASHES.txt"), "w", encoding="utf-8") as f:
    f.write("# SHA-256 of every artifact used by the forensic investigation (computed at artifact-build time)\n")
    for p in files:
        f.write(f"{sha(p) if os.path.exists(p) else 'ARTIFACT_MISSING'}  {os.path.relpath(p, R) if p.startswith(R) else p}\n")
    f.write("ARTIFACT_MISSING  replication implementation repository (edubraqd/lebre-prototipo, private; src/lebre051/, results/lebre051/run_hypotheses.py)\n")
    f.write("ARTIFACT_MISSING  replication raw outputs (results/lebre051/run_hypotheses.txt) and relatorio-avaliacao-lebre-v0.51.md\n")
    f.write("ARTIFACT_MISSING  generators of the replica's v0.1 tasks A1, A7, A8\n")

# ------------------------------------------------------------------ 03 spec completeness
S = "EXPLICITLY_SPECIFIED"; DU = "DERIVABLE_UNIQUELY"; RD = "REFERENCE_DEPENDENT"; AM = "AMBIGUOUS"; MI = "MISSING"
spec = [
    ("NLMS epsilon (S)", MI, "absolute 1e-6 added to the normaliser", "not in spec"),
    ("NLMS epsilon (M)", MI, "none; update skipped only when ||phi||^2 == 0 exactly", "spec shows w <- w + mu e phi/||phi||^2 with no regulariser"),
    ("epsilon scaling rule", MI, "S: fixed absolute; M: none (exactly scale-invariant, numerically unguarded)", "spec claims scale invariance without stating epsilon"),
    ("martingale tau", AM, "tau = rho/(sigma2_hat * m_phi), rho = 1 (unit-information prior)", "formula shown with tau; value and units absent"),
    ("candidate screening rule", MI, "2 lag candidates probed per step round-robin; EMA (w=0.2) of e*x_lag; top |score| opened", "not in spec"),
    ("candidate-test horizon", AM, "T_max = 200 test samples (1 sample per 2 steps => up to 400 steps); futility afterwards", "D4 diagram says 'futility after T_max samples'; value absent"),
    ("maximum concurrent candidate tests", MI, "H_hot = 4 lag tests + latent candidates (one per pole, while no latent active) + drive candidates (d, after latent)", "not in spec"),
    ("queue discipline", MI, "free lag slots refilled at each decision (every 10 steps) with the highest |screen| untested candidates", "not in spec"),
    ("active-set capacity", S, "M_max = 4 structural atoms (base current inputs not counted)", "parameter table"),
    ("active-set-full policy", MI, "promotion allowed only by replacing the victim with largest CUSUM R, and only if R >= h/2; otherwise the candidate waits", "not in v0.51 spec (was in an earlier spec)"),
    ("atom replacement policy", MI, "as above; hidden-dynamics candidates reset when a latent/drive is promoted", "not in spec"),
    ("removal coupling", S, "evicting the latent evicts its drive", "stated in lifecycle description of earlier versions; implicit in v0.51 D4"),
    ("single-latent limit", AM, "at most one latent state; latent candidates are not tested while one is active", "not stated in v0.51 text"),
    ("input normalization", AM, "environment-side EMA standardiser (alpha = 1e-4, mean 0/var 1 start) in the external benchmarks; raw inputs in the internal suite", "spec says 'inputs standardised by the environment' and (wrongly) 'means and variances accumulated up to the previous instant'"),
    ("target normalization", S, "S: raw target; M: raw differences", "stated"),
    ("initialization", AM, "zeros; sigma2 from first error; warm-up 20 steps; qhat = 1.645 sigma", "partially stated"),
    ("seasonal-buffer initialization", MI, "buffer of 2s+2 zeros; M predicts the last value until n >= 2s+2", "not in spec"),
    ("missing-lag behavior", MI, "as above (no forecast from features before the buffer is full)", "not in spec"),
    ("quantile cadence", S, "every 8 steps", "stated"),
    ("quantile batch semantics", AM, "indicator of the refresh step only, step multiplied by 8 (not the sum of the 8 indicators)", "'step multiplied by 8' stated; which indicator is ambiguous"),
    ("dynamic model averaging cadence", S, "loss difference every step; weight (exp) every 8 steps", "stated"),
    ("evidence gates", S, "silence (<10% power), quarantine (|x|>8 readable), dormancy (w_S < 0.01)", "stated"),
    ("sleep semantics", S, "dormancy pauses evidence only; prediction, weights and sigma2 continue", "stated"),
    ("computational accounting", AM, "counts model arithmetic only; environment standardiser (~12d/step) and memory traffic not counted", "definition stated; scope (environment excluded) not stated"),
]
pd.DataFrame(spec, columns=["item", "classification", "authoritative_code_value", "spec_status"]).to_csv(os.path.join(H, "03_SPEC_COMPLETENESS_MATRIX.csv"), index=False)

# ------------------------------------------------------------------ 04 replication diff (replica values from its report only; code missing)
diff = [
    ("S", "martingale prior", "tau formula, value missing", "rho = 1 (tau = 1/(sigma2 m_phi))", "m in {50, 200, 1000} (tau ~ 1/m, per report)", "replica far more conservative", "lower power, slower/rarer promotion", "none", "AMBIGUOUS_SPEC_CHOICE"),
    ("S", "test horizon / slots", "missing", "4 lag slots, 200 samples (400 steps)", "4 slots, up to 500 shadow steps", "longer tests in replica", "slower search throughput", "none", "AMBIGUOUS_SPEC_CHOICE"),
    ("S", "active-set-full policy", "missing", "replace victim with R >= h/2", "no replacement", "replica cannot swap atoms", "structures blocked when full", "none", "AMBIGUOUS_SPEC_CHOICE"),
    ("S", "input normalizer", "'standardised by environment'", "EMA alpha=1e-4 (benchmarks) / raw (internal suite)", "v0.1 prototype causal normalizer (EMA ~100 steps)", "different normalizer", "structure drift on non-stationary inputs (A1/A8)", "4d vs ~12d", "REPLICA_DEVIATION"),
    ("S", "screening order", "missing", "screen updated with probes after evidence/tests in the step", "screening before scale update (after a fix)", "unknown equivalence", "B2 boundary shifts (0.835 -> 0.794 in replica)", "none", "UNRESOLVED"),
    ("M", "NLMS epsilon", "missing", "none (skip only if ||phi||^2 == 0)", "unstated default; tested eps >= 1% of increment variance", "unknown", "divergence on plateaus without eps", "none", "AMBIGUOUS_SPEC_CHOICE"),
    ("M", "missing lags", "missing", "no feature forecast until buffer 2s+2 is full", "missing lag = 0", "different warm-up", "early errors differ", "none", "AMBIGUOUS_SPEC_CHOICE"),
    ("interval", "batch semantics", "'step x 8'", "current indicator x 8", "tested both readings", "none on i.i.d. data", "phase aliasing on seasonal data", "none", "VALID_SPEC_INTERPRETATION"),
    ("accounting", "normalizer cost", "not stated", "not counted (environment)", "4d counted", "scope", "FP levels not comparable (replica ~350 vs original ~120-150)", "large", "UNRESOLVED"),
    ("tasks", "A1/A7/A8 generators", "n/a", "not part of v0.51 evaluation", "replica's own v0.1 tasks", "different benchmark", "not comparable", "n/a", "UNRESOLVED"),
    ("tasks", "N1,N2,T1,B1-B4 generators", "n/a", "re-implemented from the replica's written description", "replica code", "noise scale, stream length and check schedule not stated", "affects exact fractions and latency counts", "n/a", "UNRESOLVED"),
]
pd.DataFrame(diff, columns=["component", "parameter_or_behavior", "spec", "original_code", "replica", "difference", "expected_behavioral_effect",
                            "expected_resource_effect", "classification"]).to_csv(os.path.join(H, "04_REPLICATION_IMPLEMENTATION_DIFF.csv"), index=False)

# ------------------------------------------------------------------ 05 numeric reproduction
s = pd.read_csv(os.path.join(H, "RUN_MAIN_SUMMARY.csv")); v = s[s.arm == "V051"].groupby("task").mean(numeric_only=True)
so = s[s.arm == "S_ONLY"].groupby("task").mean(numeric_only=True)
rep = {"N1": (1.0422, 1.0562, 1.0485, 352, 0.0, 0.0, None, 0.901), "N2": (1.2180, 1.0668, 1.8271, 349, 0.0, 0.0, None, 0.901),
       "T1": (0.6561, 0.6564, 1.0485, 370, 1.9, 0.9, None, 0.901), "B1": (0.6588, 0.6593, 1.0487, 370, 1.5, 0.6, 0.979, 0.901),
       "B2": (0.5123, 0.5123, 1.0486, 402, 5.4, 2.6, 0.794, 0.901), "B3": (0.3048, 0.3147, 0.6593, 363, 11.8, 7.8, 0.066, 0.901),
       "B4": (0.6458, 0.6458, 1.1435, 391, 18.9, 16.7, 0.342, 0.901)}
rows = []
def cls(a, b, tol):
    if a is None or b is None or (isinstance(b, float) and np.isnan(b)):
        return "NOT_REPRODUCIBLE"
    if abs(a - b) <= 1e-9:
        return "EXACT_REPRODUCTION"
    return "ROUNDING_MATCH" if abs(a - b) <= tol else "MATERIAL_MISMATCH"
for t, (nm, nS, nM, fp, pr, rm, ex, cv) in rep.items():
    o = v.loc[t]
    for metric, a, b, tol in [("NMSE", nm, o.nmse, 0.005), ("NMSE_S", nS, o.nmse_S, 0.005), ("NMSE_M", nM, o.nmse_M, 0.005),
                              ("FP/step", fp, o.fp_mean, 5), ("promotions/seed", pr, o.promotions, 0.5), ("removals/seed", rm, o.removals, 0.5),
                              ("exact_structure", ex, o.exact_frac if ex is not None else None, 0.02), ("coverage", cv, o.coverage, 0.005)]:
        rows.append({"task": t, "metric": metric, "replica": a, "original_code": None if b is None else round(float(b), 4),
                     "classification": cls(a, None if b is None else float(b), tol)})
for t in ("A1", "A7", "A8"):
    rows.append({"task": t, "metric": "all", "replica": "see report", "original_code": None, "classification": "NOT_REPRODUCIBLE"})
dh = pd.read_csv(os.path.join(H, "RUN_DENSE_H9.csv")).groupby("task").mean(numeric_only=True)
for t, (rn, rf) in {"B1": (1.028, 0.320), "B2": (1.088, 0.348), "B3": (1.284, None)}.items():
    rows.append({"task": t, "metric": "H9 NMSE ratio vs dense window", "replica": rn, "original_code": round(v.loc[t].nmse / dh.loc[t].nmse_dense, 4), "classification": "MATERIAL_MISMATCH" if abs(rn - v.loc[t].nmse / dh.loc[t].nmse_dense) > 0.02 else "ROUNDING_MATCH"})
    rows.append({"task": t, "metric": "H9 FP ratio vs dense window", "replica": rf, "original_code": round(v.loc[t].fp_mean / dh.loc[t].fp_dense, 4), "classification": "MATERIAL_MISMATCH" if rf is not None else "NOT_REPRODUCIBLE"})
h8 = (v.nmse / so.nmse)
for t in ("T1", "B1", "B2", "B3", "B4"):
    rows.append({"task": t, "metric": "H8 NMSE(V051)/NMSE(S alone)", "replica": "0.968-1.000", "original_code": round(float(h8.loc[t]), 4),
                 "classification": "ROUNDING_MATCH" if h8.loc[t] <= 1.01 else "MATERIAL_MISMATCH"})
pd.DataFrame(rows).to_csv(os.path.join(H, "05_H4_H9_NUMERIC_REPRODUCTION.csv"), index=False)

# ------------------------------------------------------------------ 06 event ledger (main + tau + norm runs)
led = pd.concat([pd.read_csv(os.path.join(H, f)).assign(run=f.split("_")[1]) for f in ("RUN_MAIN_LEDGER.csv", "RUN_TAU_LEDGER.csv", "RUN_NORM_LEDGER.csv")])
led["test_start_to_promotion_steps"] = led.first_promoted_t - led.first_proposed_t
led.to_csv(os.path.join(H, "06_STRUCTURAL_DISCOVERY_EVENT_LEDGER.csv"), index=False)

# ------------------------------------------------------------------ 07 H6 root cause matrix
rc = [
    ("B1", "SEARCH_MISS/TEST_QUEUE_DELAY", "first proposal median 2065 steps; test itself needs ~90 samples (~180 steps); 4 slots x 400-step futile tests serve ~1 candidate/100 steps; screening is one noisy probe per candidate every 80 steps", "exact fraction 0.93 over checks from t=1000 is lowered only by the pre-discovery period", "CONFIRMED_ARCHITECTURAL_RESULT (single lag: supported)"),
    ("B2", "SEARCH_MISS/TEST_QUEUE_DELAY + FALSE_REJECTION (futility) for the weakest atom + PARAMETER_SENSITIVITY", "lag(4,20) (coef 0.5) first promoted median 8635 steps after 1.9 episodes on average; tau grid: rho 1 -> 0.57, 1/50 -> 0.58, 1/200 -> 0.28, 1/1000 -> 0.00", "no blocking events; exact fraction per seed 0.22-0.91", "PARAMETER_SENSITIVITY / CONFIRMED_ARCHITECTURAL_FAILURE at the 80% gate"),
    ("B3", "WRONG_ATOM_PROMOTION (latent pole 0.0 or 0.5) + ELIGIBILITY_DEPENDENCY (single latent; drive tied to active pole)", "a latent with pole 0.0/0.5 is promoted first in 10/10 seeds; latent candidates are then no longer tested; the true drive q(0;0.8) can never be eligible", "active-set budget full only 3.5% of decision instants; 0 blocked crossings -> critique's 'slots full' hypothesis NOT supported in the original code", "CONFIRMED_ARCHITECTURAL_FAILURE (representable but unreachable)"),
    ("B4", "TRUE_ATOM_EVICTION (heavy tails) + SEARCH delay", "30 removals in 10 seeds (vs 3 in B2); Gaussian-LLR CUSUM sensitive to t3 outliers", "exact 0.27", "CONFIRMED_ARCHITECTURAL_FAILURE"),
    ("A8", "NORMALIZATION_DISTORTION (replica only) - generator unavailable", "replica used its v0.1 EMA-100 normalizer; original v0.51 benchmarks use an EMA alpha=1e-4 scaler; on stationary tasks B1-B3 raw/causal/EMA-100 give the same structure", "cannot rerun A8", "REPRODUCTION NOT_EXECUTABLE; IMPLEMENTATION_DIFF CONFIRMED; CAUSAL_ROOT_CAUSE INSUFFICIENT_EVIDENCE"),
]
pd.DataFrame(rc, columns=["task", "dominant_causes", "evidence", "notes", "label"]).to_csv(os.path.join(H, "07_H6_ROOT_CAUSE_MATRIX.csv"), index=False)

# ------------------------------------------------------------------ resource ledgers (18)
d = 5
orig = [  # component, ADD, MUL, DIV, CMP, SQRT, EXP, counted_in_LEBRE_FP, note (static count from source; d=5, s=24, |A|=2 lag atoms, latent inactive; per-step averages)
    ("environment standardiser (transform)", 2 * d, 0, d, 0, d, 0, "NO", "add eps, subtract mean, sqrt, divide"),
    ("environment standardiser (update)", 3 * d, 4 * d, 0, d, 0, 0, "NO", "EMA mean and variance, floor"),
    ("S base prediction", d + 1, d, 0, 0, 0, 0, "YES", "bias + theta_b . x"),
    ("S lag atoms prediction", 2, 2, 0, 0, 0, 0, "YES", "2 atoms"),
    ("S NLMS update", 2 * d + 6, 2 * d + 6, 1, 0, 0, 0, "YES", "normaliser, step, updates"),
    ("S latent bank (3 non-trivial poles)", 4, 7, 1, 0, 1, 0, "YES", "u/sigma, pole filters, sqrt(sigma2)"),
    ("S candidate search (2 probes)", 4, 4, 0, 0, 0, 0, "YES", "EMA of e*x"),
    ("S martingale tests (4 lag + 4 latent, every 2 steps)", 8, 8, 0, 0, 0, 0, "YES", "S += z, Q += z^2"),
    ("S CUSUM (2 atoms, every 2 steps)", 4, 4, 0, 2, 0, 0, "YES", "LLR, rent, max"),
    ("S decisions (every 10 steps)", 1, 1, 0.3, 1, 0, 0.1, "YES", "log-mixture with log only when needed"),
    ("S sigma2 / excitation gate", 4, 3, 0, 2, 0, 0, "YES", ""),
    ("M features (5)", 6, 0, 0, 0, 0, 0, "YES", "differences"),
    ("M prediction + NLMS", 13, 16, 1, 1, 0, 0, "YES", "dot, ||phi||^2, update"),
    ("M profile + mean", 4, 2, 0, 0, 0, 0, "YES", ""),
    ("combiner", 7, 6, 0.125, 1, 0.125, 0.125, "YES", "errors, D, weight every 8"),
    ("interval", 1, 0.4, 0, 1, 0, 0, "YES", "compare; update every 8"),
]
lo = pd.DataFrame(orig, columns=["component", "ADD", "MUL", "DIV", "COMPARE", "SQRT", "EXP", "counted_in_LEBRE_FP", "note"])
lo["arith_total"] = lo[["ADD", "MUL", "DIV", "COMPARE", "SQRT", "EXP"]].sum(axis=1)
lo.to_csv(os.path.join(H, "RESOURCE_LEDGER_ORIGINAL.csv"), index=False)
pd.DataFrame([("all components", "ARTIFACT_MISSING", "replica code not available; report states normaliser counted as 4d and total FP ~350-500/step")],
             columns=["component", "status", "note"]).to_csv(os.path.join(H, "RESOURCE_LEDGER_REPLICA.csv"), index=False)
model_only = lo[lo.counted_in_LEBRE_FP == "YES"].arith_total.sum(); env = lo[lo.counted_in_LEBRE_FP == "NO"].arith_total.sum()
b1 = v.loc["B1"]; dB1 = dh.loc["B1"]
recon = [("A: original convention (model arithmetic only)", round(float(b1.fp_mean), 1), round(float(dB1.fp_dense), 1), round(float(b1.fp_mean / dB1.fp_dense), 3)),
         ("B: replica convention (+4d normaliser)", round(float(b1.fp_mean + 4 * d), 1), round(float(dB1.fp_dense + 4 * d), 1), round(float((b1.fp_mean + 4 * d) / (dB1.fp_dense + 4 * d)), 3)),
         ("C: orthogonal ledger (+ full environment standardiser, static count)", round(float(b1.fp_mean + env), 1), round(float(dB1.fp_dense + env), 1), round(float((b1.fp_mean + env) / (dB1.fp_dense + env)), 3))]
rr = pd.DataFrame(recon, columns=["convention", "LEBRE_v051_FP_B1", "dense_variant_FP_B1", "H9_cost_ratio_B1"])
rr["static_model_only_estimate"] = round(float(model_only), 1); rr["static_environment_standardiser"] = round(float(env), 1)
rr["replica_reported_ratio_B1"] = 0.320; rr["threshold"] = round(1 / 3, 3)
rr.to_csv(os.path.join(H, "18_RESOURCE_RECONCILIATION.csv"), index=False)
print("static model-only estimate", model_only, "env", env)

# ------------------------------------------------------------------ 20 claim-by-claim verdicts
V = [("C1", "Forecasting competitive with lightweight online comparators (held-out protocol)", "SUPPORTED_WITH_SCOPE_LIMITS", "0.84x NLinear, wins 8/10 vs preregistered online comparators; post-hoc airline MLE 5% better on 9/10; Chronos-2 1.36x better"),
     ("C2", "Real-data advantage primarily due to M", "SUPPORTED", "M alone/LEBRE 1.034 and 1.006; 0 structural promotions in 15/20 real series (N6: 1 promotion, zero combiner weight); w_S ~ 0 on 16/20"),
     ("C3", "S discovers a single true lag robustly", "SUPPORTED_WITH_SCOPE_LIMITS", "T1 exact 0.98, B1 0.93 (checks from t=1000); found in 10/10 seeds; slow first proposal"),
     ("C4", "S discovers multiple true lags robustly", "NOT_SUPPORTED", "B2 exact 0.57 (0.22-0.91 per seed), B4 0.27; tau-sensitive"),
     ("C5", "S discovers latent-state structures robustly", "REFUTED", "B3 exact 0/10 seeds at all tau and all normalizers: wrong latent pole locks in (single-latent limit)"),
     ("C6", "S controls false promotions", "SUPPORTED", "0 false promotions in 2M null steps / 17,686 test episodes (95% upper bound ~1.7e-4 per episode)"),
     ("C7", "True atoms remain stable after promotion", "SUPPORTED_WITH_SCOPE_LIMITS", "T1: 3 utility removals in 974,840 active steps, all rediscovered; heavy tails (B4) 30 removals"),
     ("C8", "<=2000-step discovery latency", "NOT_SUPPORTED", "gate feasible by construction (lower bound ~300-600 steps) but search throughput delays first proposal to ~1500-2900 steps; latent atoms never"),
     ("C9", "Dynamic combination does not materially harm prediction", "SUPPORTED_WITH_SCOPE_LIMITS", "ratio V051/S <= 1.001 on T1,B1,B2,B4; B3 1.020 (> 1.01 gate)"),
     ("C10", "Structural discovery buys sufficient compute efficiency", "SUPPORTED_WITH_SCOPE_LIMITS", "vs the project's dense-window variant: FP ratio 0.15-0.21 under all 3 conventions, NMSE ratio 1.01-1.08; replica's failure depends on its own dense window"),
     ("C11", "~1.3 KB memory valid across the stated envelope", "NOT_SUPPORTED", "memory ~ 196d + 12s + ~190 bytes (float32 accounting); <=1.3 KB only if s<=78 (d=1), 46 (d=3), 13 (d=5), never at d=6; 1.46 KB at d=5,s=24; 2.9 KB s=144; 18 KB s=1440; Python stores float64 (x2)"),
     ("C12", "Interval implementation preserves stream-time semantics", "NOT_SUPPORTED", "current-indicator x 8 aliases with 8|s: real-series coverage 0.85-0.97 vs 0.900-0.906 with the 8 indicators accumulated"),
     ("C13", "NLMS numerics fully specified and scale-safe", "NOT_SUPPORTED", "M has no epsilon: exact scale invariance but divergence on flat-then-step (NMSE 8e20)"),
     ("C14", "Stability metric supports the wording", "NOT_SUPPORTED", "measures burn-in/initialisation sensitivity on one test window, not stability across time segments"),
     ("C15", "Preregistration and hashes independently verifiable", "INSUFFICIENT_EVIDENCE", "hashes verify locally (frozen code, prereg, data match; timestamps ordered) but none are published with the document"),
     ("C16", "Specification complete for independent reimplementation", "NOT_SUPPORTED", "11 items MISSING and 6 AMBIGUOUS in the completeness matrix"),
     ("C17", "Evidence supports real-world structural discovery", "NOT_SUPPORTED", "no real input-driven dataset evaluated; w_S ~ 0 on 16/20 real series")]
pd.DataFrame(V, columns=["claim", "text", "verdict", "evidence"]).to_csv(os.path.join(H, "20_CLAIM_BY_CLAIM_VERDICT.csv"), index=False)
print("ok")
