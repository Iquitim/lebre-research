<p align="center">
  <img src="../../logo/LEBRE Logo.png" alt="LEBRE Architecture logo" width="700">
</p>

# LEBRE Architecture: Executive Overview
**Full Expansion:** Lifecycle-governed Evidence-Based Resource Evolution  
**Specification Version:** 0.1 | **Status:** FROZEN_WITH_SCOPE_LIMITS  
**Historical Provenance:** Track B Single-State Organization (*Codinome Lebre*)  

---

## 1. Executive Summary

**LEBRE** is an online adaptive learning architecture designed for continuous streaming regression under micro-edge compute and memory constraints. Rather than maintaining a rigid, static parameter network or dense reservoir, LEBRE treats observable input features, temporal delay taps, and internal recurrent states as **cost-bearing adaptive computational structures**. Every structural component is subjected to a unified, evidence-driven lifecycle ($\text{DORMANT} \to \text{PROVISIONAL} \to \text{ACTIVE} \to \text{MATURE} \to \text{EVICTED}$). By isolating provisional candidates in non-interfering shadow probation, decoupling fast activity from slow relevance across quiescent gaps, and demanding positive evidence of obsolescence before deallocation, LEBRE achieves continuous, stable adaptation with an observed mean persistent model-state footprint of 440.0 bytes of RAM (compliant with the R2-MEM $\le 1024$ bytes ceiling; excluding execution stack and runtime buffers) and a measured mean algorithmic compute within the R2-FLOP limit of 100 FLOPs/step (mean 90.44 FLOPs/step, observed transient peak $\approx 206$ FLOPs/step).

---

## 2. The Core Structural Lifecycle

Every adaptive element in LEBRE is governed by an explicit 5-stage lifecycle state machine:

$$\text{DORMANT} \xrightarrow{\text{Residual Error Trigger}} \text{PROVISIONAL} \xrightarrow{\text{Probationary Utility}} \text{ACTIVE} \xrightarrow{\text{Age } \ge \tau_{\text{mature}}} \text{MATURE} \xrightarrow{\text{Positive Obsolescence}} \text{EVICTED / RECLAIMED}$$

- **DORMANT:** Latent structure consuming $0$ FLOPs and $0$ bytes of active memory.
- **PROVISIONAL (Shadow Probation):** Candidate structure learns parameters in parallel without coupling to live predictions, completely shielding the system from candidate shock.
- **ACTIVE:** Promoted structure coupled to live inference ($\hat{y}_t = \hat{y}_{\text{base}, t} + \hat{y}_{\text{rec}, t}$), protected by an initial maturation grace period.
- **MATURE:** Established structure required to continuously "pay rent" through sustained predictive or structural utility ($U_{\text{ret}}$).
- **EVICTED & RECLAIMED:** Physically excised structure whose arrays are deallocated and compute loops eliminated, returning resources to the available budget.

---

## 3. Key Empirical Results (BENCH-01B Sealed Benchmark)

LEBRE was evaluated across 15 continuous workloads (Block A mechanistic diagnostics, holdouts, and Block B real-world physical and sensor streams) over 30 independent seeds ($N=30$, 6,750 total competitive runs) against 14 baseline architectures:

| Metric / Workload | LEBRE (Frozen Track B) | Minimal GRU Baseline | Online ESN Baseline | Sealed Benchmark Context |
| :--- | :---: | :---: | :---: | :--- |
| **Mean FLOPs / Step** | **90.44** (Peak $\approx 206$) | 281.80 | 1,683.67 | **PASS** (Mean R2-FLOP $\le 100$ threshold) |
| **Persistent Model RAM** | **440.0 Bytes** | 569.6 Bytes | 6,112.0 Bytes | **PASS** (Persistent R2-MEM $\le 1024$; excludes stack/OS) |
| **Mean Benchmark NMSE** | **0.7023** | 0.8730 | 0.8161 | Evaluated across all 15 continuous workloads |
| **Observed Divergences** | **0 / 450 (0.00%)** | 0 / 450 (0.00%) | 0 / 450 (0.00%) | Zero numerical divergences observed in LEBRE runs |
| **Real-World B1 (NSW Electricity)** | 0.8364 NMSE | 2.4146 NMSE | 1.4238 NMSE | CCN achieved lowest error (0.4632); LEBRE at 24.0 FLOPs |
| **Real-World B2 (Jena Weather)** | **0.0248 NMSE** | 0.0742 NMSE | 0.3284 NMSE | LEBRE led baselines; RZA-LMS & CCN diverged |
| **Real-World B3 (Gas Sensor)** | **0.00203 NMSE** | 0.02410 NMSE | 0.26080 NMSE | LEBRE achieved lowest error across all models (79.9 FLOPs) |
| **Real-World B4 (Silverbox ID)** | 0.9932 NMSE | 0.9999 NMSE | **0.9136 NMSE** | Documented boundary: dense ESN reservoir outperformed scalar state |
| **Real-World B5 (Power Demand)**| **0.00403 NMSE** | 0.09240 NMSE | 0.11290 NMSE | LEBRE achieved lowest error (CCN: 0.0120, RZA: 0.0912) |

---

## 4. Known Boundaries & Limitations

LEBRE v0.1 is documented under explicit operational boundaries:
1. **Scalar Recurrence Ceiling ($N \le 1$):** Validated strictly for at most one active recurrent scalar state. Multi-state capacity ($N > 1$) is deferred to future unopened Milestone M3.
2. **High-Order Shift Registers (Tasks A2–A4):** A single scalar recurrent state cannot represent high-order delay lines without lag buffer feature expansion.
3. **Complex Nonlinear System ID (Task B4 Silverbox):** Continuous nonlinear system identification favors multidimensional random reservoirs (Online ESN).
4. **Micro-Regimes ($< 200$ steps):** Asymmetric hysteresis eviction requires sustained obsolescence evidence, resulting in temporary retention across ultra-short transients.
5. **Hardware Deployment Status:** LEBRE is a candidate for future constrained embedded deployment based on its low measured algorithmic compute and persistent state footprint; hardware deployment (MCU wall-clock latency, energy, total memory) has not yet been validated.

---

## 5. Architectural Non-Goals

LEBRE is explicitly **not**:
- A Large Language Model (LLM) or Transformer replacement.
- A biological brain simulation or neuro-mimetic architecture.
- An offline batch-learning framework.
- An unconstrained, arbitrarily deep latent representation learner.

---

## 6. Documentation Links (Relative)

- **Full Formal Specification (English):** [LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md](LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md)
- **Full Formal Specification (Portuguese):** [LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md](LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md)
- **Architectural Diagrams:** [LEBRE_ARCHITECTURE_DIAGRAMS.md](LEBRE_ARCHITECTURE_DIAGRAMS.md)
- **Architectural Decision Records:** [LEBRE_ARCHITECTURAL_DECISIONS.md](LEBRE_ARCHITECTURAL_DECISIONS.md)
- **Traceability Matrix:** [LEBRE_TRACEABILITY_MATRIX.csv](LEBRE_TRACEABILITY_MATRIX.csv)
- **Constant Traceability Audit:** [LEBRE_CONSTANT_TRACEABILITY.md](LEBRE_CONSTANT_TRACEABILITY.md)
- **Machine-Readable Manifest:** [LEBRE_ARCHITECTURE_MANIFEST.yaml](LEBRE_ARCHITECTURE_MANIFEST.yaml)
