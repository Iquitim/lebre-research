# LEBRE Architecture: Diagram Rendering & Visual Audit (ARCH-SPEC-01R)
**Stage ID:** ARCH-SPEC-01R  
**Architecture:** LEBRE (*Lifecycle-governed Evidence-Based Resource Evolution*)  
**Scope:** Canonical Diagrams D1–D8, Standalone SVGs, Mermaid Definitions, and Vector Assets  
**Classification:** VALIDATED_WITH_SCOPE_LIMITS  
**Date:** September 2026  

---

## 1. Executive Summary

This document establishes the diagram rendering and visual asset audit for the LEBRE Architecture Specification v0.1 suite under stage `ARCH-SPEC-01R`. 

Prior documentation possessed an incomplete set of 5 diagrams with inconsistent font rendering, overlapping labels, and non-standardized SVG viewBox dimensions. This audit certifies that all **eight canonical diagrams (D1 through D8)** have been implemented as standalone publication-grade SVGs in `docs/architecture/assets/diagrams/`, mapped to corresponding GitHub-compatible Mermaid definitions, and successfully embedded into the publication-grade condensed PDF sources.

---

## 2. Canonical Diagram Inventory & Asset Verification

| ID | Canonical Title | Standalone SVG Asset | ViewBox | File Size | Primary Mechanism Illustrated |
|:---|:---|:---|:---|:---|:---|
| **D1** | High-Level Architecture & Information Flow | `assets/diagrams/lebre_high_level_architecture.svg` | `0 0 920 620` | 7,257 B | Decoupled causal feedforward inference vs. post-target lifecycle control |
| **D2** | Structural Lifecycle State Machine | `assets/diagrams/lebre_lifecycle.svg` | `0 0 860 480` | 5,968 B | 4-state lifecycle (Dormant, Provisional, Active/Mature, Evicted) |
| **D3** | Separation of Data Flow vs. Control Flow | `assets/diagrams/lebre_data_control_flow.svg` | `0 0 840 400` | 5,103 B | Microsecond-critical inference path vs. asynchronous structural governance |
| **D4** | Shadow Mode Probation & Promotion Protocol | `assets/diagrams/lebre_shadow_probation.svg` | `0 0 800 480` | 3,101 B | Isolated candidate learning ($g_p=0$) and counterfactual promotion ($G_{\text{cand}}>0.05$) |
| **D5** | Two-Timescale Relevance & Quiescent Retention | `assets/diagrams/lebre_quiescent_retention.svg` | `0 0 820 440` | 3,782 B | Failure of naive instantaneous eviction vs. LEBRE dual-gated retention |
| **D6** | Dynamic Resource Elasticity Across Regimes | `assets/diagrams/lebre_resource_elasticity.svg` | `0 0 840 380` | 5,159 B | Dynamic scaling ($\approx 38 \to 65 \to 92 \to 40$ FLOPs/step mean) in Task A8 |
| **D7** | v0.1 Empirical Evidence Scope & Boundary | `assets/diagrams/lebre_v01_scope.svg` | `0 0 820 420` | 3,588 B | Frozen v0.1 scalar envelope vs. unopened Milestone M3 multi-state frontier |
| **D8** | Online Prequential Operational Cycle | `assets/diagrams/lebre_prequential_cycle.svg` | `0 0 820 700` | 7,398 B | Strict 8-step causal prequential execution cycle per streaming observation |

---

## 3. Visual & Technical Quality Standards Audit

### 3.1 Standalone SVG Quality & Cross-Platform Rendering
- **ViewBox Standardization:** All 8 SVGs specify explicit, scalable `viewBox` coordinates without fixed physical pixel width/height attributes, enabling fluid responsive downscaling on A4 print layouts.
- **Typography & Font Fallbacks:** Text elements use universal system font stacks (`system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif`), preventing font substitution artifacts or text truncation across Linux, macOS, and Windows rendering engines.
- **Color Palette & Contrast:** Built upon an accessible technical palette:
  - Deep Slate (`#0f172a`, `#1e293b`) for container borders and high-contrast typography.
  - Primary Blue (`#0284c7`, `#2563eb`) for data flow and active structures.
  - Purple / Violet (`#7c3aed`, `#9333ea`) for shadow mode exploration and candidate buffers.
  - Emerald Green (`#059669`, `#16a34a`) for promoted active states.
  - Amber / Red (`#d97706`, `#dc2626`) for eviction gates, hysteresis checks, and forbidden novelty zones.
  - Light neutral backgrounds (`#f8fafc`, `#f1f5f9`) for clean contrast against dark text.

### 3.2 Mermaid Compatibility in Version-Controlled Documentation
- All 8 diagrams possess validated Mermaid definitions published in `docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md`.
- Diagram definitions comply with GitHub Markdown parser rules:
  - Flowcharts specify explicit layout directions (`flowchart TD`, `flowchart LR`).
  - State machine uses standard `stateDiagram-v2` syntax.
  - Sequence diagram uses standard `sequenceDiagram` syntax with `autonumber`.
  - Gantt diagram uses standard `gantt` syntax.
  - Node labels with special characters (parentheses, mathematical notation) are cleanly wrapped in double quotes to prevent syntax parsing errors.

### 3.3 KaTeX Mathematical Interoperability
- In HTML/CSS print pipelines, SVG assets are isolated from external DOM mutations.
- The KaTeX auto-renderer configuration explicitly designates `ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code", "svg"]`, ensuring KaTeX does not alter or corrupt mathematical labels embedded directly within inline SVG markup.

---

## 4. Visual Inspection Summary

Visual QA was conducted on both raw SVG assets and rendered PDF pages exported via `pypdfium2` at 150 DPI:
- **Diagram Placement:** Each diagram D1 through D8 occupies its dedicated visual section in the Condensed Reference document, preceded by an explanatory narrative and accompanied by formal architectural captions.
- **Zero Horizontal Overflow:** All diagrams scale cleanly within the 180mm printable width of standard A4 pages with 14mm margins.
- **Vector Crispness:** Standalone SVGs maintain infinite vector fidelity when zoomed in PDF viewers.

---

## 5. Audit Certification

The diagram rendering audit is **PASSED**. All eight canonical diagrams (D1–D8) are certified technically robust, visually coherent, and publication-ready.
