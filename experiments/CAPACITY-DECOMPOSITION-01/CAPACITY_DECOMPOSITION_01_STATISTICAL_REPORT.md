# CAPACITY-DECOMPOSITION-01: Confirmatory Statistical Report

**Stage:** CAPACITY-DECOMPOSITION-01 — Causal Capacity Decomposition  
**Seeds:** EVAL seeds 601..630 ($N=30$, paired sample-for-sample across all variants)  
**Bootstrap Iterations:** 10,000 resamples  

---

## 1. Key Paired Hypothesis Tests

### Test 1: Estimator Sufficiency on Instantaneous $x_t$ (H1)
- $E0$ (NLMS on $x_t$) NMSE: **1.0593** [1.059, 1.060]
- $E1$ (RLS on $x_t$) NMSE: **1.0104** [1.010, 1.011]
- $E3$ (OLS Oracle on $x_t$) NMSE: **0.9973** [0.997, 0.997]
- **Finding:** Even with an offline least-squares oracle ($E3$) eliminating 100% of estimator variance, NMSE on A2–A4 remains **0.9998** ($pprox 1.000$).
- **Conclusion on H1:** **DECISIVELY REFUTED**. The linear hypothesis class on $x_t$ cannot predict delayed targets. The deficit is not an estimator problem.

### Test 2: Finite Temporal Representation (H2)
- On A2 (Single Delay $	au=4$):
  - $T0$ ($x_t$) NMSE: **1.115**
  - $T3$ (Lag 4) NMSE: **0.364** (drops by -0.751, $p < 10^-12$, win rate 30/30)
- On A3 (Dispersed Delays $	au=2, 8$):
  - $T0$ ($x_t$) NMSE: **1.114**
  - $T4$ (Lag 8) NMSE: **0.361** (drops by -0.753, $p < 10^-12$, win rate 30/30)
- On A4 (Long Delay $	au=30$):
  - $T0$ ($x_t$) NMSE: **1.115**
  - $T5$ (Sparse Lag $t-30$) NMSE: **0.363** (drops by -0.752, $p < 10^-12$, win rate 30/30)
- **Conclusion on H2:** **DECISIVELY SUPPORTED**. Explicit finite delay coordinates completely resolve the task, dropping error to the theoretical Bayes noise floor (NMSE ~ 0.36).

### Test 3: Static Nonlinearity (H3)
- $NL2$ (RFF on $x_t$) NMSE: **1.0533** (remains $> 1.00$)
- $NL3$ (Online MLP on $x_t$) NMSE: **1.0077** (remains $> 1.00$)
- **Conclusion on H3:** **DECISIVELY REFUTED**. Static nonlinear mapping without memory provides zero predictive advantage on delayed streams.

### Test 4: Recurrent Necessity (H5) vs Recurrent Dimension (H6)
- On A5/A7 (Positive Controls):
  - $B1$ (NoRec) NMSE: **1.0501**
  - $REC\_N1$ (Scalar Recurrence) NMSE: **0.8654** ($\Delta = -0.1847, p < 10^-8$)
  - $REC\_N2$ (2-State Recurrence) NMSE: **0.8521** ($\Delta = -0.0133$, small gain)
  - $REC\_N4$ (4-State Recurrence) NMSE: **0.8490** ($\Delta = -0.0164$, small gain)
- On A2–A4 (Negative Controls):
  - $REC\_N1$ NMSE: **1.144**
  - $REC\_N2$ NMSE: **1.141** (remains $> 1.10$)
  - $REC\_N4$ NMSE: **1.138** (remains $> 1.10$)
- **Conclusion:** Recurrence is **necessary for continuous dynamical states (A5/A7)**, but **dense recurrence fails to solve pure discrete shift-register delays (A2–A4)** without explicit lag coordinates. Expanding $N=1 	o N=2, 4$ fails to solve discrete delay lines while doubling/quadrupling FLOP costs.
