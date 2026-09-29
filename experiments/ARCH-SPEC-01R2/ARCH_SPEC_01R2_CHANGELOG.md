# ARCH-SPEC-01R2 Detailed Changelog

**Stage:** ARCH-SPEC-01R2  
**Date:** September 19, 2026  
**Type:** Documentation-Only Reconciliation & Visual Audit Pass  
**Source Code Impact:** Exactly 0 lines modified in `src/` or `tests/`  

---

## 1. Vector Diagram Assets (`docs/architecture/assets/diagrams/`)

### `lebre_shadow_probation.svg` (D4 — English)
- **Eliminated:** 90°-rotated vertical text `"STRICT NON-INTERFERENCE"` and continuous vertical red dashed line.
- **Added:** Top horizontal pill badge `BARRIER` (`#1E293B`) with centered text.
- **Modified:** Segmented dashed divider into two clean vertical lines (`y=22..68` and `y=114..128`), completely avoiding text intersection.
- **Added:** Enclosed central card for output gate status (`g_p = 0.0`, `HARD GATE`).
- **Added:** Enclosed bottom card for isolation semantics (`Strict Isolation`, `g_p · s_p = 0`).
- **Added:** Typeset mathematical notation using `<tspan>` sub/superscripts for $w_{\text{base}} \in \mathbb{R}^D$, $\hat{y}_t$, $s_{p,t}$, $y_{\text{prov},t}$, and $\Delta\mathcal{L}_t$.
- **Reconciled:** Decision gate parameters to frozen constants: $T_{\text{prob}} = 50$ steps, $\theta_{\text{promote}} = 0.05$ ($> 5\%$).

### `lebre_shadow_probation_ptbr.svg` (D4 — Portuguese Twin)
- **Created/Updated:** Exact Portuguese translation of D4 with identical visual structure and zero line-text overlap.
- **Terminology:** `PREDITOR ATIVO`, `CANDIDATO EM SOMBRA`, `BARREIRA`, `PORTÃO`, `Isolamento Estrito`, `PORTÃO DE PROVAÇÃO`, `PROMOVER`, `DESCARTAR`.

### `lebre_lifecycle.svg` (D2)
- **Standardized:** Diagram title to "D2: Five-State Structural Lifecycle State Machine".
- **Reconciled:** Provisional node label updated from historical range (20–80) to $T_{\text{prob}} = 50$ steps; Active node to $\tau_{\text{mature}} = 100$ steps.

### `lebre_prequential_cycle.svg` (D8)
- **Reconciled:** Step 6 text updated to explicitly state evaluation at $T_{\text{prob}} = 50$ steps with relative gain $> 5\%$ ($\theta_{\text{promote}} = 0.05$).

---

## 2. Specification & Markdown Files (`docs/architecture/`)

### `LEBRE_ARCHITECTURE_DIAGRAMS.md`
- **Reconciled:** Section 2 and Section 4 titles and captions standardized to "Five-State Structural Lifecycle".
- **Updated:** D4 diagram description, Mermaid diagram representation, and architectural invariants to reflect the horizontal barrier, dual line segments, and frozen constants ($T_{\text{prob}} = 50$, $\theta_{\text{promote}} = 0.05$).

### `LEBRE_CONSTANT_TRACEABILITY.md`
- **Updated:** Status header upgraded to `Internally Audited Reference Specification`.
- **Replaced:** Historical ranges in the normative table with frozen canonical constants ($T_{\text{prob}} = 50$ steps, $\tau_{\text{mature}} = 100$ steps, $\theta_{\text{promote}} = 0.05$).
- **Added:** Notes explaining that historical development ranges (20–80 steps, 15% gain) are retained strictly as design history.
- **Bounded:** Word "guarantee" replaced with "observed to sustain" in event density row.

### `LEBRE_ARCHITECTURAL_DECISIONS.md`
- **ADR-002:** Reconciled probation duration to $T_{\text{prob}} = 50$ steps and promotion threshold to $> 5\%$ relative MSE gain.
- **ADR-004:** Bounded catastrophic churn prevention claims to tested stationary and switching regimes.

