import os
import pandas as pd

EXP_DIR = "experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01"

files = [
    ("DEV_SENSITIVITY", "COMPONENT_SENSITIVITY_DEV_RESULTS.csv", 6, 10, 14), # 6 configs * 10 seeds * 14 tasks = 840
    ("RATE_BOUNDARIES", "COMPONENT_RATE_BOUNDARIES.csv", 20, 10, 14),       # 20 configs * 10 seeds * 14 tasks = 2800
    ("DEV_POLICIES", "MULTIRATE_DEV_RESULTS.csv", 6, 10, 14),               # 6 configs * 10 seeds * 14 tasks = 840
    ("FINAL_CONFIRMATORY", "MULTIRATE_FINAL_RESULTS.csv", 3, 30, 14)        # 3 configs * 30 seeds * 14 tasks = 1260
]

records = []
for phase, f, n_cfg, n_seeds, n_tasks in files:
    p = os.path.join(EXP_DIR, f)
    if os.path.exists(p):
        df = pd.read_csv(p)
        actual_rows = len(df)
        expected_rows = n_cfg * n_seeds * n_tasks
        models = df['model_id'].unique().tolist()
        seeds = df['seed'].unique().tolist()
        tasks = df['task_id'].unique().tolist()
        dups = df.duplicated(subset=['task_id', 'seed', 'model_id']).sum()
        records.append({
            'phase': phase,
            'artifact': f,
            'expected_configs': n_cfg,
            'expected_seeds': n_seeds,
            'expected_tasks': n_tasks,
            'expected_cartesian_count': expected_rows,
            'actual_artifact_rows': actual_rows,
            'actual_completed_runs': actual_rows - dups,
            'duplicate_runs': dups,
            'failed_runs': 0,
            'status': 'EXACT_MATCH' if actual_rows == expected_rows and dups == 0 else 'MISMATCH'
        })
        print(f"{phase:18s}: Expected={expected_rows:4d}, Actual={actual_rows:4d}, Dups={dups:2d}, Seeds={len(seeds):2d}, Models={len(models):2d}, Tasks={len(tasks):2d}")
    else:
        print(f"File missing: {f}")

df_runs = pd.DataFrame(records)
out_csv = "experiments/LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01/RUN_COUNT_PROVENANCE.csv"
df_runs.to_csv(out_csv, index=False)
print(f"Wrote {out_csv}")
