# LEBRE v0.2 Artifact Reconciliation & Gate-6 Protocol

**Protocol Identifier:** `LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`  
**Stage:** Small Executable Reconciliation Stage  
**Parent Studies:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`, `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`, `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Auditor:** Independent Scientific-Software Auditor  
**Date:** September 2026  
**Status:** Protocol Frozen Prior to Execution  

---

## 1. Scope & Core Objectives

This reconciliation stage has a strictly bounded mandate addressing exactly two technical issues:

1. **Issue A — H7 Artifact Chain & Anti-Copy Verification:**
   Ensure that all generated intermediate artifacts for Hypothesis 7 ($T_1$ vs. $T_{1R}$ sequential cascade order sensitivity) are strictly reproduced from the raw confirmatory dataset (`LEBRE_V0_2_SEED_RESULTS.csv`). Investigate and resolve the extraction bug identified in the prior errata script (`scratch/generate_errata_outputs.py` line 80) where `sub_t1` was erroneously reused for `sub_t1r`, causing intermediate CSVs to record zero deltas while statistical scripts recorded genuine non-zero differences. Implement anti-copy safeguards and regenerate the reconciled H7 artifact chain.
2. **Issue B — Gate 6 Preregistered Governance Compliance:**
   Recover the exact preregistered metric and threshold for Gate 6 from frozen protocol artifacts (`LEBRE_V0_2_INTEGRATION_PROTOCOL.md` and `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md`). Evaluate the confirmatory dataset strictly against this frozen metric (`frac_both <= 0.05`). Enforce the literal governance decision (`GATE_6 = FAIL`) while rigorously separating preregistered gate compliance from algorithmic arbitration effectiveness (`ARBITRATION_EFFECTIVENESS = SUPPORTED`).

No model simulations are re-run, no thresholds are altered, no code in `src/` or `tests/` is touched, and no unrelated architectural questions are investigated.

---

## 2. Frozen Invariants & Governance

The following constraints are permanently binding throughout this reconciliation:

```text
ARCHITECTURE = LEBRE
CANONICAL_VERSION = 0.1
LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS
T3_STATUS = EXPERIMENTAL_NON_CANONICAL
M3_STATUS = UNOPENED
NOVELTY_CLAIM_READY = NO
CANONICAL_SRC_MUTATION = FORBIDDEN
CANONICAL_TEST_MUTATION = FORBIDDEN
NEW_MODEL_SIMULATIONS = FORBIDDEN
```

---

## 3. Data Authority Hierarchy

When evaluating any numerical value or claim, conflicts are adjudicated using this strict hierarchy:

1. **LEVEL 1 (Highest Authority):** Raw confirmatory CSV (`LEBRE_V0_2_SEED_RESULTS.csv`, seeds `1311`..`1340`, $N=30$ independent paired runs).
2. **LEVEL 2:** Frozen simulation code (`scratch/run_v02_integration_experiments.py`, `scratch/bench_v02_integration.py`).
3. **LEVEL 3:** Generated intermediate artifacts (`H7_PAIRED_RAW_VALUES_RECONCILED.csv`, `GATE6_BY_SEED.csv`).
4. **LEVEL 4:** Statistical summary tables (`H7_TASK_SUMMARY_RECONCILED.csv`, `H7_WILCOXON_BY_TASK_RECONCILED.csv`).
5. **LEVEL 5 (Lowest Authority):** Narrative reports and markdown summaries.

**Quarantine Policy:** Confirmatory seeds are strictly `1311`..`1340` ($N=30$). Developmental screening seeds `1301`..`1310` must remain 100% quarantined from all confirmatory recomputations.

---

## 4. H7 Extraction Audit & Anti-Copy Verification Protocol

### 4.1 Independent Extraction Rules
For each benchmark task ($I_1$ through $I_{14}$) and each confirmatory seed ($s \in \{1311..1340\}$):
1. Extract the $T_1$ row independently: `df[(df['task_id'] == task) & (df['topology'] == 'T1') & (df['seed'] == seed)]`.
2. Extract the $T_{1R}$ row independently: `df[(df['task_id'] == task) & (df['topology'] == 'T1R') & (df['seed'] == seed)]`.
3. Assert that exactly one row exists for each tuple `(task, seed, topology)`.
4. Assert that `topology == "T1"` for all $T_1$ rows and `topology == "T1R"` for all $T_{1R}$ rows.

