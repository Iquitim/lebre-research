"""SVG diagrams for the LEBRE v0.51 specification. Every label comes from the language pack (PT-BR or EN)."""
import math

from v032_diagrams import C, arrow, box, lab, svg, _esc


# ------------------------------------------------------------------ D1 architecture overview
def d1(L):
    b = []
    b.append(box(24, 150, 150, 84, L["d1_in"], [L["d1_in2"], L["d1_in3"]], C["blue"], C["blue_bg"]))
    b.append(box(236, 72, 250, 100, L["d1_S"], [L["d1_S2"], L["d1_S3"], L["d1_S4"]], C["violet"], C["violet_bg"]))
    b.append(box(236, 212, 250, 100, L["d1_M"], [L["d1_M2"], L["d1_M3"], L["d1_M4"]], C["green"], C["green_bg"]))
    b.append(box(548, 142, 170, 100, L["d1_C"], [L["d1_C2"], L["d1_C3"], L["d1_C4"]], C["amber"], C["amber_bg"]))
    b.append(box(770, 72, 170, 70, L["d1_out"], [L["d1_out2"]], C["blue"], C["blue_bg"]))
    b.append(box(770, 162, 170, 70, L["d1_int"], [L["d1_int2"]], C["blue"], C["blue_bg"]))
    b.append(box(770, 252, 170, 70, L["d1_exp"], [L["d1_exp2"]], C["blue"], C["blue_bg"]))
    b.append(arrow(174, 180, 234, 125)); b.append(arrow(174, 205, 234, 262))
    b.append(arrow(486, 122, 546, 175, label="ŷ_S", lx=520, ly=138)); b.append(arrow(486, 262, 546, 212, label="ŷ_M", lx=520, ly=252))
    b.append(arrow(718, 175, 768, 108)); b.append(arrow(718, 192, 768, 197)); b.append(arrow(718, 210, 768, 285))
    b.append(f'<path d="M 633 244 L 633 360 L 360 360 L 360 314" fill="none" stroke="{C["red"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#ar)"/>')
    b.append(f'<path d="M 360 360 L 205 360 L 205 92 L 234 92" fill="none" stroke="{C["red"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#ar)"/>')
    b.append(lab(540, 374, L["d1_fb"], C["red"]))
    b.append(f'<path d="M 633 142 L 633 110 L 490 110" fill="none" stroke="{C["amber"]}" stroke-width="1.4" stroke-dasharray="3,3" marker-end="url(#a)"/>')
    b.append(lab(600, 104, L["d1_dorm"], C["amber"], 9.5))
    b.append(f'<text x="30" y="400" font-size="10.5" fill="{C["muted"]}">{_esc(L["d1_note"])}</text>')
    return svg(965, 412, L["d1_title"], L["d1_sub"], "".join(b))


# ------------------------------------------------------------------ D2 per-step flow
def d2(L):
    steps = L["d2_steps"]
    b = []
    x, w, h = 30, 160, 92
    for i, (t, s1, s2) in enumerate(steps):
        xx = x + i * 187
        col = [C["blue"], C["violet"], C["amber"], C["green"], C["red"]][i]
        fill = [C["blue_bg"], C["violet_bg"], C["amber_bg"], C["green_bg"], C["red_bg"]][i]
        b.append(box(xx, 80, w, h, f"{i + 1}. {t}", [s1, s2], col, fill, tsize=11.5, lsize=9.6))
        if i < len(steps) - 1:
            b.append(arrow(xx + w, 126, xx + 185, 126))
    b.append(f'<rect x="30" y="196" width="908" height="54" rx="6" fill="{C["grey_bg"]}" stroke="{C["grey"]}"/>')
    b.append(f'<text x="484" y="218" font-size="11" font-weight="700" fill="{C["ink"]}" text-anchor="middle">{_esc(L["d2_caus"])}</text>')
    b.append(f'<text x="484" y="238" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d2_caus2"])}</text>')
    return svg(965, 265, L["d2_title"], L["d2_sub"], "".join(b))


