# Preregistration: K=2 Recurrent-State Boundary Confirmatory Validation

**Study ID:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Date:** September 2026  

---

## 1. Preregistered Hypotheses

- **H1 (Primary Predictive Non-Inferiority):** In fresh-seed confirmatory evaluation ($N=30$ independent seeds $1941..1970$), candidate $C_2$ ($K_{\text{rec\_forward}}=2$) preserves aggregate predictive fidelity vs concurrent parent $C_0$ within the practical non-inferiority margin:
  $$\text{Upper 95\% CI on } \Delta \text{NMSE}(C_2 - C_0) < +0.0100$$
- **H2 (Critical Continuous-Latent Tracking):** $C_2$ preserves continuous latent tracking on $I_6$ and quiescent latent decay/retention on $I_7$ within a practical task-level degradation ceiling $\Delta \text{NMSE} \le +0.0100$.
- **H3 (Hybrid Dual Complementarity):** On task $I_9$, $C_2$ preserves positive dual conditional gains:
  $$G_{D|B+R} > 0 \quad \text{and} \quad G_{R|B+D} > 0$$
- **H4 (Directional Regime Switching Recovery):** $C_2$ preserves directional recovery latencies on $I_{11}, I_{12}, I_{13}, I_{14}$ within $\le +50\text{ stream steps}$ of concurrent $C_0$.
- **H5 (State Trajectory Continuity):** Decimating recurrent state propagation to $K=2$ produces mild, bounded path distortion without causing catastrophic phase lag.

---

## 2. Resource Adjudication Framework

1. **Strict Target Gate:** Mean Total Online Compute $\le 100.000000\text{ FP/step}$.
2. **Near-Miss Engineering Interval:** $100.000000 < \text{Mean Total Compute} \le 101.000000\text{ FP/step}$.
   - A near-miss within $\le 101.0\text{ FP}$ establishes eligibility for a future minimal-composition study.
   - It does NOT convert a resource FAIL into a resource PASS.
3. **Resource Fail:** Mean Total Compute $> 101.000000\text{ FP/step}$.

---

## 3. Preregistered Decision Outcomes

- **`K2_BOUNDARY_CONFIRMED_AND_RESOURCE_PASS`:** H1–H5 pass AND Mean Total FP $\le 100.0$.
- **`K2_BOUNDARY_CONFIRMED_RESOURCE_NEAR_MISS`:** H1–H5 pass AND $100.0 < \text{Mean Total FP} \le 101.0$.
- **`K2_BEHAVIORAL_NONINFERIORITY_FAILED`:** Primary upper 95% CI $\ge +0.0100$.
- **`K2_CRITICAL_TEMPORAL_MECHANISM_FAILED`:** H1 passes, but $I_6, I_7, I_9$, or switching fails.
- **`K2_STRUCTURAL_DISTORTION`:** Recurrent promotions collapse, causing pathological undermodeling.
- **`K2_RESOURCE_NOT_NEAR_MISS`:** Behavioral gates pass, but compute $> 101.0\text{ FP/step}$.
