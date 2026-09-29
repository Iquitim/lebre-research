import os
import sys
sys.path.insert(0, os.path.abspath('.'))
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Ensure output directory exists
out_dir = 'experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/figures'
os.makedirs(out_dir, exist_ok=True)

# Load data
final_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/SHADOW_RENT_FINAL_RESULTS.csv')
noninf_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/PREDICTIVE_NONINFERIORITY.csv')
switch_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/SWITCHING_LATENCY_ANALYSIS.csv')
quiesc_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/QUIESCENCE_REACTIVATION_ANALYSIS.csv')
i9_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/I9_COMPLEMENTARITY_ANALYSIS.csv')
i10_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/I10_REDUNDANCY_ANALYSIS.csv')
false_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/FALSE_WAKE_ANALYSIS.csv')
pareto_df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/SCHEDULER_PARETO_ANALYSIS.csv')

# Configure clean aesthetic
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8

sched_colors = {
    'S0_CONTINUOUS': '#1f77b4',
    'S1_SHADOW_OFF': '#7f7f7f',
    'S2_PERIODIC': '#2ca02c',
    'S3_EVENT_TRIGGERED': '#d62728'
}
sched_labels = {
    'S0_CONTINUOUS': 'S0: Continuous (100%)',
    'S1_SHADOW_OFF': 'S1: Shadow Off (0%)',
    'S2_PERIODIC': 'S2: Periodic (K=5, 20%)',
    'S3_EVENT_TRIGGERED': 'S3: Event-Triggered (PH)'
}

# -------------------------------------------------------------
# F1: Compute Breakdown by Scheduler
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
scheds = ['S0_CONTINUOUS', 'S1_SHADOW_OFF', 'S2_PERIODIC', 'S3_EVENT_TRIGGERED']
live_means = [final_df[final_df['scheduler_id'] == s]['mean_live_fp'].mean() for s in scheds]
shadow_means = [final_df[final_df['scheduler_id'] == s]['mean_shadow_fp'].mean() for s in scheds]
sched_means = [final_df[final_df['scheduler_id'] == s]['mean_scheduler_fp'].mean() for s in scheds]

x = np.arange(len(scheds))
w = 0.5
b1 = ax.bar(x, live_means, w, label='Live Execution Path', color='#3b528b')
b2 = ax.bar(x, shadow_means, w, bottom=live_means, label='Removable Shadow Block', color='#5ec962')
b3 = ax.bar(x, sched_means, w, bottom=np.array(live_means) + np.array(shadow_means), label='Scheduler Overhead', color='#fde725')

