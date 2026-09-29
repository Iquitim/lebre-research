# BENCH_01B_NEAREST_NEIGHBOR_ANALYSIS.md — Prior-Art Nearest Neighbor Analysis

**Protocol:** BENCH-01B  
**Milestone:** External Competitive Benchmark Execution  
**Governing Standard:** Sections 109–120 & 155 of Protocol BENCH-01B, `BENCH_01_SPEC.md`  
**Date:** September 19, 2026  
**Artifacts Generated:** `BENCH_01B_PRIOR_ART_CHALLENGERS.csv`, `F1_pareto_loss_vs_flops.png`, `F8_failure_and_completion_rates.png`  

---

## 1. Scientific Motivation

A critical requirement of rigorous benchmark methodology is to test whether the candidate architecture (Track B) provides measurable empirical value over its **closest structural neighbors** in the existing literature, rather than merely contrasting against strawmen.

Five specialized supplementary prior-art challengers were preregistered to isolate Track B's architectural mechanisms:
1. **S1 (Variable-Tap LMS — Zhao et al. 2008):** Dynamically adjusts filter tap length $L_t$ via error gradient leakage. Tests whether Track B's capacity adaptation is merely adaptive FIR filter order selection.
2. **S2 (LRU-Stream — Orvieto et al. 2023):** Diagonal linear recurrent unit with online causal gradient descent. Tests whether a static compact linear recurrent state matches Track B without dynamic lifecycle management.
3. **S3 (RSONN — Recurrent Self-Organizing Neural Network, 2017):** Online growing and pruning recurrent neural network. The closest published architectural neighbor to Track B's structural birth/eviction lifecycle.
4. **S4 (ACESN — Adaptive Compression Echo State Network, Zhang et al. 2026):** Reservoir computing with dynamically scheduled exposed state dimensions. Tests dynamic state exposure without physical allocation.
5. **S5 (Continual Backpropagation — Dohare et al., Nature 2024):** Continual weight replenishment based on unit maturity and utility. Tests whether maturity + utility replacement alone reproduces Track B.

---

## 2. Comparative Performance Matrix

The table below summarizes empirical findings across all 15 workloads and 30 seeds ($N=30$):

| Architecture | Model Paradigm | Mean NMSE | Mean FLOPs | Mean Memory (Bytes) | Completion Rate | Divergence Rate |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Track_B (Frozen)** | **Two-Timescale Lifecycle** | **0.7023** | **90.44** | **440.0** | **1.0000** | **0.0000** |
| S1_VARIABLE_TAP_LMS | Adaptive Filter Order | 0.8928 | 78.97 | 544.0 | 0.9333 | 0.0667 |
| S2_LRU_STREAM | Fixed Linear Recurrent | 0.8422 | 140.80 | 387.7 | 0.7900 | 0.2100 |
| S3_RSONN | Recurrent Growing/Pruning | 0.5991 | 498.38 | 792.8 | 1.0000 | 0.0000 |
| S4_ACESN | Adaptive Reservoir Masking | 0.8172 | 3898.29 | 14,720.0 | 1.0000 | 0.0000 |
| S5_CONTINUAL_BACKPROP| Continual Utility Replacement| 0.8235 | 105.13 | 513.6 | 0.8667 | 0.1333 |

---

## 3. Pairwise Architectural Dissections

### 3.1 Track B vs S1 (Variable-Tap LMS)
- **Mechanism Contrast:** S1 expands or contracts a contiguous delay line $x_{t-1}, \dots, x_{t-L}$ based on boundary tap magnitude. Track B maintains sparse feature selection across arbitrary non-contiguous features and can instantiate a recurrent state container.
- **Empirical Findings:**
  - On linear shift task A1, S1 performs poorly ($\text{NMSE} = 0.957$) because contiguous tap expansion cannot perform sparse feature subset selection in 50 ambient dimensions. Track B achieves $\text{NMSE} = 0.038$.
  - On real-world streams B2 (Jena Weather), S1 diverged completely across all 30 seeds ($\text{Divergence Rate} = 100\%$), while Track B was completely stable ($\text{NMSE} = 0.0248$).
  - S1 only outperformed Track B on pure tapped-delay tasks (A2, A3, B4 Silverbox), where an explicit FIR tapped-delay structure is the optimal inductive bias.
