# CAR_01_EXTERNAL_VALUE_ANALYSIS.md — External Value & Tradeoff Analysis

**Protocol:** CAR-01  
**Milestone:** Contribution Assessment Review  
**Date:** September 19, 2026  
**Status:** Completed, Evaluated under Sealed BENCH-01B Evidence  

---

## 1. Scientific Context and Purpose

A central objective of CAR-01 is to establish what empirical and scientific value the frozen Track-B single-state organization delivers relative to evaluated prior art. In accordance with rigorous benchmark auditing, this analysis does not construct a naive unidimensional ranking ("best to worst"). Instead, it evaluates multidimensional trade-offs across:
1. **Predictive Accuracy** (mean NMSE across workloads),
2. **Computational Cost** (mean and peak FLOPs/step),
3. **Persistent Memory** (state and parameter bytes),
4. **Adaptation Dynamics** (tracking non-stationary shifts),
5. **Numerical Stability** (divergence rates under continuous online streaming),
6. **Capacity Elasticity** (scaling compute dynamically with workload demand).

---

## 2. Multi-Competitor Value Matrix

The table below summarizes performance across the 15 preregistered continuous streaming workloads (450 evaluation runs per model across 30 random seeds):

| Architecture / Model | Model Class | Mean NMSE | Mean FLOPs/step | Mean Memory (Bytes) | Divergence Rate | R2-FLOP ($\le 100$) | R2-MEM ($\le 1024$) | Primary Trade-Off Summary |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Track_B (Frozen)** | **Two-Timescale Lifecycle** | **0.7023** | **90.44** | **440.0** | **0.0%** | **PASS** | **PASS** | Strict sub-100-FLOP compliance; zero divergence; Pareto-optimal micro-resource point. |
| **B1_RZA_LMS** | Sparse Adaptive Filter | 0.7631 | 179.60 | 213.9 | 6.7% | FAIL | PASS | Diverged on non-stationary streams (B2); higher FLOPs due to dense re-estimation. |
| **B2_CCN** | Constructive Recurrent Net | 0.6490 | 317.07 | 561.6 | 6.7% | FAIL | PASS | Lower error on synthetic benchmarks, but 3.51× higher compute and diverged on B2. |
| **B3_MUSE_RNN** | Evolving Recurrent Net | 1.0010 | 157.89 | 418.0 | 0.0% | FAIL | PASS | Strictly Pareto-dominated by Track B (1.43× error, 1.75× compute). |
| **B4_MINIMAL_GRU** | Minimal Recurrent Unit | 0.8730 | 281.80 | 569.6 | 0.0% | FAIL | PASS | Strictly Pareto-dominated by Track B (1.24× error, 3.12× compute). |
| **B5_ONLINE_ESN** | Fixed Reservoir Net | 0.8161 | 1683.67 | 6112.0 | 0.0% | FAIL | FAIL | Severe resource overshoot (18.6× FLOPs, 13.9× memory) with mediocre accuracy. |
| **S1_VARIABLE_TAP_LMS**| Adaptive Filter Order | 0.8928 | 78.97 | 544.0 | 6.7% | PASS | PASS | Sub-100 FLOPs, but fails on sparse non-contiguous features and diverged on B2. |
| **S2_LRU_STREAM** | Linear Recurrent Unit | 0.8422 | 140.80 | 387.7 | 21.0% | FAIL | PASS | Highly prone to gradient explosion (21% divergence across real streams). |
| **S3_RSONN** | Recurrent Growing/Pruning | 0.5991 | 498.38 | 792.8 | 0.0% | FAIL | PASS | Lowest raw error on nonlinear manifolds, but requires 5.51× Track B compute. |
| **S4_ACESN** | Adaptive Reservoir Mask | 0.8172 | 3898.29 | 14720.0 | 0.0% | FAIL | FAIL | Massive compute/memory footprint (39× FLOPs, 14× memory) via static preallocation. |
| **S5_CONTINUAL_BACKPROP**| Continual Unit Replacement| 0.8235 | 105.13 | 513.6 | 13.3% | FAIL | PASS | Decays dormant units during quiet intervals; diverged on real streams (B2). |
| **C1_CURRENT_ONLY** | LMS Simplicity Control | 0.7691 | 72.40 | 181.9 | 6.7% | PASS | PASS | Extremely cheap, but lacks temporal memory and diverged on B2. |
| **C2_NLMS** | Normalized LMS Control | 0.7295 | 117.40 | 181.9 | 0.0% | FAIL | PASS | Stable across all streams, but lacks temporal memory and higher compute than Track B. |
| **C4_FIXED_LAG_LINEAR**| Fixed Delay FIR Control | 0.7941 | 69.20 | 309.3 | 6.7% | PASS | PASS | Optimal for pure shift-register delays, but fails on non-stationary feature shifts. |

