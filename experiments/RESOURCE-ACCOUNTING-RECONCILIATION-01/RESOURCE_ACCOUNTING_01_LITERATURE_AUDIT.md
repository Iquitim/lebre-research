# RESOURCE-ACCOUNTING-RECONCILIATION-01: Foundational Literature Audit
## Formal Theoretical Foundations for Heterogeneous Resource Accounting on Micro-Edge Streaming

**Stage:** `RESOURCE-ACCOUNTING-RECONCILIATION-01`  
**Governing Context:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Auditor Role:** Senior ML Systems Researcher, Embedded DSP Specialist, Computer Architect  
**Status:** `PRE-EXPERIMENTAL_FREEZE`

---

## 1. Executive Statement of Purpose

The central scientific motivation of `RESOURCE-ACCOUNTING-RECONCILIATION-01` is to resolve a critical computational ambiguity: the apparent contradiction between historical resource reports (B7 reported at **82.0 FLOPs/step**) and subsequent bounded-history baselines (H0 FP32 reported at **125.1 FLOPs/step**, H3 INT8 reported at **176.0 FLOPs/step**). 

Comparing these representations directly without a rigorous, disaggregated operation taxonomy introduces two catastrophic methodological errors:
1. **Operator Conflation:** Indiscriminately labeling integer arithmetic, pointer indexing, scale adjustments, rounding, and byte moves as "FLOPs".
2. **Ignoring Memory Traffic:** Evaluating edge feasibility purely on arithmetic count while ignoring memory bandwidth, buffer traffic, and operational intensity.

This literature audit establishes the primary theoretical boundaries and architectural principles that govern our reconciled accounting framework.

---

## 2. Review of Authoritative Foundations

### A. Roofline Model & Operational Intensity
- **Primary Source:** Williams, S., Waterman, A., & Patterson, D. *"Roofline: An Insightful Visual Performance Model for Multicore Architectures."* Communications of the ACM, Vol. 52, No. 4, pp. 65–76, 2009.
- **Key Principles & Extraction for LEBRE:**
  - **Arithmetic vs. Bandwidth Bound:** Peak attainable performance $P$ (ops/sec or FLOPs/cycle) is bounded by $P \le \min\left(\text{Peak Performance}, I \times \text{Peak Bandwidth}\right)$, where $I$ is operational intensity (arithmetic operations per byte of DRAM/SRAM traffic).
  - **FLOP Count Does Not Equal Execution Time:** An algorithm that performs fewer FLOPs but moves substantially more data across buses or memory hierarchies can be significantly slower than an algorithm with higher compute density.
  - **Micro-Edge Application:** While high-end multicore Roofline models focus on DRAM caches and PCIe/DDR channels, the fundamental distinction applies directly to microcontrollers (Cortex-M0+/M4/M7): on-chip SRAM access, bus contention, and register pressure dominate latency and energy. An INT8 quantized history buffer that reduces bytes read from 660 B to 165 B fundamentally alters the memory traffic regime, even if it requires additional local scaling operations.

### B. TinyML Benchmarking & Measurement Discipline
- **Primary Source:** Banbury, C., et al. *"MLPerf Tiny Benchmark."* Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks, 2021.
- **Key Principles & Extraction for LEBRE:**
  - **Multi-Dimensional Constraint Envelope:** No single scalar metric (neither "FLOPs" nor "MACs") adequately characterizes an embedded implementation. TinyML systems are strictly constrained across four distinct vectors: latency, energy, persistent memory (Flash/ROM), and working memory (SRAM).
  - **Measurement Boundary & Equivalence:** Benchmarking requires an uncompromisingly fixed system definition: identical clock frequencies, compiler optimization levels, memory layouts, warm-up conditions, and timer measurement boundaries.
  - **Quality-Constrained Resource Evaluation:** Resource reduction is scientifically meaningless if predictive accuracy or tracking convergence is destroyed. Reduced-precision implementations must be evaluated under strict task-level predictive parity constraints.

### C. Integer-Only Quantized Computation
- **Primary Source:** Jacob, B., et al. *"Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference."* IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), pp. 2704–2713, 2018.
- **Key Principles & Extraction for LEBRE:**
  - **Representation vs. Computation:** Quantizing a variable $q = \text{clip}\left(\text{round}\left(x / S\right) + Z, q_{\min}, q_{\max}\right)$ compresses storage, but operating on quantized values requires explicit fixed-point arithmetic: scale tracking, integer multiplication, bit shifts, and rounding.
  - **INT8 Operations Are NOT FLOPs:** Integer operations use integer ALU pipelines, barrel shifters, and integer registers. In modern microcontrollers (e.g. ARM Cortex-M4/M7), a single-cycle 32-bit integer MAC instruction is physically distinct from an IEEE 754 floating-point unit (FPU) cycle. Counting an integer addition or bit shift as a "FLOP" is a fundamental category error.
  - **Requantization & Scale Overhead:** In adaptive streaming, dynamic signal ranges require dynamic scale adaptation. This introduces non-zero computation during input writes or history queries that must be accounted for explicitly under `INTEGER_OPS`, `CASTS`, or `SCALE_UPDATE`.

