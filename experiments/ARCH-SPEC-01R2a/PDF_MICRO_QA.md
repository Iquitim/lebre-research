# PDF Micro QA Report — Architectural Consistency & Visual Layout Verification

**Stage:** ARCH-SPEC-01R2a  
**Evaluation Date:** 2026-09-19  
**Auditor:** Scientific Documentation Auditor and Technical Editor  
**Target Documents:**
1. [`LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf`](<lebre-research>/docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf)
2. [`LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf`](<lebre-research>/docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf)

---

## 1. Executive Summary & Compilation Status

Both Condensed Reference PDFs were regenerated directly from their updated HTML source templates (`LEBRE_CONDENSED_EN.html` and `LEBRE_CONDENSED_PTBR.html`) via Microsoft Edge headless print-to-pdf pipeline. All 21 pages of each document were extracted, verified for non-empty text layers, and rendered to PNG at 150 DPI for visual inspection.

| Metric | English Reference (`EN`) | Brazilian Portuguese Reference (`PTBR`) | Parity Status |
| :--- | :---: | :---: | :---: |
| **Source HTML** | `LEBRE_CONDENSED_EN.html` (756,933 bytes) | `LEBRE_CONDENSED_PTBR.html` (758,377 bytes) | Reconciled |
| **Output PDF** | `LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf` | `LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf` | Recompiled |
| **PDF File Size** | 1,504,935 bytes | 1,515,323 bytes | Balanced |
| **Total Pages** | **21 Pages** | **21 Pages** | **EXACT MATCH** |
| **Page Resolution** | 1190 × 1684 px (A4 @ 150 DPI) | 1190 × 1684 px (A4 @ 150 DPI) | **EXACT MATCH** |
| **Empty Pages Detected** | **0** | **0** | **PASS** |

---

## 2. Inspection of Affected Pages

### 2.1. Page 1: Document Cover
- **Header Badge:** `STATUS: FROZEN_WITH_SCOPE_LIMITS` (Dark Navy `#0f172a`, Badge Red `#991b1b` / Border `#f87171`).
- **Logo Presentation:** Crisp rendering of `logo/LEBRE Logo.png` at 380px width, centered.
- **Title Block:** `LEBRE Architecture Specification v0.1` / `Especificação da Arquitetura LEBRE v0.1`.
- **Subtitles & Metadata:** Correct canonical expansion (*Lifecycle-governed Evidence-Based Resource Evolution*).
- **Status Box:** Fully contained within page bounds; no overflow into footer; clean margins.
- **Verdict:** **PASS**.

### 2.2. Page 3: Architectural Identity & Core Principles (Section 2)
- **Principle 1 (Linear-First):**
  - EN: *"Under the evaluated linear regimes, recurrent state allocation was not triggered when the linear baseline was sufficient."*
  - PT-BR: *"Nos regimes lineares avaliados, a alocação de estado recorrente não foi acionada quando a linha de base linear se mostrou suficiente."*
  - Verified: No universal "garante", "jamais", "always", or "guarantee".
- **Principle 2 (Shadow Probation):**
  - EN: Decoupled shadow units; probation horizon $T_{\text{prob}} = 50$, promotion threshold $\theta_{\text{promote}} = 0.05$.
  - PT-BR: Candidatos desacoplados da inferência ativa; horizonte $T_{\text{prob}} = 50$, limiar $\theta_{\text{promote}} = 0,05$.
  - Verified: Replaced "jamais" with natural decoupling statement.
- **Principle 3 (Two-Timescale Retention):**
  - Replaced unhedged "garantindo" with empirical retention across evaluated Poisson benchmarks.
- **Principle 4 (Bounded Resource Elasticity):**
  - EN & PT-BR: Explicitly state observed mean persistent state of 440.0 bytes under R2-MEM $\le 1024$ bytes ceiling, explicitly clarifying that this does not represent total device RAM in a physical microcontroller.
- **Layout & Wrapping:** Principles table and text fit cleanly without pushing into subsequent pages.
- **Verdict:** **PASS**.

