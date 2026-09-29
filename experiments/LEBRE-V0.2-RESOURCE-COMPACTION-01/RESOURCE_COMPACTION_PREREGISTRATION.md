# Preregistration: Resource Compaction of the Correlation Grid

**Document Identifier:** `RESOURCE_COMPACTION_PREREGISTRATION.md`  
**Study Identifier:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Auditor / Researcher:** Independent Skeptical Senior Researcher  
**Date:** September 2026  
**Status:** FROZEN PRIOR TO CONFIRMATORY EXECUTION  

---

## 1. Preregistration Statement & Integrity Commitment

This preregistration establishes the formal hypotheses, decision rules, practical equivalence bounds, and task groupings for `LEBRE-V0.2-RESOURCE-COMPACTION-01` prior to executing any confirmatory runs (`FINAL` cohort: seeds `1411`..`1440`).

In compliance with open science and confirmatory engineering standards (Nosek et al., 2018; Lakens, 2017), the criteria for memory compliance and behavioral equivalence are permanently locked in this document. Post-hoc relaxation of bounds or altering task groupings after observing C1 performance is strictly forbidden.

---

## 2. Formal Hypotheses

### 2.1 Primary Memory Hypothesis ($H_{\text{MEM}}$)
- **Null Hypothesis ($H_{0, \text{MEM}}$):**
  $$\text{TOTAL\_PERSISTENT\_BYTES}(C_1) > 1024 \text{ Bytes}$$
- **Alternative Hypothesis ($H_{1, \text{MEM}}$):**
  $$\text{TOTAL\_PERSISTENT\_BYTES}(C_1) \le 1024 \text{ Bytes}$$
- **Theoretical Target:** $976$ Bytes ($1,306 - 660 \text{ [FP32 grid]} + 330 \text{ [FP16 grid]}$).
- **Decision Rule:** Reject $H_{0, \text{MEM}}$ and declare Gate 11 PASS for the experimental candidate if and only if the physical persistent ledger satisfies `TOTAL_PERSISTENT_BYTES <= 1024` with zero persistent FP32 master copies.

### 2.2 Behavior Preservation Hypothesis ($H_{\text{BEHAV}}$)
- **Null Hypothesis ($H_{0, \text{BEHAV}}$):**
  $$|\mu_{C1} - \mu_{C0}| \ge \Delta_{\text{equiv}}$$
  (The difference in predictive or structural behavior exceeds practical equivalence margins).
- **Alternative Hypothesis ($H_{1, \text{BEHAV}}$):**
  $$-\Delta_{\text{equiv}} < \mu_{C1} - \mu_{C0} < +\Delta_{\text{equiv}}$$
  (The behavior of C1 is practically equivalent to C0).
- **Decision Rule:** Evaluated via Two One-Sided Tests (TOST) at $\alpha = 0.05$. Equivalent to testing whether the paired two-sided $90\%$ confidence interval for $\Delta = C_1 - C_0$ lies entirely within $[-\Delta_{\text{equiv}}, +\Delta_{\text{equiv}}]$.

---

## 3. Preregistered Practical Equivalence Margins ($\Delta_{\text{equiv}}$)

All bounds derived objectively from the empirical variance of $T_3$ in the sealed parent study (`LEBRE_V0_2_SEED_RESULTS.csv`, $N=30$):

| Domain | Metric | Frozen Margin ($\Delta_{\text{equiv}}$) | Unit | Analytical Derivation & Source Reference |
|:---|:---|:---:|:---:|:---|
| **Predictive** | Aggregate Benchmark NMSE | $\pm 0.0100$ | NMSE | $0.5 \times \text{SD}(NMSE_{T3}) = 0.0125$; restricts mean divergence to $< 1$ percentage point |
| **Predictive** | Pure Lag NMSE ($I_3, I_4, I_5, I_8$) | $\pm 0.0150$ | NMSE | Within standard error of lag tracking across seeds ($SE \approx 0.018$) |
| **Structural** | Lag Support F1 ($I_3, I_4$) | $\pm 0.0500$ | F1 Score | Parent study support F1 standard error is $0.042$ |
| **Arbitration**| $I_{10}$ Dual Occupancy (`frac_both`)| $\pm 0.0200$ | Proportion | Standard error is $0.015$; ensures arbitration remains stable |
| **Dynamic** | Hybrid Conditional Gains ($I_9$) | $\pm 0.0050$ | Gain | Significance threshold is $\theta = 0.010$; margin is $0.5 \times \theta$ |
| **Adaptation** | Regime Switch Latency ($I_{11}..I_{13}$)| $\pm 50.0$ | Steps | $\le 5\%$ of the $1,000$-step adaptation window |

---

## 4. Predefined Critical Task Groups

1. **`PURE_LAG`:** Tasks $I_3$ (Single Delay), $I_4$ (Multi-Sparse Delay), $I_5$ (Moving Support), $I_8$ (Quiescent Delay).
2. **`HYBRID`:** Tasks $I_9$ (Hybrid Delay + Latent), $I_{13}$ (Hybrid $\to$ Memoryless), $I_{14}$ (Intermittent Hybrid).
3. **`SWITCHING`:** Tasks $I_{11}$ (Delay $\to$ Latent), $I_{12}$ (Latent $\to$ Delay), $I_{13}$ (Hybrid $\to$ Memoryless), $I_{14}$ (Intermittent Hybrid).
4. **`NEGATIVE_CONTROL`:** Tasks $I_1$ (Memoryless Linear), $I_2$ (Static Nonlinear).
5. **`REDUNDANCY`:** Task $I_{10}$ (Redundant Temporal Structure).

---

## 5. Decision Stratification & Threshold Jitter Definition

To investigate potential quantization chatter near the candidate promotion boundary ($\theta = 0.20$):
- **`NEAR_THRESHOLD`:** Candidate correlation score $C_{\text{fp32}}$ satisfies $| |C_{\text{fp32}}| - 0.20 | \le 0.0100$ ($[0.190, 0.210]$);
- **`FAR_FROM_THRESHOLD`:** Candidate correlation score satisfies $| |C_{\text{fp32}}| - 0.20 | > 0.0100$.

Disagreements in candidate ranking or promotion will be explicitly stratified by this distance metric to distinguish boundary quantization noise from systematic algorithmic divergence.

---

## 6. Seed Cohort Allocation

- **DEV Seeds:** `1401`, `1402`, `1403`, `1404`, `1405`, `1406`, `1407`, `1408`, `1409`, `1410` ($N=10$).
- **FINAL Seeds:** `1411`..`1440` ($N=30$ contiguous fresh seeds).
- Both seed cohorts are cryptographically verified to have zero prior exposure in LEBRE history.
