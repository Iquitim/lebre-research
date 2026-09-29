import pandas as pd
import numpy as np

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"

print("=== 1. PREDICTIVE NON-INFERIORITY ===")
pni = pd.read_csv(f"{EXP_DIR}/PREDICTIVE_NONINFERIORITY.csv")
print(pni.tail(3))

print("\n=== 2. COMPONENT RESOURCES (MEANS ACROSS SEEDS) ===")
res = pd.read_csv(f"{EXP_DIR}/COMPONENT_RESOURCE_BY_SEED.csv")
print(res.groupby('model_id')[['live_fp_mean', 'shadow_fp_mean', 'router_fp_mean', 'total_fp_mean', 'occupied_bytes_mean', 'occupied_bytes_peak']].mean())

fin = pd.read_csv(f"{EXP_DIR}/MULTIRATE_FINAL_RESULTS.csv")
for m in ['M0', 'M1', 'S2_K5']:
    sub = fin[fin['model_id'] == m]
    tot = sub['total_fp_mean']
    print(f"{m:6s} Total FP: mean={tot.mean():.2f}, median={tot.median():.2f}, P90={np.percentile(tot, 90):.2f}, P95={np.percentile(tot, 95):.2f}, P99={np.percentile(tot, 99):.2f}, peak={tot.max():.2f}")

print("\n=== 3. PURE LAG PRESERVATION ===")
pure = pd.read_csv(f"{EXP_DIR}/PURE_LAG_PRESERVATION.csv")
print(pure[['task_id', 'm0_nmse_mean', 'm1_nmse_mean', 'delta_nmse', 'margin_status', 'm0_support_f1', 'm1_support_f1']])

print("\n=== 4. RECURRENT CONTINUITY ===")
rec = pd.read_csv(f"{EXP_DIR}/RECURRENT_CONTINUITY_ANALYSIS.csv")
print(rec)

print("\n=== 5. SWITCHING PRESERVATION ===")
sw = pd.read_csv(f"{EXP_DIR}/SWITCHING_PRESERVATION.csv")
print(sw[['task_id', 'm0_switch_latency_steps', 'm1_switch_latency_steps', 'delta_latency_steps', 'status']])

print("\n=== 6. I9 COMPLEMENTARITY ===")
i9 = pd.read_csv(f"{EXP_DIR}/I9_COMPLEMENTARITY.csv")
print(i9)

print("\n=== 7. I10 DIAGNOSTIC ===")
i10 = pd.read_csv(f"{EXP_DIR}/I10_DIAGNOSTIC.csv")
print(i10)

print("\n=== 8. QUIESCENCE REACTIVATION ===")
q = pd.read_csv(f"{EXP_DIR}/QUIESCENCE_REACTIVATION.csv")
print(q)

print("\n=== 9. TEMPORAL ROUTER ANALYSIS ===")
tr = pd.read_csv(f"{EXP_DIR}/TEMPORAL_ROUTER_ANALYSIS.csv")
print(tr)

print("\n=== 10. FIRST DIVERGENCE TRACE ===")
fdiv = pd.read_csv(f"{EXP_DIR}/FIRST_DIVERGENCE_TRACE.csv")
print(fdiv)
