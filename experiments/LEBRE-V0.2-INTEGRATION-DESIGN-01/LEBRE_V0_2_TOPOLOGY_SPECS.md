# LEBRE-V0.2-INTEGRATION-DESIGN-01: Architectural Topology Specifications
## Mathematical Formulation, Dataflow Equations & Execution Mechanics for Integration Topologies

**Document ID:** `LEBRE-V0.2-TOPO-2026-v1.0`  
**Status:** `FROZEN_TOPOLOGY_SPECIFICATIONS`  
**Phase:** Integration Design & Structural Arbitration  
**Lead Architect:** Skeptical Senior ML Systems Researcher, Modular Architecture Specialist  

---

## 1. Prequential Causal Protocol Invariant

Every topology under test operates under strict prequential streaming discipline:
1. Receive input vector $x_t \in \mathbb{R}^D$;
2. Write $x_t$ into circular history buffer;
3. Compute baseline linear prediction $\hat{y}_{t, \text{base}} = w_{\text{base}}^T x_t$;
4. Compute active module predictions ($\hat{y}_{t, \text{lag}}$, $\hat{y}_{t, \text{rec}}$);
5. Compute counterfactual shadow candidate predictions;
6. Synthesize live ensemble prediction $\hat{y}_t$;
7. Reveal ground-truth scalar $y_t$;
8. Compute live loss $\ell_t = (y_t - \hat{y}_t)^2$ and all counterfactual losses;
9. Update adaptive parameters using true error signals;
10. Update structural lifecycle governance, probation, and eviction states.

**Zero Future Leakage:** No candidate or active module may access $y_t$ or any signal derived from $y_t$ prior to recording its prediction for step $t$.

---

## 2. Common Prediction Components

At time step $t$, the representational components are defined as:
- **Baseline Linear Predictor ($L_t$):**
  $$\hat{y}_{t, \text{base}} = \sum_{i=1}^D w_{i, t} x_{i, t}, \quad e_{t, \text{base}} = y_t - \hat{y}_{t, \text{base}}$$
  Updated via Normalized LMS (NLMS) with learning rate $\mu_{\text{base}} = 0.10$.
- **Discrete Lag Memory ($D_t$):**
  $$\hat{y}_{t, \text{lag}} = \sum_{m=1}^{K_t} w_{m, t} x_{i_m, t - k_m}$$
  where $(i_m, k_m)$ are active sparse delay coordinates ($1 \le i_m \le D$, $1 \le k_m \le L_{\max}$), stored in `FP16_EXACT_ADDRESSABLE_RING`, updated via NLMS with $\mu_{\text{lag}} = 0.08$.
- **Continuous Recurrent Memory ($R_t$):**
  $$s_t = \tanh(\alpha_t) s_{t-1} + b_t x_{1, t}, \quad \hat{y}_{t, \text{rec}} = c_t s_t$$
  with real-time forward sensitivity traces $p_{\alpha, t}, p_{b, t}$ and online gradient update with $\mu_{\text{rec}} = 0.05$.

---

## 3. Topologies Under Test

### Topology T1: Ordered Residual Cascade
*Conceptual Precedent:* Stagewise Additive Modeling (Friedman, 2001) & Cascade-Correlation (Fahlman & Lebiere, 1990).

```
x_t ──► [ Linear Base ] ──► y_base ──────────────────────┬──► (+) ──► y_hat
              │                                           │     ▲
              ▼ residual e_base                           │     │
        [ Discrete Lags ] ──► y_lag ──────────────────────┼─────┘
              │                                           │     ▲
              ▼ remaining residual e_rem                  │     │
        [ Recurrent State ] ─► y_rec ─────────────────────┴─────┘
```

- **Execution Flow:**
  1. $\hat{y}_{\text{base}} = L_t$;
  2. If discrete lag taps are active: $\hat{y}_{\text{lag}} = D_t$, else $0$;
  3. Residual input to recurrence: $e_{\text{rem}} = y_t - (\hat{y}_{\text{base}} + \hat{y}_{\text{lag}})$;
  4. If recurrent state is active: $\hat{y}_{\text{rec}} = R_t(x_t)$, else $0$;
  5. Live prediction: $\hat{y}_t = \hat{y}_{\text{base}} + \hat{y}_{\text{lag}} + \hat{y}_{\text{rec}}$.
- **Structural Lifecycle in T1:**
  - Lag candidates probe and score correlation against $e_{\text{base}}$;
  - Recurrent candidate trains against remaining residual $e_{\text{rem}} = e_{\text{base}} - \hat{y}_{\text{lag}}$;
  - Promotion occurs sequentially: lag has first priority; recurrence only activates if residual variance persists after lag adaptation.
