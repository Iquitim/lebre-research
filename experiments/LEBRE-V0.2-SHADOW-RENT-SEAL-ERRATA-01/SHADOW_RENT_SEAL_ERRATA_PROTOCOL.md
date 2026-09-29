# LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01: Protocol & Forensic Audit Charter

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Role:** Independent Scientific-Software Auditor & Forensic Seal Reviewer  
**Audited Architecture:** $T_3$ Resource-Aware Conditional Arbitration  
**Compacted Memory Substrate:** $C_1$ (FP16 Persistent Correlation Grid with FP32 Update)  
**Parent Confirmatory Seeds:** $1611$ .. $1640$ ($N=30$ independent pairs)  
**Status Boundaries:** `CANONICAL_VERSION = 0.1`, `LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`, `M3_STATUS = UNOPENED`, `NOVELTY_CLAIM_READY = NO`

---

## 1. Audit Charter & Epistemic Scope

This stage constitutes a **Micro-Errata and Forensic Seal Reconciliation Audit** of the parent study `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`.

### 1.1 Strictly Prohibited Actions
In accordance with confirmatory scientific integrity and preregistration standards (Simmons et al., 2011; Nosek et al., 2018, 2019):
1. **NO CANONICAL CODE MUTATION:** `src/` and `tests/` remain 100% bitwise immutable.
2. **NO NEW STOCHASTIC RUNS:** No new model executions, seeds, or synthetic streams are permitted.
3. **NO POST-HOC OPTIMIZATION:** No scheduler retraining, threshold tuning, or hyperparameter searching is permitted.
4. **NO PARENT MUTATION:** Artifacts in `experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/` are cryptographically sealed and preserved via SHA-256 hashes (`PARENT_ARTIFACT_HASHES.txt`). All corrections must be additive forensic corrigenda.
5. **NO MILESTONE ADVANCEMENT:** Milestone M3 remains `UNOPENED`. Novelty claims remain `FORBIDDEN`.

### 1.2 Sole Objective
To determine whether the sealed parent artifacts support the governance claims made in `SHADOW_RENT_FINAL_REPORT.md`, to identify and trace all governance and threshold mutations, to correct metric conflations, and to render an authoritative, binding reconciliation of the whole-shadow scheduling seal.

---

## 2. Hard Audit Rule & Data Authority Hierarchy

### 2.1 The Hard Audit Rule
All evaluations must strictly adhere to the causal evidentiary chain:
$$\text{FROZEN PREREGISTRATION} \longrightarrow \text{RAW SEALED ARTIFACT} \longrightarrow \text{EXECUTABLE METRIC} \longrightarrow \text{RECOMPUTATION} \longrightarrow \text{CLAIM} \longrightarrow \text{GOVERNANCE DECISION}$$

Auditors must never use the final report narrative to infer or alter what the preregistration originally specified.

### 2.2 Six-Level Data Authority Hierarchy
When conflicts arise between documents or reporting levels, the higher authority strictly governs:

| Hierarchy Level | Source Type | Documents / Artifacts | Precedence |
|:---|:---|:---|:---:|
| **Level 1** | Raw Sealed Metric Artifacts | `SHADOW_RENT_FINAL_RESULTS.csv`, `RESOURCE_VECTOR_BY_SEED.csv`, `STATE_CONDITIONED_COMPUTE.csv` | **Highest Authority** |
| **Level 2** | Frozen Execution Code | `scratch/run_v02_shadow_rent_governance.py`, `GovernedLEBREModel` | Binding Logic |
| **Level 3** | Frozen Preregistration & Protocol | `SHADOW_RENT_PREREGISTRATION.md`, `SHADOW_RENT_PROTOCOL.md` | Binding Criteria |
| **Level 4** | Prior Reconciled Governance | `GATE6_PREREGISTERED_DEFINITION.md`, `MEMORY_LEDGER_RECONCILIATION.csv` | Binding Lineage |
| **Level 5** | Derived Summary Tables | `PREDICTIVE_NONINFERIORITY.csv`, `SWITCHING_LATENCY_ANALYSIS.csv` | Derivative Data |
| **Level 6** | Narrative Reports & Captions | `SHADOW_RENT_FINAL_REPORT.md`, `figures/F10_*.png`, Manifest blocks | **Lowest Authority** |

---

## 3. The 8 Core Audit Inquiries (Inquiries A–H)

