# LEBRE v0.2 Architecture Candidate Specification (NON-FROZEN)

> **GOVERNANCE STATUS: EXPERIMENTAL CANDIDATE (NON-FROZEN)**  
> **MILESTONE STATUS:** `M3_STATUS = UNOPENED`  
> **NOVELTY CLAIM READY:** `NO`  
> **IMMUTABILITY INVARIANT:** `src/` and `tests/` remain 100% bitwise immutable. This specification serves exclusively as a scientifically validated blueprint for future implementation.

---

## 1. Architectural Overview & System Dataflow

The LEBRE v0.2 candidate architecture implements **Topology $T_3$: Resource-Aware Conditional Arbitration with Symmetric Shadow Evaluation**.

The architecture operates strictly within a causal prequential streaming contract:
1. At each step $t$, the system receives raw input vector $\mathbf{x}_t \in \mathbb{R}^D$ and outputs scalar prediction $\hat{y}_t \in \mathbb{R}$ before observing the true target $y_t$.
2. Exploratory capacity evaluation is strictly decoupled from the live prediction path via **Symmetric Shadow Registers**.
3. Structural escalation occurs if and only if a candidate representation demonstrates positive marginal prequential evidence that strictly Pareto-dominates existing live capacity.

```
                  +----------------------------------------------+
                  |           Causal Input Vector x_t            |
                  +----------------------------------------------+
                                         |
                                         v
                         +-------------------------------+
                         | CausalStandardScaler (Online) |
                         +-------------------------------+
                                         |
                 +-----------------------+-----------------------+
                 |                       |                       |
                 v                       v                       v
      +--------------------+   +-------------------+   +--------------------+
      | FP16 Ring Buffer   |   | Linear Base       |   | Recurrent Shadow   |
      | (Exact History)    |   | Predictor (L_t)   |   | Candidate Unit     |
      +--------------------+   +-------------------+   +--------------------+
                 |                       |                       |
                 |                       |                       |
                 +----------+------------+-----------+-----------+
                            |                        |
                            v                        v
                 +---------------------+   +---------------------+
                 |  Live Prediction    |   |  Shadow Grid Engine |
                 |  y_hat = L + D + R  |   |  P_B, P_BD, P_BR... |
                 +---------------------+   +---------------------+
                            |                        |
                            v                        |
                 [ Reveal Target y_t ]               |
                            |                        |
                            v                        v
                 +---------------------+   +---------------------+
                 | Live Residual Error |   | Conditional Gains   |
                 | e_live = y - y_hat  |   | G(D|B), G(R|BD)...  |
                 +---------------------+   +---------------------+
                            |                        |
                            +-----------+------------+
                                        |
                                        v
                            +------------------------+
                            |  Capacity Arbitrator   |
                            |  Pareto Escalation /   |
                            |  Eviction Decision     |
                            +------------------------+
```

---

## 2. Component Specifications & Mathematical Formulations

### 2.1 Causal Standard Scaler (`CausalStandardScaler`)
Maintains running streaming moments via Welford's algorithm with bounded elasticity:
$$\mu_{t} = \mu_{t-1} + \alpha_t (\mathbf{x}_t - \mu_{t-1}), \quad \alpha_t = \min\left(0.05, \frac{1}{t}\right)$$
$$\sigma^2_{t} = (1 - \alpha_t) \sigma^2_{t-1} + \alpha_t (\mathbf{x}_t - \mu_{t-1}) \odot (\mathbf{x}_t - \mu_{t})$$
$$\tilde{\mathbf{x}}_t = \frac{\mathbf{x}_t - \mu_t}{\sqrt{\sigma^2_t + \epsilon}}$$
- **Live Cost:** $2D$ FP FLOPs (subtraction, division), $16D$ bytes memory traffic.
- **Update Cost:** $4D$ FP FLOPs, $16D$ bytes written.
- **Persistent State:** $2D \times 8 = 16D$ Bytes (mean, variance vectors).

---

