# Scientific Protocol: LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01

**Study Identifier:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Governing Standard:** Level 1 Confirmatory Preregistration, Single-Difference Invariant, Causal Decomposition  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Scientific Objective & Scope

### 1.1 Core Scientific Question
Can LEBRE decouple the operational execution rates of:
1. Structural sensing (correlation grid probing)
2. Provisional candidate observation
3. Provisional candidate parameter learning
4. Recurrent shadow state propagation
5. Recurrent shadow parameter learning (RTRL)
6. Counterfactual evidence accumulation
7. Capacity arbitration

such that computationally expensive operations execute significantly less frequently than stream rate ($K > 1$) **without degrading predictive non-inferiority, structural discovery, regime-switching agility, or quiescent retention**?

### 1.2 Strict Scope & Immutable Invariants
The following components belong to the frozen canonical and validated baseline substrate and **must remain completely unaltered**:
- Live prediction pipeline (linear predictor forward pass and LMS updates)
- Causal standard scaler (transform and online Welford updates)
- History ring buffer semantics and bounds
- Active delay tap prediction and active LMS parameter updates
- Active recurrent unit forward pass and active RTRL updates
- Lag promotion thresholds ($\theta_{\text{tol}} = 0.015$, evidence $> 0.02$, age $\ge 15$)
- Recurrent promotion thresholds ($\theta_{\text{tol}} = 0.015$, evidence $> 0.02$, age $\ge 15$)
- Dynamic eviction thresholds ($R < 0.03, \text{age} > 250$ for taps; conditional gain floor for recurrent)
- Gate 6 redundancy ceiling ($\le 0.05$ on $I_{10}$; carried forward as legacy FAIL)
- IEEE 754 float16 compacted correlation grid storage with transient float32 arithmetic
- $T_3$ resource-aware conditional arbitration topology
- Canonical `src/` and canonical `tests/` directories.

**Only the shadow discovery cadence, parameter learning cadence, and evidence routing mechanisms may be varied.**

---

## 2. Atomic Shadow Subsystem Decomposition

The shadow subsystem is decomposed into 17 atomic operations across four pipeline stages:

```
+---------------+----------------------------------+-----------------------+----------+---------+----------+
| Stage & Op ID | Operation Name                   | Functional Role       | FP Flops | Int Ops | Cast Ops |
+---------------+----------------------------------+-----------------------+----------+---------+----------+
| 7A            | corr_probe_history_query         | SENSOR                |    0.0   |    2    |    0     |
| 7B            | corr_probe_innovation            | SENSOR                |    2.0   |    0    |    0     |
| 7C            | corr_grid_ema_update             | SENSOR                |    2.0   |    2    |    2     |
| 7D            | corr_cand_threshold_check        | DECISION              |    0.0   |    1    |    0     |
+---------------+----------------------------------+-----------------------+----------+---------+----------+
| 8A            | cand_forward_predict             | OBSERVATION           |    2.0   |    0    |    0     |
| 8B            | cand_counterfactual_loss         | EVIDENCE_ACCUMULATION |    2.0   |    0    |    0     |
| 8C            | cand_evidence_ema                | EVIDENCE_ACCUMULATION |    4.0   |    0    |    0     |
| 8D            | cand_parameter_lms_update        | PARAMETER_LEARNING    |    2.0   |    0    |    0     |
+---------------+----------------------------------+-----------------------+----------+---------+----------+
| 9A            | rec_shadow_forward_state_prop    | STATE_PROPAGATION     |   12.0   |    0    |    0     |
| 9B            | rec_shadow_output_predict        | OBSERVATION           |    6.0   |    0    |    0     |
| 9C            | rec_shadow_rtrl_sensitivity      | PARAMETER_LEARNING    |    8.0   |    0    |    0     |
| 9D            | rec_shadow_rtrl_parameter_update | PARAMETER_LEARNING    |    8.0   |    0    |    0     |
| 9E            | rec_shadow_evidence_ema          | EVIDENCE_ACCUMULATION |    6.0   |    0    |    0     |
+---------------+----------------------------------+-----------------------+----------+---------+----------+
| 10A           | cf_loss_grid_construction        | EVIDENCE_ACCUMULATION |    8.0   |    0    |    0     |
| 10B           | cf_conditional_gain_eval         | EVIDENCE_ACCUMULATION |    4.0   |    0    |    0     |
| 10C           | cf_gain_ema_filtering            | EVIDENCE_ACCUMULATION |   16.0   |    0    |    0     |
| 10D           | cf_arbitration_decision          | DECISION              |    0.0   |    6    |    0     |
+---------------+----------------------------------+-----------------------+----------+---------+----------+
```

---

## 3. Disaggregated Clocks, Probation & Skip Semantics

### 3.1 The Three Clocks
Every shadow adaptive object maintains three distinct temporal counters:
1. `STREAM_AGE`: Total stream timesteps elapsed since candidate birth ($t$).
2. `OBSERVATION_COUNT`: Number of timesteps where the candidate made an explicit shadow forward prediction against active input.
3. `PARAMETER_UPDATE_COUNT`: Number of timesteps where candidate weights were modified via LMS/RTRL.

