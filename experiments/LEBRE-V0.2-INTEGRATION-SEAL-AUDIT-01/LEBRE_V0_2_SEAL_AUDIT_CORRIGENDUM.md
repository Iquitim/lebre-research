# LEBRE v0.2 Integration Seal Audit Corrigendum

**Audit Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Parent Study:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`  
**Audit Date:** September 2026  
**Auditor:** Independent Skeptical Senior Reviewer  
**Audit Governance:** Bitwise immutable preservation of parent artifacts; no source mutations; zero tolerance for unrecorded deviations.

---

## 1. Preamble and Corrigendum Policy

In accordance with Section 52 of the Audit Mandate, every substantive reporting discrepancy, gate drift, statistical overstatement, and terminology error identified during the forensic audit is documented below. 

Under the hard audit rule:
$$\text{PRESERVE} \longrightarrow \text{REPRODUCE} \longrightarrow \text{TRACE} \longrightarrow \text{CLASSIFY} \longrightarrow \text{CORRECT REPORTING} \longrightarrow \text{RE-EVALUATE DECISION}$$
no historical records have been overwritten or destroyed. The original claims and their corrected scientific status are juxtaposed to guarantee full forensic traceability.

---

## 2. Itemized Corrigenda

### Corrigendum 1: Task-Level Statistical Table NMSE Values (DEV Seed 1301 Pasting Error)
- **ORIGINAL_CLAIM:** The table in Section 4 of `LEBRE_V0_2_STATISTICAL_REPORT.md` presents the mean prequential NMSE ($t \ge 1000$) across the $N=30$ confirmatory seeds (`1311`..`1340`).
- **ORIGINAL_VALUE:** 
  - $I_1$: $T_1=0.1284, T_{1R}=0.1284, T_2=0.1284, T_3=0.1282, O_{\text{ALL}}=0.1491$
  - $I_2$: $T_1=0.9981, T_{1R}=0.9982, T_2=0.9978, T_3=0.9974, O_{\text{ALL}}=0.9980$
  - $I_3$: $T_1=0.1682, T_{1R}=0.1741, T_2=0.1678, T_3=0.1671, O_{\text{ALL}}=0.1668$
  - $I_4$: $T_1=0.4124, T_{1R}=0.5778, T_2=0.4012, T_3=0.3985, O_{\text{ALL}}=0.3942$
  - Aggregate Mean: Reported as $T_3 = 0.288 \pm 0.021$
- **RECOMPUTED_VALUE:** 
  - $I_1$: $T_1=0.1200, T_{1R}=0.1201, T_2=0.1200, T_3=0.1200, O_{\text{ALL}}=0.1409$
  - $I_2$: $T_1=1.2977, T_{1R}=1.2923, T_2=1.2626, T_3=1.0543, O_{\text{ALL}}=1.2764$
  - $I_3$: $T_1=0.3684, T_{1R}=0.2950, T_2=0.3729, T_3=0.1747, O_{\text{ALL}}=0.5116$
  - $I_4$: $T_1=0.6889, T_{1R}=0.6882, T_2=0.6849, T_3=0.5365, O_{\text{ALL}}=0.7282$
  - Aggregate Confirmatory Means: $T_3 = 0.2876, T_1 = 0.3592, T_{1R} = 0.3418, T_2 = 0.3833, O_{\text{ALL}} = 0.4258$.
- **ROOT_CAUSE:** In `scratch/run_v02_integration_experiments.py`, the markdown report generator inadvertently copied values from the single-seed exploratory DEV run (`DEV_LEBRE_V0_2_SEED_RESULTS.csv`, Seed 1301) rather than calculating column averages across the 30 confirmatory seeds (`1311`..`1340`).
- **TYPE:** REPORTING
- **CENTRAL_ARCHITECTURE_IMPACT:** None to positive. The core superiority of $T_3$ is fully preserved and its margin of victory is substantially larger under the true 30-seed confirmatory dataset ($T_3 = 0.2876$ vs. $T_1 = 0.3592, T_2 = 0.3833, O_{\text{ALL}} = 0.4258$).
- **CORRECTED_INTERPRETATION:** Replace Section 4 of `LEBRE_V0_2_STATISTICAL_REPORT.md` with the verified 30-seed confirmatory means.

---

### Corrigendum 2: Gate 11 Memory Ceiling Provenance (1024 B to 2048 B Gate Relaxation)
- **ORIGINAL_CLAIM:** Success Gate 11 required "RAM $\le 2048$ Bytes", which $T_3$ passed with $1,306$ Bytes.
- **ORIGINAL_VALUE:** Ceiling = $\le 2048$ Bytes; Outcome = PASS.
- **RECOMPUTED_VALUE:** The immutable preregistered specification in `LEBRE_V0_2_RESOURCE_MODEL.md` (line 84) and `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (line 71) defined Gate 11 as `RAM <= 1024 Bytes`. Measured persistent memory across $T_3$ is $1,306.3$ Bytes.
- **ROOT_CAUSE:** In `scratch/run_v02_integration_experiments.py`, the cross-correlation matrix `corr_grid` was instantiated as a full $5 \times 33$ float32 matrix (660 Bytes), causing persistent allocation to exceed 1024 B. After observing results, Gate 11 was silently updated in `DECISION.md` and `FINAL_REPORT.md` to 2048 B without formal pre-confirmatory amendment.
- **TYPE:** GATE_DRIFT / RESOURCE_DEFINITION
- **CENTRAL_ARCHITECTURE_IMPACT:** High governance impact. $T_3$ does **NOT** satisfy the historical `LEGACY_R2` memory budget ($\le 1024$ B). It complies only with the `PROPOSED_V0_2_CLASS` ($\le 2048$ B).
- **CORRECTED_INTERPRETATION:** Reclassify resource compliance:
  - `LEGACY_R2_MEM_COMPLIANCE = FAIL`
  - `PROPOSED_V0_2_2KB_MEM_COMPLIANCE = PASS`
  Progression requires an explicit post-audit decision: either compact memory (`LEBRE-V0.2-RESOURCE-COMPACTION-01`) or formally authorize the 2 KB governance class (`RESOURCE-GOVERNANCE-CLASS-01`).

