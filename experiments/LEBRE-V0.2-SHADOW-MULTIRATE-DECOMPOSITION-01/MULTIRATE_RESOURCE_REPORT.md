# LEBRE v0.2 Multirate Shadow Resource Audit Report

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  
**Status:** COMPLETED CONFIRMATORY AUDIT  

---

## 1. Executive Resource Summary

This audit evaluates the computational and memory resource profile of the decoupled multirate shadow subsystem ($M_1$) compared to the continuous compacted baseline ($M_0$) and the historical periodic whole-shadow baseline ($S_{2, K=5}$) across $N=30$ independent confirmatory streams ($1711..1740$) on the 14-task benchmark suite ($84,000$ steps per seed; $2,520,000$ total steps evaluated).

### Key Findings
1. **Total Online Compute:**
   - $M_0$ (Continuous): Mean = **$175.38\text{ FP/step}$**, Median = $176.75\text{ FP}$, $P_{95} = 198.62\text{ FP}$, Peak = $216.73\text{ FP}$.
   - $M_1$ (Multirate): Mean = **$108.36\text{ FP/step}$**, Median = $109.39\text{ FP}$, $P_{95} = 128.51\text{ FP}$, Peak = $143.02\text{ FP}$.
   - $S_{2, K=5}$ (Periodic): Mean = **$90.09\text{ FP/step}$**, Median = $86.55\text{ FP}$, $P_{95} = 110.25\text{ FP}$, Peak = $120.44\text{ FP}$.
2. **Shadow Compute Reduction:**
   - Continuous shadow compute was reduced from **$98.67\text{ FP/step}$** ($M_0$) to **$32.06\text{ FP/step}$** ($M_1$), a net saving of **$66.61\text{ FP/step}$** ($67.5\%$ reduction in shadow overhead).
3. **Primary Resource Gate ($\le 100.00\text{ FP/step}$):**
   - **FAIL.** $M_1$ achieved $108.36\text{ FP/step}$, exceeding the $100.00\text{ FP}$ ceiling by $8.36\text{ FP/step}$.
   - *Physical Mechanism:* The live baseline path with active dynamic taps and normalization accounts for $76.30\text{ FP/step}$, and continuous recurrent state propagation accounts for $12.00\text{ FP/step}$, establishing an irreducible floor of **$88.30\text{ FP/step}$**. The remaining allowable budget ($11.70\text{ FP/step}$) cannot accommodate $K=2$ correlation probing ($4.00\text{ FP}$), candidate evaluations ($1.00\text{ FP}$), candidate LMS updates ($0.80\text{ FP}$), recurrent RTRL updates ($2.20\text{ FP}$), arbitration ($5.60\text{ FP}$), and structural bookkeeping ($1.50\text{ FP}$).

---

## 2. Disaggregated Resource Accounting Table

| Architectural Stage | Functional Role | $M_0$ Continuous (FP/step) | $M_1$ Multirate (FP/step) | $S_{2, K=5}$ (FP/step) | Saving vs $M_0$ |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Live Normalization + Base** | BASELINE | 58.00 | 58.00 | 58.00 | 0.00 |
| **Live Active Lag Predict/Update**| DYNAMIC_LAG | 11.24 | 11.02 | 8.84 | +0.22 |
| **Live Active Recurrent Predict** | DYNAMIC_REC | 7.46 | 7.28 | 4.88 | +0.18 |
| **Total Live Pipeline** | **LIVE** | **76.70** | **76.30** | **71.72** | **+0.40** |
| Stage 7: Correlation Grid Probing | SENSOR | 8.00 | 4.00 | 1.60 | +4.00 |
| Stage 8A-C: Candidate Obs/Loss | EVIDENCE | 2.14 | 0.43 | 0.43 | +1.71 |
| Stage 8D: Candidate Parameter LMS| PARAM_LEARN | 7.68 | 0.77 | 1.54 | +6.91 |
| Stage 9A-B: Recurrent Forward | STATE_PROP | 12.00 | 12.00 | 2.40 | 0.00 |
| Stage 9C-D: Recurrent RTRL Learn | PARAM_LEARN | 38.64 | 3.86 | 7.73 | +34.78 |
| Stage 10: Counterfactual Arb | DECISION | 28.00 | 5.60 | 5.60 | +22.40 |
| Shadow Housekeeping | HOUSEKEEPING | 2.21 | 1.40 | 0.90 | +0.81 |
| **Total Shadow Subsystem** | **SHADOW** | **98.67** | **32.06** | **18.37** | **+66.61 (67.5%)** |
| Router / Sentinel Overhead | ROUTER | 0.00 | 0.00 | 0.00 | 0.00 |
| **TOTAL ONLINE COMPUTE** | **TOTAL** | **175.38** | **108.36** | **90.09** | **+67.02 (38.2%)** |

