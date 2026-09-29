# Diagram Repair & Audit Report: Canonical Diagrams D1–D8

**Stage:** ARCH-SPEC-01R2  
**Date:** September 19, 2026  
**Auditor:** Technical Illustrator & Publication-Layout Reviewer  
**Asset Directory:** `docs/architecture/assets/diagrams/`  
**Generator Script:** `scratch/generate_diagrams.py`  

---

## 1. Overview of Canonical Vector Graphics Suite

The LEBRE v0.1 architectural specification includes 8 canonical standalone SVG diagrams (D1–D8), accompanied by a dedicated Portuguese vector twin for Diagram D4 (`lebre_shadow_probation_ptbr.svg`). All SVGs are generated programmatically via `scratch/generate_diagrams.py`, ensuring reproducibility, crisp vector scalability at any zoom level, and responsive rendering across web browsers, GitHub markdown previews, and headless PDF engines.

---

## 2. Diagram-by-Diagram Repair & Audit Log

### D1: LEBRE High-Level System Architecture & Execution Flow
- **File Name:** `lebre_high_level_architecture.svg`
- **ViewBox Dimensions:** `width="800" height="480" viewBox="0 0 800 480"`
- **Prior Problem / Defect:** Contrast between observation connectors and inference boxes was muddy; label alignment caused small overlaps in tight text nodes.
- **Changes Applied:** Rebuilt vector structure with distinct semantic regions: Observation Layer (neutral gray), Dual Causal Predictor (blue/cyan), Prequential Scoring (amber/red), and Evidence & Lifecycle Controller (slate/dark). Enhanced connector contrast and drop-shadow definitions.
- **GitHub Markdown Render Status:** PASS (Renders natively in GitHub Markdown via `<img>` and raw `<svg>`)
- **PDF Headless Engine Render Status:** PASS (Sharp vector rasterization on Page 8)

---

### D2: Five-State Structural Lifecycle State Machine
- **File Name:** `lebre_lifecycle.svg`
- **ViewBox Dimensions:** `width="800" height="380" viewBox="0 0 800 380"`
- **Prior Problem / Defect:** Labeled as a four-phase or four-state lifecycle in narrative headers, despite containing five distinct structural states. The Provisional state displayed historical exploratory range ($T_{\text{prob}} = 20 - 80$ steps) rather than the frozen policy.
- **Changes Applied:** Re-titled and standardized to **Five-State Structural Lifecycle State Machine** (DORMANT, PROVISIONAL, ACTIVE, MATURE, EVICTED). Updated Provisional node label strictly to frozen constant $T_{\text{prob}} = 50$ steps, and Active node to $\tau_{\text{mature}} = 100$ steps.
- **GitHub Markdown Render Status:** PASS
- **PDF Headless Engine Render Status:** PASS (Centered, high-contrast on Page 9)

---

### D3: Separation of Data Flow vs. Control Flow
- **File Name:** `lebre_data_control_flow.svg`
- **ViewBox Dimensions:** `width="800" height="380" viewBox="0 0 800 380"`
- **Prior Problem / Defect:** Connector paths between data inference and background control loops lacked visual distinction, obscuring the microsecond real-time critical path.
- **Changes Applied:** Implemented a two-column architectural layout. Left column highlights the microsecond-critical Data Flow (pure feedforward linear + scalar recurrence, zero matrix inversion). Right column encapsulates the post-target Control Flow (evidence accumulation, two-timescale relevance, and hysteresis eviction).
- **GitHub Markdown Render Status:** PASS
- **PDF Headless Engine Render Status:** PASS (Cleanly separated on Page 10)

---

### D4: Non-Interfering Shadow Mode Probation & Promotion Protocol
- **English File:** `lebre_shadow_probation.svg` (9,316 bytes)
- **Portuguese File:** `lebre_shadow_probation_ptbr.svg` (9,273 bytes)
- **ViewBox Dimensions:** `width="800" height="390" viewBox="0 0 800 390"`
- **Prior Problem / Defect (CRITICAL):**
  1. Contained a thin vertical red dashed line with 90°-rotated vertical text ("STRICT NON-INTERFERENCE") that was illegible at normal zoom levels.
  2. The continuous dashed divider intersected the text of "Strict Isolation" / "Isolamento Estrito".
  3. Mathematical formulas were written in raw text (`w_base in R^D`, `y_hat,t = w_base^T x_t`).
  4. Promotion decision gate displayed outdated ranges ($T_{\text{prob}} = 20 - 80$, Relative Gain $> 15\%$) instead of frozen v0.1 constants.
- **Changes Applied:**
  1. Eliminated all rotated vertical text.
  2. Replaced the red dashed line with a clean, neutral dark slate header pill: `BARRIER` (`#1E293B`) / `BARREIRA`.
  3. Segmented the vertical dashed line into two clean paths (`y=22..68` and `y=114..128`), ensuring zero intersection with text.
  4. Placed the output gate status in an isolated central badge: `g_p = 0.0` (`HARD GATE` / `PORTÃO`).
  5. Enclosed the semantic boundary label in an isolated bottom badge: `Strict Isolation` / `g_p · s_p = 0`.
  6. Formatted all mathematical expressions with clean SVG sub/superscripts ($w_{\text{base}} \in \mathbb{R}^D$, $\hat{y}_t = w_{\text{base}}^\top x_t + w_s s_t$, $s_{p,t}$, $y_{\text{prov},t} = y_{\text{base},t} + w_p s_{p,t}$, $\Delta\mathcal{L}_t = e_{\text{base},t}^2 - (y_t - y_{\text{prov},t})^2$).
  7. Reconciled decision gate constants: $T_{\text{prob}} = 50$ steps, $\theta_{\text{promote}} = 0.05$ ($> 5\%$ relative MSE gain).
  8. Created an exact Portuguese vector twin (`lebre_shadow_probation_ptbr.svg`).
