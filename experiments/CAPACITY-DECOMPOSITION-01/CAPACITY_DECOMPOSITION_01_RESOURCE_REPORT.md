# CAPACITY-DECOMPOSITION-01: Algorithmic Resource Report

**Stage:** CAPACITY-DECOMPOSITION-01 — Causal Capacity Decomposition  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  

---

## 1. Resource Footprint Across All Tested Variants

| Variant | Paradigm / Axis | Trainable Params | Mean FLOPs/step | Persistent Memory (Bytes) | R2-FLOP ($\le 100$) | R2-MEM ($\le 1024$) | Resource Classification |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **B0: Frozen Baseline** | Core Architecture | 25 | 79.5 | 443 | **PASS** | **PASS** | `WITHIN_ENVELOPE` |
| **B1: No Rec Birth** | Causal Linear Ablation | 20 | 64.0 | 320 | **PASS** | **PASS** | `WITHIN_ENVELOPE` |
| **E0: NLMS** | Pure Linear ($x_t$) | 20 | 63.0 | 152 | **PASS** | **PASS** | `WITHIN_ENVELOPE` |
| **E1: Online RLS** | Second-Order Matrix RLS | 20 | 1090.0 | 2184 | **FAIL** (16.8×) | **FAIL** (3.3×) | `COMPUTE_PROHIBITIVE` |
| **E3: OLS Oracle** | Offline Exact SVD | 20 | 40.0 | 160 | N/A | N/A | `NON_CAUSAL_CEILING` |
| **T1: Lag 1** | Delay Coordinate (Lag 1) | 40 | 123.0 | 272 | **FAIL** (1.3×) | **PASS** | `SLIGHTLY_ABOVE_FLOPS` |
| **T3: Lag 4** | Delay Coordinate (Lag 4) | 100 | 303.0 | 728 | **FAIL** (3.2×) | **PASS** | `MODERATELY_ABOVE_FLOPS` |
| **T4: Lag 8** | Delay Coordinate (Lag 8) | 180 | 543.0 | 1336 | **FAIL** (5.8×) | **FAIL** (1.6×) | `PROHIBITIVE_MEMORY_FLOPS` |
| **T5: Sparse Lags** | Targeted Sparse Delays | 23 | 75.0 | 4344 | **PASS** (74 FLOPs) | **PASS** (420 Bytes) | `WITHIN_ENVELOPE` / **EFFICIENT** |
| **NL2: RFF** | Random Fourier Features | 50 | 1803.0 | 3400 | **FAIL** (1.6×) | **PASS** | `MODERATELY_ABOVE_FLOPS` |
| **NL3: MLP** | Shallow Neural Net | 353 | 1472.0 | 2824 | **FAIL** (7.2×) | **FAIL** (2.8×) | `COMPUTE_PROHIBITIVE` |
| **REC_N1** | 1-State Scalar RTRL | 42 | 107.0 | 392 | **PASS** (92 FLOPs) | **PASS** (440 Bytes) | `WITHIN_ENVELOPE` |
| **REC_N2** | 2-State Coupled RTRL | 66 | 155.0 | 552 | **FAIL** (1.4×) | **PASS** (620 Bytes) | `SLIGHTLY_ABOVE_FLOPS` |
| **REC_N4** | 4-State Coupled RTRL | 120 | 263.0 | 920 | **FAIL** (2.9×) | **FAIL** (1.1×) | `COMPUTE_PROHIBITIVE` |
