# Runtime Clock Audit: Recurrent Shadow Subsystem in Current M1*

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Target Codebase:** `scratch/run_v02_correlation_search_compaction.py` / `src/lebre/`  
**Date:** September 22, 2026  

---

## 1. Recovered Runtime Clocks from Executable Code

Static inspection of `RotatingSparseFrontierModel.step()` and `DenseMultirateModel.step()` establishes the exact active clocks:

| Operational Clock Identifier | Controlled Operations | Code Line / Condition | Cadence Value | Frequency (Executions / Step) | Cost per Execution | FP Cost per Step |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| `K_REC_STATE` | R1, R2, R3 (State Propagation) | Executed unconditionally in `step()` | **1** | 1.0 | 12.0 FP | 12.000000 FP |
| `K_REC_PREDICT` | R4, R5 (Readout Prediction) | Executed unconditionally in `step()` | **1** | 1.0 | 6.0 FP | 6.000000 FP |
| `K_REC_SENSITIVITY` | R6 (RTRL Sensitivity Prop) | Inside `if self.step_count % self.K_rec_learn == 0:` | **10** | 0.1 | 8.0 FP | 0.800000 FP |
| `K_REC_LEARNING` | R7, R8, R9 (Weight Updates) | Inside `if self.step_count % self.K_rec_learn == 0:` | **10** | 0.1 | 8.0 FP | 0.800000 FP |
| `K_REC_EVIDENCE` | R10 (Evidence EMA) | Inside `if self.step_count % self.K_rec_learn == 0:` | **10** | 0.1 | 6.0 FP | 0.600000 FP |
| `K_REC_LIFECYCLE` | R11 (Promotion Check in Arb) | Inside `if self.step_count % self.K_arbitration == 0:` | **5** | 0.2 | 0.0 FP | 0.000000 FP |
| **TOTAL** | **All Recurrent Operations** | — | — | — | — | **20.200000 FP** |

---

## 2. Key Codebase Findings

1. **State Propagation vs Learning Asymmetry:**
   - Parameter learning updates and RTRL sensitivities are ALREADY decimated to $K=10$ ($2.20	ext{ FP/step}$).
   - Forward state propagation and prediction run every single timestep ($K=1$), consuming **$18.000000	ext{ FP/step}$** ($89.11\%$ of total recurrent spend).
2. **Opportunity for Gating:**
   - Because learning is already decimated to $K=10$, virtually all remaining recurrent compute ($18.0	ext{ FP}$) is trapped in forward state propagation.
   - Any decimation of forward state directly scales this $18.0	ext{ FP}$ mass.
