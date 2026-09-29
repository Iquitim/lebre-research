# LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01 Protocol

**Confirmatory Integrity, Forensic Resource-Ledger Reconciliation, Inferential-Unit Certification & FP16 Compaction Seal**

---

## 1. Governance & Authority

This document defines the formal forensic protocol governing the seal audit of `LEBRE-V0.2-RESOURCE-COMPACTION-01` (Milestone 2, Stage 2.2).

### 1.1 Frozen Scientific Baseline
In accordance with LEBRE Experimental Governance (`AGENTS.md`, `LEBRE_V0_2_SEAL_AUDIT_PROTOCOL.md`):
- `ARCHITECTURE = LEBRE`
- `CANONICAL_VERSION = 0.1`
- `LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`
- `EXPERIMENTAL_V0_2_CANDIDATE = T3_RESOURCE_AWARE_CONDITIONAL_ARBITRATION`
- `COMPACTION_CANDIDATE = T3_FP16_CORR_GRID_FP32_UPDATE`
- `M3_STATUS = UNOPENED`
- `NOVELTY_CLAIM_READY = NO`
- `CANONICAL_SRC_MUTATION = FORBIDDEN`
- `CANONICAL_TEST_MUTATION = FORBIDDEN`
- `NEW STOCHASTIC MODEL RUNS = FORBIDDEN`
- `NEW SEEDS = FORBIDDEN`
- `THRESHOLD CHANGES = FORBIDDEN`
- `ALGORITHM CHANGES = FORBIDDEN`

### 1.2 Audit Mandate & Philosophy
The role of this audit is **NOT** to design a new topology, improve accuracy, optimize hyperparameters, fix Gate 6, or invent new memory formats.
The sole mandate is to verify whether the evidence supporting the FP16 compacted candidate $C_1$ (`T3_FP16_CORR_GRID_FP32_UPDATE`) is internally consistent, arithmetically proven, free from reporting overstatements, certified under the correct inferential unit, and cryptographically sealed as the reliable baseline for Stage `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`.

---

## 2. Core Forensic Audit Issues (A–F)

The protocol establishes six mandatory forensic reconciliation targets:

### 2.1 Issue A — Compute Ledger Semantics
Artifacts in the parent compaction study reported apparently disparate compute quantities:
- $56.52$ live FP FLOPs/step (reported in final report machine-readable block)
- $81.37$ live FP FLOPs/step (reported in resource report Table 6)
- $26.83$ shadow FP FLOPs/step (reported in resource report Table 6)
- $88.65$ shadow FP FLOPs/step (recorded in raw simulation CSV)
- $108.19$ total online FP FLOPs/step (single-regime aggregate)
- $167.99$ total online FP FLOPs/step (full 14-task canonical total)

**Audit Protocol Requirement:**
Every compute number must be traced to its exact Python code origin, execution window, component inclusion/exclusion list, and marginal vs aggregate scope.

### 2.2 Issue B — Memory Ledger Reconciliation & Arithmetic Proof
The parent study claimed persistent state of $1,306$ B ($C_0$) and $976$ B ($C_1$), saving exactly $330$ Bytes. However, the component table in `CORR_GRID_MEMORY_LEDGER.csv` contained sums of $1,410$ B and $1,080$ B due to confusion between maximum capacity and mean occupancy.

**Audit Protocol Requirement:**
The audit must establish an arithmetically closed component ledger distinguishing:
1. `ALLOCATED_CAPACITY_BYTES`
2. `ACTUAL_OCCUPIED_BYTES`
3. `MAX_LOGICAL_STATE_BYTES`
4. `MEAN_OCCUPIED_BYTES`

The audit must verify:
$$\sum \text{component\_persistent\_bytes} \equiv \text{reported\_total\_persistent\_bytes}$$
and demonstrate that under mean occupied state, $C_1$ ($976.32$ B) recovers compliance with the historical $1024$-B ceiling.

### 2.3 Issue C — Numerical Stagnation Wording Reconciliation
The parent study reported both "zero observed stagnation" and "4 stagnation events".

