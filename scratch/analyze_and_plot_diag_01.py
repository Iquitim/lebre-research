#!/usr/bin/env python3
"""
Analysis and Visualization Engine for LEBRE-DIAG-01.
Reads seed results and promotion events, computes 10,000 bootstrap CIs,
and generates Figures F1–F8.
"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from typing import Tuple, List, Dict, Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

EXP_DIR = ROOT / "experiments" / "LEBRE-DIAG-01"
FIG_DIR = EXP_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial"]
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.labelsize"] = 11

def bootstrap_ci(data: np.ndarray, n_boot: int = 10000, alpha: float = 0.05) -> Tuple[float, float, float]:
    """Computes mean and 95% percentile bootstrap CI."""
    clean = data[np.isfinite(data)]
    if len(clean) == 0:
        return 0.0, 0.0, 0.0
    mean_val = float(np.mean(clean))
    boot_means = np.empty(n_boot)
    n = len(clean)
    rng = np.random.RandomState(42)
    for i in range(n_boot):
        sample = rng.choice(clean, size=n, replace=True)
        boot_means[i] = np.mean(sample)
    low = float(np.percentile(boot_means, 100.0 * (alpha / 2.0)))
    high = float(np.percentile(boot_means, 100.0 * (1.0 - alpha / 2.0)))
    return mean_val, low, high

def main():
    seed_csv = EXP_DIR / "LEBRE_DIAG_01_SEED_RESULTS.csv"
    event_csv = EXP_DIR / "LEBRE_DIAG_01_PROMOTION_EVENTS.csv"
    
    if not seed_csv.exists() or not event_csv.exists():
        print("Data files not ready yet.")
        return
        
    df_seeds = pd.read_csv(seed_csv)
    df_events = pd.read_csv(event_csv)
    
    print(f"Loaded {len(df_seeds)} seed results and {len(df_events)} promotion events.")
    
    tasks_primary = ["A2_Single_Delayed_Dependency", "A3_Multiple_Dispersed_Delays", "A4_Long_Delay_Scaling"]
    tasks_control = ["A5_Set_Reset_Quiescent_Memory", "A7_Extended_Poisson_Quiescence", "A8_Abrupt_Tri_Regime_Transition"]
    ALL_TASKS = tasks_primary + tasks_control
    
    # -------------------------------------------------------------
    # F1: A2-A4 LEBRE vs NO_REC_BIRTH paired NMSE
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    x_positions = np.arange(len(tasks_primary))
    width = 0.35
    
    froz_means, froz_errs = [], []
    no_means, no_errs = [], []
    
    for t_id in tasks_primary:
        sub_f = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_FROZEN")]["nmse"].values
        sub_n = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_NO_REC_BIRTH")]["nmse"].values
        
        mf, lf, hf = bootstrap_ci(sub_f)
        mn, ln, hn = bootstrap_ci(sub_n)
        
        froz_means.append(mf)
        froz_errs.append([[mf - lf], [hf - mf]])
        no_means.append(mn)
        no_errs.append([[mn - ln], [hn - mn]])
        
    froz_errs = np.array(froz_errs).squeeze().T
    no_errs = np.array(no_errs).squeeze().T
    
    ax.bar(x_positions - width/2, froz_means, width, yerr=froz_errs, capsize=4, label="LEBRE_FROZEN (Recurrence Active)", color="#1E40AF", alpha=0.85)
    ax.bar(x_positions + width/2, no_means, width, yerr=no_errs, capsize=4, label="LEBRE_NO_REC_BIRTH (Ablation)", color="#059669", alpha=0.85)
    
    ax.axhline(1.0, color="#DC2626", linestyle="--", linewidth=1.2, label="Trivial Baseline (NMSE = 1.0)")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(["A2: Single Delay (lag=4)", "A3: Multiple Delays (lag=2,8)", "A4: Long Delay (lag=30)"])
    ax.set_ylabel("Test NMSE (Mean ± 95% Bootstrap CI)")
    ax.set_title("Figure F1: Primary Diagnostic Tasks A2–A4 — LEBRE vs NO_REC_BIRTH", fontweight="bold")
    ax.set_ylim(0.95, 1.20)
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F1_A2_A4_paired_nmse.png", dpi=300)
    plt.close(fig)
    print("Generated F1_A2_A4_paired_nmse.png")
    
    # -------------------------------------------------------------
    # F2: Probation Gain vs Post-Promotion Gain
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    promoted = df_events[df_events["promoted"] == True].dropna(subset=["G_prob", "G_post_250"])
    
    colors = {"A2_Single_Delayed_Dependency": "#1E40AF", "A3_Multiple_Dispersed_Delays": "#0D9488", "A4_Long_Delay_Scaling": "#F59E0B",
              "A5_Set_Reset_Quiescent_Memory": "#7C3AED", "A7_Extended_Poisson_Quiescence": "#EC4899", "A8_Abrupt_Tri_Regime_Transition": "#10B981"}
    
    for t_id in ALL_TASKS:
        sub = promoted[promoted["task_id"] == t_id]
        if len(sub) > 0:
            ax.scatter(sub["G_prob"], sub["G_post_250"], label=t_id.split("_")[0], color=colors.get(t_id, "#4B5563"), alpha=0.6, edgecolors="none", s=25)
            
    ax.axhline(0.0, color="#DC2626", linestyle="--", linewidth=1.0)
    ax.axvline(0.05, color="#6B7280", linestyle=":", linewidth=1.0, label="Promotion Threshold (0.05)")
    ax.set_xlabel("Probation Gain Statistic (G_prob)")
    ax.set_ylabel("Realized Post-Promotion Gain at H=250 (G_post_250)")
    ax.set_title("Figure F2: Probation Gain vs Realized Post-Promotion Gain", fontweight="bold")
    ax.legend(title="Task", loc="upper left", frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F2_probation_vs_post_gain.png", dpi=300)
    plt.close(fig)
    print("Generated F2_probation_vs_post_gain.png")
    
    # -------------------------------------------------------------
    # F3: Promotion Outcome Distribution
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5))
    traj_counts = []
    prom_only = df_events[df_events["promoted"] == True]
    trajectories = ["STABLE_POSITIVE", "DECAYING_POSITIVE", "SIGN_FLIP", "IMMEDIATE_NEGATIVE", "INDETERMINATE"]
    traj_colors = ["#059669", "#3B82F6", "#F59E0B", "#DC2626", "#9CA3AF"]
    
    task_labels = [t.split("_")[0] for t in ALL_TASKS]
    data_matrix = np.zeros((len(trajectories), len(ALL_TASKS)))
    
    for j, t_id in enumerate(ALL_TASKS):
        sub = prom_only[prom_only["task_id"] == t_id]
        tot = len(sub)
        if tot > 0:
            for i, traj in enumerate(trajectories):
                cnt = len(sub[sub["trajectory"] == traj])
                data_matrix[i, j] = cnt / tot * 100.0
                
    bottom = np.zeros(len(ALL_TASKS))
    for i, traj in enumerate(trajectories):
        ax.bar(task_labels, data_matrix[i], bottom=bottom, label=traj, color=traj_colors[i], width=0.55)
        bottom += data_matrix[i]
        
    ax.set_ylabel("Percentage of Promoted Candidates (%)")
    ax.set_title("Figure F3: Promotion Trajectory Classification across Tasks", fontweight="bold")
    ax.legend(loc="upper right", frameon=True)
    ax.set_ylim(0, 105)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F3_promotion_outcome_distribution.png", dpi=300)
    plt.close(fig)
    print("Generated F3_promotion_outcome_distribution.png")
    
    # -------------------------------------------------------------
    # F4: Cumulative Counterfactual Regret after Promotion
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    # Plot mean regret per task for primary tasks
    for t_id in tasks_primary:
        sub = df_events[(df_events["task_id"] == t_id) & (df_events["promoted"] == True)]
        r_vals = sub["R_harm"].dropna().values
        if len(r_vals) > 0:
            ax.hist(r_vals, bins=25, alpha=0.5, label=f"{t_id.split('_')[0]} (Mean={np.mean(r_vals):.1f})")
    ax.set_xlabel("Cumulative Excess Loss during Harmful Retention (R_harm)")
    ax.set_ylabel("Candidate Count")
    ax.set_title("Figure F4: Distribution of Harmful Retention Regret per Promoted Unit", fontweight="bold")
    ax.legend(frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F4_cumulative_counterfactual_regret.png", dpi=300)
    plt.close(fig)
    print("Generated F4_cumulative_counterfactual_regret.png")
    
    # -------------------------------------------------------------
    # F5: Harmful-State Retention Duration
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    for t_id in tasks_primary:
        sub = df_events[(df_events["task_id"] == t_id) & (df_events["promoted"] == True) & (df_events["t_evict_response"].notna())]
        lat = sub["t_evict_response"].values
        if len(lat) > 0:
            ax.hist(lat, bins=25, alpha=0.5, label=f"{t_id.split('_')[0]} (Mean={np.mean(lat):.0f} steps)")
    ax.set_xlabel("Eviction Response Latency (Steps from Harm Onset to Eviction)")
    ax.set_ylabel("Candidate Count")
    ax.set_title("Figure F5: Controller Retention Duration of Deteriorated States", fontweight="bold")
    ax.legend(frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F5_harmful_retention_duration.png", dpi=300)
    plt.close(fig)
    print("Generated F5_harmful_retention_duration.png")
    
    # -------------------------------------------------------------
    # F6: Oracle Eviction Recoverable Regret
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(tasks_primary))
    w = 0.25
    
    froz_v = [df_seeds[(df_seeds["task_id"] == t) & (df_seeds["variant"] == "LEBRE_FROZEN")]["nmse"].mean() for t in tasks_primary]
    orac_v = [df_seeds[(df_seeds["task_id"] == t) & (df_seeds["variant"] == "LEBRE_ORACLE_HARM_STOP")]["nmse"].mean() for t in tasks_primary]
    no_v   = [df_seeds[(df_seeds["task_id"] == t) & (df_seeds["variant"] == "LEBRE_NO_REC_BIRTH")]["nmse"].mean() for t in tasks_primary]
    
    ax.bar(x_pos - w, froz_v, w, label="LEBRE_FROZEN", color="#1E40AF", alpha=0.85)
    ax.bar(x_pos, orac_v, w, label="LEBRE_ORACLE_HARM_STOP", color="#F59E0B", alpha=0.85)
    ax.bar(x_pos + w, no_v, w, label="LEBRE_NO_REC_BIRTH", color="#059669", alpha=0.85)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels([t.split("_")[0] for t in tasks_primary])
    ax.set_ylabel("Test NMSE")
    ax.set_title("Figure F6: Oracle Immediate Eviction vs Frozen vs No-Birth", fontweight="bold")
    ax.set_ylim(0.95, 1.20)
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F6_oracle_eviction_recovery.png", dpi=300)
    plt.close(fig)
    print("Generated F6_oracle_eviction_recovery.png")
    
    # -------------------------------------------------------------
    # F7: Positive-Control Recurrence Value
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(tasks_control))
    w = 0.35
    
    cf_means, cf_errs = [], []
    cn_means, cn_errs = [], []
    
    for t_id in tasks_control:
        sf = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_FROZEN")]["nmse"].values
        sn = df_seeds[(df_seeds["task_id"] == t_id) & (df_seeds["variant"] == "LEBRE_NO_REC_BIRTH")]["nmse"].values
        
        mf, lf, hf = bootstrap_ci(sf)
        mn, ln, hn = bootstrap_ci(sn)
        
        cf_means.append(mf)
        cf_errs.append([[mf - lf], [hf - mf]])
        cn_means.append(mn)
        cn_errs.append([[mn - ln], [hn - mn]])
        
    cf_errs = np.array(cf_errs).squeeze().T
    cn_errs = np.array(cn_errs).squeeze().T
    
    ax.bar(x_pos - w/2, cf_means, w, yerr=cf_errs, capsize=4, label="LEBRE_FROZEN (Recurrence Active)", color="#7C3AED", alpha=0.85)
    ax.bar(x_pos + w/2, cn_means, w, yerr=cn_errs, capsize=4, label="LEBRE_NO_REC_BIRTH (Ablation)", color="#6B7280", alpha=0.85)
    
    ax.set_xticks(x_pos)
    ax.set_xticklabels(["A5: Set/Reset Quiescence", "A7: Poisson Quiescence", "A8: Tri-Regime Shift"])
    ax.set_ylabel("Test NMSE (Mean ± 95% Bootstrap CI)")
    ax.set_title("Figure F7: Positive Controls — Recurrence Essential & Strongly Beneficial", fontweight="bold")
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F7_positive_control_value.png", dpi=300)
    plt.close(fig)
    print("Generated F7_positive_control_value.png")
    
    # -------------------------------------------------------------
    # F8: Compute Cost Attributable to Recurrent Lifecycle
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5))
    x_pos = np.arange(len(ALL_TASKS))
    w = 0.25
    
    flops_froz = [df_seeds[(df_seeds["task_id"] == t) & (df_seeds["variant"] == "LEBRE_FROZEN")]["mean_flops"].mean() for t in ALL_TASKS]
    flops_shad = [df_seeds[(df_seeds["task_id"] == t) & (df_seeds["variant"] == "LEBRE_SHADOW_ONLY")]["mean_flops"].mean() for t in ALL_TASKS]
    flops_no   = [df_seeds[(df_seeds["task_id"] == t) & (df_seeds["variant"] == "LEBRE_NO_REC_BIRTH")]["mean_flops"].mean() for t in ALL_TASKS]
    
    ax.bar(x_pos - w, flops_froz, w, label="LEBRE_FROZEN (Full Lifecycle)", color="#1E40AF", alpha=0.85)
    ax.bar(x_pos, flops_shad, w, label="LEBRE_SHADOW_ONLY (Probation Overhead)", color="#0D9488", alpha=0.85)
    ax.bar(x_pos + w, flops_no, w, label="LEBRE_NO_REC_BIRTH (Base Linear)", color="#059669", alpha=0.85)
    
    ax.axhline(100.0, color="#DC2626", linestyle="--", linewidth=1.2, label="R2-FLOP Budget Ceiling (100 FLOPs/step)")
    ax.set_xticks(x_pos)
    ax.set_xticklabels([t.split("_")[0] for t in ALL_TASKS])
    ax.set_ylabel("Mean Operational Compute (FLOPs/step)")
    ax.set_title("Figure F8: Operational Compute Overhead Attributable to Lifecycle Phases", fontweight="bold")
    ax.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F8_compute_cost_breakdown.png", dpi=300)
    plt.close(fig)
    print("Generated F8_compute_cost_breakdown.png")
    
    print("\nAll 8 figures successfully generated and saved to figures/!")

if __name__ == "__main__":
    main()
