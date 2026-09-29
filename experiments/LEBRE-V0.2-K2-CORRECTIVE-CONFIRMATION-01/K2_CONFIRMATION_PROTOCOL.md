# Experimental Protocol: K=2 Corrective Confirmatory Validation

**Study ID:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Governance:** Strict single-hypothesis confirmatory validation ($N=30$)  
**Date:** September 2026  

---

## 1. Context & Motivation

In stage `LEBRE-V0.2-RECURRENT-SHADOW-SEAL-AUDIT-01`, forensic analysis established that:
1. Fixed $K=5$ recurrent-state decimation under `HOLD_STATE` is **robustly refuted** due to severe state-trajectory distortion (MAE $= 0.5810$) and predictive failure ($\Delta \text{NMSE} = +0.0321$).
2. Candidate $C_2$ ($K=2$) was identified as a **`PROMISING_DEV_BOUNDARY`** in DEV screening ($N=10$, seeds $1901..1910$), achieving an aggregate $\Delta \text{NMSE} = +0.004208 \le +0.0100$ and total compute of $100.701790\text{ FP/step}$ ($+0.702\text{ FP}$ near-miss).
3. However, $K=2$ has **never received confirmatory $N=30$ evaluation** on the current $M_1^*$ rotating sparse frontier branch.

This study exists solely to execute this fresh $N=30$ confirmatory comparison against concurrent causal parent $C_0$.

---

## 2. Experimental Arms

1. **$C_0$ (Concurrent Causal Control):**
   - Architecture: $M_1^*$ Rotating Sparse Frontier ($H=32, B=4, K_{\text{probe}}=2$).
   - Recurrent Clocks: $K_{\text{rec\_forward}}=1, K_{\text{rec\_learn}}=10$.
   - Candidate Probation: $T_{\text{prob}}=15, \theta_{\text{promote}}=0.02, \theta_{\text{tol}}=0.015, K_{\text{arb}}=5$.
   - Skip Semantics: N/A ($K=1$ runs continuously).
2. **$C_2$ (K=2 Confirmatory Candidate):**
   - Architecture: Identical to $C_0$ in every dimension.
   - Recurrent Clocks: **$K_{\text{rec\_forward}}=2$**, $K_{\text{rec\_learn}}=10$.
   - Skip Semantics: `HOLD_STATE` (stale state on odd steps).

---

## 3. Strict Invariants
1. Single-intervention invariant: only $K_{\text{rec\_forward}}$ changes ($1 \to 2$).
2. No other candidate cadences ($K=3, K=4, K=5, K=10$) are tested.
3. Reference model $R_0$ is not rerun (local causal question).
4. No post-hoc tuning or hyperparameter adjustment permitted.
5. Canonical `src/` and `tests/` remain 100% immutable.
