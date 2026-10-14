#!/usr/bin/env python3
"""build_v054_spec.py — builds the self-contained LEBRE v0.54 specification and technical report, revision 0 (PT-BR and
EN), derived from build_v053_spec.py (not changed): the same visual template, CSS, logo and PDF pipeline as build_v052_spec.py (imported, not changed), inline SVG
diagrams and matplotlib charts, KaTeX math, PDF via Edge headless, page renders for visual QA. The document describes the
whole LEBRE (structural core with triggered removal and cheap equivalence report + M1 with dormancy + M2); the charts
about the core come from build_v052_spec.charts (imported, not changed). Every empirical number is read from the result
files at build time (v054_data.py: this repository and the public LEBRE Lab); the documents never refer to local paths.
Usage: python build_v054_spec.py [pt|en] [--qa <folder for page renders>]"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_v052_spec as B52  # noqa: E402  (template, logo, CSS and Edge path only)
import v053_charts as CH  # noqa: E402
from v053_data import FAMS, ROOT  # noqa: E402
from v054_data import FAMS54, load  # noqa: E402
from v054_diagrams import all_diagrams  # noqa: E402
from v054_text import FAM, TEXT, sections  # noqa: E402

PDF_DIR = ROOT / "docs" / "architecture" / "pdf"
CH.FAM_COL.setdefault("niveis", "#7c5cc4")      # cor da família de níveis da v0.54 (a da carga, ausente nesta avaliação)


def charts(lang, N):
    T = lambda a, b: a if lang == "pt" else b
    F = CH.Fmt(lang); fam = N["final53"]["fam"]; FN = FAM[lang]; F4 = N["final54"]; fam4 = F4["fam"]
    mn52 = B52.MN[lang]; keep = dict(mn52)   # core charts: the core is labelled as such, v0.51 as the previous architecture
    mn52.update(V052_PY=T("LEBRE: núcleo", "LEBRE: core"), V051=T("arquitetura anterior (v0.51)", "previous architecture (v0.51)"))
    try:
        G = {k: v for k, v in B52.charts(lang, N["base"]).items()
             if k in ("eproc", "misadj", "ev_trace", "response", "stress", "fdr", "forecast", "bar_r3", "mcu_steps", "mcu_mem")}
    finally:
        mn52.clear(); mn52.update(keep)
    G |= {"fam_ratio": CH.fam_ratio([(FN[k], k, fam[k]["ratios"], fam[k]["ratio"]) for k in FAMS], F,
                                   T("LEBRE ÷ núcleo (MSE, escala log)", "LEBRE ÷ core (MSE, log scale)"), T("núcleo = 1", "core = 1"),
                                   T("média geométrica da família", "family geometric mean")),
         "cost_gain": CH.cost_gain([(x["acrescimo_custo"], x["v053_sobre_v052"], x["familia"]) for x in N["final"]["R"]["series"]], F,
                                   T("acréscimo de custo de M1 + M2 (FP por passo)", "cost increment of M1 + M2 (FP per step)"),
                                   T("LEBRE ÷ núcleo (MSE, log)", "LEBRE ÷ core (MSE, log)"), {k: FN[k] for k in FAMS}),
         "fam_ratio54": CH.fam_ratio([(FN[k], k, fam4[k]["ratios"], fam4[k]["ratio"]) for k in FAMS54], F,
                                     T("v0.54 ÷ versão anterior (MSE, escala log)", "v0.54 ÷ previous version (MSE, log scale)"),
                                     T("anterior = 1", "previous = 1"), T("média geométrica da família", "family geometric mean")),
         "cost54": CH.cost_gain([(x["razao_custo"], x["v054_sobre_v053"], x["familia"]) for x in F4["R"]["series"]], F,
                                T("custo por passo, v0.54 ÷ versão anterior", "cost per step, v0.54 ÷ previous version"),
                                T("v0.54 ÷ anterior (MSE, log)", "v0.54 ÷ previous (MSE, log)"), {k: FN[k] for k in FAMS54})}
    return G


def cover(L, N, lang):
    P = lang == "pt"; T = lambda a, b: a if P else b
    n = lambda x, d: (f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".") if P else f"{x:,.{d}f}")
    F = N["final54"]; F3 = N["final53"]; ov = F3["overall"]
    c_med = float(np.median(F["cost54_all"]))
    lo, hi = min(F["fam"][k]["ratio"] for k in FAMS54), max(F["fam"][k]["ratio"] for k in FAMS54)
    meta = [("Status", T("versão de pesquisa promovida por regra pré-registrada (13/10/2026), com a errata 01; escopo: previsão de um passo à frente com entradas",
                         "research version promoted by a pre-registered rule (2026-10-13), with errata 01; scope: one-step-ahead forecasting with inputs")),
            (T("Avaliação final", "Final evaluation"), T(f"{F['n']} séries reservadas; nenhuma piora por família contra a versão anterior (razão de erro {n(lo, 3)} a {n(hi, 3)}); M1 + M2 sobre o núcleo: {n(ov['geo'], 3)} na avaliação anterior",
                                                         f"{F['n']} reserved series; no harm per family against the previous version (error ratio {n(lo, 3)} to {n(hi, 3)}); M1 + M2 over the core: {n(ov['geo'], 3)} in the previous evaluation")),
            (T("Custo", "Cost"), T(f"mediana de {n(c_med, 0)} operações por passo; {n(F['cost_median'], 3)} vez o da versão anterior por série [IC 95% {n(F['cost_ci'][0], 3)}; {n(F['cost_ci'][1], 3)}]; memória estimada {n(F['ram'] / 1024, 1)} KB",
                                   f"median of {n(c_med, 0)} operations per step; {n(F['cost_median'], 3)} times the previous version's per series [95% CI {n(F['cost_ci'][0], 3)}; {n(F['cost_ci'][1], 3)}]; estimated memory {n(F['ram'] / 1024, 1)} KB")),
            (T("Escopo da evidência", "Scope of the evidence"), T("custo menor onde a M1 não ajuda e igual onde ajuda; remoção verificada no desenvolvimento e nas validações; núcleo avaliado na classe de orçamento em hidrologia e prédios",
                                     "lower cost where M1 does not help and equal where it does; removal verified in development and validations; core evaluated in the budget class on hydrology and buildings"))]
    return f"""<div class="cover-page">
