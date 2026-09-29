"""v052_charts.py — data charts of the LEBRE v0.52 documents (matplotlib -> inline SVG, text kept as text).
Colour by role, fixed order: LEBRE (blue), other budget-class models (neutral grey), classical references (orange),
foundation models (aqua). Domains: ONS / CAMELS / BDG2 = blue / orange / aqua. Every label comes from the caller (PT or EN)."""
import io
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mt  # noqa: E402
import numpy as np  # noqa: E402

LEB, BUD, REF, FMC = "#2a78d6", "#8b9099", "#eb6834", "#1baf7a"
DOM = {"ONS": "#2a78d6", "CAMELS": "#eb6834", "BDG2": "#1baf7a"}
INK, MUT, GRID = "#0f172a", "#64748b", "#e2e8f0"
RED = "#e34948"

plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Segoe UI", "DejaVu Sans"], "font.size": 8.2,
                     "svg.fonttype": "none", "axes.edgecolor": "#94a3b8", "axes.labelcolor": INK, "xtick.color": MUT,
                     "ytick.color": MUT, "axes.titlesize": 9.5, "axes.titleweight": "bold", "axes.titlecolor": INK,
                     "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "legend.fontsize": 7.6, "lines.linewidth": 1.6})


class Fmt:
    def __init__(self, lang):
        self.pt = lang == "pt"

    def n(self, x, d=2):
        s = f"{x:,.{d}f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".") if self.pt else s

    def axis(self, ax, which="y", d=None):
        def f(v, _):
            if d is None:
                s = f"{v:g}"
            else:
                s = f"{v:.{d}f}"
            return s.replace(".", ",") if self.pt else s
        (ax.yaxis if which == "y" else ax.xaxis).set_major_formatter(mt.FuncFormatter(f))

    def logaxis(self, ax, which="x"):
        sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")

        def f(v, _):
            if v <= 0:
                return ""
            e = np.log10(v)
            return f"10{str(int(round(e))).translate(sup)}" if abs(e - round(e)) < 1e-6 else ""
        (ax.xaxis if which == "x" else ax.yaxis).set_major_formatter(mt.FuncFormatter(f))
        (ax.xaxis if which == "x" else ax.yaxis).set_minor_formatter(mt.NullFormatter())


def svg(fig):
    b = io.StringIO(); fig.savefig(b, format="svg", bbox_inches="tight", pad_inches=0.04); plt.close(fig)
    s = b.getvalue(); s = s[s.find("<svg"):]
    s = re.sub(r'<svg([^>]*?)width="[^"]*"\s+height="[^"]*"', r'<svg\1', s, count=1)   # scale with the container
    return s


def _grid(ax, axis="x"):
    ax.grid(axis=axis, color=GRID, lw=0.7); ax.set_axisbelow(True)


# ------------------------------------------------------------------ accuracy by model, with CI (reserve)
def bar_ci(rows, F, xlabel, ref_label, width=7.2):
    """rows: [(label, value, lo, hi, role)] role in {leb, bud, ref, fm}; sorted top-down as given"""
    col = {"leb": LEB, "bud": BUD, "ref": REF, "fm": FMC}
    fig, ax = plt.subplots(figsize=(width, 0.27 * len(rows) + 0.8))
    y = np.arange(len(rows))[::-1]
    vmax = max(r[3] if r[3] == r[3] else r[1] for r in rows) * 1.12
    for yy, (lab, v, lo, hi, role) in zip(y, rows):
        ax.barh(yy, v, height=0.62, color=col[role], alpha=1 if role == "leb" else 0.85)
        if lo == lo and hi == hi and hi > lo:
            ax.plot([lo, hi], [yy, yy], color=INK, lw=1.0); ax.plot([lo, lo], [yy - .15, yy + .15], color=INK, lw=1.0)
            ax.plot([hi, hi], [yy - .15, yy + .15], color=INK, lw=1.0)
        ax.text((hi if hi == hi else v) + vmax * 0.012, yy, F.n(v, 3), va="center", fontsize=7.4, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=7.8)
    for tl, r in zip(ax.get_yticklabels(), rows):
        if r[4] == "leb":
            tl.set_fontweight("bold"); tl.set_color(INK)
    ax.axvline(1.0, color=RED, ls="--", lw=0.9); ax.text(1.0, y.max() + 0.75, ref_label, color=RED, fontsize=7.2, ha="center")
    ax.set_xlim(0, vmax); ax.set_xlabel(xlabel); _grid(ax); F.axis(ax, "x", 1)
    return svg(fig)


