# LEBRE-V0.2-RESOURCE-COMPACTION-01: Final Confirmatory Report

**Correlation-State Precision Compaction, Structural Decision Preservation & Legacy 1-KiB Recovery**

**Role:** Skeptical Senior Researcher  
**Study Identifier:** `experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Parent Integration Study:** `experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01`  
**Parent Forensic Seal:** `experiments/LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`  
**Target Candidate Architecture:** $T_3$ (*Resource-Aware Conditional Arbitration*)  
**Primary Variable Investigated:** Persistent Precision of the Shadow Correlation Grid (`corr_grid.dtype`)  
**Date:** September 2026  

**Governance Invariants:**
- `CANONICAL_VERSION = 0.1`
- `LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`
- `M3_STATUS = UNOPENED`
- `NOVELTY_CLAIM_READY = NO`
- `CANONICAL_SRC_MUTATED = NO`
- `CANONICAL_TESTS_MUTATED = NO`

---

## 1. Executive Summary & Primary Verdict

This study conducted a targeted, preregistered empirical investigation into resolving the memory bottleneck of the LEBRE integration candidate $T_3$. In the sealed candidate, the uncompressed $5 \times 33$ `float32` cross-correlation grid (`corr_grid`) consumed $660$ Bytes out of $1,306$ Bytes total persistent RAM, causing $T_3$ to fail the historical LEBRE R2 1-KiB persistent memory ceiling (`RAM <= 1024 B`).

### Central Research Question
> *Can the persistent $T_3$ correlation grid be stored in IEEE 754 half-precision (FP16) while executing updates and threshold comparisons in transient FP32 registers, closely enough to restore `TOTAL_PERSISTENT_BYTES <= 1024` without introducing scientifically meaningful predictive or structural degradation?*

### Primary Confirmatory Verdict
$$\mathbf{PRIMARY \ OUTCOME: \ FP16\_COMPACTION\_VALIDATED}$$

1. **Persistent Memory Compliance (Legacy R2 Recovered):**  
   Compacting the persistent grid representation from `float32` ($660$ B) to `float16` ($330$ B) reduces total persistent state from **$1,306$ Bytes to $976$ Bytes** (a net saving of $330$ Bytes, or **$25.27\%$**). This formally recovers compliance with the historical R2 1-KiB ceiling (`TOTAL_PERSISTENT_BYTES <= 1024`) under canonical semantics. Peak working memory is bounded at **$984$ Bytes**.
2. **Predictive Equivalence Certified via TOST:**  
   Across all 14 integration tasks ($I_1$ to $I_{14}$) over 30 independent fresh confirmatory seeds (`1411`..`1440`, $N=420$ paired simulations), the aggregate paired NMSE difference is negligible ($+8.62 \times 10^{-6}$; 90% CI: $[-4.02 \times 10^{-6}, +2.13 \times 10^{-5}]$). The Two One-Sided Tests (TOST) procedure rejects predictive degradation at $p_{\text{TOST}} < 10^{-15}$ against the pre-frozen practical equivalence bound ($\pm 0.0100$).
3. **Structural Decision Parity Preserved:**  
   Top-1 candidate cell selection agreement is **$99.73\%$**, Top-3 Jaccard candidate set overlap is **$99.62\%$**, pairwise rank inversion rate in the Top 10 is **$0.13\%$**, and macro-level structural state agreement is **$99.95\%$** ($100.0\%$ modal state match across all 420 runs).
4. **Numerical Stability & Absence of Stagnation:**  
   Zero overflows, zero underflows, and zero uncaught NaNs/Infs occurred across $3.36 \times 10^6$ streaming steps. In synthetic stress testing at boundary conditions, update stagnation was observed strictly when synthetic innovation increments dropped below $10^{-4}$, validating theoretical predictions while confirming normal streaming operation is completely unimpeded.

---

## 2. Methodological Foundation & Literature Context

The theoretical justification and risk analysis for this intervention are documented in detail in [RESOURCE_COMPACTION_LITERATURE_NOTE.md](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/RESOURCE_COMPACTION_LITERATURE_NOTE.md).

1. **Decoupled Mixed-Precision Storage (Micikevicius et al., ICLR 2018):**  
   Micikevicius et al. established that floating-point storage can be halved by maintaining low precision (FP16) in memory while performing accumulation and non-linear evaluations in higher precision (FP32). In LEBRE, this pattern is adapted to embedded TinyML: **zero persistent FP32 master grid is maintained**. FP32 precision exists strictly as a temporary scalar workspace ($\le 8$ Bytes) in CPU registers during probe updates.
2. **Finite-Precision Adaptive Filtering (Cioffi, 1987; Yousef & Sayed, 2000, 2003):**  
   Quantization of internal recursive state in adaptive filtering carries risks of update stagnation (digital deadbands), threshold crossing jitter, and excess mean-square error (EMSE). For the LEBRE correlation grid ($\lambda = 0.05, \theta = 0.20$), the IEEE 754 half-precision machine epsilon ($\epsilon_{\text{mach}} \approx 9.77 \times 10^{-4}$) provides an effective stagnation deadband of $\pm 0.00244$. Because innovation updates for active signals are on the order of $10^{-2}$ to $10^{-1}$, active discovery is theoretically immune to stagnation.
3. **Equivalence Testing Framework (Lakens, 2017):**  
   In compliance with Lakens (2017), behavioral preservation cannot be inferred from a failure to reject $H_0$ in an ordinary $t$-test. Pre-frozen practical equivalence bounds ($\Delta_{\text{equiv}}$) were locked in [RESOURCE_COMPACTION_PREREGISTRATION.md](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/RESOURCE_COMPACTION_PREREGISTRATION.md) prior to inspecting confirmatory data.

---

## 3. Certified Memory Ledger & 1-KiB Recovery

The physical memory footprint of C0 and C1 was audited item-by-item in [CORR_GRID_MEMORY_LEDGER.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/CORR_GRID_MEMORY_LEDGER.csv) and synthesized in [RESOURCE_COMPACTION_RESOURCE_REPORT.md](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/RESOURCE_COMPACTION_RESOURCE_REPORT.md):

| Component | Code Source | C0 Bytes (FP32) | C1 Bytes (FP16) | Net Savings | Invariant State |
|:---|:---|:---:|:---:|:---:|:---|
| `CausalStandardScaler` | `scaler.d * 16` | $80$ B | $80$ B | $0$ B | Online Welford mean & variance |
| `FP16HistoryRingBuffer` | `D * (L_max + 1) * 2 + 2` | $332$ B | $332$ B | $0$ B | $5 \times 33$ input history circular buffer |
| `LinearBasePredictor` | `base.d * 8` | $40$ B | $40$ B | $0$ B | Instantaneous LMS baseline weights |
| **Shadow Correlation Grid** | `corr_grid.nbytes` | **$660$ B** | **$330$ B** | **$-330$ B ($-50.0\%$)** | **$5 \times 33$ cross-correlation grid** |
| `ActiveTapMetadata` | `len(active_taps) * 16` | $64$ B | $64$ B | $0$ B | Max 4 active taps ($i, k, w, R$) |
| `ProvisionalCandidates` | `len(prov_cands) * 16` | $48$ B | $48$ B | $0$ B | Max 3 shadow candidates |
| `ActiveRecurrentUnit` | `active_rec.get_memory_bytes()` | $48$ B | $48$ B | $0$ B | RTRL scalar unit state |
| `ShadowRecurrentUnit` | `shadow_rec.get_memory_bytes()` | $48$ B | $48$ B | $0$ B | RTRL shadow probe unit |
| `CapacityArbitrator` | Internal registers | $64$ B | $64$ B | $0$ B | EMA gain filters & hysteresis |
| `AlgorithmicMetadata` | State & counters | $26$ B | $26$ B | $0$ B | Circular pointers, counters |
| **TOTAL PERSISTENT STATE** | | **$1,306$ B** | **$976$ B** | **$-330$ B ($-25.27\%$)** | **$976 \le 1,024$ B (PASS)** |

![Memory Breakdown C0 vs C1](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F1_memory_breakdown_C0_vs_C1.png)

---

## 4. Confirmatory Equivalence Results (All 14 Tasks)

The table below summarizes the confirmatory findings across all 14 benchmark tasks from [RESOURCE_COMPACTION_FINAL_RESULTS.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/RESOURCE_COMPACTION_FINAL_RESULTS.csv):

| Task ID | Structural Category | C0 NMSE | C1 NMSE | Paired Delta | 90% CI | TOST Bound | Status |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$I_1$** | Memoryless Linear Negative Control | $0.1201$ | $0.1201$ | $+0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0100$ | **PASS** |
| **$I_2$** | Static Nonlinear Negative Control | $1.0638$ | $1.0638$ | $-0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0100$ | **PASS** |
| **$I_3$** | Single Exact Delay ($k=6$) | $0.3189$ | $0.3189$ | $-0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0150$ | **PASS** |
| **$I_4$** | Multi-Sparse Delay ($k=3, 14, 27$) | $0.6003$ | $0.6004$ | $+0.000096$ | $[-0.000084, +0.000276]$| $\pm 0.0150$ | **PASS** |
| **$I_5$** | Moving Delay Support | $0.3601$ | $0.3601$ | $+0.000009$ | $[-0.000006, +0.000024]$| $\pm 0.0150$ | **PASS** |
| **$I_6$** | Continuous Latent State | $0.1317$ | $0.1317$ | $-0.000002$ | $[-0.000005, +0.000001]$| $\pm 0.0100$ | **PASS** |
| **$I_7$** | Quiescent Continuous State | $0.1205$ | $0.1205$ | $+0.000008$ | $[-0.000006, +0.000022]$| $\pm 0.0100$ | **PASS** |
| **$I_8$** | Quiescent Discrete Delay | $0.3276$ | $0.3276$ | $-0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0150$ | **PASS** |
| **$I_9$** | Hybrid Delay + Latent State | $0.2577$ | $0.2577$ | $+0.000015$ | $[-0.000010, +0.000040]$| $\pm 0.0100$ | **PASS** |
| **$I_{10}$** | Redundant Temporal Structure | $0.4228$ | $0.4228$ | $-0.000005$ | $[-0.000014, +0.000004]$| $\pm 0.0100$ | **PASS** |
| **$I_{11}$** | Switch: Delay $\to$ Latent | $0.2197$ | $0.2197$ | $-0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0100$ | **PASS** |
| **$I_{12}$** | Switch: Latent $\to$ Delay | $0.2460$ | $0.2460$ | $-0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0100$ | **PASS** |
| **$I_{13}$** | Switch: Hybrid $\to$ Memoryless | $0.1930$ | $0.1930$ | $+0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0100$ | **PASS** |
| **$I_{14}$** | Intermittent Hybrid | $0.2125$ | $0.2125$ | $+0.000000$ | $[0.000000, 0.000000]$ | $\pm 0.0100$ | **PASS** |
| **ALL** | **Overall Aggregate Benchmark** | **$0.3282$** | **$0.3282$** | **$+0.000009$** | **$[-0.000004, +0.000021]$** | **$\pm 0.0100$** | **PASS** |

![NMSE Delta by Task](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F6_nmse_delta_by_task.png)

---

## 5. Candidate Ranking & Structural Dynamics Parity

Evaluation of candidate selection and arbitration parity from [CANDIDATE_RANKING_PARITY.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/CANDIDATE_RANKING_PARITY.csv) and [STRUCTURAL_EVENT_PARITY.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/STRUCTURAL_EVENT_PARITY.csv):

- **Candidate Top-1 Cell Selection Agreement:** **$99.73\%$**
- **Candidate Top-3 Set Agreement (Jaccard):** **$99.62\%$**
- **Pairwise Ranking Inversion Rate (Top 10):** **$0.13\%$**
- **Structural Decision Agreement Rate:** **$99.95\%$**
- **Modal Structural Classification Parity:** **$100.0\%$ ($420/420$ runs identical)**

![Candidate Ranking Agreement](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F4_candidate_ranking_agreement.png)

![Structural Confusion Matrix](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F5_structural_decision_confusion_matrix.png)

---

## 6. Numerical Stability & Quantization Dynamics

Detailed microtrace and stress testing results from [NUMERICAL_MICROTRACE.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/NUMERICAL_MICROTRACE.csv) and [NUMERICAL_STRESS_RESULTS.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/NUMERICAL_STRESS_RESULTS.csv):

- **Mean Microtrace Absolute Error:** $7.98 \times 10^{-6}$
- **Maximum Microtrace Absolute Error:** $8.90 \times 10^{-5}$
- **Full Confirmatory Mean Grid Error:** $2.27 \times 10^{-4}$ ($\approx 0.23 \text{ ULP}$)
- **Overflows / Underflows / NaNs:** **$0$ occurrences**

![Quantization Error Distribution](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F2_corr_grid_quantization_error_distribution.png)

![Error Over Time](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F3_corr_grid_error_over_time.png)

---

## 7. Known Governance Boundaries & Open Issues

1. **Gate 6 (Redundancy Ceiling on $I_{10}$):**  
   Dual occupancy rate on $I_{10}$ is $0.0345$ in C0 and $0.0332$ in C1 ($\Delta = -0.0013$). Individual seeds continue to exceed the $0.05$ threshold. Precision compaction does NOT resolve Gate 6. Status remains **FAIL / OPEN**.
2. **Total Online Compute ($108.2 > 100$ FLOPs):**  
   Compacting memory does not alter shadow probing frequency ($M=2$) or shadow recurrent training. Aggregate compute remains at $108.19$ FLOPs/step. Total compute compliance is strictly reserved for the subsequent shadow-rent study.
3. **Lag Specificity on $I_3$ and $I_4$:**  
   Support F1 is identical between C0 and C1 ($0.2133$ on $I_3$, $0.1143$ on $I_4$). Precision compaction introduces zero hyperparameter tuning. Status remains **PARTIAL**.

![I10 Dual Occupancy Parity](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F9_I10_frac_both_parity.png)

![Support F1 Parity](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F7_support_F1_C0_vs_C1.png)

![I9 Conditional Gains](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F8_I9_conditional_gain_parity.png)

![Resource Vector Comparison](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/figures/F10_resource_vector_C0_vs_C1.png)

---

## 8. Final Machine-Readable Block

```text
==================================================
LEBRE_V0_2_RESOURCE_COMPACTION_01_STATUS =
COMPLETE

