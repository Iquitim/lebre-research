"""dev_internal.py — DEV seeds 2176..2185 (declared DEV earlier): window/cascade designs on the internal suite I1-I14."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)
import dev_arch as A
from scratch.bench_v02_integration import BENCHMARK_TASKS, generate_v02_stream
ARMS = sys.argv[1].split(",") if len(sys.argv) > 1 else ["V045", "NLIN_W005", "CPRUNE_W005"]
def run(a):
    task, seed, arm = a
    X, y, _ = generate_v02_stream(task, seed=seed, total_steps=6000)
    m = A.Model(arm, X.shape[1], None, {"NLIN_W005": .05, "CPRUNE_W005": .05}.get(arm, .1)); e = []
    for t in range(6000):
        p = m.step(X[t], float(y[t])); e.append((y[t] - p) ** 2)
    return {"task_id": task, "seed": seed, "arm": arm, "nmse": float(np.mean(e) / np.var(y))}
if __name__ == "__main__":
    jobs = [(t, s, a) for s in range(2176, 2186) for t in BENCHMARK_TASKS for a in ARMS]
    with ProcessPoolExecutor(16) as ex: df = pd.DataFrame(list(ex.map(run, jobs)))
    df.to_csv(os.path.join(HERE, "DEV_INTERNAL.csv"), index=False)
    print(df.pivot_table(index="task_id", columns="arm", values="nmse").round(4).to_string())
    print(df.groupby("arm").nmse.mean().round(4))