# ------------------------------------------------------------------ cost x error frontier
def frontier(pts, F, xlabel, ylabel, zone_label, width=7.2):
    """pts: [(label, flops, err, role, est, dx, dy)]"""
    col = {"leb": LEB, "bud": BUD, "ref": REF, "fm": FMC}
    fig, ax = plt.subplots(figsize=(width, 3.3))
    ax.axvspan(10, 1e4, color="#f1f5f9", zorder=0); ax.text(12, 0.585, zone_label, fontsize=7.2, color=MUT, va="bottom")
    for lab, fl, e, role, est, dx, dy in pts:
        ax.scatter(fl, e, s=70 if role == "leb" else 38, color=col[role], edgecolor="white", lw=1.2, zorder=3,
                   marker="D" if est else "o")
        ax.annotate(lab, (fl, e), xytext=(dx, dy), textcoords="offset points", fontsize=7.2,
                    color=INK, fontweight="bold" if role == "leb" else "normal", ha="left" if dx >= 0 else "right", va="center")
    ax.axhline(1.0, color=RED, ls="--", lw=0.8)
    ax.set_xscale("log"); ax.set_xlim(10, 3e10); F.logaxis(ax, "x")
    ax.set_ylim(0.58, max(p[2] for p in pts) * 1.08); F.axis(ax, "y", 1)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); _grid(ax, "both")
    return svg(fig)


# ------------------------------------------------------------------ per-series distribution (log scale)
def strip(series, F, ylabel, width=7.2, thr=1.5, thr_label=""):
    """series: [(label, values, role)]"""
    col = {"leb": LEB, "bud": BUD, "ref": REF, "fm": FMC}
    fig, ax = plt.subplots(figsize=(width, 2.9))
    rng = np.random.default_rng(3)
    for i, (lab, v, role) in enumerate(series):
        v = np.asarray(v, float); v = v[np.isfinite(v)]
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=9, color=col[role], alpha=0.75, lw=0, zorder=3)
        g = float(np.exp(np.log(v).mean())); ax.plot([i - 0.3, i + 0.3], [g, g], color=INK, lw=1.8, zorder=4)
    ax.axhline(1.0, color=RED, ls="--", lw=0.8); ax.axhline(thr, color=MUT, ls=":", lw=0.9)
    ax.text(len(series) - 0.5, thr * 1.04, thr_label, fontsize=7, color=MUT, ha="right", va="bottom")
    ax.set_yscale("log"); ax.set_ylim(0.05, 20)
    ax.yaxis.set_major_locator(mt.FixedLocator([0.1, 0.2, 0.5, 1, 2, 5, 10]))
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 1) if v < 1 else f"{v:g}")); ax.yaxis.set_minor_formatter(mt.NullFormatter())
    ax.set_xticks(range(len(series))); ax.set_xticklabels([s[0] for s in series], fontsize=7.4, rotation=0)
    for tl, s in zip(ax.get_xticklabels(), series):
        if s[2] == "leb":
            tl.set_fontweight("bold")
    ax.set_ylabel(ylabel); _grid(ax, "y")
    return svg(fig)


# ------------------------------------------------------------------ paired wins
def wins(rows, F, xlabel, n, width=7.2):
    """rows: [(label, wins, ratio, lo, hi, role)]"""
    col = {"bud": BUD, "ref": REF, "fm": FMC}
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(width, 0.26 * len(rows) + 0.9), sharey=True, gridspec_kw={"width_ratios": [1, 1.2]})
    y = np.arange(len(rows))[::-1]
    for yy, (lab, w, r, lo, hi, role) in zip(y, rows):
        a1.barh(yy, w, color=LEB, height=0.6); a1.barh(yy, n - w, left=w, color="#dbe3ec", height=0.6)
        a1.text(w - 1, yy, str(w), color="white", fontsize=7, va="center", ha="right", fontweight="bold")
        a2.plot([lo, hi], [yy, yy], color=col[role], lw=2.2); a2.scatter(r, yy, color=col[role], s=24, zorder=3)
        a2.text(hi + 0.03, yy, F.n(r, 3), fontsize=7.2, va="center", color=INK)
    a1.set_yticks(y); a1.set_yticklabels([r[0] for r in rows], fontsize=7.6); a1.set_xlim(0, n)
    a1.axvline(n / 2, color=MUT, lw=0.7, ls=":"); a1.set_xlabel(xlabel[0])
    a2.axvline(1.0, color=RED, ls="--", lw=0.8); a2.set_xscale("log"); a2.set_xlim(0.2, 1.8)
    a2.xaxis.set_major_locator(mt.FixedLocator([0.25, 0.5, 0.75, 1, 1.5]))
    a2.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 2))); a2.xaxis.set_minor_formatter(mt.NullFormatter())
    a2.set_xlabel(xlabel[1]); _grid(a2)
    fig.subplots_adjust(wspace=0.08)
    return svg(fig)