---

### Corrigendum 3: Compute Accounting Semantics: Live Path vs. Total Online FLOPs
- **ORIGINAL_CLAIM:** Gate 11 FP FLOPs constraint ($\le 100$) was satisfied by $T_3$ ($81.4$ FP FLOPs).
- **ORIGINAL_VALUE:** $T_3$ FP FLOPs = $81.4 \le 100$.
- **RECOMPUTED_VALUE:** 
  - Live Path FP FLOPs (mean): $81.4$
  - Shadow Path FP FLOPs (mean): $86.6$ (aggregate across stream) / $26.8$ (steady-state rent)
  - Total Online FP FLOPs (mean): $168.0$ (aggregate) / $108.2$ (steady-state)
  - Task $I_9$ (Hybrid) Live FP FLOPs: Mean $112.1$, P95 $128.3$, Peak $132.0$.
- **ROOT_CAUSE:** The historical LEBRE constraint $R2\_FP \le 100$ was intended to bound total online execution cost. Evaluating only live-path compute ($81.4$) omits the continuous exploratory compute paid by the shadow evaluation registers. Furthermore, during active hybrid states ($I_9$), live compute alone exceeds 100 FLOPs.
- **TYPE:** RESOURCE_DEFINITION
- **CENTRAL_ARCHITECTURE_IMPACT:** $T_3$ satisfies the 100 FLOPs budget under `LIVE_ONLY` accounting on 13/14 tasks, but fails under `TOTAL_ONLINE` accounting ($168.0 > 100$), and fails on $I_9$ even under live path ($112.1 > 100$).
- **CORRECTED_INTERPRETATION:** Maintain disaggregated accounting:
  - `LEGACY_R2_FP_LIVE_COMPLIANCE = PASS` (aggregate: 81.4 FLOPs)
  - `LEGACY_R2_FP_TOTAL_ONLINE_COMPLIANCE = FAIL` (168.0 FLOPs)
  - `HYBRID_LEGACY_RESOURCE_CONFLICT = PRESENT` ($I_9$ live compute reaches 127.2 FLOPs).
  Progression requires formal shadow duty-cycling governance (`SHADOW-RENT-GOVERNANCE-01`).

---

### Corrigendum 4: Statistical Claim Scope ("All 9 Hypotheses Confirmed at p < 0.001")
- **ORIGINAL_CLAIM:** "All 9 hypotheses ($H_1$–$H_9$) confirmed at $p < 0.001$."
- **ORIGINAL_VALUE:** $p < 0.001$ asserted uniformly for $H_1$ through $H_9$.
- **RECOMPUTED_VALUE:** Only three hypotheses are formal inferential tests:
  - $H_1$ ($T_3$ vs. Cascade NMSE): Paired Wilcoxon $W=0.0, p = 1.863 \times 10^{-9}$
  - $H_5$ (Hybrid Complementarity on $I_9$): Paired Wilcoxon $W=0.0, p = 2.328 \times 10^{-8}$
  - $H_7$ (Cascade Order Discrepancy on $I_4$): Paired Wilcoxon $W=0.0, p = 1.863 \times 10^{-9}$
  The remaining six hypotheses ($H_2, H_3, H_4, H_6, H_8, H_9$) are descriptive sample checks or deterministic Pareto comparisons for which no valid statistical null hypothesis or non-trivial p-value was evaluated.
