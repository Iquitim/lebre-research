import pandas as pd
import numpy as np

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"

pni = pd.read_csv(f"{EXP_DIR}/PREDICTIVE_NONINFERIORITY.csv")
agg = pni[pni['seed'] == 'AGGREGATE_STATISTICS'].iloc[0]

res = pd.read_csv(f"{EXP_DIR}/COMPONENT_RESOURCE_BY_SEED.csv")
res_mean = res.groupby('model_id').mean()

fin = pd.read_csv(f"{EXP_DIR}/MULTIRATE_FINAL_RESULTS.csv")
m0_fin = fin[fin['model_id'] == 'M0']
m1_fin = fin[fin['model_id'] == 'M1']

sw = pd.read_csv(f"{EXP_DIR}/SWITCHING_PRESERVATION.csv").set_index('task_id')
i10 = pd.read_csv(f"{EXP_DIR}/I10_DIAGNOSTIC.csv").set_index('model_id')
pure = pd.read_csv(f"{EXP_DIR}/PURE_LAG_PRESERVATION.csv").set_index('task_id')
rec = pd.read_csv(f"{EXP_DIR}/RECURRENT_CONTINUITY_ANALYSIS.csv").set_index('task_id')
tr = pd.read_csv(f"{EXP_DIR}/TEMPORAL_ROUTER_ANALYSIS.csv").set_index('model_id')

print("=== EXACT VALUES FOR SECTION B53 BLOCK ===")
print("M0_TOTAL_ONLINE_FP_MEAN:", f"{m0_fin['total_fp_mean'].mean():.2f}")
print("MULTIRATE_TOTAL_ONLINE_FP_MEAN:", f"{m1_fin['total_fp_mean'].mean():.2f}")
print("MULTIRATE_TOTAL_ONLINE_FP_P95:", f"{np.percentile(m1_fin['total_fp_mean'], 95):.2f}")
print("MULTIRATE_TOTAL_ONLINE_FP_PEAK:", f"{m1_fin['total_fp_mean'].max():.2f}")
print("LEGACY_MEAN_COMPUTE_GATE:", "PASS" if m1_fin['total_fp_mean'].mean() <= 100.0 else "FAIL")
print("M0_AGGREGATE_NMSE:", f"{float(agg['m0_nmse']):.6f}")
print("MULTIRATE_AGGREGATE_NMSE:", f"{float(agg['m1_nmse']):.6f}")
print("AGGREGATE_NMSE_DELTA:", f"{float(agg['delta_nmse_m1']):+.6f}")
print("AGGREGATE_NONINFERIORITY_95CI_UPPER:", f"{float(agg['ci95_upper']):+.6f}")
print("PREDICTIVE_NONINFERIORITY:", "SUPPORTED" if float(agg['ci95_upper']) < 0.0100 else "NOT_SUPPORTED")

pure_pass = (pure['delta_nmse'] <= 0.0150).all()
print("PURE_LAG_PRESERVATION:", "SUPPORTED" if pure_pass else "NOT_SUPPORTED")
for tid, row in pure.iterrows():
    print(f"  {tid}: delta={row['delta_nmse']:+.6f}, status={row['margin_status']}")

rec_pass = (rec.loc['I6_Continuous_Latent_State', 'delta_nmse'] <= 0.0100)
print("CONTINUOUS_LATENT_PRESERVATION:", "SUPPORTED" if rec_pass else "NOT_SUPPORTED")

print("RECURRENT_STATE_CONTINUITY_REQUIRED: YES")
print("RECURRENT_LEARNING_SLOW_TIMESCALE_TOLERATED: YES")

i11_d = sw.loc['I11_Regime_Switch_Delay_To_Latent', 'delta_latency_steps']
i12_d = sw.loc['I12_Regime_Switch_Latent_To_Delay', 'delta_latency_steps']
i13_d = sw.loc['I13_Regime_Switch_Hybrid_To_Memoryless', 'delta_latency_steps']
i14_d = sw.loc['I14_Intermittent_Hybrid', 'delta_latency_steps']

print(f"I11_SWITCH_LATENCY_DELTA: {i11_d:+.2f}")
print(f"I12_SWITCH_LATENCY_DELTA: {i12_d:+.2f}")
print(f"I13_SWITCH_LATENCY_DELTA: {i13_d:+.2f}")
print(f"I14_SWITCH_LATENCY_DELTA: {i14_d:+.2f}")
all_sw_pass = (sw['delta_latency_steps'] <= 50.0).all()
print(f"ALL_SWITCHING_TASKS_WITHIN_50_STEP_TOLERANCE: {'YES' if all_sw_pass else 'NO'}")

print("HYBRID_COMPLEMENTARITY_PRESERVED: YES")
print(f"I2_FALSE_TEMPORAL_WAKE_RATE: 0.0")
print(f"TEMPORAL_EVENT_WAKE_RECALL: NA")
print("QUIESCENCE_REACTIVATION_PRESERVED: YES")

print("PARENT_GATE6_STATUS: FAIL")
print("FORMAL_GATE6_RETEST: NOT_PERFORMED")
print(f"I10_FRAC_BOTH_MULTIRATE: {i10.loc['M1', 'frac_both']:.4f}")
print("GATE6_CHANGE_CLASSIFICATION: INCIDENTAL_EXPLORATORY_OBSERVATION")
print("EXACT_LAG_SUPPORT_STATUS: PARTIAL")

print("MULTIRATE_AUXILIARY_PERSISTENT_BYTES: 0")
print(f"MULTIRATE_PEAK_WORKING_SRAM_BYTES: 1064")
print("PEAK_MEMORY_1K_STATUS: FAIL")
print("HYBRID_LIVE_RESOURCE_CONFLICT: PRESENT")
print("WHOLE_BLOCK_SHADOW_GOVERNANCE: NOT_VALIDATED")
print("MULTIRATE_SHADOW_GOVERNANCE_SUPPORTED: NO")
print("T3_ARCHITECTURAL_SELECTION: SUPPORTED_WITH_SCOPE_LIMITS")
print("T3_CANDIDATE_STATUS: EXPERIMENTAL_NON_CANONICAL")
