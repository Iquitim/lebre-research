"""Pre-registered BENCH-03 criteria K-a..K-e for LEBRE_V04 and LEBRE_V041."""
import os, json, numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
df = pd.concat([pd.read_csv(os.path.join(HERE, "BENCH03_RESULTS.csv")), pd.read_csv(os.path.join(HERE, "BENCH03_V041_RESULTS.csv"))], ignore_index=True)
df.loc[df.status != "SUCCESS", "nmse"] = np.inf
med = df.groupby(["task_id", "model_id"]).nmse.median().unstack()
track = df.groupby("task_id").track.first()
CLASSIC = [c for c in ["IPNLMS", "CTRL_ARX_NLMS", "C2_NLMS", "C3_RLS", "CTRL_PERSISTENCE", "CTRL_SEASONAL_NAIVE"] if c in med]
best_classic = med[CLASSIC].min(axis=1); pers = med["CTRL_PERSISTENCE"]
others = med.drop(columns=["LEBRE_V04", "LEBRE_V041", "LEBRE_V032"])
rank = med.rank(axis=1, method="min")
out = {}
for v in ["LEBRE_V04", "LEBRE_V041"]:
    r = med[v]; cov = df[df.model_id == v].groupby("task_id").coverage.median()
    K = {"K-a skill>0 vs persistence": float((r < pers).mean()), "K-b <=1.25x best classic": float((r <= 1.25 * best_classic).mean()),
         "K-c zero divergences": bool((df[df.model_id == v].status == "SUCCESS").all()),
         "K-d <=1.25x v0.3.2": float((r <= 1.25 * med["LEBRE_V032"]).mean()),
         "K-e coverage in [0.85,0.95]": float(cov.between(0.85, 0.95).mean())}
    passes = [K["K-a skill>0 vs persistence"] >= 0.70, K["K-b <=1.25x best classic"] >= 0.60, K["K-c zero divergences"],
              K["K-d <=1.25x v0.3.2"] >= 0.90, K["K-e coverage in [0.85,0.95]"] >= 0.80]
    K["passes"] = int(sum(passes)); K["decision"] = ("COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE" if all(passes)
                                                     else "PARTIALLY_COMPETITIVE" if sum(passes) >= 3 else "NOT_COMPETITIVE")
    K["mean_rank"] = float(rank[v].mean()); K["global_position_by_mean_rank"] = int(rank.mean().rank(method="min")[v])
    K["beats_best_classic"] = int((r < best_classic).sum()); K["n_tasks"] = int(len(r))
    K["geo_ratio_vs_best_classic"] = float(np.exp(np.log(r / best_classic).replace([np.inf, -np.inf], np.nan).mean()))
    K["mean_fp"] = float(df[df.model_id == v].mean_flops.mean())
    out[v] = K
v032 = med["LEBRE_V032"]
out["LEBRE_V032_reference"] = {"K-a": float((v032 < pers).mean()), "K-b": float((v032 <= 1.25 * best_classic).mean()),
                               "mean_rank": float(rank["LEBRE_V032"].mean()), "divergences": int((df[df.model_id == "LEBRE_V032"].status != "SUCCESS").sum())}
json.dump(out, open(os.path.join(HERE, "BENCH03_DECISION.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
tab = pd.concat([track, med[["LEBRE_V041", "LEBRE_V04", "LEBRE_V032"]], best_classic.rename("best_classic"),
                 med[CLASSIC].idxmin(axis=1).rename("which_classic"), pers.rename("persistence"),
                 others.min(axis=1).rename("best_other"), others.idxmin(axis=1).rename("which_other"),
                 rank["LEBRE_V041"].rename("rank_v041"), med.notna().sum(axis=1).rename("n_models")], axis=1)
tab.to_csv(os.path.join(HERE, "BENCH03_BY_TASK.csv"))
pd.set_option("display.width", 250); print(tab.round(4).to_string())
mr = rank.mean().sort_values(); print(mr.head(12).round(2).to_string())
