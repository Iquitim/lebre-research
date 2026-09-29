"""v052_data.py — every empirical number of the LEBRE v0.52 documents, read from the result files at build time
(the documents never cite local paths). Frozen folders are only read."""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = ROOT / "experiments"
PROTO, EXT, DOC = E / "LEBRE-V0.52-PROTO-01", E / "LEBRE-V0.52-EXT-01", E / "LEBRE-V0.52-DOC-01"
EXT2 = E / "LEBRE-V0.52-EXT-02"
H1, H2, H3 = E / "LEBRE-V0.52-HELDOUT-01", E / "LEBRE-V0.52-HELDOUT-02", E / "LEBRE-V0.52-HELDOUT-03"


def gm(v):
    v = np.asarray(v, float); v = v[np.isfinite(v) & (v > 0)]
    return float(np.exp(np.log(v).mean())) if len(v) else float("nan")


def kv_file(p):
    return dict(re.findall(r"^(\w+)=(.+)$", Path(p).read_text(encoding="utf-8", errors="replace"), re.M))


def paired(df, a, b, seed=8003, B=2000):
    """geometric-mean ratio a/b over series, stratified bootstrap CI, wins of a"""
    d = (np.log(df[a]) - np.log(df[b])); ok = d.notna() & np.isfinite(d); dd = d[ok]; g = df.group[ok].values
    rng = np.random.default_rng(seed); idx = {k: np.flatnonzero(g == k) for k in np.unique(g)}; bs = []
    for _ in range(B):
        s = np.concatenate([rng.choice(ix, len(ix)) for ix in idx.values()]); bs.append(np.exp(dd.values[s].mean()))
    return {"ratio": float(np.exp(dd.mean())), "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5)),
            "wins": int((dd < 0).sum()), "n": int(len(dd))}


def mcu_rows():
    """Renode runs of the float32 port (development: EXT-01; reserve 3: pre-registered)"""
    rows = []
    dev = [("ons_vg", "ONS", "dev"), ("camels", "CAMELS", "dev"), ("bdg2", "BDG2", "dev")]
    for tag, grp, src in dev:
        kv = kv_file(EXT / "mcu" / f"uart_{tag}.txt"); kv["TAG"] = tag; kv["GROUP"] = grp; kv["SRC"] = src; rows.append(kv)
    for i in range(1, 5):
        kv = kv_file(H3 / "mcu" / f"r3_{i}.txt"); kv["TAG"] = f"r3_{i}"; kv["GROUP"] = "CAMELS" if kv["TASK"].startswith("camels") else "BDG2"
        kv["SRC"] = "r3"; rows.append(kv)
    df = pd.DataFrame(rows)
    for c in ("T", "DX", "STRUCT_BYTES", "STEP_SUM", "STEP_MAX", "SCALER_SUM", "STEP_P50", "STEP_P99", "STEP_P999", "EVENTS", "N_OVER_20K", "N_OVER_20K_DECIDE"):
        df[c] = df[c].astype(int)
    df["NMSE"] = df.NMSE.astype(float); df["mean"] = df.STEP_SUM / df["T"]; df["scaler"] = df.SCALER_SUM / df["T"]
    sizes = {}
    for tag in df.TAG:
        f = (EXT / "mcu" / f"size_{tag}.txt")
        if f.exists():
            sizes[tag] = {k: int(v) for k, v in re.findall(r"^\.(\w+)\s+(\d+)", f.read_text(), re.M)}
    return df, sizes


def profile(tag):
    kv = Path(DOC / "mcu_profile" / f"profile_{tag}.txt").read_text(encoding="utf-8", errors="replace")
    blk = np.array([list(map(int, m.split(","))) for m in re.findall(r"^BLK=(.+)$", kv, re.M)])
    hist = np.array([list(map(int, m.split(","))) for m in re.findall(r"^HIST=(.+)$", kv, re.M)])
    big = np.array([list(map(int, m.split(","))) for m in re.findall(r"^BIG=(.+)$", kv, re.M)])
    T = int(re.search(r"^T=(\d+)", kv, re.M).group(1))
    return {"blk": blk, "hist": hist, "big": big, "T": T}


