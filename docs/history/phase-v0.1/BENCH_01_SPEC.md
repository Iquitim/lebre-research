# BENCH_01_SPEC.md — External Benchmark Specification & Evaluation Governance

**Document ID:** BENCH-01-SPEC  
**Status:** CANONICAL SPECIFICATION FROZEN  
**Target Milestone:** BENCH-01 (External Competitive Evaluation)  
**Governing Standard:** Sections 217 & 218 of Protocol BENCH-01A  
**Date:** September 19, 2026  

---

## 1. Scientific Hypothesis (Section 3)

The BENCH-01 evaluation framework is designed to test the following primary scientific hypothesis:

$$\mathbf{H_{\text{TRACK\_B}}}: \text{A frozen resource-governed online learner can achieve competitive predictive performance while adapting active structure, compute, and memory to current temporal demand.}$$

Specifically, under streaming continuous data subject to concept drift, temporal delays, and event-driven persistence, Track B will achieve a favorable Pareto frontier (predictive accuracy versus operational FLOPs and memory footprint) compared with standard static and constructive baselines.

---

## 2. Non-Claims (Section 4)

To prevent misinterpretation and scientific inflation:
1. **No Universal Lowest Error Claim:** Track B does **NOT** claim to achieve the lowest raw MSE across all datasets. Heavy dense baselines (e.g., large ESNs, deep RNNs) with 100-fold more compute will achieve lower MSE on stationary streams.
2. **No Superiority Over Unconstrained Compute:** Track B is not designed for offline, high-throughput GPU batch training.
3. **No Representation-Order Dominance:** A scalar recurrent state ($N=1$) cannot represent high-dimensional vector memory manifolds.
4. **No Novelty of Individual Components:** Forward sensitivity (RTRL), unit maturation thresholds, utility eviction, and error-triggered allocation are foundational published techniques.

---

## 3. Frozen Track-B Version (Section 0 & 1)

The evaluation target is strictly frozen under [`M2_SINGLE_STATE_SPEC.md`](<lebre-research>/M2_SINGLE_STATE_SPEC.md):
- **Predictive Core:** Sparse linear filter with up to $K_{\max} = 10$ active features, probing $Q = 2$ candidates per step.
- **Temporal Lag Bank:** Probing arbitrary non-contiguous lags $x_{j, t-d}$ up to $D_{\max} = 50$.
- **Recurrent Core:** Minimal 1D scalar state ($N=1$) trained via exact online forward sensitivity RTRL.
- **Parsimonious Hierarchy:** Linear state tested first; gated state escalated only upon linear failure ($\ge 15\%$ error reduction).
- **Quiescent Retention:** Two-timescale structural observability ($O_{\text{struct}}$) preserving silent states during event gaps.
- **Obsolescence Accumulator:** Zero-excitation counter ($O_{\text{obs}}$) under empirical 300:1 asymmetric loss weighting.
- **Frozen Code:** All files in `src/` are frozen and bitwise immutable.

---

## 4. Benchmark Tiers (Section 141)

1. **Tier 1 (Strict Online Causal — Primary Competitive Tier):** Single-pass, zero-replay, causal step updates ($O(1)$ memory buffer).
2. **Tier 2 (Online with Replay / Auxiliary Memory — Secondary Tier):** Methods utilizing replay buffers.
3. **Tier 3 (Offline / Non-Strict Reference — Informational Tier):** Multi-epoch batch baselines reported for reference only.

---

## 5. Mechanistic Tasks (Block A; Sections 36–41)

Block A evaluates controlled synthetic streams ($T = 10{,}000$ steps per seed):
1. **A1 (Sparse Support Shift):** $D=50, K=3$; abrupt support change at $t=5000$.
2. **A2 (Single Delayed Dependency):** $y_t = 0.8 x_{1, t-4} + \epsilon_t$.
3. **A3 (Multiple Dispersed Delays):** $y_t = 0.5 x_{1, t-2} + 0.5 x_{2, t-8} + \epsilon_t$.
4. **A4 (Long-Delay Scaling):** $y_t = 0.8 x_{1, t-d} + \epsilon_t$, $d \in \{5, 15, 30, 50\}$.
5. **A5 (SET/RESET Memory):** Poisson event pulses driving bistable memory latch.
6. **A6 (Context Routing):** Context feature switching between static and AR paths.
7. **A7 (Quiescent Retention):** Information cues separated by Poisson gaps ($L_{\text{gap}} \sim \text{Poisson}(150)$).
8. **A8 (Abrupt Tri-Regime Transition):** Cyclic shift: Linear $\to$ Lag $\to$ Recurrent.
9. **H1 (Holdout Resonator):** Damped 2nd-order oscillator with drifting frequency and damping.
10. **H2 (Holdout Volterra):** State-dependent switching quadratic Volterra kernel.

---

## 6. Public Real-World Datasets (Block B; Sections 12–35)

