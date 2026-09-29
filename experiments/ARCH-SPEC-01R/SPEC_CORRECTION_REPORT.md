# LEBRE Architecture: Specification Correction Report (ARCH-SPEC-01R)
**Stage ID:** ARCH-SPEC-01R  
**Architecture:** LEBRE (*Lifecycle-governed Evidence-Based Resource Evolution*)  
**Historical Codename:** Track B Single-State Organization  
**Classification:** VALIDATED_WITH_SCOPE_LIMITS  
**Novelty Status:** NOVELTY_CLAIM_READY = NO  
**Milestone M3:** UNOPENED  
**Date:** September 2026  

---

## 1. Executive Summary

This report documents the systematic, surgical correction pass executed across the LEBRE Architecture Specification v0.1 documentation suite under stage `ARCH-SPEC-01R`. All 12 formal corrections (**Corrections A through L**) identified during scientific review have been implemented, verified, and cross-referenced.

Crucially, this audit made **zero modifications to the core architecture**, **zero changes to source code (`src/` remains 100% bitwise immutable)**, **reopened no closed benchmarks (`BENCH-01B` and `CAR-01` remain frozen)**, and **strictly withheld novelty assertions**.

---

## 2. Itemized Audit of Corrections A through L

### Correction A: R2-FLOP Mean Semantics vs. Transient Evaluation Peaks
- **Issue Identified:** Prior documentation inconsistently implied that the R2-FLOP budget ($\le 100$ FLOPs/step) was an absolute per-step ceiling enforced at every individual clock cycle.
- **Audited Truth:** In frozen benchmark runs (Task B5), LEBRE operates at an average throughput of **90.44 FLOPs/step mean**, fully compliant with the benchmark budget. However, during transient probation intervals ($T_{\text{prob}} = 50$ steps) where a shadow candidate is evaluated in parallel with active inference, operational load reaches a temporary peak of $\approx 206$ FLOPs/step.
- **Resolution Applied:** Across all specification documents, R2-FLOP is formally designated as a *mean per-step benchmark throughput budget*. The distinction between nominal steady-state inference ($\approx 99$ FLOPs/step), idle baseline ($\approx 38$ FLOPs/step), and transient peak ($\approx 206$ FLOPs/step) is explicitly detailed.

### Correction B: Microcontroller Hardware Claims Demotion & Memory Scoping
- **Issue Identified:** Prior text stated that LEBRE was "validated on ARM Cortex-M0+/M4" and characterized 440 bytes as "total system footprint".
- **Audited Truth:** LEBRE has been evaluated strictly in software simulation. It has not been flashed to physical ARM Cortex-M silicon. Furthermore, 440 bytes accounts solely for *persistent model state RAM* (weights, recurrent states, RTRL sensitivity registers, shadow buffers, and lifecycle accumulators), excluding microcontroller stack, I/O ring buffers, and RTOS runtime.
- **Resolution Applied:** Hardware claims have been demoted to *prospective candidate targets for future empirical validation*. The memory footprint is strictly qualified as *persistent model state RAM*.

### Correction C: Correction of Benchmark B5 (Silverbox) Baseline Figures
- **Issue Identified:** A typographical error in earlier draft summaries misattributed baseline MSE figures on Task B5 (Silverbox).
- **Audited Truth:** Frozen experimental logs from `BENCH-01B` establish the exact normalized test MSE values:
  - Minimal GRU: **0.09240**
  - Echo State Network (ESN): **0.11290**
  - Continuous Cascade Network (CCN): **0.01200**
  - LEBRE v0.1: **0.00940**
- **Resolution Applied:** Corrected across all tables in `LEBRE_OVERVIEW_EN.md`, `LEBRE_OVERVIEW_PTBR.md`, `LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md`, `LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md`, and the condensed reference guides.

### Correction D: Path Standardization to Relative Markdown Links
- **Issue Identified:** Documents contained machine-specific absolute file URIs (`file:///D:/...` or `d:\Projetos\...`) which break in external publication environments.
- **Audited Truth:** Portable documentation suites must rely strictly on repository-relative Markdown links.
- **Resolution Applied:** All cross-document links converted to relative paths (e.g. `docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md`).

### Correction E: Scientific Tone Moderation & "Fundamental Property" Phrasing
- **Issue Identified:** Isolated occurrences of "fundamental property" appeared in narrative text, overclaiming the theoretical finality of an empirically derived architecture.
- **Audited Truth:** Under scientific wording guidelines established in `CAR-01`, architectural characteristics must be phrased as "central architectural principles" or "empirically validated capabilities".
- **Resolution Applied:** Replaced across English and Portuguese specifications.