---

## 3. Disaggregated Shadow Clock Utilization

Normalized execution counts per 1,000 stream steps (Confirmatory Cohort $N=30$, 84,000 steps/seed):

| Clock / Stage | $M_0$ Executions / 1k | $M_1$ Executions / 1k | Decimation Ratio | Operational Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `probe_executions` | 1,000.00 | 500.00 | 2.0x | Alternate-step grid scanning |
| `candidate_observations` | 428.14 | 85.63 | 5.0x | Sparse candidate loss evaluation |
| `candidate_parameter_updates`| 384.21 | 38.42 | 10.0x | Decimated LMS gradient steps |
| `recurrent_forward_executions` | 1,000.00 | 1,000.00 | 1.0x | Continuous path-dependent tracking |
| `recurrent_parameter_updates`| 1,000.00 | 100.00 | 10.0x | Decimated RTRL sensitivity steps |
| `arbitration_updates` | 1,000.00 | 200.00 | 5.0x | Freshness-synchronized evaluation |
| `stale_arbitration_skips` | 0.00 | 0.00 | N/A | Zero stale evaluations |

---

## 4. Memory Footprint and SRAM Verification

Following the sealed Phase-A microcorrection (`MEMORY_LIFETIME_AUDIT.md`), memory metrics are classified with zero arithmetic ambiguity:

| Metric | $M_0$ Baseline | $M_1$ Multirate | Status vs 1-KiB Ceiling |
| :--- | :--- | :--- | :--- |
| **Static Preallocated State** | 904 B | 904 B | PASS ($\le 1024\text{ B}$) |
| **Mean Occupied Persistent State** | 976.32 B | 974.18 B | PASS ($\le 1024\text{ B}$) |
| **Maximum Occupied Persistent State** | 1064 B | 1064 B | **FAIL** ($> 1024\text{ B}$) |
| **Transient Register Workspace** | 8 B (FPU `s0`-`s31`) | 8 B (FPU `s0`-`s31`) | Zero SRAM impact |
| **Peak Working SRAM (Hardware FPU)** | **1064 B** | **1064 B** | **FAIL** ($+40\text{ B}$ over 1 KiB) |
| **Peak Working SRAM (Conservative Stack)** | **1072 B** | **1072 B** | **FAIL** ($+48\text{ B}$ over 1 KiB) |

### Memory Findings
1. Multirate shadow governance introduces **0 B auxiliary persistent state** ($K$-counters reside in transient loop indices or registers).
2. The legacy peak memory violation ($1064\text{ B}$ persistent occupied state during concurrent dual-structure occupancy: 904 B base + 64 B lag + 96 B recurrent = 1064 B) persists unchanged from parent study `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`.
3. Peak memory failure is **carried forward as legacy FAIL**. This stage was preregistered not to resolve peak memory compaction.

---

## 5. Compute Floor Decomposition

Two compute floors were formalized in parent errata:
1. **Absolute Execution Floor ($58.00\text{ FP/step}$):** Fully memoryless linear pipeline with no temporal memory recruited.
2. **Occupancy-Conditioned Baseline Floor ($76.30\text{ FP/step}$):** Realized average live compute when active discrete lags and recurrent states are deployed under target benchmark regimes.
3. **Multirate Shadow Floor ($32.06\text{ FP/step}$):** Lowest viable shadow compute achieving functional recurrent and discrete tracking.

$$\bar{F}_{\text{total, min}} = F_{\text{live}} + F_{\text{shadow, min}} = 76.30 + 32.06 = \mathbf{108.36\text{ FP/step}}$$

Achieving $\le 100.00\text{ FP/step}$ without reducing live model capacity or decimating probing into predictive failure requires structural innovation beyond temporal clock decimation.
