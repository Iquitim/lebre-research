# BENCH_01B_REPRODUCIBILITY_REPORT.md — Cryptographic Audit & Reproducibility Package

**Protocol:** BENCH-01B  
**Milestone:** External Competitive Benchmark Execution  
**Governing Standard:** Section 160 of Protocol BENCH-01B, `BENCH_01_SPEC.md`  
**Date:** September 19, 2026  

---

## 1. Cryptographic Hash Audit (Bit-Level Immutability)

The execution of BENCH-01B strictly verified that all protocol specification documents, configuration schemas, and dataset artifacts matched their preregistered SHA-256 cryptographic digests prior to execution:

### 1.1 Specification & Configuration Artifacts

| Document / Configuration File | Preregistered SHA-256 Hash | Verification Status |
| :--- | :--- | :---: |
| `BENCH_01_SPEC.md` | `f516914da4d511e9ed58c2eb575d628bf3e01ebaab9f8bf63f9da0ebfe0e0c28` | **VERIFIED PASS** |
| `experiments/BENCH-01A/bench_01_locked_config.json` | `cb0d696e3e2775afa802a5a037ddf58ad3887252e4ac302e62b7e6162d334f7a` | **VERIFIED PASS** |
| `experiments/BENCH-01B/BENCH_01B_SUPPLEMENTARY_PRIOR_ART_CONFIG.json` | `2d8302495db638437f6c118438a53acc41fbe1efa4f787c01a224fb7f5da10dc` | **VERIFIED PASS** |

### 1.2 External Dataset Artifacts (`data/external/`)

| Dataset Artifact | Shape | File Size (Bytes) | Verification Status |
| :--- | :---: | :---: | :---: |
| `elec2_nsw_continuous.csv` | $(45312, 7)$ | $2,185,572$ | **VERIFIED PASS** |
| `jena_climate_2014_2016.csv` | $(70000, 15)$ | $9,460,944$ | **VERIFIED PASS** |
| `gas_dynamic_mixture_co.csv` | $(20000, 19)$ | $4,858,354$ | **VERIFIED PASS** |
| `silverbox_eval_sn.csv` | $(40000, 2)$ | $1,617,790$ | **VERIFIED PASS** |
| `household_power_submetering.csv` | $(25000, 9)$ | $1,570,305$ | **VERIFIED PASS** |

---

## 2. Seed Suite Specification

- **Calibration Seeds ($N_{\text{cal}} = 3$):** `[42, 43, 44]` (strictly restricted to $[0.00T, 0.15T)$ prefix).
- **Evaluation Seeds ($N_{\text{eval}} = 30$):** `[101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130]`.
- All pseudorandom generators utilize NumPy `np.random.RandomState(seed)` instantiated locally per stream.

---

## 3. Step-by-Step Reproduction Recipe

To reproduce all 6,750 competitive runs, CSV manifests, and publication figures from scratch:

```bash
# 1. Verify project test suite integrity
python -m pytest tests/

# 2. Run the unified benchmark execution engine
python -u -m experiments.bench01.runner
```

### Execution Artifact Output Manifest:
1. `experiments/BENCH-01B/BENCH_01B_CALIBRATION_LOG.csv` (2,700 evaluated hyperparameter configurations across 14 baselines).
2. `experiments/BENCH-01B/BENCH_01B_RUN_MANIFEST.csv` (6,750 run-level prequential evaluations).
3. `experiments/BENCH-01B/BENCH_01B_FAILURE_MANIFEST.csv` (319 logged numerical divergences with failure timestamps).
4. `experiments/BENCH-01B/BENCH_01B_PRIMARY_RESULTS.csv` (2,700 primary competitive runs: Track B + B1–B5).
5. `experiments/BENCH-01B/BENCH_01B_PRIOR_ART_CHALLENGERS.csv` (4,050 supplementary challenger runs: S1–S5 + C1–C4).
6. `experiments/BENCH-01B/BENCH_01B_AGGREGATE_SUMMARY.csv` (Grouped mean, std, peak FLOPs, memory, and divergence rates).
7. Figures `F1_pareto_loss_vs_flops.png` through `F8_failure_and_completion_rates.png`.
8. `experiments/BENCH-01B/raw/*.json` (6,750 individual JSON run records).

---

## 4. Hardware & Environment Profile

- **Operating System:** Windows 11 AMD64
- **Python Runtime:** Python 3.11.9 64-bit
- **Core Dependencies:** `numpy==2.1.2`, `scipy==1.14.1`, `pandas==2.2.3`, `matplotlib==3.9.2`, `pytest==9.0.2`
- **CPU Execution:** Single-threaded causal stepping per run, zero GPU reliance, deterministic floating-point arithmetic.
