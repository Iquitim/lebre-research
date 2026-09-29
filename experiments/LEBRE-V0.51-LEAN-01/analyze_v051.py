"""analyze_v051.py — decision of PREREG_V051.md."""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
V5 = os.path.join(HERE, "..", "LEBRE-V0.46-STABLE-COMPETITIVE-01")
B04 = os.path.join(HERE, "..", "LEBRE-V0.4-EXTERNAL-BENCH-04")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
FM = ["CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]
ML = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS"]
geo = lambda a, b: float(np.exp(np.log(a / b).mean()))
R = {}


def table(df):
    df = df.copy(); df.loc[df.status != "SUCCESS", "nmse"] = np.inf
    return df.groupby(["task_id", "model_id"]).nmse.median().unstack()


# ---------------- part 1 internal
d = pd.read_csv(os.path.join(HERE, "INTERNAL_V051_RESULTS.csv"))
sn = d.groupby(["seed", "arm"]).nmse.mean().unstack(); diff = sn.V051 - sn.V045
up = float(diff.mean() + stats.t.ppf(.95, len(diff) - 1) * diff.std(ddof=1) / np.sqrt(len(diff)))
v = d[d.arm == "V051"]
cost_int = v.groupby("task_id").agg(fp=("fp", "mean"), peak=("fp_peak", "max"))
sub = d[d.task_id != "I10_Redundant_Temporal_Structure"]
R["part1"] = {"I-1_upper95": up, "I-1": up < 0.010, "I-2_cov": float(v.coverage.mean()), "I-2": bool(0.88 <= v.coverage.mean() <= 0.92),
              "I-3_faith": float(v.faith_rel.max()), "I-3": bool(v.faith_rel.max() <= 1e-9),
              "nmse": sn.mean().round(4).to_dict(), "fp_mean_by_arm": d.groupby("arm").fp.mean().round(1).to_dict(),
              "fp_peak_by_arm": d.groupby("arm").fp_peak.max().round(0).to_dict(),
              "struct_exact": (sub.groupby("arm").struct_exact.sum() / sub.groupby("arm").struct_checks.sum()).round(4).to_dict(),
              "B_internal_max_mean_fp": float(cost_int.fp.max()), "B_internal_max_peak": float(cost_int.peak.max())}
print("PART 1\n" + d.pivot_table(index="task_id", columns="arm", values="nmse").round(4).to_string()); print(cost_int.round(1).to_string())

# ---------------- part 2 held-out
h = pd.concat([pd.read_csv(os.path.join(HERE, "HELDOUT_V051_RESULTS.csv")), pd.read_csv(os.path.join(HERE, "HELDOUT_V051_CHRONOS_RESULTS.csv"))],
              ignore_index=True)
mh = table(h); r = mh.LEBRE_V051
o = pd.read_csv(os.path.join(HERE, "HELDOUT_V051_OFFSETS.csv")); g = o.groupby(["task_id", "arm"]).nmse
ins = (g.max() / g.min()).unstack()
vh = h[h.model_id == "LEBRE_V051"]
cov = vh.groupby("task_id").coverage.median()
cost_h = vh.groupby("task_id").agg(fp=("mean_flops", "mean"), peak=("peak_flops", "max"), d=("D", "first"))
rank = mh.rank(axis=1, method="min")
P = {"C1_geo_vs_NLinear": geo(r, mh.NLINEAR_ONLINE), "C2_geo_vs_best_modern_linear": geo(r, mh[ML].min(axis=1)),
     "C4_geo_vs_V05": geo(r, mh.LEBRE_V05), "C3_geo_vs_best_chronos": geo(r, mh[[c for c in FM if c in mh]].min(axis=1)),
     "S1_median": float(ins.V051.median()), "S1_max": float(ins.V051.max()), "S1_all_arms_max": ins.max().round(3).to_dict(),
     "S2_frac": float(cov.between(0.85, 0.95).mean()), "K-c": bool((vh.status == "SUCCESS").all()), "faith_max": float(vh.faith_rel.max()),
     "B_heldout_max_mean_fp": float(cost_h.fp.max()), "B_heldout_max_peak": float(cost_h.peak.max()),
     "geo_vs_V045": geo(r, mh.LEBRE_V045), "geo_vs_persistence": geo(r, mh.CTRL_PERSISTENCE),
     "position": int(rank.mean().rank(method="min").LEBRE_V051), "n_models": int(mh.shape[1]),
     "ranking": rank.mean().sort_values().round(2).to_dict()}
P["C1"] = P["C1_geo_vs_NLinear"] <= 1.10; P["C2"] = P["C2_geo_vs_best_modern_linear"] <= 1.15; P["C4"] = P["C4_geo_vs_V05"] <= 1.10
P["C3_meta"] = P["C3_geo_vs_best_chronos"] <= 1.50; P["S1"] = P["S1_median"] <= 1.10 and P["S1_max"] <= 1.50; P["S2"] = P["S2_frac"] >= 0.80
R["part2"] = P
B1 = R["part1"]["B_internal_max_mean_fp"] <= 150 and P["B_heldout_max_mean_fp"] <= 150
B2 = R["part1"]["B_internal_max_peak"] <= 500 and P["B_heldout_max_peak"] <= 500
R["B1"], R["B2"] = B1, B2
cst = h.groupby("model_id").agg(fp=("mean_flops", "mean"), peak=("peak_flops", "max"), mem=("memory_bytes", "median"), ms=("ms_per_step", "median")).round(2)
print("PART 2\n" + mh.round(4).to_string()); print(cst.to_string()); print(cost_h.round(1).to_string())
print("instabilidade\n" + ins.round(3).to_string()); print("cobertura\n" + cov.round(3).to_string())

# ---------------- part 3 (reported)
h5 = pd.concat([pd.read_csv(os.path.join(V5, "HELDOUT_V05_RESULTS.csv")), pd.read_csv(os.path.join(V5, "HELDOUT_CHRONOS_RESULTS.csv")),
                pd.read_csv(os.path.join(HERE, "HELDOUT05_V051_RESULTS.csv"))], ignore_index=True)
m5 = table(h5); rk5 = m5.rank(axis=1, method="min")
b = pd.concat([pd.read_csv(os.path.join(B04, "BENCH04_RESULTS.csv")), pd.read_csv(os.path.join(B04, "BENCH04_CHRONOS_RESULTS.csv")),
               pd.read_csv(os.path.join(V5, "BENCH04_V05_RESULTS.csv")), pd.read_csv(os.path.join(HERE, "BENCH04_V051_RESULTS.csv"))], ignore_index=True)
b = b[~b.model_id.isin(["LEBRE_V042_SL", "IPNLMS_SL", "LEBRE_V042"])]
mb = table(b); rkb = mb.rank(axis=1, method="min")
ob = pd.read_csv(os.path.join(HERE, "BENCH04_V051_OFFSETS.csv")); gb = ob.groupby("task_id").nmse
R["part3"] = {"heldout_v05": {"geo_vs_NLinear": geo(m5.LEBRE_V051, m5.NLINEAR_ONLINE), "geo_vs_V05": geo(m5.LEBRE_V051, m5.LEBRE_V05),
                              "geo_vs_best_chronos": geo(m5.LEBRE_V051, m5[[c for c in FM if c in m5]].min(axis=1)),
                              "position": int(rk5.mean().rank(method="min").LEBRE_V051), "n_models": int(m5.shape[1])},
              "bench04": {"geo_vs_NLinear": geo(mb.LEBRE_V051, mb.NLINEAR_ONLINE), "geo_vs_V05": geo(mb.LEBRE_V051, mb.LEBRE_V05),
                          "geo_vs_best_chronos": geo(mb.LEBRE_V051, mb[FM].min(axis=1)),
                          "position": int(rkb.mean().rank(method="min").LEBRE_V051), "n_models": int(mb.shape[1]),
                          "instab_max": float((gb.max() / gb.min()).max()), "mean_fp": float(b[b.model_id == "LEBRE_V051"].mean_flops.mean())}}
P1 = R["part1"]
R["PROMOTION"] = "PROMOVIDA_v0.51" if all([B1, B2, P1["I-1"], P1["I-2"], P1["I-3"], P["C1"], P["C2"], P["C4"], P["S1"], P["S2"], P["K-c"]]) else "NAO_PROMOVIDA"
json.dump(R, open(os.path.join(HERE, "V051_DECISION.json"), "w"), indent=2, default=str)
print(json.dumps(R, indent=1, default=str))
