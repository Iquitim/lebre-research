# DYNAMIC-LAG-LIFECYCLE-01: Formal Model & Variant Specifications
## Mathematical Definitions, Pseudocode & Algorithmic Mechanics

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Auditor:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, Reproducibility Auditor  
**Date:** September 2026  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Status:** PREREGISTERED & SEALED (Pre-Execution)

---

## 1. Overview of Experimental Variants

The experimental suite consists of 3 Diagnostic Oracles (O0–O2), 7 Primary Comparative Baselines (B0–B6), and the Proposed Dynamic Lag Lifecycle Architecture (B7).

```
                      +-----------------------------------+
                      |       INPUT STREAM (x_t, y_t)     |
                      +-----------------------------------+
                                        |
       +--------------------------------+--------------------------------+
       |                                |                                |
       v                                v                                v
[ ORACLES (Ceilings) ]        [ CLASSICAL BASELINES ]         [ LEBRE STRUCTURAL LIFECYCLE ]
O0: Oracle Sparse Lags        B0: Frozen LEBRE Baseline       B7: Dynamic Lag Lifecycle
O1: Full Dense FIR            B1: Linear Instantaneous            - Rotating Probing (M=2)
O2: Oracle Support Switch     B3: Fixed Contiguous FIR            - Paired Prequential Evidence
                              B4: Variable Tap-Length (Gong'05)   - Two-Timescale Relevance
                              B5: l0-LMS Sparse Dict (Gu'09)      - Hard Capacity (K_max=4)
                              B6: Proportionate PNLMS (Dutt'00)   - Quiescence Eviction Gate
```

---

## 2. Formal Mathematical Specifications

### 2.1 Oracles (Diagnostic Upper Bounds)

#### O0: ORACLE_SPARSE_LAGS
- **Description:** Given the exact ground-truth active coordinate-lag pairs $S^* = \{(i_1^*, k_1^*), \dots, (i_K^*, k_K^*)\}$ at the start of the stream.
- **Model Equation:**
  $$\hat{y}_t = \mathbf{w}_{\text{base}}^\top \mathbf{x}_t + \sum_{j=1}^{|S^*|} w_j^* x_{i_j^*, t-k_j^*}$$
- **Update:** Standard NLMS on the concatenated feature vector $[\mathbf{x}_t^\top, x_{i_1^*, t-k_1^*}, \dots]^\top$.
- **Resource Ledger:** $\mathcal{O}(D + |S^*|)$ FLOPs; memory for $|S^*|$ active buffers. Non-causal structural upper bound.

#### O1: FULL_DENSE_FIR
- **Description:** Evaluates all $D \times L_{\max}$ delayed regressors simultaneously:
  $$\hat{y}_t = \sum_{i=1}^D \sum_{k=0}^{L_{\max}-1} w_{i, k} x_{i, t-k}$$
- **Resource Ledger:** $\mathcal{O}(D \cdot L_{\max})$ FLOPs and memory. Represents unconstrained capacity ceiling.

#### O2: ORACLE_SUPPORT_LIFECYCLE
- **Description:** In time-varying streams (D4, D5, D6), receives an external trigger exactly when support changes, instantaneously swapping inactive taps for true new taps with zero latency. Establishes the lower bound on adaptation regret.

---

### 2.2 Classical & Literature Baselines

#### B0: LEBRE_v0.1_FROZEN
- Canonical frozen baseline: Instantaneous linear model + 1 scalar recurrent unit ($N=1$) under frozen lifecycle rules.

#### B1: LEBRE_NO_REC_BIRTH
- Causal linear ablation: Instantaneous NLMS on $\mathbf{x}_t$ alone ($\mu = 0.10$). Zero temporal memory.

#### B3: FIXED_DENSE_FIR
- Fixed contiguous FIR filter of order $K=4$ across all input dimensions ($4D$ total weights).

#### B4: VARIABLE_CONTIGUOUS_TAP_LENGTH (Gong & Cowan, 2005)
- **Model:** Contiguous FIR filter with dynamic length $L_t \in [1, L_{\max}]$:
  $$\hat{y}_t = \sum_{k=0}^{L_t-1} \mathbf{w}_k^\top \mathbf{x}_{t-k}$$
- **Fractional Length Adaptation:**
  $$l_{t+1} = l_t - \alpha \left( e_t^2 - \sigma_e^2(t) \right) \cdot \operatorname{sgn}\left(\sum_{k=L_t-\Delta}^{L_t} \|\mathbf{w}_k\|^2 - \theta_{\text{tail}}\right)$$
  $$L_{t+1} = \operatorname{clip}\left(\lfloor l_{t+1} \rfloor, 1, L_{\max}\right)$$
