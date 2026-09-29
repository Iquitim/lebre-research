# Visual QA Report: Condensed Architectural Specifications (EN & PT-BR)

**Stage:** ARCH-SPEC-01R2  
**Date:** September 19, 2026  
**Auditor:** Scientific Documentation Auditor & Publication-Layout Reviewer  
**Scope:** `LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf` & `LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf`  
**Render Resolution:** 2.0 Scale ($\approx 150 - 200$ DPI) via `pypdfium2`  
**Total Pages Inspected:** 42 pages (21 pages EN + 21 pages PT-BR)  
**Overall Visual QA Status:** PASS (All Checks Satisfied)  

---

## 1. Executive QA Scorecard

| Check Identifier | Requirement | Evaluation Result | Status |
| :--- | :--- | :--- | :---: |
| `COVER_LOGO_VISIBILITY` | Official logo clearly visible with high contrast | Pure white background ensures 100% logo contrast | **PASS** |
| `TITLE_CONTRAST` | Main title legible at glance without background clash | Dark slate `#0F172A` on white `#FFFFFF` | **PASS** |
| `STATUS_BOX_CONTRAST` | 4 metadata cards readable, distinct, technical | `#F8FAFC` cards with `#CBD5E1` borders | **PASS** |
| `GRAYSCALE_READABILITY` | Hierarchy preserved when printed in black and white | High luminance contrast between text and cards | **PASS** |
| `D4_SEPARATOR_READABILITY` | Non-interference boundary readable at 100% PDF zoom | Horizontal `BARRIER` pill + segmented divider | **PASS** |
| `D4_TEXT_OVERLAP` | No lines or connectors intersecting node text | Fully resolved; zero lines cross textual elements | **PASS** |
| `D4_THRESHOLD_ACCURACY` | Uses frozen constants ($T_{\text{prob}} = 50$, $\theta_{\text{promote}} = 0.05$) | Verified frozen values typeset accurately | **PASS** |
| `D4_MATH_RENDERING` | Typeset notation ($w_{\text{base}} \in \mathbb{R}^D$, $\hat{y}_t$, $\Delta\mathcal{L}_t$) | Beautiful typographical sub/superscripts | **PASS** |
| `D4_PDF_SCALE_READABILITY` | No abnormal zoom required to inspect D4 elements | Cleanly legible at normal full-page width | **PASS** |
| `FORMULA_RENDERING` | Zero raw LaTeX, broken glyphs, or formula cutoffs | KaTeX client-side prerendering flawless | **PASS** |
| `TABLE_RENDERING` | Tables fit within margins without column clipping | A1–A8 and B1–B5 fit Page 16 cleanly | **PASS** |
| `BILINGUAL_PARITY` | Exact 1:1 page, diagram, and section symmetry | Exactly 21 pages for both EN and PT-BR | **PASS** |

---

## 2. Page-by-Page Inspection Log (21 Pages)

### English & PT-BR Synchronized Inspection

| Page | Document Section / Content | Visual Issues Identified | Severity | Fix Applied | Final Status |
| :---: | :--- | :--- | :---: | :--- | :---: |
| **1** | Front Cover (Logo, Title, Metadata Grid, Footer) | Prior dark gradient obscured logo; contained "Confidential" label | HIGH | Redesigned with pure white background, top blue rule, neutral research footer | **PASS** |
| **2** | Section 1: Executive Summary & Table of Contents | Inconsistent lifecycle count in TOC; missing Block B workload IDs | MED | Updated TOC to "Five-State Structural Lifecycle" and "Benchmarks A1–A8 & B1–B5" | **PASS** |
| **3** | Section 2: Architectural Identity & Core Principles | Unhedged language regarding linear baseline guarantees | LOW | Bounded claims to evaluated empirical regimes | **PASS** |
| **4** | Section 3: Mathematical Formulation (3.1–3.4) | Parameter updates split awkwardly across page breaks | LOW | Grouped normalization, dual inference, prequential loss, and RTRL dynamics | **PASS** |
| **5** | Section 3: Mathematical Formulation (Cont.) | None; equations aligned cleanly | NONE | Preserved KaTeX block math delimiters | **PASS** |
| **6** | Section 4: Five-State Structural Lifecycle | Heading said "Structural Lifecycle" without state count; mixed thresholds | MED | Standardized title to "Five-State Structural Lifecycle", frozen constants ($T_{\text{prob}}=50$) | **PASS** |
| **7** | Section 5: Two-Timescale Retention & Quiescence | None; math boxes properly enclosed | NONE | Preserved dual-gated hysteresis equations ($\theta_{\text{ret}}=0.02, \theta_{\text{obs}}=0.80$) | **PASS** |
| **8** | Diagram D1: High-Level System Architecture | None; vector rendering sharp | NONE | Verified SVG scaling and container padding | **PASS** |
| **9** | Diagram D2: Five-State Structural Lifecycle | Historical range (20–80) in Provisional state | MED | Updated to five states (DORMANT, PROVISIONAL, ACTIVE, MATURE, EVICTED), $T_{\text{prob}}=50$ | **PASS** |
| **10** | Diagram D3: Data Flow vs. Control Flow | None; dual-column layout sharp | NONE | Preserved microsecond vs. control pipeline distinction | **PASS** |
| **11** | Diagram D4: Non-Interfering Shadow Probation | Dashed line intersected "Strict Isolation"; rotated text; plain-text math | HIGH | Complete redesign: horizontal BARRIER, dual line segments, typeset math, $T_{\text{prob}}=50$ | **PASS** |
| **12** | Diagram D5: Two-Timescale Relevance Retention | None; Poisson silent gap visual clear | NONE | Preserved comparison between naive decay and two-timescale tracking | **PASS** |
| **13** | Diagram D6: Dynamic Resource Elasticity | None; step transitions clear | NONE | Preserved topological adaptation ($38 \to 65 \to 92 \to 40$ FLOPs) | **PASS** |
| **14** | Diagram D7: Empirical Evidence Scope Boundary | None; frozen vs. M3 boundary clear | NONE | Confirmed scalar recurrence $N \le 1$ demarcation | **PASS** |
| **15** | Diagram D8: Online Prequential Operational Cycle | Step 6 mentioned historical gain threshold | LOW | Updated Step 6 to $T_{\text{prob}} = 50$, Relative Gain $> 5\%$ ($\theta_{\text{promote}} = 0.05$) | **PASS** |
| **16** | Section 7: Empirical Benchmark Validation Suite | Prior draft had incorrect system-ID names and inverted Silverbox to B5 | HIGH | Rebuilt Block A and Block B directly from sealed CSV; updated Note C | **PASS** |
| **17** | Section 8: Computational Accounting & Limits | Memory description lacked RAM exclusion caveats | MED | Added formal state RAM distinction (excludes stack, runtime, buffers) | **PASS** |
| **18** | Section 9: Architectural Scope Limits & Frozen Boundary | None; prohibited claims prominently framed | NONE | Confirmed negative scope boundaries (no M0+ flashing claim, no M3) | **PASS** |
| **19** | Section 10: Parameter Traceability Matrix (Part 1) | Historical ranges mixed with frozen constants | MED | Updated normative constants to frozen v0.1 values | **PASS** |
| **20** | Section 10: Parameter Traceability Matrix (Part 2) | Table overflow onto footer | LOW | Adjusted cell padding and font size for clean page fit | **PASS** |
| **21** | Section 11: Architectural Decision Records & Final | ADR-002 had old probation range; ADR-004 unhedged churn | MED | Reconciled ADRs to 50 steps, $> 5\%$ gain, bounded churn claims | **PASS** |

