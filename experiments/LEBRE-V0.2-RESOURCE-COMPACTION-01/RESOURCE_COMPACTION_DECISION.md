# Formal Architectural Decision: Correlation-State Precision Compaction

**Document Identifier:** `RESOURCE_COMPACTION_DECISION.md`  
**Study Identifier:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Candidate Evaluated:** $T_3$ (*Resource-Aware Conditional Arbitration*)  
**Intervention Evaluated:** C1 (*FP16 Grid Storage with Transient FP32 Update*) vs. C0 (*Sealed FP32 Reference*)  
**Auditor / Reviewer:** Independent Skeptical Senior Reviewer  
**Date:** September 2026  

---

## 1. Formal Decision Verdict

$$\mathbf{DECISION: \ RESOURCE\_COMPACTION\_SUPPORTED}$$

Based on exhaustive confirmatory benchmarking across all 14 integration tasks over 30 independent fresh seeds (`1411`..`1440`, $N=420$ paired simulations) and deterministic numerical stress testing, the empirical evidence demonstrates that:

1. **Persistent Memory Compliance (Gate 11 Recovery):**
   Casting the persistent representation of `corr_grid` from `float32` to IEEE 754 `float16` reduces persistent algorithmic memory from **$1,306$ Bytes to $976$ Bytes** (a net saving of $330$ Bytes, or $25.27\%$). This restores full compliance with the historical LEBRE R2 1-KiB ceiling (`TOTAL_PERSISTENT_BYTES <= 1024`) with zero persistent FP32 master copy. Peak working memory is bounded at **$984$ Bytes**.
2. **Predictive & Structural Equivalence:**
   Across all 14 tasks, the paired NMSE difference between C1 and C0 is negligible ($+8.62 \times 10^{-6}$ aggregate delta; 90% CI: $[-4.02 \times 10^{-6}, +2.13 \times 10^{-5}]$), rejecting degradation hypotheses at $p_{\text{TOST}} < 10^{-15}$ against the preregistered $\pm 0.0100$ bound.
   Candidate Top-1 agreement ($99.73\%$), Top-3 set overlap ($99.62\%$), structural state agreement ($99.95\%$), and modal classification ($100.0\%$) confirm complete behavioral preservation.
3. **Numerical Invariants:**
   Zero overflows, zero underflows, zero uncaught infinities/NaNs, and zero update stagnation events were detected across $2.52 \times 10^6$ streaming steps and 7 synthetic boundary stress tests.

---

## 2. Updated Architectural Baseline

The canonical integration candidate specification for $T_3$ is formally updated to incorporate the compacted correlation grid:

$$\mathbf{T3\_COMPACTED\_RESOURCE\_AWARE\_CONDITIONAL\_ARBITRATION}$$

- **Grid Allocation:** `self.corr_grid = np.zeros((5, 33), dtype=np.float16)` ($330$ Bytes);
- **Update Arithmetic:** Transient FP32 registers for accumulation and candidate threshold evaluation;
- **Persistent State Budget:** $976$ Bytes ($\le 1024$ Bytes);
- **Transient Register Budget:** $\le 8$ Bytes;
- **Peak RAM Budget:** $984$ Bytes.

---

## 3. Explicit Boundaries & Non-Decisions

To maintain scientific integrity and prevent scope inflation, the following boundaries are strictly enforced:
1. **Gate 6 Remains UNRESOLVED:** Dual occupancy rate on $I_{10}$ remains at $3.3\%$–$3.5\%$, with individual seed breaches occurring. Precision compaction does not resolve Gate 6.
2. **Total Online Compute Remains UNRESOLVED:** Aggregate online compute remains at $108.19$ FLOPs/step ($> 100$ FLOPs). Throttling shadow exploration to satisfy total-compute governance is strictly delegated to the subsequent shadow-rent study.
3. **Lag Specificity Remains UNCHANGED:** Support F1 on $I_3$ ($0.2133$) and $I_4$ ($0.1143$) is preserved without alteration.
4. **Codebase Immutability:** `src/` and `tests/` remain 100% bitwise immutable. Milestone $M_3$ remains unopened (`M3_STATUS = UNOPENED`). Canonical version remains `0.1` (`FROZEN_WITH_SCOPE_LIMITS`). `NOVELTY_CLAIM_READY = NO`.

---

## 4. Transition Authorization

With the recovery of the historical 1-KiB persistent memory ceiling formally established and behaviorally certified, the architecture is authorized to proceed to the next targeted resource investigation:

$$\mathbf{AUTHORIZED \ NEXT \ STAGE: \ LEBRE\text{-}V0.2\text{-}SHADOW\text{-}RENT\text{-}01}$$
*(Adaptive Exploration Throttling, Shadow-Rent Scheduling & Total-Compute 100-FLOP Recovery)*
