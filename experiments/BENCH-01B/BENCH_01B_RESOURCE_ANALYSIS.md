# BENCH_01B_RESOURCE_ANALYSIS.md — Computational FLOP & Memory Resource Accounting

**Protocol:** BENCH-01B  
**Milestone:** External Competitive Benchmark Execution  
**Governing Standard:** Section 156 of Protocol BENCH-01B, `BENCH_01_SPEC.md`  
**Date:** September 19, 2026  
**Artifacts Generated:** `F4_per_dataset_compute.png`, `F5_resource_use_over_stream.png`  

---

## 1. Algorithmic Resource Accounting Specification

All operational costs reported in BENCH-01B follow the frozen pricing model specified in `bench_01_locked_config.json`:
- **Addition / Subtraction:** 1 FLOP
- **Multiplication:** 1 FLOP
- **Multiply-Accumulate (MAC):** 2 FLOPs
- **Division / Reciprocal:** 4 FLOPs
- **Square Root:** 4 FLOPs
- **Elementary Transcendental ($\exp, \tanh, \sigma$):** 8 FLOPs
- **Persistent Online Memory:** 8 Bytes per `float64` coefficient/state, 4 Bytes per integer counter.

The benchmark established two resource ceilings defining Tier 1 micro-edge deployment:
- **R2-FLOP Ceiling:** Mean algorithmic compute $\le \mathbf{100.0\text{ FLOPs/step}}$.
- **R2-MEM Ceiling:** Persistent online state memory $\le \mathbf{1024\text{ Bytes}}$.

---

## 2. Resource Utilization Across Models

The table below reports empirical compute and memory metrics across all 15 workloads:

| Architecture | Mean FLOPs/step | Peak FLOPs/step | Mean Memory (Bytes) | Peak Memory (Bytes) | R2-FLOP Compliance | R2-MEM Compliance |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Track_B (Frozen)** | **90.44** | **206.0** | **440.0** | **600.0** | **PASS ($\le 100$)** | **PASS ($\le 1024$)** |
| B1_RZA_LMS | 179.60 | 501.0 | 213.9 | 464.0 | FAIL (+79.6%) | PASS |
| B2_CCN | 317.07 | 865.0 | 561.6 | 920.0 | FAIL (+217%) | PASS |
| B3_MUSE_RNN | 157.89 | 401.0 | 418.0 | 552.0 | FAIL (+57.9%) | PASS |
| B4_MINIMAL_GRU | 281.80 | 657.0 | 569.6 | 1320.0 | FAIL (+181.8%) | PASS |
| B5_ONLINE_ESN | 1683.67 | 3081.0 | 6112.0 | 11648.0 | FAIL (+1583%) | FAIL (+496%) |
| S1_VARIABLE_TAP_LMS | 78.97 | 120.0 | 544.0 | 544.0 | PASS | PASS |
| S2_LRU_STREAM | 140.80 | 412.0 | 387.7 | 888.0 | FAIL | PASS |
| S3_RSONN | 498.38 | 1272.5 | 792.8 | 928.0 | FAIL (+398%) | PASS |
| S4_ACESN | 3898.29 | 4800.0 | 14720.0 | 14720.0 | FAIL (+3798%) | FAIL (+1337%) |
| S5_CONTINUAL_BACKPROP | 105.13 | 305.0 | 513.6 | 1264.0 | FAIL (+5.1%) | PASS |
| C1_CURRENT_ONLY_LINEAR| 72.40 | 201.0 | 181.9 | 432.0 | PASS | PASS |
| C2_NLMS | 117.40 | 305.0 | 181.9 | 432.0 | FAIL (+17.4%) | PASS |
| C3_RLS | 2471.40 | 10405.0 | 4846.9 | 20464.0 | FAIL (+2371%) | FAIL (+373%) |
| C4_FIXED_LAG_LINEAR | 69.20 | 120.0 | 309.3 | 320.0 | PASS | PASS |

---

## 3. Dynamic Resource Elasticity (Task A8 Case Study)

Refer to `experiments/BENCH-01B/F5_resource_use_over_stream.png`:

Task A8 represents an abrupt tri-regime transition:
- **Regime 1 ($t \in [0, 3333]$):** Pure static linear relationship ($y_t = x_{0, t} - 0.8 x_{1, t}$).
- **Regime 2 ($t \in [3333, 6666]$):** Delayed dependency ($y_t = 0.8 x_{2, t-5}$).
- **Regime 3 ($t \in [6666, 10000]$):** Autoregressive infinite-impulse response recurrence ($s_t = 0.9 s_{t-1} + 0.2 x_{3, t-1}$).

### Empirical Operational Profile:
1. **Minimal GRU (Static):** Operates at a constant, inelastic **177 FLOPs/step** throughout all 10,000 steps, expending unnecessary compute during simple linear phases.
2. **CCN (Constructive Permanent):** Grows permanent hidden cascade units during transitions, stepping from 133 FLOPs to over 225 FLOPs permanently, unable to contract when demands decrease.
3. **Track B (Elastic Lifecycle):**
   - **Regime 1:** Operates as a minimal sparse linear filter ($K \le 3$, ~40–50 FLOPs). Provisional states are tested and evicted because they fail to pay rent.
   - **Regime 2:** Probes candidate lags, stabilizing around 55–65 FLOPs.
   - **Regime 3:** Detects residual autoregressive structure, triggers a birth event, confirms utility, promotes a scalar recurrent state to mature status, and scales up to 85–95 FLOPs.
   - **Mean A8 Compute:** **57.57 FLOPs/step**, exactly matching temporal demand.

---

## 4. Scaling Behavior with Ambient Dimension $D$

In workloads with high ambient input dimensions (e.g., A1 with $D=50$, H1 with $D=50$, H2 with $D=40$):
- Standard dense learners scale linearly or quadratically with $D$:
  - Dense LMS/NLMS compute scales as $O(D)$ ($501$ FLOPs on $D=50$).
  - Dense RLS scales as $O(D^2)$ ($10,405$ FLOPs on $D=50$).
  - Online ESN with input projection scales as $O(D \cdot N + N^2)$ ($3,081$ FLOPs on $D=50$).
- **Track B Sparse Bound:** By restricting active weights to $K_{\max} = 10$ and probing only $Q = 2$ candidate features per step, Track B bounds per-step forward and backward compute to $O(K_{\max} + Q) = O(1)$ with respect to ambient dimension $D$.
  - On $D=50$ (Task A1), Track B consumes only **205.3 FLOPs/step**, compared to 501 for RZA-LMS and 3,081 for ESN.

---

## 5. Summary Findings

Track B is the **only evaluated adaptive recurrent architecture** that strictly complies with both the R2-FLOP ($\le 100$) and R2-MEM ($\le 1024$) ceilings across the full benchmark suite while exhibiting dynamic runtime compute elasticity.