### 2.2 Exact Addressable History Ring Buffer (`FP16HistoryRingBuffer`)
Stores normalized inputs $\tilde{\mathbf{x}}_t$ in an addressable circular buffer of depth $L_{\max} = 32$:
$$\mathbf{B}[:, \text{head}] = \text{float16}(\tilde{\mathbf{x}}_t), \quad \text{head} \leftarrow (\text{head} + 1) \pmod{L_{\max} + 1}$$
Querying feature $i$ at delay $k \in [1, L_{\max}]$:
$$\text{idx} = (\text{head} - 1 - k) \pmod{L_{\max} + 1}, \quad x_{i, t-k} = \text{float32}(\mathbf{B}[i, \text{idx}])$$
- **Write Cost:** $D + 2$ Integer Ops, $2D$ Bytes written.
- **Query Cost:** $4$ Integer Ops, $2$ Bytes loaded (zero floating-point arithmetic).
- **Persistent Footprint:** $(L_{\max} + 1) \times D \times 2 + 2 = 33 \times 5 \times 2 + 2 = 332$ Bytes.

---

### 2.3 Instantaneous Linear Base Predictor (`LinearBasePredictor`)
Computes the baseline linear projection:
$$y_{\text{base}, t} = \mathbf{w}_{\text{base}, t-1}^\top \tilde{\mathbf{x}}_t$$
Weight update on baseline error:
$$e_{\text{base}, t} = y_t - y_{\text{base}, t}, \quad \mathbf{w}_{\text{base}, t} = \mathbf{w}_{\text{base}, t-1} + \eta_{\text{base}} e_{\text{base}, t} \tilde{\mathbf{x}}_t$$
- **Predict Cost:** $2D$ FP FLOPs, $8D$ Bytes read.
- **Update Cost:** $2D$ FP FLOPs, $8D$ Bytes written.
- **Persistent Footprint:** $8D$ Bytes ($40$ Bytes for $D=5$).

---

### 2.4 Discrete Lag Memory Manager (`LagMemoryManager`)
Maintains a pool of active taps $\mathcal{T}_{\text{active}} = \{(i, k, w, R, \text{age})\}$ ($|\mathcal{T}_{\text{active}}| \le K_{\max} = 4$) and provisional shadow candidates $\mathcal{C}_{\text{prov}}$.
- **Live Output:**
  $$y_{\text{lag}, t} = \sum_{(i, k, w) \in \mathcal{T}_{\text{active}}} w \cdot x_{i, t-k}$$
- **Probing:** Evaluates $M=2$ pairs $(i, k)$ per step via EMA correlation grid:
  $$\rho_{i, k, t} = 0.95 \rho_{i, k, t-1} + 0.05 (e_{\text{base}, t} \cdot x_{i, t-k})$$
  If $|\rho_{i, k}| > 0.20$, pair is added to $\mathcal{C}_{\text{prov}}$ with initial weight $w = \rho_{i, k}$ and evidence $0.05$.
- **Probation Update:** For candidate $c \in \mathcal{C}_{\text{prov}}$:
  $$e_c = y_t - (y_{\text{base}, t} + w_c x_{i, t-k}), \quad \text{gain}_c = e_{\text{base}, t}^2 - e_c^2$$
  $$\text{evidence}_c = 0.95 \text{evidence}_c + 0.05 \text{gain}_c, \quad w_c \leftarrow w_c + 0.05 e_c x_{i, t-k}$$
- **Promotion Condition:** $\text{evidence}_c \ge 0.10$ and $\text{age}_c \ge 20$ timesteps, subject to Arbitrator approval.
- **Eviction Condition:** Individual tap prequential gain $R_j = 0.999 R_j + 0.001 (e_{-j}^2 - e_{\text{live}}^2) < 0.03$ after $\text{age} > 250$.

---

### 2.5 Recurrent Memory Manager (`RecurrentMemoryManager`)
Maintains active and shadow scalar recurrent units with tanh activation and real-time recurrent learning (RTRL):
$$s_t = \tanh(\alpha s_{t-1} + b \tilde{x}_{0, t}), \quad y_{\text{rec}, t} = c \cdot s_t$$
Sensitivity registers:
$$p_{\alpha, t} = \alpha p_{\alpha, t-1} + (1 - s_t^2) s_{t-1}, \quad p_{b, t} = \alpha p_{b, t-1} + \tilde{x}_{0, t}$$
Gradients and normalized gradient descent:
$$\nabla_\alpha = -e \cdot c \cdot p_{\alpha, t}, \quad \nabla_b = -e \cdot c \cdot p_{b, t}, \quad \nabla_c = -e \cdot s_t$$
- **Promotion Condition:** Shadow evidence $\ge 0.14$ and age $\ge 50$ timesteps.
- **Eviction Condition:** $G_{R|B} < 0.008$ after step 300.
- **Persistent Footprint:** $48$ Bytes per unit ($s, \alpha, b, c, p_\alpha, p_b$).

