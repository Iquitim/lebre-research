# Milestone Specification: Autonomous Single-State Recurrent Core (M2-SINGLE-STATE-SPEC)

**Document Version:** 1.0.0  
**Effective Date:** 2026-09-19  
**Status:** Certified / Frozen with Documented Scope Limits  
**Milestone:** Milestone M2 — Autonomous Recurrent State Discovery & Lifecycle Management  
**Governance Authority:** Section 83 Protocol & Track-B Milestone Review Board  

---

## 1. Architectural Scope and Purpose

This specification formally establishes the canonical reference architecture and operational standards for the **Milestone M2 Single-State Recurrent Core**. 

Milestone M2 establishes an autonomous, online, causal learner capable of discovering when recurrent temporal memory is needed, synthesizing a single minimal scalar state, learning state transition dynamics online, selecting the parsimonious state structure (Linear vs. Gated), maintaining forward sensitivity traces, and evicting the state when obsolete to reclaim compute and memory—all **without oracle regime signals, backpropagation through time (BPTT), offline replay buffers, or human supervision**.

```
                   [ No Recurrent State (Dense / Sparse NLMS) ]
                                      |
                      Residual Error Accumulator (E_linear)
                                      |
                     [ Autonomous Birth (Provisional) ]
                                      |
                       20-Step Probation Evaluation
                                      |
                   +------------------+------------------+
                   |                                     |
         [ Linear Scalar State ]               [ Gated Scalar State ]
         (Stationary Decay: h_t)              (Discrete Hold: h_t)
                   |                                     |
                   +------------------+------------------+
                                      |
                      Causal Sensitivity Tracking (S_t)
                                      |
                   [ Active / Mature Recurrent Operation ]
                                      |
           Temporal C x O_struct + Obsolescence Accumulator (O_obs)
                                      |
                     [ Causal Hysteresis Eviction ]
                                      |
                       Physical Deletion & Reclaim
```

### Core Invariants:
1. **Strict Single-State Constraint:** $\text{MAX\_ACTIVE\_STATES} = 1$, $\text{MAX\_PROVISIONAL\_STATES} = 1$, $\text{STATE\_DIM} = 1$. Multi-state capacity is deferred to Milestone M3.
2. **Strict Parsimony Order:** Linear state representation is evaluated first. Gated state representation is deployed only when linear dynamics fail to resolve temporal residual error.
3. **Causal Operation:** Zero access to future inputs, zero access to oracle regime boundary labels, and zero non-causal smoothing.

---

## 2. Mathematical State Formulations

### 2.1 Linear Scalar Recurrent State
For input vector $x_t \in \mathbb{R}^D$, feature weight $w_{u} \in \mathbb{R}^D$, scalar state $h_t \in \mathbb{R}$, recurrent persistence $\lambda \in [0, 1)$, and readout weight $w_s \in \mathbb{R}$:

$$\text{Input Drive: } u_t = w_u^\top x_t$$
$$\text{State Forward: } h_t = \lambda h_{t-1} + u_t$$
$$\text{Readout Contribution: } \hat{y}_{\text{rec}, t} = w_s h_t$$

#### Parameter Updates (Online Gradient Descent):
$$\text{Error: } e_t = y_t - (\hat{y}_{\text{feedforward}, t} + \hat{y}_{\text{rec}, t})$$
$$\text{Forward Sensitivity Trace: } S_t = \lambda S_{t-1} + u_{t-1}$$
$$\Delta w_s = \eta_s \cdot e_t \cdot h_t$$
$$\Delta \lambda = \eta_\lambda \cdot e_t \cdot w_s \cdot S_t, \quad \text{clipped to } [0.0, 0.99]$$
$$\Delta w_u = \eta_u \cdot e_t \cdot w_s \cdot x_t$$

### 2.2 Gated Scalar Recurrent State
For input vector $x_t \in \mathbb{R}^D$, candidate input $c_t$, and candidate gate trigger $g_t$:

$$c_t = w_c^\top x_t$$
$$g_t = \sigma(w_g^\top x_t + b_g)$$
$$\text{State Forward: } h_t = (1 - g_t) h_{t-1} + g_t c_t$$
$$\text{Readout Contribution: } \hat{y}_{\text{rec}, t} = w_s h_t$$

#### Parameter Updates:
$$\Delta w_s = \eta_s \cdot e_t \cdot h_t$$
$$\Delta w_c = \eta_c \cdot e_t \cdot w_s \cdot g_t \cdot x_t$$
$$\Delta w_g = \eta_g \cdot e_t \cdot w_s \cdot (c_t - h_{t-1}) \cdot g_t(1 - g_t) \cdot x_t$$

---

## 3. Autonomous Lifecycle Mechanisms

### 3.1 Autonomous State Birth
Birth is triggered when feedforward linear prediction exhibits persistent, temporally correlated residual errors:
$$E_{\text{linear}, t} = (1 - \alpha_e) E_{\text{linear}, t-1} + \alpha_e \cdot e_t^2$$
If $E_{\text{linear}, t} > \theta_{\text{birth}}$ for $N_{\text{birth}}$ consecutive steps, a new provisional state candidate is initialized in `PROVISIONAL` status.

