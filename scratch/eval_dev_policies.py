import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/MULTIRATE_DEV_RESULTS.csv')
d0 = df[df['model_id'] == 'D0'].set_index(['task_id', 'seed'])

for m in df['model_id'].unique():
    sub = df[df['model_id'] == m].set_index(['task_id', 'seed'])
    seed_d0 = d0.groupby('seed')['nmse'].mean()
    seed_m = sub.groupby('seed')['nmse'].mean()
    delta = seed_m - seed_d0
    mean_delta = delta.mean()
    ci95 = mean_delta + stats.t.ppf(0.95, df=len(delta)-1) * (delta.std(ddof=1) / np.sqrt(len(delta)))
    total_fp = sub['total_fp_mean'].mean()
    live_fp = sub['live_fp_mean'].mean()
    shadow_fp = sub['shadow_fp_mean'].mean()
    print(f"Model: {m:6s} | Total FP: {total_fp:6.2f} (Live: {live_fp:5.2f}, Shadow: {shadow_fp:5.2f}) | NMSE: {sub['nmse'].mean():.6f} | Delta: {mean_delta:+.6f} | 95% CI Upper: {ci95:+.6f}")