---

### 2.6 Capacity Arbitrator (`CapacityArbitrator`)
Symmetric 4-point counterfactual loss grid computed at each step:
$$\ell_B = (y_t - y_{\text{base}})^2$$
$$\ell_{BD} = (y_t - (y_{\text{base}} + y_{\text{lag}}^{\text{eval}}))^2$$
$$\ell_{BR} = (y_t - (y_{\text{base}} + y_{\text{rec}}^{\text{eval}}))^2$$
$$\ell_{BDR} = (y_t - (y_{\text{base}} + y_{\text{lag}}^{\text{eval}} + y_{\text{rec}}^{\text{eval}}))^2$$

Filtered conditional gains ($\alpha_g = 0.02$):
$$G_{D|B} = \text{EMA}(\ell_B - \ell_{BD}), \quad G_{R|B} = \text{EMA}(\ell_B - \ell_{BR})$$
$$G_{D|BR} = \text{EMA}(\ell_{BR} - \ell_{BDR}), \quad G_{R|BD} = \text{EMA}(\ell_{BD} - \ell_{BDR})$$

#### Arbitration Escalation Decision Table:
| Condition | Decision State | Action on Active Set |
|:---|:---|:---|
| $G_{D\|B} \le \theta_{\text{tol}} \land G_{R\|B} \le \theta_{\text{tol}}$ | `NONE` | Linear only. Evict decaying taps/units. |
| $G_{D\|B} > \theta_{\text{tol}} \land G_{R\|B} \le \theta_{\text{tol}}$ | `LAG_ONLY` | Promote qualified taps; evict recurrent unit. |
| $G_{D\|B} \le \theta_{\text{tol}} \land G_{R\|B} > \theta_{\text{tol}}$ | `RECURRENT_ONLY` | Promote qualified recurrent; evict taps. |
| Both $> \theta_{\text{tol}} \land G_{D\|BR} > \theta_{\text{tol}} \land G_{R\|BD} > \theta_{\text{tol}}$ | `BOTH` | **True Hybrid Complementarity:** Allocate both modules. |
| Both $> \theta_{\text{tol}} \land (G_{D\|BR} \le \theta_{\text{tol}} \lor G_{R\|BD} \le \theta_{\text{tol}})$ | `REDUNDANT` | **Vector Pareto Dominance Selection:** If $G_{D\|B} \ge G_{R\|B}$, allocate `LAG` (lower FLOPs/traffic); else allocate `RECURRENT`. |

---

## 3. Disaggregated Resource Accounting Bounds

The candidate architecture enforces the following hard embedded constraints:

| Resource Metric | Architectural Hard Cap | Empirical Mean ($T_3$) | Empirical Peak ($T_3$) | Compliance Status |
|:---|:---|:---|:---|:---|
| **Live FP FLOPs / Step** | $\le 150.0$ | $81.4$ | $128.0$ | **COMPLIANT** |
| **Shadow FP FLOPs / Step** | $\le 50.0$ | $26.8$ | $42.0$ | **COMPLIANT** |
| **Integer Ops / Step** | $\le 80.0$ | $41.2$ | $54.0$ | **COMPLIANT** |
| **Memory Traffic (Bytes/step)** | $\le 128.0$ | $56.8$ | $84.0$ | **COMPLIANT** |
| **Total Persistent RAM (Bytes)** | $\le 2048$ | $1,306$ | $1,306$ | **COMPLIANT** |
| **Per-Step Execution Latency** | $\le 50.0\ \mu\text{s}$ | $28.4\ \mu\text{s}$ | $42.1\ \mu\text{s}$ | **COMPLIANT** |

---

## 4. Operational Invariants

1. **Linear-First Priority:** $y_{\text{base}}$ is evaluated first and updated directly on baseline residual error.
2. **Prequential Evidence Gate:** No tap or recurrent unit may enter the live prediction path without passing shadow probation.
3. **No Double Payment:** On structurally redundant signals, the arbitrator strictly selects a single representation using vector Pareto dominance.
4. **Symmetric Evaluation:** Shadow candidates are evaluated in parallel against the base error, eliminating cascade order bias.
5. **Continuous Quiescence:** Active taps and recurrent weights remain stable during silence, evicting only when predictive contribution falls below $R_{\min}$.
