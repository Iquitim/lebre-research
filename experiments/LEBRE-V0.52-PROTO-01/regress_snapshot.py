"""regress_snapshot.py — exact-output regression check for refactors (predictions, events, FP) on fixed dev inputs."""
import hashlib, sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run_dev as R
from lebre_v052 import LebreV052

def fingerprint():
    out = {}
    for task, seed in [("T1", 9101), ("B2", 9102), ("B3", 9103), ("N1", 9104)]:
        d = R.synth(task, seed); X, y = d["X"], d["y"]
        m = LebreV052(d=X.shape[1])
        p = np.array([m.step(X[t], float(y[t])) for t in range(len(y))])
        out[f"{task}:{seed}"] = {"pred_sha": hashlib.sha256(np.round(p, 10).tobytes()).hexdigest()[:16],
                                 "events": str(m.events)[:0] + hashlib.sha256(str(m.events).encode()).hexdigest()[:16],
                                 "fp": round(m.fp_total() / len(y), 6), "structure": str(m.structure())}
    return out

if __name__ == "__main__":
    f = fingerprint()
    path = os.path.join(HERE, "REGRESS_BASELINE.json")
    if sys.argv[1:] == ["save"]:
        json.dump(f, open(path, "w"), indent=1); print("saved"); print(json.dumps(f, indent=1))
    else:
        base = json.load(open(path))
        ok = all(base[k] == f[k] for k in base)
        for k in base:
            if base[k] != f[k]: print("DIFF", k, base[k], f[k])
        print("IDENTICAL" if ok else "CHANGED")