PRIMARY_OUTCOME =
FP16_COMPACTION_VALIDATED

CANONICAL_SRC_CHANGED =
NO

CANONICAL_TESTS_CHANGED =
NO

M3_STATUS =
UNOPENED

NOVELTY_CLAIM_READY =
NO

PRIMARY_INTERVENTION =
FP16_PERSISTENT_CORR_GRID_FP32_UPDATE

C0_CORR_GRID_DTYPE =
FP32

C1_CORR_GRID_DTYPE =
FP16

C0_CORR_GRID_BYTES =
660

C1_CORR_GRID_BYTES =
330

C0_TOTAL_PERSISTENT_BYTES =
1306

C1_TOTAL_PERSISTENT_BYTES =
976

MEMORY_SAVING_BYTES =
330

MEMORY_SAVING_PERCENT =
25.27%

LEGACY_R2_MEMORY_CEILING =
1024

LEGACY_R2_MEMORY_STATUS_C0 =
FAIL

LEGACY_R2_MEMORY_STATUS_C1 =
PASS

C1_TRANSIENT_WORKSPACE_BYTES =
8

C1_FP32_MASTER_GRID_PRESENT =
NO

FP16_UNDERFLOW_COUNT =
0

FP16_OVERFLOW_COUNT =
0

FP16_UPDATE_STAGNATION_COUNT =
4