- **Parameters:** $\alpha = 0.05, \Delta = 2, \theta_{\text{tail}} = 0.01$.

#### B5: SPARSITY_REGULARIZED_FULL_DICTIONARY ($\ell_0$-LMS; Gu et al., 2009)
- **Model:** Full dictionary of $D \cdot L_{\max}$ taps adapted with continuous $\ell_0$ zero-attraction:
  $$\mathbf{w}_{t+1} = \mathbf{w}_t + \mu \frac{e_t \mathbf{z}_t}{\|\mathbf{z}_t\|^2 + \epsilon} - \rho \alpha \operatorname{sgn}(\mathbf{w}_t) e^{-\alpha |\mathbf{w}_t|}$$
  where $\mathbf{z}_t = [\mathbf{x}_t^\top, \mathbf{x}_{t-1}^\top, \dots, \mathbf{x}_{t-L_{\max}+1}^\top]^\top$.
- **Parameters:** $\mu = 0.10, \rho = 1e-4, \alpha = 5.0$.

#### B6: PROPORTIONATE_SPARSE_ADAPTIVE_FILTER (PNLMS; Duttweiler, 2000)
- **Model:** Adapts full dictionary $\mathbf{z}_t \in \mathbb{R}^{D \cdot L_{\max}}$ using proportionate step-size matrix $\mathbf{G}_t$:
  $$g_j(t) = \frac{\max\left(\rho \max_k |w_k(t)|, |w_j(t)|\right)}{\sum_{m} \max\left(\rho \max_k |w_k(t)|, |w_m(t)|\right)}$$
  $$\mathbf{w}_{t+1} = \mathbf{w}_t + \mu \frac{\mathbf{G}_t \mathbf{z}_t}{\mathbf{z}_t^\top \mathbf{G}_t \mathbf{z}_t + \epsilon} e_t$$
- **Parameters:** $\mu = 0.10, \rho = 0.01$.

---

### 2.3 Proposed Dynamic Lag Lifecycle Architecture (B7)

#### Structural Lifecycle States
Each coordinate-lag pair $(i, k) \in \{1 \dots D\} \times \{1 \dots L_{\max}\}$ belongs to exactly one state:
1. **DORMANT:** Not instantiated. Consumes zero parameters and zero active compute. Represented only as a coordinate in the candidate search space.
2. **PROVISIONAL (Shadow Probation):** Instantiated with a shadow weight $\tilde{w}_{i, k}$ and paired prequential evidence accumulator $E_{i, k}$. Evaluated counterfactually at step $t$ without affecting live model output.
3. **ACTIVE:** Promoted into the live linear model. Updates weight $w_{i, k}$ via NLMS and contributes to live prediction $\hat{y}_t$.
4. **MATURE:** Has maintained high structural relevance for $> 500$ steps. Protected from transient eviction.
5. **EVICTED:** Retired due to persistent obsolescence. Weight zeroed and returned to DORMANT pool.

```
       [ DORMANT ] 
            |
            | (Scheduled Probe via Rotating Candidate Schedule)
            v
     [ PROVISIONAL ]  <--- Shadow probation (evaluates counterfactual marginal gain)
            |
            +-------------------------------+
            | (Prequential Evidence >= 0.12) | (Evidence < 0 over probation window)
            v                               v
       [ ACTIVE ]                      [ EVICTED ] ---> [ DORMANT ]
            |
            | (Relevance > 0.50 for 500 steps)
            v
       [ MATURE ]
            |
            | (Slow Relevance R_j < 0.05 + Obsolescence Gate)
            v
       [ EVICTED ] ---> [ DORMANT ]
```

---

#### Detailed Step-by-Step Execution Protocol (B7)

##### Step 1: Feature Retrieval & Live Prediction
1. Retrieve instantaneous normalized input $\mathbf{x}_t \in \mathbb{R}^D$.
2. For each active tap $j \in \{1 \dots K_t\}$, retrieve delayed scalar $x_{i_j, t-k_j}$ from its dedicated circular buffer.
3. Compute base linear prediction $\hat{y}_{\text{base}, t} = \mathbf{w}_{\text{base}}^\top \mathbf{x}_t$.
4. Compute active lag prediction $\hat{y}_{\text{lag}, t} = \sum_{j=1}^{K_t} w_j x_{i_j, t-k_j}$.
5. If recurrent unit is active, compute recurrent prediction $\hat{y}_{\text{rec}, t} = w_{\text{out}} s_t$.
6. Form composite live prediction:
   $$\hat{y}_t = \hat{y}_{\text{base}, t} + \hat{y}_{\text{lag}, t} + \hat{y}_{\text{rec}, t}$$

