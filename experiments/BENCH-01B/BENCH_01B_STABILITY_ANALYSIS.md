# BENCH_01B_STABILITY_ANALYSIS.md — Empirical Stability & Neutral Failure Reporting

**Protocol:** BENCH-01B  
**Milestone:** External Competitive Benchmark Execution  
**Governing Standard:** Section 157 of Protocol BENCH-01B, `BENCH_01_SPEC.md`  
**Date:** September 19, 2026  
**Artifacts Generated:** `BENCH_01B_FAILURE_MANIFEST.csv`, `F8_failure_and_completion_rates.png`  

---

## 1. Preregistered Neutral Failure Policy

Following the methodology audit of Protocol BENCH-01A-R, arbitrary synthetic penalty multipliers (e.g., $1.5\times$ divergence penalties) were excised from the evaluation framework. In their place, a neutral, deterministic failure-reporting standard was frozen:
1. **Divergence Criteria:** A run is designated as `NUMERICAL_DIVERGENCE` if prediction output $\hat{y}_t$ or loss $e_t^2$ produces `NaN`, `inf`, or exceeds numerical stability boundaries ($|\hat{y}_t| > 10^8$ or $e_t^2 > 10^{16}$).
2. **Deterministic Tracking:** Every diverged run is logged in `BENCH_01B_FAILURE_MANIFEST.csv` with the exact failure step $t_{\text{fail}}$, fraction completed $t_{\text{fail}} / T$, model configuration, and seed.
3. **Prequential Metric Isolation:** Predictive metrics (MSE, MAE, NMSE) are aggregated **strictly over valid, complete runs** (`VALID_COMPLETE_RUNS_ONLY`), preventing numerical pollution.
4. **Independent Robustness Metrics:** Algorithmic robustness is independently quantified via `completion_rate` and `divergence_rate` ($1.0 - \text{completion\_rate}$).

---

## 2. Failure Manifest Breakdown

Across the 6,750 total evaluation runs in Phase E4, a total of **319 runs diverged** ($4.73\%$ overall benchmark failure rate). All 319 incidents were classified as `NUMERICAL_DIVERGENCE`; zero runtime crashes or unhandled execution exceptions occurred.

### 2.1 Failures by Architecture

| Architecture | Model Category | Total Runs | Successful Runs | Diverged Runs | Completion Rate | Divergence Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Track_B (Frozen)** | **Primary Target** | **450** | **450** | **0** | **100.0%** | **0.00%** |
| B1_RZA_LMS | Primary Baseline | 450 | 420 | 30 | 93.33% | 6.67% |
| B2_CCN | Primary Baseline | 450 | 420 | 30 | 93.33% | 6.67% |
| B3_MUSE_RNN | Primary Baseline | 450 | 450 | 0 | 100.0% | 0.00% |
| B4_MINIMAL_GRU | Primary Baseline | 450 | 450 | 0 | 100.0% | 0.00% |
| B5_ONLINE_ESN | Primary Baseline | 450 | 450 | 0 | 100.0% | 0.00% |
| S1_VARIABLE_TAP_LMS | Supplementary | 450 | 420 | 30 | 93.33% | 6.67% |
| S2_LRU_STREAM | Supplementary | 450 | 341 | 109 | 79.00% | 21.00% |
| S3_RSONN | Supplementary | 450 | 450 | 0 | 100.0% | 0.00% |
| S4_ACESN | Supplementary | 450 | 450 | 0 | 100.0% | 0.00% |
| S5_CONTINUAL_BACKPROP| Supplementary | 450 | 390 | 60 | 86.67% | 13.33% |
| C1_CURRENT_ONLY_LINEAR| Simplicity Control | 450 | 420 | 30 | 93.33% | 6.67% |
| C2_NLMS | Simplicity Control | 450 | 450 | 0 | 100.0% | 0.00% |
| C3_RLS | Simplicity Control | 450 | 450 | 0 | 100.0% | 0.00% |
| C4_FIXED_LAG_LINEAR | Simplicity Control | 450 | 420 | 30 | 93.33% | 6.67% |

### 2.2 Failures by Workload

| Task ID | Workload Description | Total Runs | Total Failures | Models Failing on Task |
| :--- | :--- | :---: | :---: | :--- |
| **B2** | Jena Weather (Real-World) | 450 | **210** | B1, B2, S1, S2, S5, C1, C4 (30/30 seeds each) |
| **B3** | Gas Dynamic Mixture (Real-World) | 450 | **60** | S2 (30/30 seeds), S5 (30/30 seeds) |
| **B5** | Household Power (Real-World) | 450 | **30** | S2 (30/30 seeds) |
| **H1** | Damped Resonator (Holdout) | 450 | **16** | S2 (16/30 seeds) |
| **B1** | NSW Electricity (Real-World) | 450 | **3** | S2 (3/30 seeds) |
| A1–A8, H2, B4| Remaining 10 Workloads | 4,500 | **0** | None (100% stable across all models) |

---

## 3. Analysis of Failure Modes & Triggers

### 3.1 Unnormalized SGD Divergence on Task B2 (Jena Weather)
- **Root Cause:** Task B2 is a 70,000-step continuous meteorological time series containing long-term seasonal trends and sudden weather front shifts.
- Fixed-step unnormalized gradient descent algorithms without bounded activations (B1_RZA_LMS, C1, C4, S1) experienced gradient explosion when tracking temperature extremes during winter transitions.
- Cascade Correlation Network (B2_CCN) also diverged on B2: its permanent nonlinear hidden columns accumulated unbounded activations over 70,000 steps, destabilizing the output layer.
- **Track B Behavior:** Track B's combination of strictly causal standard scaling (`CausalStandardScaler`) and bounded linear/gated state transitions with rent-based eviction maintained flawless numerical stability across all 30 seeds ($\text{NMSE} = 0.0248$).

### 3.2 LRU-Stream (S2) Unbounded State Accumulation
- S2_LRU_STREAM had the highest divergence rate of all evaluated models (**21.0% divergence**, 109 failed runs).
- While diagonal complex-decay recurrent linear units are effective in offline batch settings, online streaming adaptation without state reset or eviction causes the diagonal state $h_t$ to grow uncontrollably when input variances change. S2 diverged across B2, B3, B5, H1, and B1.

### 3.3 Continual Backpropagation (S5) Random Replacement Shock
- S5 diverged on 60 runs (13.33% failure rate on B2 and B3).
- In S5, units that drop below utility thresholds are abruptly replaced with newly randomized weights. On non-stationary continuous streams, introducing untrained random weights into the active computation graph induces severe transient gradient spikes that frequently trigger numerical divergence.
- Track B avoids this through its **provisional probation window**: candidate states are updated in the background without driving the main prediction output until their utility is proven.

---

## 4. Analysis of Figure F8: Completion Rates

Refer to `experiments/BENCH-01B/F8_failure_and_completion_rates.png`:
- Track B (highlighted in crimson) achieves an exact **1.000 (100%) completion rate**.
- Robustness is matched by deep fixed models (Minimal GRU, Online ESN, MUSE-RNN) and normalized simplicity controls (NLMS), but Track B achieves this robustness while actively creating and destroying recurrent state representations online.
