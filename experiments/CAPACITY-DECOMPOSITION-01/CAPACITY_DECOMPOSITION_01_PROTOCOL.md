# CAPACITY-DECOMPOSITION-01: Preregistered Experimental Protocol

**Stage:** CAPACITY-DECOMPOSITION-01 — Causal Capacity Decomposition  
**Protocol Version:** 1.0.0 (Preregistered before final evaluation)  
**Date:** 2026-09-19  
**Lead Auditor:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, Dynamical Systems Reviewer  
**Core Invariants:**
- `ARCHITECTURE = LEBRE`
- `FROZEN_SPEC_VERSION = 0.1` (`FROZEN_WITH_SCOPE_LIMITS`)
- `LEBRE_V0_1_FORMALLY_FROZEN = YES`
- `BENCH_01B_STATUS = SEALED`
- `LEBRE_DIAG_01_STATUS = COMPLETE`
- `PROMOTION_POLICY_01_STATUS = COMPLETE`
- `M3_STATUS = UNOPENED`
- `NOVELTY_CLAIM_READY = NO`
- Codebase bitwise immutability: `src/` and `tests/` remain untouched (124/124 tests pass).

---

## 1. Experimental Variants Across the 7-Level Ladder

### Level 0: Frozen References
1. `B0_LEBRE_FROZEN` (Canonical frozen Track-B v0.1)
2. `B1_NO_REC_BIRTH` (Causal zero-recurrence baseline)
3. `B2_FIXED_STRICT` (Promotion policy successor with $\theta_{\text{promote}} = 0.15$)

### Level 1: Estimator Sufficiency (Features: $x_t$ only)
4. `E0_NLMS` (Current frozen linear learner on $x_t$)
5. `E1_RLS` (Online Recursive Least Squares, $\lambda=0.999$)
6. `E2_REG_RLS` (Regularized RLS, $\delta=1.0, \lambda=0.999$)
7. `E3_OLS_ORACLE` (Offline Ordinary Least Squares oracle, non-causal ceiling)
8. `E4_RIDGE_ORACLE` (Offline Ridge regression oracle, non-causal ceiling)

### Level 2: Finite Temporal Representation (Delay Coordinates)
9. `T0_LAG_0` ($x_t$, identical to $E0$)
10. `T1_LAG_1` ($[x_t, x_{t-1}]$)
11. `T2_LAG_2` ($[x_t, x_{t-1}, x_{t-2}]$)
12. `T3_LAG_4` ($[x_t, \dots, x_{t-4}]$ — directly spans Task A2 delay $\tau=4$)
13. `T4_LAG_8` ($[x_t, \dots, x_{t-8}]$ — directly spans Task A3 delay $\tau=8$)
14. `T5_SPARSE_LAGS` ($[x_t, x_{1, t-4}, x_{1, t-8}, x_{1, t-30}]$ — spans A4 delay $\tau=30$)

### Level 3: Static Nonlinearity Controls (Features: $x_t$ only, No Memory)
15. `NL1_POLY2` (Degree-2 polynomial expansion on top PCA features)
16. `NL2_RFF` (Random Fourier Features, $K=50$ basis projections)
17. `NL3_MLP` (Online shallow feedforward network, 16 hidden units)

### Level 4: Temporal + Nonlinear Controls
18. `TNL1_LAG4_RFF` (Lag-4 delay coordinate + RFF nonlinear projection)

### Level 5 & 6: Recurrent Necessity & State Dimension Scaling
19. `REC_N1` (1-state scalar recurrence, diagonal RTRL)
20. `REC_N2` (2-state coupled recurrence, complex-conjugate eigenvalue support)
21. `REC_N4` (4-state coupled recurrence)

### Auxiliary Audits:
- Normalization Audit: `NORM0` (Causal Online), `NORM1` (Warm-up Frozen), `NORM2` (Static Dev), `NORM3` (Full-Stream Oracle).
- Interference Audit: `I0` (Live Comparator), `I1` (Snapshot Comparator at Candidate Birth).

---

## 2. Workload & Seed Discipline

### Workloads (6 Tasks):
- **Negative Controls (A2–A4):**
  - `A2_Single_Delayed_Dependency` ($y_t = 0.8 x_{1, t-4} + \epsilon_t$)
  - `A3_Multiple_Dispersed_Delays` ($y_t = 0.5 x_{1, t-2} + 0.5 x_{2, t-8} + \epsilon_t$)
  - `A4_Long_Delay_Scaling` ($y_t = 0.8 x_{1, t-30} + \epsilon_t$)
- **Positive Controls (A5, A7):**
  - `A5_Set_Reset_Quiescent_Memory` (Bistable latch under sparse Poisson triggers)
  - `A7_Extended_Poisson_Quiescence` (Extended quiescent memory retention)