# ------------------------------------------------------------------ D3 memory expert
def d3(L):
    b = []
    x0, x1, y0 = 60, 900, 210
    s = 24
    n = 2 * s + 6
    xs = lambda i: x0 + (x1 - x0) * i / (n - 1)
    ys = [y0 - 60 - 45 * math.sin(2 * math.pi * i / s) - 0.35 * i for i in range(n)]
    pts = " ".join(f"{xs(i):.1f},{ys[i]:.1f}" for i in range(n - 1))
    b.append(f'<polyline points="{pts}" fill="none" stroke="{C["line"]}" stroke-width="1.8"/>')
    t = n - 1
    b.append(f'<circle cx="{xs(t):.1f}" cy="{ys[t]:.1f}" r="6" fill="none" stroke="{C["red"]}" stroke-width="2" stroke-dasharray="3,2"/>')
    b.append(f'<text x="{xs(t):.1f}" y="{ys[t] - 14:.1f}" font-size="11" fill="{C["red"]}" text-anchor="middle">{_esc(L["d3_target"])}</text>')
    marks = [(t - 1, L["d3_last"], C["blue"]), (t - 2, L["d3_prev"], C["blue"]), (t - s, L["d3_seas"], C["green"]),
             (t - s + 1, L["d3_seas1"], C["green"])]
    for k, (i, txt, col) in enumerate(marks):
        b.append(f'<circle cx="{xs(i):.1f}" cy="{ys[i]:.1f}" r="4.5" fill="{col}"/>')
        yy = y0 + 22 + (k % 2) * 16
        b.append(f'<line x1="{xs(i):.1f}" y1="{ys[i] + 5:.1f}" x2="{xs(i):.1f}" y2="{yy - 11}" stroke="{col}" stroke-width="0.8" stroke-dasharray="2,2"/>')
        b.append(f'<text x="{xs(i):.1f}" y="{yy}" font-size="10" fill="{col}" text-anchor="middle">{_esc(txt)}</text>')
    for c in range(3):
        xa, xb = xs(c * s), xs(min((c + 1) * s, n - 1))
        b.append(f'<line x1="{xa:.1f}" y1="72" x2="{xa:.1f}" y2="{y0}" stroke="{C["grey"]}" stroke-dasharray="3,3"/>')
    b.append(f'<text x="{(xs(0) + xs(s)) / 2:.1f}" y="76" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d3_cycle"])} k−2</text>')
    b.append(f'<text x="{(xs(s) + xs(2 * s)) / 2:.1f}" y="76" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d3_cycle"])} k−1</text>')
    b.append(f'<rect x="60" y="262" width="840" height="112" rx="6" fill="{C["green_bg"]}" stroke="{C["green"]}"/>')
    for i, ln in enumerate(L["d3_feats"]):
        b.append(f'<text x="80" y="{284 + i * 17}" font-size="10.4" fill="{C["ink"]}">{_esc(ln)}</text>')
    return svg(965, 390, L["d3_title"], L["d3_sub"], "".join(b))


# ------------------------------------------------------------------ D4 structural lifecycle
def d4(L):
    b = []
    b.append(box(30, 100, 150, 74, L["d4_dor"], [L["d4_dor2"]], C["grey"], C["grey_bg"]))
    b.append(box(270, 100, 150, 74, L["d4_prov"], [L["d4_prov2"]], C["amber"], C["amber_bg"]))
    b.append(box(525, 100, 150, 74, L["d4_act"], [L["d4_act2"]], C["green"], C["green_bg"]))
    b.append(box(780, 100, 150, 74, L["d4_evi"], [L["d4_evi2"]], C["red"], C["red_bg"]))
    b.append(arrow(180, 137, 268, 137)); b.append(lab(224, 90, L["d4_t1"], None, 9.5))
    b.append(arrow(420, 137, 523, 137, "green")); b.append(lab(472, 90, L["d4_t2"], C["green"], 9.5))
    b.append(arrow(675, 137, 778, 137, "red")); b.append(lab(727, 90, L["d4_t3"], C["red"], 9.5))
    b.append(f'<path d="M 345 174 L 345 205 L 105 205 L 105 176" fill="none" stroke="{C["line"]}" stroke-width="1.3" stroke-dasharray="5,4" marker-end="url(#a)"/>')
    b.append(lab(232, 216, L["d4_fut"], None, 9.5))
    b.append(f'<path d="M 855 174 L 855 236 L 105 236 L 105 207" fill="none" stroke="{C["red"]}" stroke-width="1.3" stroke-dasharray="5,4"/>')
    b.append(lab(480, 247, L["d4_back"], C["red"], 9.5))
    b.append(f'<rect x="30" y="262" width="905" height="96" rx="6" fill="{C["amber_bg"]}" stroke="{C["amber"]}"/>')
    for i, ln in enumerate(L["d4_gates"]):
        b.append(f'<text x="46" y="{282 + i * 17}" font-size="10.3" fill="{C["ink"]}">{_esc(ln)}</text>')
    return svg(965, 372, L["d4_title"], L["d4_sub"], "".join(b))


