# Memory Metric Dictionary & Semantic Disaggregation

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus Inquiry:** Issue B — Resolving Memory Metric Ambiguities and Conflations  

---

## 1. Executive Summary

In `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`, the final report presents apparently contradictory memory assessments:
- Section 5 (Table 5.1) lists `Peak RAM <= 1024 B` as `PASS (976 B)` for $S_0$, `PASS (980 B)` for $S_2$, and `PASS (992 B)` for $S_3$.
- In the raw per-seed ledger (`RESOURCE_VECTOR_BY_SEED.csv`), measured `peak_bytes` are recorded as **$1,064$ B** for $S_0$, **$1,068$ B** for $S_2$, and **$1,080$ B** for $S_3$ — all exceeding $1,024$ Bytes.

This document resolves the contradiction by providing unambiguous definitions for every memory concept in the LEBRE runtime, detailing their exact algebraic formulas, allocation semantics, lifetimes, and verifying compliance across historical and proposed resource gates.

---

## 2. Definitive Memory Metric Dictionary

```
+-------------------------------------------------------------------------------------------------------------------------------+
| Metric Identifier                   | Definition & System Semantics                          | Lifetime & Allocation Timing   |
+-------------------------------------------------------------------------------------------------------------------------------+
| STATIC_PREALLOCATED_BYTES           | Persistent memory required for baseline static modules  | Allocated at boot; permanent.  |
|                                     | (Scaler, History Buffer, Base Predictor, Grid, etc.)   | Never freed during stream.     |
+-------------------------------------------------------------------------------------------------------------------------------+
| MEAN_OCCUPIED_PERSISTENT_BYTES      | Time-averaged empirical byte occupancy of model state  | Measured dynamically over all  |
|                                     | across the 6,000 streaming steps.                      | streaming timesteps.           |
+-------------------------------------------------------------------------------------------------------------------------------+
| MAX_OCCUPIED_PERSISTENT_BYTES       | Worst-case persistent state occupied when all optional | Occurs during active hybrid    |
|                                     | taps, candidates, and recurrent units are recruited.   | co-adaptation (Task I9 / I14). |
+-------------------------------------------------------------------------------------------------------------------------------+
| TRANSIENT_WORKSPACE_BYTES          | Temporary SRAM required for local stack buffers, dot-  | Allocated on stack per-step;   |
|                                     | product accumulators, and ring pointers.               | popped immediately.            |
+-------------------------------------------------------------------------------------------------------------------------------+
| PEAK_WORKING_BYTES                  | Maximum total SRAM observed simultaneously:             | Measured as:                   |
|                                     | Max Occupied Persistent Bytes + Transient Workspace.   | MAX_OCCUPIED + TRANSIENT.      |
+-------------------------------------------------------------------------------------------------------------------------------+
| ALLOCATED_CAPACITY_BYTES            | Total preallocated static heap slab reserved to safely  | Statically configured physical |
|                                     | run the model without dynamic runtime malloc/free.     | buffer size in firmware.       |
+-------------------------------------------------------------------------------------------------------------------------------+
| SCHEDULER_STATE_BYTES               | Auxiliary state bytes required exclusively by the      | Allocated at init; permanent   |
|                                     | shadow scheduler logic (timers, cum_dev, counters).   | for scheduler lifetime.        |
+-------------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Mathematical Formulations & Component Breakdown

### 3.1 Base Permanent Footprint ($M_{\text{base}} = 904$ Bytes)
The invariant persistent state shared by all configurations consists of:
$$M_{\text{base}} = M_{\text{scaler}} + M_{\text{history}} + M_{\text{base\_pred}} + M_{\text{shadow\_rec}} + M_{\text{corr\_grid}} + M_{\text{arbitrator}}$$

1. **CausalStandardScaler ($M_{\text{scaler}} = 80$ B):**  
   5 features $\times$ 16 Bytes ($8$ B float64 running mean + $8$ B float64 running variance).
2. **FP16HistoryRingBuffer ($M_{\text{history}} = 342$ B):**  
   $5 \text{ features} \times 33 \text{ lags} \times 2 \text{ Bytes} = 330 \text{ B}$ data buffer + $12$ Bytes ring indices and bounds pointers.
3. **LinearBasePredictor ($M_{\text{base\_pred}} = 40$ B):**  
   $5 \text{ features} \times 8 \text{ Bytes}$ (float64 weight vector).
4. **ShadowRecurrentUnit ($M_{\text{shadow\_rec}} = 48$ B):**  
   Permanently active background recurrent tracking module ($3 \text{ weights} \times 8 \text{ B} + 24 \text{ B hidden state/pointers}$).
5. **Compacted Correlation Grid ($M_{\text{corr\_grid}} = 330$ B):**  
   $5 \text{ features} \times 33 \text{ lags} \times 2 \text{ Bytes}$ (IEEE 754 float16).
6. **Capacity Arbitrator ($M_{\text{arbitrator}} = 64$ B):**  
   Loss EMA filters, gain EMA filters, and hysteresis state registers.
$$\sum M_{\text{base}} = 80 + 342 + 40 + 48 + 330 + 64 = \mathbf{904 \text{ Bytes}}$$

### 3.2 Dynamic Temporal State ($M_{\text{dyn}} \le 160$ Bytes)
Recruited and evicted based on conditional utility:
1. **Active Delay Taps ($M_{\text{taps}} \le 64$ B):** Up to $4$ taps $\times 16$ B (lag index, weight, variance, age).
2. **Provisional Candidates ($M_{\text{cands}} \le 48$ B):** Up to $3$ shadow candidates $\times 16$ B.
3. **Active Recurrent Unit ($M_{\text{act\_rec}} \le 48$ B):** Recurrent module promoted to live prediction path.
$$\max M_{\text{dyn}} = 64 + 48 + 48 = \mathbf{160 \text{ Bytes}}$$

### 3.3 Scheduler Auxiliary State ($M_{\text{sched}}$)
- **$S_0$ (Continuous):** $M_{\text{sched}} = 0$ Bytes.
- **$S_1$ (Shadow Off):** $M_{\text{sched}} = 0$ Bytes.
- **$S_2$ (Periodic $K=5$):** $M_{\text{sched}} = 4$ Bytes ($2$ B sampling period $K$ + $2$ B modulo counter).
- **$S_3$ (Event-Triggered):** $M_{\text{sched}} = 16$ Bytes ($4$ B ref mean + $4$ B Page-Hinkley cumulative sum + $4$ B min cum sum + $2$ B heartbeat counter + $2$ B wake burst counter).

---

## 4. Reconciled Memory Ledger by Configuration

```
+-------------------------------------------------------------------------------------------------------+
| Metric (Bytes)                 | S0_CONTINUOUS | S1_SHADOW_OFF | S2_PERIODIC (K=5) | S3_EVENT_TRIGGERED|
+-------------------------------------------------------------------------------------------------------+
| Base Permanent State           |     904 B     |     904 B     |       904 B       |       904 B       |
| Scheduler Dedicated State      |       0 B     |       0 B     |         4 B       |        16 B       |
| STATIC PREALLOCATED BASE       |     904 B     |     904 B     |       908 B       |       920 B       |
+-------------------------------------------------------------------------------------------------------+
| Mean Dynamic State Occupied    |    72.32 B    |      0.00 B   |      72.32 B      |      72.32 B      |
| MEAN OCCUPIED PERSISTENT       |   976.32 B    |    904.00 B   |     980.32 B      |     992.32 B      |
+-------------------------------------------------------------------------------------------------------+
| Maximum Dynamic State Occupancy|     160 B     |       0 B*    |       160 B       |       160 B       |
| MAX OCCUPIED PERSISTENT        |    1064 B     |     904 B     |      1068 B       |      1080 B       |
+-------------------------------------------------------------------------------------------------------+
| Transient Execution Workspace  |       8 B     |       8 B     |         8 B       |         8 B       |
| PEAK WORKING SRAM              |    1064 B     |     904 B     |      1068 B       |      1080 B       |
+-------------------------------------------------------------------------------------------------------+
| ALLOCATED CAPACITY SLAB        |    1064 B     |     904 B     |      1068 B       |      1080 B       |
+-------------------------------------------------------------------------------------------------------+
* In S1, discovery is completely off, so dynamic state is never recruited.
```

---

## 5. Forensic Resolution of the Parent Study Conflation

The root cause of the apparent conflict between the text and the raw CSV in `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01` is now transparent:

1. **What the Report Table Pasted:**  
   In Table 5.1, under the row header `Peak RAM <= 1024 B`, the report pasted the **rounded integer values of Mean Occupied Persistent Bytes**:
   - $S_0$: $976.32 \text{ B} \longrightarrow 976\text{ B}$
   - $S_1$: $904.00 \text{ B} \longrightarrow 904\text{ B}$
   - $S_2$: $980.32 \text{ B} \longrightarrow 980\text{ B}$
   - $S_3$: $992.32 \text{ B} \longrightarrow 992\text{ B}$

2. **Why this Caused Confusion:**  
   The author labeled the row **"Peak RAM"**, creating the false impression that maximum observed memory remained beneath $1,024$ Bytes. In reality, observed peak persistent memory was $1,064$ B ($S_0$), $1,068$ B ($S_2$), and $1,080$ B ($S_3$).

---

## 6. Disaggregated Governance Verdicts

To prevent misrepresentation, memory compliance must be disaggregated across criteria:

```
+-----------------------------------------------------------------------------------------------------+
| Governance Criterion           | Threshold  | S0_CONTINUOUS | S1_SHADOW_OFF | S2_PERIODIC | S3_EVENT |
+-----------------------------------------------------------------------------------------------------+
| Static Base Capacity           | <= 1024 B  |     PASS      |     PASS      |    PASS     |   PASS   |
| Mean Occupied Persistent State | <= 1024 B  |     PASS      |     PASS      |    PASS     |   PASS   |
| Maximum Occupied Capacity      | <= 1024 B  |     FAIL      |     PASS      |    FAIL     |   FAIL   |
| Peak Working Memory            | <= 1024 B  |     FAIL      |     PASS      |    FAIL     |   FAIL   |
+-----------------------------------------------------------------------------------------------------+
| Historical R2 Memory Gate      | <= 1024 B  | FAIL (Peak)   | PASS          | FAIL (Peak) | FAIL(Pk) |
| Shadow-Rent Protocol Gate 3    | Capacity   | FAIL (Capac)  | PASS          | FAIL (Capac)| FAIL(Cap)|
| Proposed 2048-B Memory Class   | <= 2048 B  |     PASS      |     PASS      |    PASS     |   PASS   |
+-----------------------------------------------------------------------------------------------------+
```

### Definitive Finding
If Gate 3 is evaluated strictly as **Static Allocated Capacity $\le 1024\text{ Bytes}$**, configurations $S_0, S_2, S_3$ **FAIL**. If Gate 3 is evaluated as **Time-Averaged Mean Occupancy $\le 1024\text{ Bytes}$**, all configurations **PASS**. The errata report mandates explicitly disclosing both metrics.
