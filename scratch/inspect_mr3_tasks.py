import pandas as pd

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"
dev = pd.read_csv(f"{EXP_DIR}/MULTIRATE_DEV_RESULTS.csv")

d0 = dev[dev['model_id'] == 'D0'].set_index(['task_id', 'seed'])
mr3 = dev[dev['model_id'] == 'MR3'].set_index(['task_id', 'seed'])

tasks = dev['task_id'].unique()
print("=== MR3 DETECTION AND PERFORMANCE BY TASK ===")
for t in tasks:
    sub_d0 = d0.loc[t]
    sub_mr3 = mr3.loc[t]
    d_nmse = (sub_mr3['nmse'] - sub_d0['nmse']).mean()
    awake = sub_mr3['awake_fraction'].mean()
    prom_lag = sub_mr3['promotions_lag'].mean()
    prom_rec = sub_mr3['promotions_rec'].mean()
    print(f"{t:38s}: Awake={awake:5.3f}, PromLag={prom_lag:4.1f}, PromRec={prom_rec:4.1f}, Delta NMSE={d_nmse:+.6f}")