# ------------------------------------------------------------------ grouped bars across evaluations
def grouped(groups, series, F, ylabel, width=7.2, note=None):
    """groups: [label]; series: [(label, [values], color)]"""
    fig, ax = plt.subplots(figsize=(width, 2.7))
    k = len(series); w = 0.8 / k; x = np.arange(len(groups))
    for j, (lab, vals, c) in enumerate(series):
        xs = x - 0.4 + w * (j + 0.5)
        ax.bar(xs, vals, width=w * 0.92, color=c, label=lab)
        for xx, v in zip(xs, vals):
            if v == v:
                ax.text(xx, v + 0.015, F.n(v, 2), ha="center", fontsize=6.6, color=INK)
    ax.axhline(1.0, color=RED, ls="--", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels(groups, fontsize=7.6); ax.set_ylabel(ylabel); F.axis(ax, "y", 1)
    ax.set_ylim(0, 1.45); _grid(ax, "y"); ax.legend(ncol=min(k, 5), loc="upper center", bbox_to_anchor=(0.5, 1.2))
    return svg(fig)


# ------------------------------------------------------------------ stress test of target gaps
def stress(df, F, labels, ylabel, width=7.2):
    fig, ax = plt.subplots(figsize=(width, 2.6))
    d = df[df.scen == "gaps"]; cfgs = ["FROZEN", "HOLD", "HOLD_CLIP"]; cols = [RED, BUD, LEB]
    rng = np.random.default_rng(1)
    for i, (c, cc) in enumerate(zip(cfgs, cols)):
        v = d[d.cfg == c].max_dev_over_range.values.astype(float)
        v = np.where(np.isfinite(v), v, 1e80)
        ax.scatter(i + rng.uniform(-0.2, 0.2, len(v)), v, s=14, color=cc, alpha=0.8, lw=0)
        nexp = int((v > 10).sum())
        ax.text(i, 3e84, labels["exp"].format(nexp), ha="center", fontsize=7.6, color=INK, fontweight="bold")
    ax.axhline(10, color=MUT, ls=":", lw=0.9); ax.text(2.45, 14, labels["thr"], fontsize=7, color=MUT, ha="right", va="bottom")
    ax.set_yscale("log"); ax.set_ylim(0.05, 1e88); F.logaxis(ax, "y")
    ax.yaxis.set_major_locator(mt.FixedLocator([1, 1e10, 1e20, 1e40, 1e60, 1e80]))
    ax.set_xticks(range(3)); ax.set_xticklabels(labels["cfg"], fontsize=7.8); ax.set_ylabel(ylabel); _grid(ax, "y")
    return svg(fig)


# ------------------------------------------------------------------ misadjustment oracle
def misadj(df, F, labels, width=7.2):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(width, 2.7), gridspec_kw={"width_ratios": [1.35, 1]})
    mus = sorted(df.mu.unique(), reverse=True); rng = np.random.default_rng(2)
    orc = [c for c in df.columns if c.startswith("orac_")]
    thr = float(df.log_thr.iloc[0])
    for i, mu in enumerate(mus):
        d = df[df.mu == mu]; v = d[orc].max(axis=1).values
        acc = (d.accepted != "[]").values
        xs = i + rng.uniform(-0.2, 0.2, len(v))
        a1.scatter(xs[~acc], np.maximum(v[~acc], 0.02), s=14, color=BUD, lw=0, alpha=0.8)
        a1.scatter(xs[acc], np.maximum(v[acc], 0.02), s=22, color=RED, lw=0, marker="D")
        a1.text(i, 70, labels["acc"].format(int(acc.sum()), len(d)), ha="center", fontsize=7.4, color=INK, fontweight="bold")
    a1.axhline(thr, color=RED, ls="--", lw=0.9); a1.text(2.45, thr * 1.1, labels["thr"], fontsize=7, color=RED, ha="right", va="bottom")
    a1.set_yscale("log"); a1.set_ylim(0.01, 150)
    a1.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 2) if v < 1 else f"{v:g}")); a1.yaxis.set_minor_formatter(mt.NullFormatter())
    a1.set_xticks(range(len(mus))); a1.set_xticklabels([f"μ = {F.n(m, 2)}" for m in mus]); a1.set_ylabel(labels["y1"]); _grid(a1, "y")
    a1.set_title(labels["t1"])
    g = df.groupby("mu")[["M_emp", "M_theory"]].mean().sort_index()
    a2.plot(g.index, g.M_emp, "o-", color=LEB, label=labels["emp"]); a2.plot(g.index, g.M_theory, "s--", color=MUT, label=labels["theo"])
    a2.axvspan(0, 0.016, color="#dcfce7", zorder=0); a2.text(0.0015, 0.003, labels["exact"], fontsize=6.6, color="#166534", va="bottom")
    a2.set_xlim(0, 0.11); a2.set_ylim(0, 0.09); F.axis(a2, "x", 2); F.axis(a2, "y", 2)
    a2.set_xlabel(labels["x2"]); a2.set_ylabel(labels["y2"]); a2.legend(loc="upper left"); _grid(a2, "both"); a2.set_title(labels["t2"])
    fig.subplots_adjust(wspace=0.32)
    return svg(fig)


