import os
import time

exp_dir = 'experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01'
files = [
    'COMPONENT_SENSITIVITY_DEV_RESULTS.csv',
    'COMPONENT_RATE_BOUNDARIES.csv',
    'MULTIRATE_DEV_RESULTS.csv',
    'FINAL_CANDIDATE_FREEZE.md',
    'MULTIRATE_FINAL_RESULTS.csv',
    'SHADOW_MULTIRATE_FINAL_REPORT.md',
    'SHADOW_MULTIRATE_MANIFEST.json'
]

for f in files:
    p = os.path.join(exp_dir, f)
    mtime = os.path.getmtime(p)
    ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))
    print(f"{f:38s}: {ts}")
