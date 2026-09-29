#!/usr/bin/env python3
"""analyze_dev.py <tag> — ablation summary for dev_eval_v04 output (internal + external-as-DEV)."""
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
B02 = os.path.join(HERE, "..", "LEBRE-V0.3-EXTERNAL-BENCH-02")
tag = sys.argv[1]
d = pd.read_csv(os.path.join(HERE, f"DEV_{tag}.csv"))
pd.set_option("display.width", 250)

# ---------------- internal
i = d[d.set == "internal"]
if len(i):
    s = i[i.task_id != "I10_Redundant_Temporal_Structure"]
    t = i.groupby("variant").agg(nmse=("nmse", "mean"), fp=("fp", "mean"))
    t["struct"] = s.groupby("variant").struct_exact.sum() / s.groupby("variant").struct_checks.sum()
    if "coverage" in i:
        t["coverage"] = i.groupby("variant").coverage.mean()
    seed = i.groupby(["seed", "variant"]).nmse.mean().unstack()
    t["dNMSE_vs_V032"] = (seed.sub(seed["V032"], axis=0)).mean()
    t["seeds_better"] = (seed.sub(seed["V032"], axis=0) < 0).sum()
    print("==== INTERNAL (I1-I14, DEV seeds 3301..3310)")
    print(t.round(4).to_string())

# ---------------- external (BENCH-02 tasks as DEV)
e = d[d.set == "external"].copy()
if len(e):
    e.loc[e.status != "SUCCESS", "nmse"] = np.inf
    ref = pd.read_csv(os.path.join(B02, "BENCH02_RESULTS.csv"))
    ref.loc[ref.status != "SUCCESS", "nmse"] = np.inf
    keys = e[["task_id", "seed"]].drop_duplicates()
    ref = ref.merge(keys, on=["task_id", "seed"])
    classic = ["IPNLMS", "CTRL_ARX_NLMS", "CTRL_PERSISTENCE"]
    rmed = ref.groupby(["task_id", "model_id"]).nmse.median().unstack()
    best_classic = rmed[classic].min(axis=1)
    best_any = rmed.drop(columns=["LEBRE_V032", "LEBRE_V032_NATIVE"], errors="ignore").min(axis=1)
    pers = rmed["CTRL_PERSISTENCE"]
    vmed = e.groupby(["task_id", "variant"]).nmse.median().unstack()
    track = e.groupby("task_id").track.first()
    rows = []
    for v in vmed.columns:
        r = vmed[v]
        rows.append({"variant": v,
                     "tasks": int(r.notna().sum()),
                     "skill>0 (beats persistence)": int((r < pers).sum()),
                     "within 1.25x best classic": int((r <= 1.25 * best_classic).sum()),
                     "beats best classic": int((r < best_classic).sum()),
                     "within 1.25x best of 23": int((r <= 1.25 * best_any).sum()),
                     "geo-mean ratio vs best classic": float(np.exp(np.log(r / best_classic).replace([np.inf, -np.inf], np.nan).mean())),
                     "fp": float(e[e.variant == v].fp.mean())})
    print("==== EXTERNAL (25 BENCH-02 tasks as DEV)")
    print(pd.DataFrame(rows).set_index("variant").round(3).to_string())
    per = pd.concat([vmed[["V032", "V04_ALL"] + [c for c in vmed.columns if c not in ("V032", "V04_ALL")]],
                     best_classic.rename("best_classic"), pers.rename("persistence"), track], axis=1)
    per.to_csv(os.path.join(HERE, f"DEV_{tag}_external_per_task.csv"))
    print(per[["track", "V032", "V04_ALL", "best_classic", "persistence"]].round(4).to_string())
