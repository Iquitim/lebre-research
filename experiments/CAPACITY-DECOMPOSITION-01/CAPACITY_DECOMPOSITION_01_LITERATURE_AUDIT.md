# CAPACITY-DECOMPOSITION-01: Formal Literature Audit
## Representational Sufficiency, Temporal Information, Estimator Dynamics & Recurrent Capacity

**Stage:** CAPACITY-DECOMPOSITION-01 — Causal Capacity Decomposition  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Auditor:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, Dynamical Systems Reviewer  

---

## 1. Executive Scientific Framing

Following the findings of `LEBRE-DIAG-01` and `PROMOTION-POLICY-01`, LEBRE exhibits a persistent residual predictive deficit on delayed dependency tasks (**A2**, **A3**, **A4**), achieving $\text{NMSE} \approx 1.115$ to $1.127$ even when spurious candidate promotions are suppressed or eliminated. To prevent ungrounded architectural speculation, this audit reviews the foundational literature across six distinct domains to establish the causal boundaries between:
1. **Estimation Quality** (LMS/SGD gradient noise vs exact least-squares tracking);
2. **Instantaneous Feature Representation** (current inputs $x_t$ vs nonlinear basis expansion);
3. **Finite Temporal Delay Coordinates** (explicit finite lag embeddings $x_{t-\tau}$);
4. **Infinite-Impulse Recurrent State Space** (continuous hidden dynamical states $s_t$);
5. **Continuous Streaming Constraints** (zero replay, zero offline batch retuning, causal prequential ordering).

---

## 2. Itemized Method-by-Method Audit Across 6 Families

### Family A: Prequential & Interleaved Test-Then-Train Evaluation

