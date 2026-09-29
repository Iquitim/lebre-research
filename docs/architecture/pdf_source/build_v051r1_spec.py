#!/usr/bin/env python3
"""
build_v051r1_spec.py — Revision 1 (text incorporating Errata 01) of the v0.51 spec; builds the self-contained LEBRE v0.51 specification (PT-BR and EN): same visual template as the
v0.1 / v0.3.2 documents, inline SVG diagrams in the document language, KaTeX math, PDF via Edge headless, page renders
for visual QA. Every empirical number is read from the result files at build time (the documents themselves never
refer to local paths).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from v051_diagrams import all_diagrams  # noqa: E402
from v051r1_text import TEXT  # noqa: E402

E = ROOT / "experiments"
V51 = E / "LEBRE-V0.51-LEAN-01"
PDF_DIR = ROOT / "docs" / "architecture" / "pdf"
QA_DIR = ROOT / "scratch" / "pdf_qa_v051r1"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

tpl = (HERE / "LEBRE_CONDENSED_PTBR.html").read_text(encoding="utf-8")
STYLE = tpl[tpl.find("<style>"): tpl.find("</style>") + len("</style>")]
LOGO = re.search(r'src="(data:image/png;base64,[^"]+)"', tpl).group(1)
EXTRA_CSS = """
<style>
.small { font-size: 7.6pt; color:#475569; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
table.compact td, table.compact th { padding: 3px 5px; font-size: 7.4pt; }
.verdict { font-size: 9.5pt; font-weight: 800; color:#0f172a; background:#f0fdf4; border:1.5px solid #15803d;
           padding:8px 12px; border-radius:6px; margin:8px 0; }
.refs li { margin-bottom: 3px; font-size: 7.6pt; line-height: 1.35; }
.hl { background:#f5f3ff; font-weight:700; }
</style>"""
FM = ["CHRONOS_BOLT_TINY", "CHRONOS_BOLT_SMALL", "CHRONOS2", "CHRONOS2_COV"]
geo = lambda a, b: float(np.exp(np.log(a / b).mean()))


def table_med(df):
    df = df.copy(); df.loc[df.status != "SUCCESS", "nmse"] = np.inf
    return df.groupby(["task_id", "model_id"]).nmse.median().unstack()


def load_numbers():
    N = {"dec": json.load(open(V51 / "V051_DECISION.json"))}
    d = pd.read_csv(V51 / "INTERNAL_V051_RESULTS.csv")
    sub = d[d.task_id != "I10_Redundant_Temporal_Structure"]
    N["int"] = pd.DataFrame({"nmse": d.groupby("arm").nmse.mean(), "fp": d.groupby("arm").fp.mean(), "peak": d.groupby("arm").fp_peak.max(),
                             "cov": d.groupby("arm").coverage.mean(),
                             "struct": sub.groupby("arm").struct_exact.sum() / sub.groupby("arm").struct_checks.sum()})
    N["int_task"] = d.pivot_table(index="task_id", columns="arm", values="nmse")
    h = pd.concat([pd.read_csv(V51 / "HELDOUT_V051_RESULTS.csv"), pd.read_csv(V51 / "HELDOUT_V051_CHRONOS_RESULTS.csv")], ignore_index=True)
    mh = table_med(h); N["mh"] = mh
    N["rank"] = mh.rank(axis=1, method="min").mean().sort_values()
    N["geo_vs_nlin"] = {m: geo(mh[m], mh.NLINEAR_ONLINE) for m in mh.columns if not mh[m].isna().any() or m == "CHRONOS2_COV"}
    N["geo_vs_nlin"] = {m: geo(mh[m].dropna(), mh.NLINEAR_ONLINE[mh[m].notna()]) for m in mh.columns}
    o = pd.read_csv(V51 / "HELDOUT_V051_OFFSETS.csv"); g = o.groupby(["task_id", "arm"]).nmse
    N["instab"] = (g.max() / g.min()).unstack()
    v = h[h.model_id == "LEBRE_V051"]
    N["cov"] = v.groupby("task_id").coverage.median()
    N["costh"] = h.groupby("model_id").agg(fp=("mean_flops", "mean"), peak=("peak_flops", "max"), mem=("memory_bytes", "median"),
                                           ms=("ms_per_step", "median"))
    N["cost_task"] = v.groupby("task_id").agg(fp=("mean_flops", "mean"), peak=("peak_flops", "max"), d=("D", "first"))
    N["wfinal"] = v.groupby("task_id").w_final.first()
    N["examples"] = examples()
    # post-hoc checks requested by the external review
    ph = pd.read_csv(V51 / "POSTHOC_FEEDBACK_METRICS.csv")
    N["ph"] = ph
    N["ph_ws"] = pd.read_csv(V51 / "POSTHOC_FEEDBACK_WS.csv")
    N["ph_null"] = pd.read_csv(V51 / "POSTHOC_FEEDBACK_NULL.csv")
    pn = ph.pivot_table(index=["src", "task"], columns="arm", values="nmse")
    summ = {}
    for src in ("held", "held05"):
        q = pn.loc[src]
        for a in ("M_ONLY", "AIRLINE", "ETS", "RLS5"):
            ok = q[a].notna() & (q[a] < 1)
            summ[(src, a)] = {"geo": float(np.exp(np.log(q[a][ok] / q.V051[ok]).mean())), "n": int(ok.sum()),
                              "fail": int((~ok).sum()), "v051_wins": int((q.V051[ok] < q[a][ok]).sum()),
                              "same": int((np.abs(q[a][ok] / q.V051[ok] - 1) < 0.005).sum())}
    N["ph_summ"] = summ
    # relative MAE vs persistence for the main held-out models (from the result files) + post-hoc arms
    rm = h.copy(); rm.loc[rm.status != "SUCCESS", "mae"] = np.inf
    mae = rm.groupby(["task_id", "model_id"]).mae.median().unstack()
    N["relmae"] = mae.div(mae.CTRL_PERSISTENCE, axis=0)
    N["skill"] = 1 - mh.div(mh.CTRL_PERSISTENCE, axis=0)
    N["m_cost"] = memory_cost()
    N["diag"] = structural_diagnostics()
    return N


def structural_diagnostics():
    """Post-hoc synthetic diagnostics of structure discovery (frozen v0.51 code, 10 seeds per process)."""
    F = E / "LEBRE-V0.51-EXTERNAL-CRITIQUE-FORENSIC-INVESTIGATION-01"
    s = pd.read_csv(F / "RUN_MAIN_SUMMARY.csv"); s = s[s.arm == "V051"]
    so = pd.read_csv(F / "RUN_MAIN_SUMMARY.csv"); so = so[so.arm == "S_ONLY"]
    led = pd.read_csv(F / "RUN_MAIN_LEDGER.csv"); led = led[led.arm == "V051"]
    tau = pd.read_csv(F / "RUN_TAU_SUMMARY.csv")
    tel = pd.read_csv(F / "AUDIT_HELDOUT_TELEMETRY.csv")
    tl = pd.read_csv(F / "RUN_MAIN_B3_TIMELINE.csv"); tl = tl[tl.arm == "V051"]
    out = {"exact": s.groupby("task").exact_frac.mean().to_dict(), "T": s.groupby("task").T.first().to_dict(),
           "ratio_vs_S": (s.groupby("task").nmse.mean() / so.groupby("task").nmse.mean()).to_dict(),
           "removals": s.groupby("task").removals.sum().to_dict(),
           "null_episodes": int(s[s.task.isin(["N1", "N2"])].episodes.sum()),
           "null_promotions": int(s[s.task.isin(["N1", "N2"])].promotions.sum()),
           "tau_B2": tau[tau.task == "B2"].groupby("rho").exact_frac.mean().to_dict(),
           "tau_B3": tau[tau.task == "B3"].groupby("rho").exact_frac.mean().to_dict()}
    from scipy.stats import beta
    out["null_cp95"] = float(beta.ppf(0.95, 1, out["null_episodes"]))
    out["p_dict"] = 169
    lat = {}
    for (task, atom), g in led.groupby(["task", "atom"]):
        pr = g.first_promoted_t.dropna()
        lat[(task, atom)] = {"median": float(pr.median()) if len(pr) else None, "n_prom": int(len(pr)),
                             "le2000": int((g.first_promoted_t <= 2000).sum()),
                             "prop": float(g.first_proposed_t.median()) if g.first_proposed_t.notna().any() else None}
    out["lat"] = lat
    out["b3_full_frac"] = float((tl.n_struct >= 4).mean()) if "n_struct" in tl else None
    out["b3_blocked"] = int(s[s.task == "B3"].blocked_events.sum())
    ho = tel[tel.src == "held"]
    out["cov_A"] = (float(tel.cov_A.min()), float(tel.cov_A.max()))
    out["cov_B"] = (float(tel.cov_B.min()), float(tel.cov_B.max()))
    out["no_struct_promo"] = int((tel.S_structural_promotions == 0).sum()); out["n_real"] = len(tel)
    out["ws0"] = int((tel.mean_wS < 0.01).sum())
    # state memory (float32 accounting of the frozen code) as a function of inputs d and period s
    sys.path.insert(0, str(V51))
    from lebre_v051 import LebreV051
    mb = lambda d, s: LebreV051(d=d, season=s).memory_bytes()
    out["memtab"] = [(d, mb(d, None), mb(d, 24), mb(d, 144), mb(d, 1440),
                      max([s for s in range(2, 200) if mb(d, s) <= 1.3 * 1024] or [None])) for d in (1, 3, 5, 6)]
    return out


def memory_cost():
    """FP per step of the memory expert alone (seasonal and non-seasonal), measured on two held-out series."""
    sys.path.insert(0, str(V51)); sys.path.insert(0, str(ROOT / "data" / "external_v051"))
    from lebre_v051 import MemoryExpert
    import load051
    out = {}
    for task in ("Q1_ONS_Carga_SIN_2019_20", "Q5_BCB_GBPBRL"):
        X, y, _, _, s, j = load051.load(task)
        m = MemoryExpert(s)
        for t in range(len(y)):
            p = m.predict(); m.update(float(y[t]), p)
        out[task] = m.fp / len(y)
    return out


def examples():
    """exact decompositions of one real prediction (held-out Q1 and internal I9), computed at build time."""
    for p in (V51, ROOT, ROOT / "data" / "external_v051"):
        sys.path.insert(0, str(p))
    from lebre_v051 import LebreV051
    from experiments.bench01.streams import CausalStandardScaler
    from scratch.bench_v02_integration import generate_v02_stream
    import load051
    out = {}
    X, y, _, names, s, j = load051.load("Q1_ONS_Carga_SIN_2019_20")
    m = LebreV051(d=X.shape[1], season=s); sc = CausalStandardScaler(d=X.shape[1])
    for t in range(len(X)):
        m.step(sc.transform(X[t]), float(y[t])); sc.update(X[t])
    yh, parts = m.explain_prediction()
    out["Q1"] = {"y_hat": yh, "y": float(y[-1]), "parts": [(k, c) for k, c in parts if abs(c) > 1e-9], "wS": m.wS,
                 "interval": m.interval(), "mem_w": list(zip(m.M.names(), m.M.w))}
    X, y, _ = generate_v02_stream("I9_Hybrid_Delay_Plus_Latent_State", seed=2561, total_steps=6000)
    m = LebreV051(d=5)
    for t in range(6000):
        m.step(X[t], float(y[t]))
    yh, parts = m.explain_prediction()
    out["I9"] = {"y_hat": yh, "y": float(y[-1]), "parts": [(k, c) for k, c in parts if abs(c) > 1e-9], "wS": m.wS,
                 "interval": m.interval(), "events": [(t, a, b) for t, a, b, _ in m.S.events][:8]}
    return out


def build(lang, N):
    L = TEXT[lang]
    names = L["model_names"]
    skip = {"LEBRE_V05", "LEBRE_V045", "LEBRE_V032"}          # earlier versions appear only as named ablations in the text
    acc = [(names.get(m, m), r, m == "LEBRE_V051") for m, r in N["geo_vs_nlin"].items() if m in names and m not in skip]
    pn = N["ph"][N["ph"].src == "held"].pivot_table(index="task", columns="arm", values="nmse")
    nl = N["mh"].NLINEAR_ONLINE
    for a in ("M_ONLY", "AIRLINE"):
        ok = pn[a].notna() & (pn[a] < 1)
        acc.append((names[a], float(np.exp(np.log(pn[a][ok] / nl[pn.index[ok]]).mean())), False))
    acc = sorted(acc, key=lambda z: z[1])
    ch = N["costh"]; mc = N["m_cost"]["Q1_ONS_Carga_SIN_2019_20"]
    cost = [(names["HOLT_WINTERS"], ch.loc["HOLT_WINTERS", "fp"], False, False), (names["M_ONLY"], mc, False, False),
            (names["LEBRE_V051"], ch.loc["LEBRE_V051", "fp"], False, True),
            (names["NLINEAR_ONLINE"], ch.loc["NLINEAR_ONLINE", "fp"], False, False), (names["DLINEAR_ONLINE"], ch.loc["DLINEAR_ONLINE", "fp"], False, False),
            (names["CHRONOS_BOLT_TINY"], 6e8, True, False), (names["CHRONOS_BOLT_SMALL"], 3e9, True, False), (names["CHRONOS2"], 8e9, True, False)]
    D = all_diagrams(L["diag"], acc, cost, "," if lang == "pt" else ".")
    S = [f"""<div class="cover-page">
<div class="cover-header"><div class="cover-logo-panel"><img class="cover-logo" src="{LOGO}" alt="LEBRE"></div>
<div class="cover-badge">{L['badge']}</div></div>
<div class="cover-main"><div class="cover-title">{L['title']}</div><div class="cover-subtitle">{L['subtitle']}</div>
<div class="cover-expansion">{L['expansion']}</div>
<div class="cover-meta-grid">""" + "".join(
        f'<div class="cover-meta-card"><div class="cover-meta-label">{k}</div><div class="cover-meta-value">{v}</div></div>'
        for k, v in L["meta"]) + f"""</div></div>
<div class="cover-footer"><div>{L['footer_l']}</div><div>{L['footer_r']}</div></div></div>"""]
    S += L["sections"](N, D)
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
    if len(sys.argv) > 1 and sys.argv[1] == "numbers":
        pd.set_option("display.width", 250)
        print(N["int"].round(4)); print(N["mh"].round(4).to_string()); print(N["rank"].round(2))
        print({k: round(v, 3) for k, v in N["geo_vs_nlin"].items()}); print(N["instab"].round(3)); print(N["cov"].round(3))
        print(N["costh"].round(2)); print(N["cost_task"].round(1)); print(N["wfinal"]); print(json.dumps(N["dec"]["part3"], indent=1))
        return
    jobs = [("pt", "LEBRE_v0.51r1_SPEC_PTBR.html", "LEBRE_ARCHITECTURE_v0.51_SPEC_r1_PTBR.pdf"),
            ("en", "LEBRE_v0.51r1_SPEC_EN.html", "LEBRE_ARCHITECTURE_v0.51_SPEC_r1_EN.pdf")]
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for lang, hname, pname in jobs:
        html = build(lang, N)
        for bad in ("experiments/", "experiments\\", "data/", "D:\\", "D:/", ".csv", ".py", "scratch"):
            assert bad not in re.sub(r"<(script|link|style)[^>]*>.*?</\1>|<link[^>]*>|data:image[^\"]+", "", html, flags=re.S), (lang, bad)
        (HERE / hname).write_text(html, encoding="utf-8")
        pdf = PDF_DIR / pname
        cmd = [EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=8000",
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
