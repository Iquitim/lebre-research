# Frozen Empirical Evidence Reconciliation Report: BENCH-01B, CAR-01 & M2

**Stage:** ARCH-SPEC-01R2  
**Date:** September 19, 2026  
**Status:** SEALED EMPIRICAL TRUTH RECONCILED  
**Governing Rule:** Raw Sealed CSV / Manifest > Frozen Aggregate Tables > Final Benchmark Report > Narrative Documentation.

---

## 1. Authoritative Machine-Readable Sources of Truth

All numbers, workload names, and baseline outcomes documented across the LEBRE v0.1 architecture specification suite originate exclusively from the following immutable, sealed artifacts:

1. `experiments/BENCH-01B/BENCH_01B_AGGREGATE_SUMMARY.csv` (Primary machine-readable benchmark record)
2. `experiments/BENCH-01B/BENCH_01B_PER_DATASET_ANALYSIS.md` (Per-workload diagnostic breakdowns across 30 seeds)
3. `experiments/BENCH-01B/BENCH_01B_FINAL_REPORT.md` (Sealed comparative evaluation report)
4. `benchmarks/bench_01_locked_config.json` (Locked benchmark protocol specification)
5. `experiments/CAR-01/CAR_01_FINAL_REPORT.md` (Architectural evidence synthesis)

---

## 2. Canonical BENCH-01B Workload Suite Mapping

The BENCH-01B benchmark suite comprises 15 evaluated streaming datasets partitioned into three canonical blocks:
- **Block A (Mechanistic Synthetic Workloads):** Tasks A1–A8
- **Block B (Real-World & Dynamical System Identification Workloads):** Tasks B1–B5
- **Block H (Hostile & Adversarial Diagnostic Regimes):** Tasks H1–H2

---

## 3. Block B Canonical Identity Reconciliation (B1–B5)

### 3.1 Prior Defect & Misattribution
A previous documentation editing pass inadvertently substituted benchmark names from unrelated system-identification literature ("Cascaded Tanks", "Coupled Electric Drives", "pH Neutralization Process", "Wiener-Hammerstein Benchmark") into narrative summaries and mislabeled Task B5 as "Silverbox Non-linear Resonance".

### 3.2 Canonical Workload Mapping from Sealed Artifacts

| Block B Task ID | Canonical Dataset Name | File Stem / Artifact ID | Input Dim ($D$) | Stream Steps | Evaluation Horizon |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **B1** | NSW Electricity Continuous | `NSW_Electricity_Derived_Regression` | 8 | 45,312 | Continuous Online Streaming |
| **B2** | Jena Weather Temperature | `Jena_Weather` | 14 | 70,091 | Continuous Online Streaming |
| **B3** | Gas Dynamic Mixture | `Gas_Dynamic_Mixture` | 16 | 29,571 | Continuous Online Streaming |
| **B4** | Silverbox System ID | `Silverbox_System_ID` | 1 | 8,192 | Continuous Dynamical Identification |
| **B5** | Household Active Power | `Household_Power_Control` | 7 | 20,000 | Continuous Online Streaming |

---

## 4. Reconciled Benchmark Values Across Evaluated Workloads

### 4.1 Synthetic Mechanistic Suite (Tasks A1–A8)

Values extracted directly from `experiments/BENCH-01B/BENCH_01B_AGGREGATE_SUMMARY.csv`:

| Task ID | Workload Identity | RZA-LMS | CCN | Minimal GRU | Online ESN | LEBRE v0.1 | LEBRE Mean FLOPs | Empirical Outcome / Inductive Bias Characterization |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **A1** | Sparse Support Shift | **0.0169** | 0.0185 | 0.7897 | 0.7695 | 0.0379 | 205.3 | Linear baseline sufficiently expressive; RZA-LMS won; LEBRE adapts with 0 births. |
| **A2** | Single Delayed Dependency | 1.0010 | 1.0109 | 1.0001 | **0.9680** | 1.1327 | 97.5 | Representational boundary: Dense ESN reservoir won; scalar state insufficient without delay lag bank. |
| **A3** | Multiple Dispersed Delays | 1.0002 | 1.0107 | 1.0002 | **0.9593** | 1.1287 | 97.5 | Representational boundary: Dense ESN reservoir won; scalar state insufficient. |
| **A4** | Long-Delay Scaling | 1.0002 | 1.0106 | **1.0001** | 1.0005 | 1.1356 | 97.4 | Representational boundary: Gated units (GRU) marginally won; scalar state insufficient. |
| **A5** | Set/Reset Quiescent Memory | 1.0234 | **0.4076** | 1.0277 | 0.9990 | 0.7901 | 68.4 | CCN won; LEBRE sustained quiescent memory; instantaneous baselines failed ($>1.02$). |
| **A6** | Context Routing | **0.5245** | 0.5416 | 0.6848 | 0.6036 | 0.5668 | 56.3 | RZA-LMS won; LEBRE tracked closely at 56.3 FLOPs. |
| **A7** | Extended Poisson Quiescence | 1.0185 | **0.6017** | 1.0198 | 1.0059 | 0.8535 | 60.3 | CCN won; LEBRE retained state across long Poisson silent gaps; LMS/GRU collapsed. |
| **A8** | Abrupt Tri-Regime Transition | 0.9807 | 0.9916 | 0.9807 | 1.0209 | **0.9540** | 57.6 | **LEBRE won**; dynamically modulated topology and compute ($38 \to 92 \to 40$ FLOPs). |

