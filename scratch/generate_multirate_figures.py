#!/usr/bin/env python3
"""
generate_multirate_figures.py

Generates all 12 publication-quality figures for LEBRE v0.2 Multirate Shadow Decomposition:
- F1_atomic_shadow_cost_breakdown
- F2_component_sensitivity_K5
- F3_component_rate_vs_behavior
- F4_component_rate_vs_compute
- F5_multirate_compute_breakdown
- F6_seed_level_nmse_delta
- F7_switch_latency_by_task
- F8_recurrent_forward_vs_learning_decimation
- F9_I2_false_wake_vs_temporal_tasks
- F10_quiescence_component_duty
- F11_clock_utilization
- F12_compute_behavior_pareto

Outputs to experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/figures/
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"
FIG_DIR = os.path.join(EXP_DIR, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 13,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 14,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'lines.linewidth': 1.8,
    'grid.alpha': 0.4
})

def plot_f1():
    csv_path = os.path.join(EXP_DIR, "ATOMIC_SHADOW_OPERATION_LEDGER.csv")
    df = pd.read_csv(csv_path)
    
    fig, ax = plt.subplots(figsize=(10, 5.5))
    roles = df['role'].unique()
    colors = {
        'SENSOR': '#1f77b4',
        'EVIDENCE_ACCUMULATION': '#2ca02c',
        'PARAMETER_LEARNING': '#d62728',
        'STATE_PROPAGATION': '#9467bd',
        'DECISION': '#ff7f0e',
        'HOUSEKEEPING': '#7f7f7f'
    }
    
    bar_colors = [colors.get(r, '#333333') for r in df['role']]
    bars = ax.bar(df['operation'], df['FP_cost'], color=bar_colors, edgecolor='black', linewidth=0.8)
    
    ax.set_ylabel("FP FLOPs / Execution")
    ax.set_title("F1: Atomic Shadow Operation Cost Breakdown by Functional Role")
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['operation'], rotation=45, ha='right')
    ax.grid(True, axis='y', linestyle='--')
    
    # Legend
    legend_handles = [plt.Rectangle((0,0),1,1, color=colors[r], label=r) for r in colors if r in roles]
    ax.legend(handles=legend_handles, title="Functional Role", loc="upper left")
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F1_atomic_shadow_cost_breakdown.png"))
    plt.close()
    print("Generated F1")

def plot_f2():
    csv_path = os.path.join(EXP_DIR, "COMPONENT_SENSITIVITY_DEV_RESULTS.csv")
    df = pd.read_csv(csv_path)
    d0_nmse = df[df['model_id'] == 'D0']['nmse'].mean()
    d0_shadow = df[df['model_id'] == 'D0']['shadow_fp_mean'].mean()
    
    models = ['D7', 'D8', 'D9F', 'D9L', 'D10']
    labels = ['D7 (Probe K=5)', 'D8 (Cand K=5)', 'D9F (RecFwd K=5)', 'D9L (RecLrn K=5)', 'D10 (Arb K=5)']
    
    deltas = []
    savings = []
    for m in models:
        sub = df[df['model_id'] == m]
        deltas.append(sub['nmse'].mean() - d0_nmse)
        savings.append(d0_shadow - sub['shadow_fp_mean'].mean())
        
    fig, ax1 = plt.subplots(figsize=(9, 5))
    x = np.arange(len(models))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, deltas, width, label='Delta NMSE vs D0', color='#d62728', edgecolor='black')
    ax1.axhline(0.0100, color='darkred', linestyle='--', label='Non-Inferiority Ceiling (+0.0100)')
    ax1.axhline(0.0, color='gray', linestyle='-', linewidth=0.8)
    ax1.set_ylabel("Delta NMSE (Lower is Better)", color='#d62728')
    ax1.tick_params(axis='y', labelcolor='#d62728')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=15)
    
    ax2 = ax1.twinx()
    bars2 = ax2.bar(x + width/2, savings, width, label='Shadow Compute Saved (FP/step)', color='#1f77b4', edgecolor='black')
    ax2.set_ylabel("Shadow Compute Saved (FP/step, Higher is Better)", color='#1f77b4')
    ax2.tick_params(axis='y', labelcolor='#1f77b4')
    
    plt.title("F2: Component Sensitivity Under Isolated K=5 Decimation")
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F2_component_sensitivity_K5.png"))
    plt.close()
    print("Generated F2")

def plot_f3_f4():
    csv_path = os.path.join(EXP_DIR, "COMPONENT_RATE_BOUNDARIES.csv")
    df = pd.read_csv(csv_path)
    ref_nmse = df[df['model_id'] == 'PROBE_K1']['nmse'].mean()
    
    components = {
        'Probe (Stage 7)': ['PROBE_K1', 'PROBE_K2', 'PROBE_K5', 'PROBE_K10'],
        'Candidate (Stage 8)': ['CAND_K1', 'CAND_K2', 'CAND_K5', 'CAND_K10'],
        'Recurrent Fwd (Stage 9A)': ['REC_FWD_K1', 'REC_FWD_K2', 'REC_FWD_K5', 'REC_FWD_K10'],
        'Recurrent Learn (Stage 9C-D)': ['REC_LRN_K1', 'REC_LRN_K2', 'REC_LRN_K5', 'REC_LRN_K10'],
        'Arbitration (Stage 10)': ['ARB_K1', 'ARB_K2', 'ARB_K5', 'ARB_K10']
    }
    ks = [1, 2, 5, 10]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    markers = ['o', 's', '^', 'v', 'D']
    
    # F3: Rate vs Behavior
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for (name, model_list), c, m in zip(components.items(), colors, markers):
        d_nmses = [df[df['model_id'] == mid]['nmse'].mean() - ref_nmse for mid in model_list]
        ax.plot(ks, d_nmses, marker=m, color=c, label=name)
        
    ax.axhline(0.0100, color='darkred', linestyle='--', label='Non-Inferiority Ceiling (+0.0100)')
    ax.axhline(0.0, color='gray', linestyle='-', linewidth=0.8)
    ax.set_xlabel("Component Cadence Period K (Steps between executions)")
    ax.set_ylabel("Delta NMSE vs Continuous Baseline")
    ax.set_title("F3: Component Rate Ladder vs. Predictive Performance")
    ax.set_xticks(ks)
    ax.grid(True, linestyle='--')
    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F3_component_rate_vs_behavior.png"))
    plt.close()
    print("Generated F3")
    
    # F4: Rate vs Compute
    fig, ax = plt.subplots(figsize=(8.5, 5))
    for (name, model_list), c, m in zip(components.items(), colors, markers):
        fps = [df[df['model_id'] == mid]['total_fp_mean'].mean() for mid in model_list]
        ax.plot(ks, fps, marker=m, color=c, label=name)
        
    ax.axhline(100.0, color='darkgreen', linestyle='--', label='Feasibility Ceiling (<= 100 FP)')
    ax.set_xlabel("Component Cadence Period K (Steps between executions)")
    ax.set_ylabel("Mean Total Online Compute (FP FLOPs/step)")
    ax.set_title("F4: Component Rate Ladder vs. Total Online Compute")
    ax.set_xticks(ks)
    ax.grid(True, linestyle='--')
    ax.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F4_component_rate_vs_compute.png"))
    plt.close()
    print("Generated F4")

def plot_f5():
    res_path = os.path.join(EXP_DIR, "COMPONENT_RESOURCE_BY_SEED.csv")
    df = pd.read_csv(res_path)
    
    m0 = df[df['model_id'] == 'M0'].mean(numeric_only=True)
    m1 = df[df['model_id'] == 'M1'].mean(numeric_only=True)
    s2 = df[df['model_id'] == 'S2_K5'].mean(numeric_only=True)
    
    models = ['M0 (Continuous)', 'M1 (Frozen Multirate)', 'S2_K5 (Periodic K=5)']
    live_fp = [m0['live_fp_mean'], m1['live_fp_mean'], s2['live_fp_mean']]
    shadow_fp = [m0['shadow_fp_mean'], m1['shadow_fp_mean'], s2['shadow_fp_mean']]
    router_fp = [m0['router_fp_mean'], m1['router_fp_mean'], s2['router_fp_mean']]
    
    fig, ax = plt.subplots(figsize=(8, 5.5))
    x = np.arange(len(models))
    width = 0.45
    
    b1 = ax.bar(x, live_fp, width, label='Live Pipeline (Normalized)', color='#1f77b4', edgecolor='black')
    b2 = ax.bar(x, shadow_fp, width, bottom=live_fp, label='Shadow Operations', color='#ff7f0e', edgecolor='black')
    b3 = ax.bar(x, router_fp, width, bottom=np.array(live_fp)+np.array(shadow_fp), label='Router Overhead', color='#2ca02c', edgecolor='black')
    
    ax.axhline(100.0, color='red', linestyle='--', linewidth=1.5, label='Budget Ceiling (100 FP)')
    
    for i in range(len(models)):
        tot = live_fp[i] + shadow_fp[i] + router_fp[i]
        ax.text(x[i], tot + 2.5, f"{tot:.1f} FP", ha='center', fontweight='bold')
        
    ax.set_ylabel("Mean Online Compute (FP FLOPs/step)")
    ax.set_title("F5: Confirmatory Total Online Compute Breakdown")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 200)
    ax.grid(True, axis='y', linestyle='--')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F5_multirate_compute_breakdown.png"))
    plt.close()
    print("Generated F5")

def plot_f6():
    pni_path = os.path.join(EXP_DIR, "PREDICTIVE_NONINFERIORITY.csv")
    df = pd.read_csv(pni_path)
    seed_rows = df[df['seed'] != 'AGGREGATE_STATISTICS'].copy()
    seed_rows['delta_nmse_m1'] = seed_rows['delta_nmse_m1'].astype(float)
    
    deltas = seed_rows['delta_nmse_m1'].values
    mean_d = deltas.mean()
    std_d = deltas.std(ddof=1)
    ci95_u = mean_d + 1.699 * (std_d / np.sqrt(len(deltas)))
    
    fig, ax = plt.subplots(figsize=(8.5, 5))
    y_pos = np.arange(len(deltas))
    ax.scatter(deltas, y_pos, color='#1f77b4', alpha=0.7, edgecolors='none', s=40, label='Independent Seeds (N=30)')
    
    ax.axvline(mean_d, color='blue', linestyle='-', linewidth=2, label=f'Mean Delta ({mean_d:+.4f})')
    ax.axvline(ci95_u, color='purple', linestyle='--', linewidth=2, label=f'95% One-Sided CI Upper ({ci95_u:+.4f})')
    ax.axvline(0.0100, color='darkred', linestyle='-', linewidth=2, label='Non-Inferiority Ceiling (+0.0100)')
    ax.axvline(0.0, color='gray', linestyle=':', linewidth=1)
    
    ax.set_xlabel("Delta NMSE (M1 - M0, Seed Aggregate across 14 tasks)")
    ax.set_ylabel("Seed Index")
    ax.set_title("F6: Seed-Level Predictive Non-Inferiority Distribution (N=30)")
    ax.grid(True, linestyle='--')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F6_seed_level_nmse_delta.png"))
    plt.close()
    print("Generated F6")

def plot_f7():
    sw_path = os.path.join(EXP_DIR, "SWITCHING_PRESERVATION.csv")
    df = pd.read_csv(sw_path)
    
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(df))
    width = 0.25
    
    ax.bar(x - width, df['m0_switch_latency_steps'], width, label='M0 (Continuous)', color='#1f77b4', edgecolor='black')
    ax.bar(x, df['m1_switch_latency_steps'], width, label='M1 (Multirate)', color='#2ca02c', edgecolor='black')
    ax.bar(x + width, df['s2_switch_latency_steps'], width, label='S2_K5 (Periodic)', color='#d62728', edgecolor='black')
    
    short_labels = [t.split('_')[0] + ' ' + t.split('_')[2] for t in df['task_id']]
    ax.set_xticks(x)
    ax.set_xticklabels(short_labels)
    ax.set_ylabel("Recovery Latency (Stream Steps)")
    ax.set_title("F7: Directional Regime Switching Recovery Latency")
    ax.grid(True, axis='y', linestyle='--')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F7_switch_latency_by_task.png"))
    plt.close()
    print("Generated F7")

def plot_f8():
    csv_path = os.path.join(EXP_DIR, "COMPONENT_RATE_BOUNDARIES.csv")
    df = pd.read_csv(csv_path)
    ref_nmse = df[df['model_id'] == 'REC_FWD_K1']['nmse'].mean()
    
    fwd_models = ['REC_FWD_K1', 'REC_FWD_K2', 'REC_FWD_K5', 'REC_FWD_K10']
    lrn_models = ['REC_LRN_K1', 'REC_LRN_K2', 'REC_LRN_K5', 'REC_LRN_K10']
    ks = [1, 2, 5, 10]
    
    fwd_deltas = [df[df['model_id'] == mid]['nmse'].mean() - ref_nmse for mid in fwd_models]
    lrn_deltas = [df[df['model_id'] == mid]['nmse'].mean() - ref_nmse for mid in lrn_models]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(ks, fwd_deltas, marker='o', color='#d62728', label='Recurrent State Forward Decimation (Path-dependent)')
    ax.plot(ks, lrn_deltas, marker='s', color='#1f77b4', label='Recurrent Parameter Learning Decimation (Forward K=1)')
    
    ax.axhline(0.0, color='gray', linestyle='-', linewidth=0.8)
    ax.set_xlabel("Decimation Period K (Steps between executions)")
    ax.set_ylabel("Delta NMSE vs Continuous Recurrence")
    ax.set_title("F8: Recurrent State Continuity vs. Parameter Learning Decimation")
    ax.set_xticks(ks)
    ax.grid(True, linestyle='--')
    ax.legend(loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F8_recurrent_forward_vs_learning_decimation.png"))
    plt.close()
    print("Generated F8")

def plot_f9():
    router_path = os.path.join(EXP_DIR, "TEMPORAL_ROUTER_ANALYSIS.csv")
    df = pd.read_csv(router_path)
    
    fig, ax1 = plt.subplots(figsize=(8, 5))
    x = np.arange(len(df))
    width = 0.35
    
    ax1.bar(x - width/2, df['i2_awake_fraction'], width, label='I2 Awake Fraction (Lower is better)', color='#ff7f0e', edgecolor='black')
    ax1.set_ylabel("I2 Awake Fraction", color='#ff7f0e')
    ax1.tick_params(axis='y', labelcolor='#ff7f0e')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['model_id'])
    
    ax2 = ax1.twinx()
    ax2.plot(x + width/2, df['temporal_task_nmse'], marker='D', color='#1f77b4', linewidth=2, label='Temporal Tasks NMSE')
    ax2.set_ylabel("Temporal Tasks NMSE (Lower is better)", color='#1f77b4')
    ax2.tick_params(axis='y', labelcolor='#1f77b4')
    
    plt.title("F9: Temporal Router False Sleep vs. Temporal Task Performance")
    ax1.grid(True, linestyle='--', alpha=0.5)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F9_I2_false_wake_vs_temporal_tasks.png"))
    plt.close()
    print("Generated F9")

def plot_f10():
    q_path = os.path.join(EXP_DIR, "QUIESCENCE_REACTIVATION.csv")
    df = pd.read_csv(q_path)
    
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    x = np.arange(len(df))
    width = 0.35
    
    ax.bar(x - width/2, df['m0_quiescent_shadow_fp'], width, label='M0 Shadow FP during Quiescence', color='#1f77b4', edgecolor='black')
    ax.bar(x + width/2, df['m1_quiescent_shadow_fp'], width, label='M1 Shadow FP during Quiescence', color='#2ca02c', edgecolor='black')
    
    labels = ['I7 (Quiescent Recurrent)', 'I8 (Quiescent Discrete Lag)']
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Quiescent Shadow Compute (FP FLOPs/step)")
    ax.set_title("F10: Shadow Resource Consumption During Signal Quiescence")
    ax.grid(True, axis='y', linestyle='--')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F10_quiescence_component_duty.png"))
    plt.close()
    print("Generated F10")

def plot_f11():
    clk_path = os.path.join(EXP_DIR, "CLOCK_UTILIZATION_BY_SEED.csv")
    df = pd.read_csv(clk_path)
    
    m0_mean = df[df['model_id'] == 'M0'].mean(numeric_only=True)
    m1_mean = df[df['model_id'] == 'M1'].mean(numeric_only=True)
    
    clock_names = [
        'probe_executions', 'candidate_observations', 'candidate_parameter_updates',
        'recurrent_forward_executions', 'recurrent_parameter_updates', 'arbitration_updates'
    ]
    labels = ['Probe (7)', 'Cand Obs (8A-C)', 'Cand Lrn (8D)', 'Rec Fwd (9A)', 'Rec Lrn (9C-D)', 'Arb (10)']
    
    m0_vals = [m0_mean[f"{c}_per_1k"] for c in clock_names]
    m1_vals = [m1_mean[f"{c}_per_1k"] for c in clock_names]
    
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(clock_names))
    width = 0.35
    
    ax.bar(x - width/2, m0_vals, width, label='M0 (Continuous)', color='#1f77b4', edgecolor='black')
    ax.bar(x + width/2, m1_vals, width, label='M1 (Frozen Multirate)', color='#2ca02c', edgecolor='black')
    
    ax.set_ylabel("Executions per 1,000 Stream Steps")
    ax.set_title("F11: Disaggregated Shadow Clock Utilization")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.grid(True, axis='y', linestyle='--')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F11_clock_utilization.png"))
    plt.close()
    print("Generated F11")

def plot_f12():
    dev_path = os.path.join(EXP_DIR, "MULTIRATE_DEV_RESULTS.csv")
    dev_df = pd.read_csv(dev_path)
    
    final_res = os.path.join(EXP_DIR, "MULTIRATE_FINAL_RESULTS.csv")
    fin_df = pd.read_csv(final_res)
    
    models = {
        'M0 (Continuous Confirmatory)': (fin_df[fin_df['model_id']=='M0']['total_fp_mean'].mean(), fin_df[fin_df['model_id']=='M0']['nmse'].mean(), 'blue', 'o', 100),
        'M1 (Frozen Multirate)': (fin_df[fin_df['model_id']=='M1']['total_fp_mean'].mean(), fin_df[fin_df['model_id']=='M1']['nmse'].mean(), 'green', '*', 180),
        'S2_K5 (Periodic Whole-Shadow)': (fin_df[fin_df['model_id']=='S2_K5']['total_fp_mean'].mean(), fin_df[fin_df['model_id']=='S2_K5']['nmse'].mean(), 'red', 's', 90),
        'MR1_A (DEV)': (dev_df[dev_df['model_id']=='MR1_A']['total_fp_mean'].mean(), dev_df[dev_df['model_id']=='MR1_A']['nmse'].mean(), 'orange', '^', 70),
        'MR1_B (DEV)': (dev_df[dev_df['model_id']=='MR1_B']['total_fp_mean'].mean(), dev_df[dev_df['model_id']=='MR1_B']['nmse'].mean(), 'purple', 'v', 70),
        'MR2 (DEV Data-Selective)': (dev_df[dev_df['model_id']=='MR2']['total_fp_mean'].mean(), dev_df[dev_df['model_id']=='MR2']['nmse'].mean(), 'brown', 'D', 70),
        'MR3 (DEV Temporal Router)': (dev_df[dev_df['model_id']=='MR3']['total_fp_mean'].mean(), dev_df[dev_df['model_id']=='MR3']['nmse'].mean(), 'black', 'X', 80),
    }
    
    fig, ax = plt.subplots(figsize=(9.5, 6))
    for name, (fp, nmse, c, m, sz) in models.items():
        ax.scatter(fp, nmse, color=c, marker=m, s=sz, label=name, edgecolors='black', linewidth=0.8, zorder=4)
        
    ax.axvline(100.0, color='darkgreen', linestyle='--', linewidth=1.5, label='Budget Ceiling (<= 100 FP)')
    m0_nmse = fin_df[fin_df['model_id']=='M0']['nmse'].mean()
    ax.axhline(m0_nmse + 0.0100, color='darkred', linestyle='--', linewidth=1.5, label='Non-Inferiority Ceiling (+0.0100)')
    
    # Shade acceptable region
    ax.axvspan(0, 100, ymin=0, ymax=(m0_nmse + 0.0100 - 0.25)/(0.45 - 0.25), color='green', alpha=0.08, label='Preregistered Target Region')
    
    ax.set_xlabel("Mean Total Online Compute (FP FLOPs/step)")
    ax.set_ylabel("Mean Aggregate NMSE (Lower is Better)")
    ax.set_title("F12: Compute-Behavior Pareto Frontier Across All Architectures")
    ax.set_xlim(80, 190)
    ax.set_ylim(0.28, 0.40)
    ax.grid(True, linestyle='--')
    ax.legend(loc='upper right', framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(os.path.join(FIG_DIR, "F12_compute_behavior_pareto.png"))
    plt.close()
    print("Generated F12")

def main():
    print("Generating all 12 figures...")
    plot_f1()
    plot_f2()
    plot_f3_f4()
    plot_f5()
    plot_f6()
    plot_f7()
    plot_f8()
    plot_f9()
    plot_f10()
    plot_f11()
    plot_f12()
    print("All 12 figures successfully generated.")

if __name__ == "__main__":
    main()
