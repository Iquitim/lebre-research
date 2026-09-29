"""Part 2' of PREREG_ADDENDUM_V042.md: LEBRE v0.4.1 on the BENCH-03 tasks/seeds (baselines unchanged)."""
import hashlib, os, sys, time
from concurrent.futures import ProcessPoolExecutor
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import bench03 as C
from lebre_v042 import LebreV042 as LebreV041

class V041Step(C.B.Step):
    def __init__(self, d): self.m = LebreV041(d=d)
    def step(self, x, y):
        b = sum(self.m.fp.values()); p = self.m.step(np.asarray(x, float), float(y)); return p, sum(self.m.fp.values()) - b
    def get_memory_bytes(self): return self.m.memory_bytes()

def run(args):
    task, seed = args
    X, y, split = C.load(task, seed); D = X.shape[1]
    ts = split if split is not None else int(0.30 * len(X)); st = V041Step(D)
    r = C.B.R.run_full_stream(st, X, y, ts, is_track_b=True); r.pop("trace", None)
    return {"track": C.TASKS[task][0], "task_id": task, "model_id": "LEBRE_V042", "seed": seed, "T": len(X), "D": D, **r,
            "coverage": st.m.cover_hits / max(st.m.cover_n, 1), "n_active_final": len(st.m.active), "n_events": len(st.m.events)}

if __name__ == "__main__":
    for f, h in (("PREREG_ADDENDUM_V042.md", "PREREG_ADDENDUM_V042_SHA256.txt"), ("lebre_v042.py", "FREEZE_V042_SHA256.txt")):
        assert hashlib.sha256(open(os.path.join(HERE, f), "rb").read()).hexdigest() == open(os.path.join(HERE, h)).read().split()[0].lstrip("*")
    jobs = [(t, s) for t in C.TASKS for s in ((C.SYN_B if t.startswith("B_") else C.SYN_D) if C.TASKS[t][1] else C.REAL)]
    t0 = time.time()
    with ProcessPoolExecutor(16) as ex: df = pd.DataFrame(list(ex.map(run, jobs, chunksize=1)))
    df.to_csv(os.path.join(HERE, "BENCH03_V042_RESULTS.csv"), index=False)
    print(df.status.value_counts().to_string(), f"{time.time()-t0:.0f}s")
