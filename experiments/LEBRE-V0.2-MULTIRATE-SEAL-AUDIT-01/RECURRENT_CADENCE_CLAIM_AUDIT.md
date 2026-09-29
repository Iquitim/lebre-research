# Recurrent Cadence Claim Forensic Audit

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Claim Under Audit

The parent report (`SHADOW_MULTIRATE_FINAL_REPORT.md`) asserts:
> *"RECURRENT_STATE_CONTINUITY_REQUIRED = YES"*  
> *"Recurrent forward state propagation cannot be decimated ($K=1$ is strictly required)."*

---

## 2. Empirical Evidence from DEV Sensitivity and Rate Ladders

In `COMPONENT_RATE_BOUNDARIES.csv` and `COMPONENT_SENSITIVITY_DEV_RESULTS.csv`:
1. **Recurrent Forward State Propagation (`REC_FWD`):**
   - $K=1$: $\Delta \text{NMSE} = 0.000000$ (Reference baseline)
   - $K=2$: $\Delta \text{NMSE} = +0.001374$ (Well within $+0.0100$ predictive margin)
   - $K=5$: $\Delta \text{NMSE} = +0.002858$ (Well within $+0.0100$ predictive margin)
   - $K=10$: $\Delta \text{NMSE} = +0.010144$ (Exceeds $+0.0100$ predictive margin)
2. **Recurrent Parameter Learning (`REC_LRN`):**
   - $K=1$: $\Delta \text{NMSE} = 0.000000$
   - $K=2$: $\Delta \text{NMSE} = -0.001951$
   - $K=5$: $\Delta \text{NMSE} = +0.001242$
   - $K=10$: $\Delta \text{NMSE} = -0.000203$ (Zero performance degradation)

---

## 3. Scientific Software Forensic Analysis

Under strict scientific auditing standards, a cadence of $K=1$ cannot be termed **strictly required** merely because it performs numerically best. Strict necessity requires demonstrating that every $K > 1$ violates a preregistered requirement or breaks an essential mechanistic invariant.

Here, decimating recurrent forward propagation to $K=2$ or $K=5$ incurs only a minor predictive penalty ($+0.00137$ to $+0.00286$), which remains safely within the project's practical non-inferiority margin ($+0.0100$). Only when decimation reaches $K=10$ does the error cross the margin ($+0.01014$).

In contrast, recurrent parameter learning updates can be decimated by a factor of 10 ($K=10$) with essentially no loss in predictive fidelity ($\Delta \text{NMSE} = -0.00020$).

---

## 4. Required Classification and Overgeneralization Guard

- **Classification:** **`RECURRENT_STATE_PROPAGATION_MORE_CADENCE_SENSITIVE`**
- **Parameter Learning Status:** **`RECURRENT_PARAMETER_LEARNING_K10_TOLERATED = YES`**
- **Literature Discipline Guard:** The report must NOT claim that all recurrent learning or all RTRL algorithms can generally be updated 10× slower. The claim must strictly state:
  > *"Under the tested LEBRE benchmark and frozen candidate, recurrent parameter updates tolerated $K=10$."*
