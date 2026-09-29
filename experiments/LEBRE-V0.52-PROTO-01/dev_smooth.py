"""dev_smooth.py — dev-only: discovery on smooth-input replicas y = 0.6 x_i(t-k) + e (real inputs; seeds 7101-7199),
for several configurations (cfg file). Reports discovery rate, false units (outside truth and its group), NMSE, FP."""
import os, sys
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, semi_synth as SS, semi_synth4 as S4  # noqa: E402
CASES = [(2, 9), (2, 16), (1, 12), (1, 25), (2, 5), (4, 20)]


def job(a):
    name, kw, (i, k), seed = a
    from lebre_v052h import LebreV052H
    X = SS.inputs(); Z = (X - X.mean(0)) / X.std(0); rng = np.random.default_rng(seed)
    y = 0.6 * np.r_[np.zeros(k), Z[:-k, i]] + rng.standard_normal(len(Z)); Xs = C._scaled_inputs(X)
    m = LebreV052H(d=X.shape[1], **kw)
    pred = np.array([m.step(Xs[t], float(y[t])) for t in range(len(y))]); ts = int(0.3 * len(y))
    grp = S4.groups(X)[i]; acc = {e[3][1] for e in m.events if e[1] == "accepted" and e[3] and e[3][0] == "in" and e[3][1] < X.shape[1]}
    fin = {u[1] for u in m.structure() if u[0] == "in"}
    first = min([e[0] for e in m.events if e[1] == "accepted" and e[3] and e[3][0] == "in" and e[3][1] in grp], default=None)
    return {"cfg": name, "case": f"x{i}-{k}", "seed": seed, "found": int(bool(fin & grp)), "false": len(acc - grp),
            "first": first, "nmse": float(np.mean((y[ts:] - pred[ts:]) ** 2) / np.var(y[ts:])), "fp": m.fp_total() / len(y)}


if __name__ == "__main__":
    CFGS = eval(open(sys.argv[1], encoding="utf-8").read()); out = sys.argv[2]
    jobs = [(n, kw, c, 7101 + 10 * j + s) for n, kw in CFGS.items() for j, c in enumerate(CASES) for s in range(2)]
    with ProcessPoolExecutor(15) as ex:
        R = pd.DataFrame(list(ex.map(job, jobs, chunksize=1)))
    R.to_csv(os.path.join(HERE, out), index=False)
    pd.set_option("display.width", 200)
    print(R.pivot_table(index="case", columns="cfg", values="found", aggfunc="mean"))
    print(R.groupby("cfg")[["found", "false", "nmse", "fp", "first"]].mean().round(3))
