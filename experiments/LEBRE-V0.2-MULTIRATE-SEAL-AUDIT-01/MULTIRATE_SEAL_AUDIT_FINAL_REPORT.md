# LEBRE v0.2 Multirate Seal Audit Final Report

**Study Identifier:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Audited Parent Study:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Audit Status:** COMPLETE  
**Primary Outcome:** **`MULTIRATE_VALID_WITH_REPORTING_CORRIGENDA`**  

---

## 1. Executive Summary

This independent forensic seal audit was commissioned to adjudicate four fundamental claim and governance questions arising from `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`:
1. **The $T_{\text{probation}}$ Lineage and Execution Mystery ($300$ vs. $15$):** Did the runtime execute an unauthorized change to probation semantics, confounding the causal effect of multirate clock decimation?
2. **Memory Gate Reconciliation:** Does the reported $1064\text{ B}$ peak occupied state constitute a failure of historical v0.1 $R_2$ persistent memory, or strictly a failure of the newer v0.2 Gate 3 peak working SRAM envelope?
3. **Recurrent Continuity Claim Scope:** Is $K=1$ recurrent forward state propagation strictly necessary, or was the claim overstated relative to DEV rate boundary evidence?
4. **Sentinel Router Modal Logic:** Is residual autocorrelation a "necessary but insufficient" router signal, or does empirical evidence refute necessity?

### Core Audited Verdicts:
1. **Probation Root Cause:** The runtime executed **$15$ actual shadow observations** (`b_cand['obs_count'] >= 15` and `self.rec_obs_count >= 15`), strictly inheriting the parent T3 threshold from `LEBRE-V0.2-SHADOW-RENT-GATE-01`. The number $300$ in the report narrative was an unexecuted reporting transcription error (derived from stream warmup `step_count > 300`). **The single-intervention invariant was preserved, and the causal interpretability of the parent confirmatory result is INTACT.** No corrective stochastic confirmation is required.
2. **Memory Reconciliation:** Historical $R_2$-MEM was operationalized as **mean persistent model RAM** ($\le 1024\text{ B}$), under which candidate $M_1$ comfortably passes (**$970.34\text{ B} \le 1024\text{ B}$**, **PASS**). The observed violation occurs strictly under the newer v0.2 Gate 3 **Peak Working SRAM** metric (**$1064\text{ B} > 1024\text{ B}$**, **FAIL**).
3. **Recurrent Cadence Reclassification:** Recurrent forward propagation is significantly more cadence-sensitive than learning, but $K=1$ is not strictly required. Decimation up to $K=5$ preserves NMSE within the $+0.0100$ predictive margin ($\Delta \text{NMSE} = +0.00286$). Recurrent parameter learning tolerates $K=10$ with zero degradation ($\Delta \text{NMSE} = -0.00020$).
4. **Sentinel Router Refutation:** Residual serial correlation is **neither necessary nor sufficient** for routing temporal shadow computation. It failed to detect genuine delay regimes in $>80\%$ of steps on $I_3, I_4, I_5, I_8$, and produced $63\%$ false awakenings on static nonlinear control $I_2$.
5. **Confirmatory Result Preservation:** All primary inferential statistics reproduce with zero arithmetic discrepancies:
   - $M_1$ mean total compute = **$108.36\text{ FP/step}$** (Ceiling $\le 100.00\text{ FP} \implies$ **FAIL**).
   - $M_1$ Delta NMSE = **$+0.019376$**, $95\%$ CI upper bound = **$+0.027173$** (Ceiling $+0.0100 \implies$ **FAIL**).
   - Candidate $M_1$ is **correctly rejected** from canonical integration.

---

## 2. Recomputed Primary Inferential Metrics

All inferential metrics were deterministically recomputed from Level 1 raw seed CSVs ($N=30$, seeds $1711..1740$):

