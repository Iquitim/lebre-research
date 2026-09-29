# Final Candidate Freeze: Multirate Shadow Governance (M1)

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  
**Status:** FROZEN AND SEALED PRIOR TO CONFIRMATORY SIMULATION  

---

## 1. Selected Candidate Architecture ($M_1$)

Following DEV sensitivity screening (840 runs) and component rate boundary mapping (2800 runs), Candidate **MR1_C** is selected as the primary confirmatory multirate candidate ($M_1$).

### 1.1 Architectural Principle: Fast Sensing, Slow Adaptation
- **Structural Probing (`Stage 7`):** Must execute rapidly ($K_{\text{probe}} = 2$) to avoid severe lag discovery latency.
- **Continuous Recurrent State Propagation (`Stage 9A`):** Must execute continuously ($K_{\text{rec\_forward}} = 1$) to preserve dynamical hidden state path-dependence.
- **Decimated Parameter Learning (`Stage 8D, 9D`):** Parameter updates are slow-timescale tolerant ($K_{\text{cand\_learn}} = 10$, $K_{\text{rec\_learn}} = 10$).
- **Subsampled Candidate Observation (`Stage 8A-C`):** Executed at $K_{\text{cand\_obs}} = 5$.
- **Freshness-Gated Arbitration (`Stage 10`):** Evaluated every $K_{\text{arbitration}} = 5$ steps, conditioned on evidence age $\tau \le 2$.

---

## 2. Frozen Specification Table

| Subsystem / Operation | Clock / Parameter | Cadence ($K$) | Duty ($d$) | Role | Skip Semantic | Freshness Tolerance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Live Linear & Normalization** | $K_{\text{live}}$ | 1 | 1.00 | BASELINE | Never skipped | $\tau = 0$ (Current) |
| **Stage 7: Correlation Probing** | $K_{\text{probe}}$ | 2 | 0.50 | SENSOR | `HOLD_STATE` | N/A |
| **Stage 8A-C: Candidate Obs** | $K_{\text{cand\_obs}}$ | 5 | 0.20 | EVIDENCE | `HOLD_STATE` | N/A |
| **Stage 8D: Candidate LMS Learn** | $K_{\text{cand\_learn}}$ | 10 | 0.10 | PARAM_LEARN | `HOLD_STATE` | Requires fresh obs |
| **Stage 9A: Recurrent Forward** | $K_{\text{rec\_forward}}$ | 1 | 1.00 | STATE_PROP | Never skipped | $\tau = 0$ (Continuous) |
| **Stage 9C-D: Recurrent RTRL Learn** | $K_{\text{rec\_learn}}$ | 10 | 0.10 | PARAM_LEARN | `HOLD_STATE` | $\tau \le 2$ |
| **Stage 10: Arbitration** | $K_{\text{arbitration}}$ | 5 | 0.20 | DECISION | `NO_ARBITRATION_UPDATE` | $\tau \le 2$ |
| **Router Type** | `router_type` | N/A | N/A | ROUTER | Deterministic Modulo | 0 FP overhead |

---

## 3. Clocks, Freshness, and Probations

### 3.1 Three Disaggregated Clocks
For every shadow adaptive object:
1. `STREAM_AGE`: Global stream timestep counter ($t$).
2. `OBSERVATION_COUNT`: Number of timesteps where the candidate/recurrent state was actively evaluated.
3. `PARAMETER_UPDATE_COUNT`: Number of parameter update gradient steps applied.

### 3.2 Probation Semantics
- Probation sufficiency for promotion evaluation requires actual shadow exposures:
  $$\text{candidate\_shadow\_exposures} \ge T_{\text{probation}} = 300$$
- Unobserved timesteps (`HOLD_STATE`) do not advance probation counters.

### 3.3 Evidence Freshness Invariant
- Counterfactual arbitration evaluates only if both discrete and recurrent counterfactual evidence satisfy:
  $$\tau_{\text{discrete}} = t - t_{\text{last\_cand\_obs}} \le 2 \quad \text{and} \quad \tau_{\text{rec}} = t - t_{\text{last\_rec\_fwd}} \le 2$$
- If evidence is stale ($\tau > 2$), arbitration execution is skipped with `NO_ARBITRATION_UPDATE` (weights and EMAs frozen).

---

## 4. Confirmatory Evaluation Cohort & Seeds

- **Cohort Size:** $N = 30$ independent streams.
- **Seed Range:** $1711..1740$ (Verified zero historical collision).
- **Benchmark Tasks:** Full 14-task suite ($I_1..I_{14}$, 6,000 steps each).
- **Primary Inferential Unit:** Seed aggregate across 14 tasks ($N = 30$).
- **Comparators:**
  - $M_0$: Canonical continuous compacted T3 baseline ($K=1$ across all stages).
  - $M_1$: Frozen multirate candidate (`MR1_C`).
  - $S_2$: Periodic whole-shadow baseline ($K=5$) retained as historical comparator.

---

## 5. Frozen Acceptance Criteria

1. **Mean Total Compute:** $\bar{F}_{\text{total}} \le 100.00\text{ FP/step}$.
2. **Predictive Non-Inferiority:** Upper one-sided 95% CI of $\Delta \text{NMSE} < +0.0100$.
3. **Pure-Lag Preservation:** $\Delta \text{NMSE}_{\text{pure-lag}} \le +0.0150$.
4. **Directional Switching Tolerance:** $\Delta \text{recovery} \le +50\text{ steps}$ on $I_{11}, I_{12}, I_{13}, I_{14}$.
5. **Hybrid Complementarity:** $G_{D\|B+R} > 0$ and $G_{R\|B+D} > 0$ on $I_9$.
6. **Quiescence Preservation:** Zero shadow drift during silence, reactivation delay $\le 100\text{ steps}$.

---

## 6. Pre-Simulation Cryptographic Hashes

```
b8be8ee68edb68aaab3951913fa25414c60972a3f71e9759decb159a4e2a3adf  scratch/run_v02_multirate_experiments.py
0dd9cbc88c754262f4f637e933a83bf5c493466c438bb81ecc3ca8b222cf00d9  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SHADOW_MULTIRATE_PROTOCOL.md
b4a5e8c6dcd6e68b2c6a6adf42f594e2f8ca82020db3e7d7ed36c624c6c718da  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SHADOW_MULTIRATE_PREREGISTRATION.md
f447da4d4718934d369975f12cb2381d6ddfeea8296088fb7279041e97516ee9  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/ATOMIC_SHADOW_OPERATION_LEDGER.csv
06fe2c1eced021406bb0a7eba23d4405f1e35aeb632b503d2328d123b5a77a5d  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SHADOW_ATOMIC_DEPENDENCY_DAG.md
ee1ea3855e04b91e90da60c3ef8ed35cdb1ab1f3f01656cd7d58735a757f1841  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SKIP_SEMANTICS_SPEC.md
66f2d1a78bc4de418dd07d3cf56bb1765a1b39aa758d9d76fd596622ee505750  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/EVIDENCE_FRESHNESS_SPEC.md
b35d8c42874deb9b12d31b65d02fe949f4f0f1c4a530207b7adb013f2a24bf72  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/MULTIRATE_COMPUTE_MODEL.md
77bd30a8b4215bd52db2aa7be2033ba705d28945dff7ad4bc30662bbfd502b43  experiments/LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01/SEED_PROVENANCE.md
```