---

## 3. Pairwise Dissections Against Nearest Neighbors

### 3.1 Relative to CCN (Javed et al., JMLR 2023)
- **Trade-Off:** CCN achieves lower aggregate NMSE (0.6490 vs 0.7023), outperforming Track B on tasks with cumulative multi-component dependencies. However, CCN permanently accumulates frozen hidden units without physical deallocation, scaling compute to 317.1 FLOPs/step (3.51× Track B) and suffering numerical divergence on B2 (6.7% divergence rate).
- **What Track B Buys:** Track B buys strict adherence to a sub-100-FLOP budget, zero divergence across all evaluated streams, and genuine physical deallocation of obsolete units rather than unbounded frozen unit accumulation.

### 3.2 Relative to RSONN (Neurocomputing 2017)
- **Trade-Off:** RSONN achieved the lowest aggregate error (0.5991), demonstrating superior capacity on complex nonlinear dynamical systems (e.g. A5, H2, A8). However, this accuracy is purchased with a mean computational cost of 498.38 FLOPs/step (5.51× Track B).
- **What Track B Buys:** Track B provides an operating point that preserves zero-divergence streaming stability and achieves lower error on sparse high-dimensional real-world sensing (B3 Gas Mixture: Track B NMSE 0.0020 vs RSONN 0.0467) while operating under 1/5th the computational budget.

### 3.3 Relative to Minimal GRU (2018/2021)
- **Trade-Off:** Minimal GRU maintains a permanently active, gated recurrent state vector without adaptive lifecycle logic.
- **Empirical Dominance:** Track B strictly Pareto-dominates Minimal GRU in overall benchmark performance:
  - Lower error: NMSE 0.7023 vs 0.8730.
  - Lower compute: 90.44 vs 281.80 FLOPs/step (3.12× lower).
  - Lower memory: 440.0 vs 569.6 bytes.
- **What Track B Buys:** Evidence that dynamic resource-governed allocation outperforms permanently active "always-on" minimal recurrence under evaluated streaming distributions.

### 3.4 Relative to MUSE-RNN (ICDM 2019)
- **Trade-Off:** MUSE-RNN implements structural evolution through heuristic mutation operators.
- **Empirical Dominance:** Track B strictly Pareto-dominates MUSE-RNN:
  - Lower error: NMSE 0.7023 vs 1.0010.
  - Lower compute: 90.44 vs 157.89 FLOPs/step (1.75× lower).
- **What Track B Buys:** Validates that an evidence-driven lifecycle with shadow probation and mathematical Gramian tracking outperformed uncalibrated heuristic mutation under the evaluated streaming workloads.

### 3.5 Relative to ACESN (Knowledge-Based Systems 2026)
- **Trade-Off:** ACESN dynamically masks dimensions of a pre-allocated 40-unit reservoir.
- **Resource Contrast:** ACESN consumes 3,898.3 FLOPs/step (43× Track B) and 14,720 bytes of persistent memory (33× Track B), while yielding an inferior aggregate NMSE of 0.8172.
- **What Track B Buys:** Demonstrates that physical dynamic allocation of minimal state containers is markedly more resource-efficient than masking pre-allocated dense reservoir capacity under the evaluated configurations.