Block B comprises five genuine external continuous physical streams:
1. **B1: NSW_ELECTRICITY_DERIVED_REGRESSION** ($N = 45{,}312$, $D=5$, continuous spot price $/MWh; `TASK_STATUS = NONCANONICAL_DERIVED_REGRESSION_TASK`).
2. **B2: MPI Jena Climate Weather Stream** ($N = 70{,}000$, $D=13$, continuous temperature $^\circ\text{C}$).
3. **B3: UCI Gas Dynamic Mixture Stream** ($N = 20{,}000$, $D=16$, continuous CO ppm concentration).
4. **B4: IEEE Silverbox Nonlinear System ID** ($N = 40{,}000$, $D=1$, continuous output voltage $V$).
5. **B5: Household Power Static Negative Control** ($N = 25{,}000$, $D=6$, active power $kW$).

---

## 7. Dataset Provenance (Sections 157 & 158)

- All datasets are downloaded from canonical permanent DOIs or official government archives.
- File integrity is cryptographically validated via SHA-256 hashes before execution.
- Mutable remote web scraping is strictly prohibited.

---

## 8. Temporal Ordering (Sections 86 & 97)

All benchmark streams are strictly chronological time series. **Random train/test shuffling, k-fold cross validation, and temporal permutation are strictly forbidden.**

---

## 9. Prediction Horizons (Section 17)

Every task is evaluated at a pre-registered **single-step-ahead horizon ($h=1$)**:
$$\hat{y}_t = f(x_t, x_{t-1}, \dots; \theta_{t-1})$$
Evaluating arbitrary post-hoc multi-step horizons is prohibited.

---

## 10. Target Availability (Section 7)

Target $y_t$ becomes available strictly in Phase 5 of each step, immediately following the emission of prediction $\hat{y}_t$. Zero lookahead or retrospective label revision is permitted.

---

## 11. Prequential Protocol (Section 6)

Every streaming step executes the causal cycle:
1. Receive $x_t$;
2. Scale $x_t$ using statistics from step $t-1$;
3. Emit prediction $\hat{y}_t$;
4. Record prequential loss $(y_t - \hat{y}_t)^2$;
5. Reveal $y_t$, update model parameters, and update normalization scalers.

---

## 12. Preprocessing Governance (Sections 9–11)

- **Static Safe:** Fixed physical unit scalings.
- **Online Adaptive:** Recursive Welford scalers ($\alpha = 10^{-4}$) updated post-prediction.
- **Forbidden:** Full-dataset normalization, non-causal digital filtering, centered windows, future imputation.

---

## 13. Audited Baselines (Sections 42–66)

- **`B1_RZA_LMS`:** Sparse linear filter (Chen et al. 2009) — *Mandatory*.
- **`B2_CCN`:** Columnar-constructive scalar RTRL (Javed et al. JMLR 2023) — *Mandatory*.
- **`B3_MUSE_RNN`:** Online self-evolving RNN (Das et al. 2019; Minimal Regression Adaptation) — *Mandatory*.
- **`B4_MINIMAL_GRU`:** Static 1-state gated unit (Cho et al. 2014) — *Mandatory*.
- **`B5_ONLINE_ESN`:** Echo state network with online readout (Jaeger 2001) — *Mandatory*.
- **`B6_VARIABLE_TAP`:** Variable-tap adaptive filter (Zhao et al. 2008) — *Recommended*.
- **`B7_LRU_STREAM`:** Diagonal linear recurrent state (Orvieto et al. 2023) — *Recommended*.

---

## 14. Baseline Applicability (Sections 67 & 68)

Baseline applicability is strictly governed by `experiments/BENCH-01A/BENCH_01A_APPLICABILITY_MATRIX.csv`. Models are evaluated only where mathematically applicable without artificial modifications.

---

## 15. Operating Regime R1: Natural Configurations (Section 70)

Baselines are configured per author recommendations and native capacities (e.g., ESN with $N_{\text{res}} = 20$, CCN with 1–2 columns, MUSE-RNN with default split/prune thresholds).

---

## 16. Operating Regime R2: Architecture-Neutral Resource-Matched Configurations (Sections 71–73)