- **Hypothesized Flaw:** **Order Bias.** If a process has mixed or continuous dynamics, discrete lags may overfit spurious correlations, starving the recurrent module.

---

### Topology T1R: Reversed Residual Cascade (Diagnostic Control)
*Purpose:* Quantitative measure of Order Sensitivity.

```
x_t ──► [ Linear Base ] ──► y_base ──────────────────────┬──► (+) ──► y_hat
              │                                           │     ▲
              ▼ residual e_base                           │     │
        [ Recurrent State ] ─► y_rec ─────────────────────┼─────┘
              │                                           │     ▲
              ▼ remaining residual e_rem                  │     │
        [ Discrete Lags ] ──► y_lag ──────────────────────┴─────┘
```

- **Execution Flow:**
  1. $\hat{y}_{\text{base}} = L_t$;
  2. Recurrent candidate/active module sees baseline residual $e_{\text{base}} = y_t - \hat{y}_{\text{base}}$;
  3. Discrete lag candidates probe remaining residual $e_{\text{rem}} = e_{\text{base}} - \hat{y}_{\text{rec}}$;
  4. Live prediction: $\hat{y}_t = \hat{y}_{\text{base}} + \hat{y}_{\text{rec}} + \hat{y}_{\text{lag}}$.
- **Order Sensitivity Metric ($\rho_{\text{order}}$):**
  $$\text{Disagreement}(s) = \mathbb{I}\left( \text{Alloc}_{\text{T1}}(s) \ne \text{Alloc}_{\text{T1R}}(s) \right)$$

---

### Topology T2: Symmetric Shadow Competition
*Conceptual Precedent:* Competitive Mixture of Experts (Jacobs et al., 1991) with parallel shadow evaluation.

```
                  ┌──► [ Shadow Lag Probing ]      ──► Standalone Gain G_D|B
                  │
x_t ──► [ Linear Base ] (Live) ──► residual e_base
                  │
                  └──► [ Shadow Recurrent Unit ]   ──► Standalone Gain G_R|B
```

- **Execution Flow:**
  1. Linear baseline is **always live**: $\hat{y}_{\text{live}} = \hat{y}_{\text{base}} + \hat{y}_{\text{active}}$;
  2. In shadow mode, lag candidates and recurrent candidates BOTH evaluate against the *same* baseline residual $e_{\text{base}}$;
  3. Both modules independently accumulate statistical evidence:
     $$E_D = \text{EMA}\left( (y_t - \hat{y}_{\text{base}})^2 - (y_t - (\hat{y}_{\text{base}} + \hat{y}_{\text{lag}}))^2 \right)$$
     $$E_R = \text{EMA}\left( (y_t - \hat{y}_{\text{base}})^2 - (y_t - (\hat{y}_{\text{base}} + \hat{y}_{\text{rec}}))^2 \right)$$
  4. Promotion Rule: If a module's standalone evidence exceeds threshold $\theta_{\text{promote}}$ after probation window $T_{\text{prob}}$, it is promoted to active.
- **Hypothesized Flaw:** **Redundant Dual Promotion.** When a signal has redundant autoregressive structure, both modules achieve high standalone gain and both promote, paying double resources for shared variance.

---

### Topology T3: Resource-Aware Conditional Arbitration (Proposed Integrated Design)
*Conceptual Precedent:* Pareto Multi-Objective Optimization & Conditional Innovation Testing.

```
                    ┌──► [ Shadow Lag Candidates ]   ──► Standalone Gain G_D|B ──┐
                    │                                                            ▼
x_t ──► [ Linear Base ] ──► residual e_base                                [ ARBITRATOR ] ──► Structural Action
                    │                                                            ▲             { NONE,
                    └──► [ Shadow Recurrent State ] ──► Standalone Gain G_R|B ──┘               LAG_ONLY,
                                                                                                REC_ONLY,
                    Counterfactual Evaluation:                                                  BOTH }
                    P_D+R = y_base + y_lag + y_rec  ──► Joint Conditional Gains
                                                        G_D|B+R  and  G_R|B+D
```

- **Counterfactual Shadow Loss Grid:**  
  Before revealing $y_t$, compute:
  $$\hat{y}_{\text{BASE}} = \hat{y}_{\text{base}}$$
  $$\hat{y}_{\text{BASE}+D} = \hat{y}_{\text{base}} + \hat{y}_{\text{lag, shadow}}$$
  $$\hat{y}_{\text{BASE}+R} = \hat{y}_{\text{base}} + \hat{y}_{\text{rec, shadow}}$$
  $$\hat{y}_{\text{BASE}+D+R} = \hat{y}_{\text{base}} + \hat{y}_{\text{lag, shadow}} + \hat{y}_{\text{rec, shadow}}$$
