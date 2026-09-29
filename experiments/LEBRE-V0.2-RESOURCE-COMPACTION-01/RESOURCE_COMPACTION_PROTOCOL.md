# Protocol: Resource Compaction of the Correlation Grid

**Document Identifier:** `RESOURCE_COMPACTION_PROTOCOL.md`  
**Study Identifier:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Auditor / Researcher:** Independent Skeptical Senior Researcher  
**Date:** September 2026  
**Status:** Frozen Protocol  

---

## 1. Scope, Purpose & Research Objective

This protocol governs the targeted empirical investigation into reducing the persistent precision of the correlation-state grid (`corr_grid`) in the LEBRE candidate architecture $T_3$ (*Resource-Aware Conditional Arbitration*).

The primary objective is to evaluate whether casting the persistent representation of `corr_grid` from `float32` (FP32) to IEEE 754 half-precision `float16` (FP16) restores compliance with the historical R2 1-KiB memory ceiling (`TOTAL_PERSISTENT_BYTES <= 1024`) while preserving the predictive, structural, and arbitration dynamics of the sealed FP32 candidate.

---

## 2. Experimental Topologies & Implementation Boundary

### 2.1 C0 — FP32_GRID_REFERENCE
- **Specification:** The exact sealed implementation of $T_3$ from `LEBRE-V0.2-INTEGRATION-DESIGN-01`.
- **Persistent State:** `corr_grid` allocated as `np.zeros((5, 33), dtype=np.float32)`.
- **Storage Footprint:** $5 \times 33 \times 4 = 660$ Bytes.
- **Total Persistent State:** $1,306$ Bytes.
- **Arithmetic:** Full FP32 arithmetic, accumulation, and threshold evaluation.

### 2.2 C1 — FP16_GRID_FP32_UPDATE
- **Specification:** The targeted resource-compacted variant of $T_3$.
- **Persistent State:** `corr_grid` allocated as `np.zeros((5, 33), dtype=np.float16)`.
- **Storage Footprint:** $5 \times 33 \times 2 = 330$ Bytes.
- **Total Persistent State:** $1,306 - 660 + 330 = 976$ Bytes ($\le 1024$ Bytes).
- **Update Protocol:**
  1. Read stored cell value in FP16: $c_{\text{old}} \leftarrow \text{corr\_grid}[i_p, k_p]$;
  2. Cast to FP32 transient register: $c_{\text{fp32}} \leftarrow \text{float32}(c_{\text{old}})$;
  3. Perform exponential moving average update in FP32:
     $$c_{\text{new, fp32}} \leftarrow 0.95 \cdot c_{\text{fp32}} + 0.05 \cdot (e_{\text{probe}} \cdot x_{i_p, t-k_p})$$
  4. Perform candidate threshold comparison in FP32:
     $$\text{is\_candidate} \leftarrow |c_{\text{new, fp32}}| > 0.20$$
  5. Round and write updated value back to FP16:
     $$\text{corr\_grid}[i_p, k_p] \leftarrow \text{float16}(c_{\text{new, fp32}})$$
- **Strict Prohibition:** No persistent FP32 master copy of `corr_grid` may exist. Transient register workspace is limited to scalar registers ($\le 12$ Bytes) and ceases to exist upon completing the probe step.

---

## 3. Invariants & Controlled Factors

To isolate the causal impact of correlation grid precision, C0 and C1 must share identical configurations:
1. **Streaming Data:** Identical pseudo-random sequence generators, stream initializations, and evaluation windows ($T=6000$, evaluation $t \in [1000, 6000)$).
2. **Feature Scaler:** Shared online Welford standardizer (persistent: $20$ B).
3. **History Ring:** Shared circular buffer of length $L_{\text{max}} + 1 = 33$ across $D=5$ features (persistent: $660$ B).
4. **Linear Predictor:** Shared online LMS baseline (persistent: $24$ B).
5. **Probing Schedule:** Shared round-robin schedule across the $165$ cell pairs with probe batch size $M=2$.
6. **Candidate Lifecycle:** Shared promotion thresholds ($\theta_{\text{prom}} = 0.20, R_{\text{prom}} = 0.10, \tau_{\text{prom}} = 20$), active tap capacity ($K_{\text{max}} = 3$), and eviction logic.
7. **Recurrent Dynamics:** Shared scalar recurrent unit, shadow unit, and update equations.
8. **Arbitrator:** Shared conditional gain estimation, hysteresis thresholds, and state transition rules.

---

## 4. Benchmark Suite & Seed Allocation

### 4.1 Benchmark Tasks
All 14 integration tasks ($I_1$ to $I_{14}$) are evaluated without exclusion:
- *Memoryless / Negative Controls:* $I_1$ (Linear), $I_2$ (Static Nonlinear);
- *Pure Delay Regimes:* $I_3$ (Single Delay), $I_4$ (Multi-Sparse Delay), $I_5$ (Moving Delay Support), $I_8$ (Quiescent Discrete Delay);
- *Latent Continuous Regimes:* $I_6$ (Continuous Latent State), $I_7$ (Quiescent Continuous State);
- *Hybrid Regimes:* $I_9$ (Hybrid Delay + Latent), $I_{10}$ (Redundant Structure), $I_{14}$ (Intermittent Hybrid);
- *Non-Stationary Switching Regimes:* $I_{11}$ (Delay $\to$ Latent), $I_{12}$ (Latent $\to$ Delay), $I_{13}$ (Hybrid $\to$ Memoryless).