# ------------------------------------------------------------------ e-process simulation (development)
def eproc_sim(F, labels, width=7.2):
    names = ["psiE2", "psiE1", "bet", "mix"]
    typeI = np.array([[0.000, 0.005, 0.013], [0.003, 0.025, 0.003], [0.020, 0.033, 0.035], [0.018, 0.025, 0.018]])
    power = [0.66, 0.77, 0.91, 0.86]; tmed = [3720, 2910, 1520, 1910]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(width, 2.5), gridspec_kw={"width_ratios": [1.3, 1]})
    x = np.arange(4); w = 0.26; cols = ["#86b6ef", "#2a78d6", "#184f95"]
    for j in range(3):
        a1.bar(x - w + j * w, typeI[:, j], width=w * 0.92, color=cols[j], label=labels["forms"][j])
    a1.axhline(0.05, color=RED, ls="--", lw=0.9); a1.text(3.45, 0.052, "α = 0,05" if F.pt else "α = 0.05", color=RED, fontsize=7, ha="right", va="bottom")
    a1.set_xticks(x); a1.set_xticklabels(labels["names"], fontsize=7.4); a1.set_ylim(0, 0.065); F.axis(a1, "y", 2)
    a1.set_ylabel(labels["y1"]); a1.legend(loc="upper left", fontsize=6.8); _grid(a1, "y"); a1.set_title(labels["t1"])
    for i, (p, t) in enumerate(zip(power, tmed)):
        c = LEB if names[i] == "psiE1" else BUD
        a2.scatter(t, p, s=60 if c == LEB else 36, color=c, zorder=3)
        a2.annotate(labels["names"][i], (t, p), xytext=(6, -3), textcoords="offset points", fontsize=7.2,
                    fontweight="bold" if c == LEB else "normal")
    a2.set_xlim(1200, 4400); a2.set_ylim(0.6, 0.97); F.axis(a2, "y", 2)
    a2.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0)))
    a2.set_xlabel(labels["x2"]); a2.set_ylabel(labels["y2"]); _grid(a2, "both"); a2.set_title(labels["t2"])
    fig.subplots_adjust(wspace=0.35)
    return svg(fig)


# ------------------------------------------------------------------ example: forecast window + interval + evidence
def example_forecast(A, F, labels, t0, t1, width=7.2):
    y, f, q = A["y"], A["f"], A["q"]; t = np.arange(t0, t1)
    fig, ax = plt.subplots(figsize=(width, 2.2))
    ax.fill_between(t, f[t0:t1] - q[t0:t1], f[t0:t1] + q[t0:t1], color="#cde2fb", lw=0, label=labels["int"])
    ax.plot(t, y[t0:t1], color=INK, lw=1.1, label=labels["y"]); ax.plot(t, f[t0:t1], color=LEB, lw=1.3, ls="--", label=labels["f"])
    ax.set_xlim(t0, t1); ax.set_xlabel(labels["x"]); ax.set_ylabel(labels["yl"]); _grid(ax, "y")
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0))); ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0)))
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.2))
    return svg(fig)


