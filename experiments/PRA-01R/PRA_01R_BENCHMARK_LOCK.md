# PRA-01R: External Benchmark Candidate Set & Protocol Lock (BENCH-01)

**Document ID:** PRA-01R-BENCHMARK  
**Author:** Benchmark Governance Auditor & Experimental Methodologist  
**Date:** September 19, 2026  
**Status:** PROTOCOL FROZEN — BENCHMARK EXECUTION UNOPENED  
**Governing Standard:** Sections 67–90 of PRA-01R Protocol  

---

## 1. Governing Benchmark Principles

Per Sections 76 and 77 of the protocol:
- **Primary Benchmark Hypothesis:**  
  *"Can the frozen Track-B organization achieve competitive predictive performance while dynamically adapting active structure, compute, and memory to current temporal demand?"*
- **Strict Prohibition Against Trivial Framing:**  
  The benchmark must **NOT** be framed as *"Does Track B achieve the lowest MSE?"* A model with 100 times more parameters and compute will often achieve lower raw MSE on stationary sequences. Track B's justification rests on its **Pareto frontier** of predictive accuracy versus adaptive resource consumption under non-stationary streaming conditions.
- **Strict Prohibition Against Execution (Section 104):**  
  This document **freezes the benchmark specification only**. No baseline or model may be trained or executed during PRA-01R.
- **Architecture Freeze Rule (Section 86):**  
  No modification to Track B's architecture or hyperparameters is permitted after benchmark results are observed.

---

## 2. Benchmark Task Suite Structure

To prevent evaluation bias and overfitting to synthetic micro-benchmarks, the evaluation is bifurcated into two balanced blocks:
- **Block A (Mechanistic Diagnostics):** Controlled synthetic streams designed to isolate specific temporal failure modes (Sections 68 & 69).
- **Block B (Public / External Real-World Streams):** Publicly available, real-world non-stationary streaming datasets that were completely unobserved during Track-B development (Sections 70–73).

```
+-----------------------------------------------------------------------------+
|                          BENCH-01 EVALUATION SUITE                          |
+--------------------------------------+--------------------------------------+
| BLOCK A: MECHANISTIC DIAGNOSTICS     | BLOCK B: PUBLIC REAL-WORLD STREAMS   |
| (Targeted Temporal Failure Isolation)| (Independent External Benchmarks)    |
+--------------------------------------+--------------------------------------+
| A1: Sparse Support Shift             | B1: NSW Electricity Pricing Stream   |
| A2: Single Delayed Dependency        | B2: NOAA Global Climatology Stream   |
| A3: Multiple Dispersed Delays        | B3: Gas Sensor Array Dynamic Drift   |
| A4: Long-Delay Scaling (d=5..50)     | B4: Silverbox Nonlinear System ID    |
| A5: SET/RESET Quiescent Memory       | B5: Friedman Concept Drift Stream    |
| A6: Context-Gated Autoregression     |                                      |
| A7: Extended Poisson Quiescence      |                                      |
| A8: Abrupt Tri-Regime Transitions    |                                      |
+--------------------------------------+--------------------------------------+
```

---

## 3. Block A: Mechanistic Diagnostic Tasks (Sections 68 & 69)

All Block A tasks are evaluated in a strictly online, prequential regime ($T = 10{,}000$ steps per seed, 10 random seeds):

1. **Task A1 (Sparse Support Shift):**  
   Input dimension $D=50$, with $K=3$ active true features. At step $t=5{,}000$, active support abruptly shifts to 3 disjoint features. Tests fast sparse feature discovery and obsolete weight eviction.
2. **Task A2 (Single Delayed Dependency):**  
   $y_t = 0.8 x_{1, t-4} + \epsilon_t$. Tests discovery of a single finite lag without triggering unnecessary recurrent state birth.
