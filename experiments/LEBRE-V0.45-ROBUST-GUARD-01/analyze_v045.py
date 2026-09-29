"""analyze_v045.py — decision of PREREG_V045.md."""
import json
import os

import numpy as np
import pandas as pd
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
B04 = os.path.join(ROOT, "experiments", "LEBRE-V0.4-EXTERNAL-BENCH-04")
V03 = os.path.join(ROOT, "experiments", "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01")
pd.set_option("display.width", 230)
R = {}

# ---------------- Part 1: internal
df = pd.read_csv(os.path.join(HERE, "INTERNAL_V045_RESULTS.csv"))
sn = df.groupby(["seed", "arm"]).nmse.mean().unstack()
sub = df[df.task_id != "I10_Redundant_Temporal_Structure"]
sx = (sub.groupby(["seed", "arm"]).struct_exact.sum() / sub.groupby(["seed", "arm"]).struct_checks.sum()).unstack()


def up(d):
    n = len(d); return float(d.mean() + stats.t.ppf(0.95, n - 1) * d.std(ddof=1) / np.sqrt(n))


def lo(d):
    n = len(d); return float(d.mean() - stats.t.ppf(0.95, n - 1) * d.std(ddof=1) / np.sqrt(n))


v = df[df.arm == "V045"]
G = {"G1": up(sn.V045 - sn.V032) < 0.010, "G2": float(v.fp.mean()) <= 100.0, "G3": lo(sx.V045 - sx.V032) > -0.02,
     "G4": up(sn.V045 - sn.V02_A0) < 0, "G5": 0.88 <= float(v.coverage.mean()) <= 0.92, "G6": float(v.faithfulness_gap.max()) <= 1e-9}
tk = df.groupby(["task_id", "arm"])[["nmse", "switch_latency", "i7_reactivation"]].mean()
lat = tk.switch_latency.unstack().dropna()
dnm = tk.nmse.unstack()
det = df.groupby("arm").detection_delay.mean()
SG = {"latency_I11_I14<=+50": bool(((lat.V045 - lat.V032) <= 50).all()),
      "dNMSE_task<=+0.010": bool(((dnm.V045 - dnm.V032) <= 0.010).all()),
      "I7_reactivation<=+25": bool((tk.i7_reactivation.unstack().dropna().eval("V045 - V032") <= 25).all()),
      "detection<=1.25x": bool(det.V045 <= 1.25 * det.V032),
      "NI_vs_V042_upper<=+0.005": up(sn.V045 - sn.V042) <= 0.005}
R["part1"] = {"gates": G, "safeguards": SG,
              "nmse": sn.mean().round(4).to_dict(), "fp_V045": float(v.fp.mean()), "coverage_V045": float(v.coverage.mean()),
              "struct": sx.mean().round(4).to_dict(), "detection_delay": det.round(1).to_dict(),
              "V045-V042 nmse upper95": up(sn.V045 - sn.V042), "V045-V032 nmse upper95": up(sn.V045 - sn.V032),
              "max_dNMSE_task_vs_V032": float((dnm.V045 - dnm.V032).max()),
              "max_latency_delta": float((lat.V045 - lat.V032).max())}
print("PART 1\n" + pd.DataFrame({"V032": dnm.V032, "V042": dnm.V042, "V045": dnm.V045}).round(4).to_string())
print(lat.round(0).to_string())

# ---------------- Part 2: properties
pt = pd.read_csv(os.path.join(V03, "PROPERTY_TESTS_v045.csv"))
t3 = pt[pt.test == "T3_type_I"]
ob = pd.read_csv(os.path.join(HERE, "OBSERVABILITY_TESTS_v045.csv"))
P = {"T3_runs_with_false_promotion": float((t3.false_promotions > 0).mean()),
     "T3_ok(<=0.05)": bool((t3.false_promotions > 0).mean() <= 0.05),
     "T9_max_gap": float(ob.T9_max_faithfulness_gap.max()), "T9_ok": bool(ob.T9_max_faithfulness_gap.max() <= 1e-9),
     "T10_mean_cov": float(ob.T10_coverage.mean()), "T10_ok": bool(0.88 <= ob.T10_coverage.mean() <= 0.92)}
t5 = pt[pt.test == "T5_kalman"]
if len(t5):
    P["T5_ratio_median"] = float((t5.mse_last3000 / t5.kalman_optimal_mse).median())
    P["T5_ratio_max"] = float((t5.mse_last3000 / t5.kalman_optimal_mse).max())
t4 = pt[pt.test == "T4_false_eviction"]
P["T4_false_evictions_total"] = int(t4.filter(like="evict").select_dtypes("number").sum().sum()) if len(t4) else None
R["part2"] = P

