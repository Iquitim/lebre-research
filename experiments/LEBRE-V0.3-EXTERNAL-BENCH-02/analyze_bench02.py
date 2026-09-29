#!/usr/bin/env python3
"""analyze_bench02.py — pre-registered endpoints E1..E5 and the decision rule of PREREG_BENCH02.md."""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
FOCUS = "LEBRE_V032"
df = pd.read_csv(os.path.join(HERE, "BENCH02_RESULTS.csv"))
df.loc[df.status != "SUCCESS", ["nmse", "mse"]] = np.inf

# skill vs persistence (same task, same seed, same test window)
pers = df[df.model_id == "CTRL_PERSISTENCE"].set_index(["task_id", "seed"]).mse
df["skill_vs_persistence"] = 1.0 - df.mse / df.set_index(["task_id", "seed"]).index.map(pers).values

agg = df.groupby(["track", "task_id", "model_id"]).agg(
    nmse_median=("nmse", "median"), skill_median=("skill_vs_persistence", "median"),
    flops=("mean_flops", "mean"), mem=("memory_bytes", "mean"),
    fails=("status", lambda s: int((s != "SUCCESS").sum())), n=("status", "size")).reset_index()
agg["rank"] = agg.groupby("task_id").nmse_median.rank(method="min")
agg["n_models"] = agg.groupby("task_id").model_id.transform("size")


def pareto(g):
    g = g[np.isfinite(g.flops)]
    pts = g[["nmse_median", "flops"]].values
    return pd.Series([not any((c <= a and d <= b) and (c < a or d < b) for j, (c, d) in enumerate(pts) if j != i)
                      for i, (a, b) in enumerate(pts)], index=g.index)


agg["pareto"] = False
for t, g in agg.groupby("task_id"):
    p = pareto(g)
    agg.loc[p.index, "pareto"] = p.values
agg.to_csv(os.path.join(HERE, "BENCH02_TASK_MODEL_SUMMARY.csv"), index=False)

rows = []
for (track, task), g in agg.groupby(["track", "task_id"]):
    g = g.set_index("model_id")
    others = g.drop([m for m in g.index if m.startswith("LEBRE")])
    best = others.nmse_median.idxmin()
    sel = df[df.task_id == task]
    me = sel[sel.model_id == FOCUS].set_index("seed").nmse
    r = {"track": track, "task_id": task, "n_models": len(g), "v032_nmse": g.loc[FOCUS, "nmse_median"],
         "v032_skill": g.loc[FOCUS, "skill_median"], "v032_rank": int(g.loc[FOCUS, "rank"]),
         "v032_pareto": bool(g.loc[FOCUS, "pareto"]), "v032_flops": g.loc[FOCUS, "flops"], "v032_mem": g.loc[FOCUS, "mem"],
         "best_other": best, "best_other_nmse": others.loc[best, "nmse_median"],
         "persistence_nmse": g.loc["CTRL_PERSISTENCE", "nmse_median"], "arx_nmse": g.loc["CTRL_ARX_NLMS", "nmse_median"],
         "trackB_nmse": g.loc["Track_B", "nmse_median"]}
    if "LEBRE_V032_NATIVE" in g.index:
        r["v032_native_nmse"] = g.loc["LEBRE_V032_NATIVE", "nmse_median"]
        r["v032_native_rank"] = int(g.loc["LEBRE_V032_NATIVE", "rank"])
    for tag, mid in (("best", best), ("trackB", "Track_B"), ("arx", "CTRL_ARX_NLMS")):
        o = sel[sel.model_id == mid].set_index("seed").nmse.reindex(me.index)
        r[f"vs_{tag}_W"] = int((me < o).sum()); r[f"vs_{tag}_L"] = int((me > o).sum())
        d = (me - o).replace([np.inf, -np.inf], np.nan).dropna()
        r[f"vs_{tag}_p"] = stats.wilcoxon(d).pvalue if len(d) >= 6 and not np.allclose(d, 0) else np.nan
    r["E3_pass"] = bool(r["v032_skill"] > 0 and r["v032_rank"] <= 3)
    rows.append(r)
res = pd.DataFrame(rows)
res.to_csv(os.path.join(HERE, "BENCH02_V032_BY_TASK.csv"), index=False)

# E1: mean rank per model (global and per track)
mr = agg.pivot_table(index="model_id", columns="track", values="rank", aggfunc="mean")
mr["ALL"] = agg.groupby("model_id")["rank"].mean()
mr["tasks_top3"] = agg[agg["rank"] <= 3].groupby("model_id").size().reindex(mr.index).fillna(0).astype(int)
mr["tasks_rank1"] = agg[agg["rank"] == 1].groupby("model_id").size().reindex(mr.index).fillna(0).astype(int)
mr["tasks_pareto"] = agg.groupby("model_id").pareto.sum()
mr["median_skill"] = agg.groupby("model_id").skill_median.median()
mr["mean_flops"] = agg.groupby("model_id").flops.mean()
mr["failed_runs"] = df.groupby("model_id").status.apply(lambda s: int((s != "SUCCESS").sum()))
mr = mr.sort_values("ALL")
mr["global_position"] = np.arange(1, len(mr) + 1)
mr.to_csv(os.path.join(HERE, "BENCH02_MEAN_RANK.csv"))

pos = int(mr.loc[FOCUS, "global_position"])
e3 = res.E3_pass.mean()
top3_tracks = [t for t in ["A", "B", "C", "D"] if t in mr.columns and mr[t].rank(method="min")[FOCUS] <= 3]
if pos <= 3 and e3 >= 0.5:
    decision = "JUSTIFIED_EXTERNALLY"
elif len(top3_tracks) >= 2:
    decision = "PARTIALLY_JUSTIFIED"
else:
    decision = "NOT_JUSTIFIED_EXTERNALLY"
summary = {"n_tasks": int(len(res)), "n_models_max": int(agg.groupby("task_id").size().max()),
           "n_runs": int(len(df)), "failed_runs_total": int((df.status != "SUCCESS").sum()),
           "v032_global_position": pos, "v032_mean_rank": float(mr.loc[FOCUS, "ALL"]),
           "E3_fraction": float(e3), "top3_tracks": top3_tracks, "decision": decision,
           "v032_tasks_rank1": int(mr.loc[FOCUS, "tasks_rank1"]), "v032_tasks_top3": int(mr.loc[FOCUS, "tasks_top3"]),
           "v032_tasks_pareto": int(mr.loc[FOCUS, "tasks_pareto"]),
           "v032_tasks_skill_pos": int((res.v032_skill > 0).sum()),
           "v032_tasks_le100flops_le1KB": int(((res.v032_flops <= 100) & (res.v032_mem <= 1024)).sum()),
           "track_positions": {t: int(mr[t].rank(method="min")[FOCUS]) for t in ["A", "B", "C", "D"] if t in mr.columns}}
json.dump(summary, open(os.path.join(HERE, "BENCH02_SUMMARY.json"), "w"), indent=2)
pd.set_option("display.width", 250)
print(json.dumps(summary, indent=2))
print(mr.round(3).to_string())
print(res[["track", "task_id", "v032_nmse", "v032_skill", "v032_rank", "n_models", "best_other", "best_other_nmse",
           "persistence_nmse", "arx_nmse", "vs_best_W", "vs_best_L"] + (["v032_native_nmse"] if "v032_native_nmse" in res else [])]
      .round(4).to_string(index=False))
