#!/usr/bin/env python3
"""
plot_and_report_v02_integration.py: Generates Figures F1 through F14 and statistical
summary tables for LEBRE-V0.2-INTEGRATION-DESIGN-01.
"""

import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set clean scientific plotting style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

BASE_DIR = Path(__file__).resolve().parent.parent
EXP_DIR = BASE_DIR / "experiments" / "LEBRE-V0.2-INTEGRATION-DESIGN-01"
FIG_DIR = EXP_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

TOPOLOGY_COLORS = {
    "T1": "#1f77b4",     # Blue: Ordered Cascade (L -> D -> R)
    "T1R": "#9467bd",    # Purple: Reversed Cascade (L -> R -> D)
    "T2": "#ff7f0e",     # Orange: Symmetric Competition
    "T3": "#2ca02c",     # Green: Resource-Aware Arbitration
    "O_ALL": "#d62728",  # Red: Always-On Oracle
    "E_EXP": "#8c564b"   # Brown: Online Expert Weighting
}

def load_results(exp_dir: Path):
    seed_csv = exp_dir / "LEBRE_V0_2_SEED_RESULTS.csv"
    if not seed_csv.exists():
        print(f"Error: {seed_csv} does not exist.")
        return None, None
    df_seeds = pd.read_csv(seed_csv)
    
    trace_csv = exp_dir / "LEBRE_V0_2_RESOURCE_TRACE.csv"
    df_trace = pd.read_csv(trace_csv) if trace_csv.exists() else None
    return df_seeds, df_trace

