import re

# Update scratch/build_en_html.py
with open("scratch/build_en_html.py", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Remove Confidential Scientific Preprint from @page
text = text.replace(
    'content: "Codinome Lebre Research Suite • Confidential Scientific Preprint";',
    'content: "Codinome Lebre Research Project • Architecture Specification v0.1";'
)

# 2. Cover styles
old_cover_css = """
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
"""

new_cover_css = """
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
"""

if old_cover_css.strip() in text:
    text = text.replace(old_cover_css.strip(), new_cover_css.strip())
    print("EN Cover CSS replaced successfully.")
else:
    print("Warning: old_cover_css not found exactly in EN.")

# 3. Cover HTML body
old_cover_html = """<!-- FRONT COVER -->
<div class="cover-page">
    <div class="cover-header">
        <img class="cover-logo" src="data:image/png;base64,<!-- LOGO_B64 -->" alt="LEBRE Architecture Logo">
        <div class="cover-badge">Formal Specification v0.1</div>
    </div>
    
    <div class="cover-main">
        <div class="cover-title">LEBRE Architecture Specification</div>
        <div class="cover-subtitle">Condensed Reference Guide & System Architecture Overview</div>
        
        <div class="cover-expansion">
            <strong>Expansion:</strong> Lifecycle-governed Evidence-Based Resource Evolution<br>
            <strong>Historical Codename:</strong> Track B Single-State Organization
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
        <div>Authoring Suite: Codinome Lebre Scientific Project</div>
        <div>Date of Freeze: September 2026 • Document Version 0.1-CONDENSED</div>
    </div>
</div>"""

new_cover_html = """<!-- FRONT COVER -->
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
</div>"""

if old_cover_html in text:
    text = text.replace(old_cover_html, new_cover_html)
    print("EN Cover HTML body replaced successfully.")
else:
    print("Warning: old_cover_html not found exactly in EN.")

# 4. TOC Item 4
text = text.replace(
    '<li class="toc-item"><span class="toc-title">4. Four-Phase Structural Lifecycle State Machine</span><span class="toc-page">Page 6</span></li>',
    '<li class="toc-item"><span class="toc-title">4. Five-State Structural Lifecycle State Machine</span><span class="toc-page">Page 6</span></li>'
)

# 5. Section 2 claim bounding
text = text.replace(
    'LEBRE guarantees that trivial linear dependencies never trigger expensive state allocations.',
    'Under the evaluated linear regimes, recurrent state allocation was not triggered when the linear baseline was sufficient.'
)
text = text.replace(
    'Memory footprint is strictly bounded to \\(\\approx 440\\) bytes of persistent model state RAM (weights and state registers), while operational throughput is constrained to \\(\\le 100\\) FLOPs/step mean.',
    'Observed mean persistent model-state footprint is 440.0 bytes of RAM (excluding stack, code, runtime, and I/O buffers; benchmark limit \\(R_2\\text{-MEM} \\le 1024\\) bytes), while operational throughput is constrained to \\(\\le 100\\) FLOPs/step mean.'
)

# 6. Section 4 Heading and description
text = text.replace(
    '<h1>4. Four-Phase Structural Lifecycle State Machine</h1>\n\n<p>Every structural object in LEBRE progresses through a rigorously bounded four-state lifecycle: <strong>DORMANT</strong>, <strong>PROVISIONAL</strong>, <strong>ACTIVE / MATURE</strong>, and <strong>EVICTED</strong>.',
    '<h1>4. Five-State Structural Lifecycle State Machine</h1>\n\n<p>Every structural object in LEBRE progresses through a rigorously bounded five-state lifecycle: <strong>DORMANT</strong>, <strong>PROVISIONAL</strong>, <strong>ACTIVE</strong>, <strong>MATURE</strong>, and <strong>EVICTED</strong>.'
)

# 7. Figure D2 caption
text = text.replace(
    '<div class="diagram-caption">Figure D2: Four-state structural lifecycle governing all candidate and active allocations.</div>',
    '<div class="diagram-caption">Figure D2: Five-state structural lifecycle governing all candidate and active allocations.</div>'
)

# 8. Figure D4 caption
text = text.replace(
    '<div class="diagram-caption">Figure D4: Non-interfering shadow probation protocol. Provisional candidates learn in parallel without output coupling.</div>',
    '<div class="diagram-caption">Figure D4: Non-interfering shadow probation protocol with strict isolation barrier and empirical gate.</div>'
)

# 9. Comparison table row
text = text.replace(
    '<td>Discrete four-state machine (Dormant-Prov-Act-Evict)</td>',
    '<td>Discrete five-state machine (Dormant-Prov-Act-Mature-Evict)</td>'
)

# 10. Reconciled Tables 7.1 and 7.2 in Section 7
old_sec7_tables = """<h2>7.1 Synthetic Benchmark Suite (Tasks A1–A8)</h2>
<table>
    <thead>
        <tr>
            <th>Task ID</th>
            <th>Task Description</th>
            <th>Linear Baseline</th>
            <th>Fixed RTRL (\\(N=1\\))</th>
            <th>LEBRE v0.1</th>
            <th>Mean FLOPs/step</th>
            <th>Regret / Behavior</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>A1</strong></td>
            <td>Pure Static Linear Regression</td>
            <td>0.0042</td>
            <td>0.0049</td>
            <td class="highlight-row">0.0041</td>
            <td>38.2</td>
            <td>0 recurrent births (Parsimony intact)</td>
        </tr>
        <tr>
            <td><strong>A2</strong></td>
            <td>Sparse Feature Selection (K=5/50)</td>
            <td>0.0118</td>
            <td>0.0145</td>
            <td class="highlight-row">0.0112</td>
            <td>41.6</td>
            <td>Active feature set correctly identified</td>
        </tr>
        <tr>
            <td><strong>A3</strong></td>
            <td>Fixed Input Delay (\\(L=5\\))</td>
            <td>0.1420</td>
            <td>0.0480</td>
            <td class="highlight-row">0.0310</td>
            <td>58.4</td>
            <td>Promotes lag/recurrent capacity cleanly</td>
        </tr>
        <tr>
            <td><strong>A4</strong></td>
            <td>Linear Dynamical System (\\(N=1\\))</td>
            <td>0.2840</td>
            <td>0.0210</td>
            <td class="highlight-row">0.0185</td>
            <td>88.1</td>
            <td>Reconstructs pole location accurately</td>
        </tr>
        <tr>
            <td><strong>A5</strong></td>
            <td>Poisson Quiescent Bursts (\\(\\lambda=0.01\\))</td>
            <td>0.4150</td>
            <td>0.3890 (Evicted)</td>
            <td class="highlight-row">0.0420</td>
            <td>46.3</td>
            <td>&gt;99% state retention across silent gaps</td>
        </tr>
        <tr>
            <td><strong>A6</strong></td>
            <td>Abrupt Regime Shift (Dynamical to Static)</td>
            <td>0.3120</td>
            <td>0.0980 (Stale)</td>
            <td class="highlight-row">0.0280</td>
            <td>52.7</td>
            <td>Safe eviction completed within 42 steps</td>
        </tr>
        <tr>
            <td><strong>A7</strong></td>
            <td>Multi-Rate Event-Driven Dynamics</td>
            <td>0.3890</td>
            <td>0.1450</td>
            <td class="highlight-row">0.0380</td>
            <td>61.2</td>
            <td>Bridges variable sampling intervals</td>
        </tr>
        <tr>
            <td><strong>A8</strong></td>
            <td>Cyclic Elastic Regimes (Linear-Lag-Rec)</td>
            <td>0.3450</td>
            <td>0.1120</td>
            <td class="highlight-row">0.0340</td>
            <td>64.5</td>
            <td>Full elastic expansion and contraction</td>
        </tr>
    </tbody>
</table>

<h2>7.2 Real-World Benchmark Suite (Tasks B1–B5)</h2>
<table>
    <thead>
        <tr>
            <th>Task ID</th>
            <th>Physical System</th>
            <th>Minimal GRU</th>
            <th>Echo State (ESN)</th>
            <th>CCN</th>
            <th>LEBRE v0.1</th>
            <th>Mean FLOPs/step</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>B1</strong></td>
            <td>Cascaded Tanks System ID</td>
            <td>0.0412</td>
            <td>0.0489</td>
            <td>0.0185</td>
            <td class="highlight-row">0.0142</td>
            <td>89.4</td>
        </tr>
        <tr>
            <td><strong>B2</strong></td>
            <td>Coupled Electric Drives</td>
            <td>0.0380</td>
            <td>0.0410</td>
            <td>0.0210</td>
            <td class="highlight-row">0.0168</td>
            <td>91.2</td>
        </tr>
        <tr>
            <td><strong>B3</strong></td>
            <td>pH Neutralization Process</td>
            <td>0.0520</td>
            <td>0.0610</td>
            <td>0.0280</td>
            <td class="highlight-row">0.0215</td>
            <td>94.6</td>
        </tr>
        <tr>
            <td><strong>B4</strong></td>
            <td>Wiener-Hammerstein Benchmark</td>
            <td>0.0640</td>
            <td>0.0720</td>
            <td>0.0340</td>
            <td class="highlight-row">0.0260</td>
            <td>93.8</td>
        </tr>
        <tr>
            <td><strong>B5</strong></td>
            <td>Silverbox Nonlinear Resonance</td>
            <td>0.0924</td>
            <td>0.1129</td>
            <td>0.0120</td>
            <td class="highlight-row">0.0094</td>
            <td>90.44</td>
        </tr>
    </tbody>
</table>

<div class="alert alert-info">
<strong>Audit Confirmation (Correction C):</strong> In Benchmark B5 (Silverbox), numerical values are rigorously verified against frozen experimental logs: <strong>Minimal GRU = 0.09240</strong>, <strong>ESN = 0.11290</strong>, <strong>CCN = 0.01200</strong>, and <strong>LEBRE = 0.00940</strong>. LEBRE achieved superior predictive accuracy while consuming an average of 90.44 FLOPs/step, fully compliant with the R2-FLOP budget (\(\\le 100\\) FLOPs/step mean).
</div>"""

new_sec7_tables = """<h2>7.1 Synthetic Mechanistic Benchmark Suite (Tasks A1–A8)</h2>
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
</div>"""

if old_sec7_tables in text:
    text = text.replace(old_sec7_tables, new_sec7_tables)
    print("EN Section 7 tables replaced successfully.")
else:
    print("Warning: old_sec7_tables not found exactly in EN.")

with open("scratch/build_en_html.py", "w", encoding="utf-8") as f:
    f.write(text)

print("Updated scratch/build_en_html.py written successfully.")
