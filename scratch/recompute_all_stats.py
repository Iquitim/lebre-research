import os
import math
import numpy as np
import pandas as pd
from scipy import stats

FINAL_CSV = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/MULTIRATE_FINAL_RESULTS.csv"
OUT_DIR = "experiments/LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(FINAL_CSV)

# 1. Non-inferiority recheck
m0 = df[df['model_id'] == 'M0'].groupby('seed')['nmse'].mean()
m1 = df[df['model_id'] == 'M1'].groupby('seed')['nmse'].mean()
delta = m1 - m0
mean_d = delta.mean()
std_d = delta.std(ddof=1)
se_d = std_d / math.sqrt(len(delta))
df_deg = len(delta) - 1
t90 = stats.t.ppf(0.90, df=df_deg)
t95 = stats.t.ppf(0.95, df=df_deg)
t99 = stats.t.ppf(0.99, df=df_deg)

ci90_u = mean_d + t90 * se_d
ci95_u = mean_d + t95 * se_d
ci99_u = mean_d + t99 * se_d

recheck_pni = pd.DataFrame([{
    'n_seeds': len(delta),
    'm0_mean_nmse': m0.mean(),
    'm1_mean_nmse': m1.mean(),
    'mean_delta_nmse': mean_d,
    'std_delta_nmse': std_d,
    'se_delta_nmse': se_d,
    'ci90_upper': ci90_u,
    'ci95_upper': ci95_u,
    'ci99_upper': ci99_u,
    'margin': 0.0100,
    'p_value_noninf': stats.t.sf((0.0100 - mean_d) / se_d, df=df_deg), # P(T >= t_stat)
    'status': 'FAIL' if ci95_u >= 0.0100 else 'PASS'
}])
recheck_pni.to_csv(os.path.join(OUT_DIR, "NONINFERIORITY_RECHECK.csv"), index=False)
print("Wrote NONINFERIORITY_RECHECK.csv")

# 2. Pure Lag Recheck
pure_tasks = ["I3_Single_Exact_Delay", "I4_Multi_Sparse_Delay", "I5_Moving_Delay_Support", "I8_Quiescent_Discrete_Delay"]
pure_records = []
for t in pure_tasks:
    sub_m0 = df[(df['model_id'] == 'M0') & (df['task_id'] == t)]
    sub_m1 = df[(df['model_id'] == 'M1') & (df['task_id'] == t)]
    d_nmse = sub_m1['nmse'].mean() - sub_m0['nmse'].mean()
    pure_records.append({
        'task_id': t,
        'm0_nmse': sub_m0['nmse'].mean(),
        'm1_nmse': sub_m1['nmse'].mean(),
        'delta_nmse': d_nmse,
        'margin': 0.0150,
        'status': 'PASS' if d_nmse <= 0.0150 else 'FAIL',
        'm0_f1': sub_m0['support_f1'].mean(),
        'm1_f1': sub_m1['support_f1'].mean()
    })
df_pure = pd.DataFrame(pure_records)
df_pure.to_csv(os.path.join(OUT_DIR, "PURE_LAG_RECHECK.csv"), index=False)
print("Wrote PURE_LAG_RECHECK.csv")

# 3. Switching Recheck
switch_tasks = ["I11_Regime_Switch_Delay_To_Latent", "I12_Regime_Switch_Latent_To_Delay",
                "I13_Regime_Switch_Hybrid_To_Memoryless", "I14_Intermittent_Hybrid"]
sw_records = []
for t in switch_tasks:
    sub_m0 = df[(df['model_id'] == 'M0') & (df['task_id'] == t)]
    sub_m1 = df[(df['model_id'] == 'M1') & (df['task_id'] == t)]
    lat_m0 = sub_m0['switch_latency'].dropna().mean()
    lat_m1 = sub_m1['switch_latency'].dropna().mean()
    d_lat = lat_m1 - lat_m0
    sw_records.append({
        'task_id': t,
        'm0_latency_steps': lat_m0,
        'm1_latency_steps': lat_m1,
        'delta_latency_steps': d_lat,
        'threshold_steps': 50.0,
        'status': 'PASS' if d_lat <= 50.0 else 'FAIL'
    })
