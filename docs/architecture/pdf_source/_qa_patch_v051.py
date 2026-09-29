"""one-off QA patch for the v0.51 specification sources (kept for provenance)."""
import os

H = os.path.dirname(os.path.abspath(__file__))

# ---------------- diagrams
p = os.path.join(H, 'v051_diagrams.py'); s = open(p, encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)


rep('''    b.append(f'<path d="M 855 322 L 855 360 L 360 360 L 360 314" fill="none" stroke="{C["red"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#ar)"/>')
    b.append(f'<path d="M 360 360 L 150 360 L 150 30 L 360 30 L 360 70" fill="none" stroke="{C["red"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#ar)"/>')''',
    '''    b.append(f'<path d="M 633 244 L 633 360 L 360 360 L 360 314" fill="none" stroke="{C["red"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#ar)"/>')
    b.append(f'<path d="M 360 360 L 205 360 L 205 92 L 234 92" fill="none" stroke="{C["red"]}" stroke-width="1.5" stroke-dasharray="5,4" marker-end="url(#ar)"/>')''')
rep('''    b.append(lab(600, 356, L["d1_fb"], C["red"]))''', '''    b.append(lab(540, 374, L["d1_fb"], C["red"]))''')
rep('''    b.append(f'<text x="30" y="392" font-size="10.5" fill="{C["muted"]}">{_esc(L["d1_note"])}</text>')
    return svg(965, 405,''', '''    b.append(f'<text x="30" y="400" font-size="10.5" fill="{C["muted"]}">{_esc(L["d1_note"])}</text>')
    return svg(965, 412,''')
rep('''    b.append(box(30, 100, 160, 74, L["d4_dor"], [L["d4_dor2"]], C["grey"], C["grey_bg"]))
    b.append(box(270, 100, 170, 74, L["d4_prov"], [L["d4_prov2"]], C["amber"], C["amber_bg"]))
    b.append(box(520, 100, 170, 74, L["d4_act"], [L["d4_act2"]], C["green"], C["green_bg"]))
    b.append(box(770, 100, 165, 74, L["d4_evi"], [L["d4_evi2"]], C["red"], C["red_bg"]))
    b.append(arrow(190, 137, 268, 137, label=L["d4_t1"], ly=128))
    b.append(arrow(440, 137, 518, 137, "green", label=L["d4_t2"], ly=128))
    b.append(arrow(690, 137, 768, 137, "red", label=L["d4_t3"], ly=128))''', '''    b.append(box(30, 100, 150, 74, L["d4_dor"], [L["d4_dor2"]], C["grey"], C["grey_bg"]))
    b.append(box(270, 100, 150, 74, L["d4_prov"], [L["d4_prov2"]], C["amber"], C["amber_bg"]))
    b.append(box(525, 100, 150, 74, L["d4_act"], [L["d4_act2"]], C["green"], C["green_bg"]))
    b.append(box(780, 100, 150, 74, L["d4_evi"], [L["d4_evi2"]], C["red"], C["red_bg"]))
    b.append(arrow(180, 137, 268, 137)); b.append(lab(224, 90, L["d4_t1"], None, 9.5))
    b.append(arrow(420, 137, 523, 137, "green")); b.append(lab(472, 90, L["d4_t2"], C["green"], 9.5))
    b.append(arrow(675, 137, 778, 137, "red")); b.append(lab(727, 90, L["d4_t3"], C["red"], 9.5))''')
rep('''    b.append(f'<path d="M 355 174 L 355 205 L 110 205 L 110 176" fill="none" stroke="{C["line"]}" stroke-width="1.3" stroke-dasharray="5,4" marker-end="url(#a)"/>')''',
    '''    b.append(f'<path d="M 345 174 L 345 205 L 105 205 L 105 176" fill="none" stroke="{C["line"]}" stroke-width="1.3" stroke-dasharray="5,4" marker-end="url(#a)"/>')''')