**Audit Protocol Requirement:**
Disaggregate streaming data from synthetic stress tests:
- `STREAMING_OBSERVED_STAGNATION_COUNT`: Evaluated across all $3.36 \times 10^6$ streaming steps.
- `SYNTHETIC_STRESS_STAGNATION_COUNT`: Evaluated under adversarial Test B ($\Delta < 10^{-4}$).
- Reconcile with Cioffi's (1987) finite-precision theorem and Micikevicius et al. (2018).

### 2.4 Issue D — Gate 6 Cross-Cohort Interpretation
The parent integration confirmatory cohort ($N=30$, seeds 1311..1340) had mean `frac_both = 0.1085 > 0.05` (FAIL).
The compaction cohort ($N=30$, seeds 1411..1440) had mean `frac_both = 0.0332 \le 0.05`.

**Audit Protocol Requirement:**
Clarify that the compaction study was an intervention on precision, not an architectural arbitration redesign. Formal status of parent Gate 6 remains `FAIL`. The compaction cohort distribution must be audited for individual seed breaches.

### 2.5 Issue E — Inferential Unit Certification ($N=30$ vs $N=420$)
The parent report conducted statistical equivalence over $N=420$ pooled task-seed pairs, violating the independent inferential unit of LEBRE (Seed, $N=30$).

**Audit Protocol Requirement:**
Aggregate the 14 tasks per seed into $N=30$ genuinely independent paired observations. Recompute the Two One-Sided Tests (TOST) at $\alpha=0.05$ with bound $\pm 0.010$.

### 2.6 Issue F — Zero-Variance Statistical Edge Cases
Several metrics exhibit identical values across all seeds ($\Delta = 0.0, s=0$).

**Audit Protocol Requirement:**
Formally classify zero-variance cases as `EXACT_EMPIRICAL_EQUALITY_ON_CONFIRMATORY_SAMPLE` with `TOST_STATUS = DEGENERATE_ZERO_VARIANCE`, which deterministically satisfies equivalence.

---

## 3. Cryptographic & Verification Artifact Requirements

The audit must produce the following immutable deliverables:
1. `PARENT_ARTIFACT_HASHES.txt`
2. `RESOURCE_COMPACTION_SEAL_METHOD_NOTE.md`
3. `COMPUTE_FIELD_DICTIONARY.md`
4. `COMPUTE_EXECUTION_GRAPH.md`
5. `COMPUTE_LEDGER_RECONCILIATION.csv`
6. `MEMORY_LEDGER_RECONCILIATION.csv`
7. `MEMORY_COMPONENT_PROVENANCE.md`
8. `STEP_COUNT_PROVENANCE.csv`
9. `NUMERICAL_STABILITY_RECONCILIATION.csv`
10. `INFERENTIAL_UNIT_AUDIT.md`
11. `SEED_LEVEL_EQUIVALENCE_RECOMPUTATION.csv`
12. `EQUIVALENCE_RECONCILIATION.md`
13. `GATE6_CROSS_COHORT_RECONCILIATION.md`
14. `RESOURCE_VECTOR_CERTIFIED.csv`
15. `SHADOW_RENT_BASELINE.json`
16. `RESOURCE_COMPACTION_SEAL_CORRIGENDUM.md`
17. `RESOURCE_COMPACTION_SEAL_FINAL_REPORT.md`
18. `RESOURCE_COMPACTION_SEAL_MANIFEST.json`
19. `generate_resource_compaction_seal.py`

---

## 4. Transition Criteria to Stage 2.3

Stage 2.3 (`LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`) is authorized if and only if:
1. All parent artifacts in `LEBRE-V0.2-RESOURCE-COMPACTION-01` are 100% cryptographically preserved.
2. Canonical `src/` and `tests/` remain untouched.
3. Compute and memory ledgers are arithmetically reconciled without manual overrides.
4. Equivalence is certified under the independent inferential unit ($N=30$ seeds).
5. Numerical stability is certified under normal streaming operations.
6. The exact machine-readable block from Section 45 is produced with `SEAL_DECISION = SEALED_FOR_SHADOW_RENT_GOVERNANCE`.