#### Paper A1: Dawid (1984) — The Prequential Approach
- **REFERENCE:** Dawid, A. P. (1984). *Present position and potential developments: Some personal views: Statistical theory: The prequential approach*. Journal of the Royal Statistical Society: Series A, 147(2), 278–292. [DOI: 10.2307/2981683](https://doi.org/10.2307/2981683).
- **YEAR:** 1984
- **PROBLEM SETTING:** Sequential streaming forecast evaluation without train/test data leakage.
- **STATIC / STREAMING / CONTINUAL:** Streaming.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** General sequential probability forecast.
- **ESTIMATOR TYPE:** Any causal sequential estimator.
- **MEMORY MECHANISM:** Unspecified.
- **STRUCTURAL GROWTH MECHANISM:** None (evaluation framework).
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(1)$ per evaluation step.
- **PERSISTENT MEMORY COST:** $\mathcal{O}(1)$ loss accumulator.
- **ASSUMPTIONS:** Forecasts are generated strictly using the filtration $\mathcal{F}_{t-1}$ prior to observing $y_t$.
- **DIRECTLY APPLICABLE TO LEBRE?** YES.
- **WHY INCLUDED:** Establishes the non-negotiable evaluation discipline: $\text{Predict} \to \text{Reveal Target} \to \text{Record Loss} \to \text{Update}$.
- **WHY NOT DIRECTLY IMPORTED:** It is a methodological principle, not an estimation algorithm.

#### Paper A2: Gama, Sebastião, & Rodrigues (2013) — On Evaluating Stream Learning Algorithms
- **REFERENCE:** Gama, J., Sebastião, R., & Rodrigues, P. P. (2013). *On evaluating stream learning algorithms*. Machine Learning, 90(3), 317–346. [DOI: 10.1007/s10994-012-5320-9](https://doi.org/10.1007/s10994-012-5320-9).
- **YEAR:** 2013
- **PROBLEM SETTING:** Prequential error tracking and fading factors in non-stationary data streams.
- **STATIC / STREAMING / CONTINUAL:** Continual Streaming.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Evolving feature streams.
- **ESTIMATOR TYPE:** Online adaptive classifiers/regressors.
- **MEMORY MECHANISM:** Sliding windows / fading factors.
- **STRUCTURAL GROWTH MECHANISM:** Drift detection triggers.
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(1)$ per step.
- **PERSISTENT MEMORY COST:** Bounded decaying statistics.
- **ASSUMPTIONS:** Loss distribution reflects underlying concept stability or drift.
- **DIRECTLY APPLICABLE TO LEBRE?** YES.
- **WHY INCLUDED:** Justifies LEBRE's prequential evaluation window and sliding evaluation statistics.
- **WHY NOT DIRECTLY IMPORTED:** Evaluates classification trees; LEBRE operates on continuous regression.

---

### Family B: Adaptive Filtering & Online System Identification

#### Paper B1: Widrow & Hoff (1960) / Widrow & Stearns (1985) — Adaptive Signal Processing (LMS/NLMS)
- **REFERENCE:** Widrow, B., & Stearns, S. D. (1985). *Adaptive Signal Processing*. Prentice-Hall.
- **YEAR:** 1985
- **PROBLEM SETTING:** Stochastic gradient descent on instantaneous squared error with normalized step size (NLMS).
- **STATIC / STREAMING / CONTINUAL:** Streaming.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Linear transversal filter $\hat{y}_t = \mathbf{w}_t^T \mathbf{x}_t$.
- **ESTIMATOR TYPE:** Normalized Least Mean Squares (NLMS).
- **MEMORY MECHANISM:** Direct parameter adaptation.
- **STRUCTURAL GROWTH MECHANISM:** None (fixed dimension $D$).
- **COMPUTATIONAL COMPLEXITY:** $2D$ additions, $2D$ multiplications per step ($\mathcal{O}(D)$).
- **PERSISTENT MEMORY COST:** $D \times 8$ bytes for weights.
- **ASSUMPTIONS:** Step size $\mu$ chosen within stability bound $0 < \mu < 2 / \|\mathbf{x}_t\|^2$.
- **DIRECTLY APPLICABLE TO LEBRE?** YES (matches LEBRE's core linear component).
- **WHY INCLUDED:** Baseline reference estimator $E0$.
- **WHY NOT DIRECTLY IMPORTED:** Already forms the base linear learner of LEBRE v0.1.

#### Paper B2: Haykin (2002) / Sayed (2003) — Recursive Least Squares (RLS)
- **REFERENCE:** Haykin, S. (2002). *Adaptive Filter Theory* (4th ed.). Prentice Hall; Sayed, A. H. (2003). *Fundamentals of Adaptive Filtering*. John Wiley & Sons.
- **YEAR:** 2002 / 2003
- **PROBLEM SETTING:** Deterministic recursive minimization of weighted least-squares objective with forgetting factor $\lambda \in (0, 1]$.
- **STATIC / STREAMING / CONTINUAL:** Streaming.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Linear feature vector $\mathbf{x}_t \in \mathbb{R}^D$.
- **ESTIMATOR TYPE:** Recursive Least Squares (RLS) tracking inverse covariance matrix $\mathbf{P}_t = (\sum_{i=1}^t \lambda^{t-i} \mathbf{x}_i \mathbf{x}_i^T + \delta \lambda^t \mathbf{I})^{-1}$.
- **MEMORY MECHANISM:** Covariance matrix $\mathbf{P}_t$.
- **STRUCTURAL GROWTH MECHANISM:** None.
- **COMPUTATIONAL COMPLEXITY:** $4D^2 + 4D$ FLOPs per step ($\mathcal{O}(D^2)$).
- **PERSISTENT MEMORY COST:** $D^2 \times 8$ bytes for $\mathbf{P}_t$ + $D \times 8$ bytes for $\mathbf{w}_t$.
- **ASSUMPTIONS:** Persistent excitation of input sequence; positive-definite inverse covariance matrix.
- **DIRECTLY APPLICABLE TO LEBRE?** PARTIAL (scientific diagnostic oracle $E1$, but exceeds R2-FLOP and memory envelopes if $D$ is large).
- **WHY INCLUDED:** Discriminates between *estimator variance/convergence noise* and *representational insufficiency*.
- **WHY NOT DIRECTLY IMPORTED:** At $D=20$, $\mathbf{P}_t$ requires 400 floats (3,200 bytes) and $\approx 1,600$ FLOPs/step, violating LEBRE's $\le 100$ FLOP and $\le 1024$ byte budget.

---

### Family C: Delay-Coordinate Representation & Time-Series Embedding

#### Paper C1: Takens (1981) / Packard et al. (1980) — Detecting Strange Attractors in Turbulence
- **REFERENCE:** Takens, F. (1981). *Detecting strange attractors in turbulence*. Dynamical Systems and Turbulence, Lecture Notes in Mathematics, vol 898, Springer, 366–381. [DOI: 10.1007/BFb0091924](https://doi.org/10.1007/BFb0091924); Packard, N. H. et al. (1980). *Geometry from a time series*. Physical Review Letters, 45(9), 712.
- **YEAR:** 1980 / 1981
- **PROBLEM SETTING:** Reconstructing the topology of a $d$-dimensional dynamical system attractor from sequential scalar observations.
- **STATIC / STREAMING / CONTINUAL:** Offline / Time Series.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Delay-coordinate vector $\mathbf{v}_t = [x_t, x_{t-\tau}, x_{t-2\tau}, \dots, x_{t-(2d)\tau}]^T$.
- **ESTIMATOR TYPE:** Diffeomorphic state space reconstruction.
- **MEMORY MECHANISM:** Explicit FIFO delay line (lag buffer).
- **STRUCTURAL GROWTH MECHANISM:** Embedding dimension expansion ($m \ge 2d + 1$).
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(1)$ insertion per step.
- **PERSISTENT MEMORY COST:** $m \times 8$ bytes for the circular delay buffer.
- **ASSUMPTIONS:** Autonomous, smooth, deterministic dynamical system; generic measurement function.
- **DIRECTLY APPLICABLE TO LEBRE?** PARTIAL. Motivates finite delay coordinates ($T0$–$T5$).
- **WHY INCLUDED:** Tests whether explicit finite lag coordinates resolve delayed dependencies without requiring recurrent state.
- **WHY NOT DIRECTLY IMPORTED:** Tasks A2–A4 have stochastic noise components and specific non-delay orthogonal features; Takens' theorem guarantees topological equivalence for autonomous manifolds, not optimal online predictive filters under additive white noise.

#### Paper C2: Box, Jenkins, & Reinsel (1970/2008) — Time Series Analysis: Forecasting and Control
- **REFERENCE:** Box, G. E., Jenkins, G. M., & Reinsel, G. C. (2008). *Time Series Analysis: Forecasting and Control* (4th ed.). John Wiley & Sons.
- **YEAR:** 1970 / 2008
- **PROBLEM SETTING:** Autoregressive Moving Average (ARMA) and Finite Impulse Response (FIR) modeling of stationary and non-stationary stochastic series.
- **STATIC / STREAMING / CONTINUAL:** Sequential Time Series.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Tapped delay line (FIR): $\hat{y}_t = \sum_{k=0}^p a_k x_{t-k}$.
- **ESTIMATOR TYPE:** Yule-Walker equations / recursive gradient descent.
- **MEMORY MECHANISM:** FIFO ring buffer.
- **STRUCTURAL GROWTH MECHANISM:** Order selection via AIC/BIC/MDL.
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(p)$ FLOPs per step.
- **PERSISTENT MEMORY COST:** $p \times 8$ bytes.
- **ASSUMPTIONS:** Linear shift-invariant system with finite or rational transfer function.
- **DIRECTLY APPLICABLE TO LEBRE?** YES.
- **WHY INCLUDED:** Directly provides the mathematical basis for diagnostic lag variants $T1$ through $T5$.
- **WHY NOT DIRECTLY IMPORTED:** LEBRE v0.1 was frozen with instantaneous features $x_t$ plus scalar recurrence $s_t$; lag features represent an alternate architectural axis that must be causally diagnosed.

---

### Family D: Static Nonlinear Feature Expansions

#### Paper D1: Rahimi & Recht (2007) — Random Features for Large-Scale Kernel Machines
- **REFERENCE:** Rahimi, A., & Recht, B. (2007). *Random features for large-scale kernel machines*. Advances in Neural Information Processing Systems (NeurIPS 2007), 1177–1184.
- **YEAR:** 2007
- **PROBLEM SETTING:** Approximating shift-invariant nonlinear kernel inner products via randomized cosine/sine projections.
- **STATIC / STREAMING / CONTINUAL:** Static / Streaming compatible.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Randomized basis projection $\phi(\mathbf{x}) = \sqrt{\frac{2}{D_{\text{rff}}}} \cos(\mathbf{\Omega} \mathbf{x} + \mathbf{b})$.
- **ESTIMATOR TYPE:** Linear model on projected feature space $\phi(\mathbf{x})$.
- **MEMORY MECHANISM:** NONE (strictly static, memoryless).
- **STRUCTURAL GROWTH MECHANISM:** Increasing projection dimension $D_{\text{rff}}$.
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(D \cdot D_{\text{rff}})$ for projection + $\mathcal{O}(D_{\text{rff}})$ for linear update.
- **PERSISTENT MEMORY COST:** Fixed projection matrix $\mathbf{\Omega}$ + bias $\mathbf{b}$ + linear weights $\mathbf{w}$.
- **ASSUMPTIONS:** Shift-invariant kernel (e.g., Gaussian RBF); input vector bounded.
- **DIRECTLY APPLICABLE TO LEBRE?** YES (diagnostic control $NL2$).
- **WHY INCLUDED:** Isolates *nonlinearity* from *memory*. If Random Fourier Features on $x_t$ solve A2–A4, the deficit is static nonlinearity, not temporal recurrence.
- **WHY NOT DIRECTLY IMPORTED:** Adds matrix projection compute; must be tested causally to see if nonlinearity is actually what A2–A4 lack.

---

### Family E: Recurrent Online Learning & RTRL

#### Paper E1: Williams & Zipser (1989) — Real-Time Recurrent Learning (RTRL)
- **REFERENCE:** Williams, R. J., & Zipser, D. (1989). *A learning algorithm for continually running fully recurrent neural networks*. Neural Computation, 1(2), 270–280. [DOI: 10.1162/neco.1989.1.2.270](https://doi.org/10.1162/neco.1989.1.2.270).
- **YEAR:** 1989
- **PROBLEM SETTING:** Exact online computation of gradient $\frac{\partial y_t}{\partial \mathbf{\theta}}$ forward in time without backpropagation through time (BPTT).
- **STATIC / STREAMING / CONTINUAL:** Continual Streaming.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Recurrent state vector $\mathbf{s}_t = \sigma(\mathbf{W} \mathbf{s}_{t-1} + \mathbf{U} \mathbf{x}_t)$.
- **ESTIMATOR TYPE:** Real-time gradient descent via sensitivity tensor $p_{ijk}^t = \frac{\partial s_i^t}{\partial w_{jk}}$.
- **MEMORY MECHANISM:** Recurrent dynamical state vector $\mathbf{s}_t$.
- **STRUCTURAL GROWTH MECHANISM:** None (fixed state size $N$).
- **COMPUTATIONAL COMPLEXITY:** In general fully connected RNN: $\mathcal{O}(N^4 + N^2 D)$ FLOPs per step. For LEBRE scalar recurrence ($N=1$): $\mathcal{O}(1)$ FLOPs!
- **PERSISTENT MEMORY COST:** In general: $\mathcal{O}(N^3 + N^2 D)$. For scalar $N=1$: exactly 3 scalars (24 bytes).
- **ASSUMPTIONS:** Small learning rate; stable spectral radius ($\rho(\mathbf{W}) < 1$).
- **DIRECTLY APPLICABLE TO LEBRE?** YES. LEBRE's scalar recurrence uses exact RTRL gradient tracking.
- **WHY INCLUDED:** Establishes the exact gradient mechanics of Level 5 ($N=1$) and Level 6 ($N=2, 4$).
- **WHY NOT DIRECTLY IMPORTED:** General $N \ge 4$ RTRL scales as $\mathcal{O}(N^4)$, making fully connected RTRL prohibitive for micro-edge deployment. Diagonal or block-diagonal structures are required for low FLOPs.

#### Paper E2: Jaeger (2001) — Echo State Networks (ESN) / Reservoir Computing
- **REFERENCE:** Jaeger, H. (2001). *The “echo state” approach to analysing and training recurrent neural networks-with an erratum note*. GMD Report 148, German National Research Center for Information Technology.
- **YEAR:** 2001
- **PROBLEM SETTING:** Bypassing recurrent weight training by utilizing a large, fixed, random dynamical reservoir.
- **STATIC / STREAMING / CONTINUAL:** Continual Streaming.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** High-dimensional reservoir $\mathbf{s}_t = \tanh(\mathbf{W}_{\text{res}} \mathbf{s}_{t-1} + \mathbf{W}_{\text{in}} \mathbf{x}_t)$.
- **ESTIMATOR TYPE:** Linear readout on reservoir states ($\hat{y}_t = \mathbf{w}_{\text{out}}^T \mathbf{s}_t$).
- **MEMORY MECHANISM:** Fading memory induced by reservoir dynamics with spectral radius $\rho < 1$.
- **STRUCTURAL GROWTH MECHANISM:** None (requires large fixed reservoir, typically $N=20$ to $500$).
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(N^2 + N D)$ FLOPs per step.
- **PERSISTENT MEMORY COST:** $\mathcal{O}(N^2)$ bytes for reservoir weights + $\mathcal{O}(N)$ for states.
- **ASSUMPTIONS:** Echo State Property (fading memory condition).
- **DIRECTLY APPLICABLE TO LEBRE?** Evaluated as frozen benchmark baseline (B5 in BENCH-01B).
- **WHY INCLUDED:** Confirms why BENCH-01B dense ESN ($N=20$) achieved superior performance on A2–A4, and provides context for the representational capacity of high-dimensional state spaces.
- **WHY NOT DIRECTLY IMPORTED:** Online ESN consumes 1,683 FLOPs/step and 6,112 bytes of RAM, violating micro-edge budgets by 16.8× and 6.0× respectively.

---

### Family F: Dynamic Capacity & Structural Expansion

#### Paper F1: Yoon et al. (2018) — Dynamically Expandable Networks (DEN)
- **REFERENCE:** Yoon, J., Yang, E., Lee, J., & Hwang, S. J. (2018). *Lifelong Learning with Dynamically Expandable Networks*. International Conference on Learning Representations (ICLR 2018).
- **YEAR:** 2018
- **PROBLEM SETTING:** Dynamically allocating units and layers upon task arrival when existing capacity incurs high loss.
- **STATIC / STREAMING / CONTINUAL:** Continual Learning across Tasks.
- **TASK BOUNDARIES REQUIRED?** **YES** (requires discrete task boundaries and offline retraining).
- **REPRESENTATION TYPE:** Deep feedforward network with dynamically added hidden neurons.
- **ESTIMATOR TYPE:** Batch backpropagation with group lasso regularization.
- **MEMORY MECHANISM:** Co-allocation of network parameters across tasks.
- **STRUCTURAL GROWTH MECHANISM:** Expand network width if loss on new task remains above threshold after fine-tuning.
- **COMPUTATIONAL COMPLEXITY:** High (multi-pass offline optimization per task).
- **PERSISTENT MEMORY COST:** Unbounded network growth.
- **ASSUMPTIONS:** Replay data or historical task datasets available for retraining.
- **DIRECTLY APPLICABLE TO LEBRE?** NO (LEBRE operates in a strictly online, single-pass streaming regime without task boundaries).
- **WHY INCLUDED:** Serves as the primary reference point for representation-driven structural expansion.
- **WHY NOT DIRECTLY IMPORTED:** Relies on offline task-boundary retraining and replay buffers, strictly forbidden in LEBRE.

#### Paper F2: Mocanu et al. (2018) — Dynamic Sparse Training (SET)
- **REFERENCE:** Mocanu, D. C. et al. (2018). *Scalable training of artificial neural networks with dynamic sparse training*. Nature Communications, 9(1), 2383. [DOI: 10.1038/s41467-018-04316-3](https://doi.org/10.1038/s41467-018-04316-3).
- **YEAR:** 2018
- **PROBLEM SETTING:** Continual structural adaptation via magnitude-based pruning and random/gradient-guided regrowth.
- **STATIC / STREAMING / CONTINUAL:** Continual Training.
- **TASK BOUNDARIES REQUIRED?** NO.
- **REPRESENTATION TYPE:** Sparse weight topology.
- **ESTIMATOR TYPE:** Stochastic gradient descent with periodic topology updates.
- **MEMORY MECHANISM:** Implicit in active topological graph.
- **STRUCTURAL GROWTH MECHANISM:** Prune fraction $\zeta$ of smallest weights, regrow random or gradient-aligned connections.
- **COMPUTATIONAL COMPLEXITY:** $\mathcal{O}(\text{nnz})$ FLOPs per step.
- **PERSISTENT MEMORY COST:** Sparse index representation.
- **ASSUMPTIONS:** Topology can adapt slowly without disrupting fast parameter adaptation.
- **DIRECTLY APPLICABLE TO LEBRE?** PARTIAL. Conceptually parallel to LEBRE's two-timescale structural lifecycle.
- **WHY INCLUDED:** Illustrates parameter reallocation under a strict, constant capacity ceiling.
- **WHY NOT DIRECTLY IMPORTED:** Focuses on static deep feedforward topologies; LEBRE focuses on dynamic recurrence and lag structures in streaming time series.

---

## 3. Comparative Literature Synthesis Matrix

| Family | Canonical Method | Primary Information Captured | Estimator Type | FLOP Complexity | Persistent Memory | Replay Required? | Direct Diagnostic Role in LEBRE |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **A. Prequential** | Interleaved Test-Then-Train | Causal streaming loss tracking | Any | $\mathcal{O}(1)$ | $\mathcal{O}(1)$ | **NO** | Mandatory evaluation protocol |
| **B. Adaptive Filter** | NLMS ($E0$) | Instantaneous linear correlation | Gradient SGD | $\mathcal{O}(D)$ | $8D$ B | **NO** | Reference linear estimator |
| **B. Adaptive Filter** | RLS ($E1, E2$) | Exact least-squares covariance | Recursive Matrix | $\mathcal{O}(D^2)$ | $8D^2$ B | **NO** | Estimator sufficiency oracle |
| **B. Adaptive Filter** | Offline OLS ($E3, E4$) | Offline sample minimum loss | SVD / Inversion | Non-causal | Non-causal | **YES** | Diagnostic empirical ceiling |
| **C. Delay Embedding** | Lag Banks ($T1$–$T5$) | Finite temporal history $x_{t-\tau}$ | Linear Readout | $\mathcal{O}(L \cdot D)$ | $8L \cdot D$ B | **NO** | Finite memory control |
| **D. Static Nonlinear** | Random Fourier Features ($NL2$) | Static instantaneous nonlinearity | Linear Readout | $\mathcal{O}(D \cdot K)$ | $8K$ B | **NO** | Memoryless nonlinear control |
| **E. Recurrent Learning** | Scalar RTRL ($N=1$) | Infinite-impulse scalar state | Real-Time Gradient | $\mathcal{O}(1)$ | 24 B | **NO** | Recurrent necessity test |
| **E. Recurrent Learning** | Multi-State RTRL ($N=2, 4$) | Multi-dimensional state manifold | Diagonal RTRL | $\mathcal{O}(N)$ | $\mathcal{O}(N)$ | **NO** | Recurrent dimension limit test |
| **F. Dynamic Capacity** | DEN / Neurogenesis | Task-boundary structural expansion | Batch Retraining | Offline | Unbounded | **YES** | Contrastive prior art (unsuited) |

---

## 4. Scientific Audit Conclusion

1. **Theoretical Discrimination Established:**
   - If **RLS ($E1$) or OLS ($E3$)** closes the gap on $x_t$ without lags, the failure is an **Estimator Deficit** (NLMS stochastic gradient noise).
   - If **Explicit Lag Banks ($T1$–$T5$)** close the gap under standard linear estimation, the failure is a **Finite Temporal Information Deficit** (Takens delay embedding requirement).
   - If **Random Fourier Features ($NL2$)** close the gap without lags, the failure is a **Static Nonlinearity Deficit**.
   - If **Recurrent State ($N=1$)** outperforms estimator-matched lag and nonlinear controls, genuine **Recurrent State Requirement** is established.
   - If **$N=2$ or $N=4$** outperforms $N=1$ while controlling for parameters and FLOPs, a **Scalar Recurrence Capacity Limit** is confirmed.
2. **Methodological Rigor:** Diagnostic oracles ($E3, E4, NORM3$) are strictly segregated as non-causal investigative ceilings and will never be presented as proposed LEBRE architectures.
