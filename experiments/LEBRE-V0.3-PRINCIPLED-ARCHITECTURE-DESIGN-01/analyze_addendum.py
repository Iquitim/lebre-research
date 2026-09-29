#!/usr/bin/env python3
"""analyze_addendum.py — endpoints of Parts IV, V, VI (PREREG_ADDENDUM_V032.md)."""
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
pd.set_option("display.width", 260)


def pareto(g):
    pts = g[["nmse_median", "flops"]].values
    return pd.Series([not any((c <= a and d <= b) and (c < a or d < b) for j, (c, d) in enumerate(pts) if j != i)
                      for i, (a, b) in enumerate(pts)], index=g.index)


# ---------------- Part IV
ext = pd.read_csv(os.path.join(HERE, "ADDENDUM_EXTERNAL_RESULTS.csv"))
ext.loc[ext.status != "SUCCESS", "nmse"] = np.inf
p4 = ext[ext.part == "IV"]
agg = p4.groupby(["task_id", "model_id"]).agg(nmse_median=("nmse", "median"), flops=("mean_flops", "mean"),
                                              mem=("memory_bytes", "mean"))
agg["rank"] = agg.groupby("task_id").nmse_median.rank(method="min")
agg["pareto"] = agg.groupby("task_id", group_keys=False).apply(pareto)
agg.to_csv(os.path.join(HERE, "ADDENDUM_PART4_TASK_MODEL.csv"))
piv = agg.nmse_median.unstack("model_id")
cols = ["LEBRE_V032", "LEBRE_V031", "LEBRE_V03", "CTRL_ARX_NLMS", "Track_B", "S3_RSONN", "C4_FIXED_LAG_LINEAR",
        "S1_VARIABLE_TAP_LMS", "B1_RZA_LMS"]
print("==== PART IV median NMSE per task (permuted columns, seeds 161..190)")
print(piv[cols].round(4).to_string())
rows = []
for task, g in agg.groupby(level="task_id"):
    g = g.droplevel(0)
    base = g.drop([m for m in g.index if m.startswith("LEBRE") or m.startswith("CTRL")])
    best = base.nmse_median.idxmin()
    me = p4[(p4.task_id == task) & (p4.model_id == "LEBRE_V032")].set_index("seed").nmse
    r = {"task_id": task, "v032_rank": int(g.loc["LEBRE_V032", "rank"]), "v032_pareto": bool(g.loc["LEBRE_V032", "pareto"]),
         "best_calibrated": best}
    for tag, mid in (("trackB", "Track_B"), ("arx", "CTRL_ARX_NLMS"), ("best", best), ("v03", "LEBRE_V03")):
        o = p4[(p4.task_id == task) & (p4.model_id == mid)].set_index("seed").nmse.reindex(me.index)
        d = (me - o).replace([np.inf, -np.inf], np.nan).dropna()
        r[f"vs_{tag}_W"] = int(((me < o)).sum()); r[f"vs_{tag}_L"] = int(((me > o)).sum())
        r[f"vs_{tag}_p"] = stats.wilcoxon(d).pvalue if len(d) >= 5 and not np.allclose(d, 0) else np.nan
    rows.append(r)
t4 = pd.DataFrame(rows)
t4.to_csv(os.path.join(HERE, "ADDENDUM_PART4_V032_VS_FIELD.csv"), index=False)
print(t4.round(4).to_string(index=False))
ok = p4[np.isfinite(p4.nmse)]
ov = ok.groupby(["model_id", "task_id"]).nmse.mean().groupby("model_id").mean().to_frame("nmse_mean")
ov["mean_rank"] = agg.groupby("model_id")["rank"].mean()
ov["tasks_on_pareto"] = agg.groupby("model_id")["pareto"].sum()
ov["flops"] = agg.groupby("model_id").flops.mean()
ov["mem"] = agg.groupby("model_id").mem.mean()
ov["failed_runs"] = p4.groupby("model_id").status.apply(lambda s: int((s != "SUCCESS").sum()))
ov = ov.sort_values("mean_rank")
ov.to_csv(os.path.join(HERE, "ADDENDUM_PART4_OVERALL.csv"))
print(ov.round(4).to_string())

