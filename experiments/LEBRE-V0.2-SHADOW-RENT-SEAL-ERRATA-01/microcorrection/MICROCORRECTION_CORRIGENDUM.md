# Master Microcorrection Corrigendum: Accounting Disambiguation

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01/microcorrection`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Errata Reference:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Document Status:** Binding Additive Microcorrection & Terminology Standard  
**Date:** September 22, 2026  

---

## 1. Scope & Objective

This Corrigendum formally seals the three deterministic microcorrections mandated prior to opening the multirate shadow decomposition study (`LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`):

1. **Peak Working Memory Arithmetic Disambiguation:**  
   Formal disaggregation between CPU/FPU hardware register transients and stack SRAM frames, resolving the apparent equality between Max Occupied Persistent Bytes and Peak Working SRAM.
2. **Regression Test Suite Counting Terminology:**  
   Formal reconciliation of "57 passed" vs. "124 tests" as a discovery scope artifact between standard `unittest` discovery and full `pytest` execution.
3. **Switching Latency Unit Standardization:**  
   Formal replacement of erroneous seconds ("s") notation with discrete stream steps ("steps").

---

## 2. Master Microcorrection Table

```
+-------------------------------------------------------------------------------------------------------------------------------+
| Item ID | Topic               | Previous Reporting                 | Audited & Microcorrected Standard  | Primary Reference   |
+-------------------------------------------------------------------------------------------------------------------------------+
| MIC-01  | Peak Working Memory | PEAK_WORKING_BYTES listed equal to | Disaggregated: Hardware FPU Regs    | MEMORY_LIFETIME_    |
|         | Arithmetic          | MAX_OCCUPIED_PERSISTENT            | (0 B stack) -> 1064, 904, 1068, 1080| AUDIT.md            |
|         |                     | (1064 B, 904 B, 1068 B, 1080 B),   | Stack Frame (+8 B stack) ->         |                     |
|         |                     | omitting +8 B transient workspace. | 1072, 904, 1076, 1088 B.            |                     |
+-------------------------------------------------------------------------------------------------------------------------------+
| MIC-02  | Test Count          | Ambiguously cited as "57 tests"    | Fully disaggregated: 124 test items | TEST_COUNT_AUDIT.md |
|         | Terminology         | and "124 tests".                   | collected & executed across 20 test |                     |
|         |                     |                                    | files (all 124 passing). 57 was     |                     |
|         |                     |                                    | unittest.TestCase methods only.     |                     |
+-------------------------------------------------------------------------------------------------------------------------------+
| MIC-03  | Switching Latency   | Labeled in seconds ("s"):          | Corrected to stream steps ("steps"):| SWITCH_LATENCY_UNIT_|
|         | Units               | +50 s, +763.0 s, +290.5 s.         | +50 steps, +763.0 steps,            | AUDIT.md            |
|         |                     |                                    | +290.5 steps. Conversion = 1.0.     |                     |
+-------------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Verified Hard Gate A8 Evaluation

```
MEMORY_ACCOUNTING_SEMANTICS_RESOLVED = YES
TEST_COUNT_TERMINOLOGY_RESOLVED = YES
SWITCH_LATENCY_UNITS_RESOLVED = YES
CANONICAL_SRC_CHANGED = NO
CANONICAL_TESTS_CHANGED = NO
```

### Gate Compliance Statement
All three microcorrections are achieved with **zero modifications to canonical `src/`**, **zero modifications to canonical `tests/`**, and **zero new stochastic simulations**. Phase A is declared formally **COMPLETE** and authorized to unlock Phase B.
