# Correlation Search Seal Audit Protocol

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Seal Audit (Experimental Stream v0.2)  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **ACTIVE SEAL AUDIT PROTOCOL**  

---

## 1. Audit Mandate and Governing Constraints

This protocol governs the independent forensic seal audit of experimental study `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`.

### Invariant Governance Rules:
1. **NO NEW STOCHASTIC STREAM SIMULATIONS:** The audit operates strictly post-hoc on sealed raw artifacts, frozen specifications, and deterministic analysis. No new seeds, runs, or clock retunings are permitted.
2. **CANONICAL IMMUTABILITY:** Canonical codebase (`src/` and `tests/`) is frozen and inviolable (124/124 pytests passing).
3. **PARENT ARTIFACT PRESERVATION:** Parent artifacts in `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/` are immutable and hashed in `PARENT_ARTIFACT_HASHES.txt`. All audit outputs reside exclusively in `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01/`.
4. **PRIMARY INFERENTIAL UNIT:** The independent unit of statistical inference is the **random seed** ($N=30$, seeds $1811..1840$). Repeated benchmark tasks within seeds are aggregated prior to paired statistical tests.

---

## 2. Core Audit Objectives & Investigation Targets

1. **Statistical-Lineage Reconciliation (Flag A):**
   - Trace the exact mathematical and computational origin of the reported paired statistic:
     $$t = -4.57, \quad p = 4.20 \times 10^{-5}$$
   - Contrast this with the established $N=30$ seed-level paired test against zero difference, determining whether testing against the $+0.0100$ non-inferiority margin was conflated with testing against zero.
2. **Compute-Lineage Reconciliation (Flag B):**
   - Reconcile reported total online compute ($110.82\text{ FP/step}$) with raw data means ($111.01\text{ FP/step}$), tracing whether $110.82$ was derived from an analytical component summation.
3. **Mechanistic Replication Audit (Flag C):**
   - Evaluate whether candidate probation churn reduction observed on DEV ($89.94 \to 38.64$ births) replicated in the confirmatory FINAL cohort ($90.22$ vs $92.97$).
4. **Outcome Taxonomy & Pareto Dominance (Flags D & E):**
   - Audit whether "superior" language is justified given that $M_1^*$ has higher total compute than $R_1$ ($111.01$ vs $106.74\text{ FP/step}$), establishing whether strict Pareto dominance holds.
   - Enforce literal application of preregistered success criteria for global validation.
5. **Search Space Geometry & Memory Semantics (Flag F):**
   - Clarify the distinction between $5 \times 33 = 165$ physical cells (including lag 0) and $5 \times 32 = 160$ searchable temporal coordinates, proving the $330\text{ B}$ FP16 arithmetic.
   - Decompose the $192\text{ B}$ FP16 accumulators and $260\text{ B}$ total search state for $M_1^*$.
6. **Anti-Starvation Queue Semantics (Flag G):**
   - Reconcile the analytical exploration revisit interval ($272\text{ steps}$ for single probe vs $80\text{ steps}$ for batch probe) with the observed maximum silence ($80.00\text{ steps}$).
7. **Run-Count and Step-Count Accounting (Flags H & I):**
   - Audit Phase 2 DEV run counts ($840$ vs $980$) and confirmatory stream step accounting ($2,520,000$ per model vs $7,560,000$ total).
8. **Claim Scoping & Corrigendum (Flag J):**
   - Scope narrative claims ("Kronecker delta", "irreducible floor", "mathematically impossible below 100", "Matching Pursuit equivalence", "permanent dense deprecation") to empirical evidence.
