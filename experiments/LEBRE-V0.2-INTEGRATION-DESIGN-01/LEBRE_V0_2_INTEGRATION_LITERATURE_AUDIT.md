# LEBRE-V0.2-INTEGRATION-DESIGN-01: Comprehensive Literature Audit
## Theoretical Precedents, Structural Principles & Architectural Boundaries for Multi-Capacity Integration

**Document ID:** `LEBRE-V0.2-LIT-AUDIT-2026-v1.0`  
**Status:** `PRE-EXPERIMENTAL_LITERATURE_AUDIT`  
**Phase:** Integration Design & Structural Arbitration  
**Lead Auditor:** Skeptical Senior ML Systems Researcher, Adaptive-Filtering Specialist, Control-Theoretic Performance Analyst  

---

## 1. Executive Research Framing

The core scientific challenge of LEBRE v0.2 is **Structural Integration**:
How should a resource-constrained streaming learner orchestrate distinct representational mechanisms:
1. **Instantaneous linear representation ($L_t$):** fast, parameter-efficient, low-rent baseline;
2. **Sparse discrete temporal memory ($D_t$):** non-contiguous lag coordinates $(i, k)$ for pure delay and transport phenomena;
3. **Continuous recurrent latent memory ($R_t$):** scalar/low-dimensional dynamical state for smooth exponential relaxation and continuous state-space dynamics?

This audit investigates 10 foundational literature families to determine how prior art approaches structural growth, module specialization, residual fitting, and arbitration, identifying exactly what principles transfer to LEBRE and what must be strictly excluded.

---

## 2. Exhaustive Audit of Literature Families

### L1. Residual Model Validation & System Identification
- **Foundational References:** Ljung, L. (1999), *System Identification: Theory for the User* (2nd ed., Prentice Hall); Box, G. E. P., Jenkins, G. M., & Reinsel, G. C. (2008), *Time Series Analysis: Forecasting and Control*.
- **Core Principles:**  
  In classical prediction-error identification (PEM), a model $\hat{y}_t = f(Z^{t-1})$ is validated by inspecting the prediction error (residual) $\epsilon_t = y_t - \hat{y}_t$. For a statistically adequate model:
  1. *Innovation Whiteness:* The autocorrelation function of the residual $R_{\epsilon\epsilon}(\tau) = E[\epsilon_t \epsilon_{t-\tau}]$ should be statistically indistinguishable from white noise for all $\tau \ne 0$:
     $$|R_{\epsilon\epsilon}(\tau)| \le \frac{1.96}{\sqrt{N}} \cdot R_{\epsilon\epsilon}(0)$$
  2. *Input-Residual Independence:* The cross-correlation $R_{u\epsilon}(\tau) = E[u_{t-\tau} \epsilon_t]$ should vanish for all $\tau \ge 0$, confirming that no past input information remains unmodeled.
- **Critical LEBRE Audit Insight:**  
  **Residual non-whiteness is evidence of model inadequacy, NOT an oracle model classifier.**  
  A prominent autocorrelation spike at lag $\tau = 4$ could indicate:
  - An unmodeled pure transport delay $x_{t-4}$ (Lag required);
  - An under-damped continuous second-order pole with natural frequency $\omega_n \approx \pi / 4$ (Recurrence required);
  - A missing static nonlinear transformation of a cross-correlated input (Nonlinear expansion required).  
  Therefore, LEBRE must use residual analysis *only* to establish `MODEL_INADEQUACY_EVIDENCE`, and must never apply hard-coded rules mapping residual statistics directly to structural promotion.

### L2. Cascade-Correlation Architecture
- **Foundational References:** Fahlman, S. E., & Lebiere, C. (1990), "The Cascade-Correlation Learning Architecture", *Advances in Neural Information Processing Systems (NIPS 1989)*; Fahlman, S. E. (1990), "The Recurrent Cascade-Correlation Architecture", *NIPS 1990*.
- **Core Principles:**  
  Cascade-Correlation (CasCor) starts with a minimal linear topology (input to output). When training performance stagnates, a pool of candidate units is trained to maximize the correlation between the candidate's output and the residual error of the existing network. The best candidate is frozen and permanently installed as a new hidden unit, creating a deep cascade.
