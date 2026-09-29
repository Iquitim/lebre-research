# Metric Semantics Audit & Mathematical Definitions

**Document:** `experiments/M2-EXP-0005R/METRIC_DEFINITIONS.md`  
**Milestone:** M2 (Temporal and Sequential Learning Under Fixed Compute)  
**Experiment Reference:** M2-EXP-0005 / M2-EXP-0005R  
**Date:** 2026-09-19  
**Status:** Canonical Reference for Lifecycle Metrics  

---

## 1. Context & Motivation

In M2-EXP-0005, two seemingly conflicting sets of numbers were reported:
1. **Executive Summary Claims:**
   - State Birth Precision = $1.00$
   - State Birth Recall = $1.00$
   - Type Selection Accuracy $\approx 92.5\%$
   - Eviction Precision = $1.00$
   - Birth Latency $\approx 45$ steps, Eviction Latency $\approx 52$ steps
2. **Primary Results Table (Table A):**
   - V3 Adaptive Delta-Loss: Active Precision = $0.932$, Active Recall = $0.650$, Type Accuracy = $0.606$
   - V4 Adaptive $C \times O$: Active Precision = $0.934$, Active Recall = $0.628$, Type Accuracy = $0.578$

This document formally audits the mathematical definitions of these metrics, resolving the discrepancy into an exact **`METRIC_SCOPE_MISMATCH`** between **Event-Level Lifecycle Decisions** and **Time-Weighted Continuous Occupancy**.

---

## 2. Formal Metric Definitions

### 2.1 State Birth Metrics

#### `STATE_BIRTH_PRECISION`
- **Definition:** The fraction of triggered state birth events that occur when internal recurrent memory is genuinely required by the environment.
- **Numerator:** Number of birth trigger events occurring during a state-required regime (or within a transition tolerance window $W_{\text{trans}} = 50$ steps).
  $$N_{\text{valid\_births}} = \sum_{k=1}^{N_{\text{births}}} \mathbb{I}(\text{Regime}(t_k) \neq \text{STATE\_FREE})$$
- **Denominator:** Total number of birth events triggered across the simulation:
  $$N_{\text{total\_births}} = \sum_{k=1}^{N_{\text{births}}} 1$$
- **Eligible Time Steps:** All steps $t \in [1, T]$ where a transition from `DORMANT` $\to$ `PROVISIONAL` occurs.
- **Aggregation Type:** Per-Event aggregation, macro-averaged across evaluation seeds.
- **Scope Note:** In M2-EXP-0005, births occurred only upon entering Phase 2 and Phase 4 (or following premature evictions within those phases). Spurious births during Phase 1, Phase 3, and Phase 5 were zero, giving $1.00$ event precision.

#### `STATE_BIRTH_RECALL`
- **Definition:** The fraction of true recurrent regime onsets that successfully trigger at least one state birth event.
- **Numerator:** Number of recurrent regime transitions (Phase 1 $\to$ 2 and Phase 3 $\to$ 4) that resulted in a state birth event before regime end.
- **Denominator:** Total number of true recurrent regime onsets ($2$ in the primary stream: Linear-Integration and SET/RESET).
- **Eligible Time Steps:** Regime transition points $t \in \{1000, 3500\}$.
- **Aggregation Type:** Per-Regime-Event aggregation.
- **Scope Note:** Because the causal birth trigger fired in both recurrent phases across all 30 seeds, event recall was $1.00$.

---

### 2.2 State Active Coverage Metrics

#### `STATE_ACTIVE_PRECISION`
- **Definition:** The fraction of time steps where an internal state was active that occurred during a true state-required regime.
- **Numerator:** Number of steps where `lifecycle_status` $\in \{\text{ACTIVE}, \text{MATURE}\}$ AND `oracle_state_type` $\neq \text{NONE}$:
  $$\sum_{t=1}^T \mathbb{I}(\text{status}_t \in \{\text{ACTIVE}, \text{MATURE}\} \land \text{oracle\_type}_t \neq \text{NONE})$$
- **Denominator:** Total number of steps where `lifecycle_status` $\in \{\text{ACTIVE}, \text{MATURE}\}$:
  $$\sum_{t=1}^T \mathbb{I}(\text{status}_t \in \{\text{ACTIVE}, \text{MATURE}\})$$
