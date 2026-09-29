# CAPACITY-DECOMPOSITION-01: Formal Hypotheses & Causal Falsification Matrix

**Stage:** CAPACITY-DECOMPOSITION-01 — Causal Capacity Decomposition  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Purpose:** Formal preregistration of competing scientific hypotheses H1 through H7, their mathematical formulations, predicted consequences, and decisive falsification criteria.

---

## 1. Primary Hypothesis Formulations

### Hypothesis H1: Estimator-Limited Linear Baseline
- **Mathematical Statement:** The target $y_t$ lies in the linear span of the current observation vector $\mathbf{x}_t$, i.e., $y_t = \mathbf{w}_*^T \mathbf{x}_t + \epsilon_t$, but the online stochastic gradient (NLMS) estimator produces excessive parameter variance or slow tracking error: $\mathbb{E}[\|\mathbf{w}_t - \mathbf{w}_*\|^2] \gg 0$.
- **Experimental Test:** Compare frozen linear NLMS ($E0$) against online Recursive Least Squares ($E1$) and offline ordinary least squares oracle ($E3$) operating on **identical feature inputs** $\mathbf{x}_t$.
- **Predicted Consequence if H1 is TRUE:** $E1$ and $E3$ achieve $\text{NMSE} \ll 1.0$ on A2–A4 (e.g., $\text{NMSE} < 0.50$), closing $>70\%$ of the gap without adding temporal or nonlinear features.
- **Falsification Criterion:** If $E3$ (offline least squares oracle with zero estimation variance) achieves $\text{NMSE} \approx 1.00$ on A2–A4, H1 is **DECISIVELY REFUTED**. The linear representation on $\mathbf{x}_t$ is mathematically incapable of predicting the target regardless of estimator quality.

---

### Hypothesis H2: Finite Temporal Information Deficit (Delay Coordinates)
- **Mathematical Statement:** The target depends on past observations of the input stream, $y_t = f(x_{1, t-\tau_1}, x_{2, t-\tau_2}, \dots) + \epsilon_t$, which are absent from the instantaneous vector $\mathbf{x}_t$. The missing information is finite and fully captured by explicit delay coordinates:
  $$\mathbf{z}_t = [\mathbf{x}_t^T, \mathbf{x}_{t-1}^T, \dots, \mathbf{x}_{t-L}^T]^T$$
- **Experimental Test:** Measure the marginal performance gain as explicit lag embedding depth is expanded: $T0$ ($\mathbf{x}_t$) vs $T1$ ($L=1$) vs $T2$ ($L=2$) vs $T3$ ($L=4$) vs $T4$ ($L=8$) vs $T5$ (targeted sparse lags).
- **Predicted Consequence if H2 is TRUE:** Inclusion of the true causal lag (e.g., $L \ge 4$ for A2, $L \ge 8$ for A3, sparse lag $30$ for A4) drops NMSE towards optimal Bayes error ($\text{NMSE} \approx \sigma_\epsilon^2 / \operatorname{var}(y) \approx 0.36$) without learned recurrent state.
- **Falsification Criterion:** If explicit finite delay coordinates do not improve performance, or if NMSE remains $\approx 1.115$ even when causal lags are supplied to the linear estimator, H2 is **REFUTED**.

---

### Hypothesis H3: Static Nonlinearity Deficit (Memoryless Nonlinear Expansion)
- **Mathematical Statement:** The target depends nonlinearly on instantaneous features, $y_t = g(\mathbf{x}_t) + \epsilon_t$, but requires no past temporal memory.
- **Experimental Test:** Evaluate static nonlinear feature expansions on $\mathbf{x}_t$ alone (Polynomial expansion $NL1$, Random Fourier Features $NL2$, diagnostic shallow MLP $NL3$) with zero lagged inputs and zero recurrent state.
- **Predicted Consequence if H3 is TRUE:** $NL2$ or $NL3$ substantially closes the A2–A4 deficit, while lag features ($T1$–$T5$) provide negligible marginal gain.
- **Falsification Criterion:** If static nonlinear expansions on $\mathbf{x}_t$ achieve $\text{NMSE} \ge 1.00$ while lag representations succeed, H3 is **DECISIVELY REFUTED**.

---

### Hypothesis H4: Finite Nonlinear Temporal Representation Sufficiency
- **Mathematical Statement:** The target requires both finite memory and nonlinear mapping, $y_t = g(\mathbf{x}_t, \mathbf{x}_{t-1}, \dots, \mathbf{x}_{t-L}) + \epsilon_t$, but does not require an infinite-impulse recurrent state space.
- **Experimental Test:** Evaluate a combined model with finite delay coordinates and static Random Fourier Features ($TNL1$) against pure lag models and recurrent models.
- **Predicted Consequence if H4 is TRUE:** $TNL1$ matches or outperforms recurrent architectures without learned feedback dynamics.
- **Falsification Criterion:** If recurrent state strictly outperforms $TNL1$ on tasks with genuine temporal feedback (A5/A7), finite representations are insufficient for continuous dynamical memory.

