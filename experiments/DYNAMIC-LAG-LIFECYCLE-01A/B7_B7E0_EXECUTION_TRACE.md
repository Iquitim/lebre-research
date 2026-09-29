# B7 vs B7_E0: Execution Trace & Mechanistic Flaw Analysis
## Forensic Trace of Active Tap Lifecycles Under Channel Silence

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01A`  
**Purpose:** Explain the exact mathematical and algorithmic mechanism why B7_E0 rarely evicted taps during silence in `DYNAMIC-LAG-LIFECYCLE-01`.

---

## 1. Algorithmic Trace During Signal Silence ($t \in [3000, 7000]$ in Task D7)

In Task D7 (`D7_Quiescent_Tap`), Feature 0 is set to zero between $t=3000$ and $t=7000$:
$$X[t, 0] = 0.0, \quad \forall t \in [3000, 7000]$$
The true data-generating process is $y_t = 0.8 \cdot X[t-6, 0] + \epsilon_t$.  
Between $t=3006$ and $t=7006$, the delayed input is identically zero:
$$val = X[t-6, 0] = 0.0$$
The prediction residual is:
$$e_t = y_t - \hat{y}_t = \epsilon_t - \hat{y}_{\text{base}, t}$$

### 1.1 Weight Adaptation Equation
In `DynamicLagLifecycleModel.step()` (line 208):
$$\Delta w = \mu_{\text{lag}} \cdot e_t \cdot val = 0.05 \cdot e_t \cdot 0.0 = \mathbf{0.0}$$
Because $val = 0.0$, the gradient update is identically zero.
There is **no weight decay** ($\lambda = 0$) and **no leakage term** ($\gamma = 0$).

Therefore, for all 4,000 steps of silence:
$$w_t = w_{3006} \approx 0.800$$
The tap weight remains locked at its mature pre-quiescence magnitude ($|w| \approx 0.80 \gg 0.05$).

### 1.2 B7_E0 Eviction Condition Evaluation
In B7_E0 (lines 223–232):
```python
if abs(tap['w']) < 0.05:
    tap['zero_count'] += 1
else:
    tap['zero_count'] = 0
```
Because $|w_t| \approx 0.80 \ge 0.05$:
- `abs(tap['w']) < 0.05` evaluates to **`False`** on every single time step during silence!
- `tap['zero_count']` is reset to **`0`** on every step.
- The condition `tap['zero_count'] > 50` is **never satisfied**.
- The tap is **never evicted**.

### 1.3 Why Did B7_E0 Only Evict 3 Times Across 40 Seeds?
In 37 out of 40 runs, the promoted tap weight was stable ($|w| > 0.05$). Only in 3 seeds did pre-quiescent gradient noise or suboptimal candidate initialization produce $|w| < 0.05$, causing an eviction.
In all other 37 seeds, B7_E0's eviction logic was **completely inactive** during the silence window!

---

## 2. B7 (Two-Timescale Relevance) Behavior Under the Same Window

In B7 (lines 215–218 and 234–242):
```python
if abs(val) > 0.1:
    tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
...
if tap['R'] < self.theta_evict and tap['age'] > 300:
    if abs(val) > 0.1: # non-quiescent, truly obsolete
        tap['evict'] = True
```
During silence, $val = 0.0 < 0.1$:
- `abs(val) > 0.1` is **`False`**.
- Structural relevance $R$ is **frozen** at its pre-quiescence value ($R \approx 0.30 \gg 0.015$).
- Even if $R$ were low, the gate `if abs(val) > 0.1:` explicitly prevents eviction during channel quiescence.
- The tap survives 100% of the silence period.

---

## 3. Mechanistic Conclusion: The Ablation Was Inactive

The intended scientific comparison between B7 and B7_E0 was:
- **B7:** Protects dormant taps during quiescence via two-timescale relevance decoupling ($R$ frozen when signal absent).
- **B7_E0:** Standard magnitude/activity pruning that purges inactive/decaying taps during prolonged dormancy.

However, because B7_E0 checked $|w| < 0.05$ without any weight decay or signal activity decay, its eviction check was a no-op during silence. Both models left their mature tap weights alive during silence.

Therefore, the empirical equivalence between B7 and B7_E0 on D7 was caused by **two compound defects**:
1. **Defect 1 (Implementation):** `ABLATION_IMPLEMENTATION_INACTIVE` in B7_E0.
2. **Defect 2 (Reporting):** `REPORT_TABLE_COPY_ERROR` in `generate_dynamic_lag_reports.py`.