# ------------------------------------------------------------------ D5 accuracy chart (geo-mean NMSE relative to NLinear)
def d5(L, rows, dec=".", clip=3.2):
    """rows: list of (label, ratio, highlight); bars longer than `clip` are truncated and labelled."""
    b = []
    x0, y0, bw, rh = 250, 84, 560, 21
    vmax = clip
    for i, (name, r, hi) in enumerate(rows):
        y = y0 + i * rh
        w = bw * min(r, vmax) / vmax
        col = C["violet"] if hi else (C["blue"] if not name.startswith("Chronos") else C["amber"])
        b.append(f'<text x="{x0 - 8}" y="{y + 13}" font-size="10.5" fill="{C["ink"]}" text-anchor="end" font-weight="{700 if hi else 400}">{_esc(name)}</text>')
        b.append(f'<rect x="{x0}" y="{y + 3}" width="{w:.1f}" height="{rh - 7}" rx="2" fill="{col}" opacity="{1 if hi else 0.75}"/>')
        txt = f"{r:.2f}".replace(".", dec) + (" ►" if r > vmax else "")
        b.append(f'<text x="{x0 + w + 6:.1f}" y="{y + 13}" font-size="10" fill="{C["muted"]}">{txt}</text>')
    xr = x0 + bw * 1.0 / vmax
    yb = y0 + len(rows) * rh
    b.append(f'<line x1="{xr:.1f}" y1="{y0 - 6}" x2="{xr:.1f}" y2="{yb}" stroke="{C["red"]}" stroke-dasharray="4,3"/>')
    b.append(f'<text x="{xr + 6:.1f}" y="{y0 - 4}" font-size="10" fill="{C["red"]}">{_esc(L["d5_ref"])}</text>')
    b.append(f'<text x="{x0}" y="{yb + 22}" font-size="10" fill="{C["muted"]}">{_esc(L["d5_note"])}</text>')
    return svg(965, yb + 36, L["d5_title"], L["d5_sub"], "".join(b))


# ------------------------------------------------------------------ D6 cost chart (log scale)
def sup(k):
    return str(k).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


def d6(L, rows, dec="."):
    """rows: list of (label, fp_per_step, estimated?, highlight)"""
    b = []
    x0, y0, bw, rh = 250, 76, 600, 26
    lo, hi_ = 1, 10
    for k in range(lo, hi_ + 1):
        x = x0 + bw * (k - lo) / (hi_ - lo)
        b.append(f'<line x1="{x:.1f}" y1="{y0 - 8}" x2="{x:.1f}" y2="{y0 + len(rows) * rh}" stroke="{C["grey"]}" stroke-width="0.6"/>')
        b.append(f'<text x="{x:.1f}" y="{y0 - 12}" font-size="9.5" fill="{C["muted"]}" text-anchor="middle">10{sup(k)}</text>')
    for i, (name, v, est, hi) in enumerate(rows):
        y = y0 + i * rh
        w = bw * (math.log10(max(v, 10)) - lo) / (hi_ - lo)
        col = C["violet"] if hi else (C["amber"] if est else C["blue"])
        dash = ' stroke="#B45309" stroke-dasharray="3,2" fill-opacity="0.35"' if est else ""
        b.append(f'<text x="{x0 - 8}" y="{y + 16}" font-size="10.5" fill="{C["ink"]}" text-anchor="end" font-weight="{700 if hi else 400}">{_esc(name)}</text>')
        b.append(f'<rect x="{x0}" y="{y + 5}" width="{w:.1f}" height="{rh - 10}" rx="2" fill="{col}"{dash}/>')
        mant, ex = f"{v:.0e}".split("e+")
        txt = f"~{mant}·10{sup(int(ex))}" if est else f"{v:,.0f}".replace(",", "." if dec == "," else ",")
        b.append(f'<text x="{x0 + w + 6:.1f}" y="{y + 16}" font-size="10" fill="{C["muted"]}">{_esc(txt + (" " + L["d6_est"] if est else ""))}</text>')
    yb = y0 + len(rows) * rh
    b.append(f'<text x="{x0}" y="{yb + 20}" font-size="10" fill="{C["muted"]}">{_esc(L["d6_note"])}</text>')
    return svg(965, yb + 34, L["d6_title"], L["d6_sub"], "".join(b))


def all_diagrams(L, acc_rows, cost_rows, dec="."):
    return {"D1": d1(L), "D2": d2(L), "D3": d3(L), "D4": d4(L), "D5": d5(L, acc_rows, dec), "D6": d6(L, cost_rows, dec)}
