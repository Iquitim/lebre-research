"""SVG diagrams for the LEBRE v0.3.2 research specification (bilingual). Style follows the v0.1 diagram set."""

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
C = {"ink": "#0F172A", "muted": "#64748B", "line": "#334155", "blue": "#0284C7", "blue_bg": "#F0F9FF",
     "green": "#15803D", "green_bg": "#F0FDF4", "amber": "#B45309", "amber_bg": "#FFFBEB", "red": "#DC2626",
     "red_bg": "#FEF2F2", "grey_bg": "#F8FAFC", "grey": "#CBD5E1", "violet": "#6D28D9", "violet_bg": "#F5F3FF"}


def _defs():
    return f"""<defs>
<marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="{C['line']}"/></marker>
<marker id="ab" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="{C['blue']}"/></marker>
<marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="{C['red']}"/></marker>
<marker id="ag" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="{C['green']}"/></marker>
<filter id="sh" x="-3%" y="-4%" width="106%" height="110%" filterUnits="userSpaceOnUse"><feDropShadow dx="1" dy="2" stdDeviation="2" flood-opacity="0.08"/></filter>
</defs>"""


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, title, lines=(), stroke=C["line"], fill="#FFFFFF", tsize=12.5, lsize=10.5):
    out = [f'<g filter="url(#sh)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/></g>',
           f'<text x="{x + w / 2}" y="{y + 20}" font-size="{tsize}" font-weight="700" fill="{C["ink"]}" text-anchor="middle">{_esc(title)}</text>']
    for i, ln in enumerate(lines):
        out.append(f'<text x="{x + w / 2}" y="{y + 38 + i * 14}" font-size="{lsize}" fill="{C["muted"]}" text-anchor="middle">{_esc(ln)}</text>')
    return "\n".join(out)


def arrow(x1, y1, x2, y2, color="line", dash=False, label=None, lx=None, ly=None, lcolor=None, width=1.6):
    mk = {"line": "a", "blue": "ab", "red": "ar", "green": "ag"}[color]
    col = C[color] if color != "line" else C["line"]
    d = ' stroke-dasharray="5,4"' if dash else ""
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="{width}" marker-end="url(#{mk})"{d}/>'
    if label:
        s += f'<text x="{lx if lx is not None else (x1 + x2) / 2}" y="{ly if ly is not None else (y1 + y2) / 2 - 5}" font-size="10" fill="{lcolor or col}" text-anchor="middle">{_esc(label)}</text>'
    return s


def lab(x, y, text, color=None, size=10):
    wpx = 6.1 * len(text) * size / 10
    return (f'<rect x="{x - wpx / 2 - 4}" y="{y - size}" width="{wpx + 8}" height="{size + 5}" fill="#FFFFFF" opacity="0.92"/>'
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{color or C["muted"]}" text-anchor="middle">{_esc(text)}</text>')


def svg(w, h, title, subtitle, body):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">'
            f'{_defs()}<rect width="{w}" height="{h}" fill="#FFFFFF" rx="8"/>'
            f'<text x="30" y="32" font-size="16" font-weight="700" fill="{C["ink"]}">{_esc(title)}</text>'
            f'<text x="30" y="50" font-size="12" fill="{C["muted"]}">{_esc(subtitle)}</text>{body}</svg>')