- **Conclusion:** Track B's utility-driven allocation cannot be reduced to simple adaptive tap-length filtering.

### 3.2 Track B vs S2 (LRU-Stream)
- **Mechanism Contrast:** LRU-Stream maintains a permanently active complex-decay linear recurrence without birth or eviction.
- **Empirical Findings:**
  - LRU-Stream exhibited extreme stability vulnerabilities on non-stationary and multimodal real-world streams: it diverged on 100% of Jena Weather (B2) runs and 100% of Gas Mixture (B3) runs, yielding an overall **21.0% divergence rate**.
  - On stationary tasks, LRU achieves good error (e.g., A1: $0.0186$), but its inability to shed noisy or obsolete recurrent states leads to gradient explosion when input distributions shift.
  - Track B maintained a **0.0% divergence rate** across all 450 runs.
- **Conclusion:** Dynamic state lifecycle governance is essential for numerical stability in genuinely online, unbounded streaming environments.

### 3.3 Track B vs S3 (RSONN)
- **Mechanism Contrast:** RSONN is the most capable competitor evaluated. It dynamically grows hidden recurrent units when error exceeds an activity threshold and prunes units when contribution falls below a threshold.
- **Empirical Findings:**
  - RSONN achieved the lowest raw NMSE across the benchmark ($0.5991$), outperforming Track B on tasks with complex nonlinear state manifolds (A5: $0.344$ vs $0.790$; H2: $0.988$ vs $1.086$; A8: $0.871$ vs $0.954$).
  - However, RSONN requires **5.51× more computational FLOPs** (mean $498.4$ FLOPs vs Track B's $90.4$ FLOPs), completely violating the R2-FLOP limit ($100$ FLOPs).
  - On high-dimensional real-world gas sensing (B3), Track B achieved substantially lower predictive error ($\text{NMSE} = 0.00203$ vs RSONN's $0.0467$) at **6.2× lower compute** (79.9 FLOPs vs 498.4 FLOPs).
- **Conclusion:** RSONN validates the scientific premise that growing/pruning recurrent networks are powerful online learners, while Track B establishes a strictly constrained, low-power operating point that achieves comparable stability and favorable sparse efficiency at 1/5th the compute among the evaluated methods.

### 3.4 Track B vs S4 (ACESN)
- **Mechanism Contrast:** ACESN maintains a static 40-unit reservoir and dynamically compresses/masks active readout dimensions.
- **Empirical Findings:**
  - ACESN consumes **3,898.3 FLOPs/step** and **14,720 Bytes of memory**, exceeding R2-FLOP by 39× and R2-MEM by 14×.
  - Despite this huge resource expenditure, its mean NMSE ($0.8172$) was substantially worse than Track B's ($0.7023$).
- **Conclusion:** Dynamic capacity scheduling over a pre-allocated dense reservoir is computationally wasteful compared to Track B's physical state allocation.

### 3.5 Track B vs S5 (Continual Backpropagation)
- **Mechanism Contrast:** Continual Backpropagation replaces low-utility units with newly initialized random weights upon reaching a maturity threshold.
- **Empirical Findings:**
  - S5 suffered a **13.3% divergence rate** on real-world streams (B2 Jena Weather).
  - Track B's two-timescale structural retention ($O_{\text{struct}}$) protects silent but essential state representations during event gaps, whereas S5's continuous utility decay causes premature replacement of dormant states.
- **Conclusion:** Maturity + utility replacement alone without structural retention mechanisms fails under Poisson quiescent workloads and non-stationary physical benchmarks.

---

## 4. Scientific Takeaway

The empirical comparisons against S1–S5 confirm that Track B's performance profile is not an artifact of generic adaptive filtering, unmanaged linear recurrence, or continual weight re-initialization. Track B occupies a distinct and favorable Pareto position: robust stability ($0\%$ failure), strict micro-resource adherence ($<100$ FLOPs), and competitive accuracy.