3. **Task A3 (Multiple Dispersed Delays):**  
   $y_t = 0.5 x_{1, t-2} + 0.5 x_{2, t-8} + \epsilon_t$. Tests exploration of non-contiguous temporal delay space under a bounded probe budget ($Q=2$).
4. **Task A4 (Long-Delay Scaling):**  
   $y_t = 0.8 x_{1, t-d} + \epsilon_t$ with delay $d \in \{5, 15, 30, 50\}$. Maps the empirical phase boundary where explicit delay buffer probing becomes less efficient than recurrent state allocation.
5. **Task A5 (SET/RESET Memory):**  
   Event-driven bistable memory latch. SET pulses toggle state to $+1$; RESET pulses toggle state to $-1$; long intervening periods are silent. Tests recurrent state birth and retention.
6. **Task A6 (Context Routing):**  
   A binary context feature $x_{\text{ctx}, t} \in \{0, 1\}$ dynamically selects between a linear feedforward mapping and a temporal autoregressive loop.
7. **Task A7 (Quiescent Retention):**  
   Information cues are followed by Poisson-distributed quiescent gaps ($L_{\text{gap}} \sim \text{Poisson}(\lambda=150)$) where all inputs and outputs are near zero. Tests whether structural observability prevents premature state death during silence.
8. **Task A8 (Abrupt Tri-Regime Transition):**  
   The data generating process cycles abruptly through three distinct regimes:
   - *Regime 1 ($t \in [0, 3333]$):* Sparse linear static mapping (zero temporal dependence).
   - *Regime 2 ($t \in [3334, 6666]$):* Short finite lag autoregression ($d=3$).
   - *Regime 3 ($t \in [6667, 10000]$):* Deep infinite-impulse-response recurrent regime ($s_t = 0.95 s_{t-1} + u_t$).  
   Tests full autonomous lifecycle expansion and contraction.

---

## 4. Block B: External & Public Streaming Datasets (Sections 70–73)

To guarantee external validity, five public benchmark datasets are locked. Each dataset satisfies the requirements of Section 72:

| Dataset Identifier | Primary Domain / Source | Sample Size | Target Variable | Temporal Characteristics | Non-Stationarity Profile | Recurrent Necessity | License |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| **B1: NSW Electricity** | Australian Energy Market Operator (AEMO) | 45,312 steps | 30-min Electricity Price | Autoregressive daily/weekly cycles, demand lag | Concept drift from demand spikes, weather shocks | **HIGH** (IIR price inertia) | CC BY 4.0 / Public |
| **B2: NOAA Jena Weather** | Max Planck Institute / NOAA Climatology | 70,000 steps | 10-min Temperature & Humidity | Multi-timescale continuous dynamical system | Seasonal drift, diurnal cycles, abrupt storm fronts | **HIGH** (Thermal momentum) | Open Access (CC0) |
| **B3: Gas Sensor Array** | UCI Machine Learning Repository | 13,910 steps | Continuous gas concentration | Sensor decay, chemical diffusion dynamics | Severe monotonic sensor drift over 36 months | **MEDIUM** (Diffusion tail) | CC BY 4.0 |
| **B4: Silverbox System ID** | IEEE Benchmark for Nonlinear System ID | 40,000 steps | Nonlinear electrical output | Resonant mechanical/electrical duffing oscillator | Static non-linearity + strong physical resonance | **VERY HIGH** (Second-order resonance) | Open Benchmark |
| **B5: Friedman Drift Stream** | Synthetic Concept Drift (River ML Library) | 50,000 steps | Continuous nonlinear regression | 10 input features; nonlinear interactions | Abrupt and gradual drift in feature coefficients | **LOW-MEDIUM** (Sparse interactions) | BSD 3-Clause |

### 4.1 Data Integrity & Preprocessing Protocol
- **Single-Pass Streaming:** Data points are presented sequentially $x_t \to \hat{y}_t \to y_t \to \text{Update}$.
- **Zero Leakage:** Normalization statistics (mean, variance) are computed strictly online via exponentially weighted running statistics. No future min-max scaling or batch z-scoring is permitted.
- **Missing Data:** Forward-filled online; no interpolation with future timestamps.