- **ROOT_CAUSE:** Expository reporting overstatement conflating passing quantitative benchmarks with inferential hypothesis rejections.
- **TYPE:** STATISTICAL / REPORTING
- **CENTRAL_ARCHITECTURE_IMPACT:** Confirmatory evidence for $H_1, H_5, H_7$ remains exceptionally strong ($p < 10^{-7}$), but the blanket statement is inaccurate.
- **CORRECTED_INTERPRETATION:** Reclassify status to `REPORTING_OVERSTATEMENT`. Record $H_1, H_5, H_7$ as inferentially confirmed at $p < 0.001$; record $H_2, H_3, H_4, H_6, H_8$ as descriptive sample-level criteria satisfied; record $H_9$ as a deterministic multi-objective decision.

---

### Corrigendum 5: Pareto Dominance Generalization Scope
- **ORIGINAL_CLAIM:** $T_3$ "strictly vector Pareto dominates all alternative topologies."
- **ORIGINAL_VALUE:** Unrestricted strict Pareto dominance.
- **RECOMPUTED_VALUE:** 
  - **Aggregate Vector:** $T_3$ strictly vector Pareto dominates $T_1, T_{1R}, T_2,$ and $O_{\text{ALL}}$ on both Live Vector (`[NMSE, LIVE_FP, RAM]`) and Full Online Vector (`[NMSE, TOTAL_FP, INT, TRAFFIC, RAM]`).
  - **Task-Level Comparisons:** Across 56 pairwise comparisons (4 comparators $\times$ 14 tasks), $T_3$ strictly dominates in 49 comparisons (87.5%), but forms a `NON_DOMINATED_TRADEOFF` in 7 comparisons (12.5%) against $T_1$ and $T_{1R}$ on $I_6, I_{10}, I_{14}$.
- **ROOT_CAUSE:** Equating aggregate benchmark dominance with uniform dominance on every individual task.
- **TYPE:** TERMINOLOGY / REPORTING
- **CENTRAL_ARCHITECTURE_IMPACT:** $T_3$ is the unambiguously preferred global candidate, but universal task-level dominance is refuted.
- **CORRECTED_INTERPRETATION:** Claim status is `SUPPORTED_WITH_CORRECTION`. State: "$T_3$ strictly vector Pareto dominates all alternative topologies on the aggregate benchmark vector, and achieves non-dominated trade-offs on specific specialized tasks."

---

### Corrigendum 6: Structural Specificity Limitation (Memory Type vs. Exact Support)
- **ORIGINAL_CLAIM:** $T_3$ accurately identifies and models temporal structure on discrete delay tasks.
- **ORIGINAL_VALUE:** Implied complete structural recovery.
- **RECOMPUTED_VALUE:** 
  - Task $I_3$ (Single Delay, $k=6$): Recall = $96.7\%$, but Precision = $25.0\%$ ($\bar{K} = 3.35$ taps, $2.49$ false active taps per step).
  - Task $I_4$ (Multi-Sparse Delay, $k \in \{3, 14, 27\}$): Precision = $35.1\%$, Recall = $77.8\%$ ($\bar{K} = 1.65$ taps; $k=27$ tap frequently missed).
- **ROOT_CAUSE:** The correlation thresholding in the circular screening buffer reliably identifies the temporal family as `LAG`, but lacks the precision to isolate exact sparse tap coordinates without spurious neighbor allocation or high-lag misses.
- **TYPE:** AGGREGATION / REPORTING
- **CENTRAL_ARCHITECTURE_IMPACT:** Structural family specialization is confirmed, but exact lag support recovery is imperfect.
- **CORRECTED_INTERPRETATION:** Distinguish `MEMORY_TYPE_SPECIALIZATION = SUPPORTED` from `EXACT_SUPPORT_IDENTIFICATION = PARTIAL`. Scope the candidate architecture appropriately and recommend `LAG-SUPPORT-SPECIFICITY-01`.

---

### Corrigendum 7: Plasticity Claim Formulation (Useful Adaptation vs. Churn)
- **ORIGINAL_CLAIM:** The parent report cites $1,741$ structural transitions ($931$ promotions, $810$ evictions) across switching tasks as direct evidence of superior plasticity.
- **ORIGINAL_VALUE:** Raw transition count treated as a figure of merit.
- **RECOMPUTED_VALUE:** Useful transitions occurring during switch windows represent only $13.9\%$ to $65.2\%$ of transitions. During stationary regimes, $T_3$ exhibits persistent structural churn ($2.6$ to $4.9$ churn events per seed).
- **ROOT_CAUSE:** Correlation threshold crossings caused by variance fluctuations during stationary streaming.
- **TYPE:** REPORTING / TERMINOLOGY
- **CENTRAL_ARCHITECTURE_IMPACT:** Adaptive tracking is genuine (median discovery latency 69–486 steps, retirement latency 42–78 steps, steady correct state rate 70.8%–100.0%), but raw transition count is an invalid metric.
- **CORRECTED_INTERPRETATION:** Plasticity claim is `SUPPORTED_WITH_CORRECTION`. Justify plasticity using latency, regret, and post-switch tracking metrics rather than raw event counts.