### 4.2 Real-World Continuous Suite (Tasks B1–B5)

Values extracted directly from `experiments/BENCH-01B/BENCH_01B_AGGREGATE_SUMMARY.csv`:

| Task ID | Real-World Workload Name | RZA-LMS | CCN | Minimal GRU | Online ESN | LEBRE v0.1 | LEBRE Mean FLOPs | Sealed Winner & Empirical Characterization |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **B1** | NSW Electricity Continuous | 0.9787 | **0.4632** | 2.4146 | 1.4238 | 0.8364 | 24.04 | CCN won ($0.4632$); LEBRE competitive at $0.8364$ with low mean compute ($24.0$ FLOPs). |
| **B2** | Jena Weather Temperature | DIVERGED | DIVERGED | 0.0742 | 0.3284 | **0.0248** | 69.81 | **LEBRE won** ($0.0248$); RZA-LMS and CCN numerically diverged ($>10^3$). |
| **B3** | Gas Dynamic Mixture | 0.0492 | 0.0390 | 0.0241 | 0.2608 | **0.0020** | 79.94 | **LEBRE won** ($0.002032$); strictly outperformed all four competing baselines. |
| **B4** | Silverbox System ID | 0.9993 | 0.9963 | 0.9999 | **0.9136** | 0.9932 | 8.00 | **Online ESN won** ($0.91359$); LEBRE ($0.99320$) documented inductive bias boundary on nonlinear multi-harmonic resonance. |
| **B5** | Household Active Power | 0.0912 | 0.0120 | 0.0924 | 0.1129 | **0.0040** | 28.30 | **LEBRE won** ($0.004029$); strictly outperformed CCN ($0.01200$), RZA-LMS ($0.09120$), and GRU ($0.09240$). |

---

## 5. Explicit Reconciliation of Critical Numbers

### 5.1 Task B5 (Household Power) Metrics
- **LEBRE NMSE:** $0.004029$ (documented as $0.0040$ or $0.00403$)
- **CCN NMSE:** $0.01200$
- **RZA-LMS NMSE:** $0.09120$
- **Minimal GRU NMSE:** $0.09240$
- **Online ESN NMSE:** $0.11290$
- **LEBRE Mean Compute:** $28.30$ FLOPs/step
- **LEBRE Model Memory:** $248$ bytes

### 5.2 Task B4 (Silverbox) Metrics
- **Online ESN NMSE:** $0.91359$ (Winner)
- **LEBRE NMSE:** $0.99320$
- **CCN NMSE:** $0.99630$
- **RZA-LMS NMSE:** $0.99930$
- **Minimal GRU NMSE:** $0.99990$
- **LEBRE Mean Compute:** $8.00$ FLOPs/step
- **LEBRE Model Memory:** $208$ bytes
- **Significance:** Explicitly documented as an architectural boundary where 50-unit random reservoir projection outperforms minimal scalar recurrence ($N \le 1$) on high-order continuous mechanical vibrations.

### 5.3 Overall Suite Resource & Stability Metrics
- **Mean Algorithmic Compute (all workloads):** $90.44$ FLOPs/step (Complies with R2-FLOP $\le 100$ FLOPs/step ceiling)
- **Peak Transient Compute:** $\approx 206$ FLOPs/step (during concurrent candidate probation and feature probing)
- **Mean Persistent Model State Footprint:** $440.0$ bytes (Complies with R2-MEM $\le 1024$ bytes ceiling)
- **Evaluated Runs:** 450 runs (30 random seeds across 15 workloads)
- **Observed Numerical Divergences:** $0$ ($0.00\%$ divergence rate; contrasting with $13.3\%$ for RZA-LMS and $6.7\%$ for CCN)
- **Overall Competitive Win Rate:** $53.3\%$ statistical wins, $8.0\%$ ties, $38.7\%$ losses

---

## 6. Eradication of Prior Inaccurate Values

1. **Removed:** Fictitious system-ID names ("Cascaded Tanks", "Coupled Electric Drives", "pH Neutralization", "Wiener-Hammerstein").
2. **Removed:** Inversion of Silverbox as B5 instead of B4.
3. **Removed:** Claims that LEBRE outperformed ESN on Silverbox.
4. **Removed:** Claim that LEBRE memory is universally bounded to 440 bytes for any system.
5. **Removed:** Claim that LEBRE has been flashed or benchmarked on physical ARM Cortex microcontrollers.

All values are now 100% reconciled against sealed machine-readable evidence.
