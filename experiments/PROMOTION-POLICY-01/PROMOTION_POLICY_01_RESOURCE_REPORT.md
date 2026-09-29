# PROMOTION-POLICY-01: Algorithmic Compute and Resource Report

**Stage:** PROMOTION-POLICY-01 — Sequential Structural Evidence & False-Promotion Control  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Resource Constraint Models:** R2-FLOP ($\le 100$ FLOPs/step mean), R2-MEM ($\le 1024$ bytes RAM).

---

## 1. Algorithmic Resource Envelope Matrix

| Policy | Mean FLOPs/step | Peak FLOPs/step | Persistent Memory (Bytes) | Candidate Extra Bytes | Resource Class | Compliance Status |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: |
| **P0: Frozen Baseline** | 81.66 | 206.0 | 439.5 | 128 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **P1: Fixed Long** | 81.56 | 206.0 | 441.6 | 128 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **P2: Fixed Strict** | 73.72 | 206.0 | 431.6 | 128 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **P3: Two-Window Confirm** | **81.83** | **206.0** | **440.2** | **136** | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **P4: Confidence Sequence** | 82.72 | 218.0 | 439.5 | 152 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **P5: Global Error Budget** | 66.40 | 206.0 | 325.0 | 144 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **P6: CS + Budget** | 66.33 | 218.0 | 327.1 | 160 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |
| **LEBRE_NO_REC_BIRTH** | 64.00 | 176.0 | 320.0 | 0 | `WITHIN_V0_1_RESOURCE_CLASS` | **PASS** |

---

## 2. Computational Rent Analysis

1. **Suppression of Spurious Candidate Churn Saves FLOPs:**
   - On negative controls (A2–A4), `LEBRE_v0.1_FIXED` spends compute maintaining harmful promoted states in the live graph (97.5 FLOPs/step).
   - Policies that sharply reject spurious candidates (e.g., `TWO_WINDOW_CONFIRM` at 81.83 FLOPs) reduce unnecessary active-state adaptation overhead.
2. **Marginal Cost of Temporal Confirmation:**
   - `TWO_WINDOW_CONFIRM` requires only two additional 64-bit float accumulators during Window B (+8 bytes), and 1 addition per step during probation. Its computational rent is near-zero ($+0.05$ FLOPs/step).
3. **Marginal Cost of Confidence Sequences:**
   - Online Welford variance tracking and radical evaluation in `CS_PROMOTION` add approximately $+6.2$ FLOPs per step during probation and $+24$ bytes of state. While compliant with R2-FLOP, it does not outperform the simpler Two-Window rule.
