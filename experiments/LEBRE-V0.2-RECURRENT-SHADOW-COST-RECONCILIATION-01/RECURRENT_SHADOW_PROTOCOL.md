# Experimental Protocol: Recurrent-Shadow Cost Reconciliation & Conditional Revalidation

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Governance:** Two strictly separated layers (Phase A Deterministic, Phase B Stochastic)  
**Date:** September 22, 2026  

---

## 1. Context & Motivation

In stage `LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01`, rigorous accounting proved that the current $M_1^*$ architecture incurs **$111.013591	ext{ FP/step}$**, leaving an $11.013591	ext{ FP/step}$ deficit against the $\le 100	ext{ FP/step}$ budget ceiling. The candidate discovery and probation subsystem accounts for only $7.444633	ext{ FP/step}$ ($1.844634	ext{ FP/step}$ direct candidate work $+ 5.600000	ext{ FP/step}$ candidate arbitration). Even an impossible zero-cost candidate oracle leaves $103.568958 > 100.0	ext{ FP/step}$.

The candidate-independent compute consists of:
1. Base live linear filtering: **$75.468234	ext{ FP/step}$**
2. Rotating search frontier probing ($H=32, B=4, K_{\text{probe}}=2$): **$7.900724	ext{ FP/step}$**
3. Base recurrent shadow execution: **$20.200000	ext{ FP/step}$**

The base recurrent shadow subsystem is the **first and only candidate-independent subsystem whose mass exceeds the entire $11.013591	ext{ FP/step}$ deficit**.

---

## 2. Causal Architecture & Invariants

### 2.1 Causal Reference ($C_0$)
- Model: $M_1^*$ Rotating Sparse Frontier ($H=32, B=4, K_{\text{probe}}=2$).
- Clocks: $K_{\text{cand\_obs}}=5, K_{\text{cand\_lrn}}=10, K_{\text{arb}}=5, K_{\text{rec\_lrn}}=10, K_{\text{rec\_fwd}}=1$.
- Recurrent Cost: $20.200000	ext{ FP/step}$.
- Total Online Compute: $111.013591	ext{ FP/step}$.

### 2.2 Global Behavioral Reference ($R_0$)
- Model: Continuous $T_3$ Reference (dense $5 \times 32$ correlation grid, continuous shadow $K=1$).
- Status: $M_1^*$ currently fails predictive non-inferiority vs $R_0$ ($\Delta \text{NMSE} = +0.013027$, upper 95% CI $= +0.019402 > +0.0100$).
- Limit: This study CANNOT claim integrated validation unless $R_0$ non-inferiority is independently passed.

### 2.3 Candidate Arms Under Study
- **$C_1$ ($K_{\text{rec\_state}} = 5$):** Decimate recurrent forward propagation to $K=5$; retain $K_{\text{rec\_learn}} = 10$; skip semantics = `HOLD_STATE`.
- **$C_2$ ($K_{\text{rec\_state}} = 2$, DEV screening only):** Decimate recurrent forward propagation to $K=2$; retain $K_{\text{rec\_learn}} = 10$; skip semantics = `HOLD_STATE`.

### 2.4 Strict Invariants
1. Search frontier parameters strictly frozen: $H=32, B=4, K_{\text{probe}}=2$.
2. Candidate probation strictly frozen: $T_{\text{prob}}=15$ shadow observations, $\theta_{\text{promote}}=0.02, \theta_{\text{tol}}=0.015$.
3. Recurrent learning clock strictly frozen: $K_{\text{rec\_learn}}=10$.
4. No residual autocorrelation sentinels or adaptive event routers.
5. Zero privileged access to task IDs, true regimes, change points, or future samples.
6. Canonical `src/` and `tests/` remain 100% immutable.