def example_evidence(A, events, F, labels, tmax, width=7.2):
    ev, keys = A["ev"], A["ev_key"]
    fig, ax = plt.subplots(figsize=(width, 2.6))
    thr = None
    styles = {"add": LEB, "rem": REF, "split": FMC, "swap": BUD}
    shown = set()
    kinds = np.array([k.split("|")[0] for k in keys])
    hyp = np.array([k.split("|")[1] if k.split("|")[0] != "rem" else k.split("|")[2] for k in keys])
    for kind in ("add", "split", "rem"):
        for h in np.unique(hyp[kinds == kind]):
            m = (kinds == kind) & (hyp == h)
            tt, le, th = ev[m, 0], ev[m, 1], ev[m, 2]
            # break the line between episodes
            br = np.flatnonzero(np.diff(tt) > 10) + 1
            for seg in np.split(np.arange(len(tt)), br):
                if len(seg) < 2 or tt[seg[0]] > tmax:
                    continue
                lab = labels["kind"][kind] if kind not in shown else None; shown.add(kind)
                ax.plot(tt[seg], le[seg], color=styles[kind], lw=1.0, alpha=0.9, label=lab)
                ax.plot(tt[seg], th[seg], color=styles[kind], lw=0.6, ls=":", alpha=0.7)
    for e in events:
        if e[1] == "accepted" and e[0] <= tmax:
            ax.axvline(e[0], color=INK, lw=0.7, ls="--"); ax.text(e[0] + tmax * 0.005, ax.get_ylim()[1] if False else 7.6, labels["acc"](e), fontsize=6.8, color=INK, va="top")
    ax.set_xlim(0, tmax); ax.set_ylim(-4, 8); ax.set_xlabel(labels["x"]); ax.set_ylabel(labels["y"])
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0))); _grid(ax, "y")
    ax.legend(ncol=4, loc="lower right", fontsize=7)
    return svg(fig)


def response(resp_rows, truth, F, labels, width=7.2):
    """resp_rows: {input_label: [((lo,hi), w_per_lag)]}; truth: {input_label: {lag: w}}"""
    fig, axes = plt.subplots(1, len(resp_rows), figsize=(width, 2.2), sharey=True)
    for ax, (name, segs) in zip(np.atleast_1d(axes), resp_rows.items()):
        lags = np.arange(1, 32); w = np.zeros(31)
        for (lo, hi), v in segs:
            w[lo - 1:hi] += v
        tr = np.zeros(31)
        for k, v in truth[name].items():
            tr[k - 1] = v
        ax.bar(lags, tr, color="#dbe3ec", width=0.85, label=labels["true"])
        ax.plot(lags, w, "o-", color=LEB, ms=3, lw=1.1, label=labels["est"])
        ax.axhline(0, color="#94a3b8", lw=0.6); ax.set_title(name); ax.set_xlabel(labels["x"]); F.axis(ax, "y", 1)
        _grid(ax, "y")
    np.atleast_1d(axes)[0].set_ylabel(labels["y"]); np.atleast_1d(axes)[0].legend(loc="upper right")
    return svg(fig)


# ------------------------------------------------------------------ analytic cost
def cost_components(rows, F, labels, contract=400, width=7.2):
    """rows: [(label, {component: fp})]"""
    comps = ["memory", "structure", "screening", "experiments", "control"]
    cols = ["#1baf7a", "#2a78d6", "#86b6ef", "#eb6834", "#8b9099"]
    fig, ax = plt.subplots(figsize=(width, 0.42 * len(rows) + 0.9))
    y = np.arange(len(rows))[::-1]
    for yy, (lab, c) in zip(y, rows):
        left = 0
        for k, col in zip(comps, cols):
            v = c.get(k, 0); ax.barh(yy, v, left=left, color=col, height=0.6, label=labels["comp"][k] if yy == y[0] else None)
            if v > 28:
                ax.text(left + v / 2, yy, F.n(v, 0), ha="center", va="center", fontsize=6.8, color="white")
            left += v
        ax.text(left + 6, yy, F.n(left, 0), va="center", fontsize=7.4, color=INK, fontweight="bold")
    ax.axvline(contract, color=RED, ls="--", lw=0.9); ax.text(contract + 4, y.max() + 0.45, labels["contract"], color=RED, fontsize=7)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows]); ax.set_xlabel(labels["x"]); _grid(ax)
    ax.legend(ncol=5, loc="upper center", bbox_to_anchor=(0.5, -0.32 if len(rows) < 3 else -0.22), fontsize=7)
    return svg(fig)


def fp_hist(meta, F, labels, width=7.2):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(width, 2.3))
    for g, c in (("camels", DOM["CAMELS"]), ("bdg2", DOM["BDG2"])):
        d = meta[meta.group == g]
        a1.hist(d.fp, bins=np.arange(240, 660, 20), color=c, alpha=0.75, label=labels["grp"][g])
        a2.hist(d.fp_max, bins=np.arange(820, 1040, 10), color=c, alpha=0.75, label=labels["grp"][g])
    a1.axvline(400, color=RED, ls="--", lw=0.9); a2.axvline(1000, color=RED, ls="--", lw=0.9)
    a1.set_xlabel(labels["x1"]); a2.set_xlabel(labels["x2"]); a1.set_ylabel(labels["y"]); a1.legend(loc="upper right")
    for a in (a1, a2):
        _grid(a, "y"); a.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0)))
    fig.subplots_adjust(wspace=0.25)
    return svg(fig)


