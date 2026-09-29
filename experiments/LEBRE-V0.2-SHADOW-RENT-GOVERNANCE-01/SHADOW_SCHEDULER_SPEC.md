# Architectural & Algorithmic Specification: Shadow-Rent Schedulers

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** Algorithmic Definitions, Execution Semantics, and State Machines for $S_0, S_1, S_2, S_3$  
**Author:** Independent Skeptical Senior Researcher  
**Status:** FROZEN ALGORITHMIC SPECIFICATION  

---

## 1. Architectural Overview & Single-Difference Invariant

All four evaluated configurations are implemented within a unified class architecture (`GovernedLEBREModel`), ensuring that live execution, causal scaling, circular ring buffering, base linear prediction, active discrete delay filtering, and active recurrent filtering execute with bitwise identical logic. The sole experimental intervention is the schedule governing the execution of the removable counterfactual shadow exploration block.

```
+-------------------------------------------------------------------------------------------------+
| CANONICAL STREAM STEP t                                                                         |
|                                                                                                 |
|   1. Scaler Transform: x_norm = scaler.transform(x_raw)                          [LIVE]        |
|   2. History Buffer Write: history.write(x_norm)                                 [SHARED]      |
|   3. Base Linear Prediction: y_base = base.predict(x_norm)                       [LIVE]        |
|   4. Active Lag Prediction: y_lag_live = sum(w * x_delayed)                      [LIVE]        |
|   5. Active Recurrent Forward: y_rec_live = active_rec.forward(x_norm[0])         [LIVE]        |
|   6. Aggregate Live Prediction: y_hat_live = y_base + y_lag_live + y_rec_live     [LIVE]        |
|   7. Reveal y_true, compute e_live = y_true - y_hat_live, ell_live = e_live^2     [LIVE]        |
|   8. Base Linear Update: base.update(x_norm, y_true - y_base)                    [LIVE]        |
|   9. Active Lag Updates & Leave-One-Out Eviction Checks                          [LIVE/LIFE]   |
|  10. Active Recurrent RTRL Update                                                [LIVE]        |
|  11. Causal Scaler Welford Update: scaler.update(x_raw)                          [LIVE]        |
|                                                                                                 |
|  12. SCHEDULER STATE EVALUATION: Query is_shadow_awake(t)?                      [SCHEDULER]   |
|         |                                                                                       |
|         +---> IF AWAKE: Execute Full Removable Shadow Block                      [SHADOW]      |
|         |       - Form shadow candidate predictions (P_BASE_D, P_BASE_R, P_BASE_DR)             |
|         |       - Evaluate counterfactual losses & conditional gains (G_D|B, G_R|B, ...)        |
|         |       - Filter conditional gain EMAs (alpha_g = 0.02)                                  |
|         |       - Shadow recurrent forward pass, RTRL update, and evidence EMA                  |
|         |       - Provisional candidate LMS updates & evidence EMAs                              |
|         |       - Background 2-probe delay correlation updates (FP16 storage)                   |
|         |       - Candidate admission & arbitration promotion into active sets                   |
|         |       - Stale candidate pruning                                                       |
|         |                                                                                       |
|         +---> IF ASLEEP: Completely Skip Shadow Block                             [SLEEP]       |
|                 - All shadow learner states, weights, and EMAs remain frozen                     |
|                 - Zero FLOPs and zero memory bus reads/writes to shadow path                     |
|                 - No pseudo-observations or synthetic evidence generated                        |
+-------------------------------------------------------------------------------------------------+
```

---

## 2. Formal Scheduler Definitions

### 2.1 Scheduler $S_0$ — Continuous Shadow Reference (Baseline)
- **Execution Rule:** $\mathbb{I}_{\text{shadow}}(t) \equiv 1$ for all $t$.
- **Shadow Duty Fraction:** $1.0000$ ($100\%$).
- **Expected Total Online FP:** $\approx 167.70 \text{ FLOPs/step}$.
- **Role:** Scientific behavioral gold standard against which predictive non-inferiority and adaptation latency are measured.

---

### 2.2 Scheduler $S_1$ — Shadow-Off Negative Control
- **Execution Rule:** $\mathbb{I}_{\text{shadow}}(t) \equiv 0$ for all $t$.
- **Shadow Duty Fraction:** $0.0000$ ($0\%$).
- **Expected Total Online FP:** $\approx 81.17 \text{ FLOPs/step}$.
- **Role:** Mechanistic diagnostic establishing the degree to which continuous or intermittent shadow exploration is causally necessary for temporal discovery and regime adaptation.