- **Neutral Transition Control (A8):**
  - `A8_Abrupt_Tri_Regime_Transition` (Linear $\to$ Lag $\to$ Recurrent)

### Seed Separation:
- **Development Seeds ($N=10$, seeds `501` through `510`):**
  - Used strictly for sanity checks, numerical stability, and parameter verification.
- **Confirmatory Evaluation Seeds ($N=30$, seeds `601` through `630`):**
  - Completely fresh, untouched seeds.
  - Paired sample-for-sample across all evaluated variants and tasks.

---

## 3. Primary Metrics & Gap Decomposition

1. **Normalized Mean Squared Error (NMSE):**
   $$\text{NMSE} = \frac{\text{MSE}}{\operatorname{var}(y_{\text{test}}) + 10^{-6}} \quad (t \ge 0.30 T)$$
2. **Diagnostic Gap Contributions (Directional $\Delta$ NMSE):**
   - $G_{\text{estimation}} = \text{NMSE}(E0) - \text{NMSE}(E1)$ (Gain from exact recursive least-squares on $x_t$)
   - $G_{\text{temporal}} = \text{NMSE}(E0) - \text{NMSE}(T3)$ (Gain from explicit finite delay coordinates)
   - $G_{\text{nonlinear}} = \text{NMSE}(E0) - \text{NMSE}(NL2)$ (Gain from static nonlinear basis expansion)
   - $G_{\text{temporal\_nonlinear}} = \text{NMSE}(T3) - \text{NMSE}(TNL1)$ (Marginal nonlinear gain over pure lags)
   - $G_{\text{recurrent}} = \text{NMSE}(\text{BestNonRec}) - \text{NMSE}(REC\_N1)$ (Incremental gain from recurrence)
   - $G_{\text{dimension}} = \text{NMSE}(REC\_N1) - \text{NMSE}(REC\_N2)$ (Gain from multi-state capacity)
3. **Residual Diagnostics:**
   - Residual Autocorrelation Function (ACF) up to lag $k=35$.
   - Cross-correlation between residual $e_t$ and input features $x_{i, t-\tau}$.
4. **Computational Rent Accounting:**
   - Mean FLOPs/step, Peak FLOPs, Persistent memory (bytes), Trainable parameters.

---

## 4. Decision Tree & Scientific Rules (Cases A through H)

1. **CASE A (Estimator Limited):** If $G_{\text{estimation}}$ closes $>70\%$ of the gap on A2–A4 $\to$ `LINEAR_REPRESENTATION_SUFFICIENT_ESTIMATOR_LIMITED`.
2. **CASE B (Finite Memory Limited):** If $G_{\text{temporal}}$ closes $>70\%$ of the gap on A2–A4 without recurrence $\to$ `FINITE_TEMPORAL_REPRESENTATION_DEFICIT`.
3. **CASE C (Static Nonlinearity Limited):** If $G_{\text{nonlinear}}$ closes $>70\%$ of the gap without lags $\to$ `STATIC_NONLINEAR_REPRESENTATION_DEFICIT`.
4. **CASE D (Finite Nonlinear Temporal Sufficient):** If $TNL1$ resolves the task without recurrent state $\to$ `FINITE_NONLINEAR_TEMPORAL_REPRESENTATION_SUFFICIENT`.
5. **CASE E (Recurrent State Necessary):** Only if recurrent models strictly outperform strong estimator-matched, lagged, and nonlinear controls on positive controls $\to$ `EVIDENCE_FOR_GENUINE_RECURRENT_STATE_REQUIREMENT`.
6. **CASE F (Scalar Recurrence Limited):** Only if recurrence is proven necessary AND $N > 1$ materially outperforms $N=1$ on the Pareto frontier $\to$ `EVIDENCE_FOR_SCALAR_RECURRENT_CAPACITY_LIMIT`.
7. **CASE G (Adaptive Interference Dominated):** If $I1$ removes candidate error/churn $\to$ `ADAPTIVE_COMPARATOR_INTERFERENCE`.
8. **CASE H (Unresolved):** If no clean mechanism dominates $\to$ `CAPACITY_DEFICIT_REMAINS_UNRESOLVED`.

---

## 5. Statistical Analysis Plan

- Paired analysis across 30 seeds.
- 95% bootstrap confidence intervals (10,000 resamples).
- Paired Cohen's $d_z$ effect sizes and seed win rates.
- Holm-Bonferroni family-wise error rate control.

---

## 6. Preregistration Cryptographic Seal

- **Protocol Hash (SHA-256):** `2e17688ffbe7940f5c17902aebf29558ddc5f2dc8e7f20f12c9123acff5ae9bd`
- **Timestamp:** 2026-09-19T22:16:24-03:00
- **Status:** SEALED BEFORE CONFIRMATORY RUNS