df_sw = pd.DataFrame(sw_records)
df_sw.to_csv(os.path.join(OUT_DIR, "SWITCHING_RECHECK.csv"), index=False)
print("Wrote SWITCHING_RECHECK.csv")

# 4. I9 Recheck
i9_m0 = df[(df['model_id'] == 'M0') & (df['task_id'] == "I9_Hybrid_Delay_Plus_Latent_State")]
i9_m1 = df[(df['model_id'] == 'M1') & (df['task_id'] == "I9_Hybrid_Delay_Plus_Latent_State")]
df_i9 = pd.DataFrame([
    {
        'model_id': 'M0',
        'g_db': i9_m0['g_db_mean'].mean(),
        'g_rb': i9_m0['g_rb_mean'].mean(),
        'g_d_br': i9_m0['g_d_br_mean'].mean(),
        'g_r_bd': i9_m0['g_r_bd_mean'].mean(),
        'complementarity_present': 'YES' if (i9_m0['g_d_br_mean'].mean() > 0 and i9_m0['g_r_bd_mean'].mean() > 0) else 'NO'
    },
    {
        'model_id': 'M1',
        'g_db': i9_m1['g_db_mean'].mean(),
        'g_rb': i9_m1['g_rb_mean'].mean(),
        'g_d_br': i9_m1['g_d_br_mean'].mean(),
        'g_r_bd': i9_m1['g_r_bd_mean'].mean(),
        'complementarity_present': 'YES' if (i9_m1['g_d_br_mean'].mean() > 0 and i9_m1['g_r_bd_mean'].mean() > 0) else 'NO'
    }
])
df_i9.to_csv(os.path.join(OUT_DIR, "I9_RECHECK.csv"), index=False)
print("Wrote I9_RECHECK.csv")

# 5. I10 Recheck
i10_m0 = df[(df['model_id'] == 'M0') & (df['task_id'] == "I10_Redundant_Temporal_Structure")]
i10_m1 = df[(df['model_id'] == 'M1') & (df['task_id'] == "I10_Redundant_Temporal_Structure")]
i10_s2 = df[(df['model_id'] == 'S2_K5') & (df['task_id'] == "I10_Redundant_Temporal_Structure")]
df_i10 = pd.DataFrame([
    {'model_id': 'M0', 'frac_both': i10_m0['frac_both'].mean(), 'frac_both_ss': i10_m0['frac_both_ss'].mean(), 'gate6_threshold': 0.05, 'gate6_status': 'FAIL'},
    {'model_id': 'M1', 'frac_both': i10_m1['frac_both'].mean(), 'frac_both_ss': i10_m1['frac_both_ss'].mean(), 'gate6_threshold': 0.05, 'gate6_status': 'FAIL'},
    {'model_id': 'S2_K5', 'frac_both': i10_s2['frac_both'].mean(), 'frac_both_ss': i10_s2['frac_both_ss'].mean(), 'gate6_threshold': 0.05, 'gate6_status': 'FAIL'}
])
df_i10.to_csv(os.path.join(OUT_DIR, "I10_RECHECK.csv"), index=False)
print("Wrote I10_RECHECK.csv")

# 6. Resource Accounting Recheck
res_records = []
for m in ['M0', 'M1', 'S2_K5']:
    sub = df[df['model_id'] == m]
    tot = sub['total_fp_mean']
    res_records.append({
        'model_id': m,
        'mean_total_fp': tot.mean(),
        'median_total_fp': tot.median(),
        'p95_total_fp': np.percentile(tot, 95),
        'peak_total_fp': tot.max(),
        'live_fp_mean': sub['live_fp_mean'].mean(),
        'shadow_fp_mean': sub['shadow_fp_mean'].mean(),
        'router_fp_mean': sub['router_fp_mean'].mean(),
        'int_ops_mean': sub['int_ops_mean'].mean(),
        'occupied_bytes_mean': sub['occupied_bytes_mean'].mean(),
        'occupied_bytes_peak': sub['occupied_bytes_peak'].max(),
        'compute_gate_status': 'PASS' if tot.mean() <= 100.0 else 'FAIL'
    })
df_res = pd.DataFrame(res_records)
df_res.to_csv(os.path.join(OUT_DIR, "RESOURCE_ACCOUNTING_RECHECK.csv"), index=False)
print("Wrote RESOURCE_ACCOUNTING_RECHECK.csv")
