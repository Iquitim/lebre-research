# Final Scientific Report: LEBRE v0.2 Multirate Shadow Decomposition

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  
**Status:** COMPLETE CONFIRMATORY REPORT  

---

## 1. Executive Summary & Core Verdict

This study investigated whether the failure of whole-block shadow governance (observed in study `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01` under schedulers $S_2$ and $S_3$) could be resolved by **decoupling the shadow subsystem into fine-grained, component-specific execution rates**.

The investigation proceeded in two strictly separated phases:
1. **Phase A (Deterministic Accounting Microcorrection):** Resolved the arithmetic ambiguity regarding transient casting workspace in CPU/FPU registers ($0\text{ B}$ stack SRAM) versus conservative stack frames ($8\text{ B}$ stack SRAM), proved that the "57 tests" count was a discovery artifact of `unittest` while canonical `pytest tests/` collects and passes all 124 test items across 20 files, and corrected switching latency units from physical "seconds" to discrete stream "steps". Hard Gate A8 passed unconditionally.
2. **Phase B (Multirate Decomposition):** Decomposed the shadow subsystem into 17 atomic operations across Stages 7, 8, 9, and 10. Following DEV sensitivity screening ($N=10$, 840 runs) and rate boundary mapping (2,800 runs), Candidate $M_1$ (`MR1_C`: Fast Sensing, Slow Adaptation) was frozen and evaluated on a confirmatory cohort of $N=30$ independent streams ($1711..1740$) across the 14-task benchmark suite ($1,260$ simulation runs).

### Primary Scientific Outcome
```
PRIMARY_OUTCOME = COMPONENT_TIMESCALE_CONFLICT
MULTIRATE_SHADOW_GOVERNANCE_SUPPORTED = NO
WHOLE_BLOCK_SHADOW_GOVERNANCE = NOT_VALIDATED
SAFE_FOR_INTEGRATED_VALIDATION = NO
SAFE_TO_OPEN_M3 = NO
```

While component decoupling established conclusively that **recurrent state propagation requires path-dependent dynamical continuity ($K=1$)** while **recurrent parameter learning tolerates $10\times$ decimation**, the overall multirate architecture failed two mandatory gates:
1. **Primary Compute Gate ($\le 100.00\text{ FP/step}$):** $M_1$ achieved **$108.36\text{ FP/step}$** (FAIL).
2. **Predictive Non-Inferiority ($+0.0100$ margin):** Aggregate $\Delta \text{NMSE} = \mathbf{+0.019376}$, with a 95% one-sided CI upper bound of **$+0.027173$** (FAIL).

---

## 2. Definitive Answers to the 20 Preregistered Questions

### 1. Which shadow operations require near-stream-rate execution?
**Structural Probing (`Stage 7`)** and **Recurrent State Propagation (`Stage 9A`)**. Probing scans 165 lag pairs across the input space; any decimation ($K \ge 2$) proportionally dilates lag discovery latency. Recurrent forward propagation maintains the continuous path-dependent hidden state $h(t)$; decimating it corrupts the dynamical attractor.

### 2. Which tolerate slower observation?
**Candidate Counterfactual Loss Observation (`Stage 8A-C`)** and **Counterfactual Arbitration (`Stage 10`)**. Subsampling candidate loss evaluation to $K=5$ preserves loss trends without introducing bias, and evaluating arbitration every $K=5$ steps (conditioned on evidence freshness $\tau \le 2$) eliminates $22.40\text{ FP/step}$ with zero stability degradation.

### 3. Which tolerate slower parameter learning?
**Candidate LMS Parameter Updates (`Stage 8D`)** and **Recurrent RTRL Parameter Updates (`Stage 9C-D`)**. In online streaming settings with slow-moving statistical distributions, parameter gradient steps can be decimated to $K=10$ with negligible degradation in tracking capability, saving $34.78\text{ FP/step}$ in RTRL sensitivity compute.