- **Critical LEBRE Audit Comparison:**  
  CasCor provides strong historical precedent for *residual-driven structural expansion* and *shadow candidate evaluation*. However, LEBRE fundamentally diverges:
  1. *Online Streaming vs. Offline Batch:* CasCor optimizes candidate pools using offline batch epochs; LEBRE adapts causally step-by-step.
  2. *Plasticity & Eviction:* CasCor permanently freezes units; LEBRE requires active lifecycle governance with eviction of obsolete structure.
  3. *Heterogeneous Semantics:* CasCor adds generic sigmoid units; LEBRE arbitrates between fundamentally distinct physical memory classes (discrete shift-register vs. continuous recurrent state).
  4. *Moving-Target Mitigation:* CasCor freezes prior weights to eliminate the moving-target problem. In LEBRE, the baseline remains live, requiring prequential birth-snapshot comparators to avoid comparator drift.

### L3. Resource-Allocating Networks (RAN)
- **Foundational References:** Platt, J. C. (1991), "A Resource-Allocating Network for Function Interpolation", *Neural Computation*, 3(2), 213–225.
- **Core Principles:**  
  RAN combines local radial basis function (RBF) networks with online learning. A new unit is allocated dynamically if two conditions are met simultaneously:
  1. Prediction error exceeds a threshold: $|e_t| = |y_t - \hat{y}_t| > e_{\min}$;
  2. The novel input is distant from existing centers: $\min_k \|x_t - c_k\| > \delta_t$.  
  If these conditions fail, LMS is used to adjust weights and centers locally.
- **Critical LEBRE Audit Comparison:**  
  RAN establishes that unit creation should be *doubly gated* (error magnitude + feature novelty). In LEBRE, this motivates the two-stage structure of lag probing:
  - Error must be persistent (not a transient innovation spike);
  - The delayed candidate feature must exhibit strong cross-correlation with residual error.
  However, standard RAN lacks principled eviction (leading to explosive over-allocation in non-stationary streams), which LEBRE solves via its finite-capacity lifecycle probation and obsolescence gating.

### L4. Stagewise Additive Modeling (Boosting)
- **Foundational References:** Friedman, J. H. (2001), "Greedy Function Approximation: A Gradient Boosting Machine", *Annals of Statistics*, 29(5), 1189–1232.
- **Core Principles:**  
  Gradient Boosting constructs an additive model $\hat{y}_t = \sum_{m=1}^M f_m(x_t)$ in a forward stagewise manner. At stage $m$, a base learner $h_m(x)$ is fitted to the pseudo-residuals of the existing ensemble:
  $$\tilde{y}_{t, m} = -\left[ \frac{\partial L(y_t, F_{m-1}(x_t))}{\partial F_{m-1}(x_t)} \right]$$
  The new component is scaled by a shrinkage rate $\nu$ and added to the ensemble.
- **Critical LEBRE Audit Comparison:**  
  Stagewise residual fitting directly motivates **Topology T1 (Ordered Residual Cascade)**: fitting discrete lags to the linear baseline residual, and recurrent state to the remaining lag residual. However:
  - Boosting is fundamentally batch-oriented and non-causal;
  - Boosting assumes identical base learner classes (e.g. decision trees); LEBRE features structurally heterogeneous modules with asymmetric compute/memory footprints;
  - Boosting theoretical convergence rates do not hold under streaming non-stationary tracking.

### L5. Mixture of Experts (MoE) & Conditional Computation
- **Foundational References:** Jacobs, R. A., Jordan, M. I., Nowlan, S. J., & Hinton, G. E. (1991), "Adaptive Mixtures of Local Experts", *Neural Computation*, 3(1), 79–95; Shazeer, N., et al. (2017), "Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer", *ICLR 2017*.
- **Core Principles:**  
  MoE partitions an input space among multiple specialized expert networks governed by a parametric gating network. The gate outputs soft probabilities $g_i(x_t)$, and prediction is a convex combination $\hat{y}_t = \sum_i g_i(x_t) f_i(x_t)$. Shazeer et al. introduced top-$k$ sparse gating for computational efficiency.
- **Critical LEBRE Audit Comparison:**  
  MoE provides precedent for *expert specialization* and *conditional computation* (only paying for relevant capacity). However:
  - Standard MoE routes based on *instantaneous input features* $x_t$; LEBRE must arbitrate based on *temporal memory requirements*;
  - MoE uses a heavy learned neural gating network that introduces its own moving-target dynamics and substantial compute overhead;
  - **LEBRE rule:** LEBRE will NOT implement a learned neural router. The arbitrator must be a lightweight, rule-bounded governor based on prequential loss evidence and Pareto resource constraints.