# ------------------------------------------------------------------ microcontroller
def mcu_steps(df, F, labels, width=7.2):
    fig, ax = plt.subplots(figsize=(width, 2.9))
    x = np.arange(len(df))
    for i, r in enumerate(df.itertuples()):
        c = DOM[r.GROUP]
        ax.plot([i, i], [r.STEP_P50, r.STEP_MAX], color=c, lw=1.0, alpha=0.6)
        ax.scatter(i, r.STEP_MAX, marker="^", s=30, color=c, zorder=3)
        ax.scatter(i, r.STEP_P999, marker="_", s=180, color=c, lw=2, zorder=3)
        ax.bar(i, r.mean, width=0.55, color=c, alpha=0.9)
        ax.text(i, r.mean * 0.55, F.n(r.mean, 0), rotation=90, ha="center", va="center", fontsize=6.8, color="white", fontweight="bold")
    ax.set_yscale("log"); ax.set_ylim(800, 1.2e5)
    ax.yaxis.set_major_locator(mt.FixedLocator([1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5]))
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0))); ax.yaxis.set_minor_formatter(mt.NullFormatter())
    ax.set_xticks(x); ax.set_xticklabels(labels["ticks"], fontsize=7); ax.set_ylabel(labels["y"]); _grid(ax, "y")
    ax.axvline(2.5, color=MUT, lw=0.8, ls=":")
    ax.text(1, 9e4, labels["dev"], ha="center", fontsize=7.4, color=MUT); ax.text(4.5, 9e4, labels["r3"], ha="center", fontsize=7.4, color=MUT)
    from matplotlib.lines import Line2D
    h = [Line2D([], [], color=BUD, marker="s", ls="", ms=7, label=labels["mean"]), Line2D([], [], color=BUD, marker="_", ls="", ms=11, mew=2, label="p99,9" if F.pt else "p99.9"),
         Line2D([], [], color=BUD, marker="^", ls="", ms=6, label=labels["max"])]
    ax.legend(handles=h, loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=3)
    ax2 = ax.twinx(); lo, hi = ax.get_ylim(); ax2.set_yscale("log"); ax2.set_ylim(lo * 1.6 / 168, hi * 1.6 / 168)
    ax2.yaxis.set_major_locator(mt.FixedLocator([10, 20, 50, 100, 200, 500]))
    ax2.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:g} µs")); ax2.yaxis.set_minor_formatter(mt.NullFormatter())
    ax2.spines["right"].set_visible(True); ax2.set_ylabel(labels["y2"], color=MUT)
    return svg(fig)


def mcu_timeline(prof, F, labels, width=7.2):
    fig, axes = plt.subplots(3, 1, figsize=(width, 4.6), sharex=False)
    for ax, (tag, grp, name) in zip(axes, labels["series"]):
        p = prof[tag]; b = p["blk"]; t = b[:, 0] * 64
        cnt = np.minimum(64, p["T"] - t)
        ax.fill_between(t, 0, b[:, 2], color=DOM[grp], alpha=0.18, lw=0, step="post", label=labels["max"])
        ax.plot(t, b[:, 1] / cnt, color=DOM[grp], lw=1.0, drawstyle="steps-post", label=labels["mean"])
        if len(p["big"]):
            ax.scatter(p["big"][:, 0], p["big"][:, 1], s=10, color=INK, marker="v", zorder=3, label=labels["big"])
        ax.set_yscale("log"); ax.set_ylim(1500, 8e4); ax.set_xlim(0, p["T"])
        ax.yaxis.set_major_locator(mt.FixedLocator([2e3, 5e3, 1e4, 2e4, 5e4]))
        ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0))); ax.yaxis.set_minor_formatter(mt.NullFormatter())
        ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0)))
        ax.set_title(name, fontsize=7.8, pad=3)
        _grid(ax, "y")
    axes[0].legend(ncol=3, loc="lower right", bbox_to_anchor=(1, 1.12), fontsize=6.8); axes[-1].set_xlabel(labels["x"]); axes[1].set_ylabel(labels["y"])
    fig.subplots_adjust(hspace=0.55)
    return svg(fig)