### 3.2 Probation Semantics
- Probation maturity ($T_{\text{prob}} = 15$ steps) must be evaluated based strictly on **actual shadow exposures** (`OBSERVATION_COUNT \ge 15`), NOT on elapsed stream age.
- Decimating candidate observation inherently stretches stream probation time, protecting young candidates from premature promotion before sufficient empirical statistics are gathered.

### 3.3 Skip Semantics & Anti-Fabrication Rule
When an operation is skipped due to downsampling:
- **`HOLD_STATE`**: State variables (e.g. recurrent hidden state $h$, filter weights $w$, correlation grid cells) remain unmodified.
- **`NO_NEW_EVIDENCE`**: Evidence accumulators and gain EMAs are NOT updated. Under no circumstances may zero loss, zero gain, or zero correlation be fabricated.
- **`STALE_WITH_AGE_METADATA`**: Output signals carry an explicit `age_steps` tag. Counterfactual arbitration checks evidence freshness before updating.

---

## 4. Compute Feasibility Model & 100-FLOP Budget Boundary

Total per-step compute is modeled analytically:
$$F_{\text{total}} = F_{\text{live}} + d_{\text{probe}} F_{\text{probe}} + d_{\text{cand\_obs}} F_{\text{cand\_obs}} + d_{\text{cand\_learn}} F_{\text{cand\_learn}} + d_{\text{rec\_prop}} F_{\text{rec\_prop}} + d_{\text{rec\_learn}} F_{\text{rec\_learn}} + d_{\text{arb}} F_{\text{arb}} + F_{\text{router}}$$

Given $F_{\text{live}} \approx 81.17\text{ FP}$ and nominal unoptimized shadow cost $F_{\text{shadow}} \approx 86.53\text{ FP}$ (summing to $\approx 167.70\text{ FP}$):
To meet the mandatory primary ceiling:
$$\bar{F}_{\text{total}} \le 100.0\text{ FP/step}$$
The available marginal budget for all shadow operations and router overhead is:
$$F_{\text{shadow\_budget}} = 100.0 - 81.17 = \mathbf{18.83\text{ FP/step}}$$

### Feasible Cadence Combinations (Analytical Bounds)
- If recurrent state propagation executes continuously ($d_{\text{rec\_prop}} = 1.0$, cost $12.0\text{ FP}$), remaining shadow budget is $18.83 - 12.0 = 6.83\text{ FP/step}$.
- Probing at $K_{\text{probe}} = 2$ ($d_{\text{probe}} = 0.50$, cost $4.0\text{ FP}$) leaves $2.83\text{ FP/step}$.
- Candidate learning and recurrent learning must execute at $K \ge 5$ ($d \le 0.20$), and arbitration must execute at $K \ge 5$ or on-demand to remain strictly within $100.0\text{ FP/step}$.

---

## 5. Experimental Execution Stages

### Stage 1: Component Sensitivity Screening on DEV ($N_{\text{DEV}} = 10$, seeds `1701..1710`)
Evaluate isolated cadence interventions at diagnostic period $K=5$:
- $D_0$: Continuous baseline (all components $K=1$)
- $D_7$: Only correlation probing $K=5$; all other components $K=1$
- $D_8$: Only candidate observation and learning $K=5$; all others $K=1$
- $D_{9F}$: Only recurrent state propagation $K=5$; all others $K=1$
- $D_{9L}$: Only recurrent parameter learning $K=5$; state propagation $K=1$
- $D_{10}$: Only counterfactual arbitration $K=5$; all others $K=1$.

### Stage 2: Component Rate Ladder ($K \in \{1, 2, 5, 10\}$)
For sensitive components, refine the downsampling period across the allowed discrete ladder to identify stability and tracking boundaries.

### Stage 3: Multirate Policy Candidate Evaluation on DEV ($\le 6$ policies)
Formulate and test:
- **$MR_1$ (Fast Sensing, Slow Adaptation):** Fast probing ($K=2$), continuous recurrent propagation ($K=1$), slow candidate adaptation ($K=5$), slow recurrent learning ($K=5$), fresh-evidence arbitration.
- **$MR_2$ (Data-Selective Adaptation):** Innovation-gated candidate and recurrent parameter updates.
- **$MR_3$ (Temporal-Evidence Routed Multirate):** Cheap $\mathcal{O}(1)$ residual autocorrelation sentinel gating temporal exploration.

### Stage 4: Candidate Selection & Pre-Confirmatory Freeze
Select the simplest policy satisfying all criteria. Freeze code, clocks, thresholds, and seeds.

### Stage 5: Final Confirmatory Execution ($N_{\text{FINAL}} = 30$, seeds `1711..1740`)
Execute frozen candidate $M_1$ vs. continuous compacted baseline $M_0$ across all 14 benchmark tasks ($840$ total runs).
Evaluate primary resource gate, predictive non-inferiority, pure-lag preservation, recurrent continuity, switching latencies, and hybrid complementarity.