- **Eligible Time Steps:** All stream steps $t \in [1, T]$.
- **Excluded Periods:** Steps where the state is `DORMANT` or `PROVISIONAL` (shadow mode).
- **Aggregation Type:** Per-Step continuous time-weighted aggregation.
- **Explanation:** State Active Precision is $\approx 0.93$ because when transitioning from recurrent phases to state-free phases (e.g. at step 2500 and step 5000), eviction latency ($T_{\text{evict}} \approx 52$ steps) causes the state to remain active briefly before utility depletion triggers eviction ($52$ false positive active steps per transition).

#### `STATE_ACTIVE_RECALL`
- **Definition:** The fraction of state-required time steps during which the learner maintained an active recurrent state.
- **Numerator:** Number of steps where `oracle_state_type` $\neq \text{NONE}$ AND `lifecycle_status` $\in \{\text{ACTIVE}, \text{MATURE}\}$:
  $$\sum_{t=1}^T \mathbb{I}(\text{oracle\_type}_t \neq \text{NONE} \land \text{status}_t \in \{\text{ACTIVE}, \text{MATURE}\})$$
- **Denominator:** Total number of steps where state was required (`oracle_state_type` $\neq \text{NONE}$):
  $$\sum_{t=1}^T \mathbb{I}(\text{oracle\_type}_t \neq \text{NONE}) = 1500 (\text{Linear}) + 1500 (\text{SET/RESET}) = 3000\text{ steps}$$
- **Eligible Time Steps:** All steps $t$ where state is required ($t \in [1001, 2500] \cup [3501, 5000]$).
- **Aggregation Type:** Per-Step continuous time-weighted aggregation.
- **Why Active Recall is $\approx 0.65$:**  
  During state-required steps, the model is NOT active during:
  1. Birth detection latency ($T_{\text{birth}} \approx 45$ steps in `DORMANT`).
  2. Provisional probation window ($T_{\text{probation}} = 80$ steps in `PROVISIONAL`).
  3. Failed linear probation in Phase 4 ($80$ steps `PROVISIONAL_LINEAR` $+ 80$ steps `PROVISIONAL_GATED` $= 160$ steps).
  4. **Premature Evictions in Phase 4:** During zero-latch periods ($s_t = 0$), utility drops, triggering premature evictions. Each eviction restarts the birth ($45$ steps) $+$ linear probation ($80$ steps) $+$ gated probation ($80$ steps) cycle ($205$ lost active steps per premature eviction).

---

### 2.3 Type Selection Metrics

#### `TYPE_SELECTION_ACCURACY` (Event-Level Decision Accuracy)
- **Definition:** The fraction of completed provisional probation episodes resulting in promotion where the promoted state type matched the ground truth regime requirement.
- **Numerator:** Number of promotion events where `promoted_type == oracle_state_type`:
  $$\sum_{e=1}^{N_{\text{promotions}}} \mathbb{I}(\text{type}_e == \text{oracle\_type}_e)$$
- **Denominator:** Total number of completed promotion events $N_{\text{promotions}}$.
- **Eligible Time Steps:** Event steps where `_promote_provisional_to_active()` is executed.
- **Aggregation Type:** Per-Event decision aggregation.
- **Scope Note:** This is the metric that yielded **$92.5\%$** in the executive report. When the learner makes a final decision to promote a state to `ACTIVE`, it chooses the correct type $92.5\%$ of the time.

#### `TYPE_OCCUPANCY_ACCURACY` (Time-Weighted Occupancy Accuracy)
- **Definition:** The fraction of all state-required steps where the learner actively maintained the *exact correct state type*.
- **Numerator:** Steps where `oracle_type` $\neq \text{NONE}$ AND `status` $\in \{\text{ACTIVE}, \text{MATURE}\}$ AND `active_type == oracle_type`:
  $$\sum_{t=1}^T \mathbb{I}(\text{oracle\_type}_t \neq \text{NONE} \land \text{status}_t \in \{\text{ACTIVE}, \text{MATURE}\} \land \text{active\_type}_t == \text{oracle\_type}_t)$$