<div class="cover-header"><div class="cover-logo-panel"><img class="cover-logo" src="{B52.LOGO}" alt="LEBRE"></div>
<div class="cover-badge">{L['badge']}</div></div>
<div class="cover-main"><div class="cover-title">{L['title']}</div><div class="cover-subtitle">{L['subtitle']}</div>
<div class="cover-expansion">{L['expansion']}</div>
<div class="cover-meta-grid">""" + "".join(
        f'<div class="cover-meta-card"><div class="cover-meta-label">{k}</div><div class="cover-meta-value">{v}</div></div>' for k, v in meta) + f"""</div></div>
<div class="cover-footer"><div>{L['footer_l']}</div><div>{L['footer_r']}</div></div></div>"""


def build(lang, N):
    L = TEXT[lang]
    body = "\n".join([cover(L, N, lang)] + sections(lang, N, all_diagrams(lang), charts(lang, N)))
    body = re.sub(r'<div class="diagram-container no-break">(<svg[^>]*xmlns:xlink)', r'<div class="diagram-container no-break chart">\1', body)
    head = f"""<!DOCTYPE html><html lang="{L['html_lang']}"><head><meta charset="utf-8"><title>{L['title']}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<script>document.addEventListener("DOMContentLoaded",function(){{renderMathInElement(document.body,{{delimiters:[
{{left:'$$',right:'$$',display:true}},{{left:'\\\\(',right:'\\\\)',display:false}}],strict:false,
ignoredTags:["script","noscript","style","textarea","pre","code","svg"]}});}});</script>
{B52.STYLE.replace(L['v01_header'], L['page_header']).replace(L['v01_status'], L['page_status']).replace(L['v01_footer'], L['page_footer']).replace('"Página "', L['page_word'])}
{B52.EXTRA_CSS}</head><body>"""
    return head + body + "</body></html>"


def main():
    args = sys.argv[1:]
    qa = Path(args[args.index("--qa") + 1]) if "--qa" in args else None
    langs = [a for a in args if a in ("pt", "en")] or ["pt", "en"]
    N = load()
    jobs = {"pt": ("LEBRE_v0.54_SPEC_PTBR.html", "LEBRE_ARCHITECTURE_v0.54_SPEC_PTBR.pdf"),
            "en": ("LEBRE_v0.54_SPEC_EN.html", "LEBRE_ARCHITECTURE_v0.54_SPEC_EN.pdf")}
    for lang in langs:
        hname, pname = jobs[lang]
        html = build(lang, N)
        clean = re.sub(r"<(script|style)[^>]*>.*?</\1>|<link[^>]*>|data:image[^\"]+|<svg.*?</svg>", "", html, flags=re.S)
        assert not re.search(r"\{[a-zA-Z_]+\(|ab\[|\{n\(", clean), (lang, "unformatted expression")
        for bad in ("experiments/", "experiments\\", "D:\\", "D:/", "C:\\", ".csv", ".py", "scratch", "PROTO", "Users", "¤",
                    "especificação v0.52", "v0.52 specification", "especificação v0.53", "v0.53 specification",
                    "revisão 1, §", "revision 1, §", "ver spec", "see spec"):
            assert bad not in clean, (lang, bad)
        (HERE / hname).write_text(html, encoding="utf-8")
        pdf = PDF_DIR / pname
        cmd = [B52.EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
               "--run-all-compositor-stages-before-draw", f"--print-to-pdf={pdf}", str((HERE / hname).resolve())]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not pdf.exists():
            print("compile failed", lang, r.stderr[:500]); sys.exit(1)
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(pdf))
        empty = [i + 1 for i, p in enumerate(doc) if i > 0 and not p.get_textpage().get_text_range().strip()]
        if qa:
            qa.mkdir(parents=True, exist_ok=True)
            for f in qa.glob(f"{lang}_page_*.png"):
                f.unlink()
            for i, p in enumerate(doc):
                p.render(scale=1.4).to_pil().save(qa / f"{lang}_page_{i + 1:02d}.png")
        print(f"[{lang}] {pdf.name}: {len(doc)} pages, {pdf.stat().st_size} bytes, empty pages: {empty}")


if __name__ == "__main__":
    main()