ax.axhline(100.0, color='red', linestyle='--', linewidth=1.5, label='Historical Ceiling (100 FLOPs)')
for i, s in enumerate(scheds):
    tot = live_means[i] + shadow_means[i] + sched_means[i]
    ax.text(i, tot + 3, f'{tot:.1f} FLOPs', ha='center', va='bottom', fontsize=9, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels([sched_labels[s] for s in scheds], fontsize=9)
ax.set_ylabel('Mean Online Floating-Point Ops (FLOPs/step)', fontsize=10)
ax.set_title('Figure F1: Online Floating-Point Compute Breakdown Across Schedulers', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.set_ylim(0, 200)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F1_compute_breakdown_by_scheduler.png'))
plt.close()

# -------------------------------------------------------------
# F2: Predictive NMSE by Scheduler and Task
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
tasks = list(final_df['task_id'].unique())
x = np.arange(len(tasks))
w = 0.2
for idx, s in enumerate(scheds):
    sub = final_df[final_df['scheduler_id'] == s].groupby('task_id')['nmse'].mean().reindex(tasks)
    ax.bar(x + idx * w - 1.5 * w, sub.values, w, label=sched_labels[s], color=sched_colors[s], alpha=0.85)

ax.set_xticks(x)
ax.set_xticklabels([t.split('_')[0] for t in tasks], fontsize=9)
ax.set_ylabel('Normalized Mean Squared Error (NMSE)', fontsize=10)
ax.set_title('Figure F2: Prequential NMSE Comparison Across All 14 Tasks', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F2_predictive_nmse_by_scheduler_and_task.png'))
plt.close()

# -------------------------------------------------------------
# F3: Duty Cycle Distribution Across Tasks
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5), dpi=300)
duty_s2 = final_df[final_df['scheduler_id'] == 'S2_PERIODIC'].groupby('task_id')['duty_fraction'].mean().reindex(tasks)
duty_s3 = final_df[final_df['scheduler_id'] == 'S3_EVENT_TRIGGERED'].groupby('task_id')['duty_fraction'].mean().reindex(tasks)

x = np.arange(len(tasks))
w = 0.35
ax.bar(x - w/2, duty_s2.values * 100, w, label='S2: Periodic (Constant 20%)', color=sched_colors['S2_PERIODIC'])
ax.bar(x + w/2, duty_s3.values * 100, w, label='S3: Event-Triggered (Adaptive)', color=sched_colors['S3_EVENT_TRIGGERED'])

ax.axhline(20.0, color='#2ca02c', linestyle=':', label='S2 Baseline (20%)')
ax.set_xticks(x)
ax.set_xticklabels([t.split('_')[0] for t in tasks], fontsize=9)
ax.set_ylabel('Shadow Duty Fraction (% Steps Active)', fontsize=10)
ax.set_title('Figure F3: Shadow Exploration Duty Cycle Across Benchmark Tasks', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=9)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F3_duty_cycle_distribution_across_tasks.png'))
plt.close()

# -------------------------------------------------------------
# F4: Event vs Periodic Pareto Front
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)
for s in scheds:
    sub = final_df[final_df['scheduler_id'] == s]
    ax.scatter(sub['mean_total_fp'].mean(), sub['nmse'].mean(), s=140, color=sched_colors[s], label=sched_labels[s], zorder=4)
    ax.text(sub['mean_total_fp'].mean() + 2, sub['nmse'].mean() + 0.003, sched_labels[s], fontsize=8.5, fontweight='bold')

# Pareto frontier curve
p_x = [58.0, 89.53, 110.07, 169.06]
p_y = [0.4195, 0.3654, 0.3247, 0.3087]
ax.plot(p_x, p_y, 'k--', alpha=0.6, label='Empirical Pareto Frontier')

ax.axvline(100.0, color='red', linestyle='--', linewidth=1.2, label='100 FLOP Ceiling')
ax.set_xlabel('Mean Total Online Floating-Point Ops (FLOPs/step)', fontsize=10)
ax.set_ylabel('Aggregate Benchmark NMSE', fontsize=10)
ax.set_title('Figure F4: Multi-Objective Trade-Off: Compute vs. Predictive Error', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F4_event_vs_periodic_pareto_front.png'))
plt.close()

# -------------------------------------------------------------
# F5: Page-Hinkley Trace on Regime Switch (I11)
# -------------------------------------------------------------
from scratch.calibrate_event_trigger_grid import GovernedLEBREModel
from scratch.bench_v02_integration import generate_v02_stream

X, y, _ = generate_v02_stream('I11_Regime_Switch_Delay_To_Latent', 1611, 6000)
m_ph = GovernedLEBREModel(schedule_mode='S3_EVENT_TRIGGERED', ph_delta=0.10, ph_lambda=8.0, heartbeat_H=250)
t_range = range(2800, 3400)
losses, u_vals, awake = [], [], []
for t in range(6000):
    out = m_ph.step(X[t], y[t])
    if t in t_range:
        losses.append(out['ell_live'])
        u_vals.append(m_ph.cum_dev)
        awake.append(1.0 if out['is_shadow_awake'] else 0.0)

fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 6.5), sharex=True, dpi=300)
steps = np.array(list(t_range))
ax1.plot(steps, losses, color='#333333', linewidth=1, label='Prequential Loss ell_live')
ax1.axvline(3000, color='purple', linestyle='--', label='Regime Switch (Delay -> Latent)')
ax1.set_ylabel('Loss ell_live', fontsize=9)
ax1.set_title('Figure F5: Event-Triggered Sentinel Dynamics Around Regime Transition (I11)', fontsize=11, fontweight='bold')
ax1.legend(loc='upper right', fontsize=8)
ax1.grid(True, linestyle=':', alpha=0.6)