### Inquiry A: Gate 6 Threshold Drift & Provenance
- Trace the preregistered threshold for Gate 6 ($\rho_{\text{dual}} \le 0.05$ on $I_{10}$) across the entire study lineage.
- Determine whether any formal, pre-confirmatory protocol amendment raised the threshold to $0.10$.
- Recompute exact seed-level statistics for $S_0, S_1, S_2, S_3$ against both the $0.05$ binding threshold and the $0.10$ report threshold.
- Rigorously separate literal gate compliance (`FAIL`) from descriptive algorithmic mitigation (`SUPPORTED`).

### Inquiry B: Memory Metric Semantics & Conflation
- Audit the conflicting statements in the parent study asserting static capacity of $976$–$992$ B while measured peak working memory reached $1068$–$1080$ B.
- Construct an unambiguous memory metric dictionary separating static preallocated bytes, mean occupied bytes, max occupied capacity, transient workspace, and peak working memory.
- Disaggregate compliance across historical R2 ($1024$ B) and proposed $2048$ B ceilings.

### Inquiry C: Compute Floor Semantics
- Investigate the derivation of $F_{\text{min}} = 83.17$ FLOPs/step.
- Contrast this against $S_1$ (Shadow Off) which executed $58.00$ FLOPs/step.
- Formulate the precise definition of $F_{\text{min}}$ as `REFERENCE_OCCUPANCY_CONDITIONED_SHADOW_OFF_FLOOR` and define the unconditional `ABSOLUTE_EXECUTION_FLOOR` ($58.00$ FP).

### Inquiry D: Primary Outcome Taxonomy Drift
- Cross-reference the parent report's outcome label (`COMPUTE_RECOVERED_PREDICTIVE_DEGRADED`) against the exact frozen allowed taxonomy in Section 59 (`COMPUTE_RECOVERED_BEHAVIOR_DEGRADED`).
- Audit taxonomy fidelity and classify the drift.

### Inquiry E: Whole-Block Shadow Governance & Integration Readiness
- Evaluate whether any tested scheduler ($S_2$ or $S_3$) satisfied all mandatory gates.
- Clarify integration authorization: distinguish between `SAFE_FOR_NEXT_RESEARCH_STAGE` (yes, shadow multirate research) and `SAFE_FOR_INTEGRATED_VALIDATION` (no).

### Inquiry F: Claims of "Inherent" Accuracy Costs
- Audit statements claiming duty cycling incurs an "inherent" or "unavoidable" accuracy penalty.
- Reframe claims to state that this trade-off was observed under the specific uniform periodic policy ($K=5$) and does not represent an unalterable theoretical limit.

### Inquiry G: Long-Horizon Extrapolation Audit
- Audit claims asserting $S_3$ duty cycle drops below $5\%$ on streams longer than $6,000$ steps.
- Classify as an unverified extrapolation rather than an empirical confirmatory result.

### Inquiry H: "Energy" Terminology Audit
- Scan for colloquial uses of "energy" and replace with precise physical or algorithmic quantities (compute savings, shadow execution reduction, algorithmic work reduction).

---

## 4. Primary Outcome Taxonomy for this Audit Stage

In accordance with Section 50, the terminal outcome of this audit must be classified into one of the following exact categories:

1. `CLEAN_SHADOW_RENT_SEAL`: No substantive errata required.
2. `SHADOW_RENT_VALID_WITH_REPORTING_CORRIGENDA`: Raw experimental result remains valid, but reporting/governance semantics require correction.
3. `WHOLE_BLOCK_GOVERNANCE_NOT_VALIDATED`: No tested whole-shadow scheduler satisfies all mandatory gates.
4. `MEMORY_GATE_RECLASSIFIED`: A previous memory PASS becomes FAIL under the exact frozen gate.
5. `GATE6_THRESHOLD_DRIFT_CONFIRMED`: The 10% threshold was post-hoc / inconsistent with frozen governance.
6. `MULTIPLE_CORRECTABLE_ISSUES`: Multiple substantive errata (Gate 6 threshold drift, memory conflation, compute floor redefinition, outcome label mismatch).
7. `PARENT_RESULT_REQUIRES_REEVALUATION`: Fundamental invalidation of experimental execution.
8. `INSUFFICIENT_ARTIFACT_EVIDENCE`: Missing raw data prevents verification.
