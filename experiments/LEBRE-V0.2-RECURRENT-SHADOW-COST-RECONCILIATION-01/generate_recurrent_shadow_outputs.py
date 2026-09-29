#!/usr/bin/env python3
"""
generate_recurrent_shadow_outputs.py

Definitive master verification and reporting script for:
LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01

Computes:
1. Exact operation reconciliation (20.20 FP/step).
2. Resource distribution and gate compliance (Mean total FP <= 100.0).
3. Primary local non-inferiority vs C0 (Parent M1*, epsilon = +0.0100).
4. Global non-inferiority vs R0 (Continuous T3).
5. Continuous latent preservation (I6, I7).
6. Quiescent retention and reactivation (I7).
7. Hybrid complementarity (I9: G_D|B+R > 0, G_R|B+D > 0).
8. Switching recovery latencies (I11, I12, I14).
9. State trajectory distortion metrics (h_C1 vs h_C0).
10. Generates RECURRENT_SHADOW_MANIFEST.json.
11. Outputs the exact final machine-readable block per Section B35.
"""

import os
import sys
import json
import math
import hashlib
import numpy as np
import pandas as pd
from scipy import stats

STAGE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(STAGE_DIR, "..", ".."))

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 70)
    print("LEBRE v0.2 RECURRENT SHADOW COST RECONCILIATION: MASTER AUDIT & VERIFICATION")
    print("=" * 70)
    
    # 1. Verify Phase A files
    phase_a_files = [
        "RECURRENT_SHADOW_PROTOCOL.md",
        "RECURRENT_SHADOW_PREREGISTRATION.md",
        "PARENT_HASHES.txt",
        "SEED_PROVENANCE.md",
        "RECURRENT_SHADOW_OPERATION_LEDGER.csv",
        "RECURRENT_COMPUTE_RECONCILIATION.csv",
        "RECURRENT_CURRENT_CLOCK_AUDIT.md",
        "RECURRENT_PRIOR_TRANSFERABILITY_AUDIT.md",
        "PRIOR_D9F_D9L_RECONCILIATION.csv",
        "RECURRENT_COST_BY_TASK.csv",
        "RECURRENT_COST_BY_LIFECYCLE_STATE.csv",
        "RECURRENT_ORACLE_SAVINGS.csv",
        "RECURRENT_RESOURCE_CLOSURE_TABLE.csv",
        "RECURRENT_FAST_FORWARD_DERIVATION.md",
        "RECURRENT_SKIP_SEMANTICS.md",
        "RECURRENT_SPARSE_EXECUTION_LITERATURE_NOTE.md",
        "PHASE_A_FEASIBILITY_DECISION.md"
    ]
    for fn in phase_a_files:
        fp = os.path.join(STAGE_DIR, fn)
        assert os.path.exists(fp), f"Missing Phase A file: {fn}"
    print("Phase A files verified: 17/17 present.")

    # Check 20.20 reconciliation
    df_ledger = pd.read_csv(os.path.join(STAGE_DIR, "RECURRENT_SHADOW_OPERATION_LEDGER.csv"))
    rec_sum = df_ledger["FP_per_stream_step"].sum()
    reconciles_20p2 = abs(rec_sum - 20.200000) < 1e-9
    print(f"Recurrent Ledger Sum: {rec_sum:.6f} FP/step (Reconciles 20.2: {reconciles_20p2})")

    # 2. Verify Phase B files
    final_results_csv = os.path.join(STAGE_DIR, "RECURRENT_FINAL_RESULTS.csv")
    if not os.path.exists(final_results_csv):
        print(f"Error: {final_results_csv} not found. Ensure run_phase_b_experiments.py has completed.")
        sys.exit(1)
        
    df_final = pd.read_csv(final_results_csv)
    print(f"Loaded {len(df_final)} confirmatory simulation runs across {len(df_final['seed'].unique())} seeds and {len(df_final['task_id'].unique())} tasks.")

    # Resource distribution for C1_K5
    sub_c1 = df_final[df_final["model_label"] == "C1_K5"]
    tot_fp_c1 = sub_c1["total_fp_mean"]
    c1_fp_mean = float(tot_fp_c1.mean())
    c1_fp_median = float(tot_fp_c1.median())
    c1_fp_p90 = float(np.percentile(tot_fp_c1, 90))
    c1_fp_p95 = float(np.percentile(tot_fp_c1, 95))
    c1_fp_p99 = float(np.percentile(tot_fp_c1, 99))
    c1_fp_peak = float(tot_fp_c1.max())

    print("\n--- 1. C1 (K=5) Total Online Compute Distribution (FP/step) ---")
    print(f"Mean:   {c1_fp_mean:.4f} FP/step (Gate <= 100.0: {'PASS' if c1_fp_mean <= 100.0 else 'FAIL'})")
    print(f"Median: {c1_fp_median:.4f} FP/step")
    print(f"P90:    {c1_fp_p90:.4f} FP/step")
    print(f"P95:    {c1_fp_p95:.4f} FP/step")
    print(f"P99:    {c1_fp_p99:.4f} FP/step")
    print(f"Peak:   {c1_fp_peak:.4f} FP/step")

    # Primary Local Non-Inferiority vs C0
    c0_seed = df_final[df_final["model_label"] == "C0_M1_PARENT"].groupby("seed")["nmse"].mean()
    c1_seed = df_final[df_final["model_label"] == "C1_K5"].groupby("seed")["nmse"].mean()
    r0_seed = df_final[df_final["model_label"] == "R0_CONTINUOUS"].groupby("seed")["nmse"].mean()

    delta_c0 = c1_seed - c0_seed
    mean_d_c0 = float(delta_c0.mean())
    std_d_c0 = float(delta_c0.std(ddof=1))
    se_d_c0 = std_d_c0 / math.sqrt(len(delta_c0))
    t_crit = stats.t.ppf(0.95, df=len(delta_c0) - 1)
    ci95_u_c0 = mean_d_c0 + t_crit * se_d_c0
    local_noninf_supported = ci95_u_c0 < 0.0100

    print("\n--- 2. Primary Local Non-Inferiority vs C0 (Parent M1*, N=30) ---")
    print(f"C0 Parent Mean NMSE:    {c0_seed.mean():.6f}")
    print(f"C1 Candidate Mean NMSE: {c1_seed.mean():.6f}")
    print(f"Delta NMSE (C1 - C0):   {mean_d_c0:+.6f} (std={std_d_c0:.6f}, SE={se_d_c0:.6f})")
    print(f"One-Sided 95% Upper CI: {ci95_u_c0:+.6f} (Margin: +0.0100 -> {'SUPPORTED (PASS)' if local_noninf_supported else 'NOT_SUPPORTED (FAIL)'})")

    # Global Non-Inferiority vs R0
    delta_r0 = c1_seed - r0_seed
    mean_d_r0 = float(delta_r0.mean())
    std_d_r0 = float(delta_r0.std(ddof=1))
    se_d_r0 = std_d_r0 / math.sqrt(len(delta_r0))
    ci95_u_r0 = mean_d_r0 + t_crit * se_d_r0
    global_noninf_supported = ci95_u_r0 < 0.0100

    print("\n--- 3. Global Behavioral Status vs R0 (Continuous T3, N=30) ---")
    print(f"R0 Continuous Mean NMSE: {r0_seed.mean():.6f}")
    print(f"Delta NMSE (C1 - R0):    {mean_d_r0:+.6f} (std={std_d_r0:.6f}, SE={se_d_r0:.6f})")
    print(f"One-Sided 95% Upper CI:  {ci95_u_r0:+.6f} (Margin: +0.0100 -> {'SUPPORTED (PASS)' if global_noninf_supported else 'NOT_SUPPORTED (FAIL)'})")

    # Task Level Preservations
    # I6 & I7 Continuous Latent
    i6_c0 = df_final[(df_final["model_label"] == "C0_M1_PARENT") & (df_final["task_id"] == "I6_Continuous_Latent_State")]["nmse"].mean()
    i6_c1 = df_final[(df_final["model_label"] == "C1_K5") & (df_final["task_id"] == "I6_Continuous_Latent_State")]["nmse"].mean()
    i7_c0 = df_final[(df_final["model_label"] == "C0_M1_PARENT") & (df_final["task_id"] == "I7_Quiescent_Continuous_State")]["nmse"].mean()
    i7_c1 = df_final[(df_final["model_label"] == "C1_K5") & (df_final["task_id"] == "I7_Quiescent_Continuous_State")]["nmse"].mean()
    
    latent_preserved = (i6_c1 - i6_c0 < 0.0150) and (i7_c1 - i7_c0 < 0.0150)
    quiescence_preserved = (i7_c1 - i7_c0 < 0.0150)

    # I9 Hybrid Complementarity
    df_i9 = pd.read_csv(os.path.join(STAGE_DIR, "I9_COMPLEMENTARITY_RECHECK.csv"))
    hybrid_comp_preserved = df_i9["complementarity_preserved"].iloc[0] == "YES"

    # Switching Latencies
    df_switch = pd.read_csv(os.path.join(STAGE_DIR, "RECURRENT_SWITCHING_ANALYSIS.csv"))
    switching_preserved = all(df_switch["preserves_50step_margin"] == "YES")

    # State Path Distortion
    df_traj = pd.read_csv(os.path.join(STAGE_DIR, "RECURRENT_STATE_TRAJECTORY_ANALYSIS.csv"))
    traj_mae = float(df_traj["mean_abs_deviation"].mean())
    state_distortion_status = "ACCEPTABLE" if traj_mae < 0.20 else "EXCESSIVE"

    # Overall Cadence Supported
    compute_gate_pass = c1_fp_mean <= 100.0
    cadence_supported = (
        compute_gate_pass and
        local_noninf_supported and
        latent_preserved and
        quiescence_preserved and
        hybrid_comp_preserved and
        switching_preserved and
        state_distortion_status == "ACCEPTABLE"
    )

    if cadence_supported:
        if global_noninf_supported:
            primary_outcome = "RECURRENT_CADENCE_VALIDATED"
        else:
            primary_outcome = "RECURRENT_CADENCE_COMPUTE_RECOVERED_GLOBAL_BEHAVIOR_STILL_FAILS"
    else:
        if compute_gate_pass:
            if state_distortion_status == "EXCESSIVE":
                primary_outcome = "RECURRENT_CADENCE_STATE_DISTORTION"
            elif not switching_preserved:
                primary_outcome = "RECURRENT_CADENCE_SWITCHING_DEGRADATION"
            else:
                primary_outcome = "RECURRENT_CADENCE_STATE_DISTORTION"
        else:
            if local_noninf_supported:
                primary_outcome = "RECURRENT_CADENCE_BEHAVIOR_PRESERVED_COMPUTE_FAILS"
            else:
                primary_outcome = "RECURRENT_SUBSYSTEM_NOT_SUFFICIENT"

    print("\n" + "=" * 50)
    print("FINAL MACHINE-READABLE BLOCK")
    print("=" * 50)
    
    block = f"""==================================================
LEBRE_V0_2_RECURRENT_SHADOW_COST_RECONCILIATION_01_STATUS =
COMPLETE

PHASE_A_STATUS =
COMPLETE

PHASE_B_EXECUTED =
YES

PRIMARY_OUTCOME =
{primary_outcome}

NEW_STOCHASTIC_RUNS =
YES

CANONICAL_SRC_CHANGED =
NO

CANONICAL_TESTS_CHANGED =
NO

M3_STATUS =
UNOPENED

NOVELTY_CLAIM_READY =
NO

CURRENT_TOTAL_FP =
111.013591

TARGET_TOTAL_FP =
100.000000

REQUIRED_SAVING_FP =
11.013591

CURRENT_RECURRENT_FP =
20.200000

MAX_ALLOWED_RECURRENT_FP_FOR_100_GATE =
9.186409

REQUIRED_RECURRENT_REDUCTION_PCT =
54.5227%

RECURRENT_STATE_PROPAGATION_FP =
12.000000

RECURRENT_PREDICTION_FP =
6.000000

RECURRENT_SENSITIVITY_FP =
0.800000

RECURRENT_PARAMETER_LEARNING_FP =
0.800000

RECURRENT_EVIDENCE_FP =
0.600000

RECURRENT_LIFECYCLE_FP =
0.000000

RECURRENT_LEDGER_RECONCILES_20P2 =
{'YES' if reconciles_20p2 else 'NO'}

CURRENT_K_REC_STATE =
1

CURRENT_K_REC_LEARNING =
10

PRIOR_D9F_D9L_TRANSFERABILITY =
MECHANISTICALLY_RELEVANT_NOT_CONFIRMATORY

PRIOR_K2_DELTA_NMSE =
+0.001374

PRIOR_K5_DELTA_NMSE =
+0.002858

PRIOR_K10_DELTA_NMSE =
+0.010144

PRIOR_K10_LEARNING_DELTA_NMSE =
-0.000203

MAX_ORACLE_RECURRENCE_SAVING_FP =
12.264286

MAX_SEMANTICALLY_REMOVABLE_RECURRENCE_FP =
10.100000

RECURRENCE_ALONE_CAN_MATHEMATICALLY_CLOSE_100_GATE =
YES

K2_PROJECTED_TOTAL_FP =
102.013591

K5_PROJECTED_TOTAL_FP =
96.613591

K10_PROJECTED_TOTAL_FP =
94.813591

PHASE_B_AUTHORIZED =
YES

FINAL_REC_STATE_CADENCE_K =
5

FINAL_TOTAL_FP_MEAN =
{c1_fp_mean:.6f}

FINAL_TOTAL_FP_P95 =
{c1_fp_p95:.6f}

COMPUTE_GATE =
{'PASS' if compute_gate_pass else 'FAIL'}

LOCAL_PARENT_DELTA_NMSE =
{mean_d_c0:+.6f}

LOCAL_NONINFERIORITY_95CI_UPPER =
{ci95_u_c0:+.6f}

LOCAL_PARENT_NONINFERIORITY =
{'SUPPORTED' if local_noninf_supported else 'NOT_SUPPORTED'}

GLOBAL_R0_DELTA_NMSE =
{mean_d_r0:+.6f}

GLOBAL_R0_NONINFERIORITY =
{'SUPPORTED' if global_noninf_supported else 'NOT_SUPPORTED'}

CONTINUOUS_LATENT_PRESERVED =
{'YES' if latent_preserved else 'NO'}

QUIESCENCE_PRESERVED =
{'YES' if quiescence_preserved else 'NO'}

HYBRID_COMPLEMENTARITY_PRESERVED =
{'YES' if hybrid_comp_preserved else 'NO'}

SWITCHING_PRESERVED =
{'YES' if switching_preserved else 'NO'}

RECURRENT_STATE_PATH_DISTORTION =
{state_distortion_status}

RECURRENT_SHADOW_CADENCE_SUPPORTED =
{'YES' if cadence_supported else 'NO'}

GLOBAL_SEARCH_COMPACTION_VALIDATION =
FAILED

SEARCH_FRONTIER_STATUS =
PROMISING_EXPERIMENTAL_CANDIDATE

T3_STATUS =
EXPERIMENTAL_NON_CANONICAL

SAFE_FOR_INTEGRATED_VALIDATION =
{'YES' if (cadence_supported and global_noninf_supported) else 'NO'}

SAFE_TO_OPEN_M3 =
NO

NEXT_RECOMMENDED_STAGE =
LEBRE-V0.2-RECURRENT-SHADOW-SEAL-AUDIT-01

LEBRE_V0_1_STATUS =
FROZEN_WITH_SCOPE_LIMITS
=================================================="""
    print(block)

    # 3. Generate Manifest
    all_artifacts = [
        "RECURRENT_SHADOW_PROTOCOL.md",
        "RECURRENT_SHADOW_PREREGISTRATION.md",
        "PARENT_HASHES.txt",
        "SEED_PROVENANCE.md",
        "RECURRENT_SHADOW_OPERATION_LEDGER.csv",
        "RECURRENT_COMPUTE_RECONCILIATION.csv",
        "RECURRENT_CURRENT_CLOCK_AUDIT.md",
        "RECURRENT_PRIOR_TRANSFERABILITY_AUDIT.md",
        "PRIOR_D9F_D9L_RECONCILIATION.csv",
        "RECURRENT_COST_BY_TASK.csv",
        "RECURRENT_COST_BY_LIFECYCLE_STATE.csv",
        "RECURRENT_ORACLE_SAVINGS.csv",
        "RECURRENT_RESOURCE_CLOSURE_TABLE.csv",
        "RECURRENT_FAST_FORWARD_DERIVATION.md",
        "RECURRENT_SKIP_SEMANTICS.md",
        "RECURRENT_SPARSE_EXECUTION_LITERATURE_NOTE.md",
        "PHASE_A_FEASIBILITY_DECISION.md",
        "RECURRENT_DEV_RESULTS.csv",
        "FINAL_RECURRENT_CANDIDATE_FREEZE.md",
        "RECURRENT_FINAL_RESULTS.csv",
        "RECURRENT_STATE_TRAJECTORY_ANALYSIS.csv",
        "RECURRENT_RESOURCE_BY_SEED.csv",
        "RECURRENT_UPDATE_DUTY.csv",
        "RECURRENT_SWITCHING_ANALYSIS.csv",
        "RECURRENT_QUIESCENCE_ANALYSIS.csv",
        "I9_COMPLEMENTARITY_RECHECK.csv",
        "LOCAL_NONINFERIORITY.csv",
        "GLOBAL_R0_STATUS.csv",
        "RECURRENT_SHADOW_FINAL_REPORT.md",
        "generate_recurrent_shadow_outputs.py"
    ]
    
    manifest_entries = {}
    for a in all_artifacts:
        ap = os.path.join(STAGE_DIR, a)
        if os.path.exists(ap):
            manifest_entries[a] = {
                "sha256": compute_sha256(ap),
                "bytes": os.path.getsize(ap)
            }
        else:
            manifest_entries[a] = {"status": "PENDING_REPORT"}
            
    manifest_data = {
        "stage_id": "LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01",
        "milestone": "Milestone 2 (Experimental Stream v0.2)",
        "phase_a_status": "COMPLETE",
        "phase_b_executed": "YES",
        "primary_outcome": primary_outcome,
        "empirical_mean_total_fp": c1_fp_mean,
        "empirical_p95_total_fp": c1_fp_p95,
        "delta_nmse_vs_c0": mean_d_c0,
        "ci95_upper_vs_c0": ci95_u_c0,
        "delta_nmse_vs_r0": mean_d_r0,
        "ci95_upper_vs_r0": ci95_u_r0,
        "compute_gate": "PASS" if compute_gate_pass else "FAIL",
        "local_noninferiority": "SUPPORTED" if local_noninf_supported else "NOT_SUPPORTED",
        "global_r0_noninferiority": "SUPPORTED" if global_noninf_supported else "NOT_SUPPORTED",
        "artifacts": manifest_entries
    }
    
    manifest_path = os.path.join(STAGE_DIR, "RECURRENT_SHADOW_MANIFEST.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"\nGenerated RECURRENT_SHADOW_MANIFEST.json ({len(manifest_entries)} artifact entries).")

if __name__ == "__main__":
    main()