- **GitHub Markdown Render Status:** PASS (Crisp rendering in both English and Portuguese documentation)
- **PDF Headless Engine Render Status:** PASS (Flawless readability at 100% zoom on Page 11 of both PDFs)

---

### D5: Two-Timescale Relevance & Quiescent Memory Preservation
- **File Name:** `lebre_quiescent_retention.svg`
- **ViewBox Dimensions:** `width="800" height="380" viewBox="0 0 800 380"`
- **Prior Problem / Defect:** Contrast of Poisson silent intervals was low; text describing naive energy eviction vs. LEBRE dual-gated retention lacked clear visual hierarchy.
- **Changes Applied:** Rebuilt diagram with split-timeline contrast: Top row illustrates naive energy-based eviction prematurely killing state during Poisson silence ($x_t \approx 0$). Bottom row illustrates LEBRE's two-timescale tracking ($U_{\text{ret}}$ with $\alpha_{\text{slow}} = 0.005$) preserving state memory across hundreds of silent steps until true positive obsolescence ($O_{\text{obs}} > 0.80$) occurs.
- **GitHub Markdown Render Status:** PASS
- **PDF Headless Engine Render Status:** PASS (Rendered on Page 12)

---

### D6: Dynamic Resource Elasticity Across Non-Stationary Regimes
- **File Name:** `lebre_resource_elasticity.svg`
- **ViewBox Dimensions:** `width="800" height="380" viewBox="0 0 800 380"`
- **Prior Problem / Defect:** FLOP transitions did not accurately reflect the empirical values observed in Task A8.
- **Changes Applied:** Reconciled FLOP metrics along the adaptive timeline:
  - Phase 1 (Linear Regime): $\approx 38$ mean FLOPs/step (0 recurrent units)
  - Phase 2 (Delay Regime): $\approx 65$ mean FLOPs/step (lag bank allocated)
  - Phase 3 (Recurrent Regime): $\approx 92$ mean FLOPs/step (scalar state active)
  - Phase 4 (Post-Eviction Linear): $\approx 40$ mean FLOPs/step (reclaimed budget)
- **GitHub Markdown Render Status:** PASS
- **PDF Headless Engine Render Status:** PASS (Rendered on Page 13)

---

### D7: v0.1 Empirical Evidence Scope & Frozen Boundary
- **File Name:** `lebre_v01_scope.svg`
- **ViewBox Dimensions:** `width="800" height="380" viewBox="0 0 800 380"`
- **Prior Problem / Defect:** Visual boundary between v0.1 validated claims and Milestone M3 was insufficiently prominent.
- **Changes Applied:** Implemented a high-contrast boundary graphic. Left panel (Green/Slate) formalizes validated v0.1 scope: single scalar state ($N \le 1$), linear-first parsimony, two-timescale retention, and R2-FLOP $\le 100$ compliance. Right panel (Amber/Dashed) formalizes the strictly unopened Milestone M3 frontier: multi-unit recurrent banks ($N > 1$), adaptive feedback topologies, and hardware flash validation.
- **GitHub Markdown Render Status:** PASS
- **PDF Headless Engine Render Status:** PASS (Rendered on Page 14)

---

### D8: Online Prequential Operational Cycle
- **File Name:** `lebre_prequential_cycle.svg`
- **ViewBox Dimensions:** `width="800" height="420" viewBox="0 0 800 420"`
- **Prior Problem / Defect:** Step 6 contained unhedged gain language and lacked exact constant references.
- **Changes Applied:** Standardized the 8 sequential execution steps:
  1. Ingest $x_t$
  2. Base Forward ($y_{\text{base},t} = w_{\text{base}}^\top x_t$)
  3. Recurrent Forward ($y_{\text{rec},t} = w_s s_t$)
  4. Causal Emit ($\hat{y}_t = y_{\text{base},t} + y_{\text{rec},t}$)
  5. Target Revelation ($y_t$)
  6. Evidence Evaluation ($T_{\text{prob}} = 50$, Gain $> 5\%$)
  7. Parameter Update (Online RTRL + sparse base SGD)
  8. Resource Reclamation (Evict obsolete slots)
- **GitHub Markdown Render Status:** PASS
- **PDF Headless Engine Render Status:** PASS (Rendered on Page 15)

---

## 3. Vector Architecture Quality Certification

All 8 canonical diagrams and the Portuguese D4 twin:
1. Conform to responsive SVG standards with explicit `viewBox` coordinates and relative percentages.
2. Contain zero machine-specific paths, external bitmap dependencies, or proprietary font requirements (system sans-serif fallback stack).
3. Scale cleanly between high-resolution desktop monitors, mobile GitHub readers, and printed PDF pages.
4. Pass all automated and manual visual review inspections.
