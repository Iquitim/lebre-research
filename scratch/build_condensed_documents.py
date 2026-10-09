#!/usr/bin/env python3
"""
Full compilation script for LEBRE Condensed Reference Documents (EN & PTBR).
Generates HTML with inline SVGs, compiles via Edge headless, and audits via pypdfium2.
"""

import os
import sys
import base64
import subprocess
from pathlib import Path

WORKSPACE = Path(r".")
LOGO_PATH = WORKSPACE / "logo" / "LEBRE Logo.png"
DIAGRAMS_DIR = WORKSPACE / "docs" / "architecture" / "assets" / "diagrams"
HTML_DIR = WORKSPACE / "docs" / "architecture" / "pdf_source"
PDF_DIR = WORKSPACE / "docs" / "architecture" / "pdf"
QA_DIR = WORKSPACE / "scratch" / "pdf_qa"

HTML_DIR.mkdir(parents=True, exist_ok=True)
PDF_DIR.mkdir(parents=True, exist_ok=True)
QA_DIR.mkdir(parents=True, exist_ok=True)

with open(LOGO_PATH, "rb") as f:
    LOGO_B64 = base64.b64encode(f.read()).decode("ascii")

def read_svg(name):
    svg_file = DIAGRAMS_DIR / f"{name}.svg"
    with open(svg_file, "r", encoding="utf-8") as f:
        c = f.read()
    if "<?xml" in c:
        c = c.split("?>", 1)[1].strip()
    return c

svg_d1 = read_svg("lebre_high_level_architecture")
svg_d2 = read_svg("lebre_lifecycle")
svg_d3 = read_svg("lebre_data_control_flow")
svg_d4 = read_svg("lebre_shadow_probation")
svg_d5 = read_svg("lebre_quiescent_retention")
svg_d6 = read_svg("lebre_resource_elasticity")
svg_d7 = read_svg("lebre_v01_scope")
svg_d8 = read_svg("lebre_prequential_cycle")

CSS_BASE = """
@page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
    @top-left {
        content: "LEBRE Architecture Specification v0.1 — Reference Document";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        color: #64748b;
        font-weight: 500;
    }
    @top-right {
        content: "Status: FROZEN_WITH_SCOPE_LIMITS";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        color: #0284c7;
        font-weight: 600;
    }
    @bottom-left {
        content: "Codinome Lebre Research Suite • Confidential Scientific Preprint";
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        color: #94a3b8;
    }
    @bottom-right {
        content: "Page " counter(page);
        font-family: 'Segoe UI', system-ui, sans-serif;
        font-size: 7.5pt;
        font-weight: 700;
        color: #334155;
    }
}

@page:first {
    margin: 0;
    @top-left { content: none; }
    @top-right { content: none; }
    @bottom-left { content: none; }
    @bottom-right { content: none; }
}

* {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}

body {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    color: #1e293b;
    background: #ffffff;
    line-height: 1.48;
    font-size: 9pt;
    margin: 0;
    padding: 0;
}

.cover-page {
    page-break-after: always;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 55px 45px 40px 45px;
    background: linear-gradient(145deg, #09111e 0%, #0f172a 60%, #1e293b 100%);
    color: #ffffff;
}

.cover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    padding-bottom: 20px;
}

.cover-logo {
    max-width: 250px;
    height: auto;
}

.cover-badge {
    background: rgba(37, 99, 235, 0.25);
    border: 1px solid #3b82f6;
    color: #60a5fa;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 8pt;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.cover-main {
    margin-top: 30px;
}

.cover-title {
    font-size: 26pt;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.15;
    margin: 0 0 8px 0;
    color: #f8fafc;
}

.cover-subtitle {
    font-size: 14pt;
    font-weight: 400;
    color: #94a3b8;
    margin: 0 0 20px 0;
    line-height: 1.35;
}

.cover-expansion {
    font-size: 10.5pt;
    color: #38bdf8;
    font-weight: 500;
    margin-bottom: 25px;
    padding: 10px 16px;
    background: rgba(14, 165, 233, 0.1);
    border-left: 3px solid #0ea5e9;
    border-radius: 0 8px 8px 0;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 15px;
}

.cover-meta-card {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 10px 14px;
    border-radius: 6px;
}

.cover-meta-label {
    font-size: 7pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 3px;
}

.cover-meta-value {
    font-size: 8.5pt;
    font-weight: 600;
    color: #e2e8f0;
}

.cover-footer {
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    padding-top: 15px;
    font-size: 7.5pt;
    color: #64748b;
    display: flex;
    justify-content: space-between;
}

.page-break {
    page-break-before: always;
}

.no-break {
    page-break-inside: avoid;
    break-inside: avoid;
}

h1 {
    font-size: 15pt;
    font-weight: 800;
    color: #0f172a;
    border-bottom: 2px solid #0284c7;
    padding-bottom: 4px;
    margin-top: 20px;
    margin-bottom: 10px;
    letter-spacing: -0.01em;
}

h2 {
    font-size: 11.5pt;
    font-weight: 700;
    color: #1e293b;
    margin-top: 16px;
    margin-bottom: 6px;
    border-left: 3px solid #0ea5e9;
    padding-left: 8px;
}

h3 {
    font-size: 9.5pt;
    font-weight: 600;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 4px;
}

p {
    margin: 0 0 8px 0;
    text-align: justify;
}

ul, ol {
    margin: 0 0 8px 0;
    padding-left: 18px;
}

li {
    margin-bottom: 3px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0 14px 0;
    font-size: 7.8pt;
}

th, td {
    padding: 5px 7px;
    text-align: left;
    border: 1px solid #cbd5e1;
}

th {
    background-color: #f1f5f9;
    color: #0f172a;
    font-weight: 700;
}

tr:nth-child(even) td {
    background-color: #f8fafc;
}

.highlight-row td {
    background-color: #f0fdf4 !important;
    font-weight: 600;
}

.alert {
    padding: 8px 12px;
    border-radius: 5px;
    margin: 10px 0;
    font-size: 8pt;
    line-height: 1.4;
}

.alert-info {
    background-color: #f0f9ff;
    border-left: 4px solid #0284c7;
    color: #0369a1;
}

.alert-warning {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
}

.alert-danger {
    background-color: #fef2f2;
    border-left: 4px solid #ef4444;
    color: #b91c1c;
}

.diagram-container {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 10px;
    margin: 10px 0 14px 0;
    text-align: center;
    page-break-inside: avoid;
    break-inside: avoid;
}

.diagram-container svg {
    max-width: 100%;
    max-height: 380px;
    height: auto;
    display: block;
    margin: 0 auto;
}

.diagram-caption {
    font-size: 7.5pt;
    color: #475569;
    margin-top: 6px;
    font-style: italic;
    text-align: center;
}

.math-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-left: 3px solid #3b82f6;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 8.5pt;
    border-radius: 4px;
}

.badge {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 6.8pt;
    font-weight: 700;
    text-transform: uppercase;
}

.badge-blue { background: #dbeafe; color: #1d4ed8; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-amber { background: #fef3c7; color: #b45309; }
.badge-red { background: #fee2e2; color: #b91c1c; }

.toc-list {
    list-style-type: none;
    padding: 0;
    margin: 10px 0;
}

.toc-item {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 8.5pt;
}

.toc-title {
    font-weight: 600;
    color: #1e293b;
}

.toc-page {
    color: #0284c7;
    font-weight: 700;
}
"""

KATEX_HEAD = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false},
            {left: '\\(', right: '\\)', display: false},
            {left: '\\[', right: '\\]', display: true}
        ]
    });
});
</script>
"""

print("Compiling templates...")