### 4. Does recurrent state need faster cadence than recurrent weight learning?
**YES.** This was proven causally in isolated sensitivity test $D_{9F}$ vs. $D_{9L}$ and the rate ladder. Decimating recurrent forward propagation to $K=5$ produced a $+0.00286$ NMSE degradation, whereas decimating RTRL parameter updates to $K=10$ with continuous forward propagation maintained exact baseline tracking ($\Delta \text{NMSE} = -0.00020$). Hidden state dynamics are path-dependent; parameter adaptations are statistical averages.

### 5. Can probation be expressed in actual shadow exposures rather than stream time?
**YES.** Under the frozen probation semantics, candidate shadow exposures (`candidate_shadow_exposures`) were advanced only during active observation steps ($K_{\text{cand\_obs}}$), ensuring that structural promotions required $T_{\text{probation}} = 300$ actual exposures rather than 300 wall-clock steps. This prevented unvalidated structural escalation.

### 6. Can cheap lag sensing remain frequent while expensive candidate evaluation is sparse?
**YES, but with a severe budget conflict.** Probing at $K=2$ ($4.00\text{ FP}$) combined with candidate evaluation at $K=5$ ($1.20\text{ FP}$) successfully decoupled sensing from evaluation. However, because probing scans 165 pairs in steps of 2, even $K=2$ produces unacceptable delay in discovering true delays on moving delay streams ($I_5$).

### 7. Does data-selective adaptation outperform blind periodic decimation?
**NO.** Candidate $MR_2$ (gated by innovation threshold $\gamma_{\text{innov}} = 0.010$) suffered severe behavioral degradation ($\Delta \text{NMSE} = +0.0754$, compute = $114.09\text{ FP}$). In noisy online environments, small innovations contain vital cumulative gradient information. Skipping updates based on instantaneous thresholding starved the filters of convergence energy.

### 8. Can cheap temporal evidence reduce the I2 false-wake problem without missing genuine temporal regimes?
**NO.** Candidate $MR_3$ (residual serial correlation routing with $\theta_{\text{temporal}} = 0.15$ and heartbeat $H=100$) successfully slept on $I_2$ ($37.0\%$ silence, saving $17.5\text{ FP/step}$), but missed subtle onset dynamics in pure-lag and switching tasks ($I_3, I_4, I_5, I_{11}, I_{12}$), degrading aggregate NMSE by **$+0.0684$**. Residual autocorrelation is a necessary but insufficient indicator of model inadequacy under undermodelling (Douma et al., 2008).

### 9. How much does the router itself cost?
- Modular multirate clocks ($M_1$): **$0.00\text{ FP/step}$**, $0\text{ B}$ persistent memory (integer modulo counters).
- Data-selective innovation gate ($MR_2$): **$2.00\text{ FP/step}$**, $0\text{ B}$ persistent memory.
- Temporal autocorrelation router ($MR_3$): **$6.00\text{ FP/step}$**, $18\text{ B}$ persistent memory.

### 10. Is mean total online FP <= 100?
**NO.** Confirmatory mean across 30 independent seeds and 14 tasks is **$108.36\text{ FP/step}$** (Median: $109.39$, $P_{95}: 128.51$, Peak: $143.02$).

### 11. Is aggregate NMSE non-inferior within +0.0100?
**NO.** Aggregate $\Delta \text{NMSE} = \mathbf{+0.019376}$ (std: $0.024773$, SE: $0.004523$). The upper one-sided 95% CI bound is **$+0.027173$**, exceeding the $+0.0100$ ceiling.

### 12. Are all directional switching tasks preserved?
**NO.** On $I_{11}$ (Delay $\to$ Latent), recovery latency increased by **$+79.70\text{ steps}$** (vs $+50$ ceiling). On $I_{12}$ (Latent $\to$ Delay), recovery latency increased by **$+633.73\text{ steps}$** (severe failure). On $I_{13}$ and $I_{14}$, recovery latency met the tolerance ($\Delta = -1.50$ and $-83.20\text{ steps}$).

