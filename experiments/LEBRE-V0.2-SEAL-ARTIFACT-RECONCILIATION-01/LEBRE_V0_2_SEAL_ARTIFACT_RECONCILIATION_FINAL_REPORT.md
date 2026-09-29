# LEBRE v0.2 Seal Artifact Reconciliation Final Report

**Audit Identifier:** `LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`  
**Title:** Executable Artifact Reconciliation, H7 Data-Lineage Repair & Gate-6 Governance Correction  
**Parent Studies:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`, `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`, `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Auditor:** Independent Scientific-Software Auditor  
**Date:** September 2026  
**Status:** Sealed Reconciliation Final Report  

---

## 1. Executive Summary

This small executable reconciliation audit was conducted to resolve two specific issues identified in the LEBRE v0.2 integration record:
1. **Issue A (H7 Generated-Artifact Reproducibility):** Investigating why the intermediate artifacts generated in the prior errata study (`H7_PAIRED_RAW_VALUES.csv` and `H7_TASK_SUMMARY.csv`) recorded identically `0.0` paired deltas while the narrative and statistical scripts reported non-zero differences; and
2. **Issue B (Gate 6 Preregistered Governance Compliance):** Recovering the exact frozen preregistered definition of Gate 6 ($\rho_{\text{dual}} \le 0.05$ on $I_{10}$), evaluating confirmatory data strictly against this criterion without metric substitution, and formally classifying Gate 6 compliance.

### Definitive Reconciliation Determinations
- **H7 Extraction Bug Confirmed & Repaired:** In `scratch/generate_errata_outputs.py` (line 80), a typographical extraction bug (`nmse_t1r = sub_t1["nmse"].values` instead of `sub_t1r`) caused intermediate CSVs to record identical arrays for $T_1$ and $T_{1R}$. Anti-copy assertions now enforce that source dataframe indices are disjoint and values are extracted from distinct topological records. The reconciled intermediate datasets (`H7_PAIRED_RAW_VALUES_RECONCILED.csv`, `H7_TASK_SUMMARY_RECONCILED.csv`, `H7_WILCOXON_BY_TASK_RECONCILED.csv`) strictly reproduce the raw confirmatory data.
- **Task $I_4$ Status Settled:** On Task $I_4$, $T_1$ (0.688922) and $T_{1R}$ (0.688150) are statistically indistinguishable ($\text{diff of means} = 0.000772, W = 225.0, \mathbf{p = 0.8872}$). The narrative claim of $p = 1.86 \times 10^{-9}$ was a transcription error from the $T_3$ vs. $T_1$ comparison. Across the 14 tasks under Holm-Bonferroni correction, zero tasks achieve statistical significance. Cascade order sensitivity is a descriptive property on specific tasks ($I_8, I_3$), not an inferential confirmatory rejection (`H7_STATUS = DESCRIPTIVE_ONLY`).
- **Gate 6 Literal Evaluation: FAIL:** The frozen preregistration defines $\rho_{\text{dual, I10}}$ as the fraction of steady-state evaluation steps ($t \ge 1000$) where BOTH memory classes are active (`frac_both`), bounded at $\le 0.05$. On the 30 confirmatory seeds, $T_3$ exhibits mean `frac_both` of **$0.108467$** ($10.85\%$), with 22 of 30 seeds exceeding $0.05$. Substituting `redundant_dual_rate` ($0.0000$) is rejected as an unpreregistered post-hoc metric change. Gate 6 is formally classified as **`GATE_6_PREREGISTERED_STATUS = FAIL`**.
- **$T_3$ Arbitration Effectiveness: SUPPORTED:** Factual algorithmic effectiveness is decoupled from the rigid 5% ceiling. In unarbitrated symmetric competition ($T_2$), dual occupancy is $100.0\%$ (mean live FLOPs = $118.8$). $T_3$ suppresses steady-state dual occupancy down to $10.85\%$ (an $89.2\%$ reduction), cuts live evaluation compute by $22.2\%$ ($92.4$ FLOPs), improves predictive NMSE from $0.4940$ to $0.4173$, and eliminates useless co-allocation ($0.0000$ redundant dual rate). Thus, **`T3_I10_ARBITRATION_EFFECTIVENESS = SUPPORTED`**.
- **Architectural Candidate Status Preserved:** All settled architectural findings ($T_3$ benchmark NMSE victory, internal evaluation-order invariance, hybrid complementarity on $I_9$, aggregate vector Pareto dominance) remain fully intact.

---

## 2. Issue A: Forensic Reconciliation of H7 Artifact Chain

### 2.1 Extraction Bug Identification & Anti-Copy Safeguards
In the prior errata script (`scratch/generate_errata_outputs.py`), line 80 contained:
```python
nmse_t1 = sub_t1["nmse"].values
nmse_t1r = sub_t1["nmse"].values  # BUG: Assigned from sub_t1 instead of sub_t1r!
```
This line inadvertently cloned the $T_1$ array into $T_{1R}$, producing zeros in `H7_PAIRED_RAW_VALUES.csv`.

