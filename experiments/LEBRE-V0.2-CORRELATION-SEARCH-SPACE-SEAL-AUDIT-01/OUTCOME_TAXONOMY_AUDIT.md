# Outcome Taxonomy & Governance Reconciliation

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Outcome Taxonomy Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **AUDITED AND RECLASSIFIED**  

---

## 1. The Taxonomy Drift

In the parent study (`LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`), the final executive block emitted:
```text
PRIMARY_OUTCOME = COMPACTED_SPARSE_FRONTIER_SUPERIOR_TO_DENSE_MULTIRATE
FINAL_SEAL_VERDICT = CONDITIONALLY_SEALED_MULTIRATE_ENHANCEMENT
SEARCH_SPACE_COMPACTION_SUPPORTED = YES (WITHIN MULTIRATE REGIME)
```

### Forensic Audit of Preregistration Terms:
In `CORRELATION_SEARCH_PREREGISTRATION.md` (Section 1), the frozen primary hypothesis asserted:
> "A bounded rotating correlation-search frontier of capacity $H \in \{16, 32\}$ hypotheses ($< 20\%$ of the ambient $165$-cell grid) combined with a round-robin exploration queue $B \in \{2, 4\}$ achieves predictive non-inferiority relative to the canonical continuous reference $R_0$... while reducing mean total online compute below the project ceiling: $\bar{\mathcal{C}}_{\text{total}} \le 100.00\text{ FP/step}$."

The preregistration contained:
1. **NO "WITHIN MULTIRATE REGIME" Qualifier:** The primary inferential benchmark was continuous reference $R_0$.
2. **NO "SUPERIORITY TO DENSE MULTIRATE" Primary Outcome:** Superiority over $R_1$ was not formulated as a primary confirmatory gate.
3. **NO "CONDITIONALLY SEALED" Status:** A stage either passes all mandatory gates or fails global validation.
4. **Audit Finding:** The parent outcome labels represent **post-hoc taxonomy drift** (`OUTCOME_TAXONOMY_DRIFT` and `GOVERNANCE_OVERSTATEMENT`), softening a global gate failure into a conditional endorsement.

---

## 2. Reclassification Under Standard Taxonomy

Under Section 75 of the Audit Mandate, the governing outcome is:

```text
PRIMARY_OUTCOME = MULTIPLE_CORRECTABLE_ISSUES
```
with secondary diagnostic sub-verdicts:
- **`SPARSE_FRONTIER_FEASIBILITY`:** **`SUPPORTED`** (Frontier operates cleanly, saves $67.58\%$ RAM, zero dense arrays).
- **`ANTI_STARVATION`:** **`SUPPORTED`** (Strict $80$-step deterministic bound proven and verified).
- **`PREDICTIVE_IMPROVEMENT_VS_R1`:** **`SUPPORTED`** ($p = 0.0213$, 19 wins / 11 losses; corrected from reported $p = 4.2 \times 10^{-5}$).
- **`M1_VS_R1_STRICT_PARETO_DOMINANCE`:** **`NO`** (M1 improves NMSE and RAM, but total compute is higher: $111.01$ vs $106.74\text{ FP/step}$).
- **`PREDICTIVE_NONINFERIORITY_VS_R0`:** **`NOT_SUPPORTED`** ($\bar{\Delta} = +0.0130 > +0.0100$, Upper CI = $+0.0194$).
- **`TOTAL_COMPUTE_GATE`:** **`FAIL`** ($111.01 > 100.00\text{ FP/step}$).
- **`PURE_LAG_PRESERVATION`:** **`NOT_SUPPORTED`** (Fails on $I_3$ and $I_4$).
- **`SWITCHING_PRESERVATION`:** **`NOT_SUPPORTED`** (Fails on $I_{11}$ and $I_{12}$).
- **`CHURN_MECHANISM_REPLICATED`:** **`NO`** (DEV birth reduction was not present in FINAL).
- **`GLOBAL_SEARCH_COMPACTION_VALIDATION`:** **`FAILED`**.
- **`CORRELATION_SEARCH_SPACE_COMPACTION_SUPPORTED`:** **`NO`**.