### 2.3. Page 6: Structural Lifecycle State Machine (Section 4)
- **Heading:**
  - EN: `4. Five-State Structural Lifecycle State Machine`.
  - PT-BR: `4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados`.
- **Opening Text:**
  - EN: Lists all 5 states: DORMANT, PROVISIONAL, ACTIVE, MATURE, EVICTED.
  - PT-BR: *"Todo objeto estrutural na LEBRE progride por um ciclo de vida rigorosamente delimitado em cinco estados: DORMANT, PROVISIONAL, ACTIVE, MATURE e EVICTED."*
- **State Table:** All 5 states cleanly formatted in tabular form.
- **Probation Subsections:**
  - $T_{\text{prob}} = 50$ steps, $\theta_{\text{promote}} = 0.05$ (5%), $\tau_{\text{mature}} = 100$ steps.
  - Line wrapping: Zero overflow; mathematical equations rendered cleanly via KaTeX.
- **Verdict:** **PASS**.

### 2.4. Page 11: Diagram D4 (Evidence Accumulator Dynamics)
- **D4 Preservation Check:**
  - Horizontal readable barrier preserved: `PROBATION TIME BARRIER (T_prob = 50 steps)` with `Counterfactual Gain Threshold: theta_promote = 0.05`.
  - Zero rotated text overlap.
  - Perfect legibility at 100% zoom.
  - Strict parity between EN and PT-BR versions.
- **Verdict:** **PASS**.

### 2.5. Page 17: Computational Accounting & Hardware Qualification (Section 8)
- **Taxonomy Table:** Stationary nominal pipeline sums to $\approx 99$ FLOPs/step ($D=8, K=5, N=1$).
- **FLOP Semantics Callout:** Explicitly notes that R2-FLOP ($\le 100$ FLOPs/step) is a mean benchmark budget, distinguishing nominal throughput from temporary shadow probation peaks ($\approx 206$ FLOPs/step for 50 steps).
- **RAM Footprint Callout:** 440.0 bytes explicitly designated as observed persistent model state; hardware boundary clearly states that physical MCU deployment is prospective future work and software simulation is the sole evaluated medium.
- **Verdict:** **PASS**.

### 2.6. Page 18: Architectural Scope Limits & Frozen Frontier (Section 9)
- **Comparison Table:**
  - Row "Structural Transitions":
    - EN: `Discrete five-state machine (Dormant-Prov-Act-Mature-Evict)`.
    - PT-BR: `Máquina discreta de cinco estados (Dormant-Prov-Act-Mature-Evict)`.
- **Verdict:** **PASS**.

### 2.7. Page 21: ADRs & Formal Section 76 Decision Block
- **ADR-001 through ADR-006:** All six records presented cleanly.
- **Section 76 Block:** Preformatted monospace code box with crisp blue styling, terminating cleanly at the document footer.
- **Verdict:** **PASS**.

---

## 3. Visual & Technical QA Criteria Checklist

| QA Item | Requirement | Observed Status | Verdict |
| :--- | :--- | :--- | :---: |
| **Page Overflow** | No unintentional blank pages or spillover | Exactly 21 pages on both EN and PTBR | **PASS** |
| **Formula Rendering** | KaTeX client-side prerendering, no broken glyphs | All mathematical expressions display cleanly | **PASS** |
| **Diagram Integrity** | Diagrams D1–D8 crisp, legible, properly positioned | All SVGs scale cleanly within page margins | **PASS** |
| **D4 Barrier Design** | Horizontal barrier, $T_{\text{prob}} = 50$, $\theta = 0.05$ | Fully preserved and verified | **PASS** |
| **Header & Footer** | Running headers with page numbering and status badge | Consistent on pages 2–21 of both PDFs | **PASS** |
| **Grayscale Contrast** | Text readable under black-and-white printing | High contrast dark-on-light theme preserved | **PASS** |

---

## 4. Final QA Conclusion

The derived PDF publications [`LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf`](<lebre-research>/docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf) and [`LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf`](<lebre-research>/docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf) are completely regenerated, visually validated, and aligned with all editorial micro-corrections. They are certified ready for specification freeze.
