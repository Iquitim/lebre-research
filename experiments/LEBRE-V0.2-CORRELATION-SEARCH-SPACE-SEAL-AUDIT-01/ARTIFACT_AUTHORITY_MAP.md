# Artifact Authority Map & Epistemic Hierarchy

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Seal Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. The Epistemic Authority Hierarchy

In resolving any discrepancy, contradiction, or numerical divergence encountered during this forensic audit, the following strict authority hierarchy governs:

```text
LEVEL 1: RAW FINAL / DEV CSV AND JSON ARTIFACTS
    >
LEVEL 2: EXACT EXECUTABLE RUNNER / ANALYSIS CODE
    >
LEVEL 3: FROZEN PREREGISTRATION
    >
LEVEL 4: FROZEN PROTOCOL AND CANDIDATE SPECIFICATION
    >
LEVEL 5: MANIFESTS / CANDIDATE FREEZE DOCUMENTS
    >
LEVEL 6: GENERATED SUMMARIES / AGGREGATION CSVS
    >
LEVEL 7: NARRATIVE FINAL REPORTS
    >
LEVEL 8: AUDIT INSTRUCTION PROMPT
    >
LEVEL 9: AUDITOR ASSUMPTIONS
```

### Governing Rules of Resolution:
1. **No Silent Overrides:** A lower-level artifact cannot silently override a higher-level artifact.
2. **Raw Ground Truth (Level 1):** The step-level and run-level logs (`CORRELATION_SEARCH_FINAL_RESULTS.csv`, `SPARSE_FRONTIER_DEV_RESULTS.csv`) constitute the primary physical ground truth of executed compute, error, and memory events.
3. **Executable Implementation (Level 2):** In case of ambiguity in metric definitions, the exact mathematical operations executed in Python source code (`scratch/run_v02_correlation_search_compaction.py`) supersede descriptive prose.
4. **Governance Invariants (Level 3 & 4):** Pre-declared statistical thresholds, non-inferiority margins, and success criteria in `CORRELATION_SEARCH_PREREGISTRATION.md` cannot be post-hoc adjusted by narrative summaries.

---

## 2. Parent Artifact Inventory and Authority Mapping

| Authority Level | Artifact Filename | Canonical Role | Governing Scope |
| :--- | :--- | :--- | :--- |
| **Level 1** | `CORRELATION_SEARCH_FINAL_RESULTS.csv` | Confirmatory Raw Data | 1,260 runs ($N=30$ seeds $\times$ 14 tasks $\times$ 3 models) |
| **Level 1** | `SPARSE_FRONTIER_DEV_RESULTS.csv` | DEV Screening Raw Data | 560 candidate screening runs |
| **Level 1** | `HIERARCHICAL_SEARCH_DEV_RESULTS.csv`| DEV Negative Control | 140 hierarchical search runs |
| **Level 1** | `DENSE_CELL_PROVENANCE.csv` | Phase 0 Grid Utilization | 160 cells audited across 140 DEV streams |
| **Level 1** | `LAG_SCORE_LOCALITY_AUDIT.csv` | Phase 1 Locality Audit | 4,915 active delay instances audited |
| **Level 2** | `scratch/run_v02_correlation_search_compaction.py` | Model Implementations | Algorithmic state updates, FLOP pricing, queues |
| **Level 2** | `scratch/run_phase0_phase1_audit.py` | Phase 0/1 Runner | Locality and cell provenance computation |
| **Level 2** | `scratch/run_phase2_dev_screening.py` | Phase 2 DEV Runner | DEV candidate comparison runner |
| **Level 2** | `scratch/run_phase3_confirmatory.py` | Phase 3 Confirmatory Runner | Confirmatory execution and raw output generator |
| **Level 2** | `scratch/postprocess_confirmatory_results.py` | Statistical Processing | Summary generation and statistical testing |
| **Level 3** | `CORRELATION_SEARCH_PREREGISTRATION.md` | Sealed Preregistration | Hypotheses H1..H7, margins, decision logic |
| **Level 4** | `CORRELATION_SEARCH_PROTOCOL.md` | Sealed Experimental Protocol| 4-phase execution rules, diagnostic gates |
| **Level 4** | `SPARSE_FRONTIER_SPEC.md` | Candidate Architecture Spec | State tables, circular queue, promotion rules |
| **Level 4** | `HIERARCHICAL_SEARCH_SPEC.md` | Negative Architecture Spec | Subsampled grid, refinement window rules |
| **Level 4** | `SEARCH_SPACE_COMPUTE_MODEL.md` | Analytical Compute Ledger | FLOP formulas and clock rates |
| **Level 4** | `SEARCH_SPACE_MEMORY_MODEL.md` | Analytical Memory Ledger | RAM byte structures and zero-dense proofs |
| **Level 5** | `FINAL_SEARCH_CANDIDATE_FREEZE.md` | Candidate Selection Freeze | Freeze of $M_1^* = C_{1, H=32, B=4}$ and code hashes |
| **Level 5** | `CORRELATION_SEARCH_MANIFEST.json` | Parent Cryptographic Manifest| SHA-256 registry of 46 parent artifacts |
| **Level 6** | `SEARCH_FIDELITY_BY_SEED.csv` | Seed-Level Summary | 30 paired seed rows |
| **Level 6** | `PREDICTIVE_NONINFERIORITY.csv` | Inferential Test Output | One-sided t-tests against margin |
| **Level 6** | `PURE_LAG_PRESERVATION.csv` | Secondary Task Family | $I_3, I_4, I_5, I_8$ task-level comparisons |
| **Level 6** | `SWITCHING_PRESERVATION.csv` | Secondary Task Family | $I_{11..14}$ recovery latencies |
| **Level 6** | `SEARCH_RESOURCE_BY_SEED.csv` | Resource Accounting Summary| Per-seed compute and memory comparisons |
| **Level 6** | `SEARCH_POLICY_DEV_COMPARISON.csv` | DEV Comparison Summary | 7-candidate DEV screening summary |
| **Level 7** | `CORRELATION_SEARCH_FINAL_REPORT.md` | Narrative Final Report | Comprehensive answers to 25 questions |
| **Level 7** | `CORRELATION_SEARCH_RESOURCE_REPORT.md`| Narrative Resource Report | Disaggregated compute and memory analysis |
| **Level 7** | `CORRELATION_SEARCH_DECISION.md` | Governance Decision Document| Final seal adjudication statement |
