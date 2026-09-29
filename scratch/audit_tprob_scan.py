import os
import re

files_to_check = [
    'scratch/bench_v02_integration.py',
    'scratch/run_v02_integration_experiments.py',
    'scratch/run_v02_resource_compaction_experiments.py',
    'scratch/run_v02_corrective_confirmation.py',
    'scratch/run_v02_shadow_rent_governance.py',
    'scratch/run_v02_multirate_experiments.py',
    'scratch/run_final_evaluation.py'
]

keywords = ['probation', 't_prob', 'age >=', 'exposures >=', 'age >', 'exposures >', 'theta_promote', 'promotions_lag', 'promotions_rec']

for f in files_to_check:
    print(f"\n=================== {f} ===================")
    if not os.path.exists(f):
        print("File does not exist.")
        continue
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        for idx, line in enumerate(fp, 1):
            line_l = line.lower()
            if any(k in line_l for k in keywords):
                print(f"{idx:4d}: {line.strip()[:120]}")
