#!/usr/bin/env python3
"""analyze_external_review.py — endpoints of Parts II and III (PREREG_V03_REVIEW_BENCHMARKS.md)."""
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(HERE, "EXTERNAL_REVIEW_RESULTS.csv"))
df.loc[df.status != "SUCCESS", "nmse"] = np.inf
FOCUS = "LEBRE_V031"


def pareto(g):
    pts = g[["nmse_median", "flops"]].values
    out = []
    for i, (a, b) in enumerate(pts):
        out.append(not any((c <= a and d <= b) and (c < a or d < b) for j, (c, d) in enumerate(pts) if j != i))
    return pd.Series(out, index=g.index)


def wil(a, b):
    d = (a - b.reindex(a.index)).replace([np.inf, -np.inf], np.nan)
    # a finite value beats a divergence: count explicitly
    wins = int(((a < b.reindex(a.index)) | (np.isfinite(a) & ~np.isfinite(b.reindex(a.index)))).sum())
    losses = int(((a > b.reindex(a.index)) | (~np.isfinite(a) & np.isfinite(b.reindex(a.index)))).sum())
    d = d.dropna()
    p = stats.wilcoxon(d).pvalue if len(d) >= 5 and not np.allclose(d, 0) else np.nan
    return wins, losses, p


agg = df.groupby(["part", "task_id", "model_id"]).agg(
    nmse_median=("nmse", "median"), flops=("mean_flops", "mean"), mem=("memory_bytes", "mean"),
    fails=("status", lambda s: int((s != "SUCCESS").sum())), n=("status", "size"))
agg["rank"] = agg.groupby(["part", "task_id"]).nmse_median.rank(method="min")
agg["pareto"] = agg.groupby(["part", "task_id"], group_keys=False).apply(pareto)
agg.to_csv(os.path.join(HERE, "EXTERNAL_TASK_MODEL_SUMMARY.csv"))

rows = []
for (part, task), g in agg.groupby(level=["part", "task_id"]):
    g = g.droplevel([0, 1])
    base = g.drop(["LEBRE_V03", "LEBRE_V031", "CTRL_ARX_NLMS", "CTRL_PERSISTENCE"])
    best = base.nmse_median.idxmin()
    sel = df[df.task_id == task]
    me = sel[sel.model_id == FOCUS].set_index("seed").nmse
    r = {"part": part, "task_id": task, "v031_nmse": g.loc[FOCUS, "nmse_median"], "v031_flops": g.loc[FOCUS, "flops"],
         "v031_mem": g.loc[FOCUS, "mem"], "v031_rank": int(g.loc[FOCUS, "rank"]), "n_models": len(g),
         "v031_pareto": bool(g.loc[FOCUS, "pareto"]),
         "v03_nmse": g.loc["LEBRE_V03", "nmse_median"], "arx_nmse": g.loc["CTRL_ARX_NLMS", "nmse_median"],
         "trackB_nmse": g.loc["Track_B", "nmse_median"], "best_calibrated": best,
         "best_calibrated_nmse": base.loc[best, "nmse_median"], "best_calibrated_flops": base.loc[best, "flops"]}
    for tag, mid in (("trackB", "Track_B"), ("arx", "CTRL_ARX_NLMS"), ("best", best)):
        w, l, p = wil(me, sel[sel.model_id == mid].set_index("seed").nmse)
        r[f"vs_{tag}_wins"], r[f"vs_{tag}_losses"], r[f"vs_{tag}_p"] = w, l, p
    rows.append(r)
res = pd.DataFrame(rows)
res.to_csv(os.path.join(HERE, "EXTERNAL_V031_VS_FIELD.csv"), index=False)
pd.set_option("display.width", 280)
print(res.round(4).to_string(index=False))

for part, g in df.groupby("part"):
    ok = g[np.isfinite(g.nmse)]
    ov = ok.groupby(["model_id", "task_id"]).nmse.mean().groupby("model_id").mean().to_frame("nmse_mean_of_task_means")
    a = agg.xs(part, level="part")
    ov["mean_rank"] = a.groupby("model_id")["rank"].mean()
    ov["tasks_on_pareto"] = a.groupby("model_id")["pareto"].sum()
    ov["flops"] = a.groupby("model_id").flops.mean()
    ov["mem"] = a.groupby("model_id").mem.mean()
    ov["failed_runs"] = g.groupby("model_id").status.apply(lambda s: int((s != "SUCCESS").sum()))
    ov["tasks_le100flops_le1KB"] = a.groupby("model_id").apply(lambda x: int(((x.flops <= 100) & (x.mem <= 1024)).sum()))
    ov = ov.sort_values("mean_rank")
    ov.to_csv(os.path.join(HERE, f"EXTERNAL_OVERALL_PART{part}.csv"))
    print(f"==== PART {part}")
    print(ov.round(4).to_string())