---

## 5. Frozen Evaluation Metrics & Pareto Analysis (Sections 74 & 75)

Per Section 75, **no single arbitrary scalar score will be computed**. All systems will be evaluated along a multidimensional Pareto frontier spanning five distinct categories:

### 5.1 Predictive Accuracy Metrics
- **Mean Squared Error (MSE):** $\text{MSE} = \frac{1}{T} \sum_{t=1}^T (y_t - \hat{y}_t)^2$
- **Mean Absolute Error (MAE):** $\text{MAE} = \frac{1}{T} \sum_{t=1}^T |y_t - \hat{y}_t|$
- **Prequential Cumulative Regret:** $R_T = \sum_{t=1}^T \left[ (y_t - \hat{y}_t)^2 - (y_t - y_t^*)^2 \right]$

### 5.2 Dynamic Adaptation Metrics
- **Post-Change Regret ($R_{\text{post}}$):** Cumulative error accumulated over the first 500 steps following an abrupt regime shift.
- **Recovery Latency ($L_{\text{rec}}$):** Number of streaming steps required for rolling error to return to within $110\%$ of steady-state error after a drift event.

### 5.3 Computational & Hardware Resource Metrics
- **Mean FLOPs / Step:** Average floating-point operations executed per time step.
- **P95 FLOPs / Step:** 95th-percentile FLOP count (measures compute spikes during probe/probation).
- **Peak FLOPs / Step:** Maximum theoretical operations on any single step.
- **Active Parameter Count ($K_{\text{active}}$):** Mean number of non-zero active weights.
- **Memory Footprint (Bytes):** Persistent weights + dynamic state buffer + probe cache.

### 5.4 Lifecycle Activity Metrics (Track B & Adaptive Baselines)
- **Birth Count ($N_{\text{birth}}$):** Total number of recurrent states instantiated.
- **Eviction Count ($N_{\text{evict}}$):** Total number of recurrent states pruned.
- **Structural Churn:** Ratio of $(N_{\text{birth}} + N_{\text{evict}}) / T$.
- **State-Free Active Time (%):** Percentage of total time steps operating purely as a sparse linear filter ($N_{\text{state}} = 0$).

### 5.5 Runtime Metrics
- **Throughput:** Processed steps per wall-clock second on standardized benchmark hardware.
- **Step Latency (P50 & P99):** Latency in microseconds per time step.

---

## 6. Two-Regime Comparison Methodology (Sections 78 & 79)

Every baseline will be evaluated under two distinct operating regimes:

### Regime R1: Naturally Configured Models
- Each baseline is configured per its canonical author recommendations and default capacities (e.g., standard ESN with $N_{\text{res}} = 20$; standard GRU with 1 hidden unit; MUSE-RNN with default split/prune thresholds).
- Demonstrates how each architecture performs in its intended "out-of-the-box" design.

### Regime R2: Resource-Matched Models
- Baselines are strictly constrained to match Track B's **mean operational resource envelope**:
  - Maximum active parameters $\le K_{\max} = 10$;
  - Maximum recurrent states $N \le 1$;
  - Operational FLOP ceiling $\le 100$ FLOPs/step.
- Tests whether Track B's dynamic lifecycle outperforms static or naive baselines when computational resources are strictly equalized.

---

## 7. Hyperparameter Calibration & Tuning Policy (Sections 80–82)

To prevent tuning bias:
- **Strict Budget:** Exactly **16 hyperparameter configurations** per baseline, evaluated over **3 calibration seeds** on a dedicated calibration segment (first 15% of the stream, discarded from final test scoring).
- **Zero Test-Set Tuning (Section 82):** Hyperparameters are locked after the calibration phase. Final reported metrics are evaluated on the remaining 85% of the stream across 10 unseen evaluation seeds.
- **Tunable Parameters per Baseline:**
  - *Learning rate / step-size:* $\eta \in [10^{-4}, 10^{-1}]$ (log-spaced);
  - *Decay / regularizer:* $\lambda \in [0.90, 0.999]$;
  - *Thresholds:* Split/prune thresholds tuned within author-recommended bounds.

