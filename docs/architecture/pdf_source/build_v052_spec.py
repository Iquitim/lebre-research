#!/usr/bin/env python3
"""build_v052_spec.py — builds the self-contained LEBRE v0.52 specification and technical report (PT-BR and EN): same
visual template as the earlier documents, inline SVG diagrams and matplotlib charts in the document language, KaTeX math,
PDF via Edge headless, page renders for visual QA. Every empirical number is read from the result files at build time
(v052_data.py); the documents never refer to local paths."""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import v052_charts as CH  # noqa: E402
from v052_data import ROOT, load  # noqa: E402
from v052_diagrams import all_diagrams  # noqa: E402
from v052_text import MN, TEXT  # noqa: E402

PDF_DIR = ROOT / "docs" / "architecture" / "pdf"
QA_DIR = ROOT / "scratch" / "pdf_qa_v052r1"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

tpl = (HERE / "LEBRE_CONDENSED_PTBR.html").read_text(encoding="utf-8")
STYLE = tpl[tpl.find("<style>"): tpl.find("</style>") + len("</style>")]
LOGO = re.search(r'src="(data:image/png;base64,[^"]+)"', tpl).group(1)
EXTRA_CSS = """
<style>
.small { font-size: 7.6pt; color:#475569; }
table.compact td, table.compact th { padding: 3px 5px; font-size: 7.3pt; }
.refs li { margin-bottom: 3px; font-size: 7.6pt; line-height: 1.35; }
.diagram-container.chart svg { max-height: none; width: 100%; height: auto; }
.diagram-container svg { width: 100%; height: auto; }
pre.pseudo { font-family: Consolas, 'Cascadia Mono', 'Courier New', monospace; font-size: 6.9pt; line-height: 1.42;
             background: #f8fafc; border: 1px solid #cbd5e1; border-left: 3px solid #6d28d9; border-radius: 4px;
             padding: 8px 10px; white-space: pre-wrap; page-break-inside: auto; }
pre.pseudo .kw { color: #6d28d9; font-weight: 700; } pre.pseudo .cm { color: #64748b; }
.toc-list { columns: 2; column-gap: 26px; } .toc-item { padding: 2px 0; font-size: 8pt; break-inside: avoid; }
.math-box { page-break-inside: avoid; break-inside: avoid; }
h1 { page-break-after: avoid; break-after: avoid; } h2 { page-break-after: avoid; break-after: avoid; }
</style>"""
SHORT = {"pt": {"V052_PY": "LEBRE", "NLINEAR_ONLINE": "NLinear", "DLINEAR_ONLINE": "DLinear", "HOLT_WINTERS": "Holt-W.", "FITS": "FITS",
                "SPARSETSF": "SparseTSF", "ARX_NLMS": "ARX denso", "LASSO_ONLINE": "LASSO", "V051": "v0.51", "AIRLINE_X": "SARIMAX-X",
                "ARX_RLS_PLS": "ARX MQ"},
         "en": {"V052_PY": "LEBRE", "NLINEAR_ONLINE": "NLinear", "DLINEAR_ONLINE": "DLinear", "HOLT_WINTERS": "Holt-W.", "FITS": "FITS",
                "SPARSETSF": "SparseTSF", "ARX_NLMS": "Dense ARX", "LASSO_ONLINE": "LASSO", "V051": "v0.51", "AIRLINE_X": "SARIMAX-X",
                "ARX_RLS_PLS": "LS ARX"}}
ROLE = {"V052_PY": "leb", "AIRLINE_X": "ref", "ARX_RLS_PLS": "ref", "TTM_ZS": "fm", "TTM_FT_EXOG": "fm", "CHRONOS2_COV": "fm"}


