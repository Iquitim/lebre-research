"""null_batch.py — false changes on targets with NO structure (real inputs): fraction of runs with any accepted change.
Usage: null_batch.py "<kwargs dict>" <first_seed> <n_per_kind> <out.csv>   (dev: seeds 7001+; measurement #6: final6.py)."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, semi_synth6 as S6  # noqa: E402


def job(a):
    kind, seed, kw = a
    from lebre_v052h import LebreV052H
    X = S6.inputs(); y = S6.generate(kind, seed, X); Xs = C._scaled_inputs(X)
    m = LebreV052H(d=X.shape[1], **kw)
    for t in range(len(y)):
        m.step(Xs[t], float(y[t]))
    acc = [(e[0], e[2], e[3]) for e in m.events if e[1] == "accepted"]
    return {"kind": kind, "seed": seed, "n_acc": len(acc), "accepted": str(acc), "fp": m.fp_total() / len(y)}


if __name__ == "__main__":
    kw = eval(sys.argv[1]); s0 = int(sys.argv[2]); n = int(sys.argv[3]); out = sys.argv[4]
    jobs = [("white", s0 + i, kw) for i in range(n)] + [("heavy", s0 + n + i, kw) for i in range(n)]
    with ProcessPoolExecutor(15) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    R.to_csv(os.path.join(HERE, out), index=False)
    print(R[R.n_acc > 0].to_string(index=False))
    print(f"runs with any accepted change: {(R.n_acc > 0).sum()} of {len(R)}  (white {(R[R.kind == 'white'].n_acc > 0).sum()}, heavy {(R[R.kind == 'heavy'].n_acc > 0).sum()})")