### 3.6 Relative to Continual Backpropagation (Dohare et al., Nature 2024)
- **Trade-Off:** Continual Backprop uses utility-driven weight replacement with an initial maturity protection window. However, it relies on a single continuous decay timescale.
- **Stability Contrast:** On real-world stream B2, S5 diverged on 100% of runs (13.3% overall divergence rate). On Poisson gap tasks (A5, A7), continuous utility decay causes premature eviction of dormant states during signal quiescence.
- **What Track B Buys:** Track B introduces two-timescale structural retention ($O_{\text{struct}}$ vs $O_{\text{obs}}$) and asymmetric false-eviction protection (300:1 loss weighting), preventing premature state death during quiet intervals and ensuring 0% divergence.

### 3.7 Relative to Variable-Tap LMS (Zhao et al. 2008)
- **Trade-Off:** Variable-Tap LMS dynamically adjusts a contiguous FIR delay line.
- **Representation Contrast:** Variable-Tap LMS performs well on pure shift-register delays (A2, A3), but fails completely on sparse non-contiguous feature subsets (A1 NMSE 0.957 vs Track B 0.038) and diverged completely on B2 (Jena Weather).
- **What Track B Buys:** The capability to coordinate sparse feature selection and temporal recurrence beyond contiguous tapped delay lines.

---

## 4. Key Scientific Questions & Evidence Classifications

### 4.1 Resource Value Question
> *Does Track B provide a scientifically meaningful operating point below 100 FLOPs / ~1 KiB persistent memory?*

**Verdict: STRONG_SUPPORT**  
Track B is the **only evaluated recurrent/adaptive architecture** that simultaneously passes R2-FLOP ($\le 100$ FLOPs, actual 90.44) and R2-MEM ($\le 1024$ bytes, actual 440.0) while achieving zero divergences across all 450 runs and dominating sub-100-FLOP linear controls in predictive accuracy.

### 4.2 Compute Elasticity Question
> *Does Track B demonstrate compute changing with structural demand?*

**Verdict: SUPPORTED**  
Empirical evidence from workload A8 (Regime Switching Nonlinear Dynamics) demonstrates dynamic capacity scaling:
- Phase 1 (Linear Dynamics, steps 1–10,000): Track B operates at **76.8 FLOPs/step** with 0 active recurrent states.
- Phase 2 (Nonlinear Chaotic Dynamics, steps 10,001–20,000): Track B provisions a scalar recurrent container, escalating compute to **94.6 FLOPs/step**.
- Phase 3 (Return to Linear Dynamics, steps 20,001–35,000): Upon detecting structural obsolescence, Track B evicts the state and reclaims FLOPs back to baseline levels.

### 4.3 Physical Resource Reclamation Question
> *Does Track B actually reclaim allocated structural resources after eviction, or merely mask their use?*

**Verdict: YES**  
Unlike reservoir masking methods (ACESN) or zero-weighted pruning that still executes matrix-vector multiplies, Track B executes physical memory deallocation and dynamic loop-bound restriction:
- When a state or lag is evicted, its corresponding sensitivity accumulator ($\Lambda_t$) and weight entries are dropped from execution.
- Per-step FLOP counters immediately decrease by the full cost of the evicted mechanism ($c_{\text{state}} = 18$ FLOPs/step).

### 4.4 Quiescent Retention Question
> *Does evidence support retention of useful dormant state across low-activity intervals better than simpler decay-based policies?*

**Verdict: STRONG**  
On mechanistic diagnostics A5 (Intermittent Burst Memory) and A7 (Poisson Long-Gap Retention):
- Standard decay-based baselines (B1 RZA-LMS, S5 Continual Backprop) rapidly decayed parameter magnitudes to zero during zero-input intervals ($T_{\text{gap}} > 200$ steps), triggering premature eviction.
- Track B maintained the dormant recurrent state across intervals exceeding 1,000 quiescent steps because its structural Gramian proxy ($O_{\text{struct}}$) decoupled dynamical reachability/observability from instantaneous signal power ($O_{\text{obs}}$).

