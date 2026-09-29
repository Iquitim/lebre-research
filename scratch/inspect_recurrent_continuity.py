import pandas as pd
import numpy as np

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"

sens = pd.read_csv(f"{EXP_DIR}/COMPONENT_SENSITIVITY_DEV_RESULTS.csv")
ladder = pd.read_csv(f"{EXP_DIR}/COMPONENT_RATE_BOUNDARIES.csv")

d0_sens = sens[sens['model_id'] == 'D0']
d0_nmse = d0_sens['nmse'].mean()

print("=== DEV SENSITIVITY D9F vs D9L ===")
for m in ['D0', 'D9F', 'D9L']:
    sub = sens[sens['model_id'] == m]
    d_nmse = sub['nmse'].mean() - d0_nmse
    tot_fp = sub['total_fp_mean'].mean()
    shadow_fp = sub['shadow_fp_mean'].mean()
    i6_nmse = sub[sub['task_id'] == 'I6_Continuous_Latent_State']['nmse'].mean()
    i7_nmse = sub[sub['task_id'] == 'I7_Quiescent_Continuous_State']['nmse'].mean()
    print(f"{m:6s}: Total FP={tot_fp:6.2f}, Shadow FP={shadow_fp:5.2f}, Delta NMSE={d_nmse:+.6f}, I6 NMSE={i6_nmse:.6f}, I7 NMSE={i7_nmse:.6f}")

print("\n=== RECURRENT RATE LADDERS ===")
ref_ladder = ladder[ladder['model_id'] == 'REC_FWD_K1']['nmse'].mean()
for m in ['REC_FWD_K1', 'REC_FWD_K2', 'REC_FWD_K5', 'REC_FWD_K10', 'REC_LRN_K1', 'REC_LRN_K2', 'REC_LRN_K5', 'REC_LRN_K10']:
    sub = ladder[ladder['model_id'] == m]
    d_nmse = sub['nmse'].mean() - ref_ladder
    tot_fp = sub['total_fp_mean'].mean()
    shadow_fp = sub['shadow_fp_mean'].mean()
    i6_nmse = sub[sub['task_id'] == 'I6_Continuous_Latent_State']['nmse'].mean()
    i7_nmse = sub[sub['task_id'] == 'I7_Quiescent_Continuous_State']['nmse'].mean()
    print(f"{m:12s}: Total FP={tot_fp:6.2f}, Shadow FP={shadow_fp:5.2f}, Delta NMSE={d_nmse:+.6f}, I6 NMSE={i6_nmse:.6f}, I7 NMSE={i7_nmse:.6f}")
