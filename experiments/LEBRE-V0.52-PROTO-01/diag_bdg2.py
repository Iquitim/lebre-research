"""diag_bdg2.py — dev-only: where does the hierarchical v0.52 lose to the atomic one on a BDG2 task? Error by period and
the structural events of the (measured) hierarchical version."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import comp_dev as C, data_v052 as D  # noqa: E402
from lebre_v052h import LebreV052H  # noqa: E402
task = sys.argv[1] if len(sys.argv) > 1 else "bdg2:hotwater:Moose_education_Lori"
d = D.load(task); X, y, qu, s = d["X"], d["y"], d["quarantine"], d["season"]; Xs = C._scaled_inputs(X)
m = LebreV052H(d=X.shape[1], season=s, **eval(sys.argv[2] if len(sys.argv) > 2 else "{}")); ws = []
pred = np.empty(len(y))
for t in range(len(y)):
    pred[t] = m.step(Xs[t], float(y[t]) if np.isfinite(y[t]) else None, quarantine=bool(qu[t])); ws.append(m.wS)
comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); atom = comp[f"{task}|v052"]; nl = comp[f"{task}|NLINEAR_ONLINE"]
print(task, "T =", len(y), "season", s, "inputs", X.shape[1])
blocks = np.array_split(np.arange(int(0.3 * len(y)), len(y)), 10)
rows = []
for b in blocks:
    ok = np.isfinite(y[b]) & np.isfinite(pred[b]) & np.isfinite(atom[b]) & np.isfinite(nl[b])
    mse = lambda p: float(np.mean((y[b][ok] - p[b][ok]) ** 2))
    den = max(mse(nl), 1e-12)
    rows.append({"from": b[0], "to": b[-1], "hier_mse": mse(pred), "atom_mse": mse(atom), "nl_mse": mse(nl), "wS": float(np.mean(np.array(ws)[b])),
                 "y_sd": float(np.nanstd(y[b]))})
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("events:", [e[:5] for e in m.events if e[1] == "accepted"])
