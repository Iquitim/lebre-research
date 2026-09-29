# Artifact Authority Map & Evidentiary Precedence

**Audit Identifier:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Parent Study Audited:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Standard:** Eight-Tier Authority Hierarchy  

---

## 1. Evidentiary Hierarchy Classification

When discrepancies arise between artifacts, precedence is strictly dictated by the authority hierarchy:

```
LEVEL 1: Raw Sealed Execution Artifacts (CSV, JSON, Event Traces)
    >
LEVEL 2: Executable Implementation & Frozen Code (Model runtime, runner scripts)
    >
LEVEL 3: Preregistration & Frozen Candidate Specs (Pre-simulation freezes)
    >
LEVEL 4: Experimental Protocols & Methodological Standards
    >
LEVEL 5: Sealed Forensic Errata & Prior Certified Audits
    >
LEVEL 6: Narrative Reports, Summaries, and Generated Figure Captions
    >
LEVEL 7: User Requests & Interactive Prompts
    >
LEVEL 8: Unverified Assumptions & Post-Hoc Interpretations
```

---

## 2. Comprehensive Artifact Precedence Table

| Artifact Name | Location | Authority Level | Epistemic Role & Authority Bound |
| :--- | :--- | :--- | :--- |
| `MULTIRATE_FINAL_RESULTS.csv` | `experiments/...-01/` | **LEVEL 1** | Ground-truth confirmatory telemetry for 1,260 runs. Binding over all reports. |
| `FIRST_DIVERGENCE_TRACE.csv` | `experiments/...-01/` | **LEVEL 1** | Step-by-step structural event trace. Verifies exact runtime promotion timing. |
| `COMPONENT_RATE_BOUNDARIES.csv` | `experiments/...-01/` | **LEVEL 1** | Ground-truth empirical rate boundary grid across 2,800 runs. |
| `COMPONENT_SENSITIVITY_DEV_RESULTS.csv` | `experiments/...-01/` | **LEVEL 1** | Isolated $K=5$ sensitivity data across 840 DEV runs. |
| `MULTIRATE_DEV_RESULTS.csv` | `experiments/...-01/` | **LEVEL 1** | Full DEV policy candidate comparison across 840 runs. |
| `run_v02_multirate_experiments.py` | `scratch/` | **LEVEL 2** | Definitive executable candidate logic. Overrules narrative text when text differs. |
| `run_final_evaluation.py` | `scratch/` | **LEVEL 2** | Deterministic runner and metric aggregation logic. |
| `FINAL_CANDIDATE_FREEZE.md` | `experiments/...-01/` | **LEVEL 3** | Sealed pre-simulation candidate contract. Frozen prior to final runs. |
| `SHADOW_MULTIRATE_PREREGISTRATION.md` | `experiments/...-01/` | **LEVEL 3** | Pre-DEV registered hypotheses, inferential tests, and success gates. |
| `SHADOW_MULTIRATE_PROTOCOL.md` | `experiments/...-01/` | **LEVEL 4** | Operational protocol, benchmark task definitions, and clock specifications. |
| `SHADOW_RENT_SEAL_ERRATA_FINAL_REPORT.md`| `experiments/...-ERRATA-01/` | **LEVEL 5** | Forensic authority on whole-shadow governance failure and Gate 6 ceiling. |
| `MEMORY_METRIC_DICTIONARY.md` | `experiments/...-ERRATA-01/` | **LEVEL 5** | Forensic authority on memory terminology and metric disaggregation. |
| `COMPUTE_FLOOR_SEMANTICS.md` | `experiments/...-ERRATA-01/` | **LEVEL 5** | Forensic authority on 58 FP vs 83.17 FP execution floor definitions. |
| `SHADOW_MULTIRATE_FINAL_REPORT.md` | `experiments/...-01/` | **LEVEL 6** | Narrative synthesis. Subject to Level 1 and Level 2 override upon conflict. |
| `MULTIRATE_RESOURCE_REPORT.md` | `experiments/...-01/` | **LEVEL 6** | Narrative resource breakdown. Subject to Level 1 CSV override. |
| `MULTIRATE_DECISION.md` | `experiments/...-01/` | **LEVEL 6** | Narrative decision document. Subject to Level 1 and Level 3 criteria. |

---

## 3. Discrepancy Arbitration Rules

1. **Rule 1 (Text vs. Runtime Code/Trace):** If a narrative report states a parameter value (e.g. $T_{\text{probation}} = 300$) while Level 2 runtime code and Level 1 event traces execute another value (e.g. `obs_count >= 15`), the Level 1/Level 2 execution is binding. The discrepancy is cataloged as a `REPORTING_ERROR`.
2. **Rule 2 (Report Metric vs. Sealed Metric Definition):** If a narrative report labels a metric using a historical gate identifier (e.g. `HISTORICAL_R2_PERSISTENT_MEMORY_STATUS = FAIL`) while Level 5 errata defines historical R2 compliance via mean persistent memory, the Level 5 metric dictionary is binding.
3. **Rule 3 (Causal Scope):** Empirical findings in Level 1 CSVs are strictly binding only for the tested policies. Generalizations to untested topologies (Level 6 overreach) must be qualified and demoted to `SUPPORTED_ONLY_FOR_TESTED_POLICIES`.