### 4.2 Seed Cohorts
To prevent data snooping and maintain confirmatory integrity, seeds are partitioned as follows:
- **DEV Cohort:** Seeds `1401`..`1410` ($N=10$, verified fresh). Used exclusively for implementation validation, numerical microtraces, zero NaN/Inf assertions, and pipeline integrity checks.
- **FINAL Cohort:** Seeds `1411`..`1440` ($N=30$, verified fresh). Executed strictly once under frozen protocols for confirmatory inference.

---

## 5. Diagnostic Protocols & Intermediate Datasets

### 5.1 Numerical Microtrace (`NUMERICAL_MICROTRACE.csv`)
Logs every update to `corr_grid` on an identical stream for 500 steps, recording:
`step`, `feature_i`, `lag_k`, `fp32_before`, `fp16_stored_before`, `fp32_update_result`, `fp16_stored_after`, `absolute_error`, `relative_error`, `ulp_spacing`.

### 5.2 Numerical Stress Suite (`NUMERICAL_STRESS_RESULTS.csv`)
Deterministic synthetic tests evaluating FP16 boundary conditions:
- Test A: Normal correlation range ($[-0.8, +0.8]$);
- Test B: Micro-updates near FP16 resolution ($|\Delta C| < 10^{-4}$);
- Test C: Values approaching zero ($|C| < 10^{-5}$, subnormal transition);
- Test D: Values hovering at threshold boundary ($\theta = 0.20 \pm 10^{-4}$);
- Test E: Near-tied candidate ranking ($\Delta C_{12} < 10^{-4}$);
- Test F: Rapid sign oscillations ($\pm 0.15$ sign flips);
- Test G: Maximum magnitude extremes ($|C| \to 1.0$).

### 5.3 Candidate-Ranking Parity (`CANDIDATE_RANKING_PARITY.csv`)
At every probing opportunity, compare C0 and C1 candidate rankings:
`TOP1_AGREEMENT_RATE`, `TOPM_SET_AGREEMENT_RATE`, `PAIRWISE_RANK_INVERSION_RATE`, `PROMOTION_THRESHOLD_DISAGREEMENT_RATE`.

### 5.4 Structural Event Parity (`STRUCTURAL_EVENT_PARITY.csv`)
Compare paired structural events: candidate births, lag promotions/evictions, recurrent promotions/evictions, and arbitration state occupancy (`NONE`, `LAG`, `RECURRENT`, `BOTH`).

---

## 6. Governance Rules on Known Open Issues

1. **Gate 6 (Redundancy Ceiling $\le 0.05$ on $I_{10}$):**
   This stage does NOT attempt to fix Gate 6. The historical status remains `FAIL`. If C1 exhibits a different `frac_both` on $I_{10}$, it is reported descriptively as `INCIDENTAL_EXPLORATORY_CHANGE`. If C1 worsens `frac_both` beyond equivalence margins, it counts as a behavioral preservation failure.
2. **Exact Lag-Support Specificity on $I_3/I_4$:**
   The historical status remains `PARTIAL`. Any shift in support F1 is evaluated against equivalence bounds. Intentional parameter tuning to improve precision/recall is strictly prohibited.
3. **Compute Status:**
   FP16 memory compaction does not resolve the legacy total-online compute failure ($108.2 > 100$ FLOPs). Total compute governance is reserved for the subsequent shadow-rent study.

---

## 7. Success & Failure Criteria

### 7.1 Mandatory Failure Conditions
C1 fails resource compaction if any of the following occur:
- **Fail A:** `TOTAL_PERSISTENT_BYTES > 1024`;
- **Fail B:** Any NaN, Inf, or uncaught overflow is observed;
- **Fail C:** Update stagnation systematically halts candidate discovery;
- **Fail D:** Predictive degradation exceeds preregistered TOST equivalence bounds;
- **Fail E:** Lag support F1 degrades beyond preregistered bounds;
- **Fail F:** Hybrid complementarity classification on $I_9$ changes from `COMPLEMENTARY`;
- **Fail G:** Arbitration state distribution diverges beyond preregistered tolerance;
- **Fail H:** An unreported persistent FP32 master copy is required.

### 7.2 Definitive Success Conditions
C1 is declared `RESOURCE_COMPACTION_SUPPORTED` if and only if:
1. Measured `TOTAL_PERSISTENT_BYTES <= 1024`;
2. Zero persistent FP32 master grid is present;
3. Complete numerical stability (0 NaN, 0 Inf, 0 uncaught overflows);
4. Predictive equivalence is established via TOST;
5. Structural decision parity and hybrid complementarity are preserved;
6. Resource ledger is fully reconciled.
