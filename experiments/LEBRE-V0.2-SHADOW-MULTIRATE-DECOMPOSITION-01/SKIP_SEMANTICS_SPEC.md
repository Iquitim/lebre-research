# Specification: Skip Semantics & Anti-Fabrication Invariants

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Objective & Non-Negotiable Rule

When an atomic shadow operation is skipped due to rate decimation ($K > 1$) or data-selective gating, the system must **never fabricate fictitious values**:
- Under no circumstances may skipped operations inject `0.0` error, `0.0` gain, `0.0` correlation, or `0.0` prediction into downstream filters.
- Fabricating `0.0` pulls exponential moving average filters ($\alpha$) toward zero, corrupting steady-state capacity estimates and causing premature structural evictions.

Every skipped operation must strictly adhere to one of three preregistered skip semantics:

```
+---------------------------+----------------------------------------------------+------------------------------------------+
| Skip Semantic             | Formal Operational Behavior                        | Applicable Atomic Operations             |
+---------------------------+----------------------------------------------------+------------------------------------------+
| 1. HOLD_STATE             | Persistent registers retain their exact value from | 7C (corr_grid), 8D (cand_weights),       |
|                           | the previous execution step. Zero math is executed.| 9A (hidden_state), 9D (rec_weights),     |
|                           | Pointers and state flags remain static.            | 10D (structural allocation).             |
+---------------------------+----------------------------------------------------+------------------------------------------+
| 2. NO_NEW_EVIDENCE        | Evidence accumulators and EMA filters do not       | 7B (innovation), 8B/8C (cand_evidence),  |
|                           | update. Filter time constants (alpha) are NOT      | 9E (rec_evidence), 10A/10B/10C           |
|                           | advanced. Memory registers hold previous filtered  | (conditional gain EMAs).                 |
|                           | values without decay or bias.                      |                                          |
+---------------------------+----------------------------------------------------+------------------------------------------+
| 3. STALE_WITH_AGE_METADATA| Signals provided to downstream consumers carry an   | 8A (y_lag_eval), 9B (y_rec_eval).        |
|                           | explicit integer `age_steps` metadata tag.         | Consumer inspects freshness before use.  |
+---------------------------+----------------------------------------------------+------------------------------------------+
```

---

## 2. Mathematical Definition of Filter Freezing (`NO_NEW_EVIDENCE`)

In continuous operation ($K=1$), an exponential moving average update is:
$$S(t) = (1 - \alpha) S(t-1) + \alpha X(t)$$

Under multirate skipping at timestep $t$:
$$S(t) = S(t-1) \quad (\text{Strict Invariance})$$

**Forbidden Post-Hoc Behavior:**
$$S(t) \ne (1 - \alpha) S(t-1) + \alpha \cdot 0 \quad (\text{PROHIBITED: Fictitious Zero Injection})$$
$$S(t) \ne (1 - \alpha) S(t-1) + \alpha X(t_{\text{prev}}) \quad (\text{PROHIBITED: Double-Counting Stale Innovations})$$

---

## 3. Candidate Probation Clocks Under Skipping

Provisional delay candidates and shadow recurrent units require $T_{\text{prob}} = 15$ steps of evidence before becoming eligible for live promotion.
- Under multirate downsampling ($K > 1$), candidate probation count increments **only on timesteps where the candidate is actively observed**:
  $$\text{OBSERVATION\_COUNT}(t) = \text{OBSERVATION\_COUNT}(t-1) + \mathbb{I}(\text{Candidate Observed at } t)$$
- Eligibility condition:
  $$\text{OBSERVATION\_COUNT} \ge 15 \quad \text{AND} \quad \text{evidence} > 0.02$$
- `STREAM_AGE` increments every stream step ($t$). If a candidate fails to accumulate sufficient evidence within $\text{STREAM\_AGE} > 150$, it is pruned for non-performance.