In `generate_reconciliation_outputs.py`, the following four anti-copy assertions are enforced prior to any calculation:
1. `assert (sub_t1["topology"] == "T1").all()` and `assert (sub_t1r["topology"] == "T1R").all()`;
2. `assert len(sub_t1) == 30` and `assert len(sub_t1r) == 30`;
3. `assert len(set(sub_t1.index).intersection(set(sub_t1r.index))) == 0` (strictly disjoint dataframe row indices);
4. Anti-copy verification: If `np.array_equal(nmse_t1, nmse_t1r)`, inspect source rows to classify `GENUINELY_IDENTICAL_RAW_VALUES` vs. `EXTRACTION_BUG`.

### 2.2 Reconciled Task-by-Task Statistics
Recomputed values from `H7_TASK_SUMMARY_RECONCILED.csv` and `H7_WILCOXON_BY_TASK_RECONCILED.csv` ($N=30$ confirmatory seeds):

| Task ID | Task Description | Mean $T_1$ | Mean $T_{1R}$ | Mean $|T_1 - T_{1R}|$ | Wilcoxon $W$ | Raw $p$-value | Holm $\alpha$ | Holm Sig? |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$I_1$** | Memoryless Linear | $0.119971$ | $0.120088$ | $0.000121$ | $1.0$ | $0.004439$ | $0.003571$ | **No** |
| **$I_2$** | Static Nonlinear Control | $1.297740$ | $1.292256$ | $0.017308$ | $167.0$ | $0.183969$ | $0.006250$ | **No** |
| **$I_3$** | Single Exact Delay | $0.368426$ | $0.295007$ | $0.158641$ | $155.0$ | $0.114177$ | $0.004167$ | **No** |
| **$I_4$** | Multi-Sparse Delay | $0.688922$ | $0.688150$ | $0.047750$ | $225.0$ | **$0.887195$** | $0.050000$ | **No** |
| **$I_5$** | Moving Delay Support | $0.459651$ | $0.439447$ | $0.058516$ | $182.0$ | $0.308521$ | $0.008333$ | **No** |
| **$I_6$** | Continuous Latent State | $0.107166$ | $0.106703$ | $0.001285$ | $189.0$ | $0.381798$ | $0.012500$ | **No** |
| **$I_7$** | Quiescent Continuous State | $0.147475$ | $0.145727$ | $0.003874$ | $174.0$ | $0.236652$ | $0.007143$ | **No** |
| **$I_8$** | Quiescent Discrete Delay | $0.386497$ | $0.293291$ | **$0.165426$** | $158.0$ | $0.129353$ | $0.004545$ | **No** |
| **$I_9$** | Hybrid Delay + Latent | $0.289364$ | $0.280909$ | $0.042289$ | $207.0$ | $0.612006$ | $0.025000$ | **No** |
| **$I_{10}$**| Redundant Temporal Structure | $0.257398$ | $0.259028$ | $0.005171$ | $189.0$ | $0.381798$ | $0.010000$ | **No** |
| **$I_{11}$**| Regime Switch (Delay $\to$ Latent) | $0.189212$ | $0.164571$ | $0.033932$ | $104.0$ | $0.007111$ | $0.003846$ | **No** |
| **$I_{12}$**| Regime Switch (Latent $\to$ Delay) | $0.327351$ | $0.326215$ | $0.002973$ | $165.0$ | $0.170598$ | $0.005556$ | **No** |
| **$I_{13}$**| Regime Switch (Hybrid $\to$ Memless) | $0.215726$ | $0.211776$ | $0.022279$ | $190.0$ | $0.393050$ | $0.016667$ | **No** |
| **$I_{14}$**| Intermittent Hybrid | $0.173439$ | $0.161524$ | $0.031691$ | $163.0$ | $0.157948$ | $0.005000$ | **No** |

### 2.3 Scientific Conclusions on H7
1. Reversing cascade order does not yield a statistically significant difference on Task $I_4$ ($p = 0.8872$).
2. The benchmark maximum discrepancy occurs on Task $I_8$ ($0.165426$), but fails family-wise significance ($p = 0.1294$).
3. Zero of 14 tasks survive Holm-Bonferroni correction. Cascade order sensitivity is a descriptive stochastic phenomenon on specific delay streams.
4. $T_3$ evaluation-order invariance remains **VERIFIED** by independent analytical commutativity and deterministic permutation microtests.

---

## 3. Issue B: Gate 6 Preregistered Governance Recovery & Recomputation

### 3.1 Preregistered Specification
From `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (line 61) and `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (lines 68–71):
- **Target Task:** $I_{10}$ (`I10_Redundant_Temporal_Structure`)
- **Metric:** $\rho_{\text{dual, I10}} \equiv \text{frac\_both}$ ($t \ge 1000$)
- **Threshold:** $\le 0.05$ ($5.0\%$ of evaluation steps)