### D. Finite-Word-Length Adaptive Filtering
- **Primary Source:** Yousef, N. R., & Sayed, A. H. *"Fixed-Point Steady-State Analysis of Adaptive Filters."* IEEE Transactions on Signal Processing, Vol. 51, No. 4, pp. 928–941, 2003.
- **Key Principles & Extraction for LEBRE:**
  - **Separation of Error, Wordlength, and Complexity:** In adaptive filters (LMS, NLMS, RLS), finite wordlength effects introduce coefficient quantization error, input quantization error, and round-off noise. The excess mean-square error (EMSE) scales predictably with quantization step size $\Delta = S / 2^{B-1}$.
  - **Empirical Decoupling:** One must not confuse the mathematical prediction error (EMSE degradation) with the architectural operation count (ALU cycles). A quantized filter may suffer small asymptotic excess error $\Delta \text{EMSE} \approx \sigma_q^2 / (2 - \mu)$ while requiring distinct integer conversion steps. Both dimensions must be audited independently.

### E. Hardware Energy & Datatype Scaling
- **Primary Source:** Horowitz, M. *"Computing's Energy Problem (and What Can We Do About It?)."* IEEE International Solid-State Circuits Conference (ISSCC) Digest of Technical Papers, pp. 10–14, 2014.
- **Key Principles & Extraction for LEBRE:**
  - **Energy Asymmetry Across Operations:**
    - An 8-bit integer addition consumes roughly $30\times$ less energy than a 32-bit floating-point addition ($0.03\,\text{pJ}$ vs $0.9\,\text{pJ}$ in 45nm).
    - An 8-bit integer multiplication consumes roughly $5\times$ to $20\times$ less energy than a 32-bit FP multiplication ($0.2\,\text{pJ}$ vs $3.7\,\text{pJ}$).
    - Reading data from an SRAM buffer consumes $10\times$ to $100\times$ more energy than an arithmetic ALU operation itself ($5\,\text{pJ}$ for 32-bit SRAM read vs $0.1\,\text{pJ}$ for an INT add).
  - **Methodological Guard:** While exact picojoule numbers vary across CMOS nodes and architectures, the qualitative hierarchy is immutable: memory traffic is energy-expensive, integer operations are lighter than IEEE floats, and reducing memory footprint directly preserves edge battery life. Therefore, reporting a single aggregated "FLOP" metric completely obscures the physical efficiency advantages of quantized history.

### F. Experimental Reproducibility & Traceability
- **Primary Source:** Association for Computing Machinery (ACM). *"Artifact Review and Badging."* Version 1.1, 2020; and National Academies of Sciences, Engineering, and Medicine. *"Reproducibility and Replicability in Science."* Washington, DC: The National Academies Press, 2019.
- **Key Principles & Extraction for LEBRE:**
  - **Immutable Baseline:** Reconciling past discrepancies requires preserving historical artifacts bitwise while publishing transparent corrigenda that map past conventions to the standardized taxonomy.
  - **Deterministic Microtraces:** Abstract formulas must be verified against actual cycle-by-cycle and step-by-step instrumented execution traces on deterministic reference streams.

---

## 3. Methodological Guardrails for this Stage

1. **Four Disaggregated Resource Channels:**
   - $\mathcal{R}_{\text{FP}}$: IEEE 754 Floating-Point Operations.
   - $\mathcal{R}_{\text{INT}}$: Integer arithmetic, logical, and bitwise operations.
   - $\mathcal{R}_{\text{MEM}}$: Memory traffic (Bytes read, bytes written, peak persistent/transient footprint).
   - $\mathcal{R}_{\text{PLAT}}$: Platform-dependent measured latency/cycles on host hardware.
2. **Standardized MAC Convention:**
   - $1 \text{ Multiply} = 1 \text{ FLOP}$.
   - $1 \text{ Addition/Subtraction} = 1 \text{ FLOP}$.
   - $1 \text{ FMA / Multiply-Accumulate} = 2 \text{ FLOPs}$.
   - If historical reports used $1 \text{ MAC} = 1 \text{ FLOP}$, that convention is documented as a legacy undercount and mapped explicitly.
3. **Strict Zero-Optimization Policy:**
   - Any identified inefficiencies in H0 or H3 will be measured and documented, but **not optimized** within this audit.