---

### Hypothesis H5: Genuine Recurrent Memory Requirement
- **Mathematical Statement:** The task requires continuous dynamical state integration across indefinite or variable durations (e.g., quiescent bistable latches, long-tail Poisson memory) that cannot be represented by bounded-length finite lag buffers without exponential parameter explosion.
- **Experimental Test:** Compare matched estimator baselines against a scalar recurrent state ($N=1$) on positive controls A5 (Bistable Latch) and A7 (Poisson Quiescence).
- **Predicted Consequence if H5 is TRUE:** Recurrent state achieves massive, statistically significant error reductions over estimator-matched non-recurrent controls on A5 and A7.
- **Falsification Criterion:** If finite lag buffers ($T3/T4$) achieve equal or lower NMSE than recurrence on A5/A7 at comparable or lower resource cost, H5 is **REFUTED**.

---

### Hypothesis H6: Scalar Recurrence Dimension Limit ($N \le 1$ Capacity Ceiling)
- **Mathematical Statement:** Recurrent memory is necessary, but a 1-dimensional scalar state ($s_t = \lambda s_{t-1} + \mathbf{w}^T \mathbf{x}_t$) has a strictly monotonic, first-order impulse response $h[k] = w \lambda^k$, making it mathematically incapable of creating a transfer function peak at delay $\tau > 1$. Multi-dimensional recurrence ($N \ge 2$) is required to support complex conjugate poles or orthogonal state manifolds.
- **Experimental Test:** Evaluate recurrent state dimension scaling: $N=1$ vs $N=2$ vs $N=4$ under matched online RTRL updates, with strict cost-performance accounting.
- **Predicted Consequence if H6 is TRUE:** $N=2$ or $N=4$ significantly improves performance on delayed or oscillatory tasks over $N=1$, and this advantage survives resource rent accounting.
- **Falsification Criterion:** If $N=2$ and $N=4$ fail to improve NMSE over $N=1$ on delayed streams, or if their marginal FLOP/memory cost exceeds their predictive gain, H6 is **REFUTED / UNJUSTIFIED**.

---

### Hypothesis H7: Normalization Dynamics & Comparator Interference
- **Mathematical Statement:** The residual deficit or false-promotion rate is amplified by artifacts of online causal normalization (running mean/variance drift) or adaptive comparator interference (moving baseline during candidate probation).
- **Experimental Test:**
  - Normalization Audit: Compare frozen causal normalization ($NORM0$) against warm-up frozen ($NORM1$), static statistics ($NORM2$), and full-stream oracle normalization ($NORM3$).
  - Interference Audit: Compare live baseline comparator ($I0$) against a frozen snapshot of the baseline taken at candidate birth ($I1$).
- **Predicted Consequence if H7 is TRUE:** $NORM3$ or $I1$ substantially reduces residual variance or eliminates false candidate births.
- **Falsification Criterion:** If $NORM1$–$NORM3$ and $I1$ yield statistically indistinguishable NMSE and candidate behavior compared to $NORM0$ and $I0$, H7 is **REFUTED**.

---

## 2. Summary Falsification Matrix

| Hypothesis | Test Variant | Primary Metric | Expected if TRUE | Expected if FALSE | Decisive Falsification Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **H1 (Estimator)** | $E1$ (RLS), $E3$ (OLS) | NMSE on A2–A4 | NMSE $< 0.50$ | NMSE $\approx 1.00$ | $E3 \text{ NMSE} \ge 0.95$ |
| **H2 (Finite Lags)** | $T1$–$T5$ (Lags) | $\Delta$ NMSE vs $T0$ | NMSE drops toward $0.36$ | NMSE remains $\approx 1.115$ | $T3 \text{ NMSE} \ge 0.95$ |
| **H3 (Nonlinearity)** | $NL1, NL2$ (RFF) | NMSE on A2–A4 | NMSE $< 0.60$ on $x_t$ | NMSE $\ge 1.00$ on $x_t$ | $NL2 \text{ NMSE} \ge 0.95$ |
| **H4 (Finite Nonlin)** | $TNL1$ (Lag+RFF) | NMSE on A5/A7 | Outperforms RNN | Fails on long gaps | $TNL1 \text{ NMSE} > \text{REC}$ on A7 |
| **H5 (Recurrence)** | $REC\_N1$ | Paired $\Delta$ on A5/A7 | $\text{NMSE} \ll \text{NonRec}$ | No gain over Lags | $\text{REC} \ge \text{NonRec}$ on A5/A7 |
| **H6 ($N > 1$)** | $REC\_N2, REC\_N4$ | NMSE & FLOP Pareto | $N \ge 2$ wins on Pareto | $N \ge 2$ dominated | $N=2 \text{ gain} \le 0.01$ |
| **H7 (Artifacts)** | $NORM3, I1$ | Variance & Churn | Drastic reduction | Statistically neutral | Paired $p > 0.05$ |