### 13. Is I9 complementarity preserved?
**YES.** On Task $I_9$, counterfactual gains remained strictly positive: $G_{D\|B+R} = 0.2311 > 0$ and $G_{R\|B+D} = 0.0532 > 0$. Dual structural occupancy was maintained without competitive exclusion.

### 14. Is quiescence preserved?
**YES.** On $I_7$ (quiescent latent state) and $I_8$ (quiescent discrete delay), shadow compute during the silence interval ($t \in [2000, 4000)$) was reduced by **$45.8\%$** with $100\%$ parameter retention and zero reactivation delay upon signal resumption.

### 15. What happens incidentally to I10 dual occupancy?
On Task $I_{10}$ (redundant temporal control), $M_1$ exhibited a steady-state dual occupancy rate of $\text{frac\_both} = \mathbf{0.5140}$ ($51.40\%$), compared to $0.3983$ in $M_0$ and $0.1675$ in $S_2$. Gate 6 remains a **FAIL** ($> 0.05$). Incidental observation only; no Gate-6 repair was claimed.

### 16. Does peak-memory failure remain?
**YES.** Maximum occupied persistent state remains **$1064\text{ B}$** ($+40\text{ B}$ above 1 KiB) during concurrent lag and recurrent promotion. Peak working SRAM remains **$1064\text{ B}$** (hardware FPU) or **$1072\text{ B}$** (stack frame). Legacy status carried forward as **FAIL**.

### 17. Which atomic component dominates remaining shadow cost?
**Stage 9A: Recurrent State Propagation ($12.00\text{ FP/step}$)**, followed by **Stage 10: Counterfactual Arbitration ($5.60\text{ FP/step}$)** and **Stage 7: Probing ($4.00\text{ FP/step}$)**.

### 18. Is the resulting mechanism simpler or more complex than S3?
**Simpler in runtime logic, but structurally more disaggregated.** $M_1$ uses purely deterministic modular integer counters ($K_{\text{probe}}=2, K_{\text{cand}}=5, K_{\text{rec}}=10, K_{\text{arb}}=5$) without stateful threshold sentinels (Page-Hinkley) or heuristic wake/sleep states. However, it requires tracking 6 independent component clocks.

### 19. Is the additional complexity justified empirically?
**NO.** Because $M_1$ fails both the compute budget ($108.36 > 100\text{ FP}$) and predictive non-inferiority ($+0.0272 > +0.0100$), the multirate decoupling does not achieve its preregistered objectives.

### 20. Is the candidate ready only for further validation, or for later integrated validation?
**NEITHER.** The multirate shadow candidate $M_1$ is **REJECTED** from integration. The project must pivot to memory compaction and structural grid dimension reduction before reopening shadow governance.

---

## 3. Visualizations & Graphical Evidence

The experimental findings are illustrated in 12 publication-quality figures located in `figures/`:

1. **Figure F1 (`F1_atomic_shadow_cost_breakdown.png`):** Disaggregated FP FLOP cost of each atomic shadow operation categorized by functional role.
2. **Figure F2 (`F2_component_sensitivity_K5.png`):** Isolated sensitivity screening at $K=5$ demonstrating high sensitivity of Probing ($D_7$) versus high tolerance of Recurrent Learning ($D_{9L}$) and Arbitration ($D_{10}$).
3. **Figure F3 (`F3_component_rate_vs_behavior.png`):** Rate ladder impact on $\Delta \text{NMSE}$ as decimation period $K$ increases from 1 to 10.
4. **Figure F4 (`F4_component_rate_vs_compute.png`):** Total online compute vs. component cadence $K$.
5. **Figure F5 (`F5_multirate_compute_breakdown.png`):** Confirmatory compute breakdown comparing $M_0$ ($175.4\text{ FP}$), $M_1$ ($108.4\text{ FP}$), and $S_{2, K=5}$ ($90.1\text{ FP}$) against the $100\text{ FP}$ ceiling.
6. **Figure F6 (`F6_seed_level_nmse_delta.png`):** Distribution of seed-level $\Delta \text{NMSE}$ across $N=30$ independent streams showing 95% CI upper bound exceeding $+0.0100$.
7. **Figure F7 (`F7_switch_latency_by_task.png`):** Directional regime switching recovery latency across tasks $I_{11}..I_{14}$.
8. **Figure F8 (`F8_recurrent_forward_vs_learning_decimation.png`):** Causal demonstration that recurrent state propagation requires continuous execution while parameter learning tolerates $K=10$ decimation.
9. **Figure F9 (`F9_I2_false_wake_vs_temporal_tasks.png`):** False sleep and predictive failure of the temporal autocorrelation router ($MR_3$).
10. **Figure F10 (`F10_quiescence_component_duty.png`):** Shadow compute reduction during signal silence on $I_7$ and $I_8$.
11. **Figure F11 (`F11_clock_utilization.png`):** Normalized executions per 1,000 stream steps for each disaggregated clock in $M_0$ vs. $M_1$.
12. **Figure F12 (`F12_compute_behavior_pareto.png`):** Compute-behavior Pareto frontier illustrating the empty intersection between $\le 100\text{ FP}$ and $\Delta \text{NMSE} \le +0.0100$.

---

## 4. Confirmatory Statistical Verification Tables

### 4.1 Predictive Non-Inferiority ($N=30$, Inferential Unit: Seed)
- $M_0$ Mean NMSE: **$0.299225$**
- $M_1$ Mean NMSE: **$0.318601$**
- Mean $\Delta \text{NMSE}$: **$+0.019376$**
- Standard Deviation: **$0.024773$**
- Standard Error: **$0.004523$**
- 90% One-Sided CI Upper: **$+0.025301$**
- 95% One-Sided CI Upper: **$+0.027173$**
- 99% One-Sided CI Upper: **$+0.030509$**
- Preregistered Ceiling: **$+0.010000$**
- Status: **FAIL**

### 4.2 Directional Switching Latency ($N=30$)
| Benchmark Task | $M_0$ Recovery (steps) | $M_1$ Recovery (steps) | $\Delta$ Latency (steps) | Preregistered Limit | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $I_{11}$ (Delay $\to$ Latent) | 480.80 | 560.50 | **$+79.70$** | $\le +50.0\text{ steps}$ | **FAIL** |
| $I_{12}$ (Latent $\to$ Delay) | 884.27 | 1518.00 | **$+633.73$** | $\le +50.0\text{ steps}$ | **FAIL** |
| $I_{13}$ (Hybrid $\to$ Memoryless) | 126.50 | 125.00 | **$-1.50$** | $\le +50.0\text{ steps}$ | **PASS** |
| $I_{14}$ (Intermittent Hybrid) | 465.20 | 382.00 | **$-83.20$** | $\le +50.0\text{ steps}$ | **PASS** |

---

## 5. Architectural Implications & Governance

1. **The Irreducible Floor:** In a dual-memory online architecture where linear normalization costs $58.0\text{ FP}$, active lag and recurrent prediction add $18.3\text{ FP}$, and continuous recurrent forward tracking adds $12.0\text{ FP}$, the minimum operational baseline is **$88.3\text{ FP/step}$**.
2. **The Timescale Dilemma:** Discrete memory discovery across 165 lag combinations cannot be decimated without proportional discovery delays. Decimating probing from $K=1$ to $K=2$ produces a catastrophic $+633\text{ step}$ latency penalty when transitioning from latent to discrete regimes ($I_{12}$).
3. **Governance Mandate:** The candidate $M_1$ is experimental and non-canonical. It must NOT be merged into canonical `src/` or `tests/`. Canonical files remain bitwise immutable.
