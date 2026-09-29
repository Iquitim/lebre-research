# Compute Floor Semantics & Structural Disambiguation

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus Inquiry:** Issue C — Disambiguation of the Theoretical Compute Floor  

---

## 1. Executive Summary

In `SHADOW_RENT_FINAL_REPORT.md` (Section 1.2, Line 22), the parent study declares:
> *"The theoretical compute floor is $F_{\text{min}} = 81.17 + 2.00 = 83.17\text{ FLOPs/step} \le 100.0$."*

However, in the same study's empirical results (Table 5.1 and `RESOURCE_VECTOR_BY_SEED.csv`), configuration **$S_1$ (Shadow Off)** reports a total compute of only **$58.00\text{ FLOPs/step}$** — substantially lower than $83.17$ FLOPs/step.

This audit investigates the origin of this discrepancy and proves:
1. $83.17\text{ FLOPs/step}$ is **NOT an unconditional, universal lower bound**.
2. Rather, $83.17\text{ FLOPs/step}$ represents the **Reference-Occupancy Conditioned Floor**: the computational burden required to execute live inference and updates *assuming the full structural occupancy discovered by continuous baseline $S_0$ is preserved*, with shadow exploration turned off and $2.00$ FLOPs of housekeeping added.
3. The true **Absolute Minimal Execution Floor** of the LEBRE base pipeline is **$58.00\text{ FLOPs/step}$**, attained when no temporal structures (delays or recurrent units) are active.
4. Live-path compute is dynamic: because disabling or throttling shadow discovery alters structural recruitment, live compute itself varies across schedulers ($58.00$ for $S_1$, $72.60$ for $S_2$, $80.49$ for $S_3$, $82.64$ for $S_0$).

---

## 2. Component-by-Component Algorithmic Decomposition

The LEBRE pipeline executes sequential stages each timestep. The floating-point operation costs are derived directly from the canonical implementation:

```
+---------------------------------------------------------------------------------------------------------+
| Pipeline Stage                      | Math Operations & Flop Counting                    | FLOPs/step   |
+---------------------------------------------------------------------------------------------------------+
| 1. Causal Normalization (Scaler)    | 5 features x (Sub mean + Div std) = 5 x 2          | 10.0 FLOPs   |
| 2. Welford Online Stat Update       | 5 features x (Delta + Mean + Var update) = 5 x 2   | 10.0 FLOPs   |
| 3. FP16 History Ring Buffer Write   | Scaling / clamping to FP16 representation          |  0.0 FLOPs*  |
| 4. Base Linear Predictor Forward    | Dot product: 5 features x (Mul + Add)              | 10.0 FLOPs   |
| 5. Aggregate Prediction & Residual  | y_hat = y_base + y_lag + y_rec (2 Add); e = y - y_hat|  3.0 FLOPs   |
| 6. Base Linear Predictor Update     | LMS/SGD: 5 features x (Grad + Weight update)       | 25.0 FLOPs   |
+---------------------------------------------------------------------------------------------------------+
| TOTAL MINIMAL BASE EXECUTION (NONE) | Mandatory memoryless linear baseline pipeline      | 58.0 FLOPs   |
+---------------------------------------------------------------------------------------------------------+
| Optional Delay Taps (Live Forward)  | k active taps x (Weight x Delay + Add)             | 2.0 k FLOPs  |
| Optional Delay Taps (LMS Update)    | k active taps x (Step-size x Error x Input)        | 3.0 k FLOPs  |
| Optional Recurrent Unit (Forward)   | Hidden state update (tanh) + linear projection    | 12.0 FLOPs   |
| Optional Recurrent Unit (RTRL)      | Real-time recurrent learning derivative updates   | 14.0 FLOPs   |
+---------------------------------------------------------------------------------------------------------+
| Arbitrator Gain Tracking (EMA)      | 4 exponential moving average filters (4 x 2)      |  8.0 FLOPs   |
+---------------------------------------------------------------------------------------------------------+
* Ring buffer writes and circular pointer increments are integer indexing operations, accounted in int_ops.
```

---

## 3. Disambiguation of Compute Floors