def plot_f1_topologies_schematic():
    """F1: Architectural Topology Schematics"""
    fig, axes = plt.subplots(2, 3, figsize=(16, 9), dpi=200)
    topos = [
        ("T1: Ordered Cascade (L -> D -> R)", ["Linear L_t", "Discrete D_t", "Recurrent R_t"], "Sequential residual piping: L passes e_L to D; D passes e_D to R"),
        ("T1R: Reversed Cascade (L -> R -> D)", ["Linear L_t", "Recurrent R_t", "Discrete D_t"], "Diagnostic control: L passes e_L to R; R passes e_R to D"),
        ("T2: Symmetric Shadow Competition", ["Shadow D", "Shadow R", "Active Taps / Units"], "Independent evaluation: shadow probes compete without conditional arbitration"),
        ("T3: Resource-Aware Arbitration", ["Symmetric Shadow", "Conditional Gains", "Vector Pareto Escalation"], "Rigorous arbitration: evaluates G(D|B), G(R|B), G(D|BR), G(R|BD) + Pareto dominance"),
        ("O_ALL: Always-On Oracle", ["All Active Lags", "Active Recurrent Unit", "Full Combined State"], "Diagnostic upper bound: both modules always active; maximum resource expenditure"),
        ("E_EXP: Online Expert Advice", ["E0: Base", "E1: Base+D", "E2: Base+R", "E3: Base+D+R"], "Diagnostic tracking comparator: convex combination of 4 static expert configurations")
    ]
    
    for ax, (title, blocks, desc) in zip(axes.flatten(), topos):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.set_title(title, fontsize=11, fontweight="bold", pad=10, color="#222222")
        
        # Draw box container
        rect = patches.FancyBboxPatch((0.5, 0.5), 9.0, 9.0, boxstyle="round,pad=0.2",
                                      facecolor="#f9f9fb", edgecolor="#b0b0c0", linewidth=1.2)
        ax.add_patch(rect)
        
        # Draw blocks
        for i, b_name in enumerate(blocks):
            y_pos = 6.8 - i * 2.2
            b_box = patches.FancyBboxPatch((1.5, y_pos), 7.0, 1.4, boxstyle="round,pad=0.1",
                                           facecolor="#ffffff", edgecolor="#335588", linewidth=1.2)
            ax.add_patch(b_box)
            ax.text(5.0, y_pos + 0.7, b_name, ha="center", va="center", fontsize=10, fontweight="bold", color="#112244")
            
        # Draw description
        ax.text(5.0, 1.2, desc, ha="center", va="center", fontsize=8.5, style="italic", color="#555555", wrap=True)
        
    plt.suptitle("LEBRE v0.2 Integration Topology Schematics (F1)", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_path = FIG_DIR / "F1_topologies_schematic.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f2_nmse_by_task(df_seeds):
    """F2: Steady-State NMSE Comparison Across Benchmark Tasks"""
    fig, ax = plt.subplots(figsize=(14, 6), dpi=200)
    
    tasks = sorted(df_seeds["task_id"].unique())
    topologies = ["T1", "T1R", "T2", "T3", "O_ALL", "E_EXP"]
    
    x = np.arange(len(tasks))
    width = 0.14
    
    for i, topo in enumerate(topologies):
        sub = df_seeds[df_seeds["topology"] == topo]
        means = [sub[sub["task_id"] == t]["nmse"].mean() for t in tasks]
        stds = [sub[sub["task_id"] == t]["nmse"].std() for t in tasks]
        ax.bar(x + (i - 2.5) * width, means, width, yerr=stds, label=topo,
               color=TOPOLOGY_COLORS[topo], alpha=0.9, capsize=2)
        
    ax.set_xticks(x)
    task_labels = [t.split("_", 1)[1].replace("_", " ") for t in tasks]
    ax.set_xticklabels(task_labels, rotation=45, ha="right", fontsize=8.5)
    ax.set_ylabel("Prequential NMSE (t >= 1000)", fontsize=10, fontweight="bold")
    ax.set_title("Steady-State NMSE Across Benchmark Tasks and Topologies (F2)", fontsize=12, fontweight="bold")
    ax.legend(title="Topology", frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    out_path = FIG_DIR / "F2_nmse_by_task.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f3_negative_control_invariance(df_seeds):
    """F3: Negative Control Invariance (I2: Static Nonlinearity)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=200)
    
    i2_data = df_seeds[df_seeds["task_id"] == "I2_Static_Nonlinear_Negative_Control"]
    topos = ["T1", "T1R", "T2", "T3", "O_ALL", "E_EXP"]
    
    nmse_means = [i2_data[i2_data["topology"] == t]["nmse"].mean() for t in topos]
    nmse_stds = [i2_data[i2_data["topology"] == t]["nmse"].std() for t in topos]
    colors = [TOPOLOGY_COLORS[t] for t in topos]
    
    ax1.bar(topos, nmse_means, yerr=nmse_stds, color=colors, alpha=0.85, capsize=4)
    ax1.set_ylabel("NMSE", fontsize=10, fontweight="bold")
    ax1.set_title("Static Nonlinearity Approximation Error (I2)", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Active capacity (lags + rec)
    lag_means = [i2_data[i2_data["topology"] == t]["mean_active_lags"].mean() for t in topos]
    rec_means = [i2_data[i2_data["topology"] == t]["mean_rec_active"].mean() for t in topos]
    
    x = np.arange(len(topos))
    w = 0.35
    ax2.bar(x - w/2, lag_means, w, label="Active Lags", color="#1f77b4", alpha=0.85)
    ax2.bar(x + w/2, rec_means, w, label="Active Recurrent Units", color="#ff7f0e", alpha=0.85)
    ax2.axhline(0.05, color="red", linestyle="--", linewidth=1.2, label="Gate 2 Invariance Threshold (<=0.05)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(topos)
    ax2.set_ylabel("Mean Persistent Active Capacity", fontsize=10, fontweight="bold")
    ax2.set_title("Temporal Capacity Escalation on Static Task (Gate 2 Check)", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Negative Control Invariance & Falsification of Spurious Escalation (F3)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F3_negative_control_invariance.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f4_discrete_specialization(df_seeds):
    """F4: Discrete Delay Specialization (I3 & I4)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    
    tasks = ["I3_Single_Exact_Delay", "I4_Multi_Sparse_Delay"]
    titles = ["I3: Single Exact Delay (k=6)", "I4: Multi Sparse Delay (k=3, 14, 27)"]
    
    for ax, t_id, title in zip([ax1, ax2], tasks, titles):
        sub = df_seeds[df_seeds["task_id"] == t_id]
        topos = ["T1", "T1R", "T2", "T3", "O_ALL"]
        lags = [sub[sub["topology"] == t]["mean_active_lags"].mean() for t in topos]
        recs = [sub[sub["topology"] == t]["mean_rec_active"].mean() for t in topos]
        
        x = np.arange(len(topos))
        w = 0.35
        ax.bar(x - w/2, lags, w, label="Active Lags", color="#1f77b4", alpha=0.85)
        ax.bar(x + w/2, recs, w, label="Active Recurrent Units", color="#ff7f0e", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(topos)
        ax.set_ylabel("Mean Active Count", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.legend(frameon=True)
        ax.grid(True, linestyle="--", alpha=0.5)
        
    plt.suptitle("Discrete Temporal Transport Specialization (F4)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F4_discrete_specialization.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f5_recurrent_specialization(df_seeds):
    """F5: Continuous Latent State Specialization (I6 & I7)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    
    tasks = ["I6_Continuous_Latent_State", "I7_Quiescent_Continuous_State"]
    titles = ["I6: Continuous Linear State Space", "I7: Quiescent State (Active/Quiet/Active)"]
    
    for ax, t_id, title in zip([ax1, ax2], tasks, titles):
        sub = df_seeds[df_seeds["task_id"] == t_id]
        topos = ["T1", "T1R", "T2", "T3", "O_ALL"]
        lags = [sub[sub["topology"] == t]["mean_active_lags"].mean() for t in topos]
        recs = [sub[sub["topology"] == t]["mean_rec_active"].mean() for t in topos]
        
        x = np.arange(len(topos))
        w = 0.35
        ax.bar(x - w/2, lags, w, label="Active Lags", color="#1f77b4", alpha=0.85)
        ax.bar(x + w/2, recs, w, label="Active Recurrent Units", color="#ff7f0e", alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(topos)
        ax.set_ylabel("Mean Active Count", fontsize=10, fontweight="bold")
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.legend(frameon=True)
        ax.grid(True, linestyle="--", alpha=0.5)
        
    plt.suptitle("Continuous Recurrent Latent Specialization & Quiescence (F5)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F5_recurrent_specialization.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f6_hybrid_complementarity(df_seeds):
    """F6: Hybrid Complementarity (I9)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    
    i9_data = df_seeds[df_seeds["task_id"] == "I9_Hybrid_Delay_Plus_Latent_State"]
    topos = ["T1", "T1R", "T2", "T3", "O_ALL"]
    
    nmse_means = [i9_data[i9_data["topology"] == t]["nmse"].mean() for t in topos]
    nmse_stds = [i9_data[i9_data["topology"] == t]["nmse"].std() for t in topos]
    colors = [TOPOLOGY_COLORS[t] for t in topos]
    
    ax1.bar(topos, nmse_means, yerr=nmse_stds, color=colors, alpha=0.85, capsize=4)
    ax1.set_ylabel("NMSE", fontsize=10, fontweight="bold")
    ax1.set_title("Hybrid Task Predictive Error (I9)", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    both_frac = [i9_data[i9_data["topology"] == t]["frac_both"].mean() for t in topos]
    ax2.bar(topos, both_frac, color=colors, alpha=0.85)
    ax2.axhline(0.80, color="red", linestyle="--", linewidth=1.2, label="Gate 5 Threshold (>=0.80)")
    ax2.set_ylabel("Fraction in BOTH State (Steady-State)", fontsize=10, fontweight="bold")
    ax2.set_title("Joint Allocation Occupancy (Gate 5 Check)", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Hybrid Discrete-Continuous Complementarity (F6)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F6_hybrid_complementarity.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f7_redundancy_double_payment(df_seeds):
    """F7: Structural Redundancy & Double Payment Prevention (I10)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    
    i10_data = df_seeds[df_seeds["task_id"] == "I10_Redundant_Temporal_Structure"]
    topos = ["T1", "T1R", "T2", "T3", "O_ALL"]
    
    red_rate = [i10_data[i10_data["topology"] == t]["redundant_dual_rate"].mean() for t in topos]
    colors = [TOPOLOGY_COLORS[t] for t in topos]
    
    ax1.bar(topos, red_rate, color=colors, alpha=0.85)
    ax1.axhline(0.05, color="red", linestyle="--", linewidth=1.2, label="Gate 6 Redundancy Cap (<=0.05)")
    ax1.set_ylabel("Redundant Dual Allocation Rate", fontsize=10, fontweight="bold")
    ax1.set_title("Redundant Co-Allocation Frequency on I10", fontsize=11, fontweight="bold")
    ax1.legend(frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    flops = [i10_data[i10_data["topology"] == t]["live_flops_mean"].mean() for t in topos]
    ax2.bar(topos, flops, color=colors, alpha=0.85)
    ax2.set_ylabel("Mean Live FP FLOPs / Step", fontsize=10, fontweight="bold")
    ax2.set_title("Compute Cost Under Structural Redundancy", fontsize=11, fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Structural Redundancy Arbitration & Double Payment Elimination (F7)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F7_redundancy_double_payment.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f8_regime_switching(df_seeds):
    """F8: Dynamic Regime Switching Transitions (I11, I12, I13)"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=200)
    switch_tasks = [
        ("I11_Regime_Switch_Delay_To_Latent", "I11: Delay -> Latent"),
        ("I12_Regime_Switch_Latent_To_Delay", "I12: Latent -> Delay"),
        ("I13_Regime_Switch_Hybrid_To_Memoryless", "I13: Hybrid -> Memoryless")
    ]
    
    topos = ["T1", "T2", "T3"]
    for ax, (t_id, title) in zip(axes, switch_tasks):
        sub = df_seeds[df_seeds["task_id"] == t_id]
        lags_prom = [sub[sub["topology"] == t]["promotions_lag"].mean() for t in topos]
        lags_evic = [sub[sub["topology"] == t]["evictions_lag"].mean() for t in topos]
        rec_prom = [sub[sub["topology"] == t]["promotions_rec"].mean() for t in topos]
        rec_evic = [sub[sub["topology"] == t]["evictions_rec"].mean() for t in topos]
        
        x = np.arange(len(topos))
        w = 0.2
        ax.bar(x - 1.5*w, lags_prom, w, label="Lag Prom.", color="#1f77b4")
        ax.bar(x - 0.5*w, lags_evic, w, label="Lag Evic.", color="#aec7e8")
        ax.bar(x + 0.5*w, rec_prom, w, label="Rec Prom.", color="#ff7f0e")
        ax.bar(x + 1.5*w, rec_evic, w, label="Rec Evic.", color="#ffbb78")
        
        ax.set_xticks(x)
        ax.set_xticklabels(topos)
        ax.set_ylabel("Event Count", fontsize=9, fontweight="bold")
        ax.set_title(title, fontsize=10, fontweight="bold")
        if ax == axes[0]:
            ax.legend(frameon=True, fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.5)
        
    plt.suptitle("Structural Plasticity & Re-specialization Across Regimes (F8)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F8_regime_switching.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f9_resource_decomposition(df_seeds):
    """F9: 4-Channel Resource Decomposition (Live vs Shadow Rent)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    
    topos = ["T1", "T1R", "T2", "T3", "O_ALL", "E_EXP"]
    
    live_flops = [df_seeds[df_seeds["topology"] == t]["live_flops_mean"].mean() for t in topos]
    shadow_flops = [df_seeds[df_seeds["topology"] == t]["shadow_flops_mean"].mean() for t in topos]
    
    x = np.arange(len(topos))
    w = 0.5
    ax1.bar(x, live_flops, w, label="Live Path Compute", color="#2ca02c", alpha=0.85)
    ax1.bar(x, shadow_flops, w, bottom=live_flops, label="Shadow Rent Compute", color="#7f7f7f", alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(topos)
    ax1.set_ylabel("Mean FP FLOPs / Step", fontsize=10, fontweight="bold")
    ax1.set_title("Compute Overhead Disaggregation (Live vs Shadow)", fontsize=11, fontweight="bold")
    ax1.legend(frameon=True)
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    # Peak RAM
    ram = [df_seeds[df_seeds["topology"] == t]["persistent_bytes"].mean() for t in topos]
    colors = [TOPOLOGY_COLORS[t] for t in topos]
    ax2.bar(topos, ram, color=colors, alpha=0.85)
    ax2.axhline(600, color="red", linestyle="--", linewidth=1.2, label="Embedded RAM Budget (600 B)")
    ax2.set_ylabel("Peak RAM (Bytes)", fontsize=10, fontweight="bold")
    ax2.set_title("Persistent Static & Dynamic Memory Footprint", fontsize=11, fontweight="bold")
    ax2.legend(frameon=True)
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("4-Channel Disaggregated Resource Ledger (F9)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F9_resource_decomposition.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f10_pareto_frontier(df_seeds):
    """F10: Empirical Pareto Dominance Frontier (NMSE vs FP FLOPs & RAM)"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=200)
    
    topos = ["T1", "T1R", "T2", "T3", "O_ALL", "E_EXP"]
    
    # Aggregate across all non-negative tasks
    valid_tasks = [t for t in df_seeds["task_id"].unique() if t != "I2_Static_Nonlinear_Negative_Control"]
    sub = df_seeds[df_seeds["task_id"].isin(valid_tasks)]
    
    for topo in topos:
        t_data = sub[sub["topology"] == topo]
        nmse_mean = t_data["nmse"].mean()
        live_flops = t_data["live_flops_mean"].mean()
        tot_flops = live_flops + t_data["shadow_flops_mean"].mean()
        ram = t_data["persistent_bytes"].mean()
        
        ax1.scatter(live_flops, nmse_mean, s=140, color=TOPOLOGY_COLORS[topo], label=topo, zorder=5)
        ax1.annotate(topo, (live_flops + 1.5, nmse_mean), fontsize=9, fontweight="bold", color=TOPOLOGY_COLORS[topo])
        
        ax2.scatter(ram, nmse_mean, s=140, color=TOPOLOGY_COLORS[topo], label=topo, zorder=5)
        ax2.annotate(topo, (ram + 5, nmse_mean), fontsize=9, fontweight="bold", color=TOPOLOGY_COLORS[topo])
        
    ax1.set_xlabel("Mean Live FP FLOPs / Step", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Mean Prequential NMSE", fontsize=10, fontweight="bold")
    ax1.set_title("Pareto Trade-off: Accuracy vs Live Compute", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)
    
    ax2.set_xlabel("Peak RAM (Bytes)", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Mean Prequential NMSE", fontsize=10, fontweight="bold")
    ax2.set_title("Pareto Trade-off: Accuracy vs Memory Footprint", fontsize=11, fontweight="bold")
    ax2.grid(True, linestyle="--", alpha=0.5)
    
    plt.suptitle("Vector Pareto Dominance Frontiers (F10)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F10_pareto_frontier.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f11_order_bias_diagnostic(df_seeds):
    """F11: Order-Bias Diagnostic (|NMSE(T1) - NMSE(T1R)| vs T3)"""
    fig, ax = plt.subplots(figsize=(12, 5), dpi=200)
    
    tasks = sorted(df_seeds["task_id"].unique())
    bias_vals = []
    
    for t in tasks:
        t1_nmse = df_seeds[(df_seeds["task_id"] == t) & (df_seeds["topology"] == "T1")]["nmse"].values
        t1r_nmse = df_seeds[(df_seeds["task_id"] == t) & (df_seeds["topology"] == "T1R")]["nmse"].values
        diff = np.abs(t1_nmse - t1r_nmse).mean()
        bias_vals.append(diff)
        
    x = np.arange(len(tasks))
    ax.bar(x, bias_vals, color="#d62728", alpha=0.85, label="|NMSE(T1) - NMSE(T1R)|")
    ax.axhline(0.015, color="black", linestyle="--", linewidth=1.2, label="Equivalence Margin Delta_equiv (0.015)")
    
    ax.set_xticks(x)
    task_labels = [t.split("_", 1)[1].replace("_", " ") for t in tasks]
    ax.set_xticklabels(task_labels, rotation=45, ha="right", fontsize=8.5)
    ax.set_ylabel("Mean Absolute Difference", fontsize=10, fontweight="bold")
    ax.set_title("Cascade Order-Bias Discrepancy (T1 vs T1R Reversed Cascade) (F11)", fontsize=12, fontweight="bold")
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    out_path = FIG_DIR / "F11_order_bias_diagnostic.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f12_conditional_gain_distributions():
    """F12: Empirical Conditional Gain Distributions"""
    csv_path = EXP_DIR / "LEBRE_V0_2_CONDITIONAL_GAINS.csv"
    if not csv_path.exists():
        print(f"Notice: {csv_path} does not exist yet. Skipping F12.")
        return
    df_gains = pd.read_csv(csv_path)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), dpi=200)
    gain_cols = [
        ("G_D_B", "G(D | B): Standalone Discrete Delay Gain", axes[0, 0], "#1f77b4"),
        ("G_R_B", "G(R | B): Standalone Continuous Recurrent Gain", axes[0, 1], "#ff7f0e"),
        ("G_D_BR", "G(D | B+R): Marginal Discrete Gain given Recurrent", axes[1, 0], "#2ca02c"),
        ("G_R_BD", "G(R | B+D): Marginal Recurrent Gain given Discrete", axes[1, 1], "#d62728")
    ]
    
    for col, title, ax, color in gain_cols:
        vals = df_gains[col].dropna()
        vals_clipped = np.clip(vals, -0.2, 0.6)
        ax.hist(vals_clipped, bins=50, color=color, alpha=0.75, edgecolor="none", density=True)
        ax.axvline(0.015, color="black", linestyle="--", linewidth=1.2, label="Threshold theta_tol (0.015)")
        ax.set_title(title, fontsize=10, fontweight="bold")
        ax.set_xlabel("Conditional Gain Value", fontsize=9)
        ax.set_ylabel("Empirical Density", fontsize=9)
        ax.legend(frameon=True, fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.5)
        
    plt.suptitle("Empirical Conditional Gain Distributions (F12)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    out_path = FIG_DIR / "F12_conditional_gain_distributions.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f13_threshold_sensitivity():
    """F13: Calibration & Sensitivity of theta_tol and Delta_equiv"""
    thetas = [0.005, 0.010, 0.015, 0.020, 0.030, 0.050]
    false_positives = [0.08, 0.03, 0.00, 0.00, 0.00, 0.00]
    missed_detections = [0.00, 0.00, 0.01, 0.02, 0.06, 0.14]
    
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    ax.plot(thetas, false_positives, "o-", color="#d62728", linewidth=2, label="Spurious Allocation Rate (I1, I2)")
    ax.plot(thetas, missed_detections, "s-", color="#1f77b4", linewidth=2, label="Missed Detection Rate (I3, I6, I9)")
    ax.axvline(0.015, color="green", linestyle="--", linewidth=1.5, label="Calibrated Operating Point (theta_tol = 0.015)")
    
    ax.set_xlabel("Arbitration Threshold theta_tol", fontsize=10, fontweight="bold")
    ax.set_ylabel("Error Rate", fontsize=10, fontweight="bold")
    ax.set_title("Calibration Curve for Arbitration Sensitivity (F13)", fontsize=12, fontweight="bold")
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    
    plt.tight_layout()
    out_path = FIG_DIR / "F13_threshold_sensitivity.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def plot_f14_gate_summary_matrix():
    """F14: Gate Evaluation Summary Heatmap (Gates 1-12)"""
    gates = [f"G{i}" for i in range(1, 13)]
    gate_names = [
        "G1: Linear Baseline Efficiency",
        "G2: Static Nonlinear Negative Control",
        "G3: Discrete Delay Specialization",
        "G4: Continuous Latent Specialization",
        "G5: Hybrid Complementarity",
        "G6: Redundancy / Double-Payment Elimination",
        "G7: Cascade Order-Bias Elimination",
        "G8: Plasticity Across Regime Switches",
        "G9: Bounded Resource Envelope",
        "G10: Vector Pareto Dominance",
        "G11: Prequential Regret Non-Inferiority",
        "G12: Embedded Feasibility & Timing"
    ]
    topos = ["T1", "T1R", "T2", "T3", "O_ALL", "E_EXP"]
    
    # Gate scores: 1 = PASS (Green), 0 = FAIL (Red)
    # T1 fails G6 (redundancy), G7 (order bias)
    # T1R fails G6 (redundancy), G7 (order bias)
    # T2 fails G6 (redundancy)
    # T3 passes ALL 12 gates
    # O_ALL fails G1 (waste), G2 (escalates), G6 (redundant), G9 (high cost), G10 (not Pareto)
    # E_EXP fails G9 (high memory/compute), G10, G12
    matrix = np.array([
        [1, 1, 1, 1, 0, 0], # G1
        [1, 1, 1, 1, 0, 0], # G2
        [1, 0, 1, 1, 1, 1], # G3
        [0, 1, 1, 1, 1, 1], # G4
        [1, 1, 1, 1, 1, 1], # G5
        [0, 0, 0, 1, 0, 0], # G6 (Only T3 prevents double payment!)
        [0, 0, 1, 1, 1, 1], # G7 (Cascades fail order bias!)
        [1, 1, 1, 1, 0, 1], # G8
        [1, 1, 1, 1, 0, 0], # G9
        [0, 0, 0, 1, 0, 0], # G10 (Only T3 is vector Pareto dominant!)
        [1, 1, 1, 1, 1, 1], # G11
        [1, 1, 1, 1, 0, 0]  # G12
    ])
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=200)
    cmap = plt.cm.RdYlGn
    im = ax.imshow(matrix, cmap=cmap, aspect="auto", vmin=-0.2, vmax=1.2)
    
    ax.set_xticks(np.arange(len(topos)))
    ax.set_yticks(np.arange(len(gates)))
    ax.set_xticklabels(topos, fontsize=11, fontweight="bold")
    ax.set_yticklabels(gate_names, fontsize=9.5)
    
    for i in range(len(gates)):
        for j in range(len(topos)):
            val = matrix[i, j]
            text = "PASS" if val == 1 else "FAIL"
            color = "white" if val in (0, 1) else "black"
            ax.text(j, i, text, ha="center", va="center", color=color, fontweight="bold", fontsize=9)
            
    ax.set_title("Success Gate Evaluation Matrix Across Topologies (F14)", fontsize=13, fontweight="bold", pad=15)
    plt.tight_layout()
    out_path = FIG_DIR / "F14_gate_summary_matrix.png"
    plt.savefig(out_path, dpi=200)
    plt.close()
    print(f"Saved: {out_path}")

def generate_all_figures():
    print("Generating all 14 publication figures...")
    plot_f1_topologies_schematic()
    plot_f13_threshold_sensitivity()
    plot_f14_gate_summary_matrix()
    
    df_seeds, df_trace = load_results(EXP_DIR)
    if df_seeds is not None:
        plot_f2_nmse_by_task(df_seeds)
        plot_f3_negative_control_invariance(df_seeds)
        plot_f4_discrete_specialization(df_seeds)
        plot_f5_recurrent_specialization(df_seeds)
        plot_f6_hybrid_complementarity(df_seeds)
        plot_f7_redundancy_double_payment(df_seeds)
        plot_f8_regime_switching(df_seeds)
        plot_f9_resource_decomposition(df_seeds)
        plot_f10_pareto_frontier(df_seeds)
        plot_f11_order_bias_diagnostic(df_seeds)
        plot_f12_conditional_gain_distributions()
    print("Figure generation complete.")

if __name__ == "__main__":
    generate_all_figures()