### L6. Prediction with Expert Advice & Online Tracking
- **Foundational References:** Freund, Y., & Schapire, R. E. (1997), "A Decision-Theoretic Generalization of On-Line Learning and an Application to Boosting", *Journal of Computer and System Sciences*, 55(1), 119–139; Herbster, M., & Warmuth, M. K. (1998), "Tracking the Best Expert", *Machine Learning*, 32(2), 151–178.
- **Core Principles:**  
  In the adversarial online prediction setting, a master algorithm maintains weights over $K$ fixed experts:
  $$w_{i, t+1} = \frac{w_{i, t} \exp(-\eta \ell_{i, t})}{\sum_j w_{j, t} \exp(-\eta \ell_{j, t})}$$
  Herbster & Warmuth's Fixed-Share algorithm adds a mixing parameter $\alpha$ that periodically shares weight across all experts, proving optimal cumulative regret bounds against arbitrary sequences of switching best experts.
- **Critical LEBRE Audit Comparison:**  
  Expert tracking motivates the design of **Diagnostic Comparator E_EXP**: maintaining online weights over the structural configurations $E_0$ (Base), $E_1$ (Base+Lag), $E_2$ (Base+Rec), $E_3$ (Base+Lag+Rec). However:
  - LEBRE's modules are *internally adaptive learning components*, violating the fixed-expert assumption;
  - Regret bounds do not immediately apply; E_EXP is strictly a diagnostic benchmark for non-stationary regime transitions.

### L7. Adaptive Structural Complexity & Regularization
- **Foundational References:** Cortes, C., Gonzalvo, X., Kuznetsov, V., Mohri, M., & Yang, S. (2017), "AdaNet: Adaptive Structural Learning of Artificial Neural Networks", *ICML 2017*.
- **Core Principles:**  
  AdaNet adaptively grows neural network architectures while providing generalization bounds based on Rademacher complexity. It trades off empirical risk minimization against structural complexity via an explicit scalar complexity penalty:
  $$\min_{h} \left\{ \hat{R}(h) + \Gamma(h) \right\}$$
- **Critical LEBRE Audit Comparison:**  
  AdaNet demonstrates the mathematical necessity of regularizing structural expansion. However:
  - AdaNet collapses model complexity into a single scalar $\Gamma(h)$;
  - LEBRE operates in embedded environments where hardware resources are fundamentally **vector-valued**:
    $$\mathbf{R} = [\text{FP\_FLOPS}, \text{INTEGER\_OPS}, \text{MEMORY\_TRAFFIC}, \text{PERSISTENT\_BYTES}]^T$$
  - Arbitrary scalarization (e.g. $1 \text{ FLOP} + 0.1 \text{ Byte}$) is physically ungrounded. LEBRE must use **Pareto partial ordering** rather than scalar complexity scores.

### L8. Adaptive Filter Structure & Tap-Length Adaptation
- **Foundational References:** Gong, Y., & Cowan, C. F. N. (2005), "An LMS Style Variable Tap-Length Algorithm for Structure Adaptation", *IEEE Transactions on Signal Processing*, 53(7), 2400–2407; Gu, Y., Jin, J., & Mei, S. (2009), "$\ell_0$ Norm Constraint LMS Algorithm for Sparse System Identification", *IEEE Trans. SP*.
- **Core Principles:**  
  Gong & Cowan treat the filter tap-length $L$ as an integer parameter updated causally via gradient descent on error:
  $$L_{t+1} = L_t - \gamma (e_t^2 - \sigma_n^2)$$
  Active weights are contiguous from lag 1 to $L$.
- **Critical LEBRE Audit Comparison:**  
  Gong & Cowan demonstrate that temporal order can be an adaptive structural variable. However, their formulation forces *contiguous* tap allocation. For widely separated delays (e.g. lag 2 and lag 30), it allocates 30 active taps. LEBRE enforces *non-contiguous sparse tap selection*, isolating isolated delay coordinates at a fraction of the compute and memory.

### L9. Hybrid Static & Dynamic System Identification
- **Foundational References:** Narendra, K. S., & Parthasarathy, K. (1990), "Identification and Control of Dynamical Systems Using Neural Networks", *IEEE Transactions on Neural Networks*, 1(1), 4–27.
- **Core Principles:**  
  Classifies nonlinear dynamic identification into canonical topologies (NARX, Hammerstein, Wiener, Bilinear). Proves that unconstrained static networks fail to capture unobserved internal states, requiring dynamic feedback (recurrent neurons) or tapped delay lines.