rep('''    b.append(f'<path d="M 852 174 L 852 236 L 110 236 L 110 207" fill="none" stroke="{C["red"]}" stroke-width="1.3" stroke-dasharray="5,4"/>')''',
    '''    b.append(f'<path d="M 855 174 L 855 236 L 105 236 L 105 207" fill="none" stroke="{C["red"]}" stroke-width="1.3" stroke-dasharray="5,4"/>')''')
rep('''def d5(L, rows):
    """rows: list of (label, ratio, highlight)"""
    b = []
    x0, y0, bw, rh = 250, 70, 560, 21
    vmax = max(r for _, r, _ in rows) * 1.08''', '''def d5(L, rows, dec=".", clip=3.2):
    """rows: list of (label, ratio, highlight); bars longer than `clip` are truncated and labelled."""
    b = []
    x0, y0, bw, rh = 250, 84, 560, 21
    vmax = clip''')
rep('''        w = bw * r / vmax
        col = C["violet"] if hi else (C["blue"] if not name.startswith("Chronos") else C["amber"])
        b.append(f'<text x="{x0 - 8}" y="{y + 13}" font-size="10.5" fill="{C["ink"]}" text-anchor="end" font-weight="{700 if hi else 400}">{_esc(name)}</text>')
        b.append(f'<rect x="{x0}" y="{y + 3}" width="{w:.1f}" height="{rh - 7}" rx="2" fill="{col}" opacity="{1 if hi else 0.75}"/>')
        b.append(f'<text x="{x0 + w + 6:.1f}" y="{y + 13}" font-size="10" fill="{C["muted"]}">{r:.2f}</text>')''', '''        w = bw * min(r, vmax) / vmax
        col = C["violet"] if hi else (C["blue"] if not name.startswith("Chronos") else C["amber"])
        b.append(f'<text x="{x0 - 8}" y="{y + 13}" font-size="10.5" fill="{C["ink"]}" text-anchor="end" font-weight="{700 if hi else 400}">{_esc(name)}</text>')
        b.append(f'<rect x="{x0}" y="{y + 3}" width="{w:.1f}" height="{rh - 7}" rx="2" fill="{col}" opacity="{1 if hi else 0.75}"/>')
        txt = f"{r:.2f}".replace(".", dec) + (" ►" if r > vmax else "")
        b.append(f'<text x="{x0 + w + 6:.1f}" y="{y + 13}" font-size="10" fill="{C["muted"]}">{txt}</text>')''')
rep('''    b.append(f'<text x="{xr:.1f}" y="{y0 - 10}" font-size="10" fill="{C["red"]}" text-anchor="middle">{_esc(L["d5_ref"])}</text>')''',
    '''    b.append(f'<text x="{xr + 6:.1f}" y="{y0 - 4}" font-size="10" fill="{C["red"]}">{_esc(L["d5_ref"])}</text>')''')
rep('''        b.append(f'<text x="{x:.1f}" y="{y0 - 12}" font-size="9.5" fill="{C["muted"]}" text-anchor="middle">10^{k}</text>')''',
    '''        b.append(f'<text x="{x:.1f}" y="{y0 - 12}" font-size="9.5" fill="{C["muted"]}" text-anchor="middle">10{sup(k)}</text>')''')
rep('''        txt = f"~{v:.0e}".replace("e+0", "·10^").replace("e+", "·10^") if est else f"{v:,.0f}"''',
    '''        mant, ex = f"{v:.0e}".split("e+")
        txt = f"~{mant}·10{sup(int(ex))}" if est else f"{v:,.0f}".replace(",", "." if dec == "," else ",")''')
rep('''def d6(L, rows):''', '''def sup(k):
    return str(k).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))


def d6(L, rows, dec="."):''')
rep('''def all_diagrams(L, acc_rows, cost_rows):
    return {"D1": d1(L), "D2": d2(L), "D3": d3(L), "D4": d4(L), "D5": d5(L, acc_rows), "D6": d6(L, cost_rows)}''',
    '''def all_diagrams(L, acc_rows, cost_rows, dec="."):
    return {"D1": d1(L), "D2": d2(L), "D3": d3(L), "D4": d4(L), "D5": d5(L, acc_rows, dec), "D6": d6(L, cost_rows, dec)}''')