def load():
    N = {}
    # ---------------- reserve 3 (pre-registered, 60 series)
    N["r3_tab"] = pd.read_csv(H3 / "RESERVA3_TABLE.csv").set_index("model")
    R3 = pd.read_csv(H3 / "RESERVA3_FULLMASK.csv"); N["r3"] = R3
    P3 = pd.read_csv(H3 / "RESERVA3_1000PTS.csv"); N["r3p"] = P3
    N["r3_meta"] = pd.read_csv(H3 / "RESERVA3_META.csv")
    N["r3_cat"] = pd.read_csv(H3 / "RESERVA3_CATASTROPHIC.csv")
    others = ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "FITS", "ARX_NLMS", "LASSO_ONLINE", "V051", "SPARSETSF",
              "AIRLINE_X", "ARX_RLS_PLS"]
    N["r3_pair"] = {m: paired(R3, "V052_PY", m) for m in others}
    N["r3_pair_fm"] = {m: paired(P3, "V052_PY", m) for m in ["TTM_ZS", "TTM_FT_EXOG", "CHRONOS2_COV", "AIRLINE_X", "NLINEAR_ONLINE"]}
    N["r3p_gm"] = {m: {"ALL": gm(P3[m]), "camels": gm(P3[P3.group == "camels"][m]), "bdg2": gm(P3[P3.group == "bdg2"][m])}
                   for m in P3.columns if m not in ("task", "group") and not m.startswith("flops")}
    N["ttm_flops"] = (float(P3.flops_TTM_ZS.mean()), float(P3.flops_TTM_FT_EXOG.mean()))
    # ---------------- reserve 2 (pre-registered, 40 series)
    N["r2_tab"] = pd.read_csv(H2 / "RESERVA2_TABLE.csv").set_index("model")
    R2 = pd.read_csv(H2 / "RESERVA2_FULLMASK.csv"); N["r2"] = R2
    P2 = pd.read_csv(H2 / "RESERVA2_1000PTS.csv"); N["r2p"] = P2
    N["r2p_gm"] = {m: gm(P2[m]) for m in P2.columns if m not in ("task", "group")}
    N["r2_pair"] = {m: paired(R2, "V052_CORRIGIDA", m) for m in ["V052_CONGELADA", "AIRLINE_X", "DLINEAR_ONLINE"]}
    N["r2_pair_fm"] = paired(P2, "V052_CORRIGIDA", "CHRONOS2_COV")
    N["r2_meta"] = pd.read_csv(H2 / "RESERVA2_META.csv")
    # ---------------- reserve 1 (pre-registered, 125 series, version without the gap fix)
    N["r1_tab"] = pd.read_csv(H1 / "HELDOUT_TABLE_FULLMASK.csv").set_index("model")
    N["r1"] = pd.read_csv(H1 / "HELDOUT_FULLMASK.csv")
    N["r1_meta"] = pd.read_csv(H1 / "HELDOUT_META.csv")
    # ---------------- development
    N["dev_comp"] = pd.read_csv(EXT / "DEV_COMP_1000PTS.csv")
    N["dev_cost"] = pd.read_csv(EXT / "DEV_COMP_COST.csv")
    N["stress"] = pd.read_csv(PROTO / "STRESS_GAPS.csv")
    N["misadj"] = pd.read_csv(EXT / "MISADJ_VERIFY2.csv")
    N["equiv"] = pd.read_csv(EXT / "EQUIV_TEST.csv")
    N["null7"] = pd.read_csv(PROTO / "FINAL7_NULL.csv")
    N["null6"] = pd.read_csv(PROTO / "FINAL6_NULL.csv")
    N["synth7"] = pd.read_csv(PROTO / "FINAL7_SYNTH.csv")
    N["ex"] = json.load(open(DOC / "DOC_EXAMPLES.json", encoding="utf-8"))
    N["exA"] = dict(np.load(DOC / "DOC_EXAMPLE_A.npz")); N["exB"] = dict(np.load(DOC / "DOC_EXAMPLE_B.npz"))
    # ---------------- microcontroller
    N["mcu"], N["mcu_size"] = mcu_rows()
    N["prof"] = {t: profile(t) for t in ("ons_vg", "camels", "bdg2")}
    N["trace"] = pd.read_csv(DOC / "TRACE_BREAKDOWN.csv")
    # ---------------- post-freeze checks (EXT-02)
    N["fdr_sum"] = pd.read_csv(EXT2 / "FDR_SIM_SUMMARY.csv"); N["fdr_runs"] = pd.read_csv(EXT2 / "FDR_SIM_RUNS_FINAL.csv")
    N["abl"] = pd.read_csv(EXT2 / "ABL_ALLON_SUMMARY.csv").set_index("res")
    return N


if __name__ == "__main__":
    N = load()
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(N["r3_tab"].round(3)); print({k: {a: round(b, 3) if isinstance(b, float) else b for a, b in v.items()} for k, v in N["r3_pair"].items()})
    print({k: {a: round(b, 3) if isinstance(b, float) else b for a, b in v.items()} for k, v in N["r3_pair_fm"].items()})
    print({k: {a: round(b, 3) for a, b in v.items()} for k, v in N["r3p_gm"].items()})
    print(N["r2_tab"].round(3)); print(N["r2_pair"], N["r2_pair_fm"]); print({k: round(v, 3) for k, v in N["r2p_gm"].items()})
    print(N["r1_tab"].round(3))
    print(N["mcu"][["TAG", "TASK", "GROUP", "T", "DX", "mean", "STEP_P50", "STEP_P999", "STEP_MAX", "scaler", "NMSE", "EVENTS"]]); print(N["mcu_size"])
    print(N["stress"].groupby(["scen", "cfg"]).explode.sum()); print(N["misadj"].groupby("mu").accepted.apply(lambda s: (s != "[]").sum()))
    print(N["r3_meta"][["fp", "fp_max", "fp_p999", "n_acc", "coverage", "clipped"]].describe().round(3))
    print(N["r2_meta"].columns.tolist())