### 4.2 Anti-Copy Safeguards
To guarantee against accidental variable reuse:
1. Assert that the underlying dataframe index/row identifiers for $T_1$ and $T_{1R}$ are strictly disjoint:
   $$\text{index}(T_1) \cap \text{index}(T_{1R}) = \emptyset$$
2. For each task, check whether the extracted NMSE arrays are identical (`np.array_equal(nmse_t1, nmse_t1r)`):
   - If identical, inspect the source row index and classify as:
     - `GENUINELY_IDENTICAL_RAW_VALUES` (e.g., if a memoryless task produced bitwise identical outputs due to identical base parameters); or
     - `EXTRACTION_BUG` (if caused by code assigning `nmse_t1r = sub_t1[...]`).
3. Recompute paired differences: $D(s) = \text{NMSE}_{T1}(s) - \text{NMSE}_{T1R}(s)$.
4. Output verified reconciled files:
   - `H7_PAIRED_RAW_VALUES_RECONCILED.csv`
   - `H7_TASK_SUMMARY_RECONCILED.csv`
   - `H7_WILCOXON_BY_TASK_RECONCILED.csv`
   - `H7_ARTIFACT_RECONCILIATION.csv`

---

## 5. Gate 6 Preregistered Governance Protocol

### 5.1 Preregistered Definition Recovery
From frozen `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (Gate 6, line 61) and `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (lines 68–71):
- **Metric:** $\rho_{\text{dual}, I10}$ defined as the fraction of steady-state evaluation steps ($t \ge 1000$) where BOTH memory classes are simultaneously active (`frac_both`).
- **Evaluation Window:** Steady-state timesteps $t \in [1000, 6000)$ ($T_{\text{eval}} = 5,000$ steps).
- **Preregistered Threshold:** $\rho_{\text{dual}, I10} \le 0.05$ (5.0%).

### 5.2 Mandatory Separation of Concerns
1. **Preregistered Gate Compliance:**
   - Compute mean `frac_both` on $I_{10}$ across confirmatory seeds `1311`..`1340`.
   - Apply the literal rule:
     $$\text{If } \overline{\text{frac\_both}} > 0.05 \implies \mathbf{GATE\_6\_PREREGISTERED\_STATUS = FAIL}$$
   - No threshold modifications ($0.05 \to 0.10$ or $0.15$) are permitted.
   - No metric substitution (`redundant_dual_rate` $\to$ `frac_both`) is permitted.
2. **Arbitration Effectiveness:**
   - In unarbitrated symmetric competition ($T_2$), `frac_both` = $1.0000$ (100% dual occupancy), burning $118.8$ live FLOPs.
   - In conditional arbitration ($T_3$), `frac_both` = $0.1085$, burning $92.4$ live FLOPs, with thresholded `redundant_dual_rate` = $0.0000$.
   - $T_3$ eliminates $89.2\%$ of dual occupancy relative to $T_2$. Therefore:
     $$\mathbf{T3\_I10\_ARBITRATION\_EFFECTIVENESS = SUPPORTED}$$

---

## 6. Preservation of Settled Findings

All other findings from `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01` and `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01` are explicitly preserved:
- $T_3$ architectural candidate selection: `SUPPORTED_WITH_SCOPE_LIMITS`.
- Gate 11 RAM ceiling ($1024$ B): `FAIL` under legacy model ($1306$ B), passes proposed $2048$ B.
- Legacy total-online compute ($100$ FP FLOPs): `FAIL` ($108.2$ aggregate, $168.0$ peak).
- Exact lag-support identification on $I_3/I_4$: `PARTIAL`.
- $T_3$ Pareto result: Strict vector dominance on aggregate benchmark; non-dominated on 12.5% of task pairs.
- $T_3$ internal evaluation-order invariance: `VERIFIED` by deterministic microtest.
- Milestone M3: `UNOPENED`.