# ------------------------------------------------------------------ D1 high-level architecture
def d1(L):
    b = []
    b.append(box(30, 80, 150, 70, L["d1_in"], [L["d1_in2"], L["d1_in3"]], C["blue"], C["blue_bg"]))
    b.append(box(230, 70, 175, 58, L["d1_base"], [L["d1_base2"]]))
    b.append(box(230, 138, 175, 58, L["d1_lag"], [L["d1_lag2"]]))
    b.append(box(230, 206, 175, 72, L["d1_lat"], [L["d1_lat2"], L["d1_lat3"]]))
    b.append(f'<circle cx="465" cy="170" r="20" fill="#FFFFFF" stroke="{C["line"]}" stroke-width="1.6"/><text x="465" y="176" font-size="18" text-anchor="middle" fill="{C["ink"]}">Σ</text>')
    b.append(box(520, 140, 110, 60, "ŷ_t", [L["d1_pred"]], C["green"], C["green_bg"]))
    b.append(box(660, 140, 110, 60, "e_t = y_t − ŷ_t", [L["d1_err"]], C["amber"], C["amber_bg"], tsize=11))
    for y in (99, 167, 242):
        b.append(arrow(180, 115, 228, y))
        b.append(arrow(405, y, 447, 170))
    b.append(arrow(485, 170, 518, 170))
    b.append(arrow(630, 170, 658, 170))
    # control plane
    b.append(f'<rect x="30" y="310" width="740" height="150" rx="8" fill="{C["grey_bg"]}" stroke="{C["grey"]}" stroke-dasharray="6,4"/>')
    b.append(f'<text x="45" y="455" font-size="10.5" font-weight="700" fill="{C["muted"]}">{_esc(L["d1_ctrl"])}</text>')
    b.append(box(45, 325, 125, 105, L["d1_scr"], [L["d1_scr2"], L["d1_scr3"]], C["violet"], C["violet_bg"], 11.5, 9.5))
    b.append(box(185, 325, 140, 105, L["d1_test"], [L["d1_test2"], L["d1_test3"]], C["violet"], C["violet_bg"], 11.5, 9.5))
    b.append(box(340, 325, 135, 105, L["d1_sup"], [L["d1_sup2"], L["d1_sup3"]], C["blue"], C["blue_bg"], 11.5, 9.5))
    b.append(box(490, 325, 135, 105, L["d1_ev"], [L["d1_ev2"], L["d1_ev3"]], C["red"], C["red_bg"], 11.5, 9.5))
    b.append(box(640, 325, 120, 105, L["d1_gov"], [L["d1_gov2"], L["d1_gov3"]], C["amber"], C["amber_bg"], 11.5, 9.5))
    b.append(arrow(170, 392, 183, 392)); b.append(arrow(325, 392, 338, 392)); b.append(arrow(488, 392, 477, 392))
    b.append(arrow(715, 200, 715, 323, "red", True, L["d1_fb"], 735, 265))
    b.append(arrow(407, 323, 340, 282, "blue", True, L["d1_set"], 440, 300))
    b.append(f'<text x="400" y="480" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d1_note"])}</text>')
    return svg(800, 490, L["d1_title"], L["d1_sub"], "\n".join(b))


# ------------------------------------------------------------------ D2 lifecycle
def d2(L):
    b = []
    xs = [40, 235, 430, 625]
    names = [("DORMANT", L["d2_dor"], C["grey"], C["grey_bg"]), ("PROVISIONAL", L["d2_prov"], C["violet"], C["violet_bg"]),
             ("ACTIVE", L["d2_act"], C["green"], C["green_bg"]), ("EVICTED", L["d2_evi"], C["red"], C["red_bg"])]
    for x, (n, d, s, f) in zip(xs, names):
        b.append(box(x, 120, 150, 80, n, [d], s, f, 13, 10))
    b.append(arrow(190, 150, 233, 150, "line", False, L["d2_t1"], 212, 112))
    b.append(arrow(385, 150, 428, 150, "green", False, "log M ≥ log(p/α)", 407, 112))
    b.append(arrow(580, 150, 623, 150, "red", False, "R > h", 602, 112))
    b.append(f'<path d="M 310 202 C 310 250, 115 250, 115 204" fill="none" stroke="{C["muted"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#a)"/>')
    b.append(lab(212, 247, L["d2_fut"]))
    b.append(f'<path d="M 700 202 C 700 300, 115 300, 115 204" fill="none" stroke="{C["muted"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#a)"/>')
    b.append(lab(410, 295, L["d2_back"]))
    y0 = 345
    for i, ln in enumerate(L["d2_rules"]):
        b.append(f'<text x="40" y="{y0 + i * 17}" font-size="10.5" fill="{C["ink"]}">• {_esc(ln)}</text>')
    return svg(800, y0 + 17 * len(L["d2_rules"]) + 10, L["d2_title"], L["d2_sub"], "\n".join(b))