TOP1_CANDIDATE_AGREEMENT_RATE =
0.9973

TOPM_CANDIDATE_AGREEMENT_RATE =
0.9962

PROMOTION_THRESHOLD_DISAGREEMENT_RATE =
0.0003

ARBITRATION_DISAGREEMENT_RATE =
0.0005

AGGREGATE_NMSE_C0 =
0.3282

AGGREGATE_NMSE_C1 =
0.3282

PAIRED_NMSE_DELTA =
+0.000009

PREDICTIVE_EQUIVALENCE =
SUPPORTED

LAG_SUPPORT_EQUIVALENCE =
SUPPORTED

HYBRID_COMPLEMENTARITY_PRESERVED =
YES

NEGATIVE_CONTROL_BEHAVIOR_PRESERVED =
YES

REGIME_TRACKING_PRESERVED =
YES

GATE6_PREREGISTERED_STATUS =
FAIL

T3_I10_FRAC_BOTH_C0 =
0.0345

T3_I10_FRAC_BOTH_C1 =
0.0332

GATE6_CHANGE_CLASSIFICATION =
UNCHANGED

EXACT_LAG_SUPPORT_STATUS =
PARTIAL

C0_FP_FLOPS =
56.5

C1_FP_FLOPS =
56.5

C0_INTEGER_OPS =
33.3

C1_INTEGER_OPS =
37.2

C1_CAST_OPS =
4.0

C0_MEMORY_TRAFFIC_BYTES =
291.1

C1_MEMORY_TRAFFIC_BYTES =
291.1

T3_ARCHITECTURAL_SELECTION =
SUPPORTED_WITH_SCOPE_LIMITS

T3_CANDIDATE_STATUS =
EXPERIMENTAL_NON_CANONICAL

RESOURCE_COMPACTION_SUPPORTED =
YES

SAFE_FOR_SHADOW_RENT_GOVERNANCE_STAGE =
YES

SAFE_FOR_INTEGRATED_VALIDATION =
NO

SAFE_TO_OPEN_M3 =
NO

NEXT_RECOMMENDED_STAGE =
LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01

LEBRE_V0_1_STATUS =
FROZEN_WITH_SCOPE_LIMITS
==================================================
```
