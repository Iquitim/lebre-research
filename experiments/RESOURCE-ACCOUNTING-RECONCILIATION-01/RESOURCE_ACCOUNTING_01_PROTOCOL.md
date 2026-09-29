# RESOURCE-ACCOUNTING-RECONCILIATION-01: Experimental Protocol & Pre-Registration

**Stage:** `RESOURCE-ACCOUNTING-RECONCILIATION-01`  
**Parent Framework:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Lineage State:** Post-`AUDIT-SEAL-01` and `BOUNDED-HISTORY-LAG-INTEGRATION-01`  
**Lead Auditor:** Senior ML Systems Researcher, Embedded DSP Specialist, Computer Architect  
**Pre-Registration Date:** 2026-09-20  

---

## 1. Experimental Objectives

This protocol governs the execution of the unified compute and resource audit. The primary objectives are:
1. **Reconciliation of 82.0 vs. 125.1 FLOPs:** Decompose the 43.1 delta between the historical B7 report (82.0 FLOPs/step) and the H0 FP32 baseline (125.1 FLOPs/step) into exact, mathematically traceable component differences, achieving zero unexplained residual.
2. **Disaggregation of Heterogeneous Operations:** Separate floating-point arithmetic, integer arithmetic, quantization/dequantization, and memory traffic into four non-interchangeable channels.
3. **Quantification of INT8 Overhead:** Quantify the incremental cost of H3 INT8 history relative to the unified H0 FP32 reference across quantization, scale tracking, clipping, rounding, casts, and memory traffic.
4. **Validation of Legacy R2-FLOP Metric:** Formally audit what `R2_FLOP <= 100` originally meant and evaluate H0 and H3 under both legacy and standardized definitions.
5. **Predictive Parity Confirmation:** Guarantee that accounting instrumentation does not alter numerical predictions, support sets, or tracking dynamics.

---

## 2. Experimental Constraints & Invariants

- **Canonical Immutability:** `src/` and `tests/` directories remain 100% bitwise untouched.
- **Milestone Constraint:** `M3_STATUS = UNOPENED`.
- **No Optimization in this Stage:** Identified inefficiencies in H3 or provider abstractions must be documented under `NEXT_STAGE_CANDIDATES`, not altered.
- **No Arbitrary Conversion Weights:** Integer operations are never multiplied by ad-hoc weights to produce "FLOPs".
- **Primary Inferential Unit:** `INDEPENDENT_SEED`. Deterministic operation counters require exact algebraic match; dynamic event distributions report Mean, Median, P95, and Peak.

---

## 3. Representative Task & Seed Selection

To avoid unnecessary bulk execution while capturing diverse dynamic regimes, the standardized audit evaluates $N=10$ audit seeds across 6 representative workloads from the `BOUNDED-HISTORY-01` suite:

| Task ID | Workload Type | Dimensionality $D$ | Horizon $L_{\max}$ | Active Taps | Regime Description |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **BH1** | Static Single Delay | 5 | 32 | Lag $(1, 12)$ | Baseline stationary discovery |
| **BH4** | Support Relocation / Shift | 5 | 32 | $(2, 8) \to (2, 22)$ | Abrupt delay relocation & eviction |
| **BH10** | Quiescence & Channel Silence | 5 | 32 | Lag $(2, 14)$ | Quiescent retention during silence |
| **BH9** | Memoryless Control | 5 | 32 | None | False discovery / noise rejection |
| **BH11** | Continuous State-Space | 5 | 32 | Continuous AR(2) | Distributed polynomial dynamic |
| **BH8** | Complex Multi-Lag Stress | 5 | 32 | 4 non-contiguous | Dynamic range burst & capacity stress |

**Audit Seeds ($N=10$):** Seeds `1201` through `1210` (isolated from past evaluation seeds).

---

## 4. Evaluated History Representations

| Candidate ID | Representation Name | Wordlength | Scale Adaptation Policy |
| :--- | :--- | :---: | :--- |
| **H0** | Exact FP32 Ring | 32-bit float | None (exact float32 point lookup) |
| **H1** | Exact FP16 Ring | 16-bit float | Direct float16 casting |
| **H2** | Fixed INT16 Ring | 16-bit int | Dynamic causal peak tracking |
| **H3** | Quantized INT8 Ring | 8-bit int | Dynamic causal peak tracking |
| **H4** | Age-Aware Mixed Ring | FP16/INT8 | Dual-buffer split at lag 8 |

---

## 5. Formal Pre-Registered Hypotheses

- **H-REC-1 (Reconciliation Residual Zero):** The discrepancy $\Delta = 125.1 - 82.0 = 43.1$ is 100% explainable by:
  1. Provider query accounting in H0 ($q_{\text{flops}} = 2$ added to forward pass, candidate scoring, tap updates, and probing).
  2. Provider write accounting in H0 ($w_{\text{flops}} = D = 5$ added per step).
  3. Additional normalization divisions in candidate scoring and weight updates.
  The unexplained residual satisfies $|\Delta - \sum \delta_i| < 10^{-4}$.
- **H-REC-2 (H3 INT8 Floating-Point Equivalence):** Under standardized accounting, the pure floating-point FLOP count of H3 is **comparable to or lower than** H0, while its incremental overhead resides entirely in `INTEGER_OPS` and `CASTS`.
- **H-REC-3 (Memory Traffic Dominance):** H3 achieves a **$\ge 60\%$ reduction in history memory bus traffic** (bytes moved per step) compared to H0.
- **H-REC-4 (Legacy R2-FLOP Compliance):** Under the original MAC-based linear/adaptive filter convention ($1 \text{ MAC} = 1 \text{ FLOP}$), H0 and H3 both satisfy `R2_FLOP <= 100` if provider indexing operations are properly classified as control rather than arithmetic FLOPs.

---

## 6. Decision Logic Matrix

Following completion of the standardized audit:
- If H3 compute overhead is real and attributable to dynamic scale tracking: recommend `QUANTIZED-HISTORY-EFFICIENCY-01` to optimize scale adaptation without rewriting history.
- If H3 compute overhead is purely mislabeled integer/indexing overhead and hardware-dependent: classify as `HARDWARE_DEPENDENT`, recommend `LEBRE-V0.2-INTEGRATION-DESIGN` with multi-dimensional compute vector.
- Under all conditions: `M3_STATUS` remains `UNOPENED`.