# ------------------------------------------------------------------ D3 promotion test episode
def d3(L):
    import math
    b = []
    x0, y0, w, h = 70, 80, 660, 250
    b.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{C["grey_bg"]}" stroke="{C["grey"]}"/>')
    thr_y = y0 + h * 0.35
    b.append(f'<line x1="{x0}" y1="{thr_y}" x2="{x0 + w}" y2="{thr_y}" stroke="{C["red"]}" stroke-dasharray="6,4" stroke-width="1.5"/>')
    b.append(f'<text x="{x0 + w - 5}" y="{thr_y - 6}" font-size="10.5" fill="{C["red"]}" text-anchor="end">log(p/α) ≈ 8.2–10.4 nats</text>')
    thr_v = 1 - (thr_y - y0) / h

    def curve(fn, col, label, stop=False):
        pts, cross = [], None
        for i in range(0, 101):
            t = i / 100
            v = fn(t)
            pts.append(f"{x0 + t * w:.1f},{y0 + h - v * h:.1f}")
            if stop and v >= thr_v:
                cross = t
                break
        lx, ly = pts[-1].split(",")
        return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" stroke-width="2.2"/>'
                f'<text x="{float(lx) - 8}" y="{float(ly) - 10}" font-size="10.5" fill="{col}" text-anchor="end">{_esc(label)}</text>'), cross
    true_fn = lambda t: 0.04 + 0.9 * (1 - math.exp(-2.6 * t)) + 0.03 * math.sin(23 * t)
    null_fn = lambda t: 0.07 + 0.05 * math.sin(13 * t) * math.exp(-t) + 0.02 * math.sin(41 * t)
    s_true, ct = curve(true_fn, C["green"], L["d3_true"], stop=True)
    s_null, _ = curve(null_fn, C["muted"], L["d3_null"])
    b.append(s_true); b.append(s_null)
    cross = x0 + (ct if ct is not None else 0.5) * w
    b.append(f'<line x1="{cross}" y1="{y0}" x2="{cross}" y2="{y0 + h}" stroke="{C["green"]}" stroke-dasharray="3,3"/>')
    b.append(f'<text x="{cross + 6}" y="{thr_y + 16}" font-size="10" fill="{C["green"]}">{_esc(L["d3_promo"])}</text>')
    b.append(f'<text x="{x0 + w / 2}" y="{y0 + h + 22}" font-size="11" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d3_x"])}</text>')
    b.append(f'<text x="{x0 - 12}" y="{y0 + h / 2}" font-size="11" fill="{C["muted"]}" text-anchor="middle" transform="rotate(-90 {x0 - 12} {y0 + h / 2})">log M_t</text>')
    b.append(f'<text x="400" y="{y0 + h + 48}" font-size="11" fill="{C["ink"]}" text-anchor="middle">log M_t = τS²/(2(1+τQ)) − ½·log(1+τQ),  S = Σ e·φ,  Q = Σ (e·φ)²</text>')
    b.append(f'<text x="400" y="{y0 + h + 66}" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d3_note"])}</text>')
    return svg(800, 420, L["d3_title"], L["d3_sub"], "\n".join(b))


