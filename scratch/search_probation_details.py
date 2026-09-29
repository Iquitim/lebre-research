import os
import re

files = [
    'experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/FINAL_CANDIDATE_FREEZE.md',
    'experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SHADOW_MULTIRATE_PREREGISTRATION.md',
    'experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SHADOW_MULTIRATE_PROTOCOL.md',
    'experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SHADOW_MULTIRATE_FINAL_REPORT.md',
    'scratch/run_v02_shadow_rent_governance.py',
    'scratch/run_v02_corrective_confirmation.py',
    'scratch/run_v02_integration_experiments.py',
    'scratch/run_v02_multirate_experiments.py',
    'scratch/run_v02_resource_compaction_experiments.py'
]

for f in files:
    if not os.path.exists(f):
        continue
    print(f"\n=== {f} ===")
    with open(f, 'r', encoding='utf-8') as fp:
        for idx, line in enumerate(fp, 1):
            if any(term in line for term in ['300', '15', 'T_prob', 'probation', 'obs_count', 'rec_age']):
                print(f"{idx:4d}: {line.strip()[:110]}")