### 3.2 Probation & Dynamic Type Selection
- **Probation Horizon:** $T_{\text{prob}} = 20$ stream steps.
- **Evaluation:** During probation, candidate states learn parameters but do not contribute to live primary predictions.
- **Parsimony Order:**
  1. A `LinearScalarState` is instantiated first.
  2. If candidate MSE improves over feedforward baseline by $\ge \delta_{\text{promote}}$ ($15\%$), the linear state is promoted to `ACTIVE`.
  3. If the linear state fails probation, a `GatedScalarState` is provisionally tested.
  4. If the gated state satisfies probation, it is promoted to `ACTIVE`. Otherwise, the candidate is discarded.

### 3.3 Causal Retention Metric ($U_{\text{ret}}$)
Retention utility balances causal sensitivity and structural recurrence observability:
$$C_t = |e_t \cdot w_s \cdot h_t| \quad \text{(Instantaneous Causal Sensitivity)}$$
$$O_{\text{struct}, t} = |w_s| \cdot (|h_t| + \sigma_h) \quad \text{(Structural Observability)}$$
$$U_{\text{inst}, t} = C_t \cdot O_{\text{struct}, t}$$
$$U_{\text{ret}, t} = (1 - \alpha_{\text{slow}}) U_{\text{ret}, t-1} + \alpha_{\text{slow}} \cdot U_{\text{inst}, t}$$
- **Slow Timescale:** $\alpha_{\text{slow}} = 0.005$ ($\tau_{\text{ret}} \approx 140$ steps) to bridge long Poisson quiescence intervals.

### 3.4 Positive Obsolescence Accumulator ($O_{\text{obs}}$)
To distinguish passive silence from true structural obsolescence:
$$z_t = \mathbf{1}\left[ \|x_t\|_\infty < \epsilon_x \land |\hat{y}_{\text{rec}, t}| < \epsilon_y \right]$$
$$O_{\text{obs}, t} = (1 - \beta_{\text{obs}}) O_{\text{obs}, t-1} + \beta_{\text{obs}} \cdot z_t$$
where $\beta_{\text{obs}} = 0.02$, $\epsilon_x = 0.10$, $\epsilon_y = 0.05$.

### 3.5 Causal Hysteresis Eviction Rule
An active state is marked for eviction when:
$$U_{\text{ret}, t} < \theta_{\text{ret}} \quad \text{AND} \quad O_{\text{obs}, t} > \theta_{\text{obs}}$$
This condition must hold continuously for $\text{patience} = 30$ steps. Upon trigger:
1. State is immediately transitioned to `EVICTED`.
2. State memory is reclaimed and arrays are physically freed.
3. Learner returns to pure feedforward state-free computation.

---

## 4. Resource Ceilings & Computational Budget

All implementations conforming to `M2-SINGLE-STATE-SPEC` must execute strictly within the following ceilings:

| Component | State-Free Baseline | Active Linear State | Active Gated State | Strict Ceiling |
| :--- | :---: | :---: | :---: | :---: |
| **Forward Pass FLOPs** | $2D$ | $2D + 5$ | $3D + 8$ | **$\le 38$ FLOPs** ($D=10$) |
| **Parameter Update FLOPs**| $2D + 2$ | $4D + 12$ | $5D + 18$ | **$\le 68$ FLOPs** ($D=10$) |
| **Amortized Total FLOPs** | $48.5$ FLOPs/step | $50.1$ FLOPs/step | $51.2$ FLOPs/step | **$\le 55.0$ FLOPs/step** |
| **State Memory Overhead** | $0$ bytes | $12$ bytes | $24$ bytes | **$\le 145$ bytes RAM** |
| **State Capacity ($K$)** | $0$ | $1$ | $1$ | **Strictly $K \le 1$** |

---

## 5. Scope Limits & Operational Boundary Conditions

This specification is certified under explicit operational boundaries established during the M2-R1 audit:

### 5.1 Certified Operational Regimes
1. **Regime Duration Horizon:** $\ge 500$ steps per stationary phase.
2. **Quiescent Event Gaps:** Successfully bridges Poisson silence intervals up to $250$ steps with $P(\text{retention}) > 99.0\%$.
3. **Regime Switching Latency:** Expected eviction latency of $250 - 350$ steps upon entering true state-free regimes. On phases $> 2,000$ steps, stale retention overhead is guaranteed $\le 10.0\%$.
4. **Predictive Accuracy:** Global MSE within $1.02\times$ of non-causal Oracle baseline.

### 5.2 Documented Scope Limitations (Out-of-Scope)
1. **Micro-Regimes ($< 200$ steps):** Eviction latency exceeds regime duration; learner will linger across rapid phase shifts.
2. **Ultra-Sparse Events ($p_{\text{event}} < 0.003$):** Quiescent gaps exceeding $350$ steps may suffer premature eviction under default parameters.
3. **Simultaneous Multi-Timescale Memory:** Systems requiring two or more concurrent recurrence dynamics ($\lambda_1 \neq \lambda_2$) cannot be represented by this single-state core and require multi-state capacity (Milestone M3).

---

## 6. Audit & Conformance Authority

Conformance with `M2-SINGLE-STATE-SPEC` is validated by executing the test suite in `tests/test_m2_r1.py`. Modifications to state equations, probation rules, or type-selection hierarchies are prohibited under Milestone M2 freeze protocol.
