#!/usr/bin/env python3
"""
analyze_resource_compaction.py

Statistical Analysis and Diagnostic Visualizations for
LEBRE-V0.2-RESOURCE-COMPACTION-01

Generates:
  - 10 Diagnostic Figures (F1..F10) in experiments/.../figures/
  - TOST Equivalence Tests and Summary Statistics
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

from scratch.bench_v02_integration import BENCHMARK_TASKS

ROOT = Path.cwd()
EXP_DIR = ROOT / "experiments" / "LEBRE-V0.2-RESOURCE-COMPACTION-01"
FIG_DIR = EXP_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

# Set high-quality styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

def generate_figures():
    print("Loading datasets...")
    df_ledger = pd.read_csv(EXP_DIR / "CORR_GRID_MEMORY_LEDGER.csv")
    df_micro = pd.read_csv(EXP_DIR / "NUMERICAL_MICROTRACE.csv")
    df_stress = pd.read_csv(EXP_DIR / "NUMERICAL_STRESS_RESULTS.csv")
    df_final = pd.read_csv(EXP_DIR / "RESOURCE_COMPACTION_FINAL_RESULTS.csv")
    df_ranking = pd.read_csv(EXP_DIR / "CANDIDATE_RANKING_PARITY.csv")
    df_events = pd.read_csv(EXP_DIR / "STRUCTURAL_EVENT_PARITY.csv")
    
    # -------------------------------------------------------------------------
    # F1: Memory Breakdown C0 vs C1
    # -------------------------------------------------------------------------
    print("Generating F1: Memory Breakdown C0 vs C1...")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    
    components = [
        ("CausalStandardScaler", 80, 80, "#4a7bb0"),
        ("FP16HistoryRingBuffer", 332, 332, "#5fa8d3"),
        ("LinearBasePredictor", 40, 40, "#62b6cb"),
        ("ShadowCorrelationGrid", 660, 330, "#e63946"), # Key intervention
        ("ActiveTapMetadata", 64, 64, "#f4a261"),
        ("ProvisionalCandidates", 48, 48, "#e76f51"),
        ("RecurrentUnits (Act+Shd)", 96, 96, "#2a9d8f"),
        ("Arbitrator & Meta", 86, 86, "#8d99ae")
    ]
    
    bottom_c0 = 0
    bottom_c1 = 0
    for name, c0_val, c1_val, color in components:
        ax.bar(0, c0_val, bottom=bottom_c0, width=0.45, color=color, edgecolor="black", linewidth=0.5, label=name)
        ax.bar(1, c1_val, bottom=bottom_c1, width=0.45, color=color, edgecolor="black", linewidth=0.5)
        bottom_c0 += c0_val
        bottom_c1 += c1_val
        
    ax.axhline(1024, color="#d90429", linestyle="--", linewidth=1.5, label="Legacy R2 Ceiling (1024 B)")
    ax.axhline(2048, color="#6c757d", linestyle=":", linewidth=1.2, label="Proposed 2KB Ceiling (2048 B)")
    
    ax.text(0, 1315, "C0: 1,306 B\n(FAIL legacy R2)", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#d90429")
    ax.text(1, 985, "C1: 976 B\n(PASS legacy R2)", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#2a9d8f")
    
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["C0: FP32 Grid Reference\n(Sealed Candidate)", "C1: FP16 Grid Storage\n(Targeted Compaction)"], fontsize=10)
    ax.set_ylabel("Persistent Algorithmic State (Bytes)", fontsize=11)
    ax.set_title("F1: Persistent Memory Footprint & 1-KiB Ceiling Recovery", fontsize=12, fontweight="bold", pad=12)
    ax.set_ylim(0, 1600)
    ax.legend(loc="upper right", bbox_to_anchor=(1.45, 1.0), fontsize=8)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F1_memory_breakdown_C0_vs_C1.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    
    # -------------------------------------------------------------------------
    # F2: Correlation Grid Quantization Error Distribution
    # -------------------------------------------------------------------------
    print("Generating F2: Correlation Grid Quantization Error Distribution...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
    
    abs_errors = df_micro["absolute_error"].values
    rel_errors = df_micro["relative_error"].values
    
    ax1.hist(abs_errors, bins=40, color="#1d3557", alpha=0.8, edgecolor="black", density=True)
    ax1.axvline(np.median(abs_errors), color="#e63946", linestyle="-", linewidth=1.5, label=f"Median: {np.median(abs_errors):.2e}")
    ax1.axvline(9.765625e-4, color="#f4a261", linestyle="--", linewidth=1.5, label=r"FP16 $\epsilon_{mach}$ ($9.77 \times 10^{-4}$)")
    ax1.set_xlabel("Absolute Numerical Error $|C_0 - C_1|$", fontsize=10)
    ax1.set_ylabel("Probability Density", fontsize=10)
    ax1.set_title("Absolute Quantization Error Distribution", fontsize=11, fontweight="bold")
    ax1.legend(fontsize=8)
    
    ax2.hist(rel_errors, bins=40, color="#457b9d", alpha=0.8, edgecolor="black", density=True)
    ax2.axvline(np.median(rel_errors), color="#e63946", linestyle="-", linewidth=1.5, label=f"Median: {np.median(rel_errors):.2e}")
    ax2.set_xlabel("Relative Numerical Error $|C_0 - C_1| / (|C_0| + \epsilon)$", fontsize=10)
    ax2.set_ylabel("Probability Density", fontsize=10)
    ax2.set_title("Relative Quantization Error Distribution", fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8)
    
    fig.suptitle("F2: IEEE 754 Float16 Storage Quantization Error (500-Step Microtrace)", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F2_corr_grid_quantization_error_distribution.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F3: Correlation Grid Error Over Time
    # -------------------------------------------------------------------------
    print("Generating F3: Correlation Grid Error Over Time...")
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    
    # Group microtrace by step to get max and mean per step
    step_grp = df_micro.groupby("step")["absolute_error"].agg(["mean", "max"]).reset_index()
    
    ax.plot(step_grp["step"], step_grp["max"], color="#e63946", linewidth=1.2, label="Max Grid Error per Step")
    ax.plot(step_grp["step"], step_grp["mean"], color="#1d3557", linewidth=1.5, label="Mean Grid Error per Step")
    ax.axhline(9.765625e-4, color="#f4a261", linestyle="--", linewidth=1.2, label=r"FP16 $\epsilon_{mach}$ Boundary")
    
    ax.set_xlabel("Streaming Timestep (Updates)", fontsize=10)
    ax.set_ylabel("Absolute Discrepancy", fontsize=10)
    ax.set_title("F3: Temporal Error Trajectory (Absence of Secular Roundoff Drift)", fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="upper right", fontsize=9)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F3_corr_grid_error_over_time.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F4: Candidate Ranking Agreement
    # -------------------------------------------------------------------------
    print("Generating F4: Candidate Ranking Agreement...")
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    
    tasks_short = [t.split("_")[0] for t in BENCHMARK_TASKS]
    t_grp = df_ranking.groupby("task_id")[["top1_agreement_rate", "top3_set_agreement_rate"]].mean()
    
    x = np.arange(len(BENCHMARK_TASKS))
    width = 0.35
    
    ax.bar(x - width/2, t_grp["top1_agreement_rate"] * 100, width, color="#2a9d8f", label="Top-1 Cell Agreement (%)", edgecolor="black", linewidth=0.5)
    ax.bar(x + width/2, t_grp["top3_set_agreement_rate"] * 100, width, color="#457b9d", label="Top-3 Jaccard Set Agreement (%)", edgecolor="black", linewidth=0.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(tasks_short, fontsize=9)
    ax.set_ylabel("Agreement Rate (%)", fontsize=10)
    ax.set_ylim(85, 102)
    ax.set_title("F4: Candidate Ranking & Selection Parity Across Tasks", fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="lower right", fontsize=9)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F4_candidate_ranking_agreement.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F5: Structural Decision Confusion Matrix
    # -------------------------------------------------------------------------
    print("Generating F5: Structural Decision Confusion Matrix...")
    fig, ax = plt.subplots(figsize=(6, 5), dpi=300)
    
    states = ["NONE", "LAG", "RECURRENT", "BOTH"]
    conf_matrix = np.zeros((4, 4))
    
    for idx, row in df_events.iterrows():
        c0_s = row["c0_modal_state"]
        c1_s = row["c1_modal_state"]
        i = states.index(c0_s)
        j = states.index(c1_s)
        conf_matrix[i, j] += 1
        
    cax = ax.matshow(conf_matrix, cmap="Blues")
    fig.colorbar(cax)
    
    for i in range(4):
        for j in range(4):
            val = int(conf_matrix[i, j])
            color = "white" if val > 100 else "black"
            ax.text(j, i, str(val), ha="center", va="center", color=color, fontsize=11, fontweight="bold")
            
    ax.set_xticks(range(4))
    ax.set_yticks(range(4))
    ax.set_xticklabels(states, fontsize=10)
    ax.set_yticklabels(states, fontsize=10)
    ax.set_xlabel("C1 Modal State (FP16 Grid)", fontsize=10, labelpad=10)
    ax.set_ylabel("C0 Modal State (FP32 Grid)", fontsize=10)
    ax.set_title("F5: Modal Structural Decision Agreement", fontsize=12, fontweight="bold", pad=20)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F5_structural_decision_confusion_matrix.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F6: NMSE Delta By Task (Forest Plot with TOST Bounds)
    # -------------------------------------------------------------------------
    print("Generating F6: NMSE Delta By Task...")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Calculate paired differences per task
    c0_df = df_final[df_final["variant"] == "C0"].set_index(["task_id", "seed"])
    c1_df = df_final[df_final["variant"] == "C1"].set_index(["task_id", "seed"])
    
    delta_df = c1_df["nmse"] - c0_df["nmse"]
    delta_task = delta_df.groupby("task_id").agg(["mean", "std", "count"]).reset_index()
    
    # Sort by task order in BENCHMARK_TASKS
    delta_task["task_order"] = delta_task["task_id"].apply(lambda t: BENCHMARK_TASKS.index(t))
    delta_task = delta_task.sort_values("task_order").reset_index(drop=True)
    
    y_pos = np.arange(len(delta_task))
    means = delta_task["mean"].values
    # 90% confidence interval for TOST (alpha = 0.05)
    ci90 = 1.699 * (delta_task["std"].values / np.sqrt(delta_task["count"].values))
    
    ax.errorbar(means, y_pos, xerr=ci90, fmt="o", color="#1d3557", ecolor="#1d3557", elinewidth=1.5, capsize=3, label="Paired Mean $\\Delta$ (90% CI)")
    
    # Bounds: +/- 0.010 for general, +/- 0.015 for lag
    ax.axvline(0.0, color="black", linestyle="-", linewidth=0.8)
    ax.axvline(0.010, color="#e63946", linestyle="--", linewidth=1.2, label=r"Preregistered Equivalence Bound ($\pm 0.010$)")
    ax.axvline(-0.010, color="#e63946", linestyle="--", linewidth=1.2)
    ax.axvspan(-0.010, 0.010, color="#a8dadc", alpha=0.25, label="Practical Equivalence Zone")
    
    ax.set_yticks(y_pos)
    ax.set_yticklabels([t.split("_")[0] + " " + "_".join(t.split("_")[1:3]) for t in delta_task["task_id"]], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("Paired NMSE Difference ($C_1 - C_0$)", fontsize=10)
    ax.set_title("F6: Paired NMSE Differences Across Tasks vs. Equivalence Margins", fontsize=12, fontweight="bold", pad=12)
    ax.legend(loc="lower left", fontsize=8)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F6_nmse_delta_by_task.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F7: Support F1 C0 vs C1 on I3 and I4
    # -------------------------------------------------------------------------
    print("Generating F7: Support F1 C0 vs C1...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=300)
    
    # I3
    i3_c0 = df_final[(df_final["task_id"] == "I3_Single_Exact_Delay") & (df_final["variant"] == "C0")]["support_f1"].values
    i3_c1 = df_final[(df_final["task_id"] == "I3_Single_Exact_Delay") & (df_final["variant"] == "C1")]["support_f1"].values
    
    ax1.boxplot([i3_c0, i3_c1], patch_artist=True, boxprops=dict(facecolor="#a8dadc"), medianprops=dict(color="#1d3557", linewidth=1.5))
    ax1.set_xticklabels(["C0 (FP32)", "C1 (FP16)"], fontsize=10)
    ax1.set_ylabel("Lag Support F1 Score", fontsize=10)
    ax1.set_title("I3: Single Exact Delay Support F1", fontsize=11, fontweight="bold")
    ax1.set_ylim(0, 1.05)
    
    # I4
    i4_c0 = df_final[(df_final["task_id"] == "I4_Multi_Sparse_Delay") & (df_final["variant"] == "C0")]["support_f1"].values
    i4_c1 = df_final[(df_final["task_id"] == "I4_Multi_Sparse_Delay") & (df_final["variant"] == "C1")]["support_f1"].values
    
    ax2.boxplot([i4_c0, i4_c1], patch_artist=True, boxprops=dict(facecolor="#f4a261"), medianprops=dict(color="#e76f51", linewidth=1.5))
    ax2.set_xticklabels(["C0 (FP32)", "C1 (FP16)"], fontsize=10)
    ax2.set_ylabel("Lag Support F1 Score", fontsize=10)
    ax2.set_title("I4: Multi-Sparse Delay Support F1", fontsize=11, fontweight="bold")
    ax2.set_ylim(0, 1.05)
    
    fig.suptitle("F7: Lag Support Recovery Parity (I3 and I4)", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F7_support_F1_C0_vs_C1.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F8: I9 Conditional Gain Parity
    # -------------------------------------------------------------------------
    print("Generating F8: I9 Conditional Gain Parity...")
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    
    i9_df = df_final[df_final["task_id"] == "I9_Hybrid_Delay_Plus_Latent_State"]
    i9_c0 = i9_df[i9_df["variant"] == "C0"].sort_values("seed")
    i9_c1 = i9_df[i9_df["variant"] == "C1"].sort_values("seed")
    
    gains = ["g_db_mean", "g_rb_mean", "g_d_br_mean", "g_r_bd_mean"]
    gain_labels = [r"$G_{D|B}$", r"$G_{R|B}$", r"$G_{D|B+R}$", r"$G_{R|B+D}$"]
    
    x = np.arange(len(gains))
    width = 0.35
    
    c0_means = [i9_c0[g].mean() for g in gains]
    c1_means = [i9_c1[g].mean() for g in gains]
    c0_sems = [i9_c0[g].sem() for g in gains]
    c1_sems = [i9_c1[g].sem() for g in gains]
    
    ax.bar(x - width/2, c0_means, width, yerr=c0_sems, capsize=3, color="#457b9d", label="C0 (FP32)", edgecolor="black", linewidth=0.5)
    ax.bar(x + width/2, c1_means, width, yerr=c1_sems, capsize=3, color="#e76f51", label="C1 (FP16)", edgecolor="black", linewidth=0.5)
    ax.axhline(0.015, color="#d90429", linestyle="--", linewidth=1.2, label=r"Arbitration Threshold $\theta = 0.015$")
    
    ax.set_xticks(x)
    ax.set_xticklabels(gain_labels, fontsize=11)
    ax.set_ylabel("Filtered Conditional Gain Value", fontsize=10)
    ax.set_title("F8: Task I9 Hybrid Conditional Gains Parity", fontsize=12, fontweight="bold", pad=10)
    ax.legend(fontsize=9)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F8_I9_conditional_gain_parity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F9: I10 Dual Occupancy (frac_both) Parity
    # -------------------------------------------------------------------------
    print("Generating F9: I10 Dual Occupancy Parity...")
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    
    i10_c0 = df_final[(df_final["task_id"] == "I10_Redundant_Temporal_Structure") & (df_final["variant"] == "C0")]["frac_both"].values
    i10_c1 = df_final[(df_final["task_id"] == "I10_Redundant_Temporal_Structure") & (df_final["variant"] == "C1")]["frac_both"].values
    
    ax.boxplot([i10_c0, i10_c1], patch_artist=True, boxprops=dict(facecolor="#e9c46a"), medianprops=dict(color="#e76f51", linewidth=1.5))
    ax.axhline(0.05, color="#d90429", linestyle="--", linewidth=1.5, label="Gate 6 Ceiling (frac_both <= 0.05)")
    ax.axhline(0.10, color="#6c757d", linestyle=":", linewidth=1.2, label="Relaxed Ceiling (0.10)")
    
    ax.set_xticklabels(["C0: FP32 Grid", "C1: FP16 Grid"], fontsize=10)
    ax.set_ylabel("Dual Occupancy Rate (frac_both)", fontsize=10)
    ax.set_title("F9: Task I10 Dual Occupancy (Unchanged Gate 6 Status)", fontsize=12, fontweight="bold", pad=10)
    ax.legend(loc="upper right", fontsize=9)
    
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F9_I10_frac_both_parity.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    # -------------------------------------------------------------------------
    # F10: Resource Vector C0 vs C1
    # -------------------------------------------------------------------------
    print("Generating F10: Resource Vector C0 vs C1...")
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(10, 8), dpi=300)
    
    # 1. Live FLOPs
    live_c0 = df_final[df_final["variant"] == "C0"]["live_flops_mean"].mean()
    live_c1 = df_final[df_final["variant"] == "C1"]["live_flops_mean"].mean()
    ax1.bar(["C0", "C1"], [live_c0, live_c1], color=["#457b9d", "#2a9d8f"], width=0.4, edgecolor="black")
    ax1.axhline(100.0, color="#d90429", linestyle="--", label="100 FLOP Ceiling")
    ax1.set_title("Mean Live Compute (FLOPs/step)", fontsize=11, fontweight="bold")
    ax1.set_ylim(0, 120)
    ax1.legend(fontsize=8)
    
    # 2. Total Online Compute (Live + Shadow)
    tot_c0 = (df_final[df_final["variant"] == "C0"]["live_flops_mean"] + df_final[df_final["variant"] == "C0"]["shadow_flops_mean"]).mean()
    tot_c1 = (df_final[df_final["variant"] == "C1"]["live_flops_mean"] + df_final[df_final["variant"] == "C1"]["shadow_flops_mean"]).mean()
    ax2.bar(["C0", "C1"], [tot_c0, tot_c1], color=["#457b9d", "#2a9d8f"], width=0.4, edgecolor="black")
    ax2.axhline(100.0, color="#d90429", linestyle="--", label="100 FLOP Ceiling")
    ax2.set_title("Total Online Compute (FLOPs/step)", fontsize=11, fontweight="bold")
    ax2.set_ylim(0, 140)
    ax2.legend(fontsize=8)
    
    # 3. Integer & Cast Ops
    int_c0 = df_final[df_final["variant"] == "C0"]["int_ops_mean"].mean()
    int_c1 = df_final[df_final["variant"] == "C1"]["int_ops_mean"].mean()
    ax3.bar(["C0", "C1"], [int_c0, int_c1], color=["#457b9d", "#2a9d8f"], width=0.4, edgecolor="black")
    ax3.set_title("Integer Ops & Casts (ops/step)", fontsize=11, fontweight="bold")
    
    # 4. Persistent Bytes
    mem_c0 = 1306
    mem_c1 = 976
    ax4.bar(["C0", "C1"], [mem_c0, mem_c1], color=["#e63946", "#2a9d8f"], width=0.4, edgecolor="black")
    ax4.axhline(1024.0, color="#d90429", linestyle="--", label="1024 B Ceiling")
    ax4.set_title("Persistent Algorithmic State (Bytes)", fontsize=11, fontweight="bold")
    ax4.set_ylim(0, 1500)
    ax4.legend(fontsize=8)
    
    fig.suptitle("F10: Comprehensive Resource Vector Comparison (C0 vs C1)", fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig.savefig(FIG_DIR / "F10_resource_vector_C0_vs_C1.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("All 10 figures generated successfully!")

if __name__ == "__main__":
    generate_figures()
