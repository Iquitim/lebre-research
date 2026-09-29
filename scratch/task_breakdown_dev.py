import pandas as pd
import numpy as np

df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/MULTIRATE_DEV_RESULTS.csv')
d0 = df[df['model_id'] == 'D0'].set_index(['task_id', 'seed'])

tasks = df['task_id'].unique()
models = ['MR1_A', 'MR1_B', 'MR1_C', 'MR2', 'MR3']

print(f"{'Task':32s} | " + " | ".join([f"{m:7s}" for m in models]))
print("-" * 80)
for t in tasks:
    row = [f"{t:32s}"]
    for m in models:
        sub = df[(df['model_id'] == m) & (df['task_id'] == t)].set_index('seed')
        sub_d0 = df[(df['model_id'] == 'D0') & (df['task_id'] == t)].set_index('seed')
        d = (sub['nmse'] - sub_d0['nmse']).mean()
        row.append(f"{d:+7.4f}")
    print(" | ".join(row))

print("-" * 80)
print(f"{'Mean Compute (FP)':32s} | " + " | ".join([f"{df[df['model_id']==m]['total_fp_mean'].mean():7.2f}" for m in models]))