# ---------------- Part VI (semi-held-out)
p6 = ext[ext.part == "VI"].groupby("task_id").agg(nmse_median=("nmse", "median"), flops=("mean_flops", "mean"),
                                                  mem=("memory_bytes", "mean"))
old = pd.read_csv(os.path.join(HERE, "EXTERNAL_TASK_MODEL_SUMMARY.csv"))
old = old[old.part == "III"].pivot(index="task_id", columns="model_id", values="nmse_median")
p6 = p6.join(old[["LEBRE_V031", "LEBRE_V03", "CTRL_PERSISTENCE", "CTRL_ARX_NLMS", "Track_B", "C2_NLMS", "S3_RSONN"]])
p6.to_csv(os.path.join(HERE, "ADDENDUM_PART6_REAL.csv"))
print("==== PART VI (semi-held-out) real data, median NMSE; LEBRE_V032 = nmse_median")
print(p6.round(4).to_string())

# ---------------- Part V
idf = pd.read_csv(os.path.join(HERE, "ADDENDUM_INTERNAL_RESULTS.csv"))
seed_nmse = idf.groupby(["seed", "arm"]).nmse.mean().unstack()
sub = idf[idf.task_id != "I10_Redundant_Temporal_Structure"]
sx = (sub.groupby(["seed", "arm"]).struct_exact.sum() / sub.groupby(["seed", "arm"]).struct_checks.sum()).unstack()


def one_sided(d, alt):
    n = len(d); m = d.mean(); se = d.std(ddof=1) / np.sqrt(n); tq = stats.t.ppf(0.95, n - 1); t = m / se
    p = stats.t.cdf(t, n - 1) if alt == "less" else stats.t.sf(t, n - 1)
    return {"N": n, "mean": m, "sd": d.std(ddof=1), "one_sided_upper": m + tq * se, "one_sided_lower": m - tq * se,
            "p_one_sided": p, "favourable": int((d < 0).sum() if alt == "less" else (d > 0).sum())}


res = pd.DataFrame([{"contrast": n, **one_sided(d, a)} for n, d, a in [
    ("H1' V032-V02_A0 NMSE", seed_nmse.V032 - seed_nmse.V02_A0, "less"),
    ("H3' V032-CTRL_ARX NMSE", seed_nmse.V032 - seed_nmse.CTRL_ARX, "less"),
    ("H4' V032-V02_A0 struct", sx.V032 - sx.V02_A0, "greater"),
    ("S V032-V031 NMSE", seed_nmse.V032 - seed_nmse.V031, "less"),
    ("S V032-V031 struct", sx.V032 - sx.V031, "greater")]])
fam = res.iloc[:3].sort_values("p_one_sided"); run, holm = 0.0, []
for i, p in enumerate(fam.p_one_sided):
    run = max(run, min(1.0, (3 - i) * p)); holm.append(run)
fam["p_holm"] = holm
res = res.merge(fam[["contrast", "p_holm"]], on="contrast", how="left")
res.to_csv(os.path.join(HERE, "ADDENDUM_PART5_CONTRASTS.csv"), index=False)
arms = idf.groupby("arm").agg(nmse=("nmse", "mean"), fp=("fp", "mean"), fp_p99=("fp_p99", "mean"))
arms["struct_exact_rate"] = sub.groupby("arm").struct_exact.sum() / sub.groupby("arm").struct_checks.sum()
arms.to_csv(os.path.join(HERE, "ADDENDUM_PART5_ARMS.csv"))
print("==== PART V (internal, seeds 2146..2175)")
print(arms.round(4).to_string())
print(res.round(5).to_string(index=False))
tk = idf.pivot_table(index="task_id", columns="arm", values=["nmse", "switch_latency", "i7_reactivation", "fp"],
                     aggfunc="mean")
tk.to_csv(os.path.join(HERE, "ADDENDUM_PART5_TASKS.csv"))
print(tk["nmse"].round(4).to_string())
print(tk["fp"].round(1).to_string())
print(tk["switch_latency"].dropna(how="all").round(1).to_string())
