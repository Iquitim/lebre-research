import pandas as pd
import numpy as np
from pathlib import Path

EXP_DIR = Path('experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01')
df_final = pd.read_csv(EXP_DIR / 'RESOURCE_COMPACTION_FINAL_RESULTS.csv')
df_ranking = pd.read_csv(EXP_DIR / 'CANDIDATE_RANKING_PARITY.csv')
df_events = pd.read_csv(EXP_DIR / 'STRUCTURAL_EVENT_PARITY.csv')
df_stress = pd.read_csv(EXP_DIR / 'NUMERICAL_STRESS_RESULTS.csv')

c0 = df_final[df_final['variant'] == 'C0']
c1 = df_final[df_final['variant'] == 'C1']

final_rank = df_ranking[df_ranking['cohort'] == 'FINAL']
final_events = df_events[df_events['cohort'] == 'FINAL']

print('C0 Aggregate NMSE:', f"{c0['nmse'].mean():.4f}")
print('C1 Aggregate NMSE:', f"{c1['nmse'].mean():.4f}")
print('Paired Delta NMSE:', f"{(c1['nmse'].values - c0['nmse'].values).mean():+.6f}")

print('Top-1 Agreement:', f"{final_rank['top1_agreement_rate'].mean():.4f}")
print('Top-M (Top-3) Agreement:', f"{final_rank['top3_set_agreement_rate'].mean():.4f}")
total_probes_eval = 420 * 300
total_disag = final_rank['threshold_crossing_disagreements'].sum()
print('Promotion Threshold Disagreement Rate:', f"{total_disag / (total_probes_eval * 160):.6f}")
print('Arbitration Disagreement Rate:', f"{(1.0 - final_events['state_agreement_rate'].mean()):.4f}")

print('T3 I10 frac_both C0:', f"{c0[c0['task_id'].str.contains('I10')]['frac_both'].mean():.4f}")
print('T3 I10 frac_both C1:', f"{c1[c1['task_id'].str.contains('I10')]['frac_both'].mean():.4f}")

print('C0 Live FP FLOPs:', f"{c0['live_flops_mean'].mean():.1f}")
print('C1 Live FP FLOPs:', f"{c1['live_flops_mean'].mean():.1f}")
print('C0 Integer Ops:', f"{c0['int_ops_mean'].mean():.1f}")
print('C1 Integer Ops:', f"{c1['int_ops_mean'].mean():.1f}")
print('C1 Cast Ops:', f"{c1['cast_ops_mean'].mean():.1f}")
print('C0 Memory Traffic:', f"{c0['bytes_moved_mean'].mean():.1f}")
print('C1 Memory Traffic:', f"{c1['bytes_moved_mean'].mean():.1f}")

print('Stress Underflow Sum:', df_stress['underflow_count'].sum())
print('Stress Overflow Sum:', df_stress['overflow_count'].sum())
print('Stress Stagnation Sum:', df_stress['update_stagnation_count'].sum())