- **Conditional Gains Computed upon Revelation of $y_t$:**
  $$G_{D|B} = (y_t - \hat{y}_{\text{BASE}})^2 - (y_t - \hat{y}_{\text{BASE}+D})^2$$
  $$G_{R|B} = (y_t - \hat{y}_{\text{BASE}})^2 - (y_t - \hat{y}_{\text{BASE}+R})^2$$
  $$G_{R|B+D} = (y_t - \hat{y}_{\text{BASE}+D})^2 - (y_t - \hat{y}_{\text{BASE}+D+R})^2$$
  $$G_{D|B+R} = (y_t - \hat{y}_{\text{BASE}+R})^2 - (y_t - \hat{y}_{\text{BASE}+D+R})^2$$
- **Arbitration Decision Table:**

| Condition on Exponentially Filtered Gains | Pareto Dominance | Structural Decision | Physical Rationale |
| :--- | :--- | :--- | :--- |
| $\bar{G}_{D\|B} \le \theta_{\text{tol}}$ AND $\bar{G}_{R\|B} \le \theta_{\text{tol}}$ | N/A | **`NONE`** | Neither temporal mechanism explains persistent error (e.g. I1, I2). |
| $\bar{G}_{D\|B} > \theta_{\text{tol}}$ AND $\bar{G}_{R\|B} \le \theta_{\text{tol}}$ | Lag dominates | **`LAG_ONLY`** | Pure discrete delay structure (e.g. I3, I4). |
| $\bar{G}_{R\|B} > \theta_{\text{tol}}$ AND $\bar{G}_{D\|B} \le \theta_{\text{tol}}$ | Recurrent dominates | **`RECURRENT_ONLY`** | Pure continuous latent state (e.g. I6). |
| Both $\bar{G}_{D\|B}, \bar{G}_{R\|B} > \theta_{\text{tol}}$, BUT $\bar{G}_{R\|B+D} \le \theta_{\text{tol}}$ AND $\bar{G}_{D\|B+R} \le \theta_{\text{tol}}$ | Vector Resource Comparison | **Pareto Dominant** (Prefer Lag if cheaper, or higher standalone gain) | Redundant structure (e.g. I10). Explaining once is sufficient. |
| Both $\bar{G}_{D\|B+R} > \theta_{\text{tol}}$ AND $\bar{G}_{R\|B+D} > \theta_{\text{tol}}$ | Both Feasible | **`BOTH`** | True hybrid complementarity (e.g. I9). Both provide unique marginal value. |

- **Zero Learned Router:** The arbitrator contains **zero trainable neural parameters**. It evaluates filtered prequential loss differences with hysteresis to prevent structural chatter.

---

### Topology O_ALL: Always-On Oracle (Diagnostic Upper Bound)
- **Concept:** Linear + Discrete Lag + Recurrent modules are **permanently active** simultaneously ($K=4$ active taps, $N=1$ recurrent unit).
- **Purpose:** Establishes the empirical capacity ceiling and quantifies **Structural Governance Regret**:
  $$\text{Regret}_{\text{gov}} = \text{NMSE}(\text{Topology}) - \text{NMSE}(\text{O\_ALL})$$
  $$\text{Savings}_{\text{gov}} = \text{Compute}(\text{O\_ALL}) - \text{Compute}(\text{Topology})$$

---

### Topology E_EXP: Online Expert Weighting Comparator (Diagnostic Benchmark)
- **Concept:** Fixed-Share exponential loss weighting over 4 static structural configurations:
  - Expert $E_0$: Baseline Only ($L$)
  - Expert $E_1$: Baseline + Lag ($L + D$)
  - Expert $E_2$: Baseline + Recurrent ($L + R$)
  - Expert $E_3$: Baseline + Lag + Recurrent ($L + D + R$)
- **Update Rule:**
  $$w_{i, t+1} = (1 - \alpha) \frac{w_{i, t} \exp(-\eta \ell_{i, t})}{\sum_j w_{j, t} \exp(-\eta \ell_{j, t})} + \frac{\alpha}{4}$$
  with learning rate $\eta = 0.5$, mixing parameter $\alpha = 0.01$.
- **Purpose:** Benchmarks the speed of structural reallocation during sudden regime transitions (I11, I12, I13).
