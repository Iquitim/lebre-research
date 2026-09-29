"""analyze_bench04.py — primary K-a..K-e and secondary S1..S8 of PREREG_BENCH04.md."""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OBJ = "LEBRE_V042"
CLASSIC = ["IPNLMS", "CTRL_ARX_NLMS", "C2_NLMS", "C3_RLS", "CTRL_PERSISTENCE", "CTRL_SEASONAL_NAIVE"]
MODERN_LIN = ["HOLT_WINTERS", "DLINEAR_ONLINE", "NLINEAR_ONLINE"]
FM = ["CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]
SL = ["LEBRE_V042_SL", "IPNLMS_SL"]

on = pd.read_csv(os.path.join(HERE, "BENCH04_RESULTS.csv"))
fm_path = os.path.join(HERE, "BENCH04_CHRONOS_RESULTS.csv")
fm = pd.read_csv(fm_path) if os.path.exists(fm_path) else pd.DataFrame(columns=on.columns)
df = pd.concat([on, fm], ignore_index=True)
df.loc[df.status != "SUCCESS", "nmse"] = np.inf
MED = df.groupby(["task_id", "model_id"]).nmse.median().unstack()


def evaluate(tasks):
    med = MED.loc[tasks]
    rk_models = [c for c in med.columns if c not in SL]
    r = med[OBJ]; pers = med["CTRL_PERSISTENCE"]
    bc = med[[c for c in CLASSIC if c in med]].min(axis=1)
    bc_ext = med[[c for c in CLASSIC + MODERN_LIN if c in med]].min(axis=1)
    rank = med[rk_models].rank(axis=1, method="min")
    sub = df[(df.model_id == OBJ) & df.task_id.isin(tasks)]
    cov = sub.groupby("task_id").coverage.median()
    K = {"K-a": float((r < pers).mean()), "K-b": float((r <= 1.25 * bc).mean()), "K-c": bool((sub.status == "SUCCESS").all()),
         "K-d": float((r <= 1.25 * med["LEBRE_V032"]).mean()), "K-e": float(cov.between(0.85, 0.95).mean())}
    p = [K["K-a"] >= .70, K["K-b"] >= .60, K["K-c"], K["K-d"] >= .90, K["K-e"] >= .80]
    K["passes"] = int(sum(p))
    K["decision"] = ("COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE" if all(p) else
                     "PARTIALLY_COMPETITIVE" if sum(p) >= 3 else "NOT_COMPETITIVE")
    fmc = [c for c in FM if c in med]
    bfm = med[fmc].min(axis=1) if fmc else pd.Series(np.nan, index=med.index)
    bml = med[[c for c in MODERN_LIN if c in med]].min(axis=1)
    geo = lambda a, b: float(np.exp(np.log(a / b).replace([np.inf, -np.inf], np.nan).mean()))
    K.update({"n_tasks": len(tasks), "n_models_ranked": len(rk_models),
              "mean_rank": float(rank[OBJ].mean()), "position": int(rank.mean().rank(method="min")[OBJ]),
              "S3_Kb_extended": float((r <= 1.25 * bc_ext).mean()),
              "S2_frac_le_1.25_best_chronos": float((r <= 1.25 * bfm).mean()),
              "S2_geo_ratio_vs_best_chronos": geo(r, bfm),
              "S2_frac_le_1.25_best_modern_linear": float((r <= 1.25 * bml).mean()),
              "S2_geo_ratio_vs_best_modern_linear": geo(r, bml),
              "geo_ratio_vs_best_classic": geo(r, bc), "geo_ratio_vs_v032": geo(r, med["LEBRE_V032"]),
              "beats_best_classic": int((r < bc).sum())})
    top = rank.mean().sort_values().round(2)
    tab = pd.DataFrame({"LEBRE_V042": r, "LEBRE_V032": med["LEBRE_V032"], "persistence": pers, "best_classic": bc,
                        "which_classic": med[[c for c in CLASSIC if c in med]].idxmin(axis=1),
                        "best_modern_linear": bml, "best_chronos": bfm,
                        "which_chronos": med[fmc].idxmin(axis=1) if fmc else None,
                        "best_overall": med[rk_models].min(axis=1), "which_best": med[rk_models].idxmin(axis=1),
                        "rank_v042": rank[OBJ], "coverage_v042": cov})
    for c in SL:
        if c in med:
            tab[c] = med[c]
    return K, top, tab


ALL = sorted(MED.index)
BRT = [t for t in ALL if t.startswith("BR")]
K_all, top_all, tab_all = evaluate(ALL)
K_br, top_br, tab_br = evaluate(BRT)

# S5 intervals, S6 cost, S8 explanation
iv = df[df.model_id.isin([OBJ, "LEBRE_V042_SL"] + FM)].groupby(["task_id", "model_id"])[["coverage", "interval_width_rel"]].median()
cost = df.groupby("model_id").agg(mean_fp=("mean_flops", "mean"), memory_bytes=("memory_bytes", "median"),
                                  ms_per_step=("ms_per_step", "median"),
                                  divergences=("status", lambda s: int((s != "SUCCESS").sum()))).sort_values("ms_per_step")
expl = df[df.model_id == OBJ].groupby("task_id")[["n_active_final", "n_struct_final", "n_events"]].median()

out = {"ALL": K_all, "BR": K_br, "top_all": top_all.head(15).to_dict(), "top_br": top_br.head(10).to_dict()}
json.dump(out, open(os.path.join(HERE, "BENCH04_DECISION.json"), "w"), indent=2)
tab_all.to_csv(os.path.join(HERE, "BENCH04_BY_TASK.csv")); MED.to_csv(os.path.join(HERE, "BENCH04_NMSE_MATRIX.csv"))
iv.to_csv(os.path.join(HERE, "BENCH04_INTERVALS.csv")); cost.to_csv(os.path.join(HERE, "BENCH04_COST.csv"))
expl.to_csv(os.path.join(HERE, "BENCH04_EXPLANATION.csv"))
top_all.to_csv(os.path.join(HERE, "BENCH04_RANKING.csv"), header=["mean_rank"])
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
print(json.dumps({"ALL": K_all, "BR": K_br}, indent=1))
print(top_all.to_string())
print(tab_all.round(4).to_string())
print(iv.round(3).unstack().to_string())
print(cost.round(3).to_string())
print(expl.to_string())
