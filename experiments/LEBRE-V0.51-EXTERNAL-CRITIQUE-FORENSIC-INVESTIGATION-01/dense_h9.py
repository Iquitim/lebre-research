"""dense_h9.py — H9 analogue with the project's own dense-window variant (v0.5) on B1-B3, same seeds/generators."""
import os, sys, numpy as np, pandas as pd
from concurrent.futures import ProcessPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import forensic_runs as F
from lebre_v05 import LebreV05
def one(a):
    task, seed = a
    X, y = F.generate(task, seed); m = LebreV05(d=5, season=None); e = []; fp = []
    for t in range(len(y)):
        b = sum(m.fp.values()); p = m.step(X[t], float(y[t])); e.append((y[t] - p) ** 2); fp.append(sum(m.fp.values()) - b)
    return {"task": task, "seed": seed, "nmse_dense": float(np.mean(e) / np.var(y)), "fp_dense": float(np.mean(fp))}
if __name__ == "__main__":
    with ProcessPoolExecutor(16) as ex:
        df = pd.DataFrame(list(ex.map(one, [(t, s) for t in ("B1", "B2", "B3") for s in F.SEEDS])))
    df.to_csv(os.path.join(HERE, "RUN_DENSE_H9.csv"), index=False); print(df.groupby("task").mean(numeric_only=True))
