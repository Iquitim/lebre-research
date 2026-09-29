#!/usr/bin/env python3
"""
build_v032_spec.py — builds the LEBRE v0.3.2 research specification (PT-BR and EN) in the style of the
v0.1 condensed reference (same CSS, cover, KaTeX, inline SVG), then compiles PDFs with Edge headless and
renders every page for visual QA. All empirical numbers are read from the result CSV/JSON files.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from v032_diagrams import all_diagrams  # noqa: E402

V03 = ROOT / "experiments" / "LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01"
B02 = ROOT / "experiments" / "LEBRE-V0.3-EXTERNAL-BENCH-02"
PDF_DIR = ROOT / "docs" / "architecture" / "pdf"
QA_DIR = ROOT / "scratch" / "pdf_qa_v032"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# ------------------------------------------------------------------ template pieces from v0.1
tpl = (HERE / "LEBRE_CONDENSED_PTBR.html").read_text(encoding="utf-8")
STYLE = tpl[tpl.find("<style>"): tpl.find("</style>") + len("</style>")]
LOGO = re.search(r'src="(data:image/png;base64,[^"]+)"', tpl).group(1)
EXTRA_CSS = """
<style>
.kv { display:grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.kv div { background:#f8fafc; border:1px solid #e2e8f0; border-radius:5px; padding:6px 9px; font-size:8pt; }
.small { font-size: 7.6pt; color:#475569; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
.verdict { font-size: 10pt; font-weight: 800; color:#0f172a; background:#f0fdf4; border:1.5px solid #15803d;
           padding:8px 12px; border-radius:6px; margin:8px 0; }
.verdict-warn { background:#fffbeb; border-color:#b45309; }
</style>"""


# ------------------------------------------------------------------ data
def load_numbers():
    N = {}
    pt = pd.read_csv(V03 / "PROPERTY_TESTS_v032.csv")
    g = lambda t: pt[pt.test == t].dropna(axis=1, how="all")
    N["T1"] = float(g("T1_causality").max_abs_diff_upto_t0.max())
    N["T2"] = int(g("T2_lag_alignment").exact.sum())
    t3 = g("T3_type_I")
    N["T3"] = {k: float(v) for k, v in t3.groupby("noise").false_promotions.mean().items()}
    N["T3_n"] = int(len(t3))
    a = g("T4_false_eviction"); N["T4"] = (int(a.false_evictions.sum()), int(a.steps_monitored.sum()))
    a = g("T5_kalman"); N["T5"] = (float(a.excess_ratio.median()), float(a.excess_ratio.max()))
    a = g("T6_quiescence"); N["T6"] = (int(a.latent_at_3999.astype(str).eq("True").sum()), len(a),
                                       float(a.lifecycle_events_during_silence.mean()))
    a = g("T7_scale"); N["T7"] = [float(a[c].mean()) for c in ("nmse_scale_0.001", "nmse_scale_1", "nmse_scale_1000")]
    a = g("T8_hidden_cost"); N["T8"] = float(a.fp_per_step.mean())
    arms = pd.read_csv(V03 / "ADDENDUM_PART5_ARMS.csv").set_index("arm")
    con = pd.read_csv(V03 / "ADDENDUM_PART5_CONTRASTS.csv").set_index("contrast")
    N["int"] = {"arms": arms, "con": con}
    N["p4"] = pd.read_csv(V03 / "ADDENDUM_PART4_OVERALL.csv").set_index("model_id")
    N["p4task"] = pd.read_csv(V03 / "ADDENDUM_PART4_V032_VS_FIELD.csv")
    N["p6"] = pd.read_csv(V03 / "ADDENDUM_PART6_REAL.csv").set_index("task_id")
    if (B02 / "BENCH02_SUMMARY.json").exists():
        N["b02"] = json.load(open(B02 / "BENCH02_SUMMARY.json"))
        N["b02rank"] = pd.read_csv(B02 / "BENCH02_MEAN_RANK.csv").set_index("model_id")
        N["b02task"] = pd.read_csv(B02 / "BENCH02_V032_BY_TASK.csv")
    return N


def f(x, d=3):
    return f"{x:.{d}f}"


def table(head, rows, cls=""):
    h = "".join(f"<th>{c}</th>" for c in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="no-break {cls}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


# ------------------------------------------------------------------ language packs
from v032_text import TEXT  # noqa: E402


def build(lang, N):
    L = TEXT[lang]
    D = all_diagrams(L["diag"])
    S = []
    S.append(f"""<div class="cover-page">
<div class="cover-header"><div class="cover-logo-panel"><img class="cover-logo" src="{LOGO}" alt="LEBRE"></div>
<div class="cover-badge">{L['badge']}</div></div>
<div class="cover-main"><div class="cover-title">{L['title']}</div><div class="cover-subtitle">{L['subtitle']}</div>
<div class="cover-expansion">{L['expansion']}</div>
<div class="cover-meta-grid">""" + "".join(
        f'<div class="cover-meta-card"><div class="cover-meta-label">{k}</div><div class="cover-meta-value">{v}</div></div>'
        for k, v in L["meta"]) + f"""</div></div>
<div class="cover-footer"><div>{L['footer_l']}</div><div>{L['footer_r']}</div></div></div>""")
    for sec in L["sections"](N, D, table, f):
        S.append(sec)
    head = f"""<!DOCTYPE html><html lang="{L['html_lang']}"><head><meta charset="utf-8"><title>{L['title']}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<script>document.addEventListener("DOMContentLoaded",function(){{renderMathInElement(document.body,{{delimiters:[
{{left:'$$',right:'$$',display:true}},{{left:'\\\\(',right:'\\\\)',display:false}},{{left:'\\\\[',right:'\\\\]',display:true}}],
ignoredTags:["script","noscript","style","textarea","pre","code","svg"]}});}});</script>
{STYLE.replace(L['v01_header'], L['page_header']).replace(L['v01_status'], L['page_status']).replace(L['v01_footer'], L['page_footer']).replace('"Página "', L['page_word'])}
{EXTRA_CSS}</head><body>"""
    return head + "\n".join(S) + "</body></html>"


def main():
    N = load_numbers()
    jobs = [("pt", "LEBRE_v0.3.2_RESEARCH_SPEC_PTBR.html", "LEBRE_ARCHITECTURE_v0.3.2_RESEARCH_SPEC_PTBR.pdf"),
            ("en", "LEBRE_v0.3.2_RESEARCH_SPEC_EN.html", "LEBRE_ARCHITECTURE_v0.3.2_RESEARCH_SPEC_EN.pdf")]
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for lang, hname, pname in jobs:
        html = build(lang, N)
        (HERE / hname).write_text(html, encoding="utf-8")
        pdf = PDF_DIR / pname
        cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
               "--run-all-compositor-stages-before-draw", f"--print-to-pdf={pdf}", str((HERE / hname).resolve())]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not pdf.exists():
            print("compile failed", lang, r.stderr[:500]); sys.exit(1)
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(pdf))
        empty = [i + 1 for i, p in enumerate(doc) if i > 0 and not p.get_textpage().get_text_range().strip()]
        for i, p in enumerate(doc):
            p.render(scale=1.4).to_pil().save(QA_DIR / f"{lang}_page_{i + 1:02d}.png")
        print(f"[{lang}] {pdf.name}: {len(doc)} pages, {pdf.stat().st_size} bytes, empty pages: {empty}")


if __name__ == "__main__":
    main()