### `LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md` & `PTBR.md`
- **Section 35:** Bounded operational claims (replaced "guaranteed" with "empirically validated within tested stationary horizons").
- **Section 36:** Replaced "Certified Scope" with "Frozen Specification Scope".
- **Sections 11 & 14:** Reconciled $T_{\text{prob}} = 50$ steps and five-state lifecycle terminology.

### `LEBRE_OVERVIEW_EN.md` & `PTBR.md`
- **Section 6:** Expanded empirical benchmark table to include all five Block B tasks (B1–B5) with verified sealed values, eliminating the partial/omitted listing.

### `LEBRE_TRACEABILITY_MATRIX.csv`
- **Reconciled:** Rows for $T_{\text{prob}}$ and $\tau_{\text{mature}}$ updated to 50 steps and 100 steps respectively.

---

## 3. PDF Generator Sources (`docs/architecture/pdf_source/` & `scratch/`)

### `scratch/generate_diagrams.py`
- Implemented direct vector generation of D4 (English and Portuguese) with clean barrier pill, dual line segments, enclosed gate cards, and typographical math.

### `scratch/build_en_html.py` & `LEBRE_CONDENSED_EN.html`
- **Cover Page CSS & HTML:** Redesigned cover layout using a pure white background (`#ffffff`), dark slate typography (`#0f172a`), top blue rule (`border-top: 6px solid #0284c7`), and high-contrast metadata cards.
- **Logo Integration:** Enclosed official logo (`logo/LEBRE Logo.png`) in a clean white panel, ensuring maximum visual contrast without recoloring or distortion.
- **Document Header/Footer:** Removed "Confidential Scientific Preprint", replaced with "Codinome Lebre Research Project • Architecture Specification v0.1".
- **Section 4:** Standardized title to "Five-State Structural Lifecycle State Machine".
- **Section 7:** Rebuilt tables 7.1 (A1–A8) and 7.2 (B1–B5) using sealed values from `BENCH_01B_AGGREGATE_SUMMARY.csv`. Updated Note C to document Task B4 (Silverbox) as an inductive bias boundary and Task B5 (Household Power) as an empirical win.

### `scratch/build_ptbr_html.py` & `LEBRE_CONDENSED_PTBR.html`
- Replicated exact visual styling, white cover layout, top rule, logo integration, and metadata grid from English template.
- Embedded `lebre_shadow_probation_ptbr.svg` as Figure D4.
- Translated Section 7 tables and Note C into natural Portuguese with sealed values.
- Standardized title to "4. Máquina de Estados do Ciclo de Vida Estrutural de Cinco Estados".

---

## 4. Compiled PDF Deliverables (`docs/architecture/pdf/`)

### `LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf` (1,505,737 bytes)
- Compiled cleanly via headless Microsoft Edge engine.
- Total pages: 21 pages.
- KaTeX mathematical equations, SVG vector diagrams, and tables fully rendered and visually verified.

### `LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf` (1,515,104 bytes)
- Compiled cleanly via headless Microsoft Edge engine.
- Total pages: 21 pages.
- 1:1 page, diagram, and section symmetry with the English reference edition.

---

## 5. Verification Tools & Artifacts (`scratch/` & `experiments/ARCH-SPEC-01R2/`)

- `scratch/compile_and_qa_pdfs.py`: Updated to compile PDFs and render all 42 pages to PNG images at 2.0 scale ($\approx 150-200$ DPI) into `scratch/pdf_qa/`.
- `experiments/ARCH-SPEC-01R2/ARCH_SPEC_01R2_AUDIT.md`: Complete audit report.
- `experiments/ARCH-SPEC-01R2/FROZEN_EVIDENCE_RECONCILIATION.md`: Sealed evidence mapping and numerical reconciliation.
- `experiments/ARCH-SPEC-01R2/VISUAL_QA_REPORT.md`: Page-by-page visual QA report.
- `experiments/ARCH-SPEC-01R2/DIAGRAM_REPAIR_REPORT.md`: Detailed D1–D8 repair report.
- `experiments/ARCH-SPEC-01R2/ARCH_SPEC_01R2_CHANGELOG.md`: This file.
