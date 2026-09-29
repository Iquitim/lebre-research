import os
import re

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
            if f.endswith('.csv') or f.endswith('.json') or f.endswith('.py') or f.endswith('.md'):
                p = os.path.join(root, f)
                try:
                    with open(p, 'r', encoding='utf-8', errors='ignore') as fp:
                        content = fp.read()
                        for s in test_seeds:
                            # Match exact seed numbers
                            if re.search(r'\b' + str(s) + r'\b', content):
                                collisions.setdefault(s, []).append(p.replace('\\\\', '/'))
                except Exception:
                    pass

print(f"Seed collisions found in prior studies: {len(collisions)}")
if collisions:
    for s, files in sorted(collisions.items()):
        print(f"Seed {s}: in {files[:3]}")
else:
    print("Zero collisions! All seeds 1701..1740 are 100% fresh and independent of prior studies.")
