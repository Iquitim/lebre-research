# Scientific Decision Document: Multirate Shadow Governance

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  
**Status:** SEALED SCIENTIFIC DECISION  

---

## 1. Primary Scientific Verdict

```
======================================================================
PRIMARY_OUTCOME =
COMPONENT_TIMESCALE_CONFLICT

MULTIRATE_SHADOW_GOVERNANCE_SUPPORTED =
NO

WHOLE_BLOCK_SHADOW_GOVERNANCE =
NOT_VALIDATED

SAFE_FOR_INTEGRATED_VALIDATION =
NO

SAFE_FOR_GATE6_REPAIR_STAGE =
NO

SAFE_FOR_LAG_SPECIFICITY_STAGE =
NO

SAFE_TO_OPEN_M3 =
NO

CANONICAL_SRC_CHANGED =
NO

CANONICAL_TESTS_CHANGED =
NO
======================================================================
```

---

## 2. Evidence Synthesis Across Preregistered Criteria

| # | Acceptance Criterion | Preregistered Threshold | Observed M1 Value | Inferential Unit / N | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Mean Total Online Compute** | $\le 100.00\text{ FP/step}$ | $108.36\text{ FP/step}$ | Seed aggregate ($N=30$) | **FAIL** |
| 2 | **Predictive Non-Inferiority** | 95% CI Upper $< +0.0100$ | $+0.027173$ ($\Delta = +0.019376$) | Seed aggregate ($N=30$) | **FAIL** |
| 3 | **Pure-Lag Preservation** | $\Delta \text{NMSE} \le +0.0150$ | $I_4: +0.0339, I_5: +0.0721$ | Task mean ($N=30$) | **FAIL** |
| 4 | **Continuous-Latent Preservation** | Discovery preserved, $\Delta \le 0.01$ | $I_6: +0.001150$ | Task mean ($N=30$) | **PASS** |
| 5 | **Directional Switching** | $\Delta \text{latency} \le +50\text{ steps}$ | $I_{11}: +79.7, I_{12}: +633.7$ | Task mean ($N=30$) | **FAIL** |
| 6 | **Hybrid Complementarity** | $G_{D\|BR} > 0, G_{R\|BD} > 0$ | $G_{D\|BR}=0.231, G_{R\|BD}=0.053$ | Task $I_9$ ($N=30$) | **PASS** |
| 7 | **Quiescent Retention** | Zero drift during silence | Preserved ($100\%$ retention) | Tasks $I_7, I_8$ | **PASS** |
| 8 | **No Privileged Information** | Zero oracle access | Audited (Strict causal online) | Full pipeline | **PASS** |
| 9 | **All Overhead Counted** | Zero unmetered operations | 100% ops accounted in ledger | Full pipeline | **PASS** |
| 10| **Numerical Stability** | Zero NaN / Inf / float overflow | Verified (0 numerical faults) | 1,260 runs | **PASS** |
| 11| **Memory Accounting** | Phase A semantics applied | 1064 B peak persistent | Audited | **FAIL (Legacy)** |
| 12| **Canonical Immutability** | `src/` and `tests/` untouched | 0 bytes modified | Git tree hash verified | **PASS** |

---

## 3. Causal Interpretation of the Failure Mechanism

The experiment aimed to resolve the whole-shadow failure observed in $S_2$ and $S_3$ by decomposing the shadow subsystem into component-specific temporal clocks:
$$\text{Probing } (K=2), \quad \text{Candidate Obs } (K=5), \quad \text{Candidate LMS } (K=10), \quad \text{Recurrent Fwd } (K=1), \quad \text{Recurrent RTRL } (K=10), \quad \text{Arbitration } (K=5)$$

While this design proved two critical scientific hypotheses:
1. **`RECURRENT_STATE_CONTINUITY_REQUIRED = YES`:** Path-dependent hidden state propagation cannot be decimated without dynamical instability, whereas parameter gradient updates tolerate $10\times$ decimation.
2. **`RECURRENT_LEARNING_SLOW_TIMESCALE_TOLERATED = YES`:** Decoupling recurrent state forward propagation ($K=1$) from RTRL gradient evaluation ($K=10$) saved $34.78\text{ FP/step}$ with zero loss of latent tracking capacity.

It encountered a fundamental **`COMPONENT_TIMESCALE_CONFLICT`**:
- Probing 165 pairs in the correlation grid requires rapid scanning ($K=1$). Decimating probing to $K=2$ halves scanning velocity, delaying candidate discovery. This directly caused:
  - Failure of pure-lag preservation on $I_4$ ($\Delta \text{NMSE} = +0.0339$) and $I_5$ ($\Delta \text{NMSE} = +0.0721$).
  - Failure of directional switching on $I_{11}$ ($\Delta = +79.7\text{ steps}$) and $I_{12}$ ($\Delta = +633.7\text{ steps}$).
- Meanwhile, keeping recurrent forward continuous ($12.00\text{ FP/step}$) on top of the live pipeline ($76.30\text{ FP/step}$) sets a hard baseline of $88.30\text{ FP/step}$.
- Consequently, total online compute reached **$108.36\text{ FP/step}$**, failing the primary compute gate ($\le 100.00\text{ FP/step}$).
- Event-triggered routing ($MR_3$) successfully breached the budget ($92.49\text{ FP/step}$), but caused severe predictive collapse ($\Delta \text{NMSE} = +0.0684$) by falsely sleeping on critical delay discovery intervals.

---

## 4. Next Recommended Stage

The evidence conclusively demonstrates that neither monolithic whole-shadow decimation ($S_2/S_3$) nor independent temporal rate decimation ($M_1$) can achieve $\le 100.00\text{ FP/step}$ without predictive or structural impairment under the current 165-pair correlation grid topology.

Furthermore, the 1-KiB peak SRAM ceiling remains violated ($1064\text{ B}$ peak persistent occupied state).

Therefore, the next recommended research stage is:
**`LEBRE-V0.2-PEAK-MEMORY-COMPACTION-01`**  
Focus: Compacting the dual-occupancy persistent state representations and resolving the correlation grid dimension to physically lower the live and shadow floors before reopening architectural integration.
