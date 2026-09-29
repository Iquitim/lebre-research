# Architectural Candidate Decision: Corrective Confirmation of Resource Compaction

**Decision ID:** `LEBRE-V0.2-CORRECTIVE-CONFIRMATION-DECISION-01`  
**Parent Decision:** `LEBRE-V0.2-RESOURCE-COMPACTION-DECISION-01`  
**Evaluation Target:** $C_1$ (`C1_CANONICAL_FP16`) vs $C_0$ (`C0_CANONICAL_FP32`) under True Canonical Scaling  
**Author:** Independent Skeptical Senior Reviewer  
**Status:** CONFIRMED AND AUTHORIZED  

---

## 1. Executive Summary & Verdict

Following the discovery in the forensic seal audit that the online causal scaler update (`self.scaler.update`) was omitted from the parent compaction runner, study `LEBRE-V0.2-RESOURCE-COMPACTION-CORRECTIVE-CONFIRMATION-01` was executed to evaluate the FP16 correlation-grid compaction under strictly verified canonical conditions.

### Final Audit Verdict: `PASS_CORRECTIVE_CONFIRMATION`

1. **Deterministic Canonical Parity:** $C_0$ demonstrated 100% bitwise parity against the sealed canonical reference `IntegratedLEBREModel(topology="T3")` across all 14 benchmark tasks for 6,000 steps ($84,000$ total steps evaluated, 0 event mismatches, $\max |\hat{y}_{\text{canon}} - \hat{y}_{C0}| = 0.00\times 10^0$).
2. **Predictive Equivalence Reconfirmed:** Across 30 independent confirmatory seeds ($N=30$, 840 total model runs), $C_1$ achieved an aggregate mean NMSE of $0.28986$ compared to $0.29080$ for $C_0$ ($\bar{\Delta} = -0.00094$). The paired Two One-Sided Tests (TOST) within the preregistered equivalence margin $\Delta_{\text{tol}} = \pm 0.0100$ rejected the null hypothesis of non-equivalence at $p_{\text{TOST}} = 7.59 \times 10^{-20}$ ($90\%$ CI: $[-0.00179, -0.00009]$).
3. **Physical Memory Ceiling Met:** Compacting the persistent background correlation grid from IEEE 754 single precision (`float32`, $660$ B) to half precision (`float16`, $330$ B) yields an exact physical memory reduction of $330.0$ Bytes. Total preallocated persistent capacity decreases from $1,306$ Bytes to **$976$ Bytes**, and peak working memory (including stack execution workspace) decreases from $1,310$ Bytes to **$984$ Bytes**—both strictly satisfying the preregistered $1,024$ Byte ceiling (Gate 11).
4. **Structural & Dynamic Parity:** Modal structural state agreement was $99.8\%$ ($419/420$ task runs identical). Discrete lag support recovery $F_1$ was preserved with $0.0000$ delta on $I_3$ ($0.4000$) and $I_4$ ($0.2990$). Redundancy arbitration co-activation fraction on $I_{10}$ changed by only $-0.0042$, and regime switching latencies remained within $16$ steps.

---

## 2. Gate Verification Ledger

| Gate | Criterion | Threshold / Bound | Measured C0 | Measured C1 | Delta / CI | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gate 1: Canonical Parity** | Parity vs `IntegratedLEBREModel` | Bitwise Identity | $0$ err | N/A (Tested C0) | $\max \Delta = 0.00\text{e}0$ | **PASS** |
| **Gate 2: Aggregate NMSE** | Paired TOST ($N=30$ seeds) | $\pm 0.0100$ | $0.29080$ | $0.28986$ | $[-0.00179, -0.00009]$ | **PASS** ($p < 10^{-19}$) |
| **Gate 3: Pure Delay NMSE** | Pure delay streams ($I_3, I_4, I_5$) | $\pm 0.0150$ | $0.34569$ | $0.34234$ | $-0.00335 \pm 0.0112$ | **PASS** |
| **Gate 4: Lag Support F1** | $F_1$ score on $I_3, I_4$ | $\pm 0.0500$ | $0.3495$ | $0.3495$ | $\Delta = 0.0000$ | **PASS** |
| **Gate 5: Arbitration Parity** | $I_{10}$ dual active fraction | $\pm 0.0200$ | $0.0946$ | $0.0904$ | $\Delta = -0.0042$ | **PASS** |
| **Gate 6: Hybrid Gains** | $I_9$ conditional gains | $\pm 0.0050$ | $0.2521, 0.1400$ | $0.2565, 0.1402$ | $+0.0044, +0.0002$ | **PASS** |
| **Gate 7: Tracking Latency** | Median switch latency | $\pm 50.0$ steps | $408.5, 223.0, 89.5$ | $408.5, 207.0, 89.5$ | $\Delta \in [-16.0, 0.0]$ | **PASS** |
| **Gate 8: Persistent Capacity** | Static persistent ceiling | $\le 1,024$ Bytes | $1,306$ B | **$976$ B** | $-330$ Bytes | **PASS** |
| **Gate 9: Peak Working RAM** | Persistent + transient stack | $\le 1,024$ Bytes | $1,310$ B | **$984$ B** | $-326$ Bytes | **PASS** |
| **Gate 10: Numerical Stability**| NaN, Inf, or saturation | 0 occurrences | $0$ | $0$ | None | **PASS** |

---

## 3. Scope Limits & Explicit Authorizations

1. **Authorization Granted:** The architectural candidate $T_3$ with half-precision correlation grid compaction ($C_1$) is formally authorized as the reference baseline for Milestone M2.5.
2. **Resource Reclassification Resolved:** Under $C_1$, $T_3$ satisfies the strict legacy R2 persistent memory ceiling ($< 1,024$ Bytes), eliminating the need for post-hoc gate relaxation to $2,048$ Bytes.
3. **Shadow Compute Remains Unbounded:** Live floating-point compute is compliant ($81.17$ FLOPs/step $\le 100$), but total online compute remains $167.70$ FLOPs/step due to un-optimized round-robin shadow probing ($86.53$ FLOPs/step). Milestone M2.6 must focus on shadow-rent reduction (adaptive probing, event-triggered evaluation).
4. **Immutability Maintained:** Canonical source code in `src/` and `tests/` remains 100% bitwise untouched. Milestone M3 remains unopened.
