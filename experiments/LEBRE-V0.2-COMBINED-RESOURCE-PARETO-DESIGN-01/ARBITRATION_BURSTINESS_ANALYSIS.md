# Arbitration Decision Burstiness & Redundancy Analysis

## 1. Empirical Switch-Opportunity Rate & Redundancy (B22, B23)

From trace analysis across all 14 benchmark tasks on seed 1941 ($16,800$ arbitration evaluations):
- **Total $K=5$ Arbitration Evaluations:** `16800`
- **Total Meaningful Structural State Changes:** `76` (promotions + evictions)
- **Meaningful Decision Rate:** **`0.4524%`** (approx. 1 event per `221.1` evaluations)
- **Redundant Evaluation Rate:** **`99.5476%`**
- **$K=10$ Skipped Evaluations:** `8400`
- **Structural State Changes Falling on Skipped Steps:** `33`
- **Skipped Meaningful Decision Rate:** **`0.3929%`**

### Key Takeaway:
Over **99.4%** of arbitration evaluations produce identical structural allocations to the prior step. This confirms substantial computational redundancy in continuous and $K=5$ arbitration. However, redundancy cannot be equated with safely skippable behavior without examining temporal clustering.

---

## 2. Temporal Clustering & Burstiness (B24)

Structural allocation changes are **highly bursty and non-uniformly distributed**:
1. **Startup Epoch ($t \in [0, 500]$):** Initial discovery of primary lags and recurrent state. Over $45\%$ of all promotions occur in this window.
2. **Regime Transition Epoch ($t \in [3000, 3200]$):** In directional tasks ($I_{11}..I_{14}$), sudden loss degradation causes tap eviction and recurrent promotion within 200 steps.
3. **Quiescent Reactivation Epoch ($t \in [4000, 4200]$):** On $I_7$, state reactivation after 2000 steps of silence causes concentrated arbitration evaluations.
4. **Quiescent Steady-State ($t \in [1000, 2900]$ and $t > 4500$):** In steady-state regimes, arbitration decisions are virtually $100\%$ redundant.

---

## 3. Event-Triggered Arbitration: Future Research Hypothesis (B25)

Because meaningful decisions cluster heavily near innovations, fixed periodic decimation ($K=10$) is an intermediate approximation.
$$\mathbf{\text{EVENT\_TRIGGERED\_ARBITRATION} = \text{FUTURE\_HYPOTHESIS\_ONLY}}.$$
If fixed $K=10$ later fails in confirmatory testing due to switching lag, an event-triggered scheduler (evaluating arbitration only when prediction residual $|e_t| > \gamma$ or after changepoints) is the principled successor architecture. It is NOT implemented in this stage to maintain single-intervention discipline.
