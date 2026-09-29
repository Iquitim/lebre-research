"""pts_unit.py — dev-only: score the input-level v0.52 on the SAME 1000 points and mask as COMP_DEV_1000PTS (Chronos protocol).
The mask is rebuilt from the saved online predictions and checked against the stored n_points; tasks whose n differs are flagged."""
import os, sys
import numpy as np
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import data_v052 as D, chronos_dev as CH  # noqa: E402
TAG = sys.argv[1] if len(sys.argv) > 1 else "UNIT"
P = pd.read_csv(os.path.join(HERE, "COMP_DEV_1000PTS.csv")); U = np.load(os.path.join(HERE, f"REAL_{TAG}_PREDS.npz"))
comp = np.load(os.path.join(HERE, "COMP_DEV_PREDS.npz")); rows = []
for t in D.dev_tasks():
    y = D.load(t)["y"]; idx = CH.points(y); yt = y[idx]
    ok = np.ones(len(idx), bool)
    for k in comp.files:
        if k.split("|")[0] == t and np.isfinite(comp[k][idx]).mean() > 0.95:
            ok &= np.isfinite(comp[k][idx])
    u = U[t][idx]; ok &= np.isfinite(u)
    n_ref = int(P[P.task == t].n_points.iloc[0])
    v052 = comp[f"{t}|v052"][idx]; var = float(np.var(yt[ok]))
    rows.append({"task": t, "model": f"v052_{TAG}", "nmse": float(np.mean((yt[ok] - u[ok]) ** 2) / var), "n_points": int(ok.sum()), "n_ref": n_ref,
                 "v052_check": float(np.mean((yt[ok] - v052[ok]) ** 2) / var)})
R = pd.DataFrame(rows)
chk = R.merge(P[P.model == "v052"][["task", "nmse"]].rename(columns={"nmse": "v052_stored"}), on="task")
print("mask check: max |v052 recomputed - stored| =", float((chk.v052_check - chk.v052_stored).abs().max()), " n mismatches:", int((R.n_points != R.n_ref).sum()))
A = pd.concat([P, R[["task", "model", "nmse", "n_points"]]]); A.to_csv(os.path.join(HERE, f"COMP_DEV_1000PTS_{TAG}.csv"), index=False)
p = A.pivot_table(index="task", columns="model", values="nmse")
cols = [f"v052_{TAG}", "CHRONOS2_COV", "v052", "CHRONOS2", "ARX_NLMS", "AIRLINE_X"]
for grp in ("ons", "camels", "bdg2", ""):
    q = p[p.index.str.startswith(grp)]
    print(grp or "ALL", {m: round(float(np.exp(np.log(q[m] / q["NLINEAR_ONLINE"]).mean())), 3) for m in cols if m in q.columns})
print(f"v052_{TAG} beats CHRONOS2_COV in", int((p[f"v052_{TAG}"] < p.CHRONOS2_COV).sum()), "of", len(p), "tasks")
