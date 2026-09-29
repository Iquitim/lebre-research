"""analyze_v05.py — decision of PREREG_V05.md."""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
B04 = os.path.join(HERE, "..", "LEBRE-V0.4-EXTERNAL-BENCH-04")
pd.set_option("display.width", 240); pd.set_option("display.max_columns", 40)
FM = ["CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]
ML = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS"]
CLASSIC = ["IPNLMS", "CTRL_ARX_NLMS", "C2_NLMS", "C3_RLS", "CTRL_PERSISTENCE", "CTRL_SEASONAL_NAIVE"]
geo = lambda a, b: float(np.exp(np.log(a / b).mean()))
R = {}

# ---------------- part 1
d = pd.read_csv(os.path.join(HERE, "INTERNAL_V05_RESULTS.csv"))
sn = d.groupby(["seed", "arm"]).nmse.mean().unstack(); diff = sn.V05 - sn.V045
up = float(diff.mean() + stats.t.ppf(.95, len(diff) - 1) * diff.std(ddof=1) / np.sqrt(len(diff)))
v = d[d.arm == "V05"]; sub = d[d.task_id != "I10_Redundant_Temporal_Structure"]
st = (sub.groupby("arm").struct_exact.sum() / sub.groupby("arm").struct_checks.sum()).round(4).to_dict()
R["part1"] = {"I-1_upper95_V05-V045": up, "I-1": up < 0.010, "I-2_cov": float(v.coverage.mean()),
              "I-2": bool(0.88 <= v.coverage.mean() <= 0.92), "I-3_faith_max": float(v.faith_rel.max()), "I-3": bool(v.faith_rel.max() <= 1e-9),
              "nmse": sn.mean().round(4).to_dict(), "fp": d.groupby("arm").fp.mean().round(1).to_dict(), "struct_exact": st,
              "w_structural_final_mean": float(v.w_structural_final.mean())}
print("PART 1 por tarefa\n" + d.pivot_table(index="task_id", columns="arm", values="nmse").round(4).to_string())


# ---------------- part 2 held-out and part 3 BENCH-04
def table(df):
    df = df.copy(); df.loc[df.status != "SUCCESS", "nmse"] = np.inf
    return df.groupby(["task_id", "model_id"]).nmse.median().unstack()


def offsets(path):
    o = pd.read_csv(path); g = o.groupby(["task_id", "arm"]).nmse
    return (g.max() / g.min()).unstack(), g.median().unstack()


h = pd.concat([pd.read_csv(os.path.join(HERE, "HELDOUT_V05_RESULTS.csv")), pd.read_csv(os.path.join(HERE, "HELDOUT_CHRONOS_RESULTS.csv"))],
              ignore_index=True)
mh = table(h); r = mh.LEBRE_V05
ins, _ = offsets(os.path.join(HERE, "HELDOUT_V05_OFFSETS.csv"))
cov = h[h.model_id == "LEBRE_V05"].groupby("task_id").coverage.median()
rank = mh.rank(axis=1, method="min")
R["part2"] = {"C1_geo_vs_NLinear": geo(r, mh.NLINEAR_ONLINE), "C2_geo_vs_best_modern_linear": geo(r, mh[ML].min(axis=1)),
              "C3_geo_vs_best_chronos": geo(r, mh[[c for c in FM if c in mh]].min(axis=1)),
              "S1_instab_median": float(ins.V05.median()), "S1_instab_max": float(ins.V05.max()),
              "S1_other_arms_median": ins.median().round(3).to_dict(), "S1_other_arms_max": ins.max().round(3).to_dict(),
              "S2_frac_cov_ok": float(cov.between(0.85, 0.95).mean()), "K-c": bool((h[h.model_id == "LEBRE_V05"].status == "SUCCESS").all()),
              "faith_max": float(h[h.model_id == "LEBRE_V05"].faith_rel.max()),
              "geo_vs_V045": geo(r, mh.LEBRE_V045), "geo_vs_V032": geo(r, mh.LEBRE_V032), "geo_vs_persistence": geo(r, mh.CTRL_PERSISTENCE),
              "mean_rank": float(rank.LEBRE_V05.mean()), "position": int(rank.mean().rank(method="min").LEBRE_V05), "n_models": int(mh.shape[1]),
              "ranking": rank.mean().sort_values().round(2).to_dict()}
p = R["part2"]
p["C1"] = p["C1_geo_vs_NLinear"] <= 1.10; p["C2"] = p["C2_geo_vs_best_modern_linear"] <= 1.15; p["C3_meta"] = p["C3_geo_vs_best_chronos"] <= 1.50
p["S1"] = p["S1_instab_median"] <= 1.10 and p["S1_instab_max"] <= 1.50; p["S2"] = p["S2_frac_cov_ok"] >= 0.80
cost = h.groupby("model_id").agg(fp=("mean_flops", "mean"), ms=("ms_per_step", "median")).round(3)
print("PART 2 NMSE mediano\n" + mh.round(4).to_string()); print(cost.to_string())
print("instabilidade max/min\n" + ins.round(3).to_string()); print("cobertura V05\n" + cov.round(3).to_string())

b = pd.concat([pd.read_csv(os.path.join(B04, "BENCH04_RESULTS.csv")), pd.read_csv(os.path.join(B04, "BENCH04_CHRONOS_RESULTS.csv")),
               pd.read_csv(os.path.join(HERE, "..", "LEBRE-V0.45-ROBUST-GUARD-01", "BENCH04_V045_RESULTS.csv")),
               pd.read_csv(os.path.join(HERE, "BENCH04_V05_RESULTS.csv"))], ignore_index=True)
b = b[~b.model_id.isin(["LEBRE_V042_SL", "IPNLMS_SL", "LEBRE_V042"])]
mb = table(b); rb = mb.LEBRE_V05; rkb = mb.rank(axis=1, method="min")
insb, _ = offsets(os.path.join(HERE, "BENCH04_V05_OFFSETS.csv"))
covb = b[b.model_id == "LEBRE_V05"].groupby("task_id").coverage.median()
bc = mb[[c for c in CLASSIC if c in mb]].min(axis=1)
K = {"K-a": float((rb < mb.CTRL_PERSISTENCE).mean()), "K-b": float((rb <= 1.25 * bc).mean()),
     "K-c": bool((b[b.model_id == "LEBRE_V05"].status == "SUCCESS").all()), "K-d": float((rb <= 1.25 * mb.LEBRE_V032).mean()),
     "K-e": float(covb.between(0.85, 0.95).mean())}
R["part3"] = {**K, "C1_geo_vs_NLinear": geo(rb, mb.NLINEAR_ONLINE), "C2_geo_vs_best_modern_linear": geo(rb, mb[ML].min(axis=1)),
              "C3_geo_vs_best_chronos": geo(rb, mb[FM].min(axis=1)), "S1_instab_median": float(insb.V05.median()),
              "S1_instab_max": float(insb.V05.max()), "NLIN_instab_max": float(insb.NLIN.max()),
              "geo_vs_V045": geo(rb, mb.LEBRE_V045), "mean_rank": float(rkb.LEBRE_V05.mean()),
              "position": int(rkb.mean().rank(method="min").LEBRE_V05), "n_models": int(mb.shape[1]),
              "top10": rkb.mean().sort_values().head(10).round(2).to_dict()}
print("PART 3 BENCH-04\n" + mb[["LEBRE_V05", "LEBRE_V045", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS"] + FM].round(4).to_string())

P1, P2 = R["part1"], R["part2"]
R["PROMOTION"] = "PROMOVIDA_v0.5" if (P1["I-1"] and P1["I-2"] and P1["I-3"] and P2["C1"] and P2["C2"] and P2["S1"] and P2["S2"] and P2["K-c"]) \
    else "NAO_PROMOVIDA"
json.dump(R, open(os.path.join(HERE, "V05_DECISION.json"), "w"), indent=2, default=str)
print(json.dumps({k: v for k, v in R.items()}, indent=1, default=str))