### Correction F: Provisional State Weight Notation Standardization
- **Issue Identified:** Notation for provisional candidate weights varied between $w_{\text{cand}}$, $w_{\text{shadow}}$, and $w_p$.
- **Audited Truth:** Mathematical consistency requires a single canonical symbol.
- **Resolution Applied:** Standardized to $w_p$ (with vector input projection $\mathbf{w}_{p,\text{in}}$ and feedback weight $\lambda_p$).

### Correction G: Clarification of the 300:1 Cost Asymmetry
- **Issue Identified:** References to "300:1" implied an explicit hardcoded hyperparameter multiplier in code.
- **Audited Truth:** Inspection of `src/state_lifecycle.py` and `src/two_timescale_retention.py` confirms that 300:1 is an *empirical cost ratio* (false eviction regret vs. dormant state retention overhead). The codebase enforces this conservative asymmetry structurally via a dual-gated threshold ($U_{\text{ret}} < 0.02$ AND $O_{\text{obs}} > 0.80$) held across a 30-step hysteresis patience counter.
- **Resolution Applied:** Explicitly audited and documented across Section 5 and ADR-004.

### Correction H: Semantic and Terminological Parity across EN and PTBR Suites
- **Issue Identified:** Minor divergence in section numbering and translated terminology between English and Portuguese files.
- **Audited Truth:** Technical specifications must maintain 1-to-1 semantic, mathematical, and structural parity.
- **Resolution Applied:** Complete alignment of all 41 sections and subsections across both language editions.

### Correction I: ADR Status & Document Metadata Reconciliation
- **Issue Identified:** ADR-001, ADR-004, and ADR-006 lacked updated cross-references to the corrected B5 values, R2-FLOP mean semantics, and the 300:1 empirical cost ratio clarification.
- **Audited Truth:** Architectural Decision Records must reflect the final audited consensus.
- **Resolution Applied:** Updated `docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md` with full traceability.

### Correction J: Architecture Manifest Synchronization
- **Issue Identified:** `docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml` listed legacy provisional fields.
- **Audited Truth:** Manifest metadata must match specification metrics bit for bit.
- **Resolution Applied:** Reconciled `r2_flop_compliance: MEAN_R2_COMPLIANT`, `peak_flops_observed: 206.0`, and `hardware_validated: false`.

### Correction K: Canonical D1–D8 Architectural Diagram Catalog
- **Issue Identified:** Documentation referenced an incomplete 5-diagram set with rendering and styling inconsistencies.
- **Audited Truth:** Full specification requires 8 canonical diagrams (D1–D8) covering system flow, lifecycle, data vs control separation, shadow probation, quiescent retention, resource elasticity, evidence scope boundary, and prequential operational cycle.
- **Resolution Applied:** Implemented 8 standalone SVG assets in `docs/architecture/assets/diagrams/`, updated `docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md` with matching Mermaid definitions, and embedded SVGs directly into condensed PDF sources.

### Correction L: Comprehensive Hyperparameter & Constant Traceability Matrix
- **Issue Identified:** Thresholds and constants were scattered across multiple documents without an explicit traceability index.
- **Audited Truth:** Scientific reproducibility demands an exhaustive dictionary mapping every parameter to its implementation file, default value, and sensitivity horizon.
- **Resolution Applied:** Created `docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md` and integrated the complete 22-parameter matrix into all specifications.

---

## 3. Files Audited and Reconciled

| File Path | Status | Primary Corrections Implemented |
|:---|:---|:---|
| `docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md` | **Updated & Verified** | Corrections A, B, C, D, E, F, G, H, L |
| `docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md` | **Updated & Verified** | Corrections A, B, C, D, E, F, G, H, L |
| `docs/architecture/LEBRE_OVERVIEW_EN.md` | **Updated & Verified** | Corrections A, B, C, D, E |
| `docs/architecture/LEBRE_OVERVIEW_PTBR.md` | **Updated & Verified** | Corrections A, B, C, D, E |
| `docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md` | **Updated & Verified** | Corrections A, B, G, I |
| `docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml` | **Updated & Verified** | Corrections A, B, J |
| `docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md` | **Created & Verified** | Correction L |
| `docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md` | **Updated & Verified** | Correction K |
| `docs/architecture/assets/diagrams/lebre_*.svg` (8 files) | **Generated & Verified** | Correction K |
| `docs/architecture/pdf_source/LEBRE_CONDENSED_EN.html` | **Created & Verified** | Full PDF source suite |
| `docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html` | **Created & Verified** | Full PDF source suite |
| `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf` | **Compiled & QA Verified** | Condensed Reference PDF |
| `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf` | **Compiled & QA Verified** | Condensed Reference PDF |
| `experiments/ARCH-SPEC-01/README_INTEGRATION_PROPOSAL.md` | **Updated & Verified** | Relative links to spec suite and PDFs |

---

## 4. Conclusion & Sign-Off

All corrections have been executed with zero regression in test suite execution (124/124 tests pass). The specification suite is formally synchronized, scientifically bounded, and ready for publication archive.