def charts(lang, N):
    P = lang == "pt"; T = lambda a, b: a if P else b
    F = CH.Fmt(lang); mn = MN[lang]; sh = SHORT[lang]; G = {}
    t3 = N["r3_tab"]
    ci = lambda s: [float(v) for v in s.strip("[]").split(",")]
    models = [m for m in t3.sort_values("ALL").index if m != "V052_C32"]
    G["bar_r3"] = CH.bar_ci([(mn[m], t3.loc[m, "ALL"], *ci(t3.loc[m, "CI95"]), ROLE.get(m, "bud")) for m in models], F,
                            T("erro quadrático relativo ao NLinear online (média geométrica, 60 séries)", "squared error relative to online NLinear (geometric mean, 60 series)"),
                            "NLinear = 1")
    R3 = N["r3"]; order = ["V052_PY", "AIRLINE_X", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "FITS", "ARX_NLMS", "LASSO_ONLINE", "ARX_RLS_PLS", "V051", "SPARSETSF"]
    G["strip_r3"] = CH.strip([(sh[m], R3[m].values, ROLE.get(m, "bud")) for m in order], F, T("erro relativo por série (log)", "per-series relative error (log)"),
                             thr_label=T("1,5", "1.5"))
    pp, pf = N["r3_pair"], N["r3_pair_fm"]
    wr = [(mn[m], pp[m]["wins"], pp[m]["ratio"], pp[m]["lo"], pp[m]["hi"], ROLE.get(m, "bud")) for m in
          ["NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "FITS", "SPARSETSF", "ARX_NLMS", "LASSO_ONLINE", "V051", "AIRLINE_X", "ARX_RLS_PLS"]]
    wr += [(mn[m] + T(" (1.000 pts)", " (1,000 pts)"), pf[m]["wins"], pf[m]["ratio"], pf[m]["lo"], pf[m]["hi"], "fm") for m in ["TTM_ZS", "TTM_FT_EXOG", "CHRONOS2_COV"]]
    G["wins"] = CH.wins(wr, F, (T("séries em que a LEBRE erra menos (de 60)", "series where LEBRE errs less (of 60)"),
                                T("razão pareada LEBRE / comparador (log)", "paired ratio LEBRE / comparator (log)")), 60)
    dv = N["dev_comp"]; gm = lambda v: float(np.exp(np.log(v[v > 0].dropna()).mean()))
    r2 = N["r2p_gm"]; r3 = N["r3p_gm"]
    G["consistency"] = CH.grouped([T("Desenvolvimento (29)", "Development (29)"), T("Reserva 2 (40)", "Reserve 2 (40)"), T("Reserva 3 (60)", "Reserve 3 (60)")],
                                  [("LEBRE", [gm(dv.V052), r2["V052_CORRIGIDA"], r3["V052_PY"]["ALL"]], CH.LEB),
                                   (mn["DLINEAR_ONLINE"], [gm(dv.DLINEAR_ONLINE), r2["DLINEAR_ONLINE"], r3["DLINEAR_ONLINE"]["ALL"]], CH.BUD),
                                   (mn["AIRLINE_X"], [gm(dv.AIRLINE_X), r2["AIRLINE_X"], r3["AIRLINE_X"]["ALL"]], CH.REF),
                                   (mn["CHRONOS2_COV"], [gm(dv.CHRONOS2_COV), r2["CHRONOS2_COV"], r3["CHRONOS2_COV"]["ALL"]], CH.FMC)],
                                  F, T("erro relativo ao NLinear (1.000 pontos)", "error relative to NLinear (1,000 points)"))
    fl = {m: float(N["r3_meta"][f"flops_{m}"].astype(float).mean()) for m in ["V052_PY", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "HOLT_WINTERS", "FITS", "SPARSETSF", "ARX_NLMS", "LASSO_ONLINE", "V051", "ARX_RLS_PLS"]}
    fl["TTM_ZS"], fl["TTM_FT_EXOG"] = N["ttm_flops"]; fl["CHRONOS2_COV"] = 3e9
    off = {"V052_PY": (8, -9), "NLINEAR_ONLINE": (7, 6), "DLINEAR_ONLINE": (7, -7), "HOLT_WINTERS": (7, 0), "FITS": (7, 0), "SPARSETSF": (7, 0),
           "ARX_NLMS": (-7, 6), "LASSO_ONLINE": (7, 4), "V051": (7, 0), "ARX_RLS_PLS": (7, 0), "TTM_ZS": (7, 5), "TTM_FT_EXOG": (7, -6), "CHRONOS2_COV": (-8, 0)}
    G["frontier"] = CH.frontier([(sh.get(m, mn[m]), fl[m], r3[m]["ALL"], ROLE.get(m, "bud"), m == "CHRONOS2_COV", *off[m]) for m in off], F,
                                T("operações de ponto flutuante por previsão (log)", "floating-point operations per forecast (log)"),
                                T("erro relativo ao NLinear", "error relative to NLinear"), T("classe de orçamento", "budget class"))
    G["misadj"] = CH.misadj(N["misadj"], F, {"acc": T("{}/{} aceitas", "{}/{} accepted"), "thr": T("limiar log(1/α)", "threshold log(1/α)"),
                                             "y1": T("log-evidência do oráculo (máx. por série)", "oracle log-evidence (max per series)"),
                                             "t1": T("Oráculo de projeção", "Projection oracle"), "emp": T("medido", "measured"), "theo": "μ/(2−μ)",
                                             "exact": T("garantia\nexata", "exact\nguarantee"), "x2": T("passo μ da referência", "reference step μ"),
                                             "y2": T("desajuste M", "misadjustment M"), "t2": T("Desajuste do NLMS", "NLMS misadjustment")})
    G["stress"] = CH.stress(N["stress"], F, {"exp": T("{} com desvio > 10×", "{} with deviation > 10×"), "thr": T("10× a amplitude", "10× the range"),
                                             "cfg": [T("sem correção", "no fix"), T("retenção", "hold"), T("retenção + contrato", "hold + contract")]},
                            T("desvio máximo / amplitude (log)", "max deviation / range (log)"))
    G["eproc"] = CH.eproc_sim(F, {"forms": [T("recortada", "clipped"), T("dois pontos", "two-point"), T("cauda pesada", "heavy tail")],
                                  "names": [T("c dois lados", "two-sided c"), T("c unilateral", "one-sided c"), T("apostas", "betting"), T("mistura", "mixture")],
                                  "y1": T("erro tipo I", "type-I error"), "t1": T("Validade", "Validity"), "x2": T("tempo mediano até o limiar (passos)", "median time to threshold (steps)"),
                                  "y2": T("poder", "power"), "t2": T("Poder", "Power")})
    A = N["exA"]; ex = N["ex"]
    G["forecast"] = CH.example_forecast(A, F, {"int": T("intervalo de 90%", "90% interval"), "y": T("observado", "observed"), "f": T("previsão", "forecast"),
                                               "x": T("passo", "step"), "yl": T("vazão (m³/s)", "flow (m³/s)")}, 21000, 21400)
    G["ev_trace"] = CH.example_evidence(A, ex["A"]["events"], F, {"kind": {"add": T("acrescentar", "add"), "split": T("dividir", "split"), "rem": T("remover", "remove")},
                                                                  "acc": lambda e: T("aceita: ", "accepted: ") + ("x0" if "'in', 0" in e[3] else T("resíduo", "residual")),
                                                                  "x": T("passo", "step"), "y": "log E"}, 9000)
    truth = {"x0": {12: 0.8}, "x1": {k: 0.075 for k in range(4, 8)}, T("x2 (não aceita)", "x2 (not accepted)"): {}}
    rb = ex["B"]["resp"]
    G["response"] = CH.response({"x0": [(tuple(a), b) for a, b in rb["('in', 0)"]], "x1": [(tuple(a), b) for a, b in rb["('in', 1)"]],
                                 T("x2 (não aceita)", "x2 (not accepted)"): []}, truth, F,
                                {"true": T("verdadeira", "true"), "est": T("recuperada", "recovered"), "x": T("atraso", "lag"), "y": T("peso por atraso", "weight per lag")})
    comp_lab = {"memory": T("memória", "memory"), "structure": T("estrutura (base + blocos)", "structure (base + blocks)"), "screening": T("triagem", "screening"),
                "experiments": T("experimentos", "experiments"), "control": T("controle", "control")}
    G["cost_comp"] = CH.cost_components([(T("Série real (1 entrada + próprio passado)", "Real series (1 input + own past)"), ex["A"]["comp"]),
                                         (T("Sintético (3 entradas + próprio passado)", "Synthetic (3 inputs + own past)"), ex["B"]["comp"])], F,
                                        {"comp": comp_lab, "contract": T("contrato 400", "contract 400"), "x": T("operações por passo (média)", "operations per step (mean)")})
    G["fp_hist"] = CH.fp_hist(N["r3_meta"], F, {"grp": {"camels": "CAMELS", "bdg2": "BDG2"}, "x1": T("média por passo", "mean per step"),
                                                "x2": T("máximo por passo", "maximum per step"), "y": T("séries", "series")})
    G["equiv"] = CH.equiv(N["equiv"], N["r3_meta"], F, {"dev": T("desenvolvimento (29)", "development (29)"), "r3": T("reserva 3 (60)", "reserve 3 (60)"),
                                                          "same": T("mesmas decisões", "same decisions"), "diff": T("decisão deslocada", "shifted decision"),
                                                          "crit": T("critério 10⁻⁴", "criterion 10⁻⁴"), "x": T("|diferença relativa do NMSE| (log)", "|relative NMSE difference| (log)")})
    mcu = N["mcu"]
    tick = [("ONS\n" + T("(dev.)", "(dev.)")), ("CAMELS\n(dev.)"), ("BDG2\n(dev.)")] + [("CAMELS\n" if t.startswith("camels") else "BDG2\n") + t.split(":")[-1].split("_")[0] for t in mcu.TASK[3:]]
    G["mcu_steps"] = CH.mcu_steps(mcu, F, {"ticks": tick, "y": T("instruções por passo (log)", "instructions per step (log)"), "y2": T("tempo estimado", "estimated time"),
                                           "dev": T("desenvolvimento", "development"), "r3": T("reserva 3 (pré-registrada)", "reserve 3 (pre-registered)"),
                                           "mean": T("média", "mean"), "max": T("máximo", "maximum")})
    series = [("ons_vg", "ONS", T("ONS (1 entrada, 32.144 passos)", "ONS (1 input, 32,144 steps)")), ("camels", "CAMELS", T("CAMELS (3 entradas, 16.253 passos)", "CAMELS (3 inputs, 16,253 steps)")),
              ("bdg2", "BDG2", T("BDG2 (2 entradas, 17.544 passos)", "BDG2 (2 inputs, 17,544 steps)"))]
    G["mcu_timeline"] = CH.mcu_timeline(N["prof"], F, {"series": series, "max": T("máximo do bloco", "block maximum"), "mean": T("média do bloco", "block mean"),
                                                       "big": T("> 20 mil", "> 20 thousand"), "x": T("passo", "step"), "y": T("instruções por passo", "instructions per step")})
    G["mcu_hist"] = CH.mcu_hist(N["prof"], F, {"series": series, "x": T("instruções por passo (log)", "instructions per step (log)"), "y": T("fração dos passos", "fraction of steps")})
    fn = {"lebre052_step": T("passo principal", "main step"), "seg_mean": T("médias de segmentos", "segment means"), "memcpy": T("cópias (memcpy)", "copies (memcpy)"),
          "block": T("blocos de resposta", "response blocks"), "cfeat": T("regressores do desafiante", "challenger regressors"), "split_keys": T("chaves de divisão", "split keys"),
          "main": T("medição (firmware)", "measurement (firmware)")}
    for k in ("__adddf3", "__aeabi_dmul", "__extendsfdf2", "__aeabi_ddiv", "__aeabi_d2f", "__truncdfsf2", "__gtdf2"):
        fn[k] = T("precisão dupla emulada", "emulated double precision")
    for k in ("__ieee754_expf", "expf", "__ieee754_logf", "logf", "finitef", "__ieee754_log", "log", "pow", "__ieee754_pow", "sqrtf", "__ieee754_sqrtf"):
        fn[k] = T("exp/log (libm)", "exp/log (libm)")
    G["mcu_break"] = CH.mcu_breakdown(N["trace"], F, {"s_ons": "ONS", "s_bdg2": "BDG2", "t1": T("Ciclos por classe", "Cycles by class"), "t2": T("Ciclos por função", "Cycles by function"),
                                                      "cls": {"alu": T("inteiros/lógica", "integer/logic"), "ldst": T("load/store", "load/store"), "branch": T("desvios", "branches"),
                                                              "fpldst": T("load/store FP", "FP load/store"), "fp": T("aritmética FP", "FP arithmetic"), "fpdiv": T("divisão FP", "FP division"),
                                                              "other": T("outros", "other")},
                                                      "fn": fn, "fn_other": T("outras", "other")})
    G["mcu_mem"] = CH.mcu_memory(F, {"state": T("estado do modelo {} KB", "model state {} KB"), "free": T("histograma de medição 16 KB; livre", "measurement histogram 16 KB; free"),
                                     "ram": "RAM", "flash": "Flash", "code": T("modelo {} KB + libm/libgcc {} KB", "model {} KB + libm/libgcc {} KB")},
                                 int(mcu.STRUCT_BYTES.iloc[0]), 91372, 14560, 10107)
    G["fdr"] = CH.fdr_sim(N["fdr_sum"], N["fdr_runs"], F, {"y1": T("execuções com mudança falsa", "runs with a false change"), "y2": T("FDR estimado", "estimated FDR"),
                                                            "null": T("nulos", "nulls"), "partial": T("com uma entrada verdadeira", "with one true input"),
                                                            "final": T("falsa ainda no fim", "false still at the end")})
    return G


def cover(L, N, lang):
    P = lang == "pt"; T = lambda a, b: a if P else b
    n = lambda x, d: (f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".") if P else f"{x:,.{d}f}")
    t3 = N["r3_tab"]; mcu = N["mcu"]
    meta = [(T("Custo", "Cost"), T(f"~{n(N['r3_meta'].fp.mean(), 0)} operações/passo (analítico; contrato de 400 não cumprido por 3,7%); {n(mcu['mean'].min() / 1000, 1)}–{n(mcu['mean'].max() / 1000, 1)} mil instruções/passo num Cortex-M4F simulado",
                                   f"~{n(N['r3_meta'].fp.mean(), 0)} operations/step (analytic; 400 contract not met by 3.7%); {n(mcu['mean'].min() / 1000, 1)}–{n(mcu['mean'].max() / 1000, 1)} thousand instructions/step on a simulated Cortex-M4F")),
            (T("Avaliação", "Evaluation"), T("três avaliações pré-registradas sequenciais; versão final confirmada em 40 + 60 séries nunca vistas (a primeira, com 125, revelou a falha corrigida)", "three sequential pre-registered evaluations; final version confirmed on 40 + 60 never-seen series (the first, with 125, revealed the fixed failure)")),
            (T("Última avaliação (60 séries)", "Last evaluation (60 series)"), T(f"erro {n(t3.loc['V052_PY', 'ALL'], 2)}× NLinear; empate com SARIMAX-X; ~25% acima do Chronos-2; 0 falhas graves",
                                                                                 f"error {n(t3.loc['V052_PY', 'ALL'], 2)}× NLinear; tie with SARIMAX-X; ~25% above Chronos-2; 0 severe failures")),
            ("Status", T("versão de pesquisa congelada, não promovida; escopo: hidrologia e prédios, um passo à frente", "frozen research version, not promoted; scope: hydrology and buildings, one step ahead"))]
    return f"""<div class="cover-page">
<div class="cover-header"><div class="cover-logo-panel"><img class="cover-logo" src="{LOGO}" alt="LEBRE"></div>
<div class="cover-badge">{L['badge']}</div></div>
<div class="cover-main"><div class="cover-title">{L['title']}</div><div class="cover-subtitle">{L['subtitle']}</div>
<div class="cover-expansion">{L['expansion']}</div>
<div class="cover-meta-grid">""" + "".join(
        f'<div class="cover-meta-card"><div class="cover-meta-label">{k}</div><div class="cover-meta-value">{v}</div></div>' for k, v in meta) + f"""</div></div>
<div class="cover-footer"><div>{L['footer_l']}</div><div>{L['footer_r']}</div></div></div>"""


def build(lang, N):
    L = TEXT[lang]
    D = all_diagrams(lang); G = charts(lang, N)
    for k in G:
        G[k] = G[k]
    S = [cover(L, N, lang)] + L["sections"](N, D, G)
    body = "\n".join(S)
    body = body.replace('<div class="diagram-container no-break ">', '<div class="diagram-container no-break">')
    # charts: mark containers holding matplotlib SVGs so they are not height-limited
    body = re.sub(r'<div class="diagram-container no-break">(<svg[^>]*xmlns:xlink)', r'<div class="diagram-container no-break chart">\1', body)
    head = f"""<!DOCTYPE html><html lang="{L['html_lang']}"><head><meta charset="utf-8"><title>{L['title']}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<script>document.addEventListener("DOMContentLoaded",function(){{renderMathInElement(document.body,{{delimiters:[
{{left:'$$',right:'$$',display:true}},{{left:'\\\\(',right:'\\\\)',display:false}}],strict:false,
ignoredTags:["script","noscript","style","textarea","pre","code","svg"]}});}});</script>
{STYLE.replace(L['v01_header'], L['page_header']).replace(L['v01_status'], L['page_status']).replace(L['v01_footer'], L['page_footer']).replace('"Página "', L['page_word'])}
{EXTRA_CSS}</head><body>"""
    return head + body + "</body></html>"


def main():
    N = load()
    jobs = [("pt", "LEBRE_v0.52r1_SPEC_PTBR.html", "LEBRE_ARCHITECTURE_v0.52_SPEC_r1_PTBR.pdf"),
            ("en", "LEBRE_v0.52r1_SPEC_EN.html", "LEBRE_ARCHITECTURE_v0.52_SPEC_r1_EN.pdf")]
    if len(sys.argv) > 1:
        jobs = [j for j in jobs if j[0] in sys.argv[1:]]
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for lang, hname, pname in jobs:
        html = build(lang, N)
        clean = re.sub(r"<(script|style)[^>]*>.*?</\1>|<link[^>]*>|data:image[^\"]+|<svg.*?</svg>", "", html, flags=re.S)
        assert not re.search(r"\{[a-zA-Z_]+\(|ab\[|\{n\(", clean), (lang, "unformatted expression")
        for bad in ("experiments/", "experiments\\", "D:\\", "D:/", ".csv", ".py", "scratch", "HELDOUT", "PROTO", "Codinome Lebre\\", "¤"):
            assert bad not in clean, (lang, bad)
        (HERE / hname).write_text(html, encoding="utf-8")
        pdf = PDF_DIR / pname
        cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
               "--run-all-compositor-stages-before-draw", f"--print-to-pdf={pdf}", str((HERE / hname).resolve())]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not pdf.exists():
            print("compile failed", lang, r.stderr[:500]); sys.exit(1)
        import pypdfium2 as pdfium
        doc = pdfium.PdfDocument(str(pdf))
        empty = [i + 1 for i, p in enumerate(doc) if i > 0 and not p.get_textpage().get_text_range().strip()]
        for f in QA_DIR.glob(f"{lang}_page_*.png"):
            f.unlink()
        for i, p in enumerate(doc):
            p.render(scale=1.4).to_pil().save(QA_DIR / f"{lang}_page_{i + 1:02d}.png")
        print(f"[{lang}] {pdf.name}: {len(doc)} pages, {pdf.stat().st_size} bytes, empty pages: {empty}")


if __name__ == "__main__":
    main()
