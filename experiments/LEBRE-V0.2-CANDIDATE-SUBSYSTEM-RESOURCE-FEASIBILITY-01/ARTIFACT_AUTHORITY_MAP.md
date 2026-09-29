# Artifact Authority Map: Candidate Subsystem Resource Feasibility
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Authority Mapping & Precedence Hierarchy

This document codifies the 9-level epistemic authority hierarchy governing data extraction, statistical reconciliation, and resource accounting for stage `LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01`.

---

## 1. Epistemic Precedence Hierarchy

```
Level 1: Raw Sealed CSV Data & Event Traces
         (CORRELATION_SEARCH_FINAL_RESULTS.csv, SEARCH_DESCENDANT_COST.csv, PROMOTION_POLICY_01_EVENTS.csv)
   >
Level 2: Executable Mathematical & Architectural Code
         (src/lebre/search/compact_frontier.py, src/lebre/subsystems/candidate_probation.py)
   >
Level 3: Sealed Forensic Audits & Binding Corrigenda
         (LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01, LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01)
   >
Level 4: Frozen Experimental Protocols
         (CANDIDATE_RESOURCE_FEASIBILITY_PROTOCOL.md)
   >
Level 5: Preregistration Specifications & Gate Criteria
         (CORRELATION_SEARCH_PREREGISTRATION.md)
   >
Level 6: Frozen Architecture Specifications
         (LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md)
   >
Level 7: Generated Scientific Reports & Summaries
         (CORRELATION_SEARCH_FINAL_REPORT.md)
   >
Level 8: Prompt Instructions & Conversational Prompts
   >
Level 9: Agent Assumptions & Speculative Narrative
```

---

## 2. Parent Artifact Authority Matrix

| Artifact Path | Authority Level | Description & Status | Certified Invariant |
|:---|:---:|:---|:---|
| `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/CORRELATION_SEARCH_FINAL_RESULTS.csv` | Level 1 | 1,260 confirmatory simulation runs (30 seeds, 14 tasks, 3 models). | Sealed ground truth for NMSE, FP totals, births, and probation costs. |
| `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SEARCH_DESCENDANT_COST.csv` | Level 1 | Cell-level candidate descendant cost breakdown. | Directly links search threshold crossings to probation FLOPs. |
| `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/PREDICTIVE_NONINFERIORITY.csv` | Level 1 | Seed-level aggregated non-inferiority statistics. | Certified non-inferiority test outputs vs margin $+0.0100$. |
| `experiments/PROMOTION-POLICY-01/PROMOTION_POLICY_01_EVENTS.csv` | Level 1 | Fine-grained candidate lifecycle event traces. | Detailed birth, observation, update, and decision traces. |
| `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01/CORRELATION_SEARCH_SEAL_AUDIT_FINAL_REPORT.md` | Level 3 | Sealed audit report from previous stage. | Corrected statistical lineage ($t=-2.435$, compute $=111.01$). |
| `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01/CORRELATION_SEARCH_SEAL_CORRIGENDUM.md` | Level 3 | Binding errata notice. | Formal retractions of churn/filter claims. |
| `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01/SEARCH_MEMORY_RECONCILIATION.csv` | Level 3 | Memory component decomposition. | Establishes 330B, 192B, 260B, and 802B RAM definitions. |
| `src/lebre/` | Level 2 | Canonical immutable source code. | Strictly immutable (124/124 pytests passing). |

---

## 3. Epistemic Conflict Resolution Rules

1. **Raw Log Invariance:** In any dispute between narrative descriptions in Level 7 reports and numerical columns in Level 1 CSVs (e.g. candidate births, compute breakdowns, or NMSE differences), the Level 1 CSV strictly prevails.
2. **Deterministic Derivations:** All totals, margins, ratios, and percentages in this stage must be computed directly from raw data via deterministic Python scripts. Manual transcription of floating point numbers into reports without programmatic validation is prohibited.
3. **No Retuning Invariant:** Algorithmic parameters ($T_{\text{prob}} = 15$ shadow observations, $H = 32, B = 4, K_{\text{probe}} = 2$, multirate clocks, $\theta_{\text{promote}}$) are strictly frozen.