- **Critical LEBRE Audit Comparison:**  
  Establishes the fundamental necessity of both feedforward delay paths and internal feedback states in system identification. Validates LEBRE's core hypothesis that instantaneous linear models, tapped delays, and recurrent states represent non-interchangeable functional classes.

### L10. Continuous Distributed Temporal Memory
- **Foundational References:** Voelker, A. R., Kajić, I., & Eliasmith, C. (2019), "Legendre Memory Units: Continuous-Time Representations in Recurrent Neural Networks", *NeurIPS 2019*; Gu, A., Dao, T., Ermon, S., Rudra, A., & Ré, C. (2020), "HiPPO: Recurrent Memory with Optimal Polynomial Projections", *NeurIPS 2020*.
- **Core Principles:**  
  Compress continuous history streams $u(t)$ into a low-dimensional state vector by maintaining the optimal coefficients of an orthogonal polynomial basis (Legendre) via continuous linear state-space equations:
  $$\frac{d}{dt} m(t) = A m(t) + B u(t)$$
- **Critical LEBRE Audit Comparison:**  
  Previous LEBRE milestone `BOUNDED-HISTORY-LAG-INTEGRATION-01` conclusively proved that continuous Legendre projections (HiPPO-6) fail catastrophically on discrete high-entropy delays ($F_1 = 0.173$), but outperform discrete ring buffers on continuous linear state-space systems. This audit locks the boundary: continuous recurrence and discrete ring buffers belong to disjoint memory classes. No new continuous basis integration is required in this stage.

---

## 3. Literature Audit Master Table

The table below summarizes the 10 audited literature families across all 18 mandated dimensions:

| Dimension | L1: PEM / Ljung (1999) | L2: CasCor (1990) | L3: RAN (1991) | L4: GBM / Friedman (2001) | L5: MoE / Jacobs (1991) | L6: Expert Advice (1997) | L7: AdaNet (2017) | L8: Var Tap-Length (2005) | L9: Narendra & Parth. (1990) | L10: HiPPO / LMU (2020) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Reference** | Ljung (1999) | Fahlman & Lebiere (1990) | Platt (1991) | Friedman (2001) | Jacobs et al. (1991) | Freund & Schapire (1997) | Cortes et al. (2017) | Gong & Cowan (2005) | Narendra & Parth. (1990) | Gu et al. (2020) |
| **2. Year** | 1999 | 1990 | 1991 | 2001 | 1991 | 1997 | 2017 | 2005 | 1990 | 2020 |
| **3. Primary Verified** | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| **4. Problem Setting** | System ID / PEM | Supervised Learning | Function Interpolation | Greedy Regr / Classif | Multi-Task / Mixture | Adversarial Online | Deep Architecture Search | Adaptive Filtering | Dynamic Control | Continuous Sequence |
| **5. Online / Offline** | Both (Mostly Offline) | Offline Batch | Causal Online | Offline Batch | Minibatch Gradient | Causal Streaming | Offline Batch | Causal Streaming | Minibatch / Offline | Streaming / Recurrent |
| **6. Structure** | Fixed / Pre-selected | Adaptive Growth | Adaptive Growth | Adaptive Growth | Fixed Capacity | Fixed Experts | Adaptive Growth | Adaptive Order | Fixed Topology | Fixed State Dim |
| **7. Module Special.** | Residual correlation | Generic Hidden Units | Local RBF Centers | Generic Trees / Additive | Local Input Partition | External Experts | Sub-networks | Contiguous Taps | Static vs Dynamic | Continuous Legendre |
| **8. Residual Driven** | Yes (Model Validation) | Yes (Candidate Maxim.) | Yes (Error Magnitude) | Yes (Pseudo-Residuals) | No (Competitive Error) | Yes (Loss Relative) | Yes (Rademacher Risk) | Yes (Error Energy) | No (Direct Gradient) | No (Analytic Projection) |
| **9. Gating / Arbitr.** | None (Diagnostics) | None (Frozen Cascade) | Gated Unit Creation | None (Shrinkage Additive)| Neural Gating Network | Exponential Weights | Complexity Regularizer | Gradient on Order | None (Summation) | None (Fixed LTI) |
| **10. Capacity Growth** | Manual Model Order | Greedy Unit Addition | RBF Node Insertion | Stagewise Boosting | Fixed Ensemble Size | Fixed Expert Pool | Layer / Block Addition| Contiguous Tap Incr. | Manual Layer Sizing | Fixed State Size |
| **11. Eviction** | Model Pruning | None (Permanent) | None (Monotonic) | Tree Pruning | Implicit Gating Zero | Weight Decay | None | Contiguous Tap Decr. | Weight Decay | None |
| **12. Resource Aware** | AIC / BIC Penalty | None | None | Max Tree Depth | Sparse Top-k (Shazeer) | None | Rademacher Penalty | None | None | State Compression |
| **13. Nonstationary** | Recursive PEM | Poor (Frozen Weights) | Poor (Over-allocation) | None | Local Re-adaptation | Excellent (Fixed-Share) | Poor (Batch Risk) | Excellent (Tracking) | Poor (Local Minima) | Drift Tracking |
| **14. Guarantees** | Asymptotic Whiteness | Stepwise Convergence | Local Error Bound | Geometric Convergence | EM Lower Bound | Regret $O(\sqrt{T \ln K})$ | Rademacher Gen. Bound | Mean-Square Stability | Stability Criteria | Optimal Poly Error |
| **15. Assumptions** | Stationary Erg. Noise | IID Batch Data | Smooth Target Function | Differentiable Loss | Mixture Distribution | Bounded Losses $[0, 1]$ | IID Sampling | Stationary Auto-corr. | Bounded State Dynamics | Continuous Time Signal |
| **16. Transferable** | **Partial** | **Partial** | **Partial** | **Partial** | **Partial** | **Partial** | **Partial** | **Partial** | **Partial** | **No (Boundary Only)** |
| **17. Motivates** | Residual Diagnostics | Shadow Candidate Eval | Error-Gated Creation | Residual Cascade (T1) | Specialization Concept | Comparator E_EXP | Vector Pareto Dominance| Temporal Adaptability | Static + Dynamic Hybrid| Disjoint Memory Class |
| **18. Must Not Import** | Residual -> Lag rule | Unit Freezing / Batch | Monotonic Growth | Batch Trees / Shrinkage| Heavy Neural Router | Regret Bounds to Struct.| Scalar Complexity Score| Contiguous Tap Bloat | Dense MLP Feedback | Poly Basis for Delays |