def mcu_hist(prof, F, labels, width=7.2):
    fig, ax = plt.subplots(figsize=(width, 2.4))
    for tag, grp, name in labels["series"]:
        h = prof[tag]["hist"]; T = prof[tag]["T"]
        x = h[:, 0] + 32; frac = h[:, 1] / T
        ax.step(x, np.cumsum(frac), where="mid", color=DOM[grp], lw=1.4, label=name)
    ax.set_xscale("log"); ax.set_xlim(1000, 6e4); ax.set_ylim(0, 1.01)
    ax.xaxis.set_major_locator(mt.FixedLocator([1e3, 2e3, 5e3, 1e4, 2e4, 5e4]))
    ax.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 0))); ax.xaxis.set_minor_formatter(mt.NullFormatter())
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:.0%}".replace(".", ",")))
    ax.axhline(0.999, color=MUT, lw=0.7, ls=":"); ax.text(1050, 0.985, "99,9%" if F.pt else "99.9%", fontsize=6.8, color=MUT, va="top")
    ax.set_xlabel(labels["x"]); ax.set_ylabel(labels["y"]); ax.legend(loc="center right"); _grid(ax, "both")
    return svg(fig)


def mcu_breakdown(tr, F, labels, width=7.2):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(width, 2.8), gridspec_kw={"width_ratios": [1, 1.25]})
    series = [("ons_vg", labels["s_ons"]), ("bdg2", labels["s_bdg2"])]
    cls_order = ["alu", "ldst", "branch", "fpldst", "fp", "fpdiv", "call", "div", "fpmac", "other"]
    ccol = ["#2a78d6", "#86b6ef", "#8b9099", "#1baf7a", "#8fd9bd", "#e34948", "#c3c7cd", "#c3c7cd", "#c3c7cd", "#c3c7cd"]
    for j, (tag, nm) in enumerate(series):
        d = tr[(tr.series == tag) & (tr.group_type == "class")].set_index("group").cycles; tot = d.sum(); left = 0
        for k, c in zip(cls_order, ccol):
            v = d.get(k, 0) / tot
            a1.barh(1 - j, v, left=left, color=c, height=0.55, label=labels["cls"].get(k, labels["cls"]["other"]) if j == 0 and k in labels["cls"] else None)
            if v > 0.06:
                a1.text(left + v / 2, 1 - j, f"{v:.0%}", ha="center", va="center", fontsize=6.6, color="white")
            left += v
    a1.set_yticks([1, 0]); a1.set_yticklabels([s[1] for s in series]); a1.set_xlim(0, 1)
    a1.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:.0%}")); a1.set_title(labels["t1"])
    a1.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.18), fontsize=6.6)
    fn_map = labels["fn"]
    agg = {}
    for tag, _ in series:
        d = tr[(tr.series == tag) & (tr.group_type == "function")]; tot = d.cycles.sum()
        g = {}
        for r in d.itertuples():
            key = fn_map.get(r.group, labels["fn_other"]); g[key] = g.get(key, 0) + r.cycles / tot
        agg[tag] = g
    keys = sorted(set(agg["ons_vg"]) | set(agg["bdg2"]), key=lambda k: -(agg["ons_vg"].get(k, 0) + agg["bdg2"].get(k, 0)))
    keys = [k for k in keys if k != labels["fn_other"]] + [labels["fn_other"]]
    y = np.arange(len(keys))[::-1]; h = 0.36
    for j, ((tag, nm), c) in enumerate(zip(series, [DOM["ONS"], DOM["BDG2"]])):
        vals = [agg[tag].get(k, 0) for k in keys]
        a2.barh(y + (h / 2 if j == 0 else -h / 2), vals, height=h, color=c, label=nm)
    a2.set_yticks(y); a2.set_yticklabels(keys, fontsize=7); a2.xaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    a2.legend(loc="lower right", fontsize=6.8); _grid(a2); a2.set_title(labels["t2"])
    fig.subplots_adjust(wspace=0.75)
    return svg(fig)


def mcu_memory(F, labels, state, bss, text_model, text_libm, width=7.2):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(width, 1.9))
    kb = lambda b: b / 1024
    a1.barh(0, kb(state), color=LEB, height=0.55); a1.barh(0, kb(bss - state), left=kb(state), color="#86b6ef", height=0.55)
    a1.barh(0, 192 - kb(bss), left=kb(bss), color="#eef2f6", height=0.55)
    a1.text(kb(state) / 2, 0, labels["state"].format(F.n(kb(state), 1)), color="white", ha="center", va="center", fontsize=7)
    a1.text(kb(bss) + 2, 0, labels["free"], color=MUT, ha="left", va="center", fontsize=7)
    a1.axvline(128, color=INK, lw=0.8, ls=":"); a1.text(128.5, 0.42, "128 KB", fontsize=6.6, color=INK)
    a1.set_xlim(0, 192); a1.set_yticks([0]); a1.set_yticklabels([labels["ram"]])
    a2.barh(0, kb(text_model), color=LEB, height=0.55); a2.barh(0, kb(text_libm), left=kb(text_model), color="#86b6ef", height=0.55)
    a2.barh(0, 1024 - kb(text_model + text_libm), left=kb(text_model + text_libm), color="#eef2f6", height=0.55)
    a2.text(kb(text_model + text_libm) + 6, 0, labels["code"].format(F.n(kb(text_model), 1), F.n(kb(text_libm), 1)), fontsize=7, va="center", color=INK)
    a2.set_xlim(0, 1024); a2.set_yticks([0]); a2.set_yticklabels([labels["flash"]]); a2.set_xlabel("KB")
    for a in (a1, a2):
        a.spines["left"].set_visible(False); a.tick_params(axis="y", length=0)
    fig.subplots_adjust(hspace=0.9)
    return svg(fig)


