#!/usr/bin/env python3
"""
compare_bench01.py — compares frozen LEBRE v0.3 (iter4) against all 15 sealed BENCH-01B models.
Reads sealed raw JSONs (read-only). Seed is the paired unit within a task.
"""
import glob
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "BENCH-01B", "raw")

rows = [json.load(open(p)) for p in glob.glob(os.path.join(RAW, "*.json"))]
base = pd.DataFrame(rows)[["task_id", "model_id", "seed", "status", "nmse", "mean_flops", "memory_bytes"]]
v3 = pd.read_csv(os.path.join(HERE, "BENCH01_LEBRE_V03_RESULTS.csv"))[base.columns]
df = pd.concat([base, v3], ignore_index=True)
V3 = "LEBRE_V03_FROZEN_ITER4"
df.loc[df.status != "SUCCESS", "nmse"] = np.inf

# per task summary: median-robust and mean
agg = df.groupby(["task_id", "model_id"]).agg(nmse_mean=("nmse", "mean"), nmse_median=("nmse", "median"),
                                              flops=("mean_flops", "mean"), mem=("memory_bytes", "mean"),
                                              fail=("status", lambda s: int((s != "SUCCESS").sum())))
agg["rank"] = agg.groupby("task_id").nmse_median.rank(method="min")
agg.to_csv(os.path.join(HERE, "BENCH01_TASK_MODEL_SUMMARY.csv"))

# Pareto front per task on (median NMSE, mean FLOPs)
def pareto(g):
    pts = g[["nmse_median", "flops"]].values
    dom = []
    for i, (a, b) in enumerate(pts):
        dom.append(any((c <= a and d <= b) and (c < a or d < b) for j, (c, d) in enumerate(pts) if j != i))
    return pd.Series(~np.array(dom), index=g.index)

agg["pareto"] = agg.groupby("task_id", group_keys=False).apply(pareto)

out = []
for task, g in agg.groupby(level="task_id"):
    g = g.droplevel(0)
    others = g.drop(V3)
    best_id = others.nmse_median.idxmin()
    tb = df[(df.task_id == task) & (df.model_id == "Track_B")].set_index("seed").nmse
    bb = df[(df.task_id == task) & (df.model_id == best_id)].set_index("seed").nmse
    me = df[(df.task_id == task) & (df.model_id == V3)].set_index("seed").nmse

    def wil(a, b):
        d = (a - b.reindex(a.index)).replace([np.inf, -np.inf], np.nan).dropna()
        if len(d) < 5 or np.allclose(d, 0):
            return np.nan, int((d < 0).sum()), int((d > 0).sum())
        return stats.wilcoxon(d).pvalue, int((d < 0).sum()), int((d > 0).sum())

    p_tb, w_tb, l_tb = wil(me, tb)
    p_bb, w_bb, l_bb = wil(me, bb)
    low = others[others.flops <= 100]
    best_low = low.nmse_median.idxmin() if len(low) else None
    out.append({
        "task_id": task, "D": None,
        "v03_nmse_median": g.loc[V3, "nmse_median"], "v03_flops": g.loc[V3, "flops"],
        "v03_rank_of_16": int(g.loc[V3, "rank"]), "v03_on_pareto": bool(g.loc[V3, "pareto"]),
        "trackB_nmse_median": g.loc["Track_B", "nmse_median"], "trackB_flops": g.loc["Track_B", "flops"],
        "v03_vs_trackB_wins": w_tb, "v03_vs_trackB_losses": l_tb, "v03_vs_trackB_wilcoxon_p": p_tb,
        "best_other_model": best_id, "best_other_nmse_median": others.loc[best_id, "nmse_median"],
        "best_other_flops": others.loc[best_id, "flops"],
        "v03_vs_best_wins": w_bb, "v03_vs_best_losses": l_bb, "v03_vs_best_wilcoxon_p": p_bb,
        "best_other_le100flops": best_low,
        "best_other_le100_nmse_median": low.nmse_median.min() if len(low) else np.nan,
    })
res = pd.DataFrame(out).drop(columns="D")
res.to_csv(os.path.join(HERE, "BENCH01_V03_VS_FIELD.csv"), index=False)
pd.set_option("display.width", 260)
print(res.round(4).to_string(index=False))

# overall (same aggregation as BENCH-01B: mean over tasks of per-task mean NMSE, successful runs)
ok = df[df.status == "SUCCESS"]
ov = ok.groupby(["model_id", "task_id"]).agg(nmse=("nmse", "mean"), flops=("mean_flops", "mean"),
                                             mem=("memory_bytes", "mean")).groupby("model_id").mean()
ov["mean_rank_median_nmse"] = agg.groupby("model_id")["rank"].mean()
ov["tasks_on_pareto"] = agg.groupby("model_id")["pareto"].sum()
ov["failed_runs"] = df.groupby("model_id").status.apply(lambda s: int((s != "SUCCESS").sum()))
ov = ov.sort_values("mean_rank_median_nmse")
ov.to_csv(os.path.join(HERE, "BENCH01_OVERALL_WITH_V03.csv"))
print(ov.round(4).to_string())