```
+-------------------------------------------------------------------------------------------------------------+
| Concept Identifier               | Value      | Definition & Operational Assumptions                        |
+-------------------------------------------------------------------------------------------------------------+
| ABSOLUTE_EXECUTION_FLOOR         | 58.00 FP   | The minimum floating-point operations executed by LEBRE     |
|                                  |            | when operating purely as a causal linear model (Structural  |
|                                  |            | State = NONE, zero taps active, zero recurrent units).      |
+-------------------------------------------------------------------------------------------------------------+
| REFERENCE_OCCUPANCY_CONDITIONED  | 83.17 FP   | The compute required to execute the average structural      |
| SHADOW_OFF_FLOOR                 |            | burden discovered by continuous baseline S0 (81.17 FP live) |
| (F_ref_floor)                    |            | with shadow exploration silenced, plus 2.00 FP housekeeping.|
+-------------------------------------------------------------------------------------------------------------+
| EMPIRICAL_LIVE_COMPUTE           | 58.00 (S1) | The actual time-averaged live execution compute observed    |
| (Varies by Scheduler)            | 72.60 (S2) | under each scheduling regime, reflecting the structural    |
|                                  | 80.49 (S3) | recruitment rates sustained by that scheduler.              |
|                                  | 82.64 (S0) |                                                             |
+-------------------------------------------------------------------------------------------------------------+
```

### 3.1 Why $S_1$ Executes Exactly $58.00$ FLOPs
Under configuration $S_1$ (Shadow Off), shadow discovery is permanently disabled:
- The correlation grid is never queried or updated.
- Provisional delay candidates are never evaluated.
- The shadow recurrent unit is never simulated.
- Consequently, **no delay taps or recurrent units are ever promoted to the live path**.
- The model spends $100.0\%$ of timesteps in the `NONE` structural state.
- Live compute is strictly:
  $$F_{\text{live}, S_1} = 10 (\text{scale}) + 10 (\text{stat}) + 10 (\text{base forward}) + 3 (\text{loss}) + 25 (\text{base update}) = \mathbf{58.00\text{ FLOPs/step}}$$

### 3.2 Why $F_{\text{ref\_floor}} = 83.17$ FLOPs
Under baseline $S_0$, background shadow exploration actively recruits temporal structures across the 14 benchmark streams:
- Across the $14$ streams and $30$ seeds, $S_0$ spent $14.2\%$ in `NONE`, $42.5\%$ in `LAG`, $25.1\%$ in `RECURRENT`, and $18.2\%$ in `BOTH`.
- The empirical average live execution cost across this structural mixture was **$81.17\text{ FLOPs/step}$**.
- Adding $2.00\text{ FLOPs/step}$ for minimal periodic housekeeping (modulo counter, ring pointer check) yields:
  $$F_{\text{ref\_floor}} = 81.17 + 2.00 = \mathbf{83.17\text{ FLOPs/step}}$$

---

## 4. State-Conditioned Compute Across Schedulers

```
+-----------------------------------------------------------------------------------------------------+
| Structural State | S0_CONTINUOUS | S1_SHADOW_OFF | S2_PERIODIC (K=5) | S3_EVENT_TRIGGERED           |
+-----------------------------------------------------------------------------------------------------+
| NONE (Base only) |  58.00 FLOPs  |  58.00 FLOPs  |    58.00 FLOPs    |   58.00 FLOPs (+4.0 sched)   |
| LAG (1-4 taps)   | 68.0-78.0 FP  |     N/A*      |   68.0-78.0 FP    |  68.0-78.0 FP (+4.0 sched)   |
| RECURRENT (Rec)  |  84.00 FLOPs  |     N/A*      |    84.00 FLOPs    |   84.00 FLOPs (+4.0 sched)   |
| BOTH (Lag + Rec) | 94.0-104.0 FP |     N/A*      |   94.0-104.0 FP   |  94.0-104.0 FP (+4.0 sched)  |
+-----------------------------------------------------------------------------------------------------+
* In S1, LAG, RECURRENT, and BOTH states are never entered.
```

### Definitive Conclusion
The parent study's statement must be formally qualified in the corrigendum:
> **Audited Formulation:** $83.17\text{ FLOPs/step}$ is the *behavior-preserving reference floor* conditioned on $S_0$ structural density. The *absolute execution floor* of the architecture is $58.00\text{ FLOPs/step}$.
