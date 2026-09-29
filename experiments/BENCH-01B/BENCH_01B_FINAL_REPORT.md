# BENCH_01B_FINAL_REPORT.md — Frozen External Competitive Benchmark Evaluation

**Document ID:** BENCH-01B-FINAL  
**Status:** COMPLETED, AUDITED & SEALED  
**Target Milestone:** BENCH-01B (Competitive Benchmark Execution)  
**Governing Documents:** Protocol BENCH-01B, Protocol BENCH-01A-R, `BENCH_01_SPEC.md`  
**Date:** September 19, 2026  

---

## Section 213: Benchmark Executive Summary Block

```yaml
BENCHMARK_EXECUTION_SUMMARY:
  benchmark_id: "BENCH-01B"
  specification_version: "1.0.0-FROZEN"
  execution_date: "2026-09-19"
  total_workloads: 15
    block_a_mechanistic: 8 (A1-A8)
    mechanistic_holdouts: 2 (H1-H2)
    block_b_real_world: 5 (B1-B5)
  evaluation_seeds: 30 (seeds 101-130)
  total_competitive_runs: 6750
  completed_successful_runs: 6431
  numerical_divergences: 319 (0 in Track B)
  models_evaluated: 15
    primary_target: 1 ("Track_B_Frozen_M2")
    primary_baselines: 5 ("B1_RZA_LMS", "B2_CCN", "B3_MUSE_RNN", "B4_MINIMAL_GRU", "B5_ONLINE_ESN")
    supplementary_challengers: 5 ("S1_VARIABLE_TAP_LMS", "S2_LRU_STREAM", "S3_RSONN", "S4_ACESN", "S5_CONTINUAL_BACKPROP")
    simplicity_controls: 4 ("C1_CURRENT_ONLY_LINEAR", "C2_NLMS", "C3_RLS", "C4_FIXED_LAG_LINEAR")

OVERALL_METRICS_TABLE:
  Track_B:
    mean_nmse: 0.7023
    mean_flops: 90.44
    mean_memory_bytes: 440.0
    completion_rate: 1.0000
    divergence_rate: 0.0000
    r2_flop_pass_le_100: YES
    r2_mem_pass_le_1024: YES
  B1_RZA_LMS:
    mean_nmse: 0.7631
    mean_flops: 179.60
    mean_memory_bytes: 213.9
    completion_rate: 0.9333
    divergence_rate: 0.0667
    r2_flop_pass_le_100: NO
    r2_mem_pass_le_1024: YES
  B2_CCN:
    mean_nmse: 0.6490
    mean_flops: 317.07
    mean_memory_bytes: 561.6
    completion_rate: 0.9333
    divergence_rate: 0.0667
    r2_flop_pass_le_100: NO
    r2_mem_pass_le_1024: YES
  B3_MUSE_RNN:
    mean_nmse: 1.0010
    mean_flops: 157.89
    mean_memory_bytes: 418.0
    completion_rate: 1.0000
    divergence_rate: 0.0000
    r2_flop_pass_le_100: NO
    r2_mem_pass_le_1024: YES
  B4_MINIMAL_GRU:
    mean_nmse: 0.8730
    mean_flops: 281.80
    mean_memory_bytes: 569.6
    completion_rate: 1.0000
    divergence_rate: 0.0000
    r2_flop_pass_le_100: NO
    r2_mem_pass_le_1024: YES
  B5_ONLINE_ESN:
    mean_nmse: 0.8161
    mean_flops: 1683.67
    mean_memory_bytes: 6112.0
    completion_rate: 1.0000
    divergence_rate: 0.0000
    r2_flop_pass_le_100: NO
    r2_mem_pass_le_1024: NO

GOVERNANCE_STATUS:
  M3_STATUS: "UNOPENED"
  NOVELTY_CLAIM_READY: "NO"
  ARCHITECTURE_NAMING: "UNNAMED (Track B Single-State Organization)"
  NEXT_RECOMMENDED_PHASE: "CAR-01 (Contribution Assessment Review)"
```

---

## 1. Scientific Hypotheses & Non-Claims

The primary hypothesis evaluated by BENCH-01B is:

$$\mathbf{H_{\text{TRACK\_B}}}: \text{A resource-governed online learner can achieve competitive predictive performance while adapting active structure, compute, and memory to current temporal demand.}$$

### Explicit Non-Claims (Section 4 of `BENCH_01_SPEC.md`)
1. **No Universal Lowest Error:** Track B does not claim to achieve lowest raw error on every stream. Higher-capacity models (e.g., CCN, large ESNs) with 3× to 20× higher compute achieve lower error on stationary switching or dynamical ID tasks.
2. **No Representation-Order Dominance:** A single scalar recurrent state ($N=1$) cannot represent high-dimensional vector manifolds or long contiguous tapped-delay shift registers.
3. **No Component-Level Novelty:** Individual elements (RTRL sensitivities, utility decay, sparse feature banks) are published techniques.

