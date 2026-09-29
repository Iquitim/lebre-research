# Diagnostic Report: M2-EXP-0005R — Lifecycle Reconciliation & Bottleneck Diagnosis

**Primary Decision:** `PREMATURE_EVICTION_PRIMARY`  
**Secondary Decision:** `METRIC_SCOPE_MISMATCH_EXPLAINED`  
**Metric Reconciliation Status:** `METRIC_SCOPE_MISMATCH_EXPLAINED`  
**M2-EXP-0005 Revised Status:** `M2_EXP_0005_REVISED_STATUS = PARTIAL_GO`  
**Architecture Evidence:** `EMERGING`  
**Multi-State Capacity Justified:** `MULTI_STATE_CAPACITY_JUSTIFIED = NOT_YET`  
**Next Objective:** `NEXT = STATE_UTILITY_AND_EVICTION_DIAGNOSTIC`  

---

## 1. Diagnostic Summary

The audit of M2-EXP-0005 resolves the apparent contradictions in reported metrics and causally isolates where the adaptive recurrent state lifecycle loses performance relative to the oracle baseline (V6 Oracle Type).

### 1.1 Resolution of Metric Discrepancies
- **Discrepancy 1:** Reported Birth Precision & Recall = $1.000$, but Active Recall = $0.650$.
  - *Cause:* Birth precision/recall is an **event-level metric** measuring whether the trigger fired upon regime transition. Active Recall is a **time-weighted continuous metric** measuring the fraction of state-needed steps where state is active. The gap ($35\%$) is lost to probation delay and premature eviction recovery.
- **Discrepancy 2:** Reported Type Selection Accuracy $\approx 92.5\%$, but Primary Table Type Accuracy $\approx 0.606$.
  - *Cause:* $92.5\%$ measures **Event-Level Promotion Accuracy** ($N_{\text{correct\_promotions}} / N_{\text{total\_promotions}}$). Table A's $0.606$ value measures **Continuous Correct Type Occupancy** ($N_{\text{correct\_active\_steps}} / N_{\text{state\_needed\_steps}}$), which is mathematically bounded by $\text{Active Recall} \times P(\text{Correct} \mid \text{Active}) = 0.650 \times 0.932 = 0.606$.
  - *Verdict:* `METRIC_SCOPE_MISMATCH_EXPLAINED`.

---

## 2. Causal Priority Ranking of Lifecycle Decisions

Through systematic counterfactual evaluation (Q0–Q7) over 30 evaluation seeds and 20 fresh confirmation seeds, the lifecycle decisions rank by fraction of adaptive regret closed as follows:

| Rank | Lifecycle Intervention | Counterfactual Variant | Regret Closed % | Active Recall Impact | MSE Impact |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **1** | **Inhibit Premature Eviction** | **Q4 (Oracle Eviction Only)** | **47.67%** | **0.650 $\to$ 0.878** | **0.3094 $\to$ 0.2720** |
| **2** | **Bypass Probation Window** | Contrast Q4 vs Q6/Q7 | ~38.00% | 0.878 $\to$ 1.000 | 0.2720 $\to$ 0.2310 |
| **3** | **Oracle Type Selection** | Q3 (Oracle Type Only) | 2.29% | 0.650 $\to$ 0.658 | 0.3094 $\to$ 0.3076 |
| **4** | **Instantaneous Birth Trigger** | Q2 (Oracle Birth Only) | 3.17% | 0.650 $\to$ 0.656 | 0.3094 $\to$ 0.3069 |

### Detailed Analysis of the Primary Bottleneck: Premature Eviction
The root cause of underperformance in the adaptive lifecycle manager is a fundamental flaw in the **utility metric during event-driven quiescent periods**:
1. In SET/RESET (Phase 4), after a RESET event occurs, the latent latch is cleared to zero ($s_t = 0$).
2. During the subsequent event-free gap, the environment output is $y_t = 0$. The base linear model predicts $y_{\text{base}} = 0$, and the active gated model predicts $y_{\text{hat}} = 0$.
3. As a consequence, prediction error is identically zero without the state ($e_{\text{base}} = 0, e_t = 0$).
4. The paired counterfactual delta-loss $\Delta L_t = e_{\text{base}}^2 - e_t^2 = 0$.
5. The exponential moving average $\text{EMA}(\Delta L)$ decays exponentially toward zero.
6. Once $\text{EMA}(\Delta L) < \theta_{\text{evict}} = 0.02$ for $P = 40$ steps, the manager concludes the state is obsolete and **executes physical structural deletion**.
7. When the next SET event arrives, the model has no state. It experiences an error spike, requires ~45 steps to detect birth, spends 80 steps failing linear probation, and spends 80 steps passing gated probation—**losing 205 steps of active coverage for every premature eviction**.
8. In Phase 4, this thrashing occurred an average of **$2.20$ times per seed**, reducing active coverage to $35.8\%$ and explaining $64.2\%$ of missing state-needed time.

When premature eviction is disabled (Q4), active recall immediately surges to **$87.8\%$**, and nearly half ($47.67\%$) of the total regret is eliminated.

---

## 3. Scientific Capacity Justification

### Is One State Still Sufficient?
**YES.**  
Under Q7 (Full Oracle Lifecycle with $\text{STATE\_DIM} = 1$), Global MSE is **$0.2310$**, matching the oracle baseline V6. The single scalar state successfully integrates continuous signals ($\text{MSE} \approx 0.75$) and holds discrete latch events ($\text{MSE} \approx 0.12$). The performance gap in V3 is an operational lifecycle management problem, not a capacity limit.

### Is Multi-State Capacity Justified Now?
**NOT_YET.**  
Increasing state capacity ($\text{MAX\_ACTIVE\_STATES} > 1$) would not solve premature eviction during quiescent states. A multi-state learner would still evict its latent units whenever their driving signals paused. The rigorous scientific path is to diagnose and fix state utility estimation for sparse-event regimes.

---

## 4. Milestone Reassessment & Next Steps

### Status Reassessment
- In accordance with Section 71, because the preregistered continuous active coverage criterion was compromised by premature evictions, **`M2_EXP_0005_REVISED_STATUS = PARTIAL_GO`**.
- Architecture evidence is maintained as **`EMERGING`** (no claim escalation during reconciliation).

### Recommended Next Milestone Step
`NEXT = STATE_UTILITY_AND_EVICTION_DIAGNOSTIC`  
The next experiment must investigate state utility metrics that distinguish **quiescent retention** ($s_t = 0$ or event-free gap) from **true obsolescence** (state-free regime), enabling zero-churn retention of valid memories without preventing prompt eviction in truly state-free environments.

**Section 153 / Audit Hard Stop:** Simulation halted; all deliverables prepared for user review.