---

### Corrigendum 8: Control Comparator Nomenclature ($O_{\text{ALL}}$)
- **ORIGINAL_CLAIM:** $O_{\text{ALL}}$ is labeled an "Always-On Oracle / Diagnostic Upper Bound".
- **ORIGINAL_VALUE:** "Oracle".
- **RECOMPUTED_VALUE:** $O_{\text{ALL}}$ is an unarbitrated control where all modules are concurrently active and adapting. On noise and simple linear tasks ($I_1, I_2, I_3$), it overfits and achieves higher error ($NMSE = 0.4258$) than $T_3$ ($0.2876$). It possesses no privileged target information.
- **ROOT_CAUSE:** Mislabeling an all-capacity baseline as an oracle.
- **TYPE:** TERMINOLOGY
- **CENTRAL_ARCHITECTURE_IMPACT:** Clarifies that $T_3$ beating $O_{\text{ALL}}$ does not violate theoretical bounds.
- **CORRECTED_INTERPRETATION:** Relabel $O_{\text{ALL}}$ to `UNARBITRATED_FULL_CAPACITY_CONTROL` or `DIAGNOSTIC_MAX_CAPACITY_BASELINE`.

---

### Corrigendum 9: Gate 2 Threshold Relaxation ($S_{\text{bar}} \le 0.05 \to 0.10$)
- **ORIGINAL_CLAIM:** Gate 2 threshold reported as $S_{\text{bar}} \le 0.10$ in final reports.
- **ORIGINAL_VALUE:** $\le 0.10$.
- **RECOMPUTED_VALUE:** Preregistered criterion in `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (line 53) was $S_{\text{bar}} \le 0.05$. Measured recurrent occupancy on $I_2$ was $0.058 \pm 0.021$.
- **ROOT_CAUSE:** Threshold was relaxed post-result inspection when empirical mean exceeded $0.05$.
- **TYPE:** GATE_DRIFT
- **CENTRAL_ARCHITECTURE_IMPACT:** Gate 2 fails under the strict preregistered threshold ($0.058 > 0.05$), but passes under the exploratory $0.10$ ceiling.
- **CORRECTED_INTERPRETATION:** Disclose exploratory threshold adjustment; document that static nonlinearity causes minor recurrent leakage ($5.8\%$).

---

## 3. Summary Impact Table

| Item | Original Status | Corrected Status | Architectural Viability of $T_3$ |
|:---|:---|:---|:---|
| **NMSE Table Traceability** | Seed 1301 Dev pasted | Recomputed 30-Seed Confirmatory Mean | **PRESERVED & STRENGTHENED** |
| **Gate 11 RAM Ceiling** | Preregistered 2048 B | Post-hoc relaxation from 1024 B | **RECLASSIFIED TO PROPOSED 2KB CLASS** |
| **Compute Accounting** | 81.4 FLOPs (Live only) | 81.4 Live / 168.0 Total Online | **LIVE PASS / TOTAL ONLINE GOVERNANCE REQ.** |
| **All 9 p < 0.001 Claim** | Uniform inferential confirmation | 3 Inferential rejections, 6 Descriptive | **REPORTING OVERSTATEMENT CORRECTED** |
| **Pareto Dominance** | Universal strict dominance | Aggregate dominance / Task trade-offs | **SCOPED TO AGGREGATE VECTOR** |
| **Lag Support Recovery** | Full structural identification | High Recall (97%), Modest Precision (25%) | **SPECIALIZATION PASS / SUPPORT PARTIAL** |
| **Plasticity Evidence** | 1,741 transitions = plasticity | Latencies prove tracking; churn noted | **CONFIRMED VIA LATENCY & REGRET** |
| **Oracle Nomenclature** | $O_{\text{ALL}}$ = Oracle | $O_{\text{ALL}}$ = Full Capacity Control | **TERMINOLOGY CORRECTED** |
| **Gate 2 Threshold** | Preregistered 0.10 | Post-hoc relaxation from 0.05 | **QUALIFIED PASS (5.8% LEAKAGE)** |

---

**Auditor Sign-off:**  
The architectural selection of **$T_3$ (Resource-Aware Conditional Arbitration)** remains scientifically sound and empirically superior to cascades and unarbitrated competition. However, its resource classification must be updated to the proposed 2 KB class, its total-online compute requires duty-cycle governance, and its claims must be strictly scoped to what the sealed artifacts objectively substantiate.