##### Step 2: Counterfactual Candidate Scoring (Before Weight Update)
For each provisional candidate $m \in \{1 \dots M_t\}$ with coordinate $(i_m, k_m)$:
1. Retrieve candidate delayed feature $x_{i_m, t-k_m}$ from the candidate probe history buffer.
2. Compute counterfactual shadow prediction:
   $$\hat{y}_{\text{cand}, m} = \hat{y}_t + \tilde{w}_m x_{i_m, t-k_m}$$
3. Reveal true target $y_t$.
4. Compute live residual: $e_t = y_t - \hat{y}_t$.
5. Compute candidate counterfactual residual: $e_{\text{cand}, m} = y_t - \hat{y}_{\text{cand}, m}$.
6. Record paired squared-error improvement:
   $$\Delta_{m, t} = e_t^2 - e_{\text{cand}, m}^2$$
7. Update cumulative provisional evidence:
   $$E_m(t) = (1 - \beta_{\text{cand}}) E_m(t-1) + \beta_{\text{cand}} \Delta_{m, t}$$

##### Step 3: Candidate Promotion Gate
A candidate $(i_m, k_m)$ is promoted from **PROVISIONAL $\to$ ACTIVE** if:
$$E_m(t) \ge \theta_{\text{promote\_lag}} \quad (0.10) \quad \text{and} \quad \text{age}_m \ge W_{\min} \quad (50 \text{ steps})$$
- If current active tap count $K_t < K_{\max}$ (where $K_{\max} = 4$): promote immediately into an empty slot.
- If all $K_{\max}$ slots are occupied: evaluate **Replacement Regret**. Let $j^* = \arg\min_j R_j$ be the weakest active tap. If:
  $$E_m(t) > R_{j^*} + \theta_{\text{replace\_margin}} \quad (0.05)$$
  then evict tap $j^*$ and replace it with candidate $m$. Otherwise, candidate $m$ is rejected.

##### Step 4: Active Weight Adaptation
Active tap weights are updated via Normalized LMS:
$$\mathbf{w}_{\text{active}}(t+1) = \mathbf{w}_{\text{active}}(t) + \mu_{\text{lag}} \frac{e_t \mathbf{z}_{\text{active}, t}}{\|\mathbf{z}_{\text{active}, t}\|^2 + \epsilon}$$
where $\mu_{\text{lag}} = 0.08$.

##### Step 5: Two-Timescale Structural Relevance & Eviction Gate
For each active tap $j \in \{1 \dots K_t\}$, evaluate its marginal contribution:
$$e_{-j, t} = y_t - (\hat{y}_t - w_j x_{i_j, t-k_j})$$
$$\Delta_{-j, t} = e_{-j, t}^2 - e_t^2$$
Update slow structural relevance:
$$R_j(t) = (1 - \gamma_{\text{rel}}) R_j(t-1) + \gamma_{\text{rel}} \Delta_{-j, t} \quad (\gamma_{\text{rel}} = 0.001)$$
An active tap is evicted if:
$$R_j(t) < \theta_{\text{evict}} \quad (0.01) \quad \text{and} \quad \text{tap\_age}_j > W_{\text{grace}} \quad (200 \text{ steps})$$
and the tap has failed to provide positive contribution for $> 100$ consecutive evaluations (**Obsolescence Gate**).

##### Step 6: Bounded Candidate Probing (Rotating Search Schedule)
To guarantee strict compliance with R2-FLOP ($\le 100$ FLOPs):
- The algorithm does **NOT** scan all $D \cdot L_{\max}$ candidates per step.
- At each step $t$, a rotating scheduler tests $M = 2$ candidate pairs $(i, k)$ in round-robin fashion across the search grid.
- Probing compute is strictly bounded: $2 \times 6 = 12$ FLOPs/step.

---

## 3. Eviction Comparator Variants (Prompt Section 23)

To test Hypothesis H5 (quiescence vs obsolescence), we compare 3 eviction policies for active taps:
- **E0 (Instantaneous Magnitude Pruning):** Evicts tap if $|w_j(t)| < \theta_{\text{mag}}$ for 20 consecutive steps.
- **E1 (Slow Relevance Pruning):** Evicts tap if $R_j(t) < \theta_{\text{evict}}$, regardless of current signal presence.
- **E2 (Slow Relevance + Obsolescence Gate):** Evicts tap only if $R_j(t) < \theta_{\text{evict}}$ AND error increases when tap is zeroed out during non-silent periods. Prevents eviction when input variance $\operatorname{Var}(x_{i_j}) \approx 0$ (quiescence).
