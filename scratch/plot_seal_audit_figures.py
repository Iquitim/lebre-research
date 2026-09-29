#!/usr/bin/env python3
"""
plot_seal_audit_figures.py:
Generates all 12 mandatory forensic audit figures (F1 to F12) for
experiments/LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01/figures/
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Setup style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['figure.dpi'] = 300

AUDIT_DIR = Path("experiments/LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01")
FIG_DIR = AUDIT_DIR / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)
PARENT_DIR = Path("experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01")

df_seeds = pd.read_csv(PARENT_DIR / "LEBRE_V0_2_SEED_RESULTS.csv")
df_gains = pd.read_csv(PARENT_DIR / "LEBRE_V0_2_CONDITIONAL_GAINS.csv")
df_cell = pd.read_csv(AUDIT_DIR / "REPORT_CELL_TRACEABILITY.csv")
df_res = pd.read_csv(AUDIT_DIR / "RESOURCE_COMPLIANCE_MATRIX.csv")
df_supp = pd.read_csv(AUDIT_DIR / "SUPPORT_RECOVERY_AUDIT.csv")
df_reg = pd.read_csv(AUDIT_DIR / "REGIME_TRACKING_AUDIT.csv")
df_trans = pd.read_csv(AUDIT_DIR / "TRANSITION_CLASSIFICATION.csv")
df_pareto = pd.read_csv(AUDIT_DIR / "PARETO_RECOMPUTATION.csv")
df_claims = pd.read_csv(AUDIT_DIR / "CLAIM_TRACEABILITY.csv")
df_stats = pd.read_csv(AUDIT_DIR / "STATISTICAL_CLAIM_TRACEABILITY.csv")

# -------------------------------------------------------------
# F1: Reported vs Recomputed NMSE (Seed 1301 Dev paste vs 30-Seed Mean)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
nmse_cells = df_cell[(df_cell["TABLE"].str.contains("Task-Level")) & (df_cell["COLUMN"] == "NMSE_T3")]
tasks = [r.replace("_", " ") for r in nmse_cells["ROW"]]
x = np.arange(len(tasks))
width = 0.35

reported_vals = nmse_cells["REPORTED_VALUE"].astype(float).values
recomputed_vals = nmse_cells["RECOMPUTED_VALUE"].astype(float).values

rects1 = ax.bar(x - width/2, reported_vals, width, label='Reported NMSE (Pasted Dev Seed 1301)', color='#e74c3c', alpha=0.85)
rects2 = ax.bar(x + width/2, recomputed_vals, width, label='Recomputed NMSE (30-Seed Confirmatory Mean)', color='#2ecc71', alpha=0.85)

ax.set_ylabel('Prequential NMSE (t >= 1000)')
ax.set_title('F1: Reported vs. Recomputed NMSE for Topology T3 (Traceability Audit)')
ax.set_xticks(x)
ax.set_xticklabels(tasks, rotation=45, ha='right', fontsize=8)
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(FIG_DIR / "F1_reported_vs_recomputed_values.png")
plt.close(fig)
print("Saved F1")

# -------------------------------------------------------------
# F2: Resource Gate Provenance Timeline
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.5))
events = [
    ("LEBRE v0.1 Canonical Spec\n(Historical Baseline)", "1024 B persistent RAM\n100 FP FLOPs", 1.0, "#34495e"),
    ("LEBRE v0.2 Resource Model\n(Line 84 Preregistered)", "RAM <= 1024 Bytes\nExplicit Limit", 2.5, "#2980b9"),
    ("LEBRE v0.2 Protocol\n(Line 71 Preregistered)", "Gate 11: RAM <= 1024 B\nPre-Confirmatory Freeze", 4.0, "#2980b9"),
    ("Confirmatory Simulation Runs\n(scratch/run_v02_integration)", "Measured RAM = 1306 B\nExceeds 1024 B Ceiling!", 5.5, "#e67e22"),
    ("Post-Result Reports\n(DECISION.md & FINAL_REPORT.md)", "Gate 11 silently changed to:\nRAM <= 2048 B (POST-HOC)", 7.0, "#c0392b")
]

ax.axhline(0, color='gray', linestyle='--', linewidth=1.5, zorder=1)
for name, desc, xpos, col in events:
    ax.scatter([xpos], [0], color=col, s=180, zorder=3)
    ax.text(xpos, 0.15 if xpos % 2 == 1 else -0.45, f"{name}\n[{desc}]", 
            ha='center', va='center', fontsize=8, weight='bold',
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec=col, lw=1.5))
    ax.vlines(xpos, 0, 0.12 if xpos % 2 == 1 else -0.22, color=col, lw=1.5, linestyle=':')

ax.set_xlim(0.2, 7.8)
ax.set_ylim(-0.7, 0.5)
ax.axis('off')
ax.set_title("F2: Provenance Timeline of Gate 11 Memory Ceiling (1024 B -> 2048 B Relaxation)", fontsize=11, weight='bold')
plt.tight_layout()
fig.savefig(FIG_DIR / "F2_resource_gate_provenance_timeline.png")
plt.close(fig)
print("Saved F2")

# -------------------------------------------------------------
# F3: Live, Shadow, and Total Compute by Task for T3
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5))
task_res = df_res[~df_res["REGIME_OR_TASK"].str.startswith("STATE_")]
tasks = [r.replace("_", " ") for r in task_res["REGIME_OR_TASK"]]
x = np.arange(len(tasks))
width = 0.25

live_fp = task_res["LIVE_FP_MEAN"].astype(float).values
shadow_fp = task_res["SHADOW_FP_MEAN"].astype(float).values
total_fp = task_res["TOTAL_FP_MEAN"].astype(float).values

ax.bar(x - width, live_fp, width, label='Live FP FLOPs (mean)', color='#2980b9')
ax.bar(x, shadow_fp, width, label='Shadow FP FLOPs (mean)', color='#8e44ad')
ax.bar(x + width, total_fp, width, label='Total Online FP FLOPs (Live + Shadow)', color='#d35400')

ax.axhline(100.0, color='red', linestyle='--', linewidth=1.5, label='Legacy R2 FP Ceiling (100 FLOPs)')
ax.set_ylabel('FP FLOPs per Step')
ax.set_title('F3: Disaggregated T3 Compute Expenditure Across 14 Tasks')
ax.set_xticks(x)
ax.set_xticklabels(tasks, rotation=45, ha='right', fontsize=8)
ax.legend(frameon=True, loc='upper left')
plt.tight_layout()
fig.savefig(FIG_DIR / "F3_live_shadow_total_compute_by_task.png")
plt.close(fig)
print("Saved F3")

# -------------------------------------------------------------
# F4: Persistent vs Peak Memory by Task for T3
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 4.5))
pers_ram = task_res["PERSISTENT_BYTES"].astype(float).values
peak_ram = task_res["PEAK_RAM"].astype(float).values

ax.bar(x - width/2, pers_ram, width, label='Persistent RAM (Bytes)', color='#16a085')
ax.bar(x + width/2, peak_ram, width, label='Peak RAM (Bytes)', color='#27ae60')

ax.axhline(1024.0, color='red', linestyle='--', linewidth=1.5, label='Legacy R2 Memory Ceiling (1024 Bytes) [FAIL]')
ax.axhline(2048.0, color='blue', linestyle=':', linewidth=1.5, label='Proposed v0.2 Class Ceiling (2048 Bytes) [PASS]')

ax.set_ylabel('Bytes')
ax.set_title('F4: Memory Allocation of T3 Across Tasks vs Historical and Proposed Ceilings')
ax.set_xticks(x)
ax.set_xticklabels(tasks, rotation=45, ha='right', fontsize=8)
ax.set_ylim(0, 2300)
ax.legend(frameon=True, loc='lower right')
plt.tight_layout()
fig.savefig(FIG_DIR / "F4_persistent_vs_peak_memory_by_task.png")
plt.close(fig)
print("Saved F4")

# -------------------------------------------------------------
# F5: Legacy vs Proposed Resource Compliance Heatmap
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 6))
matrix_rows = df_res["REGIME_OR_TASK"].values
categories = ["LEGACY_R2_FP_PASS_LIVE", "LEGACY_R2_FP_PASS_TOTAL", "LEGACY_R2_MEM_PASS", "PROPOSED_V0_2_MEM_PASS"]
cat_labels = ["Legacy FP (Live <= 100)", "Legacy FP (Total <= 100)", "Legacy RAM (<= 1024 B)", "Proposed RAM (<= 2048 B)"]

grid = np.zeros((len(matrix_rows), len(categories)))
for i, row in enumerate(matrix_rows):
    sub = df_res[df_res["REGIME_OR_TASK"] == row]
    for j, cat in enumerate(categories):
        val = sub[cat].values[0]
        grid[i, j] = 1 if val == "PASS" else 0

im = ax.imshow(grid, cmap='RdYlGn', vmin=0, vmax=1, aspect='auto')
ax.set_xticks(np.arange(len(cat_labels)))
ax.set_xticklabels(cat_labels, rotation=25, ha='right', fontsize=9)
ax.set_yticks(np.arange(len(matrix_rows)))
ax.set_yticklabels([r.replace("_", " ") for r in matrix_rows], fontsize=8)
ax.set_title("F5: Resource Compliance Matrix Across Regimes & Tasks", weight='bold')

for i in range(len(matrix_rows)):
    for j in range(len(categories)):
        text = "PASS" if grid[i, j] == 1 else "FAIL"
        ax.text(j, i, text, ha="center", va="center", color="black" if grid[i, j] == 1 else "white", weight="bold", fontsize=8)

plt.tight_layout()
fig.savefig(FIG_DIR / "F5_legacy_vs_proposed_resource_compliance.png")
plt.close(fig)
print("Saved F5")

# -------------------------------------------------------------
# F6: Live Vector Pareto Front
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5.5))
topos = ["T1", "T1R", "T2", "T3", "O_ALL"]
topo_colors = {"T1": "#3498db", "T1R": "#9b59b6", "T2": "#e67e22", "T3": "#2ecc71", "O_ALL": "#e74c3c"}

for topo in topos:
    sub = df_seeds[df_seeds["topology"] == topo]
    nmse_m = sub["nmse"].mean()
    live_m = sub["live_flops_mean"].mean()
    ram_m = sub["persistent_bytes"].mean()
    ax.scatter(nmse_m, live_m, s=ram_m/5, color=topo_colors[topo], edgecolors='black', linewidth=1.5, label=f"{topo} (RAM={ram_m:.0f}B)", zorder=4)
    ax.text(nmse_m + 0.005, live_m + 1.0, f"{topo}\n({nmse_m:.3f}, {live_m:.1f} FLOPs)", fontsize=8, weight='bold')

ax.set_xlabel('Aggregate Benchmark NMSE (Lower is Better)')
ax.set_ylabel('Live Path FP FLOPs (Lower is Better)')
ax.set_title('F6: Live Path Vector Trade-off (NMSE vs Live FP FLOPs, Size = RAM)')
ax.legend(frameon=True, loc='upper left')
plt.tight_layout()
fig.savefig(FIG_DIR / "F6_live_vector_pareto_front.png")
plt.close(fig)
print("Saved F6")

# -------------------------------------------------------------
# F7: Full Online Vector Pareto Front
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5.5))
for topo in topos:
    sub = df_seeds[df_seeds["topology"] == topo]
    nmse_m = sub["nmse"].mean()
    tot_m = sub["live_flops_mean"].mean() + sub["shadow_flops_mean"].mean()
    ram_m = sub["persistent_bytes"].mean()
    ax.scatter(nmse_m, tot_m, s=ram_m/5, color=topo_colors[topo], edgecolors='black', linewidth=1.5, label=f"{topo} (RAM={ram_m:.0f}B)", zorder=4)
    ax.text(nmse_m + 0.005, tot_m + 1.0, f"{topo}\n({nmse_m:.3f}, {tot_m:.1f} FLOPs)", fontsize=8, weight='bold')

ax.set_xlabel('Aggregate Benchmark NMSE (Lower is Better)')
ax.set_ylabel('Total Online FP FLOPs [Live + Shadow] (Lower is Better)')
ax.set_title('F7: Full Online Vector Trade-off (NMSE vs Total FP FLOPs, Size = RAM)')
ax.legend(frameon=True, loc='upper left')
plt.tight_layout()
fig.savefig(FIG_DIR / "F7_full_online_vector_pareto_front.png")
plt.close(fig)
print("Saved F7")

# -------------------------------------------------------------
# F8: I3 and I4 Support Precision and Recall
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
x = np.arange(2)
width = 0.25

tasks = ["I3 (Single Delay, k=6)", "I4 (Multi-Sparse, k=3,14,27)"]
rec = df_supp["SUPPORT_RECALL"].astype(float).values
prec = df_supp["SUPPORT_PRECISION"].astype(float).values
k_act = df_supp["MEAN_ACTIVE_K"].astype(float).values
k_true = df_supp["TRUE_COUNT"].astype(float).values

ax.bar(x - width, rec * 100, width, label='Support Recall (%)', color='#2ecc71')
ax.bar(x, prec * 100, width, label='Support Precision (%)', color='#e74c3c')

# Annotations
for i in range(2):
    ax.text(x[i] - width, rec[i]*100 + 2, f"{rec[i]*100:.1f}%", ha='center', fontsize=8, weight='bold')
    ax.text(x[i], prec[i]*100 + 2, f"{prec[i]*100:.1f}%", ha='center', fontsize=8, weight='bold')
    ax.text(x[i] + width, 50, f"True K = {k_true[i]:.0f}\nActive K = {k_act[i]:.2f}", ha='center', fontsize=8,
            bbox=dict(boxstyle="round,pad=0.3", fc="#ecf0f1", ec="gray"))

ax.set_ylabel('Percentage (%)')
ax.set_title('F8: Structural Specificity Audit: I3 and I4 Support Precision & Recall')
ax.set_xticks(x)
ax.set_xticklabels(tasks, fontsize=9)
ax.set_ylim(0, 115)
ax.legend(frameon=True, loc='upper right')
plt.tight_layout()
fig.savefig(FIG_DIR / "F8_I3_I4_support_precision_recall.png")
plt.close(fig)
print("Saved F8")

# -------------------------------------------------------------
# F9: Regime Switch Correct State Tracking Timeline
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 4.5))
reg_tasks = df_reg["TASK_ID"].values
disc_lat = [int(v.replace(" steps", "")) for v in df_reg["MEDIAN_DISCOVERY_LATENCY"]]
ret_lat = [int(v.replace(" steps", "")) for v in df_reg["MEDIAN_RETIREMENT_LATENCY"]]
corr_rate = df_reg["STEADY_POST_SWITCH_CORRECT_RATE"].astype(float).values * 100

x = np.arange(len(reg_tasks))
width = 0.35

ax.bar(x - width/2, disc_lat, width, label='Median New Module Discovery Latency (steps)', color='#3498db')
ax.bar(x + width/2, ret_lat, width, label='Median Old Module Retirement Latency (steps)', color='#e67e22')

for i in range(len(reg_tasks)):
    ax.text(x[i], max(disc_lat[i], ret_lat[i]) + 20, f"Steady Correct: {corr_rate[i]:.1f}%", ha='center', fontsize=8, weight='bold')

ax.set_ylabel('Steps after Regime Switch')
ax.set_title('F9: Autonomous Regime Adaptation Latency and Post-Switch Correct Tracking')
ax.set_xticks(x)
ax.set_xticklabels([t.replace("_", " ") for t in reg_tasks], rotation=20, ha='right', fontsize=8)
ax.set_ylim(0, 600)
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(FIG_DIR / "F9_regime_switch_correct_state_timeline.png")
plt.close(fig)
print("Saved F9")

# -------------------------------------------------------------
# F10: Useful Transitions vs Stationary Churn
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5))
trans_tasks = [t.replace("_", " ") for t in df_trans["TASK_ID"]]
x = np.arange(len(trans_tasks))
width = 0.4

useful = (df_trans["USEFUL_PROMOTIONS_TOTAL"] + df_trans["USEFUL_EVICTIONS_TOTAL"]).values
churn = (df_trans["STATIONARY_CHURN_PROMOTIONS"] + df_trans["STATIONARY_CHURN_EVICTIONS"]).values
total = useful + churn
useful_pct = useful / total * 100

ax.bar(x, useful, width, label='Useful Transitions (during switch windows)', color='#2ecc71')
ax.bar(x, churn, width, bottom=useful, label='Stationary Churn (outside switch windows)', color='#e74c3c')

for i in range(len(trans_tasks)):
    ax.text(x[i], total[i] + 5, f"Useful: {useful_pct[i]:.1f}%\nTotal: {total[i]}", ha='center', fontsize=8, weight='bold')

ax.set_ylabel('Total Transition Events (30 Seeds)')
ax.set_title('F10: Structural Plasticity vs. Churn Breakdown (Useful Adaptation vs Noise Churn)')
ax.set_xticks(x)
ax.set_xticklabels(trans_tasks, rotation=20, ha='right', fontsize=8)
ax.set_ylim(0, 400)
ax.legend(frameon=True)
plt.tight_layout()
fig.savefig(FIG_DIR / "F10_useful_transitions_vs_churn.png")
plt.close(fig)
print("Saved F10")

# -------------------------------------------------------------
# F11: I9 Conditional Gain Distribution
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
i9_gains = df_gains[(df_gains["task_id"] == "I9_Hybrid_Delay_Plus_Latent_State") & (df_gains["topology"] == "T3")]
gd_br = i9_gains["G_D_BR"].values
gr_bd = i9_gains["G_R_BD"].values

data = [gd_br, gr_bd]
labels = ["Marginal Discrete Gain\nG(D | Base + Recurrent)", "Marginal Recurrent Gain\nG(R | Base + Delay)"]

bp = ax.boxplot(data, patch_artist=True, labels=labels, widths=0.4)
colors = ['#3498db', '#9b59b6']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# Overlay jittered points
for i, d in enumerate(data):
    y = d
    x = np.random.normal(i + 1, 0.04, size=len(y))
    ax.scatter(x, y, color='black', alpha=0.5, s=20, zorder=3)

ax.axhline(0.01, color='red', linestyle='--', linewidth=1.5, label='Significance Threshold (0.01)')
ax.set_ylabel('Empirical Conditional Gain')
ax.set_title('F11: Task I9 Conditional Gains Confirming Orthogonal Complementarity (p = 2.33e-8)')
ax.legend(frameon=True, loc='upper right')
plt.tight_layout()
fig.savefig(FIG_DIR / "F11_I9_conditional_gain_distribution.png")
plt.close(fig)
print("Saved F11")

# -------------------------------------------------------------
# F12: Claim Status Scorecard Matrix
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6.5))
claims = df_claims["CLAIM_ID"].values
statuses = df_claims["STATUS"].values
short_desc = [
    "Cascade order bias present",
    "Symmetric shadow avoids bias",
    "Negative control invariance",
    "Delay/Recurrent specialization",
    "I9 hybrid complementarity",
    "I10 redundancy elimination",
    "Autonomous regime plasticity",
    "Strict vector Pareto dominance"
]

status_colors = {
    "SUPPORTED": "#2ecc71",
    "SUPPORTED_WITH_CORRECTION": "#f39c12",
    "OVERSTATED": "#e67e22",
    "UNSUPPORTED": "#e74c3c"
}

y_pos = np.arange(len(claims))
colors_list = [status_colors.get(s, "#95a5a6") for s in statuses]

bars = ax.barh(y_pos, [1]*len(claims), color=colors_list, alpha=0.85, edgecolor='black')

ax.set_yticks(y_pos)
ax.set_yticklabels([f"{c}: {d}" for c, d in zip(claims, short_desc)], fontsize=8, weight='bold')
ax.set_xlim(0, 1.3)
ax.set_xticks([])

for i, bar in enumerate(bars):
    st = statuses[i]
    ax.text(0.5, y_pos[i], st, ha='center', va='center', color='white', weight='bold', fontsize=9)

ax.set_title('F12: LEBRE v0.2 Integration Claim Status Scorecard (Forensic Seal Audit)', weight='bold')

# Legend
legend_patches = [patches.Patch(color=c, label=l) for l, c in status_colors.items()]
ax.legend(handles=legend_patches, loc='lower right', frameon=True)

plt.tight_layout()
fig.savefig(FIG_DIR / "F12_claim_status_matrix.png")
plt.close(fig)
print("Saved F12")

print("All 12 forensic figures successfully generated!")
