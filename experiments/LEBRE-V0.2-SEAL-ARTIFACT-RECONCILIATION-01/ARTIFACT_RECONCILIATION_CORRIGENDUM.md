# LEBRE v0.2 Artifact Reconciliation Corrigendum

**Document Identifier:** `ARTIFACT_RECONCILIATION_CORRIGENDUM.md`  
**Audit Context:** `LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`  
**Auditor:** Independent Scientific-Software Auditor  
**Date:** September 2026  
**Status:** Sealed Corrigendum  

---

## 1. Itemized Reconciliation Table

This corrigendum provides an itemized record of all discrepancies between prior intermediate artifacts, narrative summaries, and the reconciled Level 1 raw confirmatory dataset:

| Ref ID | Target Area | Previous / Faulty Record | Reconciled Level 1 Record | Root Cause Analysis | Corrected Scientific Status |
|:---|:---|:---|:---|:---|:---|
| **CORR-01** | H7 Intermediate Datasets | Delata values identically `0.0` across all 14 tasks in `H7_PAIRED_RAW_VALUES.csv` & `H7_TASK_SUMMARY.csv` | Non-zero paired deltas on all 14 tasks (e.g. $I_8 = 0.1654, I_3 = 0.1586, I_4 = 0.0478$) | **EXTRACTION BUG:** In `scratch/generate_errata_outputs.py` (line 80), code assigned `nmse_t1r = sub_t1["nmse"].values` instead of `sub_t1r`. Corrected in `generate_reconciliation_outputs.py`. | **REPAIRED:** Reconciled artifacts regenerated with anti-copy assertions. |
| **CORR-02** | Gate 6 Evaluation Metric | Prior reports referenced `redundant_dual_rate = 0.0000` to suggest Gate 6 passed | Preregistered metric is `frac_both` ($\rho_{\text{dual}} = 0.108467 \pm 0.0821$) | **METRIC SUBSTITUTION:** Protocol line 61 explicitly defines $\rho_{\text{dual}}$ as the fraction of evaluation steps in BOTH state, which is `frac_both`. Secondary gain thresholding was unpreregistered. | **RECLASSIFIED:** Gate 6 evaluates strictly against `frac_both`. |
| **CORR-03** | Gate 6 Governance Decision | Informally claimed as passing or ambiguous | $\overline{\text{frac\_both}} = 0.108467 > 0.05$; $22/30$ seeds violate ceiling | **LITERAL GOVERNANCE VIOLATION:** Mean dual occupancy exceeds the 5% threshold by a factor of 2.17. | **CLASSIFIED AS FAIL:** `GATE_6_PREREGISTERED_STATUS = FAIL`. |
| **CORR-04** | $T_3$ Arbitration Effectiveness | Conflated with Gate 6 compliance | $T_3$ reduces steady-state dual occupancy from 100.0% ($T_2$) to 10.85% | **DECOUPLING REQUIRED:** Factual algorithmic effectiveness is distinct from meeting a rigid preregistered ceiling. | **VINDICATED:** `T3_I10_ARBITRATION_EFFECTIVENESS = SUPPORTED`. |
| **CORR-05** | Task $I_4$ H7 Narrative Statistics | Previously reported as $|T_1 - T_{1R}| = 0.1654$ with $p = 1.86 \times 10^{-9}$ | $\text{Mean } T_1 = 0.6889, \text{Mean } T_{1R} = 0.6882$, diff = $0.000772$, $W=225.0, p=0.8872$ | **CONFLATION & TRANSCRIPTION ERROR:** Narrative conflated the benchmark maximum on $I_8$ ($0.1654$) with DEV paste and transposed p-value from $T_3$ vs. $T_1$. | **CONFIRMED DESCRIPTIVE ONLY:** Reversal of cascade produces negligible difference on $I_4$. |

---

## 2. Corrected Narrative Claim Wording

### Corrected Gate 6 Claim
> **Original / Ambiguous Claim:**  
> *"Topology T3 passes Gate 6 by eliminating redundant dual allocation on task I10 (redundant dual rate = 0.0%)."*  
>  
> **Corrected Authoritative Claim:**  
> *"Topology T3 fails the rigid preregistered Gate 6 ceiling ($\rho_{\text{dual}} \le 0.05$), exhibiting a steady-state dual occupancy rate of $10.85\% \pm 8.21\%$ with 22 of 30 seeds exceeding 5% (`GATE_6_PREREGISTERED_STATUS = FAIL`). However, conditional arbitration is algorithmically effective, suppressing dual occupancy by 89.2% relative to unarbitrated symmetric competition ($T_2$, 100.0%), cutting live evaluation compute by 22.2%, and reducing thresholded redundant allocation to 0.0% (`T3_I10_ARBITRATION_EFFECTIVENESS = SUPPORTED`)."*

### Corrected H7 Order Sensitivity Claim
> **Original / Bugged Record:**  
> *"Intermediate CSVs show 0.0 difference between T1 and T1R on all tasks."*  
>  
> **Corrected Authoritative Record:**  
> *"The appearance of 0.0 differences in `H7_PAIRED_RAW_VALUES.csv` was an extraction script defect (`nmse_t1r = sub_t1[...]`). Reconciled extraction confirms genuine non-zero differences across all 14 tasks. On Task $I_4$, $T_1$ (0.6889) and $T_{1R}$ (0.6882) are statistically indistinguishable (diff = 0.000772, $W=225.0, p=0.8872$). The maximum task discrepancy is 0.1654 on Task $I_8$, but zero tasks survive Holm-Bonferroni multiplicity control. Cascade order sensitivity is a descriptive property on specific tasks, not an inferential confirmatory rejection (`H7_STATUS = DESCRIPTIVE_ONLY`)."*
