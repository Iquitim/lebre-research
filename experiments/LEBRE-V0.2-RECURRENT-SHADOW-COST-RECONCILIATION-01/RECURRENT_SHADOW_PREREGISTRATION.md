# Preregistration: Recurrent-Shadow Cost Reconciliation & Conditional Revalidation

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Date:** September 22, 2026  

---

## 1. Preregistered Hypotheses

- **H1 (Mathematical Resource Feasibility):** Under exact atomic operation accounting, reducing recurrent forward state cadence to $K_{\text{rec\_state}} = 5$ recovers at least $14.40	ext{ FP/step}$, driving total $M_1^*$ compute below $100.0	ext{ FP/step}$ ($96.61	ext{ FP/step}$ projected).
- **H2 (Resource Inadequacy of K=2):** Reducing recurrent state cadence to $K_{\text{rec\_state}} = 2$ saves only $9.00	ext{ FP/step}$, leaving total compute at $102.01	ext{ FP/step} > 100.0	ext{ FP/step}$ (FAILS resource gate).
- **H3 (Local Predictive Non-Inferiority):** In confirmatory evaluation on $N=30$ seeds ($1911..1940$), $C_1$ ($K=5$) preserves aggregate predictive fidelity vs causal parent $C_0$ within the frozen margin $\epsilon = +0.0100$ (one-sided 95% upper confidence bound $< +0.0100$).
- **H4 (Continuous Latent & Quiescent Preservation):** $C_1$ preserves continuous latent tracking on $I_6$ and quiescent retention on $I_7$ within the practical margin.
- **H5 (Hybrid & Switching Preservation):** $C_1$ preserves hybrid dual complementarity on $I_9$ ($G_{D|B+R} > 0, G_{R|B+D} > 0$) and directional regime recovery latency on $I_{11}, I_{12}, I_{14}$ within $\le +50$ steps.

---

## 2. Preregistered Success Criteria

The experimental candidate $C_1$ is declared **SUPPORTED** if and only if ALL of the following 10 conditions are met:
1. Mean total online compute $\le 100.000000	ext{ FP/step}$.
2. Local aggregate non-inferiority vs $C_0$ passes: $\Delta \text{NMSE}_{95\%\text{ upper}} < +0.0100$.
3. $I_6$ and $I_7$ continuous latent performance preserved.
4. $I_9$ hybrid complementarity preserved ($G_{D|B+R} > 0$ and $G_{R|B+D} > 0$).
5. Directional switching recovery criteria preserved on $I_{11}, I_{12}, I_{14}$.
6. Quiescent retention preserved on $I_7$.
7. Zero numerical instability, overflow, or NaN events.
8. Complete operation ledger reconciles to $20.200000	ext{ FP/step}$ within numerical tolerance.
9. No privileged runtime regime or task information used.
10. Canonical `src/` and `tests/` remain 100% untouched.
