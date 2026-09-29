# LEBRE v0.2 Integration Forensic Seal Audit Protocol

**Study Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Audited Directory:** `experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/`  
**Auditor:** Independent Skeptical Senior Reviewer  
**Audit Pipeline:** `PRESERVE -> REPRODUCE -> TRACE -> CLASSIFY -> CORRECT REPORTING -> RE-EVALUATE DECISION`  

---

## 1. Audit Scope & Mandate

This protocol establishes the immutable verification plan for auditing `LEBRE-V0.2-INTEGRATION-DESIGN-01`.
The auditor is charged with assessing whether the evidence supporting `T3_RESOURCE_AWARE_CONDITIONAL_ARBITRATION` is internally consistent, reproducible from sealed artifacts, traceable to preregistered resource governance, and methodologically sound.

### Hard Constraints:
1. **Zero Model Tuning:** The auditor shall not adjust thresholds, modify learning rates, alter arbitration rules, or tweak benchmark generators to force compliance.
2. **Canonical Code Immutability:** `src/` and `tests/` remain 100% bitwise immutable.
3. **Artifact Integrity:** Parent artifacts in `experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/` are read-only and preserved by SHA256 hashes in `LEBRE_V0_2_PARENT_ARTIFACT_HASHES.txt`. All audit scripts, tables, and reports are written strictly into `experiments/LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01/`.
4. **Governance Preservation:** `M3_STATUS = UNOPENED`, `NOVELTY_CLAIM_READY = NO`, `LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`.

---

## 2. The 8 Motivating Audit Questions

- **Question A (Artifact Traceability):** Exact cell-by-cell recomputation of every table in the final and statistical reports from raw CSVs.
- **Question B (Resource-Gate Provenance):** Full timeline analysis of when, where, why, and before/after inspection the memory ceiling was stated as 1024 B vs. 2048 B.
- **Question C (Live vs. Shadow Compute):** Forensic analysis of whether historical `R2_FP <= 100` was intended to bound live-path, total online, or steady-state compute.
- **Question D (Per-Regime Resource Compliance):** Analysis of T3 resource usage across every benchmark task, during BOTH allocation, during structural search, and at P95/peak.
- **Question E (Pareto Claim Audit):** Mathematical verification of strict Pareto dominance vs. non-dominated trade-offs across both Live-Path and Full-Online objective vectors.
- **Question F (Statistical Claim Traceability):** Verification of the claim "all 9 hypotheses confirmed at p < 0.001", checking whether each hypothesis has an inferential test, independent seed data, and reproducible p-values.
- **Question G (Structural Correctness):** Distinction between memory family specialization (selecting LAG vs. RECURRENT) and exact internal support identification (recovering true lag coordinates).
- **Question H (Plasticity vs. Structural Churn):** Quantitative evaluation of whether 931 promotions and 810 evictions represent useful tracking or excessive structural instability.

---

## 3. Audit Execution Pipeline & Dependencies

```
[Sealed Raw Artifacts]
       │
       ├─► 1. Parent Hash Verification (LEBRE_V0_2_PARENT_ARTIFACT_HASHES.txt)
       ├─► 2. Protocol & Resource Gate Provenance (GATE_PROVENANCE_AUDIT.csv, RESOURCE_CEILING_PROVENANCE.md)
       ├─► 3. Compute Semantics Reconstruction (R2_COMPUTE_SEMANTICS_HISTORY.md)
       ├─► 4. Raw Recomputation & Cell Traceability (REPORT_CELL_TRACEABILITY.csv)
       ├─► 5. Resource Compliance Profiling (RESOURCE_COMPLIANCE_MATRIX.csv)
       ├─► 6. Statistical Lineage Audit (STATISTICAL_CLAIM_TRACEABILITY.csv)
       ├─► 7. Multi-Objective Pareto Verification (PARETO_OBJECTIVE_PROVENANCE.md, PARETO_RECOMPUTATION.csv)
       ├─► 8. Structural Support & Plasticity Audits (SUPPORT_RECOVERY_AUDIT.csv, REGIME_TRACKING_AUDIT.csv)
       ├─► 9. Audit Figures Generation (figures/F1..F12)
       ├─► 10. Formal Corrigendum (LEBRE_V0_2_SEAL_AUDIT_CORRIGENDUM.md)
       └─► 11. Final Audit Report & Seal Manifest (FINAL_REPORT.md, AUDIT_SEAL_MANIFEST.json)
```

---

## 4. Primary Audit Outcome Taxonomy

The audit will conclude with exactly one of the following primary classifications:
- `CLEAN_SEAL`: All tables reproduce; resource gates are preregistered and compliant; Pareto claims are strictly valid; conclusions hold without modification.
- `REPORTING_CORRIGENDUM_ONLY`: T3 selection remains supported, but tables, labels, p-values, or resource terminology require formal correction.
- `RESOURCE_GOVERNANCE_RECLASSIFICATION`: T3 architecture is supported, but it fails the historical 1KB resource class and requires an explicitly defined new resource envelope.
- `PARETO_CLAIM_DOWNGRADED`: T3 remains a strong candidate, but strict Pareto dominance is refuted under full-online compute metrics.
- `STRUCTURAL_SPECIFICITY_LIMITATION`: Memory-type arbitration works, but internal lag support exhibits significant over/under-allocation.
- `PLASTICITY_CLAIM_DOWNGRADED`: Promotion/eviction counts overstate useful regime adaptation.
- `MULTIPLE_CORRECTABLE_ISSUES`: Central architectural selection remains supported, but multiple reporting, governance, and Pareto claims require formal correction.
- `CENTRAL_SELECTION_REQUIRES_REEVALUATION`: Raw data fail to reproduce the central performance advantages of T3.
- `IMPLEMENTATION_ERROR_REQUIRES_RECONFIRMATION`: A code defect materially invalidates the comparison.

---

## 5. Decision Rules for Milestone Progression

1. **If T3 architecture is supported AND legacy 1KB / 100 FLOPs pass:**  
   `NEXT = LEBRE-V0.2-INTEGRATED-VALIDATION-01`.
2. **If T3 architecture is supported BUT memory exceeds 1024 B:**  
   `NEXT = LEBRE-V0.2-RESOURCE-COMPACTION-01` or `RESOURCE-GOVERNANCE-CLASS-01`.
3. **If T3 architecture is supported BUT total online compute exceeds 100 FLOPs:**  
   `NEXT = SHADOW-RENT-GOVERNANCE-01`.
4. **If exact lag support recovery exhibits low precision/recall:**  
   `NEXT = LAG-SUPPORT-SPECIFICITY-01`.
