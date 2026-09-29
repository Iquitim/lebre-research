import sys
from pathlib import Path
sys.path.insert(0, '.')
from scratch.run_dynamic_lag_lifecycle_01 import run_single_stream, VARIANTS

print(f"Testing all {len(VARIANTS)} variants on D1 seed 701...")
for var in VARIANTS:
    s, evs, trajs = run_single_stream("D1_Single_Static_Delay", 701, var, phase="DEV")
    print(f"  {var:<40}: NMSE = {s['nmse']:.4f} | FLOPs = {s['mean_flops']:.1f} | Mem = {s['memory_bytes']} B")
print("All variants executed successfully!")