---

## 8. Standardized Hardware & Accounting Protocol (Sections 83–85)

- **Benchmark Hardware:** Dedicated x86-64 CPU execution node (AMD Ryzen 9 or Intel Core i9, fixed clock frequency, single-thread pinning, zero GPU acceleration).
- **FLOP Accounting Standard:**
  - Scalar Multiply-Accumulate (MAC) = 2 FLOPs ($a \cdot b + c$).
  - Activation functions: $\tanh(x)$, $\sigma(x)$, $\exp(x)$ standardized at 8 FLOPs each.
  - Forward sensitivity trace step = 4 FLOPs ($S_t = \lambda S_{t-1} + u_{t-1}$).
- **Memory Accounting Standard:**
  - Persistent model weights: 8 bytes per float64 parameter.
  - Recurrent state buffer: 8 bytes per scalar state.
  - Probe cache & sensitivity history: exact bytes dynamically tracked.

---

## 9. Pre-Registered Decision Criteria & Success Interpretation (Sections 89 & 90)

Prior to running any benchmark experiments, the outcome interpretation is pre-registered across five mutually exclusive cases:

| Case | Empirical Benchmark Outcome | Scientific Interpretation & Verdict | Permissible Public Claim |
| :---: | :--- | :--- | :--- |
| **Case A** | Predictive error within 5% of heavy baselines (ESN, GRU), but with $\ge 50\%$ lower mean FLOPs and memory. | **Efficiency Justification:** Dynamic lifecycle successfully matches heavy models at a fraction of continuous resource cost. | *"Empirical resource efficiency under evaluated non-stationary regimes."* |
| **Case B** | Statistically lower cumulative regret ($p < 0.01$) following regime shifts compared to static models at matched resources (Regime R2). | **Continual Adaptation Justification:** Autonomous structural birth and eviction accelerates adaptation to concept drift. | *"Superior adaptation latency under resource-constrained regime shifts."* |
| **Case C** | Lower resource usage, but predictive error is materially worse ($>25\%$ higher MSE) across all public tasks. | **Tradeoff Only:** The lifecycle mechanism trades off accuracy for compute, but does not provide an advantageous Pareto frontier. | *"Resource-constrained operational tradeoff; predictive fidelity degraded."* |
| **Case D** | Static baselines (RZA-LMS, Minimal GRU) or CCN match or beat Track B in both prediction error AND resource usage. | **Hypothesis Falsified:** Track B's complex lifecycle is **not empirically justified**. Engineering overhead provides no tangible benefit. | *"Architectural lifecycle not justified over standard static or constructive baselines."* |
| **Case E** | Mixed results; Track B dominates on synthetic tasks (Block A) but is dominated on public datasets (Block B). | **Domain-Specific Specialization:** Track B's heuristics overfit synthetic event structures and lack general real-world advantage. | *"Pareto trade-off restricted to event-driven synthetic regimes; no general superiority."* |

> [!IMPORTANT]
> **GOVERNANCE PROHIBITION (Section 90):**  
> Under no circumstances may Track B be described as a "superior architecture" or "state-of-the-art framework." Even under Case A or Case B, conclusions must be restricted to *"empirical advantage under evaluated streaming regimes."*

---

## 10. Summary of Benchmark Lock

Milestone **BENCH-01** is now fully governed:
- 5 Mandatory + 2 Recommended Baselines locked;
- 8 Mechanistic + 5 Public Real-World Tasks locked;
- 16 Pareto metrics locked;
- 16-configuration tuning policy locked;
- Cases A–E pre-registered.

Benchmark execution is deferred until formal authorization.
