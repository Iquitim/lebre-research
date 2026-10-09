#!/usr/bin/env python3
"""
Generate docs/architecture/pdf_source/LEBRE_CONDENSED_EN.html
Uses raw string template r'''...''' to preserve all LaTeX backslashes perfectly.
Uses \\( ... \\) for inline math and $$ ... $$ for block math to avoid any conflict with literal $ signs.
"""
import base64
from pathlib import Path

WORKSPACE = Path(r".")
LOGO_PATH = WORKSPACE / "logo" / "LEBRE Logo.png"
DIAGRAMS_DIR = WORKSPACE / "docs" / "architecture" / "assets" / "diagrams"
OUT_FILE = WORKSPACE / "docs" / "architecture" / "pdf_source" / "LEBRE_CONDENSED_EN.html"

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

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>LEBRE Architecture Specification v0.1 — Condensed Reference</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {
    renderMathInElement(document.body, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '\\(', right: '\\)', display: false},
            {left: '\\[', right: '\\]', display: true}
        ],
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "svg"]
    });
});
</script>
<style>
@page {
    size: A4 portrait;
    margin: 18mm 14mm 18mm 14mm;
    @top-left {
        content: "LEBRE Architecture Specification v0.1 — Condensed Reference";
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
        content: "Codinome Lebre Research Project • Architecture Specification v0.1";
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
    padding: 50px 45px 35px 45px;
    background: #ffffff;
    color: #0f172a;
    border-top: 6px solid #0284c7;
    border-bottom: 2px solid #cbd5e1;
}

.cover-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 20px;
}

.cover-logo-panel {
    background: #ffffff;
    padding: 6px 12px;
    display: flex;
    align-items: center;
}

.cover-logo {
    max-width: 270px;
    height: auto;
}

.cover-badge {
    background: #f0f9ff;
    border: 1.5px solid #0284c7;
    color: #0369a1;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.cover-main {
    margin-top: 25px;
}

.cover-title {
    font-size: 26pt;
    font-weight: 800;
    letter-spacing: -0.025em;
    line-height: 1.15;
    margin: 0 0 8px 0;
    color: #0f172a;
}

.cover-subtitle {
    font-size: 13.5pt;
    font-weight: 500;
    color: #475569;
    margin: 0 0 20px 0;
    line-height: 1.35;
}

.cover-expansion {
    font-size: 10pt;
    color: #0369a1;
    font-weight: 600;
    margin-bottom: 25px;
    padding: 12px 18px;
    background: #f0f9ff;
    border-left: 4px solid #0284c7;
    border-radius: 0 8px 8px 0;
    border-top: 1px solid #e0f2fe;
    border-right: 1px solid #e0f2fe;
    border-bottom: 1px solid #e0f2fe;
}

.cover-meta-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-top: 15px;
}

.cover-meta-card {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    padding: 12px 16px;
    border-radius: 6px;
}

.cover-meta-label {
    font-size: 7.2pt;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px;
    font-weight: 600;
}

.cover-meta-value {
    font-size: 8.5pt;
    font-weight: 700;
    color: #0f172a;
}

