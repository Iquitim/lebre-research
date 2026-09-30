#!/usr/bin/env python3
"""build_assets.py — generates every number, table and data figure of the paper from the result files
(no number is typed by hand in main.tex). Outputs: generated/numbers.tex (macros), generated/tab_*.tex, figures/*.pdf.
Run from anywhere: python paper/build_assets.py"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "docs" / "architecture" / "pdf_source"))
from v052_data import load  # noqa: E402

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mt  # noqa: E402

GEN, FIG = HERE / "generated", HERE / "figures"
GEN.mkdir(exist_ok=True); FIG.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "font.size": 8, "axes.spines.top": False,
                     "axes.spines.right": False, "pdf.fonttype": 42, "axes.titlesize": 8.5, "legend.frameon": False,
                     "legend.fontsize": 7, "savefig.bbox": "tight", "savefig.pad_inches": 0.02})
C_LEB, C_BUD, C_REF, C_FM, C_RED = "#1f5fa8", "#9aa0a6", "#e0702a", "#1a9c6e", "#c0392b"
NAME = {"V052_PY": "LEBRE", "NLINEAR_ONLINE": "Online NLinear", "DLINEAR_ONLINE": "Online DLinear", "HOLT_WINTERS": "Online Holt-Winters",
        "FITS": "FITS", "SPARSETSF": "SparseTSF", "ARX_NLMS": "Dense ARX (NLMS)", "LASSO_ONLINE": "Online LASSO", "V051": "LEBRE v0.51",
        "AIRLINE_X": "SARIMAX with inputs", "ARX_RLS_PLS": "Least-squares ARX", "TTM_ZS": "TTM zero-shot",
        "TTM_FT_EXOG": "TTM fine-tuned (inputs)", "CHRONOS2_COV": "Chronos-2 (covariates)"}
ROLE = {"V052_PY": "leb", "AIRLINE_X": "ref", "ARX_RLS_PLS": "ref", "TTM_ZS": "fm", "TTM_FT_EXOG": "fm", "CHRONOS2_COV": "fm"}
COL = {"leb": C_LEB, "bud": C_BUD, "ref": C_REF, "fm": C_FM}
N = load()
f3 = lambda x: f"{x:.3f}"
f2 = lambda x: f"{x:.2f}"
ci = lambda s: [float(v) for v in s.strip("[]").split(",")]
macros = {}


def mac(name, val):
    macros[name] = val


# ------------------------------------------------------------------ numbers
t3, p3, pf, g1, meta3 = N["r3_tab"], N["r3_pair"], N["r3_pair_fm"], N["r3p_gm"], N["r3_meta"]
lo, hi = ci(t3.loc["V052_PY", "CI95"])
mac("rThreeAll", f3(t3.loc["V052_PY", "ALL"])); mac("rThreeLo", f3(lo)); mac("rThreeHi", f3(hi))
mac("rThreeSarimax", f3(t3.loc["AIRLINE_X", "ALL"]))
for k, m in (("Sar", "AIRLINE_X"), ("Nl", "NLINEAR_ONLINE"), ("Dl", "DLINEAR_ONLINE"), ("Fits", "FITS"), ("Stsf", "SPARSETSF"), ("Arx", "ARX_RLS_PLS")):
    mac(f"pair{k}", f3(p3[m]["ratio"])); mac(f"pair{k}Lo", f3(p3[m]["lo"])); mac(f"pair{k}Hi", f3(p3[m]["hi"])); mac(f"pair{k}Wins", str(p3[m]["wins"]))
for k, m in (("Chr", "CHRONOS2_COV"), ("TtmZ", "TTM_ZS"), ("TtmF", "TTM_FT_EXOG")):
    mac(f"pair{k}", f3(pf[m]["ratio"])); mac(f"pair{k}Lo", f3(pf[m]["lo"])); mac(f"pair{k}Hi", f3(pf[m]["hi"])); mac(f"pair{k}Wins", str(pf[m]["wins"]))
mac("kLebThousand", f3(g1["V052_PY"]["ALL"])); mac("kChrThousand", f3(g1["CHRONOS2_COV"]["ALL"]))
mac("kChrBdg", f3(g1["CHRONOS2_COV"]["bdg2"])); mac("kLebBdg", f3(g1["V052_PY"]["bdg2"]))
fp, fpmax = float(meta3.fp.mean()), float(meta3.fp_max.max())
mac("fpMean", f"{fp:.0f}"); mac("fpMax", f"{fpmax:,.0f}"); mac("fpOverMean", f"{100 * (fp / 400 - 1):.1f}"); mac("fpOverMax", f"{100 * (fpmax / 1000 - 1):.1f}")
mac("covThree", f3(float(meta3.coverage.mean())))
mac("ttmZsFlops", f"{N['ttm_flops'][0] / 1e6:.1f}"); mac("ttmFtFlops", f"{N['ttm_flops'][1] / 1e6:.1f}")
t2 = N["r2_tab"]; lo2, hi2 = ci(t2.loc["V052_CORRIGIDA", "CI95"])
mac("rTwoAll", f3(t2.loc["V052_CORRIGIDA", "ALL"])); mac("rTwoLo", f3(lo2)); mac("rTwoHi", f3(hi2))
mac("rTwoSar", f3(N["r2_pair"]["AIRLINE_X"]["ratio"])); mac("rTwoChr", f3(N["r2_pair_fm"]["ratio"]))
mac("rTwoFrozen", f3(t2.loc["V052_CONGELADA", "ALL"])); mac("rTwoFrozenRatio", f3(N["r2_pair"]["V052_CONGELADA"]["ratio"]))
mac("rTwoFrozenCat", str(int(t2.loc["V052_CONGELADA", "catastrophic"])))
mac("rOneAll", f2(N["r1_tab"].loc["V052_COMPLETA", "ALL"]))
mcu = N["mcu"]
mac("instrMin", f"{mcu['mean'].min() / 1000:.1f}"); mac("instrMax", f"{mcu['mean'].max() / 1000:.1f}")
mac("usMin", f"{mcu['mean'].min() * 1.6 / 168:.0f}"); mac("usMax", f"{mcu['mean'].max() * 1.6 / 168:.0f}")
mac("stateKB", f"{mcu.STRUCT_BYTES.iloc[0] / 1024:.0f}"); mac("peakMin", f"{mcu.STEP_MAX.min() / 1000:.0f}"); mac("peakMax", f"{mcu.STEP_MAX.max() / 1000:.0f}")
tr = N["trace"]; cpi = {s: tr[(tr.series == s) & (tr.group_type == "class")] for s in ("ons_vg", "bdg2")}
mac("cpiA", f2(cpi["ons_vg"].cycles.sum() / cpi["ons_vg"].instructions.sum())); mac("cpiB", f2(cpi["bdg2"].cycles.sum() / cpi["bdg2"].instructions.sum()))
eq = N["equiv"]; mac("eqDevF", str(int(eq.events_equal_f32.sum()))); mac("eqDevD", str(int(eq.events_equal_f64.sum())))
mac("eqThree", str(int(meta3.c32_events_equal.sum())))
ma = N["misadj"]; orc = [c for c in ma.columns if c.startswith("orac_")]
for k, mu in (("A", 0.1), ("B", 0.05), ("C", 0.03)):
    d = ma[ma.mu == mu]; mac(f"misAcc{k}", str(int((d.accepted != "[]").sum()))); mac(f"misOrcMed{k}", f"{d[orc].max(axis=1).median():.1f}")
    mac(f"misOrcMax{k}", f"{d[orc].max(axis=1).max():.1f}")
mac("misThr", f"{float(ma.log_thr.iloc[0]):.2f}")
fs, fr = N["fdr_sum"], N["fdr_runs"]; cell = lambda s, r: fs[(fs.scen == s) & (fs.rho == str(r))].iloc[0]; allr = fs[fs.rho == "all"].set_index("scen")
nul = fr[fr.scen.str.startswith("N")]
mac("simRuns", str(len(fr))); mac("simNullRuns", str(len(nul))); mac("simNullFalse", str(int((nul.V > 0).sum())))
mac("simPTwoFdr", f3(cell("P2", 0.5).FDR)); mac("simPThreeFdr", f3(cell("P3", 0.5).FDR))
mac("simPTwoRuns", str(int(cell("P2", 0.5)["runs_V>0"]))); mac("simPThreeRuns", str(int(cell("P3", 0.5)["runs_V>0"])))
mac("simPTwoPool", f3(allr.loc["P2", "FDR"])); mac("simPThreePool", f3(allr.loc["P3", "FDR"]))
mac("simAffected", str(int((fr.V > 0).sum()))); mac("simRemoved", str(int(((fr.V > 0) & ~fr.final_false).sum()))); mac("simFinal", str(int(fr.final_false.sum())))
mac("simPThreeFound", f"{100 * cell('P3', 0.95).found_truth:.0f}")
ab = N["abl"].loc["r2+r3"]; mac("ablRatio", f3(ab["ratio"])); mac("ablLo", f3(ab["lo"])); mac("ablHi", f3(ab["hi"])); mac("ablWins", str(int(ab["LEBRE_wins"])))
mac("ablCost", f"{N['abl'].loc['r3', 'fp_allon']:.0f}")
with open(GEN / "numbers.tex", "w", encoding="utf-8") as fh:
    fh.write("% generated by build_assets.py -- do not edit\n")
    for k, v in macros.items():
        fh.write(f"\\newcommand{{\\{k}}}{{{v.replace(',', '{,}')}}}\n")


# ------------------------------------------------------------------ tables
def tab_reserve3():
    order = ["V052_PY", "AIRLINE_X", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "FITS", "ARX_RLS_PLS", "ARX_NLMS",
             "LASSO_ONLINE", "V051", "SPARSETSF"]
    rows = []
    for m in order:
        lo_, hi_ = ci(t3.loc[m, "CI95"]); cls = "reference" if m in ("AIRLINE_X", "ARX_RLS_PLS") else "budget"
        fl = t3.loc[m, "FLOPs"]; fl = "ML fit" if fl != fl else f"{fl:,.0f}"
        name = r"\textbf{LEBRE}" if m == "V052_PY" else NAME[m]
        rows.append(f"{name} & {cls} & {t3.loc[m, 'CAMELS']:.3f} & {t3.loc[m, 'BDG2']:.3f} & {t3.loc[m, 'ALL']:.3f} [{lo_:.3f}, {hi_:.3f}] & "
                    f"{100 * t3.loc[m, 'share>1.5']:.0f}\\% & {int(t3.loc[m, 'catastrophic'])} & {fl} \\\\")
    return "\n".join(rows)


def tab_fm():
    rows = []
    for m, fl in (("V052_PY", f"$\\approx${fp:.0f}"), ("AIRLINE_X", "ML fit"), ("TTM_ZS", f"{N['ttm_flops'][0] / 1e6:.1f}M"),
                  ("TTM_FT_EXOG", f"{N['ttm_flops'][1] / 1e6:.1f}M"), ("CHRONOS2_COV", "$\\sim$1e9--1e10")):
        pr = "--" if m == "V052_PY" else f"{pf[m]['ratio']:.3f} [{pf[m]['lo']:.3f}, {pf[m]['hi']:.3f}]"
        w = "--" if m == "V052_PY" else f"{pf[m]['wins']}/60"
        name = r"\textbf{LEBRE}" if m == "V052_PY" else NAME[m]
        rows.append(f"{name} & {g1[m]['camels']:.3f} & {g1[m]['bdg2']:.3f} & {g1[m]['ALL']:.3f} & {pr} & {w} & {fl} \\\\")
    return "\n".join(rows)


def tab_mcu():
    rows = []
    for r in mcu.itertuples():
        name = {"ons_vg": "ONS (dev.)", "camels": "CAMELS (dev.)", "bdg2": "BDG2 (dev.)"}.get(r.TAG)
        if name is None:
            name = r.TASK.replace("bdg2:chilledwater:", "BDG2 ").replace("camels:", "CAMELS ").replace("_", r"\_")
        rows.append(f"{name} & {r.DX} & {r.mean:,.0f} & {r.STEP_P50:,} & {r.STEP_P999:,} & {r.STEP_MAX:,} & "
                    f"{r.mean * 1.6 / 168:.0f} & {r.NMSE:.4f} & {r.EVENTS} \\\\")
    return "\n".join(rows)


# whole tabular environments (an \input inside a booktabs tabular breaks the alignment)
HEAD = {"tab_reserve3": ("llrrlrrr", r"Model & Class & CAMELS & BDG2 & All [95\% CI] & $>1.5$ & Cat. & Ops/forecast\\"),
        "tab_fm": ("lrrrlrr", r"Model & CAMELS & BDG2 & All & Paired ratio & LEBRE wins & Ops/forecast\\"),
        "tab_mcu": ("lrrrrrrrr", r"Series & Inputs & Mean & Median & p99.9 & Peak & $\mu$s & NMSE & Changes\\")}
for name, fn in (("tab_reserve3", tab_reserve3), ("tab_fm", tab_fm), ("tab_mcu", tab_mcu)):
    spec, head = HEAD[name]
    body = ("% generated by build_assets.py -- do not edit\n"
            + f"\\begin{{tabular}}{{{spec}}}\n\\toprule\n{head}\n\\midrule\n{fn()}\n\\bottomrule\n\\end{{tabular}}\n")
    with open(GEN / f"{name}.tex", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)


# ------------------------------------------------------------------ figures
def fig_accuracy():
    models = [m for m in t3.sort_values("ALL").index if m != "V052_C32"]
    fig, ax = plt.subplots(figsize=(3.4, 2.7))
    y = np.arange(len(models))[::-1]
    for yy, m in zip(y, models):
        v = t3.loc[m, "ALL"]; lo_, hi_ = ci(t3.loc[m, "CI95"]); r = ROLE.get(m, "bud")
        ax.barh(yy, v, color=COL[r], height=0.62)
        ax.plot([lo_, hi_], [yy, yy], color="k", lw=0.8)
    ax.axvline(1, color=C_RED, ls="--", lw=0.7)
    ax.set_yticks(y); ax.set_yticklabels([NAME[m] for m in models])
    ax.get_yticklabels()[[NAME[m] for m in models].index("LEBRE")].set_fontweight("bold")
    ax.set_xlabel("MSE relative to online NLinear (geometric mean, 60 series)")
    fig.savefig(FIG / "reserve3_accuracy.pdf"); plt.close(fig)


def fig_frontier():
    fl = {m: float(meta3[f"flops_{m}"].astype(float).mean()) for m in ["V052_PY", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS",
                                                                       "FITS", "SPARSETSF", "ARX_NLMS", "LASSO_ONLINE", "V051", "ARX_RLS_PLS"]}
    fl["TTM_ZS"], fl["TTM_FT_EXOG"] = N["ttm_flops"]; fl["CHRONOS2_COV"] = 3e9
    short = {"V052_PY": "LEBRE", "NLINEAR_ONLINE": "NLinear", "DLINEAR_ONLINE": "DLinear", "HOLT_WINTERS": "Holt-W.", "FITS": "FITS",
             "SPARSETSF": "SparseTSF", "ARX_NLMS": "ARX", "LASSO_ONLINE": "LASSO", "V051": "v0.51", "ARX_RLS_PLS": "LS-ARX",
             "TTM_ZS": "TTM-ZS", "TTM_FT_EXOG": "TTM-FT", "CHRONOS2_COV": "Chronos-2"}
    off = {"V052_PY": (5, -6), "NLINEAR_ONLINE": (4, 5), "DLINEAR_ONLINE": (4, -6), "ARX_NLMS": (-4, 5), "TTM_FT_EXOG": (4, -6), "CHRONOS2_COV": (-5, 0)}
    fig, ax = plt.subplots(figsize=(3.4, 2.4))
    ax.axvspan(10, 1e4, color="#eef1f4", zorder=0)
    for m, x in fl.items():
        r = ROLE.get(m, "bud"); v = g1[m]["ALL"]
        ax.scatter(x, v, s=28 if m == "V052_PY" else 14, color=COL[r], marker="D" if m == "CHRONOS2_COV" else "o", zorder=3)
        dx, dy = off.get(m, (4, 0))
        ax.annotate(short[m], (x, v), xytext=(dx, dy), textcoords="offset points", fontsize=6.5, ha="left" if dx >= 0 else "right", va="center",
                    fontweight="bold" if m == "V052_PY" else "normal")
    ax.axhline(1, color=C_RED, ls="--", lw=0.7); ax.set_xscale("log"); ax.set_xlim(10, 3e10)
    ax.set_xlabel("floating-point operations per forecast (log)"); ax.set_ylabel("MSE rel. to NLinear (1,000 points)")
    ax.text(12, 3.0, "budget class", fontsize=6.5, color="#555")
    fig.savefig(FIG / "frontier.pdf"); plt.close(fig)


def fig_misadj():
    fig, ax = plt.subplots(figsize=(3.2, 2.2)); rng = np.random.default_rng(2)
    for i, mu in enumerate((0.1, 0.05, 0.03)):
        d = ma[ma.mu == mu]; v = np.maximum(d[orc].max(axis=1).values, 0.02); acc = (d.accepted != "[]").values
        xs = i + rng.uniform(-0.18, 0.18, len(v))
        ax.scatter(xs[~acc], v[~acc], s=7, color=C_BUD); ax.scatter(xs[acc], v[acc], s=12, color=C_RED, marker="D")
        ax.text(i, 80, f"{int(acc.sum())}/{len(d)} accepted", ha="center", fontsize=6.5)
    ax.axhline(float(ma.log_thr.iloc[0]), color=C_RED, ls="--", lw=0.7)
    ax.set_yscale("log"); ax.set_ylim(0.01, 150); ax.set_xticks(range(3)); ax.set_xticklabels([r"$\mu=0.10$", r"$\mu=0.05$", r"$\mu=0.03$"])
    ax.set_ylabel("oracle log-evidence")
    fig.savefig(FIG / "misadjustment.pdf"); plt.close(fig)


def fig_fdr():
    cells = [(s, r) for s in ["N1", "N2", "N3", "N4", "P1", "P2", "P3"] for r in (0.5, 0.95)]
    fig, ax = plt.subplots(figsize=(3.4, 1.9)); x = np.arange(len(cells))
    for i, (s, r) in enumerate(cells):
        c = cell(s, r); g = fr[(fr.scen == s) & (fr.rho == r)]
        ax.bar(i, c["frac_V>0"], color=C_LEB if s.startswith("N") else C_REF, width=0.7)
        ax.plot([i, i], [c.cp_lo, c.cp_hi], color="k", lw=0.7)
        ax.scatter(i, g.final_false.mean(), marker="_", s=60, color="k", zorder=3)
    ax.axhline(0.05, color=C_RED, ls="--", lw=0.7)
    ax.set_xticks(x); ax.set_xticklabels([f"{s}\n{r}" for s, r in cells], fontsize=5.8)
    ax.set_ylabel("runs with a false change")
    fig.savefig(FIG / "false_changes.pdf"); plt.close(fig)


def fig_mcu():
    fig, ax = plt.subplots(figsize=(3.4, 2.0))
    prof = N["prof"]
    for tag, lab, c in (("ons_vg", "ONS (1 input)", C_LEB), ("camels", "CAMELS (3 inputs)", C_REF), ("bdg2", "BDG2 (2 inputs)", C_FM)):
        h = prof[tag]["hist"]; T = prof[tag]["T"]
        ax.step(h[:, 0] + 32, np.cumsum(h[:, 1] / T), where="mid", color=c, lw=1.1, label=lab)
    ax.set_xscale("log"); ax.set_xlim(1000, 6e4); ax.set_ylim(0, 1.01)
    ax.xaxis.set_major_locator(mt.FixedLocator([1e3, 2e3, 5e3, 1e4, 2e4, 5e4]))
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v / 1000:g}k")); ax.xaxis.set_minor_formatter(mt.NullFormatter())
    ax.set_xlabel("instructions per step (simulated Cortex-M4F, log)"); ax.set_ylabel("fraction of steps"); ax.legend(loc="lower right")
    fig.savefig(FIG / "mcu_cdf.pdf"); plt.close(fig)


for fn in (fig_accuracy, fig_frontier, fig_misadj, fig_fdr, fig_mcu):
    fn()
print(f"{len(macros)} macros, 3 tables, 5 figures")
