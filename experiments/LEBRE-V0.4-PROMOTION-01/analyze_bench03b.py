"""Pre-registered K-a..K-e for LEBRE_V042 on BENCH-03b (held-out) and on BENCH-03 (semi-held-out, reported)."""
import os, json, sys, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
CLASSIC_ALL = ["IPNLMS", "CTRL_ARX_NLMS", "C2_NLMS", "C3_RLS", "CTRL_PERSISTENCE", "CTRL_SEASONAL_NAIVE"]

def evaluate(df, obj, label):
    df = df.copy(); df.loc[df.status != "SUCCESS", "nmse"] = np.inf
    med = df.groupby(["task_id", "model_id"]).nmse.median().unstack()
    CL = [c for c in CLASSIC_ALL if c in med]; bc = med[CL].min(axis=1); pers = med["CTRL_PERSISTENCE"]
    rank = med.rank(axis=1, method="min"); r = med[obj]
    cov = df[df.model_id == obj].groupby("task_id").coverage.median()
    K = {"K-a": float((r < pers).mean()), "K-b": float((r <= 1.25 * bc).mean()),
         "K-c": bool((df[df.model_id == obj].status == "SUCCESS").all()),
         "K-d": float((r <= 1.25 * med["LEBRE_V032"]).mean()), "K-e": float(cov.between(0.85, 0.95).mean())}
    p = [K["K-a"] >= .70, K["K-b"] >= .60, K["K-c"], K["K-d"] >= .90, K["K-e"] >= .80]
    K.update({"passes": int(sum(p)), "decision": "COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE" if all(p) else
              ("PARTIALLY_COMPETITIVE" if sum(p) >= 3 else "NOT_COMPETITIVE"),
              "mean_rank": float(rank[obj].mean()), "position": int(rank.mean().rank(method="min")[obj]), "n_models": int(med.shape[1]),
              "n_tasks": int(len(r)), "beats_best_classic": int((r < bc).sum()),
              "geo_ratio_vs_best_classic": float(np.exp(np.log(r / bc).replace([np.inf, -np.inf], np.nan).mean())),
              "geo_ratio_vs_v032": float(np.exp(np.log(r / med["LEBRE_V032"]).replace([np.inf, -np.inf], np.nan).mean())),
              "mean_fp": float(df[df.model_id == obj].mean_flops.mean()), "label": label})
    top = rank.mean().sort_values().head(10).round(2).to_dict()
    tab = pd.concat([df.groupby("task_id").track.first(), med[[obj, "LEBRE_V032"]], bc.rename("best_classic"),
                     med[CL].idxmin(axis=1).rename("which_classic"), pers.rename("persistence"),
                     rank[obj].rename("rank"), med.notna().sum(axis=1).rename("n_models")], axis=1)
    return K, top, tab

b = pd.read_csv(os.path.join(HERE, "BENCH03B_RESULTS.csv"))
K1, top1, tab1 = evaluate(b, "LEBRE_V042", "BENCH-03b held-out")
b3 = pd.concat([pd.read_csv(os.path.join(HERE, "BENCH03_RESULTS.csv")), pd.read_csv(os.path.join(HERE, "BENCH03_V042_RESULTS.csv"))])
b3 = b3[b3.model_id != "LEBRE_V04"]
K2, top2, tab2 = evaluate(b3, "LEBRE_V042", "BENCH-03 semi-held-out")
json.dump({"BENCH03B": K1, "BENCH03_semi": K2, "top_BENCH03B": top1, "top_BENCH03_semi": top2},
          open(os.path.join(HERE, "BENCH03B_DECISION.json"), "w"), indent=2)
tab1.to_csv(os.path.join(HERE, "BENCH03B_BY_TASK.csv")); tab2.to_csv(os.path.join(HERE, "BENCH03_V042_BY_TASK.csv"))
pd.set_option("display.width", 220)
print(json.dumps({"BENCH03B": K1, "BENCH03_semi": K2}, indent=1)); print(top1); print(tab1.round(4).to_string())