# ------------------------------------------------------------------ D4 eviction CUSUM + rent
def d4(L):
    b = []
    x0, y0, w, h = 70, 80, 660, 230
    b.append(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" fill="{C["grey_bg"]}" stroke="{C["grey"]}"/>')
    thr = y0 + 40
    b.append(f'<line x1="{x0}" y1="{thr}" x2="{x0 + w}" y2="{thr}" stroke="{C["red"]}" stroke-dasharray="6,4" stroke-width="1.5"/>')
    b.append(f'<text x="{x0 + 8}" y="{thr - 6}" font-size="10.5" fill="{C["red"]}">h = log(ARL) = log 6000 ≈ 8.70</text>')
    # piecewise: useful (R≈0), silence (flat, gated), change (ramp to threshold)
    seg = [(0.0, 0.0), (0.30, 0.02), (0.31, 0.0), (0.45, 0.01)]
    pts = [(x0 + t * w, y0 + h - v * (h - 40)) for t, v in [(0, 0), (0.15, 0.03), (0.2, 0), (0.35, 0.02), (0.4, 0),
                                                           (0.42, 0), (0.62, 0), (0.66, 0.05), (0.70, 0.35), (0.74, 0.7), (0.765, 1.0)]]
    b.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{C["blue"]}" stroke-width="2.2"/>')
    b.append(f'<rect x="{x0 + 0.42 * w}" y="{y0}" width="{0.2 * w}" height="{h}" fill="#E2E8F0" opacity="0.6"/>')
    b.append(f'<text x="{x0 + 0.52 * w}" y="{y0 + h / 2}" font-size="10.5" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d4_sil"])}</text>')
    b.append(f'<text x="{x0 + 0.52 * w}" y="{y0 + h / 2 + 14}" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d4_sil2"])}</text>')
    b.append(f'<line x1="{x0 + 0.64 * w}" y1="{y0}" x2="{x0 + 0.64 * w}" y2="{y0 + h}" stroke="{C["amber"]}" stroke-dasharray="3,3"/>')
    b.append(f'<text x="{x0 + 0.645 * w + 4}" y="{y0 + h - 8}" font-size="10" fill="{C["amber"]}">{_esc(L["d4_chg"])}</text>')
    b.append(f'<text x="{x0 + 0.765 * w + 6}" y="{thr + 16}" font-size="10" fill="{C["red"]}">{_esc(L["d4_evict"])}</text>')
    b.append(f'<text x="{x0 + 0.2 * w}" y="{y0 + h - 30}" font-size="10" fill="{C["blue"]}" text-anchor="middle">{_esc(L["d4_useful"])}</text>')
    b.append(f'<text x="400" y="{y0 + h + 26}" font-size="11" fill="{C["ink"]}" text-anchor="middle">R_t = max(0, R_(t−1) − ℓ_t + r·min(1, φ²/v_ref)),   ℓ_t = c(2e + c)/(2σ̂²)</text>')
    b.append(f'<text x="400" y="{y0 + h + 44}" font-size="10" fill="{C["muted"]}" text-anchor="middle">{_esc(L["d4_note"])}</text>')
    return svg(800, 380, L["d4_title"], L["d4_sub"], "\n".join(b))


# ------------------------------------------------------------------ D5 latent innovations pathway
def d5(L):
    b = []
    b.append(box(30, 90, 150, 60, "e_t", [L["d5_e"]], C["amber"], C["amber_bg"]))
    b.append(box(30, 190, 150, 60, "x_(t,i)", [L["d5_x"]], C["blue"], C["blue_bg"]))
    b.append(box(225, 80, 170, 80, L["d5_u"], ["u_t = e_t + Σ c_latent", "ũ_t = u_t / σ̂_t"]))
    b.append(box(440, 80, 170, 80, L["d5_s"], ["s_t = p·s_(t−1) + (1−p)·ũ_t", "p ∈ {0, .5, .8, .95}"], C["violet"], C["violet_bg"], 12, 10))
    b.append(box(440, 180, 170, 80, L["d5_q"], ["q_t = p·q_(t−1) + (1−p)·x_(t,i)", L["d5_q2"]], C["violet"], C["violet_bg"], 12, 10))
    b.append(box(650, 125, 125, 80, L["d5_out"], ["θ_s·s + θ_q·q", L["d5_out2"]], C["green"], C["green_bg"], 12, 10))
    b.append(arrow(180, 120, 223, 120)); b.append(arrow(395, 120, 438, 120)); b.append(arrow(180, 220, 438, 220))
    b.append(arrow(610, 120, 648, 155)); b.append(arrow(610, 220, 648, 180))
    b.append(f'<text x="400" y="300" font-size="11" fill="{C["ink"]}" text-anchor="middle">{_esc(L["d5_eq"])}</text>')
    for i, ln in enumerate(L["d5_notes"]):
        b.append(f'<text x="40" y="{330 + i * 17}" font-size="10.5" fill="{C["ink"]}">• {_esc(ln)}</text>')
    return svg(800, 340 + 17 * len(L["d5_notes"]), L["d5_title"], L["d5_sub"], "\n".join(b))


def all_diagrams(L):
    return {"D1": d1(L), "D2": d2(L), "D3": d3(L), "D4": d4(L), "D5": d5(L)}