open(p, 'w', encoding='utf-8').write(s)

# ---------------- build
p = os.path.join(H, 'build_v051_spec.py'); s = open(p, encoding='utf-8').read()
rep('    D = all_diagrams(L["diag"], acc, cost)', '    D = all_diagrams(L["diag"], acc, cost, "," if lang == "pt" else ".")')
open(p, 'w', encoding='utf-8').write(s)

# ---------------- text
p = os.path.join(H, 'v051_text.py'); s = open(p, encoding='utf-8').read()
rep('''$$G_{{p}}\\\\leftarrow G_{{p}}+a\\\\,\\\\big[(y_t-y_{{t-1}})-G_{{p}}\\\\big],\\\\;a=0.1;\\\\qquad m_t\\\\leftarrow m_{{t-1}}+0.01\\\\,(y_t-m_{{t-1}});\\\\qquad \\\\mathbf w\\\\leftarrow''',
    '''$$G_{{p}}\\\\leftarrow G_{{p}}+a\\\\,\\\\big[(y_t-y_{{t-1}})-G_{{p}}\\\\big],\\\\;a=0.1;\\\\qquad m_t\\\\leftarrow m_{{t-1}}+0.01\\\\,(y_t-m_{{t-1}})$$
$$\\\\mathbf w\\\\leftarrow''')
rep('''\\\\text{{intervalo/interval}}=\\\\hat y_t\\\\pm\\\\hat q_t''', '''\\\\text{{{T("intervalo", "interval")}}}=\\\\hat y_t\\\\pm\\\\hat q_t''')
rep('''LABEL_PT_EVT = [("PROVISIONAL->ACTIVE", "promovido"), ("ACTIVE->EVICTED\\\\(replaced\\\\)", "removido (substituído)"), ("ACTIVE->EVICTED", "removido")]''',
    '''LABEL_PT_EVT = [(r"\\\\[estrutural, peso ([0-9.]+)\\\\]", r"Estrutural (peso \\\\1):"), (r"\\\\[memória, peso ([0-9.]+)\\\\] memória: ", r"Memória (peso \\\\1): "),
                ("PROVISIONAL->ACTIVE", "promovido"), ("ACTIVE->EVICTED\\\\(replaced\\\\)", "removido (substituído)"),
                ("ACTIVE->EVICTED\\\\(coupled\\\\)", "removido (acoplado)"), ("ACTIVE->EVICTED", "removido"), (r"(\\\\d)\\\\.(\\\\d)", r"\\\\1,\\\\2")]''')
rep('''LABEL_EN = [(r"\\\\[estrutural, peso ([0-9.]+)\\\\]", r"[structural, weight \\\\1]"), (r"\\\\[memória, peso ([0-9.]+)\\\\]", r"[memory, weight \\\\1]"),''',
    '''LABEL_EN = [(r"\\\\[estrutural, peso ([0-9.]+)\\\\]", r"Structural (weight \\\\1):"), (r"\\\\[memória, peso ([0-9.]+)\\\\] ", r"Memory (weight \\\\1): "),''')
for a, b in [('("memória: último valor y\\\\(t-1\\\\)", "memory: last value y(t-1)")', '("memória: último valor y\\\\(t-1\\\\)", "last value y(t-1)")'),
             ('("memória: reversão à média", "memory: mean reversion")', '("memória: reversão à média", "mean reversion")'),
             ('("memória: incremento recente", "memory: recent increment")', '("memória: incremento recente", "recent increment")'),
             ('("memória: sazonal: ", "memory: seasonal: ")', '("memória: sazonal: ", "seasonal: ")'),
             ('("memória: incremento de um ciclo atrás", "memory: increment one cycle ago")', '("memória: incremento de um ciclo atrás", "increment one cycle ago")'),
             ('("memória: perfil sazonal de incrementos", "memory: seasonal profile of increments")', '("memória: perfil sazonal de incrementos", "seasonal profile of increments")'),
             ('("ACTIVE->EVICTED\\\\(replaced\\\\)", "evicted (replaced)"), ("ACTIVE->EVICTED", "evicted")]',
              '("ACTIVE->EVICTED\\\\(replaced\\\\)", "evicted (replaced)"), ("ACTIVE->EVICTED\\\\(coupled\\\\)", "evicted (coupled)"), ("ACTIVE->EVICTED", "evicted")]')]:
    rep(a, b)
