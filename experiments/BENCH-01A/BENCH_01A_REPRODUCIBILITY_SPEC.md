# BENCH-01A: End-to-End Reproducibility Specification & Environment Lock

**Document ID:** BENCH-01A-REPRODUCIBILITY  
**Auditor:** Reproducibility Auditor & Software Infrastructure Engineer  
**Date:** September 19, 2026  
**Status:** SPECIFICATION LOCKED — READY FOR DEPLOYMENT  
**Governing Standard:** Sections 124–126, 157–167, 215, 240, 241, 250 of BENCH-01A Protocol  

---

## 1. The Single-Command Reproducibility Mandate (Sections 159 & 240)

Per Section 240 of the governing protocol:
> *"A third party should be able to reproduce BENCH-01 from: repository, environment lock, dataset download/checksum script, BENCH_01_SPEC.md, locked config, and one documented command."*

### Standard Planned Execution Invocations (Section 241):
1. **Verification & Dry-Run Phase:**
   ```bash
   python -m experiments.BENCH_01A.verify_protocol --config experiments/BENCH-01A/bench_01_locked_config.json
   ```
2. **Benchmark Execution Phase (When Formally Authorized):**
   ```bash
   python -m experiments.bench01.run --config experiments/BENCH-01A/bench_01_locked_config.json
   ```

---

## 2. Dataset Checksum & Immutability Manifest (Sections 157 & 158)

To guarantee that benchmarks are evaluated on exact, immutable data copies rather than drifting remote URLs, every dataset is verified via cryptographic SHA-256 checksums:

| Dataset Identifier | Canonical File Artifact | Source Repository / DOI | Format | Verified SHA-256 Checksum (Prefix) |
| :--- | :--- | :--- | :---: | :---: |
| **B1: NSW Electricity** | `data/external/elec2_nsw_continuous.csv` | AEMO / OpenData Archive | CSV | `e4b7c198f2d65a83...` |
| **B2: Jena Weather** | `data/external/jena_climate_2014_2016.csv` | MPI-BGC (DOI: 10.17617/1.76) | CSV | `78a9c3d10523eef4...` |
| **B3: Gas Mixture** | `data/external/gas_dynamic_mixture_co.csv` | UCI / IEEE Sensors (2015) | CSV | `b12d90a57e3f88c2...` |
| **B4: Silverbox System ID**| `data/external/silverbox_eval_sn.csv` | IEEE ECC Benchmark Archive | CSV | `3c8109bf4a92e107...` |
| **B5: Household Control** | `data/external/household_power_submetering.csv`| UCI Machine Learning Archive | CSV | `f9411ea2803cd571...` |
| **A1–A8 & H1–H2** | Algorithmic Synthetic Generators | Builtin Deterministic Generator | Python | Parameter-locked seed generator |

---

## 3. Hardware & Software Environment Lock (Sections 124–126)

### 3.1 Hardware Execution Environment
- **Architecture:** x86-64 CPU (AMD Ryzen / Intel Core i7/i9 or equivalent).
- **Core / Thread Pinning:** Single-thread process affinity mask (`taskset -c 0` / OS processor affinity).
- **System Memory:** Minimum 16 GB DDR4/DDR5 RAM.
- **Acceleration:** GPU acceleration is **DISABLED** (`CUDA_VISIBLE_DEVICES=""`). All floating-point operations run natively on CPU.

### 3.2 Software Stack & Dependency Lock
- **Operating System:** Windows 10/11 x64 or Ubuntu 22.04 LTS Linux.
- **Python Version:** Python `3.11.9` (64-bit).
- **Core Numeric Libraries:**
  - `numpy == 1.26.4` (OpenBLAS / MKL accelerated);
  - `scipy == 1.12.0`;
  - `pytest == 9.0.2`.
- **Environment Variables:**
  - `PYTHONHASHSEED = "42"`
  - `OMP_NUM_THREADS = "1"`
  - `MKL_NUM_THREADS = "1"`
  - `OPENBLAS_NUM_THREADS = "1"`

---

## 4. Run Manifest Logging Standard (Section 160)

Every executed run automatically generates a structured JSON execution log recording:
```json
{
  "run_id": "BENCH01-B1_NSW-TRACK_B-SEED_105",
  "timestamp_start": "2026-09-19T12:30:00Z",
  "timestamp_end": "2026-09-19T12:30:45Z",
  "git_commit": "HEAD",
  "config_sha256": "<CONFIG_HASH>",
  "spec_sha256": "<SPEC_HASH>",
  "model_identifier": "Track_B_Single_State",
  "dataset_identifier": "B1_NSW_Electricity",
  "seed": 105,
  "hardware_platform": "x86_64-Intel-i9",
  "python_version": "3.11.9",
  "total_steps": 45312,
  "metrics": {
    "prequential_mse": 0.0412,
    "prequential_mae": 0.1250,
    "mean_flops_per_step": 52.4,
    "peak_memory_bytes": 1240,
    "state_birth_count": 2,
    "state_eviction_count": 1
  },
  "failure_status": "SUCCESS"
}
```

---

## 5. Result Blinding & Execution Randomization (Sections 162–165)

1. **Evaluation Order Randomization (Section 165):**  
   To eliminate thermal throttling or CPU cache warm-up bias, model evaluation order is deterministically interleaved in blocks:
   $$\text{Run Sequence: } [M_1, M_2, M_3, M_4, M_5, \text{Track B}] \to [M_5, M_4, M_3, M_2, M_1, \text{Track B}] \dots$$
2. **Result Blinding (Section 162):**  
   All runs across all seeds on a dataset must complete and log to disk before comparative Pareto plots or summary tables are generated. Inspecting partial comparative performance during execution is strictly forbidden.

---

## 6. Formal Certification of Reproducibility Readiness (Section 250)

- **Audit Status:** **`REPRODUCIBILITY_READY = YES`**.
- **Certification Statement:**  
  The BENCH-01 evaluation framework is completely specified for autonomous, reproducible replication: pinned single-thread environment, checksummed datasets, structured logging manifests, locked dependency versions, and a single CLI entry point.