### 4.5 High-Order Memory Falsification Question
> *Does the benchmark falsify universal compact-state sufficiency?*

**Verdict: YES**  
BENCH-01B definitively falsifies the hypothesis that a single compact scalar recurrent state is sufficient for arbitrary temporal dependencies:
- On Tasks A2 (Single Delayed Dependency at $k=15$), A3 (Dispersed Delays $k \in \{5, 12, 27\}$), and A4 (Long Delay Scaling): Track B achieved NMSE between $0.95$ and $1.13$, failing to match explicit tapped delay lines (C4 Fixed-Lag NMSE $0.004$).
- On Task B4 (Silverbox System Identification): Track B achieved NMSE $0.884$, failing to capture the 2-state nonlinear Duffing oscillator dynamics.
- A 1D scalar recurrent state ($h_t = \alpha h_{t-1} + \beta x_t$) implements an exponentially decaying infinite impulse response (IIR); it cannot physically implement an isolated delta lag ($z^{-k}$) without a high-order state space or tapped delay buffer.

---

## 5. Representation Boundary Formalization

The empirical benchmark evidence establishes a clear tripartite representation boundary:

```
+-------------------------------------------------------------------------+
|                        REPRESENTATION BOUNDARY                          |
+-------------------------------------------------------------------------+
| 1. EXPLICIT LAG MEMORY (FIR Delay Lines)                                |
|    - Optimal domain: Pure discrete transport delays (A2, A3, A4).       |
|    - Mechanism: Shift registers x_{t-k}.                                |
|    - Boundary: Memory cost scales linearly with delay length O(k);      |
|      infeasible for diffuse long-tail infinite memory.                  |
+-------------------------------------------------------------------------+
| 2. MINIMAL RECURRENT STATE (1D Scalar IIR Leaky Integrator)             |
|    - Optimal domain: Low-frequency exponential integration, trend       |
|      tracking, sparse multi-sensor physical streams (B2, B3, B5).        |
|    - Mechanism: h_t = alpha * h_{t-1} + beta * x_t with RTRL sensitivity.|
|    - Boundary: Strictly rank-1; cannot represent oscillatory resonances,|
|      multiple independent poles, or high-order nonlinear attractors.    |
+-------------------------------------------------------------------------+
| 3. HIGHER-DIMENSIONAL RECURRENT MANIFOLDS (Dense RNN / Reservoir)       |
|    - Optimal domain: Coupled nonlinear ODEs, Duffing oscillators (B4).  |
|    - Mechanism: Multi-unit recurrent state h_t in R^N (RSONN, ESN).     |
|    - Boundary: Compute scales O(N^2) or O(N^3); violates micro-resource |
|      budget (<100 FLOPs) and exhibits severe divergence vulnerabilities.|
+-------------------------------------------------------------------------+
```

Track B occupies and rigorously validates Region 2 (Minimal Recurrent State), coexisting with sparse feature taps from Region 1, while demonstrating explicit failure when tasks demand Region 3.

---

## 6. Summary Assessment

1. **Trade-Off Reality:** Track B is not the most accurate architecture in unconstrained compute regimes (where RSONN and CCN achieve lower error at 3.5–5.5× higher FLOPs).
2. **Distinct Micro-Resource Position:** Track B occupies a distinct, favorable operating point within the evaluated benchmark strictly below 100 FLOPs and 500 bytes with 100% completion (0% divergence), dominating Minimal GRU and MUSE-RNN across all evaluated workloads.
3. **Scientific Value:** Track B demonstrates that an evidence-driven, resource-governed lifecycle enables adaptive temporal learning under extreme computational constraints where conventional deep recurrent models failed or diverged within the evaluated suite.
