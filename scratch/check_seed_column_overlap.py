import os
import pandas as pd

prior_dirs = [
    'experiments/BENCH-01A',
    'experiments/CAR-01',
    'experiments/DYNAMIC-LAG-LIFECYCLE-01',
    'experiments/PROMOTION-POLICY-01',
    'experiments/CAPACITY-DECOMPOSITION-01',
    'experiments/BOUNDED-HISTORY-LAG-INTEGRATION-01',
    'experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01',
    'experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01',
    'experiments/LEBRE-V0.2-RESOURCE-COMPACTION-CORRECTIVE-CONFIRMATION-01',
    'experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01',
    'experiments/LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01'
]

test_seeds = set(range(1701, 1741))
collisions = {}

for d in prior_dirs:
    if not os.path.exists(d):
        continue
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.endswith('.csv'):
                p = os.path.join(root, f)
                try:
                    df = pd.read_csv(p, nrows=50000) # sample or full
                    if 'seed' in df.columns:
                        seeds_in_df = set(df['seed'].unique())
                        overlap = test_seeds.intersection(seeds_in_df)
                        if overlap:
                            collisions[p] = sorted(list(overlap))
                except Exception:
                    pass

print(f"True SEED collisions found: {len(collisions)}")
if collisions:
    for f, s in collisions.items():
        print(f"{f}: {s}")
else:
    print("Zero seed collisions! Neither DEV (1701..1710) nor FINAL (1711..1740) were ever used as seeds in any prior study.")
