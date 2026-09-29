import pandas as pd
import numpy as np

sens = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/COMPONENT_SENSITIVITY_DEV_RESULTS.csv')
ladder = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/COMPONENT_RATE_BOUNDARIES.csv')

print("=== COMPONENT SENSITIVITY AT K=5 ===")
for m in sens['model_id'].unique():
    sub = sens[sens['model_id'] == m]
    d0 = sens[sens['model_id'] == 'D0']
    d_nmse = sub['nmse'].mean() - d0['nmse'].mean()
    fp = sub['total_fp_mean'].mean()
    s_fp = sub['shadow_fp_mean'].mean()
    print(f"{m:6s}: Total FP={fp:6.2f}, Shadow FP={s_fp:5.2f}, Delta NMSE={d_nmse:+.6f}")

print("\n=== COMPONENT RATE LADDERS ===")
for m in ladder['model_id'].unique():
    sub = ladder[ladder['model_id'] == m]
    d0 = ladder[ladder['model_id'] == 'PROBE_K1']
    d_nmse = sub['nmse'].mean() - d0['nmse'].mean()
    fp = sub['total_fp_mean'].mean()
    s_fp = sub['shadow_fp_mean'].mean()
    print(f"{m:12s}: Total FP={fp:6.2f}, Shadow FP={s_fp:5.2f}, Delta NMSE={d_nmse:+.6f}")