---

### 2.3 Scheduler $S_2$ — Periodic Budgeted Shadow
- **Execution Rule:**
  $$\mathbb{I}_{\text{shadow}}(t) = \begin{cases} 1, & \text{if } t \equiv 0 \pmod 5 \\ 0, & \text{otherwise} \end{cases}$$
- **Governing Parameter:** $K = 5$ (derived analytically from the 100-FLOP ceiling).
- **Shadow Duty Fraction:** $0.2000$ ($20.0\%$, 200 shadow executions per 1,000 steps).
- **Expected Total Online FP:** $\approx 98.47 \text{ FLOPs/step}$.
- **Scheduler Computational Overhead:** $0.0 \text{ FP FLOPs}$, $1 \text{ Integer Modulo Op}$, $0 \text{ Memory Bus Traffic}$.
- **Scheduler Memory Footprint:** $4 \text{ Bytes}$ (`uint16 period_K`, `uint16 step_counter`).

---

### 2.4 Scheduler $S_3$ — Event-Triggered + Heartbeat Shadow
$S_3$ combines a low-cost prequential loss sequential change sentinel with a deterministic anti-starvation heartbeat.

#### 2.4.1 Sentinel Input & State Variables
- **Input:** Instantaneous prequential squared error:
  $$\ell_{\text{live}}(t) = (y_t - \hat{y}_t)^2$$
- **Baseline Reference Loss EMA ($\bar{\ell}_t$):**
  $$\bar{\ell}_t = (1 - \alpha_{\ell}) \bar{\ell}_{t-1} + \alpha_{\ell} \ell_{\text{live}}(t), \quad \alpha_{\ell} = 0.01$$
- **Page-Hinkley Cumulative Positive Deviation ($U_t$):**
  $$d_t = \ell_{\text{live}}(t) - (\bar{\ell}_{t-1} + \delta)$$
  $$U_t = \max(0.0, U_{t-1} + d_t)$$
  where $\delta$ is the insensitivity slack parameter.
- **Alarm Threshold ($\lambda$):** An event alarm is triggered whenever:
  $$U_t > \lambda$$

#### 2.4.2 Wake-Burst Semantics
When an event alarm fires:
1. Reset the cumulative statistic: $U_t \leftarrow 0.0$.
2. Wake the full shadow block for a continuous burst of $W$ steps:
   $$C_{\text{burst}} \leftarrow W = 50 \text{ steps}$$
3. Reset the heartbeat counter: $C_{\text{hb}} \leftarrow 0$.
4. **Trigger During Burst Rule:** `IGNORE`. Any secondary threshold breaches occurring while $C_{\text{burst}} > 0$ are discarded, preventing recursive runaway bursts.

#### 2.4.3 Anti-Starvation Heartbeat Mechanism
To prevent prolonged structural blindness in regimes where changes occur without an immediate large error spike:
1. At each step where the shadow block is asleep, increment the heartbeat counter:
   $$C_{\text{hb}} \leftarrow C_{\text{hb}} + 1$$
2. When $C_{\text{hb}} \ge H$:
   - Trigger a heartbeat wake event.
   - Reset $C_{\text{hb}} \leftarrow 0$.
   - Wake the shadow block for a single evaluation step ($W_{\text{hb}} = 1$) or short inspection burst.
   - Set wake reason code: `WAKE_HEARTBEAT`.

#### 2.4.4 Scheduler Computational Cost Accounting
At every stream step, evaluating the sentinel incurs:
- 1 EMA update: $(1 - \alpha) \bar{\ell} + \alpha \ell$ ($2 \text{ FLOPs}$)
- 1 slack subtraction: $\ell - (\bar{\ell} + \delta)$ ($2 \text{ FLOPs}$)
- 1 accumulation: $U + d$ ($1 \text{ FLOP}$)
- 2 threshold checks: $U > 0$ and $U > \lambda$ ($2 \text{ Integer Ops}$)
Total Sentinel Compute: **$5.0 \text{ FLOPs/step}$** and **$2 \text{ Integer Ops/step}$**, accounted explicitly in `res.fp_flops`.

#### 2.4.5 Scheduler Memory Footprint
Total persistent memory is exactly **$16 \text{ Bytes}$** (as cataloged in `SCHEDULER_MEMORY_LEDGER.csv`), utilizing 0 Bytes of heap workspace.