rep('''T(f'Previsão {n(i9["y_hat"], 3)} (observado {n(i9["y"], 3)}), w<sub>S</sub>''', '''T(f'Previsão {n(i9["y_hat"], 3)} ± {n(i9["interval"], 3)} (observado {n(i9["y"], 3)}), w<sub>S</sub>''')
rep('''f'Forecast {n(i9["y_hat"], 3)} (observed {n(i9["y"], 3)}), w<sub>S</sub>''', '''f'Forecast {n(i9["y_hat"], 3)} ± {n(i9["interval"], 3)} (observed {n(i9["y"], 3)}), w<sub>S</sub>''')
rep('''        rows_m = [(MN[m], n(ch.loc[m, "fp"], 0), n(ch.loc[m, "peak"], 0), (n(ch.loc[m, "mem"] / 1024, 2) + " KB") if ch.loc[m, "mem"] > 0 else "—", n(ch.loc[m, "ms"], 3))''',
    '''        est = "(est.)"
        FMX = {"CHRONOS_BOLT_TINY": ("~6·10⁸ " + est, "~36 MB"), "CHRONOS_BOLT_SMALL": ("~3·10⁹ " + est, "~190 MB"),
               "CHRONOS2": ("~8·10⁹ " + est, "~480 MB"), "CHRONOS2_COV": ("~10¹⁰ " + est, "~480 MB")}
        rows_m = [(MN[m], FMX[m][0] if m in FMX else n(ch.loc[m, "fp"], 0), "—" if m in FMX else n(ch.loc[m, "peak"], 0),
                   FMX[m][1] if m in FMX else n(ch.loc[m, "mem"] / 1024, 2) + " KB", n(ch.loc[m, "ms"], 3))''')
rep('''<h2>9.3 {T('Critérios pré-registrados e resultado', 'Pre-registered criteria and outcome')}</h2>
{tbl(acc, crit)}''', '''<div class="no-break"><h2>9.3 {T('Critérios pré-registrados e resultado', 'Pre-registered criteria and outcome')}</h2>
{tbl(acc, crit)}</div>''')
rep('''        rk = [(i + 1, MN.get(m, m), n(v, 2)) for i, (m, v) in enumerate(rank.items())]''',
    '''        pos = rank.rank(method="min").astype(int)
        rk = [(f"{pos[m]}º" if P else f"{pos[m]}", MN.get(m, m), n(v, 2)) for m, v in rank.items()]''')
rep('''        out.append(f"""<h1>13. {toc[12]}</h1><ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>""")
        return out''', '''        out.append(f"""<h1>13. {toc[12]}</h1><ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>""")
        if P:
            fix = lambda m: re.sub(r"(?<=\\d)\\.(?=\\d)", "{,}", m.group(0))
            out = [re.sub(r'<div class="math-box">.*?</div>', fix, o, flags=re.S) for o in out]
        return out''')
rep('''meta=[("Custo", "~120 operações/passo; ~1,4 KB"),''', '''meta=[("Custo", "~121 operações/passo; ~1,3 KB"),''')
rep('''meta=[("Cost", "~120 operations/step; ~1.4 KB"),''', '''meta=[("Cost", "~121 operations/step; ~1.3 KB"),''')
rep("e ~1,4 KB de estado", "e ~1,3 KB de estado")
rep("and ~1.4 KB of state", "and ~1.3 KB of state")
open(p, 'w', encoding='utf-8').write(s)
print("ok")