ax2.plot(steps, u_vals, color='#d62728', linewidth=1.5, label='Page-Hinkley Sum U_t')
ax2.axhline(8.0, color='red', linestyle='--', label='Alarm Threshold lambda=8.0')
ax2.set_ylabel('Cumulative U_t', fontsize=9)
ax2.legend(loc='upper right', fontsize=8)
ax2.grid(True, linestyle=':', alpha=0.6)

ax3.fill_between(steps, 0, awake, color='#5ec962', alpha=0.5, step='mid', label='Shadow Awake Status')
ax3.set_ylabel('Awake [0, 1]', fontsize=9)
ax3.set_xlabel('Streaming Timestep t', fontsize=10)
ax3.legend(loc='upper right', fontsize=8)
ax3.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F5_page_hinkley_trace_regime_switch.png'))
plt.close()

# -------------------------------------------------------------
# F6: Switching Latency Comparison
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
sw_tasks = ['I11', 'I12']
s0_lats = [switch_df[(switch_df['task_id'].str.startswith(t)) & (switch_df['scheduler_id'] == 'S0_CONTINUOUS')]['median_discovery_latency'].values[0] for t in sw_tasks]
s2_lats = [switch_df[(switch_df['task_id'].str.startswith(t)) & (switch_df['scheduler_id'] == 'S2_PERIODIC')]['median_discovery_latency'].values[0] for t in sw_tasks]
s3_lats = [switch_df[(switch_df['task_id'].str.startswith(t)) & (switch_df['scheduler_id'] == 'S3_EVENT_TRIGGERED')]['median_discovery_latency'].values[0] for t in sw_tasks]

x = np.arange(len(sw_tasks))
w = 0.25
ax.bar(x - w, s0_lats, w, label='S0: Continuous', color=sched_colors['S0_CONTINUOUS'])
ax.bar(x, s2_lats, w, label='S2: Periodic (K=5)', color=sched_colors['S2_PERIODIC'])
ax.bar(x + w, s3_lats, w, label='S3: Event-Triggered', color=sched_colors['S3_EVENT_TRIGGERED'])