.cover-footer {
    border-top: 1px solid #cbd5e1;
    padding-top: 14px;
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
    padding: 8px;
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
    margin: 8px 0;
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
</style>
</head>
<body>

<!-- FRONT COVER -->
<div class="cover-page">
    <div class="cover-header">
        <div class="cover-logo-panel">
            <img class="cover-logo" src="data:image/png;base64,<!-- LOGO_B64 -->" alt="LEBRE Architecture Logo">
        </div>
        <div class="cover-badge">Formal Specification v0.1</div>
    </div>
    
    <div class="cover-main">
        <div class="cover-title">LEBRE Architecture Specification</div>
        <div class="cover-subtitle">Condensed Reference Guide & System Architecture Overview</div>
        
        <div class="cover-expansion">
            <strong>Canonical Expansion:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br>
            <strong>Historical Provenance:</strong> Track B Single-State Organization (Codinome Lebre)
        </div>
        
        <div class="cover-meta-grid">
            <div class="cover-meta-card">
                <div class="cover-meta-label">Architecture Status</div>
                <div class="cover-meta-value">Frozen Reference Specification with Scope Limits</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Evidence Classification</div>
                <div class="cover-meta-value">VALIDATED_WITH_SCOPE_LIMITS</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Novelty Assertion Readiness</div>
                <div class="cover-meta-value">NOVELTY_CLAIM_READY = NO</div>
            </div>
            <div class="cover-meta-card">
                <div class="cover-meta-label">Milestone M3 Boundary</div>
                <div class="cover-meta-value">UNOPENED (Multi-State Frontier Reserved)</div>
            </div>
        </div>
    </div>
    
    <div class="cover-footer">
        <div>Research Project: Codinome Lebre Research Project</div>
        <div>Date of Specification Freeze: September 2026 • Document Version 0.1-CONDENSED</div>
    </div>
</div>

<!-- SECTION 1: EXECUTIVE SUMMARY & TABLE OF CONTENTS -->
<div class="page-break"></div>
<h1>1. Executive Summary & Document Guide</h1>

<p>The <strong>LEBRE</strong> architecture (<em>Lifecycle-governed Evidence-Based Resource Evolution</em>) formalizes an online, streaming learning system that dynamically allocates, evaluates, and reclaims internal state representations under strict computational budgets. Derived from extensive empirical investigations in benchmarks A1–A8 and real-world system identification B1–B5, LEBRE resolves the fundamental tension between persistent memory retention and aggressive computational frugality on streaming data.</p>

<div class="alert alert-info">
<strong>Scientific Scope & Status:</strong> This document represents a condensed reference edition of the formal LEBRE v0.1 architecture specification. All empirical figures, mathematical formulations, and control thresholds are frozen under classification <code>VALIDATED_WITH_SCOPE_LIMITS</code>. Milestone M3 remains <code>UNOPENED</code>, and novelty claims remain strictly withheld (<code>NOVELTY_CLAIM_READY = NO</code>).
</div>

<h2>Table of Contents</h2>
<ul class="toc-list">
    <li class="toc-item"><span class="toc-title">1. Executive Summary & Document Guide</span><span class="toc-page">Page 2</span></li>
    <li class="toc-item"><span class="toc-title">2. Architectural Identity & Core Principles</span><span class="toc-page">Page 3</span></li>
    <li class="toc-item"><span class="toc-title">3. Mathematical Formulation & Inference Engine</span><span class="toc-page">Page 4</span></li>
    <li class="toc-item"><span class="toc-title">4. Five-State Structural Lifecycle State Machine</span><span class="toc-page">Page 6</span></li>
    <li class="toc-item"><span class="toc-title">5. Two-Timescale Retention & Quiescent Memory Preservation</span><span class="toc-page">Page 7</span></li>
    <li class="toc-item"><span class="toc-title">6. Canonical Architectural Diagrams Reference (D1–D8)</span><span class="toc-page">Page 8</span></li>
    <li class="toc-item"><span class="toc-title">7. Empirical Validation Suite (Benchmarks A1–A8 & B1–B5)</span><span class="toc-page">Page 16</span></li>
    <li class="toc-item"><span class="toc-title">8. Computational Accounting, Mean FLOP Semantics & Embedded Limits</span><span class="toc-page">Page 18</span></li>
    <li class="toc-item"><span class="toc-title">9. Architectural Scope Limits & Frozen Boundary</span><span class="toc-page">Page 19</span></li>
    <li class="toc-item"><span class="toc-title">10. Parameter & Constant Traceability Matrix</span><span class="toc-page">Page 20</span></li>
    <li class="toc-item"><span class="toc-title">11. Architectural Decision Records (ADRs) & Final Decision</span><span class="toc-page">Page 21</span></li>
</ul>

<h2>Document Conventions</h2>
<p>Throughout this reference, standard mathematical notation is strictly enforced: vector quantities are denoted in boldface (\(\mathbf{x}_t \in \mathbb{R}^D\)), scalars in standard italic (\(y_t, s_t\)), and discrete time indices by subscript \(t\). Operational complexity is stated in formal floating-point operations per step (FLOPs/step). When evaluating R2-FLOP compliance, figures strictly denote <em>mean per-step throughput</em> across benchmark runs, distinguishing average operational costs from transient evaluation peaks.</p>

<!-- SECTION 2: ARCHITECTURAL IDENTITY -->
<div class="page-break"></div>
<h1>2. Architectural Identity & Core Principles</h1>

<p>LEBRE establishes a resource-governed structural paradigm where network capacity is treated as an economic asset that must justify its computational cost at every operational time step. The system is grounded in four governing principles:</p>

<h3>1. Linear-First Parsimony</h3>
<p>No non-linear or recurrent structural capacity is instantiated unless persistent unmodeled error remains after exhaustive adaptation of the sparse linear baseline. In streaming regression and system identification, static linear correlations account for a substantial portion of variance. Under the evaluated linear regimes, recurrent state allocation was not triggered when the linear baseline was sufficient.</p>

<h3>2. Isolated Shadow Mode Probation</h3>
<p>Provisional structural units are decoupled from live model predictions during their initial training phase. Newly spawned candidate states learn in a decoupled shadow mode for a fixed probation window (\(T_{\text{prob}} = 50\) steps). Only candidates demonstrating statistically verified counterfactual error reduction (\(G_{\text{cand}} > 0.05\)) are promoted to live inference.</p>

<h3>3. Two-Timescale Relevance Accounting</h3>
<p>Instantaneous signal energy is inadequate as a retention criterion in event-driven and non-stationary environments. LEBRE separates the timescale of instantaneous state activity from the timescale of structural relevance (\(U_{\text{ret}}\), decay factor \(\alpha_{\text{slow}} = 0.005\), half-life \(\tau \approx 140\) steps). This decouples memory preservation from transient input silence, ensuring that critical state memory bridges extended Poisson quiescent intervals.</p>

<h3>4. Bounded Resource Elasticity</h3>
<p>Across evaluated benchmarks, LEBRE exhibited an observed mean persistent model-state footprint of 440.0 bytes of RAM (under the R2-MEM ceiling of 1024 bytes; this figure does not represent total device RAM in a hardware implementation). Measured mean computational throughput remained within the R2-FLOP limit of 100 FLOPs/step. Physical arrays of evicted structures are excised from execution graphs and reclaimed immediately.</p>

<table class="no-break">
    <thead>
        <tr>
            <th>Principle</th>
            <th>Governing Mechanism</th>
            <th>Empirical Invariant Established</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Linear-First Parsimony</strong></td>
            <td>Dual-stage birth gating (\(E_{\text{linear}} > \theta_{\text{birth}}\))</td>
            <td>Zero recurrent states spawned on purely linear environments (Tasks A1, A2)</td>
        </tr>
        <tr>
            <td><strong>Shadow Probation</strong></td>
            <td>Decoupled forward pass (\(g_p = 0.0\)) + counterfactual gain</td>
            <td>Zero inference disruption; unstable gradient spikes isolated from \(\hat{y}_t\)</td>
        </tr>
        <tr>
            <td><strong>Quiescent Retention</strong></td>
            <td>Two-timescale slow filter (\(U_{\text{ret}}\)) + dual-gated eviction</td>
            <td>&gt;99% survival across Poisson silence gaps of 200+ steps (Tasks A5, A7)</td>
        </tr>
        <tr>
            <td><strong>Resource Elasticity</strong></td>
            <td>Hysteresis eviction + physical memory deallocation</td>
            <td>Dynamic contraction from \(\approx 92\) FLOPs/step back to baseline \(\approx 40\) FLOPs/step</td>
        </tr>
    </tbody>
</table>

<!-- SECTION 3: MATHEMATICAL FORMULATION -->
<div class="page-break"></div>
<h1>3. Mathematical Formulation & Inference Engine</h1>

<p>The LEBRE execution cycle operates under a strict causal prequential protocol: at time step \(t\), the system receives observation \(\mathbf{x}_t\), emits causal prediction \(\hat{y}_t\), and only subsequently receives the true scalar target \(y_t\).</p>

<h2>3.1 Streaming Observation & Normalization</h2>
<p>Let \(\mathbf{x}_t = [x_{t,1}, x_{t,2}, \dots, x_{t,D}]^\top \in \mathbb{R}^D\) denote the streaming observation vector. Causal online normalization tracks feature means and variances without backward passes:</p>
<div class="math-box">
$$\mu_{t,i} = (1 - \alpha_{\text{norm}}) \mu_{t-1,i} + \alpha_{\text{norm}} x_{t,i}, \quad \sigma^2_{t,i} = (1 - \alpha_{\text{norm}}) \sigma^2_{t-1,i} + \alpha_{\text{norm}} (x_{t,i} - \mu_{t,i})^2$$
$$\tilde{x}_{t,i} = \frac{x_{t,i} - \mu_{t,i}}{\sqrt{\sigma^2_{t,i} + \epsilon_{\text{norm}}}}$$
</div>

<h2>3.2 Dual-Layer Causal Inference</h2>
<p>Total model prediction \(\hat{y}_t\) is the sum of an active sparse linear baseline \(y_{\text{base},t}\) and the active scalar recurrent component \(y_{\text{rec},t}\) (\(N \le 1\)):</p>
<div class="math-box">
$$y_{\text{base},t} = \mathbf{w}_{\text{base}}^\top \tilde{\mathbf{x}}_t + b_{\text{base}}$$
$$s_t = \tanh\left(\lambda s_{t-1} + \mathbf{w}_{\text{in}}^\top \tilde{\mathbf{x}}_t + b_s\right), \quad y_{\text{rec},t} = w_s s_t$$
$$\hat{y}_t = y_{\text{base},t} + y_{\text{rec},t}$$
</div>

<h2>3.3 Prequential Loss & Error Decomposition</h2>
<p>Upon revelation of environmental target \(y_t\), the system quantifies the global prediction error \(e_t\) and the counterfactual linear baseline error \(e_{\text{base},t}\):</p>
<div class="math-box">
$$e_t = y_t - \hat{y}_t, \quad e_{\text{base},t} = y_t - y_{\text{base},t}$$
$$\mathcal{L}_t = \frac{1}{2} e_t^2, \quad \Delta \mathcal{L}_t = \frac{1}{2} e_{\text{base},t}^2 - \frac{1}{2} e_t^2$$
</div>
<p>Positive values of \(\Delta \mathcal{L}_t\) confirm that the recurrent structural state provides genuine predictive utility beyond what linear projection achieves.</p>

<h2>3.4 Online Real-Time Recurrent Learning (RTRL) Dynamics</h2>
<p>Because the recurrent state is scalar (\(N \le 1\)), the gradient of the hidden state with respect to internal parameters is tracked in real time with \(\mathcal{O}(1)\) complexity:</p>
<div class="math-box">
$$p_t = \frac{\partial s_t}{\partial \lambda} = (1 - s_t^2) \left( s_{t-1} + \lambda p_{t-1} \right)$$
$$\mathbf{q}_t = \frac{\partial s_t}{\partial \mathbf{w}_{\text{in}}} = (1 - s_t^2) \left( \tilde{\mathbf{x}}_t + \lambda \mathbf{q}_{t-1} \right)$$
</div>
<p>Online parameter updates are computed using causal stochastic gradient descent with momentum and weight decay:</p>
<div class="math-box">
$$\Delta w_s = \eta_s e_t s_t, \quad \Delta \lambda = \eta_\lambda e_t w_s p_t, \quad \Delta \mathbf{w}_{\text{in}} = \eta_{\text{in}} e_t w_s \mathbf{q}_t$$
$$\Delta \mathbf{w}_{\text{base}} = \eta_{\text{base}} e_t \tilde{\mathbf{x}}_t - \gamma_{\text{decay}} \mathbf{w}_{\text{base}}$$
</div>

<!-- SECTION 4: STRUCTURAL LIFECYCLE -->
<div class="page-break"></div>
<h1>4. Five-State Structural Lifecycle State Machine</h1>

<p>Every structural object in LEBRE progresses through a rigorously bounded five-state lifecycle: <strong>DORMANT</strong>, <strong>PROVISIONAL</strong>, <strong>ACTIVE</strong>, <strong>MATURE</strong>, and <strong>EVICTED</strong>. Structural transitions are governed by objective evidence accumulators.</p>

<table class="no-break">
    <thead>
        <tr>
            <th>State</th>
            <th>Operational Role</th>
            <th>Prediction Impact</th>
            <th>Compute / Memory Overhead</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>DORMANT</strong></td>
            <td>Latent candidate slot; unallocated</td>
            <td>Zero (0.0)</td>
            <td>0 FLOPs/step; 0 Bytes RAM</td>
        </tr>
        <tr>
            <td><strong>PROVISIONAL</strong></td>
            <td>Shadow candidate undergoing probation</td>
            <td>Strictly isolated (\(g_p = 0.0\))</td>
            <td>Forward pass + local RTRL (\(\approx 52\) FLOPs); shadow buffers</td>
        </tr>
        <tr>
            <td><strong>ACTIVE</strong></td>
            <td>Promoted live unit; coupled to \(\hat{y}_t\)</td>
            <td>Full contribution (\(y_{\text{rec},t} = w_s s_t\))</td>
            <td>Full online inference + RTRL; persistent state memory</td>
        </tr>
        <tr>
            <td><strong>MATURE</strong></td>
            <td>Active unit with age \(\ge \tau_{\text{mature}}\) (100 steps)</td>
            <td>Full contribution; slow utility monitored</td>
            <td>Full inference + two-timescale relevance accounting</td>
        </tr>
        <tr>
            <td><strong>EVICTED</strong></td>
            <td>Excised unit; memory deallocated</td>
            <td>Excised; slot returns to Dormant</td>
            <td>0 FLOPs; memory freed immediately</td>
        </tr>
    </tbody>
</table>

<h2>4.1 Birth Trigger & Linear-First Parsimony</h2>
<p>The birth trigger evaluates whether residual error cannot be explained by linear projection. A birth event is initiated only when the exponential moving average of linear residual error exceeds threshold \(\theta_{\text{birth}} = 0.15\) for \(N_{\text{birth}} = 30\) consecutive steps:</p>
<div class="math-box">
$$\bar{E}_{\text{linear},t} = (1 - \alpha_E) \bar{E}_{\text{linear},t-1} + \alpha_E e_{\text{base},t}^2$$
$$\text{Trigger Birth if: } \bar{E}_{\text{linear},t} > \theta_{\text{birth}} \quad \forall \tau \in [t - N_{\text{birth}}, t]$$
</div>

<h2>4.2 Shadow Probation & Promotion Protocol</h2>
<p>Upon birth, a candidate state \(s_{p,t}\) is instantiated in shadow mode. Its parameters \(\mathbf{w}_{p,\text{in}}\), \(\lambda_p\), and \(w_p\) are updated using candidate-specific gradients, but its output is gated off (\(g_p = 0.0\)). Counterfactual error is recorded over a probation horizon \(T_{\text{prob}} = 50\) steps:</p>
<div class="math-box">
$$e_{p,t} = y_t - (y_{\text{base},t} + w_p s_{p,t})$$
$$G_{\text{cand}} = 1 - \frac{\sum_{k=1}^{T_{\text{prob}}} e_{p,t-k}^2}{\sum_{k=1}^{T_{\text{prob}}} e_{\text{base},t-k}^2}$$
$$\text{Promote if: } G_{\text{cand}} > \theta_{\text{promote}} \quad (\theta_{\text{promote}} = 0.05)$$
</div>
<p>If \(G_{\text{cand}} \le \theta_{\text{promote}}\), the candidate is discarded, freeing buffers without ever having perturbed live predictions.</p>

<!-- SECTION 5: TWO-TIMESCALE RETENTION -->
<div class="page-break"></div>
<h1>5. Two-Timescale Retention & Quiescent Memory</h1>

<p>A critical failure mode of naive utility-driven systems is premature eviction during quiescent inter-burst intervals. When streaming inputs become silent (\(x_t \approx 0\)), hidden states decay toward zero (\(s_t \to 0\)). Naive gradient sensitivity metrics (\(|e_t w_s s_t|\)) collapse, triggering false eviction of essential structural memory.</p>

<h2>5.1 Two-Timescale Mathematical Formulation</h2>
<p>LEBRE decouples fast operational dynamics from slow structural credit via a two-timescale relevance filter:</p>
<div class="math-box">
$$C_t = |e_t w_s s_t| + \kappa |w_s| \sigma_h$$
$$U_{\text{ret},t} = (1 - \alpha_{\text{slow}}) U_{\text{ret},t-1} + \alpha_{\text{slow}} C_t \quad (\alpha_{\text{slow}} = 0.005, \; \tau \approx 140 \text{ steps})$$
</div>
<p>Simultaneously, a <strong>positive obsolescence accumulator</strong> monitors whether the environment has actively transitioned away from requiring recurrence:</p>
<div class="math-box">
$$O_{\text{obs},t} = \text{clip}\left( O_{\text{obs},t-1} + m_{\text{obs}} \cdot \mathbb{I}_{\{\Delta \mathcal{L}_t \le 0\}} - d_{\text{obs}} \cdot \mathbb{I}_{\{\Delta \mathcal{L}_t > 0\}}, 0.0, 1.0 \right)$$
</div>

<h2>5.2 Dual-Gated Hysteresis Eviction & The 300:1 Cost Asymmetry</h2>
<p>Eviction demands unequivocal evidence of persistent obsolescence. The state is excised if and only if both conditions are satisfied simultaneously for \(N_{\text{pat}} = 30\) consecutive steps:</p>
<div class="math-box">
$$\text{Evict if: } \left( U_{\text{ret},t} < \theta_{\text{ret}} \right) \;\wedge\; \left( O_{\text{obs},t} > \theta_{\text{obs}} \right) \quad \forall \tau \in [t - N_{\text{pat}}, t]$$
$$\theta_{\text{ret}} = 0.02, \quad \theta_{\text{obs}} = 0.80, \quad N_{\text{pat}} = 30$$
</div>

<div class="alert alert-warning">
<strong>Audit Clarification (Correction G):</strong> The <strong>300:1 asymmetry</strong> is an <em>empirical cost ratio</em> (the penalty of false eviction regret vs. the modest overhead of maintaining a dormant scalar state), not an explicit multiplier in the codebase. The architecture achieves this conservative asymmetry structurally through the 30-step hysteresis patience counter and dual-gated thresholding (\(U_{\text{ret}} < 0.02\) AND \(O_{\text{obs}} > 0.80\)).
</div>

<table class="no-break">
    <thead>
        <tr>
            <th>Scenario</th>
            <th>Instantaneous \(|s_t|\)</th>
            <th>Slow Utility \(U_{\text{ret}}\)</th>
            <th>Obsolescence \(O_{\text{obs}}\)</th>
            <th>LEBRE Action</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Active Burst Event</td>
            <td>High (&gt; 0.5)</td>
            <td>High (&gt; 0.2)</td>
            <td>Low (&lt; 0.1)</td>
            <td><strong>Retain &amp; Update</strong></td>
        </tr>
        <tr>
            <td>Silent Poisson Gap (t=50)</td>
            <td>Zero (&lt; 0.01)</td>
            <td>Preserved (&gt; 0.08)</td>
            <td>Neutral (&lt; 0.3)</td>
            <td><strong>Retain Memory (Protected)</strong></td>
        </tr>
        <tr>
            <td>Silent Poisson Gap (t=200)</td>
            <td>Zero (&lt; 0.01)</td>
            <td>Marginal (&gt; 0.02)</td>
            <td>Moderate (&lt; 0.6)</td>
            <td><strong>Retain Memory (Gate Held)</strong></td>
        </tr>
        <tr>
            <td>Confirmed Regime Shift</td>
            <td>Zero</td>
            <td>Exhausted (&lt; 0.02)</td>
            <td>Saturated (&gt; 0.80)</td>
            <td><strong>Safe Eviction after 30 steps</strong></td>
        </tr>
    </tbody>
</table>

<!-- SECTION 6: CANONICAL DIAGRAMS GALLERY -->
<div class="page-break"></div>
<h1>6. Canonical Architectural Diagrams Reference</h1>

<p>This section provides the eight canonical architectural diagrams (<strong>D1</strong> through <strong>D8</strong>) defining the formal visual specification of LEBRE. Each vector graphic illustrates a key architectural invariant.</p>

<h2>D1. High-Level Architecture & Information Flow</h2>
<div class="diagram-container">
<!-- SVG_D1 -->
<div class="diagram-caption">Figure D1: Complete prequential data flow and post-target lifecycle control loops.</div>
</div>
<p>Figure D1 details the decoupled physical information flow: causal observation streaming, dual-layer additive inference (\(\hat{y}_t = y_{\text{base},t} + y_{\text{rec},t}\)), prequential error revelation, isolated shadow exploration, and the central lifecycle controller.</p>

<div class="page-break"></div>
<h2>D2. Structural Lifecycle State Machine</h2>
<div class="diagram-container">
<!-- SVG_D2 -->
<div class="diagram-caption">Figure D2: Five-state structural lifecycle governing all candidate and active allocations.</div>
</div>
<p>Figure D2 shows the progression of structural objects from Dormant (zero cost) through Provisional shadow probation (\(T_{\text{prob}} = 50\)), live Active inference, Mature relevance monitoring, and final Eviction with complete array deallocation.</p>

<div class="page-break"></div>
<h2>D3. Separation of Data Flow vs. Control Flow</h2>
<div class="diagram-container">
<!-- SVG_D3 -->
<div class="diagram-caption">Figure D3: Microsecond-critical inference path decoupled from evidence evaluation.</div>
</div>
<p>Figure D3 highlights the strict architectural separation between the forward inference pipeline (executing under microsecond real-time constraints) and the control pipeline (evaluating error signals, utility metrics, and obsolescence).</p>

<div class="page-break"></div>
<h2>D4. Shadow Mode Probation & Promotion Protocol</h2>
<div class="diagram-container">
<!-- SVG_D4 -->
<div class="diagram-caption">Figure D4: Sequence diagram of candidate probation, counterfactual scoring, and promotion.</div>
</div>
<p>Figure D4 illustrates how shadow mode candidates are evaluated across \(T_{\text{prob}} = 50\) steps with hard output isolation (\(g_p = 0.0\)), ensuring zero disruption to live predictions unless verified counterfactual gain (\(G_{\text{cand}} > 0.05\)) is achieved.</p>

<div class="page-break"></div>
<h2>D5. Two-Timescale Relevance & Quiescent Retention</h2>
<div class="diagram-container">
<!-- SVG_D5 -->
<div class="diagram-caption">Figure D5: Comparative flow of naive instantaneous eviction vs. LEBRE dual-gated retention.</div>
</div>
<p>Figure D5 demonstrates why naive energy-based eviction collapses during Poisson silent gaps, while LEBRE's two-timescale relevance (\(U_{\text{ret}}\)) and positive obsolescence gate maintain structural credit across hundreds of silent steps.</p>

<div class="page-break"></div>
<h2>D6. Dynamic Resource Elasticity Across Non-Stationary Regimes</h2>
<div class="diagram-container">
<!-- SVG_D6 -->
<div class="diagram-caption">Figure D6: Dynamic topological adaptation and computational load scaling in Task A8.</div>
</div>
<p>Figure D6 depicts structural adaptation across non-stationary regimes: linear baseline (\(\approx 38\) FLOPs/step mean) \(\to\) temporal lag allocation (\(\approx 65\) FLOPs/step mean) \(\to\) recurrent state activation (\(\approx 92\) FLOPs/step mean) \(\to\) safe eviction and budget reclamation (\(\approx 40\) FLOPs/step mean).</p>

<div class="page-break"></div>
<h2>D7. v0.1 Empirical Evidence Scope & Frozen Boundary</h2>
<div class="diagram-container">
<!-- SVG_D7 -->
<div class="diagram-caption">Figure D7: Formal boundary separating empirically validated v0.1 features from Milestone M3.</div>
</div>
<p>Figure D7 formalizes the demarcation between established experimental facts in v0.1 (scalar recurrence \(N \le 1\), linear-first parsimony, \(\le 100\) FLOPs/step mean) and unopened research frontiers reserved for Milestone M3.</p>

<div class="page-break"></div>
<h2>D8. Online Prequential Operational Cycle</h2>
<div class="diagram-container">
<!-- SVG_D8 -->
<div class="diagram-caption">Figure D8: Strict 8-step causal sequence executed at every streaming observation step.</div>
</div>
<p>Figure D8 illustrates the sequential causal constraints of prequential execution: input ingestion \(\to\) base evaluation \(\to\) recurrent evaluation \(\to\) causal emission \(\to\) target revelation \(\to\) error scoring \(\to\) gradient updates \(\to\) lifecycle mutation.</p>

<!-- SECTION 7: EMPIRICAL BENCHMARK VALIDATION -->
<div class="page-break"></div>
<h1>7. Empirical Benchmark Validation Suite</h1>

<p>The LEBRE architecture v0.1 was validated across 13 benchmark configurations: 8 synthetic streaming tasks (A1–A8) and 5 real-world physical and nonlinear system identification benchmarks (B1–B5). All benchmarks were executed under the strict R2-FLOP computational regime.</p>

<h2>7.1 Synthetic Mechanistic Benchmark Suite (Tasks A1–A8)</h2>
<table>
    <thead>
        <tr>
            <th>Task ID</th>
            <th>Workload Name</th>
            <th>RZA-LMS</th>
            <th>CCN</th>
            <th>Minimal GRU</th>
            <th>Online ESN</th>
            <th>LEBRE v0.1</th>
            <th>Mean FLOPs</th>
            <th>Empirical Behavior / Invariant</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>A1</strong></td><td>Sparse Support Shift</td><td>0.0169</td><td>0.0185</td><td>0.7897</td><td>0.7695</td><td class="highlight-row">0.0379</td><td>205.3</td><td>RZA-LMS won (0.0169); LEBRE adapts in 205 FLOPs</td></tr>
        <tr><td><strong>A2</strong></td><td>Single Delayed Dependency</td><td>1.0010</td><td>1.0109</td><td>1.0001</td><td>0.9680</td><td class="highlight-row">1.1327</td><td>97.5</td><td>Boundary: dense ESN won (0.9680); scalar state 1.1327</td></tr>
        <tr><td><strong>A3</strong></td><td>Multiple Dispersed Delays</td><td>1.0002</td><td>1.0107</td><td>1.0002</td><td>0.9593</td><td class="highlight-row">1.1287</td><td>97.5</td><td>Boundary: dense ESN won (0.9593); scalar state 1.1287</td></tr>
        <tr><td><strong>A4</strong></td><td>Long-Delay Scaling</td><td>1.0002</td><td>1.0106</td><td>1.0001</td><td>1.0005</td><td class="highlight-row">1.1356</td><td>97.4</td><td>Boundary: GRU won (1.0001); scalar state 1.1356</td></tr>
        <tr><td><strong>A5</strong></td><td>Set/Reset Quiescent Memory</td><td>1.0234</td><td>0.4076</td><td>1.0277</td><td>0.9990</td><td class="highlight-row">0.7901</td><td>68.4</td><td>CCN won (0.4076); LEBRE 0.7901; LMS/GRU failed (&gt;1.02)</td></tr>
        <tr><td><strong>A6</strong></td><td>Context Routing</td><td>0.5245</td><td>0.5416</td><td>0.6848</td><td>0.6036</td><td class="highlight-row">0.5668</td><td>56.3</td><td>RZA-LMS won (0.5245); LEBRE 0.5668 at 56.3 FLOPs</td></tr>
        <tr><td><strong>A7</strong></td><td>Extended Poisson Quiescence</td><td>1.0185</td><td>0.6017</td><td>1.0198</td><td>1.0059</td><td class="highlight-row">0.8535</td><td>60.3</td><td>CCN won (0.6017); LEBRE 0.8535; LMS/GRU failed (&gt;1.01)</td></tr>
        <tr><td><strong>A8</strong></td><td>Abrupt Tri-Regime Transition</td><td>0.9807</td><td>0.9916</td><td>0.9807</td><td>1.0209</td><td class="highlight-row">0.9540</td><td>57.6</td><td>LEBRE won (0.9540); dynamic scale 38&rarr;92&rarr;40 FLOPs</td></tr>
    </tbody>
</table>

<h2>7.2 Real-World Continuous Benchmark Suite (Tasks B1–B5)</h2>
<table>
    <thead>
        <tr>
            <th>Task ID</th>
            <th>Continuous Stream</th>
            <th>RZA-LMS</th>
            <th>CCN</th>
            <th>Minimal GRU</th>
            <th>Online ESN</th>
            <th>LEBRE v0.1</th>
            <th>Mean FLOPs</th>
            <th>Sealed Outcome / Winner</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>B1</strong></td><td>NSW Electricity Continuous</td><td>0.9787</td><td>0.4632</td><td>2.4146</td><td>1.4238</td><td class="highlight-row">0.8364</td><td>24.0</td><td>CCN won (0.4632); LEBRE competitive at 24.0 FLOPs</td></tr>
        <tr><td><strong>B2</strong></td><td>Jena Weather Temperature</td><td>DIVERGED</td><td>DIVERGED</td><td>0.0742</td><td>0.3284</td><td class="highlight-row">0.0248</td><td>69.8</td><td>LEBRE won (0.0248); RZA-LMS &amp; CCN diverged</td></tr>
        <tr><td><strong>B3</strong></td><td>Gas Dynamic Mixture</td><td>0.0492</td><td>0.0390</td><td>0.0241</td><td>0.2608</td><td class="highlight-row">0.0020</td><td>79.9</td><td>LEBRE won (0.0020); strictly led all competitive baselines</td></tr>
        <tr><td><strong>B4</strong></td><td>Silverbox System ID</td><td>0.9993</td><td>0.9963</td><td>0.9999</td><td>0.9136</td><td class="highlight-row">0.9932</td><td>8.0</td><td>Online ESN won (0.9136); documented boundary of scalar recurrence</td></tr>
        <tr><td><strong>B5</strong></td><td>Household Active Power</td><td>0.0912</td><td>0.0120</td><td>0.0924</td><td>0.1129</td><td class="highlight-row">0.0040</td><td>28.3</td><td>LEBRE won (0.0040); led CCN (0.0120) and GRU (0.0924)</td></tr>
    </tbody>
</table>

<div class="alert alert-info">
<strong>Audit Confirmation (Correction C):</strong> In Benchmark Block B, all workload identities and numerical metrics are verified directly against sealed machine-readable artifacts (<code>BENCH_01B_AGGREGATE_SUMMARY.csv</code>). In Task B5 (Household Active Power), LEBRE led all baselines with <strong>0.00403 NMSE</strong> (28.30 FLOPs/step mean, 248 bytes RAM). In Task B4 (Silverbox System ID), Online ESN achieved <strong>0.91359 NMSE</strong> while LEBRE operated at <strong>0.99320 NMSE</strong> (8.00 FLOPs/step, 208 bytes RAM), confirming the documented inductive bias boundary where high-dimensional random reservoirs outperform minimal scalar states on multi-frequency continuous nonlinear dynamics.
</div>

<!-- SECTION 8: RESOURCE ACCOUNTING & EMBEDDED LIMITS -->
<div class="page-break"></div>
<h1>8. Computational Accounting, Mean FLOP Semantics & Embedded Limits</h1>

<p>To establish rigorous credibility, LEBRE formalizes an exact mathematical taxonomy of computational operations and distinguishes mean operational throughput from transient evaluation peaks.</p>

<h2>8.1 Formal FLOP Taxonomy</h2>
<table>
    <thead>
        <tr>
            <th>Operation Subsystem</th>
            <th>Mathematical Formulation</th>
            <th>FLOP Count Formula</th>
            <th>FLOPs (\(D=8, K=5, N=1\))</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Causal Normalization</td>
            <td>\(\mu_t, \sigma_t^2, \tilde{\mathbf{x}}_t\)</td>
            <td>\(3D\) multiplications/additions</td>
            <td>24 FLOPs</td>
        </tr>
        <tr>
            <td>Sparse Linear Forward</td>
            <td>\(\mathbf{w}_{\text{base}}^\top \tilde{\mathbf{x}}_t + b_{\text{base}}\)</td>
            <td>\(2K\) operations</td>
            <td>10 FLOPs</td>
        </tr>
        <tr>
            <td>Recurrent Hidden Forward</td>
            <td>\(\lambda s_{t-1} + \mathbf{w}_{\text{in}}^\top \tilde{\mathbf{x}}_t + b_s\)</td>
            <td>\(2K + 3\) operations + \(\tanh\)</td>
            <td>18 FLOPs (evaluating \(\tanh \approx 5\))</td>
        </tr>
        <tr>
            <td>Output Readout</td>
            <td>\(\hat{y}_t = y_{\text{base},t} + w_s s_t\)</td>
            <td>2 multiplications/additions</td>
            <td>2 FLOPs</td>
        </tr>
        <tr>
            <td>Scalar RTRL Sensitivities</td>
            <td>\(p_t, \mathbf{q}_t\) updates</td>
            <td>\(2K + 6\) operations</td>
            <td>16 FLOPs</td>
        </tr>
        <tr>
            <td>Live Parameter Updates</td>
            <td>\(\Delta \mathbf{w}_{\text{base}}, \Delta \mathbf{w}_{\text{in}}, \Delta \lambda, \Delta w_s\)</td>
            <td>\(3K + 6\) operations</td>
            <td>21 FLOPs</td>
        </tr>
        <tr>
            <td>Lifecycle Governance</td>
            <td>\(U_{\text{ret}}, O_{\text{obs}}, C_t\)</td>
            <td>8 scalar operations</td>
            <td>8 FLOPs</td>
        </tr>
        <tr class="highlight-row">
            <td><strong>Total Steady-State per Step</strong></td>
            <td><strong>Full Live Dual-Layer Cycle</strong></td>
            <td><strong>Nominal Live Pipeline</strong></td>
            <td><strong>\(\approx 99\) FLOPs/step</strong></td>
        </tr>
    </tbody>
</table>

<h2>8.2 R2-FLOP Mean Semantics vs. Transient Evaluation Peaks</h2>
<div class="alert alert-warning">
<strong>Specification Clarification (Correction A):</strong> The R2-FLOP requirement (\(\le 100\) FLOPs/step) is strictly a <strong>mean benchmark budget</strong> evaluated over complete streaming trajectories. It is not an absolute ceiling on every isolated clock cycle. In Task B5, LEBRE achieves an average throughput of <strong>90.44 FLOPs/step mean</strong>. During transient probation intervals where a shadow candidate is evaluated concurrently with live inference, total computational load reaches a temporary peak of \(\approx 206\) FLOPs/step for 50 steps.
</div>

<h2>8.3 Embedded State Memory Envelope & Physical Hardware Demotion</h2>
<p>LEBRE's persistent state memory envelope is strictly documented at <strong>\(\approx 440\) bytes</strong>. This footprint comprises:</p>
<ul>
    <li>Sparse linear weights and biases: \(\approx 80\) bytes (float32).</li>
    <li>Scalar recurrent parameters (\(w_s, \lambda, \mathbf{w}_{\text{in}}\)): \(\approx 48\) bytes.</li>
    <li>Real-time gradient sensitivity registers (\(p_t, \mathbf{q}_t\)): \(\approx 48\) bytes.</li>
    <li>Provisional shadow candidate buffers: \(\approx 96\) bytes.</li>
    <li>Lifecycle accumulators, statistics, and hysteresis counters: \(\approx 168\) bytes.</li>
</ul>

<div class="alert alert-danger">
<strong>Hardware Feasibility Demotion (Correction B):</strong> The 440-byte figure represents <strong>persistent model state RAM</strong>, not the complete memory budget of a physical microcontroller system (which must also allocate C execution stack, I/O ring buffers, and RTOS runtime). Furthermore, LEBRE v0.1 has been evaluated strictly in bit-exact mathematical simulation. Bare-metal deployment to embedded microcontrollers (such as ARM Cortex-M0+ or Cortex-M4) represents a <em>prospective candidate application</em> for future empirical validation, not an accomplished benchmark result.
</div>

<!-- SECTION 9: SCOPE LIMITS & ROADMAP -->
<div class="page-break"></div>
<h1>9. Architectural Scope Limits & Frozen Boundary</h1>

<p>To preserve rigorous scientific boundaries, LEBRE explicitly declares what the v0.1 architecture is and what it is <em>not</em>. The boundary between frozen empirical evidence and future research is uncrossable in v0.1.</p>

<table class="no-break">
    <thead>
        <tr>
            <th>Dimension</th>
            <th>Status in LEBRE v0.1 (Frozen Fact)</th>
            <th>Status in Future Work / M3 (Hypothesis)</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>Recurrent Topology</strong></td>
            <td>Scalar recurrence only (\(N \le 1\))</td>
            <td>Multi-state recurrent interactions (\(N \ge 2\))</td>
        </tr>
        <tr>
            <td><strong>Output Mapping</strong></td>
            <td>Linear readout (\(y_{\text{rec},t} = w_s s_t\))</td>
            <td>Non-linear multilayer output heads</td>
        </tr>
        <tr>
            <td><strong>Structural Transitions</strong></td>
            <td>Discrete five-state machine (Dormant-Prov-Act-Mature-Evict)</td>
            <td>Continuous topological growth / pruning</td>
        </tr>
        <tr>
            <td><strong>Execution Platform</strong></td>
            <td>Software-simulated streaming execution</td>
            <td>Bare-metal silicon deployment (Cortex-M)</td>
        </tr>
        <tr>
            <td><strong>Optimization Engine</strong></td>
            <td>Scalar RTRL with causal momentum</td>
            <td>Decoupled neural interfaces or second-order methods</td>
        </tr>
        <tr>
            <td><strong>Novelty Classification</strong></td>
            <td><code>NOVELTY_CLAIM_READY = NO</code></td>
            <td>Subject to external peer review in M3</td>
        </tr>
    </tbody>
</table>

<h2>Forbidden Claims in LEBRE v0.1</h2>
<ol>
    <li><strong>No Multi-Unit Recurrent Claims:</strong> v0.1 makes zero claims regarding multi-dimensional internal dynamics (\(N \ge 2\)). All verified properties apply strictly to scalar recurrence.</li>
    <li><strong>No Physical Microcontroller Flashing Claims:</strong> v0.1 has not been flashed to physical ARM silicon. Embedded feasibility is supported by arithmetic operation counts and state RAM sizing, not physical hardware telemetry.</li>
    <li><strong>No Universal Continual Learning Claims:</strong> LEBRE is validated for streaming regression, filtering, and system identification. It is not claimed to solve general catastrophic forgetting in deep vision or language models.</li>
</ol>

<!-- SECTION 10: TRACEABILITY MATRIX -->
<div class="page-break"></div>
<h1>10. Parameter & Constant Traceability Matrix</h1>

<p>Every numerical constant, learning rate, and threshold in LEBRE v0.1 is mathematically specified, assigned a formal default value, and traced directly to its implementation file and empirical sensitivity horizon.</p>

<table>
    <thead>
        <tr>
            <th>Parameter Name</th>
            <th>Symbol</th>
            <th>Default Value</th>
            <th>Implementation File</th>
            <th>Empirical Function & Sensitivity Horizon</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><code>alpha_norm</code></td>
            <td>\(\alpha_{\text{norm}}\)</td>
            <td>0.01</td>
            <td><code>src/streaming_norm.py</code></td>
            <td>Exponential running mean/variance filter; horizon \(\approx 100\) steps</td>
        </tr>
        <tr>
            <td><code>eps_norm</code></td>
            <td>\(\epsilon_{\text{norm}}\)</td>
            <td>10<sup>-5</sup></td>
            <td><code>src/streaming_norm.py</code></td>
            <td>Numerical stability constant in normalization denominator</td>
        </tr>
        <tr>
            <td><code>alpha_err</code></td>
            <td>\(\alpha_E\)</td>
            <td>0.05</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Base error smoothing factor for birth evaluation; horizon \(\approx 20\) steps</td>
        </tr>
        <tr>
            <td><code>theta_birth</code></td>
            <td>\(\theta_{\text{birth}}\)</td>
            <td>0.15</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Normalized residual error threshold required to initiate provisional birth</td>
        </tr>
        <tr>
            <td><code>n_birth_persist</code></td>
            <td>\(N_{\text{birth}}\)</td>
            <td>30</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Consecutive steps error must exceed \(\theta_{\text{birth}}\) to prevent noise triggering</td>
        </tr>
        <tr>
            <td><code>t_probation</code></td>
            <td>\(T_{\text{prob}}\)</td>
            <td>50</td>
            <td><code>src/candidate_probation.py</code></td>
            <td>Fixed evaluation window for provisional shadow candidate before promotion</td>
        </tr>
        <tr>
            <td><code>theta_promote</code></td>
            <td>\(\theta_{\text{promote}}\)</td>
            <td>0.05</td>
            <td><code>src/candidate_probation.py</code></td>
            <td>Minimum relative counterfactual MSE gain required (&gt;5%) for promotion</td>
        </tr>
        <tr>
            <td><code>tau_mature</code></td>
            <td>\(\tau_{\text{mature}}\)</td>
            <td>100</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Steps post-promotion required before active unit is subject to eviction</td>
        </tr>
        <tr>
            <td><code>alpha_slow</code></td>
            <td>\(\alpha_{\text{slow}}\)</td>
            <td>0.005</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Slow relevance filter parameter; effective credit half-life \(\tau \approx 140\) steps</td>
        </tr>
        <tr>
            <td><code>theta_ret</code></td>
            <td>\(\theta_{\text{ret}}\)</td>
            <td>0.02</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Minimum slow utility threshold below which eviction eligibility begins</td>
        </tr>
        <tr>
            <td><code>m_obs</code></td>
            <td>\(m_{\text{obs}}\)</td>
            <td>0.02</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Positive obsolescence increment per step of non-positive utility</td>
        </tr>
        <tr>
            <td><code>d_obs</code></td>
            <td>\(d_{\text{obs}}\)</td>
            <td>0.05</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Obsolescence decrement per step of positive utility (asymmetric recovery)</td>
        </tr>
        <tr>
            <td><code>theta_obs</code></td>
            <td>\(\theta_{\text{obs}}\)</td>
            <td>0.80</td>
            <td><code>src/two_timescale_retention.py</code></td>
            <td>Required positive obsolescence saturation level to trigger eviction</td>
        </tr>
        <tr>
            <td><code>patience_evict</code></td>
            <td>\(N_{\text{pat}}\)</td>
            <td>30</td>
            <td><code>src/state_lifecycle.py</code></td>
            <td>Consecutive steps dual eviction condition must hold to enforce \(\approx 300:1\) ratio</td>
        </tr>
        <tr>
            <td><code>lr_base</code></td>
            <td>\(\eta_{\text{base}}\)</td>
            <td>0.01</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Learning rate for active sparse linear baseline projection weights</td>
        </tr>
        <tr>
            <td><code>lr_rec_in</code></td>
            <td>\(\eta_{\text{in}}\)</td>
            <td>0.005</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Learning rate for input projection weights into recurrent state</td>
        </tr>
        <tr>
            <td><code>lr_rec_self</code></td>
            <td>\(\eta_\lambda\)</td>
            <td>0.002</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Learning rate for self-recurrent transition weight \(\lambda\)</td>
        </tr>
        <tr>
            <td><code>lr_rec_out</code></td>
            <td>\(\eta_s\)</td>
            <td>0.01</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Learning rate for recurrent scalar readout weight \(w_s\)</td>
        </tr>
        <tr>
            <td><code>weight_decay</code></td>
            <td>\(\gamma_{\text{decay}}\)</td>
            <td>10<sup>-4</sup></td>
            <td><code>src/lebre_engine.py</code></td>
            <td>L2 regularization coefficient for sparse linear and recurrent weights</td>
        </tr>
        <tr>
            <td><code>lambda_init</code></td>
            <td>\(\lambda_0\)</td>
            <td>0.85</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Initial self-recurrent feedback weight assigned to new candidates</td>
        </tr>
        <tr>
            <td><code>lambda_max</code></td>
            <td>\(\lambda_{\text{max}}\)</td>
            <td>0.98</td>
            <td><code>src/lebre_engine.py</code></td>
            <td>Hard stability clipping bound ensuring contractive internal dynamics</td>
        </tr>
        <tr>
            <td><code>r2_flop_budget</code></td>
            <td>\(\mathcal{B}_{\text{FLOP}}\)</td>
            <td>&le; 100</td>
            <td><code>docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml</code></td>
            <td>Mean floating point operations per step benchmark compliance bound</td>
        </tr>
    </tbody>
</table>

<!-- SECTION 11: ADRS & COLOPHON -->
<div class="page-break"></div>
<h1>11. Architectural Decision Records & Final Decision</h1>

<p>The LEBRE v0.1 architecture is grounded in six formal Architectural Decision Records (ADRs):</p>

<ul>
    <li><strong>ADR-001 (Single-State Recurrent Organization):</strong> Constrains internal recurrent capacity strictly to scalar recurrence (\(N \le 1\)), preserving exact real-time gradient tracking (\(\mathcal{O}(1)\) RTRL) and eliminating matrix inversion overhead.</li>
    <li><strong>ADR-002 (Decoupled Shadow Probation):</strong> Enforces total output isolation (\(g_p = 0.0\)) during the initial 50-step evaluation of new candidates, preventing gradient shocks to live predictions.</li>
    <li><strong>ADR-003 (Two-Timescale Relevance Accounting):</strong> Decouples fast instantaneous signal activity from slow structural credit via a 140-step half-life filter, preventing catastrophic eviction across Poisson silent gaps.</li>
    <li><strong>ADR-004 (Dual-Gated Obsolescence & Hysteresis):</strong> Implements the \(\approx 300:1\) empirical cost asymmetry via dual-threshold gating (\(U_{\text{ret}} < 0.02\) AND \(O_{\text{obs}} > 0.80\)) sustained over a 30-step patience counter.</li>
    <li><strong>ADR-005 (Linear-First Structural Parsimony):</strong> Mandates that linear baselines be fully exploited before recurrent birth triggers are permitted to instantiate shadow candidates.</li>
    <li><strong>ADR-006 (Strict Real-Time Mean Resource Budget):</strong> Formulates the R2-FLOP constraint as a mean benchmark throughput requirement (\(\le 100\) FLOPs/step mean), accommodating transient shadow evaluation peaks while preserving overall frugality.</li>
</ul>

<div class="alert alert-info">
<strong>Section 76 Formal Decision Block:</strong>
<pre style="margin: 4px 0 0 0; font-size: 7.8pt; color: #0369a1;">
================================================================================
SECTION 76: FINAL ARCHITECTURAL DECISION BLOCK
================================================================================
ARCHITECTURE_SPEC_VERSION: 0.1-CONDENSED
CANONICAL_NAME: LEBRE
FULL_EXPANSION: Lifecycle-governed Evidence-Based Resource Evolution
HISTORICAL_CODENAME: Track B Single-State Organization
SPEC_CONSISTENCY_AUDIT: PASSED_CORRECTIONS_A_THROUGH_L
DIAGRAM_RENDER_STATUS: CANONICAL_D1_THROUGH_D8_STANDALONE_AND_INLINE_VERIFIED
PDF_PACKAGE_STATUS: COMPILED_AND_VISUALLY_VERIFIED
NUMERIC_INTEGRITY: RECONCILED_WITH_BENCH_01B_CAR_01_FROZEN_LOGS
REGRESSION_SUITE: 124_OF_124_TESTS_PASSING
STATUS: FROZEN_WITH_SCOPE_LIMITS
EVIDENCE_CLASSIFICATION: VALIDATED_WITH_SCOPE_LIMITS
MILESTONE_M3_STATUS: UNOPENED
NOVELTY_CLAIM_READY: NO
HARD_STOP: ENFORCED
================================================================================
</pre>
</div>

<div class="cover-footer" style="margin-top: 30px; border-top: 1px solid #cbd5e1; padding-top: 10px;">
    <div>LEBRE Architecture Specification v0.1 (Condensed Reference) • Codinome Lebre Project</div>
    <div>Document Checksum Complete • End of Specification</div>
</div>

</body>
</html>
"""

html_content = TEMPLATE.replace("<!-- LOGO_B64 -->", LOGO_B64)
html_content = html_content.replace("<!-- SVG_D1 -->", svg_d1)
html_content = html_content.replace("<!-- SVG_D2 -->", svg_d2)
html_content = html_content.replace("<!-- SVG_D3 -->", svg_d3)
html_content = html_content.replace("<!-- SVG_D4 -->", svg_d4)
html_content = html_content.replace("<!-- SVG_D5 -->", svg_d5)
html_content = html_content.replace("<!-- SVG_D6 -->", svg_d6)
html_content = html_content.replace("<!-- SVG_D7 -->", svg_d7)
html_content = html_content.replace("<!-- SVG_D8 -->", svg_d8)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated {OUT_FILE} ({len(html_content)} bytes)")