### 3.2 Confirmatory Recomputation on Task $I_{10}$
From `GATE6_BY_SEED.csv` ($N=30$ seeds):
- **$T_3$ Mean `frac_both`:** **$0.108467$** ($10.85\%$)
- **$T_3$ Median `frac_both`:** **$0.079300$** ($7.93\%$)
- **$T_3$ 95% Bootstrap CI:** $[0.0764, 0.1463]$
- **$T_3$ Max `frac_both`:** $0.500200$ ($50.02\%$)
- **$T_3$ Seeds Exceeding $0.05$:** **$22 / 30$** ($73.3\%$)
- **$T_2$ Mean `frac_both`:** **$1.000000$** ($100.0\%$)

### 3.3 Governance Verdict
$$\text{Observed Mean } (0.108467) > \text{Preregistered Threshold } (0.05) \implies \mathbf{GATE\_6\_PREREGISTERED\_STATUS = FAIL}$$

### 3.4 Decoupled Arbitration Effectiveness
While failing the literal 5% gate, $T_3$'s conditional arbitration is demonstrably effective:
- Unarbitrated $T_2$ maintains both modules continuously ($100.0\%$ of evaluation steps), burning $118.8$ live FLOPs with $NMSE = 0.4940$.
- Arbitrated $T_3$ suppresses dual occupancy down to $10.85\%$ (an $89.2\%$ reduction), burns $92.4$ live FLOPs ($-22.2\%$ savings), and achieves superior accuracy ($NMSE = 0.4173$).
- Redundant dual allocation under secondary gain thresholding is $0.0000$.

$$\mathbf{T3\_I10\_ARBITRATION\_EFFECTIVENESS = SUPPORTED}$$

---

## 4. Preservation of Settled Findings

All other architectural and resource findings are carried forward unchanged:
- **T3 Architectural Selection:** `SUPPORTED_WITH_SCOPE_LIMITS`.
- **Gate 11 Legacy Memory:** `FAIL` under 1024B ceiling ($1306$ B), passes proposed 2048B ceiling.
- **Legacy Total-Online Compute:** `FAIL` ($108.2$ aggregate, $168.0$ peak).
- **Exact Lag-Support Identification on $I_3/I_4$:** `PARTIAL`.
- **T3 Aggregate Pareto Dominance:** Confirmed on benchmark aggregate; non-dominated on 12.5% of task pairs.
- **T3 Internal Evaluation-Order Invariance:** `VERIFIED`.
- **Milestone M3:** `UNOPENED`.

---

## 5. Final Machine-Readable Governance Seal Block

==================================================
LEBRE_V0_2_SEAL_ARTIFACT_RECONCILIATION_01_STATUS =
COMPLETE

PRIMARY_OUTCOME =
CLEAN_RECONCILIATION

CANONICAL_SRC_CHANGED =
NO

CANONICAL_TESTS_CHANGED =
NO

M3_STATUS =
UNOPENED

NOVELTY_CLAIM_READY =
NO

CONFIRMATORY_SEEDS =
1311..1340

DEV_SEEDS_QUARANTINED =
YES

H7_RAW_PAIR_EXTRACTION_VERIFIED =
YES

H7_OLD_ARTIFACT_GENERATION_BUG =
YES

H7_I4_T1_MEAN =
0.688922

H7_I4_T1R_MEAN =
0.688150

H7_I4_DIFF_OF_MEANS =
0.000772

H7_I4_WILCOXON_P =
0.887195

H7_STATUS =
DESCRIPTIVE_ONLY

T3_INTERNAL_ORDER_INVARIANCE =
VERIFIED

GATE6_PREREGISTERED_METRIC =
frac_both

GATE6_PREREGISTERED_THRESHOLD =
0.05

T3_I10_FRAC_BOTH_MEAN =
0.108467

T3_I10_FRAC_BOTH_MEDIAN =
0.079300

T3_I10_FRAC_BOTH_MAX =
0.500200

T3_I10_SEEDS_EXCEEDING_GATE =
22/30

GATE6_PREREGISTERED_STATUS =
FAIL

T3_I10_ARBITRATION_EFFECTIVENESS =
SUPPORTED

REDUNDANT_DUAL_RATE_USED_FOR_GATE6 =
NO

T3_ARCHITECTURAL_SELECTION =
SUPPORTED_WITH_SCOPE_LIMITS

T3_CANDIDATE_STATUS =
EXPERIMENTAL_NON_CANONICAL

LEGACY_R2_MEMORY_STATUS =
FAIL

LEGACY_R2_TOTAL_ONLINE_COMPUTE_STATUS =
FAIL

ARTIFACT_CHAIN_RECONCILED =
YES

SEAL_READY =
YES

SAFE_FOR_RESOURCE_COMPACTION =
YES

SAFE_FOR_INTEGRATED_VALIDATION =
NO

SAFE_TO_OPEN_M3 =
NO

NEXT_RECOMMENDED_STAGE =
LEBRE-V0.2-RESOURCE-COMPACTION-01

LEBRE_V0_1_STATUS =
FROZEN_WITH_SCOPE_LIMITS
==================================================
