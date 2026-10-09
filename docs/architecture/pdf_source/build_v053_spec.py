#!/usr/bin/env python3
"""build_v053_spec.py — builds the LEBRE v0.53 specification and technical report (PT-BR and EN): the same visual
template, CSS, logo and PDF pipeline as build_v052_spec.py (imported, not changed), inline SVG diagrams and matplotlib
charts, KaTeX math, PDF via Edge headless, page renders for visual QA. Every empirical number is read from the result
files at build time (v053_data.py: this repository and the public LEBRE Lab); the documents never refer to local paths.
Usage: python build_v053_spec.py [pt|en] [--qa <folder for page renders>]"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_v052_spec as B52  # noqa: E402  (template, logo, CSS and Edge path only)
import v053_charts as CH  # noqa: E402
from v053_data import FAMS, ROOT, load  # noqa: E402
from v053_diagrams import all_diagrams  # noqa: E402
from v053_text import FAM, TEXT, sections  # noqa: E402

PDF_DIR = ROOT / "docs" / "architecture" / "pdf"


def charts(lang, N):
    T = lambda a, b: a if lang == "pt" else b
    F = CH.Fmt(lang); fam = N["final"]["fam"]; FN = FAM[lang]
    G = {"fam_ratio": CH.fam_ratio([(FN[k], k, fam[k]["ratios"], fam[k]["ratio"]) for k in FAMS], F,
                                   T("v0.53 ÷ v0.52 (MSE, escala log)", "v0.53 ÷ v0.52 (MSE, log scale)"), "v0.52 = 1",
                                   T("média geométrica da família", "family geometric mean")),
         "cost_gain": CH.cost_gain([(x["acrescimo_custo"], x["v053_sobre_v052"], x["familia"]) for x in N["final"]["R"]["series"]], F,
                                   T("acréscimo de custo sobre a v0.52 (FP por passo)", "cost increment over v0.52 (FP per step)"),
                                   T("v0.53 ÷ v0.52 (MSE, log)", "v0.53 ÷ v0.52 (MSE, log)"), {k: FN[k] for k in FAMS})}
    return G


def cover(L, N, lang):
    P = lang == "pt"; T = lambda a, b: a if P else b
    n = lambda x, d: (f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".") if P else f"{x:,.{d}f}")
    F = N["final"]; ov = F["overall"]
    import numpy as np
    inc = float(np.median(F["inc_all"]))
    meta = [("Status", T("versão de pesquisa promovida por regra pré-registrada (09/10/2026); a v0.52 continua congelada e inalterada",
                         "research version promoted by a pre-registered rule (2026-10-09); v0.52 remains frozen and unchanged")),
            (T("Avaliação final", "Final evaluation"), T(f"{F['n']} séries reservadas; v0.53 ÷ v0.52 = {n(ov['geo'], 3)} [IC 95% {n(ov['ic95'][0], 3)}; {n(ov['ic95'][1], 3)}]; nenhuma piora por família",
                                                         f"{F['n']} reserved series; v0.53 ÷ v0.52 = {n(ov['geo'], 3)} [95% CI {n(ov['ic95'][0], 3)}; {n(ov['ic95'][1], 3)}]; no harm per family")),
            (T("Custo", "Cost"), T(f"acréscimo mediano de {n(inc, 0)} operações por passo sobre a v0.52 na avaliação final (limite de 1.100); memória estimada {n(F['ram'] / 1024, 1)} KB",
                                   f"median increment of {n(inc, 0)} operations per step over v0.52 in the final evaluation (limit 1,100); estimated memory {n(F['ram'] / 1024, 1)} KB")),
            (T("Escopo", "Scope"), T("ganho em bacias e câmbio; idêntica à v0.52 em solar, eólica e carga; um passo à frente",
                                     "gain in basins and FX; identical to v0.52 in solar, wind and load; one step ahead"))]
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
    jobs = {"pt": ("LEBRE_v0.53_SPEC_PTBR.html", "LEBRE_ARCHITECTURE_v0.53_SPEC_PTBR.pdf"),
            "en": ("LEBRE_v0.53_SPEC_EN.html", "LEBRE_ARCHITECTURE_v0.53_SPEC_EN.pdf")}
    for lang in langs:
        hname, pname = jobs[lang]
        html = build(lang, N)
        clean = re.sub(r"<(script|style)[^>]*>.*?</\1>|<link[^>]*>|data:image[^\"]+|<svg.*?</svg>", "", html, flags=re.S)
        assert not re.search(r"\{[a-zA-Z_]+\(|ab\[|\{n\(", clean), (lang, "unformatted expression")
        for bad in ("experiments/", "experiments\\", "D:\\", "D:/", "C:\\", ".csv", ".py", "scratch", "PROTO", "Users", "¤"):
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