Universal resource matching operates strictly on observable physical envelopes rather than internal architectural semantics:
- **`R2-FLOP` (Algorithmic Compute Ceiling):** $\text{Mean\_FLOPs} \le 100\text{ FLOPs/step}$ (calibrated against Track B's measured peak of 72 FLOPs/step);
- **`R2-MEM` (Deployment Memory Ceiling):** $M_{\text{DEPLOY}} = M_{\text{STATIC}} + M_{\text{STATE}} + M_{\text{AUX}} \le 1{,}024\text{ Bytes (1.0 KB)}$ (calibrated against Track B's deployment memory of $\approx 200$–$400$ Bytes).
- **Prohibition:** Zero internal structural constraints ($K \le 10$, $N \le 1$, columns, or reservoir nodes) are imposed on external baselines. Baselines configure their own internal knobs to satisfy the observable envelopes.

---

## 17. Hyperparameter Search Spaces (Section 79)

All non-frozen baselines are assigned explicit, locked 16-configuration search grids detailed in `BENCH_01A_TUNING_SPEC.md`.

---

## 18. Hyperparameter Tuning Budget (Section 78)

Exactly **16 configurations** (`MAX_CONFIGS = 16`) per baseline per task family. Additional result-driven searching is strictly prohibited.

---

## 19. Chronological Calibration / Validation / Test Splitting (Sections 85–93)

- **Calibration Prefix (0% – 15%):** Hyperparameter selection on 3 seeds. Discarded from test scoring.
- **Validation Segment (15% – 30%):** Stability and divergence check.
- **Final Test Segment (30% – 100%):** Locked competitive evaluation over 30 independent seeds.

---

## 20. Seed Policy (Sections 94–97)

$N = 30$ independent random seeds ($\mathcal{S} = \{101, \dots, 130\}$) for all stochastic components. Stream ordering remains 100% fixed and identical across all models.

---

## 21. Statistical Analysis Plan (Sections 98–103)

- Paired differences over identical seeds and streams;
- 10,000-replicate bootstrap 95% confidence intervals;
- Benjamini-Hochberg False Discovery Rate correction ($q = 0.05$);
- Effect size reporting (Cohen's $d_z$ and Cliff's $\delta$).

---

## 22. Predictive Accuracy Metrics (Section 74)

- Mean Squared Error (MSE);
- Mean Absolute Error (MAE);
- Normalized MSE (NMSE);
- Prequential Cumulative Regret ($R_T$).

---

## 23. Dynamic Adaptation Metrics (Sections 74 & 111)

- Post-change regret ($R_{\text{post}}$, first 500 steps post-drift);
- Recovery latency ($L_{\text{rec}}$, steps to return within $110\%$ of steady-state error);
- Rolling MSE trajectories.

---

## 24. Computational Operations Metrics (Sections 114–116)

- Mean FLOPs / step;
- P95 FLOPs / step;
- Peak FLOPs / step;
- Active parameter count ($K_{\text{active}}$).

---

## 25. Memory Metrics (Sections 127–131)

- Persistent parameter memory ($M_{\text{STATIC}}$);
- Recurrent state buffer ($M_{\text{STATE}}$);
- Auxiliary statistics and traces ($M_{\text{AUX}}$);
- Deployment footprint ($M_{\text{STATIC}} + M_{\text{STATE}} + M_{\text{AUX}}$ in Bytes);
- Resource reclamation delta ($M_{\text{post}} - M_{\text{pre}}$).

---

## 26. Runtime Metrics (Sections 117–123, 132–135)

- Median step latency ($\mu s$);
- P95 and P99 latency;
- Throughput (samples/second) on dedicated single-thread CPU.

---

## 27. Multi-Objective Pareto Analysis (Sections 168–173)

No single winner score. Pre-registered 2D projections:
1. Mean FLOPs/step vs Normalized MSE;
2. Persistent Memory (Bytes) vs Normalized MSE;
3. Mean FLOPs/step vs Post-Change Regret ($R_{\text{post}}$).

---

## 28. Hardware Execution Environment (Sections 124 & 125)

Standardized x86-64 CPU execution node (pinned single-thread execution, GPU disabled, 16 GB RAM).

---

## 29. Software Environment & Lock (Sections 125 & 126)

Python `3.11.9`, NumPy `1.26.4`, SciPy `1.12.0`, PyTest `9.0.2`. Thread limits enforced (`OMP_NUM_THREADS=1`).

---

## 30. Reproducibility Guarantee (Sections 240 & 241)

Reproducible via single CLI command:
```bash
python -m experiments.bench01.run --config experiments/BENCH-01A/bench_01_locked_config.json
```

---

## 31. Failure Handling Policy (Sections 143–147)

Numerical divergences are logged as categorical execution failures (`NUMERICAL_DIVERGENCE`). The arbitrary $1.5\times$ penalty is excised. Primary predictive metrics are aggregated strictly over valid, complete runs; algorithmic reliability is reported via explicit `DIVERGENCE_RATE`. Consumed compute prior to failure is fully accounted for. Zero secret configuration replacement.

---

## 32. Pre-Registered Decision Criteria (Cases A–E; Section 177)

- **Case A (Efficiency Justification):** Match prediction within 5% with $\ge 50\%$ lower compute/memory.
- **Case B (Continual Adaptation Justification):** Faster recovery ($p < 0.01$) at resource parity (Regime R2).
- **Case C (Tradeoff Only):** Lower compute but $>25\%$ higher error.
- **Case D (Hypothesis Falsified):** Baselines match or beat prediction and compute.
- **Case E (Pareto Tradeoff):** Domain-specific results; no superiority claim.

---

## 33. Forbidden Post-Hoc Modifications (Section 184)

Zero modifications to Track B code, thresholds, or mechanisms are permitted after benchmark execution begins.

---

## 34. Known Architectural Limitations (Section 0)

1. Single-state capacity limit ($N=1$ cannot represent vector manifolds);
2. Sequential probe latency (non-contiguous delay discovery requires exploration budget);
3. Linear-first probation delay (requires 100-step shadow testing before active prediction).