---

## 4. Key Architectural Takeaways for LEBRE v0.2 Integration

1. **Residuals Provide Inadequacy Evidence, Not Category Labels (from L1):**  
   Residual whiteness tests indicate whether the model is complete. They do *not* determine whether missing structure is discrete lag, continuous recurrence, or static nonlinearity. Model escalation must evaluate competing hypotheses prequentially.
2. **Shadow Evaluation Eliminates Moving-Target Destabilization (from L2 & L3):**  
   Evaluating candidate structures in shadow mode against baseline residuals—without mutating live predictions until statistical maturity—prevents the circular instability observed in early adaptive networks.
3. **Cascading Imposes Order Bias (from L4):**  
   Fitting discrete lags first and then fitting recurrence to remaining residuals creates a structural order bias. A complementary diagnostic reversed cascade (T1R) is mandatory to measure order sensitivity.
4. **Arbitration Must Avoid Heavy Neural Gates (from L5 & L6):**  
   Neural gating networks (MoE) introduce excessive parameter overhead and internal moving targets. LEBRE’s structural governor must rely on prequential loss evidence ($G_{D|B}, G_{R|B}, G_{R|B+D}, G_{D|B+R}$) and Pareto resource dominance.
5. **Hardware Constraints Require Vector Partial Orders (from L7):**  
   Scalar complexity regularization (AdaNet) is invalid for micro-edge embedded ML. Resources must be tracked as a 4-channel vector $\mathbf{R} = [\text{FP\_FLOPS}, \text{INT\_OPS}, \text{MEM\_TRAFFIC}, \text{RAM}]$, applying Pareto dominance rather than arbitrary utility weights.
6. **Symmetric Shadow Competition Provides Order-Free Arbitration (Synthesis of L2, L5, L7):**  
   Parallel shadow evaluation of both lag and recurrent candidates against the baseline residual enables unbiased, symmetric discovery. Structural promotion occurs only when conditional marginal gain exceeds noise floors and resource budgets permit.

---

## 5. Formal Pre-Registration of Literature Audit

This literature audit is hereby completed and pre-registered prior to the authoring of experimental protocols and execution of integration experiments in accordance with the `LEBRE-V0.2-INTEGRATION-DESIGN-01` charter.
