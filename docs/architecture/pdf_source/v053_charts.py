"""v053_charts.py — data charts of the LEBRE v0.53 documents (matplotlib -> inline SVG), same style as v052_charts.py
(imported, not changed). Every label comes from the caller (PT or EN)."""
import matplotlib.pyplot as plt
import numpy as np

from v052_charts import BUD, FMC, GRID, INK, LEB, MUT, RED, REF, Fmt, _grid, svg  # noqa: F401

FAM_COL = {"camels": "#eb6834", "bdg2": "#1baf7a", "solar": "#e0a100", "eolica": "#2a78d6", "carga": "#7c5cc4",
           "fx_ret": "#64748b", "fx_abs": "#94a3b8", "fx_niv": "#334155"}


def fam_ratio(rows, F, xlabel, ref_label, geo_label, width=7.2):
    """rows: [(label, family_key, [series ratios], geo)] top-down."""
    fig, ax = plt.subplots(figsize=(width, 0.36 * len(rows) + 0.9))
    y = np.arange(len(rows))[::-1]
    rng = np.random.default_rng(0)
    for yy, (lab, k, vals, g) in zip(y, rows):
        v = np.asarray(vals, float)
        ax.scatter(v, yy + rng.uniform(-0.17, 0.17, len(v)), s=13, color=FAM_COL[k], alpha=0.75, edgecolor="none", zorder=2)
        ax.plot([g, g], [yy - 0.3, yy + 0.3], color=INK, lw=2.2, zorder=3)
        ax.text(max(v.max(), g) * 1.02, yy, F.n(g, 3), va="center", fontsize=7.4, color=INK)
    ax.axvline(1.0, color=RED, ls="--", lw=0.9)
    ax.text(1.0, y.max() + 0.62, ref_label, color=RED, fontsize=7.2, ha="center")
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=7.8)
    ax.set_xscale("log"); ax.set_xlabel(xlabel)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: F.n(v, 2)))
    ax.xaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_xticks([0.5, 0.7, 0.85, 1.0, 1.1])
    _grid(ax)
    ax.plot([], [], color=INK, lw=2.2, label=geo_label); ax.legend(loc="lower left", fontsize=7.2)
    return svg(fig)


def cost_gain(points, F, xlabel, ylabel, groups, width=7.2):
    """points: [(increment_fp, ratio, family_key)]; groups: {family_key: label}."""
    fig, ax = plt.subplots(figsize=(width, 3.1))
    for k, lab in groups.items():
        p = [(a, b) for a, b, kk in points if kk == k]
        if p:
            a, b = zip(*p)
            ax.scatter(a, b, s=16, color=FAM_COL[k], alpha=0.8, edgecolor="none", label=lab)
    ax.axhline(1.0, color=RED, ls="--", lw=0.9)
    ax.set_yscale("log"); ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: F.n(v, 2))); ax.yaxis.set_minor_formatter(plt.NullFormatter())
    ax.set_yticks([0.5, 0.7, 0.85, 1.0, 1.1])
    _grid(ax, "y"); ax.legend(ncol=4, fontsize=7.0, loc="lower left")
    return svg(fig)


def f6_bars(rows, F, xlabel, labels, width=7.2):
    """rows: [(family_label, v052, v053, meta)] top-down; labels: (v052, v053, meta)."""
    fig, ax = plt.subplots(figsize=(width, 0.55 * len(rows) + 0.9))
    y = np.arange(len(rows))[::-1]
    h = 0.34
    for yy, (lab, a, b, m) in zip(y, rows):
        ax.barh(yy + h / 2, a, height=h, color=BUD)
        ax.barh(yy - h / 2, b, height=h, color=LEB)
        ax.plot([m, m], [yy - 0.45, yy + 0.45], color=RED, lw=1.4)
        ax.text(a + 0.02, yy + h / 2, F.n(a, 3), va="center", fontsize=7.0, color=MUT)
        ax.text(b + 0.02, yy - h / 2, F.n(b, 3), va="center", fontsize=7.0, color=INK)
    ax.set_yticks(y); ax.set_yticklabels([r[0] for r in rows], fontsize=7.8)
    ax.set_xlabel(xlabel); ax.set_xlim(0, max(max(r[1], r[3]) for r in rows) * 1.15)
    _grid(ax); F.axis(ax, "x", 1)
    ax.barh([], [], color=BUD, label=labels[0]); ax.barh([], [], color=LEB, label=labels[1])
    ax.plot([], [], color=RED, lw=1.4, label=labels[2]); ax.legend(loc="lower right", fontsize=7.2)
    return svg(fig)
