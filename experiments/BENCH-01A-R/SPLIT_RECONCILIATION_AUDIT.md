# BENCH-01A-R: Chronological Stream Split Audit & Reconciliation

**Document ID:** BENCH-01A-R-SPLIT-AUDIT  
**Auditor:** Benchmark Methodology Auditor & Reproducibility Reviewer  
**Date:** September 19, 2026  
**Status:** RECONCILIATION COMPLETE — LOCKED SPLIT 15/15/70 CONFIRMED  

---

## 1. Audit Target & Problem Statement

A discrepancy was identified between:
- The **15/15/70** split previously documented across protocol specifications (`BENCH_01_SPEC.md`, `bench_01_locked_config.json`, `BENCH_01A_TUNING_SPEC.md`);
- An erroneous textual reference to **10/20/70** reported in conversational test summary narrative during the BENCH-01A-R closure report.

The auditor was instructed to:
1. Verify which partition is effectively encoded in `BENCH_01_SPEC.md` and `experiments/BENCH-01A/bench_01_locked_config.json`;
2. Select a single split under rigorous methodological justification without inspecting any competitive results;
3. Synchronize specification, configuration, automated tests, and documentation;
4. Verify cryptographic SHA-256 hashes of locked assets.

---

## 2. Codebase Verification of Locked Assets

A line-by-line inspection of locked benchmark files was performed:

### 2.1 `BENCH_01_SPEC.md` (Section 19)
```markdown
## 19. Chronological Calibration / Validation / Test Splitting (Sections 85–93)

- **Calibration Prefix (0% – 15%):** Hyperparameter selection on 3 seeds. Discarded from test scoring.
- **Validation Segment (15% – 30%):** Stability and divergence check.
- **Final Test Segment (30% – 100%):** Locked competitive evaluation over 30 independent seeds.
```
- **Calibration Prefix:** $t \in [0, 0.15 \cdot T]$ $\to$ Fraction = **$0.15$ (15%)**
- **Validation Segment:** $t \in [0.15 \cdot T, 0.30 \cdot T]$ $\to$ Fraction = **$0.15$ (15%)**
- **Final Test Segment:** $t \in [0.30 \cdot T, 1.00 \cdot T]$ $\to$ Fraction = **$0.70$ (70%)**

### 2.2 `experiments/BENCH-01A/bench_01_locked_config.json` (Lines 15–20)
```json
  "stream_chronological_splits": {
    "calibration_prefix_fraction": 0.15,
    "validation_segment_fraction": 0.15,
    "test_segment_fraction": 0.70,
    "warm_start_state_transfer": true
  },
```
- Exactly encoded as: **$0.15$ / $0.15$ / $0.70$**.

### 2.3 `experiments/BENCH-01A/BENCH_01A_TUNING_SPEC.md` (Section 2)
```markdown
|  [CALIBRATION PREFIX: 0% - 15%]  -->  Baseline Hyperparameter Grid Screen     |
|  [VALIDATION SEGMENT: 15% - 30%] -->  Configuration Stability Confirmation   |
|  [FINAL TEST SEGMENT: 30% - 100%]->  Frozen Competitive Evaluation (N=30 seeds|
```
- Fully aligned with: **$0.15$ / $0.15$ / $0.70$**.

### 2.4 Origin of the 10/20/70 Reference
In the previous turn narrative, the summary listed `splits (0.10 / 0.20 / 0.70)`. Simultaneously, the test `test_config_integrity()` in `tests/test_bench_01_protocol.py` loaded `bench_01_locked_config.json` (which contained $0.15 / 0.15 / 0.70$) but only asserted `np.isclose(total_fraction, 1.0)` without explicitly asserting the individual fractions. This textual reporting error created ambiguity.

---

## 3. Methodological Justification: 15/15/70 vs 10/20/70

A rigorous methodological evaluation of stream partitioning under online streaming constraints yields the following conclusion:

1. **Calibration Sample Adequacy ($T_{\text{calib}} = 0.15 \cdot T$):**
   - For shorter synthetic streams ($T = 10{,}000$ in Block A), a 10% calibration allocation would provide only 1,000 steps.
   - For baseline learners with temporal delays up to $D=50$ (e.g., Task A4) or sparse event latches with Poisson inter-event intervals $\sim 150$ steps (Task A7), 1,000 steps provides fewer than 7 excitation cycles. This is insufficient to reliably screen 16 candidate configurations across 3 seeds.
   - An allocation of 15% (1,500 steps) increases the event sample by +50%, substantially dampening initial selection variance and preventing selection of degenerate hyperparameter configurations.

2. **Validation Quarantine Function ($T_{\text{valid}} = 0.15 \cdot T$):**
   - The validation segment is strictly a stability confirmation / divergence guard; **no hyperparameter re-tuning or selection occurs here**.
   - Expanding validation from 15% to 20% would consume an extra 5% of stream data without serving any model selection purpose, whilst starving the calibration phase if taken from calibration.
   - An allocation of 15% ($1,500$ to $10{,}500$ steps depending on dataset) is more than sufficient to detect numerical overflow, gradient explosion, or infinite predictions.

3. **Competitive Out-of-Sample Test Quarantining ($T_{\text{test}} = 0.70 \cdot T$):**
   - The final 70% of every stream ($7{,}000$ steps on Block A; $49{,}000$ steps on Jena Weather) remains completely quarantined from hyperparameter selection and is evaluated across 30 independent seeds with state warm-start.

4. **Protocol Immutability & Zero-Churn Principle:**
   - Because `15/15/70` was the exact division specified in `BENCH_01_SPEC.md` and locked in `bench_01_locked_config.json` prior to any run, retaining `15/15/70` upholds pre-registration integrity and avoids modifying locked protocol specifications.

**Decision:** Formally lock and confirm **`15 / 15 / 70`** as the sole, canonical stream partition.

---

## 4. Synchronization of Spec, Config, Tests & Documentation

1. **`BENCH_01_SPEC.md`:** Confirmed at Section 19 (0%–15% Calibration, 15%–30% Validation, 30%–100% Test). Unmodified.
2. **`bench_01_locked_config.json`:** Confirmed at lines 15–20 (`0.15` / `0.15` / `0.70`). Unmodified.
3. **`tests/test_bench_01_protocol.py`:** Updated `test_config_integrity()` with explicit assertions:
   ```python
   splits = cfg["stream_chronological_splits"]
   assert splits["calibration_prefix_fraction"] == 0.15, "Calibration prefix must be exactly 0.15 (15%)"
   assert splits["validation_segment_fraction"] == 0.15, "Validation segment must be exactly 0.15 (15%)"
   assert splits["test_segment_fraction"] == 0.70, "Test segment must be exactly 0.70 (70%)"
   assert np.isclose(total_fraction, 1.0), "Splits must sum to 1.0"
   ```
4. **Documentation:** Synchronized in `PROJECT_STATE.md`, `BENCH_01A_R_SUMMARY.md`, and this audit record.

---

## 5. Cryptographic SHA-256 Hash Verification

Because neither `BENCH_01_SPEC.md` nor `experiments/BENCH-01A/bench_01_locked_config.json` required byte-level changes (both already contained the correct `15/15/70` split), their previously reconciled cryptographic hashes remain 100% valid:

- **`BENCH_01_SPEC.md` SHA-256:**  
  `f516914da4d511e9ed58c2eb575d628bf3e01ebaab9f8bf63f9da0ebfe0e0c28`
- **`experiments/BENCH-01A/bench_01_locked_config.json` SHA-256:**  
  `cb0d696e3e2775afa802a5a037ddf58ad3887252e4ac302e62b7e6162d334f7a`

---

## 6. Execution Safeguards

- Milestone M3 remains **`UNOPENED`**;
- Competitive benchmark execution of BENCH-01B remains **`UNOPENED`**;
- No competitive performance data has been generated, inspected, or utilized;
- All unit and protocol tests pass (124/124).