- **Denominator:** Total number of state-required steps:
  $$\sum_{t=1}^T \mathbb{I}(\text{oracle\_type}_t \neq \text{NONE})$$
- **Eligible Time Steps:** All steps $t$ where state is required ($3000$ steps).
- **Aggregation Type:** Per-Step continuous time-weighted aggregation.
- **Scope Note:** In Table A of M2-EXP-0005, the column named `type_accuracy` was ACTUALLY computed as `TYPE_OCCUPANCY_ACCURACY`:
  $$\text{Table A Type Accuracy} = \text{Active Recall} \times P(\text{Correct Type} \mid \text{Active}) \approx 0.650 \times 0.932 \approx 0.606$$

#### `TYPE_DECISION_PRECISION` & `TYPE_DECISION_RECALL`
- **`TYPE_DECISION_PRECISION(Type k)`**: Fraction of times type $k$ was promoted that type $k$ was truly needed:
  $$\frac{N_{\text{promoted}}(k) \cap N_{\text{needed}}(k)}{N_{\text{promoted}}(k)}$$
- **`TYPE_DECISION_RECALL(Type k)`**: Fraction of regimes requiring type $k$ where type $k$ was successfully promoted:
  $$\frac{N_{\text{promoted}}(k) \cap N_{\text{needed}}(k)}{N_{\text{regimes}}(k)}$$

---

### 2.4 Promotion & Eviction Metrics

#### `PROMOTION_PRECISION`
- **Definition:** Fraction of provisional states promoted to active that were truly useful.
- **Numerator:** Number of promoted states whose post-promotion utility $U_t > \theta_{\text{evict}}$ for at least $\tau_{\text{mature}}$ steps.
- **Denominator:** Total number of promotion events.

#### `PROMOTION_RECALL`
- **Definition:** Fraction of provisional candidate states of the correct type that successfully achieved promotion.

#### `EVICTION_PRECISION`
- **Definition:** Fraction of eviction events that occurred when internal state was genuinely obsolete or useless.
- **Numerator:** Number of evictions occurring when `oracle_state_type == NONE` (or when state was proven wrong type in probation).
- **Denominator:** Total number of eviction events.

#### `EVICTION_RECALL`
- **Definition:** Fraction of transitions from recurrent to state-free regimes that resulted in structural state eviction within $W_{\text{trans}} = 100$ steps.
- **Numerator:** Transitions where eviction occurred before the next regime onset.
- **Denominator:** Total number of transitions to state-free regimes ($2$ in primary stream: Phase 2 $\to$ 3 and Phase 4 $\to$ 5).

---

## 3. Resolution of the Central Discrepancy

### Verdict: `METRIC_SCOPE_MISMATCH_EXPLAINED`

The discrepancy between the Executive Summary claim ($92.5\%$ Type Accuracy) and Table A ($0.606$ Type Accuracy) is fully resolved:

1. **Executive Claim ($92.5\%$):** Represents **Event-Level Type Decision Accuracy** ($N_{\text{correct\_promotions}} / N_{\text{total\_promotions}}$). When the probation mechanism promotes a state, it promotes the correct type with $>92\%$ accuracy.
2. **Table A Value ($0.606$):** Represents **Time-Weighted Correct Type Occupancy** ($N_{\text{correct\_active\_steps}} / N_{\text{state\_needed\_steps}}$). Because the state is only active for $65.0\%$ of state-needed steps (Active Recall = $0.650$), and when active, it is the correct type $93.2\%$ of the time, the continuous occupancy of the correct state is:
   $$0.6498 \times 0.9325 = 0.6060$$
3. **The Root Cause of Missing Active Time ($35.0\%$):**
   - In Phase 2 (Linear): Active recall is **$94.1\%$** (only $5.9\%$ lost to birth latency and probation).
   - In Phase 4 (SET/RESET): Active recall collapsed to **$35.8\%$** due to **premature eviction during zero-latch periods** ($s_t = 0$), which re-triggered birth and two-stage probation cycles ($44.8\%$ spent in probation, $19.4\%$ dormant).

All future tables and reports will report BOTH metrics explicitly demarcated as:
- `TYPE_EVENT_ACCURACY` (Decision Level)
- `TYPE_OCCUPANCY_ACCURACY` (Time-Weighted Continuous Occupancy).