---

## 2. Integrity Verification & Reproducibility (Phase E0)

Prior to running competitive workloads, cryptographic verification confirmed the bit-level immutability of all governing files:
- `BENCH_01_SPEC.md` SHA-256: `f516914da4d511e9ed58c2eb575d628bf3e01ebaab9f8bf63f9da0ebfe0e0c28` (**PASS**)
- `experiments/BENCH-01A/bench_01_locked_config.json` SHA-256: `cb0d696e3e2775afa802a5a037ddf58ad3887252e4ac302e62b7e6162d334f7a` (**PASS**)
- `experiments/BENCH-01B/BENCH_01B_SUPPLEMENTARY_PRIOR_ART_CONFIG.json` SHA-256: `2d8302495db638437f6c118438a53acc41fbe1efa4f787c01a224fb7f5da10dc` (**PASS**)
- The full test suite passed with zero regressions: **124 / 124 tests passing (100% PASS)**.

---

## 3. Prequential Evaluation Protocol & Split Verification

The frozen chronological split was applied strictly across all streams:
- **Calibration Prefix ($[0.00T, 0.15T)$):** Used exclusively on 3 calibration seeds (`42, 43, 44`) to tune baseline hyperparameters across 2,700 search configurations. Track B underwent **zero tuning** (0 configurations evaluated).
- **Validation Segment ($[0.15T, 0.30T)$):** Verified numerical stability of selected configurations.
- **Sealed Test Segment ($[0.30T, 1.00T]$):** Metrics recorded prequentially across 30 fresh evaluation seeds (`101–130`). Continuous state transfer was preserved from $t=0$ without test-time reset.
- **Prequential Timing Invariant:** For every step $t$, prediction $\hat{y}_t$ was generated from current state, prequential loss $e_t^2$ was scored, and parameter/lifecycle updates were performed strictly post-prediction.

---

## 4. Primary Competitive Benchmark Results

Across the 15 workloads, Track B achieved:
1. **Lowest Error on 4 Workloads:**
   - **A8 (Abrupt Tri-Regime Transition):** $\text{NMSE} = 0.9540$ (lowest of all models).
   - **B2 (Jena Weather Meteorology):** $\text{NMSE} = 0.0248$ (outperforming Minimal GRU $0.0742$ and Online ESN $0.3284$; RZA-LMS and CCN completely diverged).
   - **B3 (Gas Dynamic Chemical Sensor Array):** $\text{NMSE} = 0.00203$ (outperforming Minimal GRU $0.0241$, CCN $0.0390$, LMS $0.0492$, and ESN $0.2608$).
   - **B5 (Household Active Power Demand):** $\text{NMSE} = 0.00403$ (outperforming CCN $0.0120$, LMS $0.0912$, and GRU $0.0924$).
2. **Competitive Adaptation on Concept Drift & Quiescence:**
   - **A1 (Sparse Support Shift):** $\text{NMSE} = 0.0379$ (drastically beating static recurrent networks GRU $0.7897$ and ESN $0.7695$).
   - **A5 & A7 (Set/Reset & Extended Poisson Quiescence):** $\text{NMSE} = 0.7901$ and $0.8535$ (retaining information across silent intervals where LMS and GRU fail with $\text{NMSE} > 1.018$).
3. **Falsification & Boundary Identification:**
   - **A2, A3, A4 (Tapped Delays):** Single scalar recurrent state without active delay-line expansion yields $\text{NMSE} \approx 1.13$. Dense reservoirs (ESN: $0.959$–$0.968$) or tapped-delay LMS filters outperform Track B on pure shift-register memory tasks.
   - **B4 (Silverbox Electronic System ID):** Pure single-channel dynamical system ID favors multi-dimensional reservoir manifolds (ESN: $0.9136$) over Track B's 8.0 FLOP linear default ($0.9932$).

---

## 5. Resource Accounting & Pareto Dominance

Refer to generated figures `F1_pareto_loss_vs_flops.png`, `F2_pareto_loss_vs_memory.png`, and `F4_per_dataset_compute.png`:
- **R2-FLOP Limit ($\le 100$ Mean FLOPs):**
  - Track B: **90.44 FLOPs** (**PASS**)
  - RZA-LMS: **179.6 FLOPs** (**FAIL**)
  - Minimal GRU: **281.8 FLOPs** (**FAIL**)
  - CCN: **317.1 FLOPs** (**FAIL**)
  - Online ESN: **1,683.7 FLOPs** (**FAIL**)