---

## 3. Detailed Review of Critical Components

### 3.1 PDF Cover QA
- **EN Cover Image:** `scratch/pdf_qa/en_page_1.png`
- **PT-BR Cover Image:** `scratch/pdf_qa/ptbr_page_1.png`
- **Inspection Findings:**
  - The official LEBRE logo is displayed at native aspect ratio inside a dedicated pure white panel (`#FFFFFF`).
  - Dark-slate title (`#0F172A`) provides contrast ratio $> 14:1$ against white background.
  - Subtitle and expansion box use subtle technical accents (`#0284C7` border, `#F0F9FF` background).
  - Four metadata cards cleanly separate Architecture Status, Evidence Classification, Novelty Readiness, and Milestone M3 Boundary.
  - Footer attribution replaced "Confidential Scientific Preprint" with "Codinome Lebre Research Project • Architecture Specification v0.1".

### 3.2 Diagram D4 QA
- **EN Page 11 Image:** `scratch/pdf_qa/en_page_11.png`
- **PT-BR Page 11 Image:** `scratch/pdf_qa/ptbr_page_11.png`
- **Inspection Findings:**
  - Vertical rotated text is 100% eliminated.
  - Non-interference barrier is visually represented by a dark slate pill (`BARRIER` / `BARREIRA`) above a neutral gray dashed divider.
  - Middle gate status card displays `g_p = 0.0` (`HARD GATE` / `PORTÃO`) with zero line overlap.
  - Bottom isolation card encloses `Strict Isolation` (`Isolamento Estrito`) and `g_p · s_p = 0` with zero line intersections.
  - Mathematical notation uses clean typographical subscripts and superscripts: $w_{\text{base}} \in \mathbb{R}^D$, $\hat{y}_t$, $s_{p,t}$, $y_{\text{prov},t}$, $\Delta\mathcal{L}_t$.
  - Decision gate uses exact frozen constants: $T_{\text{prob}} = 50$ steps, $\theta_{\text{promote}} = 0.05$ ($> 5\%$).

### 3.3 Empirical Benchmark Tables (Page 16) QA
- **EN Page 16 Image:** `scratch/pdf_qa/en_page_16.png`
- **PT-BR Page 16 Image:** `scratch/pdf_qa/ptbr_page_16.png`
- **Inspection Findings:**
  - Both tables (A1–A8 and B1–B5) comfortably fit on Page 16 without encroaching on page margins.
  - Task B4 is accurately identified as `Silverbox System ID` (Online ESN won with $0.9136$; LEBRE $0.9932$ at $8.0$ FLOPs).
  - Task B5 is accurately identified as `Household Active Power` (LEBRE won with $0.0040$ at $28.3$ FLOPs; outperforming CCN $0.0120$ and GRU $0.0924$).
  - Note C explains the exact inductive bias boundary of scalar recurrence on multi-frequency nonlinear dynamics.

---

## 4. Visual QA Verdict

Both `LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf` and `LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf` pass all visual, layout, typographical, and mathematical criteria. The specification is approved for publication distribution and formal freeze.