| Metric | Parent Reported | Recomputed Exact | Evaluation Standard | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **$M_0$ Total Compute** | $175.38\text{ FP}$ | $175.3807\text{ FP}$ | Baseline Reference | VERIFIED |
| **$M_1$ Total Compute** | $108.36\text{ FP}$ | $108.3585\text{ FP}$ | Gate Ceiling $\le 100.00\text{ FP}$ | **FAIL** |
| **$M_0$ Aggregate NMSE** | $0.299225$ | $0.299225$ | Baseline Reference | VERIFIED |
| **$M_1$ Aggregate NMSE** | $0.318601$ | $0.318601$ | Candidate Reference | VERIFIED |
| **Mean Delta NMSE** | $+0.019376$ | $+0.019376$ | Margin $\le +0.0100$ | **FAIL** |
| **95% One-Sided Upper CI** | $+0.027173$ | $+0.027173$ | Margin $\le +0.0100$ | **FAIL** |
| **Pure-Lag Preservation** | FAIL | FAIL | $\Delta \text{NMSE} \le +0.0150$ on $I_3, I_4, I_5, I_8$ | **FAIL** ($I_4, I_5, I_8$ fail) |
| **Continuous-Latent Pres.** | PASS | PASS | $\Delta \text{NMSE} \le +0.0150$ on $I_6, I_7$ | **PASS** ($+0.0015, +0.0052$) |
| **Switching Preservation** | FAIL | FAIL | $\Delta \text{Latency} \le +50\text{ steps}$ on $I_{11..14}$ | **FAIL** ($I_{11}: +79.7, I_{12}: +633.7$) |
| **Hybrid Complementarity** | PASS | PASS | $G_{D|B+R} > 0$ and $G_{R|B+D} > 0$ | **PASS** ($0.2311, 0.0532$) |
| **Historical $R_2$ Memory** | FAIL (Reported) | **PASS (Reconciled)** | Mean Persistent RAM $\le 1024\text{ B}$ | **PASS** ($970.34\text{ B}$) |
| **Peak Working SRAM** | FAIL | FAIL | Peak Working SRAM $\le 1024\text{ B}$ | **FAIL** ($1064\text{ B}$) |
| **Modular Clock FP Cost** | $0.0\text{ FP}$ | $0.0\text{ FP}$ | Floating-Point Accounting | VERIFIED |
| **Clock Integer ALU Cost** | Not Reported | $6.0\text{ INT ops/step}$ | Integer Operation Ledger | AUDITED |
| **Clock Persistent State** | $0\text{ Bytes}$ | $0\text{ Bytes}$ | Memory Allocation Ledger | VERIFIED |

---

## 3. Governance Invariants and Seal Decisions

1. **`CANONICAL_SRC_CHANGED`:** `NO` (Verified 124 passing canonical pytest items).
2. **`CANONICAL_TESTS_CHANGED`:** `NO`.
3. **`M3_STATUS`:** `UNOPENED`.
4. **`NOVELTY_CLAIM_READY`:** `NO`.
5. **`T3_CANDIDATE_STATUS`:** `EXPERIMENTAL_NON_CANONICAL`.
6. **`SAFE_FOR_INTEGRATED_VALIDATION`:** `NO`.
7. **`SAFE_TO_OPEN_M3`:** `NO`.
8. **`SAFE_FOR_PEAK_MEMORY_COMPACTION_STAGE`:** `YES`.
9. **`SAFE_FOR_CORRELATION_SEARCH_SPACE_RESEARCH`:** `YES`.

---

## 4. Next Recommended Stage

Because candidate $M_1$ is causally valid but genuinely fails both compute and predictive non-inferiority gates, no corrective multirate confirmation is necessary. The failure is a genuine scientific property of the decoupled clock schedule under the 165-cell correlation grid.

Upon human review, the project may proceed to:
- **`LEBRE-V0.2-PEAK-MEMORY-COMPACTION-01`** (To resolve the $1064\text{ B}$ peak working SRAM violation); or
- **`LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`** (To test the research hypothesis that reducing correlation grid dimensionality resolves the timescale conflict).
