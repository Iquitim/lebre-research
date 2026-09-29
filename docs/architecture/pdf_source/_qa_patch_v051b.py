"""one-off QA patch (part 2) for v051_text.py (kept for provenance)."""
import os

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v051_text.py")
s = open(p, encoding="utf-8").read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b)


rep("""T(f'Previsão {n(i9["y_hat"], 3)} (observado {n(i9["y"], 3)}), w<sub>S</sub>""",
    """T(f'Previsão {n(i9["y_hat"], 3)} ± {n(i9["interval"], 3)} (observado {n(i9["y"], 3)}), w<sub>S</sub>""")
rep("""f'Forecast {n(i9["y_hat"], 3)} (observed {n(i9["y"], 3)}), w<sub>S</sub>""",
    """f'Forecast {n(i9["y_hat"], 3)} ± {n(i9["interval"], 3)} (observed {n(i9["y"], 3)}), w<sub>S</sub>""")
rep("""        rows_m = [(MN[m], n(ch.loc[m, "fp"], 0), n(ch.loc[m, "peak"], 0), (n(ch.loc[m, "mem"] / 1024, 2) + " KB") if ch.loc[m, "mem"] > 0 else "—", n(ch.loc[m, "ms"], 3))""",
    """        est = "(est.)"
        FMX = {"CHRONOS_BOLT_TINY": ("~6·10⁸ " + est, "~36 MB"), "CHRONOS_BOLT_SMALL": ("~3·10⁹ " + est, "~190 MB"),
               "CHRONOS2": ("~8·10⁹ " + est, "~480 MB"), "CHRONOS2_COV": ("~10¹⁰ " + est, "~480 MB")}
        rows_m = [(MN[m], FMX[m][0] if m in FMX else n(ch.loc[m, "fp"], 0), "—" if m in FMX else n(ch.loc[m, "peak"], 0),
                   FMX[m][1] if m in FMX else n(ch.loc[m, "mem"] / 1024, 2) + " KB", n(ch.loc[m, "ms"], 3))""")
rep("""<h2>9.3 {T('Critérios pré-registrados e resultado', 'Pre-registered criteria and outcome')}</h2>
{tbl(acc, crit)}""", """<div class="no-break"><h2>9.3 {T('Critérios pré-registrados e resultado', 'Pre-registered criteria and outcome')}</h2>
{tbl(acc, crit)}</div>""")
rep("""        rk = [(i + 1, MN.get(m, m), n(v, 2)) for i, (m, v) in enumerate(rank.items())]""",
    """        pos = rank.rank(method="min").astype(int)
        rk = [(f"{pos[m]}º" if P else f"{pos[m]}", MN.get(m, m), n(v, 2)) for m, v in rank.items()]""")
rep("""        out.append(f\"\"\"<h1>13. {toc[12]}</h1><ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>\"\"\")
        return out""", """        out.append(f\"\"\"<h1>13. {toc[12]}</h1><ol class="refs">{''.join(f'<li>{r}</li>' for r in REFS)}</ol>\"\"\")
        if P:
            fix = lambda mm: re.sub(r"(?<=\\d)\\.(?=\\d)", "{,}", mm.group(0))
            out = [re.sub(r'<div class="math-box">.*?</div>', fix, o, flags=re.S) for o in out]
        return out""")
rep('''meta=[("Custo", "~120 operações/passo; ~1,4 KB"),''', '''meta=[("Custo", "~121 operações/passo; ~1,3 KB"),''')
rep('''meta=[("Cost", "~120 operations/step; ~1.4 KB"),''', '''meta=[("Cost", "~121 operations/step; ~1.3 KB"),''')
rep("e ~1,4 KB de estado", "e ~1,3 KB de estado")
rep("and ~1.4 KB of state", "and ~1.3 KB of state")
open(p, "w", encoding="utf-8").write(s)
print("ok")