# ---------------- Part 3: BENCH-04 rerun
CLASSIC = ["IPNLMS", "CTRL_ARX_NLMS", "C2_NLMS", "C3_RLS", "CTRL_PERSISTENCE", "CTRL_SEASONAL_NAIVE"]
FM = ["CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]
b = pd.concat([pd.read_csv(os.path.join(B04, "BENCH04_RESULTS.csv")), pd.read_csv(os.path.join(B04, "BENCH04_CHRONOS_RESULTS.csv")),
               pd.read_csv(os.path.join(HERE, "BENCH04_V045_RESULTS.csv"))], ignore_index=True)
b = b[~b.model_id.isin(["LEBRE_V042_SL", "IPNLMS_SL"])]
b.loc[b.status != "SUCCESS", "nmse"] = np.inf
med = b.groupby(["task_id", "model_id"]).nmse.median().unstack()


def kcrit(obj, excl):
    m = med.drop(columns=excl); r = m[obj]; bc = m[[c for c in CLASSIC if c in m]].min(axis=1)
    cov = b[b.model_id == obj].groupby("task_id").coverage.median()
    K = {"K-a": float((r < m.CTRL_PERSISTENCE).mean()), "K-b": float((r <= 1.25 * bc).mean()),
         "K-c": bool((b[b.model_id == obj].status == "SUCCESS").all()), "K-d": float((r <= 1.25 * m.LEBRE_V032).mean()),
         "K-e": float(cov.between(0.85, 0.95).mean())}
    p = [K["K-a"] >= .7, K["K-b"] >= .6, K["K-c"], K["K-d"] >= .9, K["K-e"] >= .8]
    K["passes"] = int(sum(p))
    K["decision"] = "COMPETITIVE_WITH_OBSERVABILITY_ADVANTAGE" if all(p) else ("PARTIALLY_COMPETITIVE" if sum(p) >= 3 else "NOT_COMPETITIVE")
    rank = m.rank(axis=1, method="min")
    K["mean_rank"] = float(rank[obj].mean()); K["position"] = int(rank.mean().rank(method="min")[obj]); K["n_models"] = m.shape[1]
    K["geo_vs_v032"] = float(np.exp(np.log(r / m.LEBRE_V032).mean()))
    K["geo_vs_best_chronos"] = float(np.exp(np.log(r / m[FM].min(axis=1)).mean()))
    K["geo_vs_nlinear"] = float(np.exp(np.log(r / m.NLINEAR_ONLINE).mean()))
    return K


R["part3"] = {"V045": kcrit("LEBRE_V045", ["LEBRE_V042"]), "V042": kcrit("LEBRE_V042", ["LEBRE_V045"]),
              "geo_V045_vs_V042": float(np.exp(np.log(med.LEBRE_V045 / med.LEBRE_V042).mean()))}
print("PART 3\n" + med[["LEBRE_V045", "LEBRE_V042", "LEBRE_V032", "CTRL_PERSISTENCE", "NLINEAR_ONLINE", "CHRONOS2"]].round(4).to_string())

# ---------------- Parts 4-5: offsets
o = pd.read_csv(os.path.join(HERE, "OFFSETS_V045.csv"))
w = o[o.arm != "PERSISTENCE"].pivot_table(index=["task_id", "offset"], columns="arm", values="nmse")
pers = o[o.arm == "PERSISTENCE"].set_index("task_id").nmse


def geo(tasks, a, c):
    x = w.loc[w.index.get_level_values(0).isin(tasks)]
    return float(np.exp(np.log(x[a] / x[c]).mean()))


def instab(tasks, a):
    x = o[(o.arm == a) & o.task_id.isin(tasks)].groupby("task_id").nmse
    return float((x.quantile(.9) / x.quantile(.1)).median())


H = [t for t in o.task_id.unique() if t.startswith("H")]
BT = [t for t in o.task_id.unique() if t.startswith(("BR", "R"))]
medo = o.groupby(["task_id", "arm"]).nmse.median().unstack()
R["part4"] = {"H1_geo_V045_V042": geo(H, "V045", "V042"), "H1_ok": geo(H, "V045", "V042") <= 1.0,
              "H2_geo_V045_V032": geo(H, "V045", "V032"), "H2_ok": geo(H, "V045", "V032") <= 1.10,
              "H3_instab": {a: instab(H, a) for a in ("V032", "V042", "V045")},
              "bench04_offsets_geo_V045_V042": geo(BT, "V045", "V042"), "bench04_offsets_geo_V045_V032": geo(BT, "V045", "V032"),
              "bench04_offsets_instab": {a: instab(BT, a) for a in ("V032", "V042", "V045")}}
x3 = medo.loc["X3_MetroTraffic"]
R["part5"] = {"X3_median": x3.round(4).to_dict(), "X3_ok": bool(x3.V045 <= 1.10 * x3.V042)}
print("PARTS 4-5 (mediana sobre 10 offsets)\n" + medo.round(4).to_string())

ok = all(G.values()) and all(SG.values()) and P["T3_ok(<=0.05)"] and P["T9_ok"] and P["T10_ok"] and \
    R["part4"]["H1_ok"] and R["part4"]["H2_ok"] and R["part5"]["X3_ok"] and \
    R["part3"]["V045"]["passes"] >= R["part3"]["V042"]["passes"] and R["part3"]["V045"]["decision"] != "NOT_COMPETITIVE"
R["PROMOTION"] = "PROMOVIDA_v0.4.5" if ok else "NAO_PROMOVIDA"
json.dump(R, open(os.path.join(HERE, "V045_DECISION.json"), "w"), indent=2, default=str)
print(json.dumps(R, indent=1, default=str))
