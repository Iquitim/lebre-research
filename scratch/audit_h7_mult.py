import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv('experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_SEED_RESULTS.csv')
tasks = sorted(df['task_id'].unique())

rows = []
for t in tasks:
    t1 = df[(df['task_id']==t) & (df['topology']=='T1')].sort_values('seed')['nmse'].values
    t1r = df[(df['task_id']==t) & (df['topology']=='T1R')].sort_values('seed')['nmse'].values
    d = t1 - t1r
    diff_means = np.mean(t1) - np.mean(t1r)
    mean_abs_d = np.mean(np.abs(d))
    w_stat, p_val = stats.wilcoxon(d, zero_method='wilcox')
    rows.append({
        'task': t,
        'mean_t1': np.mean(t1),
        'mean_t1r': np.mean(t1r),
        'diff_means': diff_means,
        'mean_abs_d': mean_abs_d,
        'w_stat': w_stat,
        'p_val': p_val
    })

res_df = pd.DataFrame(rows).sort_values('p_val')
res_df['holm_rank'] = range(1, len(res_df) + 1)
res_df['holm_alpha'] = 0.05 / (len(res_df) - res_df['holm_rank'] + 1)
res_df['holm_sig'] = res_df['p_val'] < res_df['holm_alpha']

for _, r in res_df.iterrows():
    print(f"{r['task']:38s} | DiffMeans={r['diff_means']:+.5f} | MeanAbsD={r['mean_abs_d']:.5f} | W={r['w_stat']:4.0f} | p={r['p_val']:.4e} | HolmSig={r['holm_sig']}")