def equiv(dev, r3, F, labels, width=7.2):
    fig, ax = plt.subplots(figsize=(width, 2.2))
    v1 = np.abs(dev.rel_nmse_f32.values); v2 = np.abs(r3.rel_nmse_c32.values)
    rng = np.random.default_rng(4)
    for i, (v, eq, lab) in enumerate(((v1, dev.events_equal_f32.values, labels["dev"]), (v2, r3.c32_events_equal.values, labels["r3"]))):
        v = np.maximum(v, 1e-12); ys = i + rng.uniform(-0.2, 0.2, len(v))
        ax.scatter(v[eq.astype(bool)], ys[eq.astype(bool)], s=14, color=LEB, lw=0, label=labels["same"] if i == 0 else None)
        ax.scatter(v[~eq.astype(bool)], ys[~eq.astype(bool)], s=22, color=REF, marker="D", lw=0, label=labels["diff"] if i == 0 else None)
    ax.axvline(1e-4, color=RED, ls="--", lw=0.9); ax.text(1.15e-4, 1.45, labels["crit"], color=RED, fontsize=7, va="top")
    ax.set_xscale("log"); ax.set_xlim(1e-10, 0.05); F.logaxis(ax, "x")
    ax.set_yticks([0, 1]); ax.set_yticklabels([labels["dev"], labels["r3"]]); ax.set_ylim(-0.5, 1.5)
    ax.set_xlabel(labels["x"]); ax.legend(loc="lower left", fontsize=7); _grid(ax)
    return svg(fig)


# ------------------------------------------------------------------ false-change simulation (EXT-02)
def fdr_sim(S, runs, F, labels, width=7.2):
    """S: summary per (scen, rho); runs: per-run with final_false"""
    cells = [(s, r) for s in ["N1", "N2", "N3", "N4", "P1", "P2", "P3"] for r in (0.5, 0.95)]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(width, 3.6), sharex=True, gridspec_kw={"height_ratios": [1.3, 1]})
    x = np.arange(len(cells))
    for i, (s, r) in enumerate(cells):
        row = S[(S.scen == s) & (S.rho.astype(str) == str(r))].iloc[0]
        g = runs[(runs.scen == s) & (runs.rho == r)]
        c = LEB if s.startswith("N") else REF
        a1.bar(i, row["frac_V>0"], color=c, width=0.7, alpha=0.9)
        a1.plot([i, i], [row.cp_lo, row.cp_hi], color=INK, lw=1)
        fin = g.final_false.mean()
        a1.scatter(i, fin, marker="_", s=120, color=INK, lw=2, zorder=3)
        a2.bar(i, row.FDR, color=c, width=0.7, alpha=0.9); a2.plot([i, i], [row.FDR, row.FDR_hi], color=INK, lw=1)
    a1.axhline(0.05, color=RED, ls="--", lw=0.8); a2.axhline(0.05, color=RED, ls="--", lw=0.8)
    a2.text(len(cells) - 0.4, 0.055, "α = 0,05" if F.pt else "α = 0.05", color=RED, fontsize=7, ha="right", va="bottom")
    a1.set_ylabel(labels["y1"]); a2.set_ylabel(labels["y2"])
    for a in (a1, a2):
        a.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: F.n(v, 2))); _grid(a, "y")
    a1.set_ylim(0, 0.36); a2.set_ylim(0, 0.18)
    a2.set_xticks(x); a2.set_xticklabels([f"{s}\nρ={F.n(r, 2)}" for s, r in cells], fontsize=6.8)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    a1.legend(handles=[Patch(color=LEB, label=labels["null"]), Patch(color=REF, label=labels["partial"]),
                       Line2D([], [], color=INK, marker="_", ls="", ms=10, mew=2, label=labels["final"])], loc="upper left", fontsize=7)
    fig.subplots_adjust(hspace=0.12)
    return svg(fig)
