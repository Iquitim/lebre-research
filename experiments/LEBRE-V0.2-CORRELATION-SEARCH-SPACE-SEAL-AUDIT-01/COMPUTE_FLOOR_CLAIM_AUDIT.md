# Compute-Floor & Budget Impossibility Claim Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Resource-Claim Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **SCOPED & QUALIFIED**  

---

## 1. Audit of the "Irreducible Floor" Narrative

### The Parent Narrative Claim:
In `CORRELATION_SEARCH_RESOURCE_REPORT.md` Section 3 and `CORRELATION_SEARCH_FINAL_REPORT.md` Q10:
> "The live baseline path with active dynamic taps and normalization accounts for $76.45\text{ FP/step}$, and continuous recurrent state propagation accounts for $12.00\text{ FP/step}$, establishing an irreducible floor of $88.45\text{ FP/step}$... Operating below $100.00\text{ FP/step}$ is mathematically impossible within the frozen v0.1 multirate clock framework."

---

## 2. Epistemic Classification of the Floor

We audit the arithmetic and contextual scope of this claim:

| Component | Cost (FP/step) | Execution Condition | Generality Classification |
| :--- | :--- | :--- | :--- |
| **Causal Standardization & Normalization** | 25.00 | Every step ($K=1$) | Universal baseline requirement |
| **Linear Base Predictor & LMS Update** | 33.00 | Every step ($K=1$) | Universal baseline requirement |
| **Live Active Lag Predict & Update** | 11.15 | Conditioned on promoted taps | **Occupancy-Conditioned (Not Irreducible)** |
| **Live Active Recurrent Predict & Update** | 7.30 | Conditioned on promoted recurrent unit | **Occupancy-Conditioned (Not Irreducible)** |
| **Recurrent Forward State Propagation** | 12.00 | Continuous path tracking ($K=1$) | **Architecture-Specific (Requires RTRL Unit)** |
| **Sum Reported as "Irreducible Floor"** | **88.45** | Fully active model state | **`ACTIVE_STRUCTURE_CONDITIONED_FLOOR`** |

### Audit Findings:
1. **Not a Global Architectural Floor:**
   In an inactive or quiescent stream (e.g., $I_1$ Memoryless Linear), there are no active dynamic lag taps or promoted recurrent units. In such regimes, live compute is only $58.00\text{ FP/step}$, not $76.45\text{ FP/step}$.
2. **Configuration-Specific Impossibility:**
   The impossibility statement ($< 100\text{ FP/step}$) is **valid ONLY when strictly conditioned on**:
   - The frozen multirate clock set ($K_{\text{probe}}=2, K_{\text{cand\_obs}}=5, K_{\text{cand\_learn}}=10, K_{\text{rec\_fwd}}=1, K_{\text{rec\_learn}}=10, K_{\text{arb}}=5$);
   - Continuous recurrent tracking ($K_{\text{rec\_fwd}}=1$);
   - A non-empty active tier where at least one lag tap and one recurrent unit are promoted.
3. **Corrected Claim Formulation:**
   The claim must not state that "LEBRE cannot operate below 100 FP/step". The legally sound formulation is:
   *"Under the frozen $M_1^*$ configuration, clocks, pricing rules, and active structural occupancy, the derived mean compute exceeds the $100.00\text{ FP/step}$ ceiling."*
4. **Classification:** `UNSUPPORTED_IMPOSSIBILITY_CLAIM` / `GOVERNANCE_OVERSTATEMENT`.