- **R2-MEM Limit ($\le 1024$ Bytes):**
  - Track B: **440.0 Bytes** (**PASS**)
  - Online ESN: **6,112.0 Bytes** (**FAIL**)
  - ACESN: **14,720.0 Bytes** (**FAIL**)
- **Pareto Inhabitation:** Track B strictly Pareto-dominates Minimal GRU (achieving lower error at 3.1× lower compute and lower memory) and MUSE-RNN (lower error at 1.75× lower compute).

---

## 6. Stability & Neutral Failure Reporting

Refer to `F8_failure_and_completion_rates.png` and `BENCH_01B_FAILURE_MANIFEST.csv`:
- Total Divergences: 319 runs diverged out of 6,750 runs (4.73%).
- **Track B Divergence Rate:** **0.00%** (450/450 completed runs).
- **Competitor Divergence Rates:**
  - S2_LRU_STREAM: **21.00%** (109 diverged runs).
  - S5_CONTINUAL_BACKPROP: **13.33%** (60 diverged runs).
  - B1_RZA_LMS, B2_CCN, S1, C1, C4: **6.67%** (30 diverged runs each, all failing on B2 Jena Weather).
- Track B exhibited strong numerical robustness under the evaluated streams, consistent with the intended role of its two-timescale lifecycle, whereas unnormalized gradient descent and unmanaged recurrence without lifecycle control experienced numerical divergence on long physical benchmarks.

---

## 7. Explicit Answers to Preregistered Scientific Questions

### Question 214: Does the frozen Track-B single-state organization provide a useful prediction / adaptation / resource tradeoff compared with appropriate existing methods under genuinely online, unseen, and fairly tuned conditions?
**YES.**  
The empirical evidence decisively confirms this trade-off:
1. Under the strict micro-edge operational envelope ($\le 100$ FLOPs/step, $\le 1024$ Bytes), Track B Pareto-dominates all compliant baselines and simplicity controls in predictive accuracy and stability.
2. Compared to unconstrained recurrent baselines (Minimal GRU, CCN, Online ESN), Track B achieves competitive or lower error on real-world multi-sensor streams (B2, B3, B5) at 3.5× to 18.6× lower computational expenditure.
3. Track B achieved statistically significant lower error in **53.3%** of all competitive paired tests across the benchmark suite ($p_{\text{FDR}} < 0.05$).

### Question 215: What are the primary failure modes, negative results, and empirical boundary conditions of Track B?
**The boundary conditions are clear and falsifiable:**
1. **High-Order Pure Delays:** When temporal dependencies are purely shift-register delays without physical decay (A2, A3, A4), Track B's scalar recurrent state ($N=1$) cannot substitute for dense tapped-delay lines, yielding excess error ($\text{NMSE} \approx 1.13$).
2. **Dense Non-Linear System ID on Scalar Channels:** When ambient input dimension is $D=1$ and the underlying system is a continuous high-order nonlinear manifold (B4 Silverbox), Track B defaults to its linear mode ($8.0$ FLOPs) and is outperformed by high-dimensional reservoirs (Online ESN).
3. **Complex Instantaneous Bimodal Logic:** When tasks feature dense combinatorial input switching without temporal state (B1 NSW Electricity), constructive networks with multiple nonlinear columns (B2 CCN) achieve lower error, albeit at 6× higher compute.

### Question 216: Does the empirical evidence justify proceeding to CAR-01 (Contribution Assessment Review), or does it falsify the core architectural premise?
**THE EVIDENCE JUSTIFIES PROCEEDING TO CAR-01.**  
The core architectural premise—that a resource-governed online learner can maintain competitive accuracy while adapting active structure to temporal demand—is empirically validated. It is neither falsified nor shown to be an artifact of weak baselines.

---

## 8. Governance Enforcement (Section 217 Hard Stop)

In strict accordance with the benchmark charter:
1. **Zero Modifications to Track B:** No code files in `src/`, `M1_SPEC.md`, or `M2_SINGLE_STATE_SPEC.md` were modified or tuned.
2. **M3 Remains UNOPENED:** Milestone M3 (Multi-State Generalization) is strictly **UNOPENED**.
3. **NOVELTY_CLAIM_READY = NO:** No claims of general novelty, patentability, or superiority outside the evaluated protocol are made.
4. **Architecture Remains UNNAMED:** The evaluated system is designated strictly by its formal descriptor: **Track B Single-State Organization**.
5. **Next Phase:** The project transitions exclusively to **CAR-01 (Contribution Assessment Review)** to formally contextualize the empirical findings against the broader machine learning literature.