ax.set_xticks(x)
ax.set_xticklabels(['I11 (Delay -> Latent)', 'I12 (Latent -> Delay)'], fontsize=9.5)
ax.set_ylabel('Median Discovery Latency (steps)', fontsize=10)
ax.set_title('Figure F6: Structural Discovery Latency Post-Transition', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F6_switching_latency_comparison.png'))
plt.close()

# -------------------------------------------------------------
# F7: Post-Switch Regret Comparison
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
regret_tasks = ['I11', 'I12', 'I14']
x = np.arange(len(regret_tasks))
w = 0.25
for idx, s in enumerate(['S0_CONTINUOUS', 'S2_PERIODIC', 'S3_EVENT_TRIGGERED']):
    vals = [switch_df[(switch_df['task_id'].str.startswith(t)) & (switch_df['scheduler_id'] == s)]['post_switch_regret'].values[0] for t in regret_tasks]
    ax.bar(x + idx * w - w, vals, w, label=sched_labels[s], color=sched_colors[s])

ax.set_xticks(x)
ax.set_xticklabels(regret_tasks, fontsize=9.5)
ax.set_ylabel('Excess Mean Squared Error (Regret)', fontsize=10)
ax.set_title('Figure F7: Post-Switch Regret Across Non-Stationary Tasks', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F7_post_switch_regret_comparison.png'))
plt.close()

# -------------------------------------------------------------
# F8: Quiescent Sleep Efficiency
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
q_tasks = ['I7 (Continuous)', 'I8 (Discrete Delay)']
q_s2 = quiesc_df[quiesc_df['scheduler_id'] == 'S2_PERIODIC']['quiescent_sleep_fraction'].values * 100
q_s3 = quiesc_df[quiesc_df['scheduler_id'] == 'S3_EVENT_TRIGGERED']['quiescent_sleep_fraction'].values * 100

x = np.arange(len(q_tasks))
w = 0.35
ax.bar(x - w/2, q_s2, w, label='S2: Periodic (80% Sleep)', color=sched_colors['S2_PERIODIC'])
ax.bar(x + w/2, q_s3, w, label='S3: Event-Triggered (99.4% Sleep)', color=sched_colors['S3_EVENT_TRIGGERED'])

ax.set_xticks(x)
ax.set_xticklabels(q_tasks, fontsize=9.5)
ax.set_ylabel('Quiescent Sleep Fraction (% Steps Asleep)', fontsize=10)
ax.set_title('Figure F8: Quiescent Phase Energy Preservation (I7, I8)', fontsize=11, fontweight='bold')
ax.set_ylim(0, 115)
for i in range(len(q_tasks)):
    ax.text(i - w/2, q_s2[i] + 2, f'{q_s2[i]:.1f}%', ha='center', fontsize=9)
    ax.text(i + w/2, q_s3[i] + 2, f'{q_s3[i]:.1f}%', ha='center', fontsize=9, fontweight='bold')
ax.legend(loc='lower right', frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F8_quiescent_sleep_efficiency.png'))
plt.close()

# -------------------------------------------------------------
# F9: I9 Complementarity Preservation
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
sched_order = ['S0_CONTINUOUS', 'S2_PERIODIC', 'S3_EVENT_TRIGGERED']
g_d_br = i9_df.set_index('scheduler_id').reindex(sched_order)['mean_G_D_BR'].values
g_r_bd = i9_df.set_index('scheduler_id').reindex(sched_order)['mean_G_R_BD'].values

x = np.arange(len(sched_order))
w = 0.35
ax.bar(x - w/2, g_d_br, w, label='Conditional Lag Gain G_D|BR', color='#3b528b')
ax.bar(x + w/2, g_r_bd, w, label='Conditional Recurrent Gain G_R|BD', color='#5ec962')

ax.axhline(0.015, color='red', linestyle='--', label='Tolerance Threshold theta_tol=0.015')
ax.set_xticks(x)
ax.set_xticklabels([sched_labels[s] for s in sched_order], fontsize=9)
ax.set_ylabel('Mean Conditional Gain', fontsize=10)
ax.set_title('Figure F9: Preservation of Hybrid Complementarity on Task I9', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F9_i9_complementarity_preservation.png'))
plt.close()

# -------------------------------------------------------------
# F10: I10 Redundancy Mitigation
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
both_fracs = i10_df.set_index('scheduler_id').reindex(scheds)['frac_both'].values * 100
x = np.arange(len(scheds))
w = 0.5
bars = ax.bar(x, both_fracs, w, color=[sched_colors[s] for s in scheds])
ax.axhline(10.0, color='red', linestyle='--', label='Gate 6 Redundancy Ceiling (10%)')

for i, b in enumerate(bars):
    val = both_fracs[i]
    ax.text(b.get_x() + b.get_width()/2, val + 0.5, f'{val:.1f}%', ha='center', fontsize=9, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels([sched_labels[s] for s in scheds], fontsize=8.5)
ax.set_ylabel('Dual-Active Occupancy Fraction (%)', fontsize=10)
ax.set_title('Figure F10: Redundant Co-Activation Mitigation on Task I10', fontsize=11, fontweight='bold')
ax.set_ylim(0, 25)
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F10_i10_redundancy_mitigation.png'))
plt.close()

# -------------------------------------------------------------
# F11: False Wake Rate on Negative Controls
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.5, 4.5), dpi=300)
alarms_i1 = false_df[false_df['task_id'] == 'I1_Memoryless_Linear'].set_index('scheduler_id').reindex(scheds)['mean_alarm_count'].values
alarms_i2 = false_df[false_df['task_id'] == 'I2_Static_Nonlinear_Negative_Control'].set_index('scheduler_id').reindex(scheds)['mean_alarm_count'].values

x = np.arange(len(scheds))
w = 0.35
ax.bar(x - w/2, alarms_i1, w, label='I1: Memoryless Linear (Benign Noise)', color='#3b528b')
ax.bar(x + w/2, alarms_i2, w, label='I2: Static Nonlinear (Mismatch Risk)', color='#d62728')

ax.set_xticks(x)
ax.set_xticklabels([sched_labels[s] for s in scheds], fontsize=8.5)
ax.set_ylabel('Mean Alarms per 6,000 Steps', fontsize=10)
ax.set_title('Figure F11: False Alarm Susceptibility on Negative Controls', fontsize=11, fontweight='bold')
ax.legend(frameon=True, facecolor='white', framealpha=0.9, fontsize=8.5)
ax.grid(axis='y', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F11_false_wake_rate_negative_controls.png'))
plt.close()

# -------------------------------------------------------------
# F12: Scheduler Decision Matrix
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
ax.axis('off')

# Table of evaluation gates
table_data = [
    ['Evaluation Criterion', 'S0 (Continuous)', 'S1 (Off)', 'S2 (Periodic K=5)', 'S3 (Event-Triggered)'],
    ['Gate 1: Total FP <= 100', 'FAIL (169.1)', 'PASS (58.0)', 'PASS (89.5)', 'FAIL (110.1)'],
    ['Gate 2: Non-Inf Margin <= 0.01', 'REFERENCE', 'FAIL (+0.111)', 'FAIL (+0.057)', 'FAIL (+0.016)'],
    ['Gate 3: RAM <= 1024 B', 'PASS (976 B)', 'PASS (904 B)', 'PASS (980 B)', 'PASS (992 B)'],
    ['Gate 4: Switch Latency (+50)', 'REFERENCE', 'FAIL (Blind)', 'FAIL (+763 steps)', 'PASS (-15 steps)'],
    ['Gate 5: Hybrid Complementarity', 'PASS (Preserved)', 'FAIL (None)', 'PASS (Preserved)', 'PASS (Preserved)'],
    ['Gate 6: Redundancy Gate (I10)', 'FAIL (18.2%)', 'PASS (0.0%)', 'PASS (9.2%)', 'PASS (8.4%)'],
    ['Quiescent Sleep Efficiency', '0.0% (Awake)', '100.0% (Asleep)', '80.0% (Periodic)', '99.4% (Deep Sleep)'],
    ['PRIMARY SEAL VERDICT', 'SEALED_BASELINE', 'DIAGNOSTIC_CONTROL', 'SELECTED_BUDGETED', 'FEASIBILITY_CHALLENGE']
]

table = ax.table(cellText=table_data, loc='center', cellLoc='center')
table.auto_set_font_size(False)
table.set_fontsize(8.5)
table.scale(1, 1.8)

# Color header
for col in range(5):
    cell = table[(0, col)]
    cell.set_facecolor('#333333')
    cell.set_text_props(color='white', fontweight='bold')

# Color verdicts
for r in range(1, len(table_data)):
    for c in range(1, 5):
        cell = table[(r, c)]
        txt = cell.get_text().get_text()
        if 'PASS' in txt or 'SELECTED' in txt:
            cell.set_facecolor('#d4edda')
        elif 'FAIL' in txt:
            cell.set_facecolor('#f8d7da')
        elif 'REFERENCE' in txt or 'SEALED' in txt:
            cell.set_facecolor('#e2e3e5')

plt.title('Figure F12: Comprehensive Scheduler Compliance & Decision Matrix', fontsize=11, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(out_dir, 'F12_scheduler_decision_matrix.png'))
plt.close()

print('All 12 figures successfully generated and saved!')
