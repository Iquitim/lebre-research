# LEBRE-V0.2-INTEGRATION-DESIGN-01: Pre-Registered Experimental Protocol
## Rigorous Causal Streaming Protocol, Statistical Policy, Hardware Ceilings & Success Gate Definitions

**Document ID:** `LEBRE-V0.2-PROTO-2026-v1.0`  
**Status:** `PRE-REGISTERED_AND_FROZEN_PROTOCOL`  
**Phase:** Integration Design & Structural Arbitration  
**Lead Protocol Officer:** Skeptical Senior ML Systems Researcher, Statistical Reviewer, Scientific-Software Auditor  

---

## 1. Experimental Scope & Architectural Freeze

1. **Governing State:** Canonical LEBRE v0.1 remains frozen with scope limits. Codebase directories `src/` and `tests/` remain 100% bitwise immutable. Milestone M3 remains `UNOPENED`.
2. **Primary History Representation:** `FP16_EXACT_ADDRESSABLE_RING` (350 Bytes RAM, $92.42$ FP FLOPs reference workload). Description: *"No observed discovery degradation in tested regime"*.
3. **Secondary Diagnostic Arm:** `INT8_QUANTIZED_HISTORY` (Post-selection representation stability check only; does not select topology).
4. **Primary Inferential Unit:** `INDEPENDENT_SEED`. All inferential claims evaluated on $N=30$ paired independent seeds (`1311`..`1340`).
5. **Development Screening Arm:** $N=10$ independent seeds (`1301`..`1310`) for implementation debugging and sanity checks, strictly segregated from final evaluation.

---

## 2. Prequential Causal Scoring Protocol

At each time step $t \in \{1..T\}$ ($T=6000$):
1. **Feature Arrival:** $x_t \in \mathbb{R}^D$ is received and transformed via `CausalStandardScaler`.
2. **History Write:** $x_t$ is recorded into `HistoryProvider`.
3. **Prediction Formation:**
   - Compute baseline prediction: $\hat{y}_{t, \text{base}} = w_{\text{base}}^T x_t$.
   - For each active module, compute live prediction: $\hat{y}_{t, \text{live}}$.
   - For all topologies, compute the counterfactual loss grid in shadow mode:
     $$\hat{y}_{\text{BASE}} = \hat{y}_{\text{base}}$$
     $$\hat{y}_{\text{BASE}+D} = \hat{y}_{\text{base}} + \hat{y}_{\text{lag, shadow}}$$
     $$\hat{y}_{\text{BASE}+R} = \hat{y}_{\text{base}} + \hat{y}_{\text{rec, shadow}}$$
     $$\hat{y}_{\text{BASE}+D+R} = \hat{y}_{\text{base}} + \hat{y}_{\text{lag, shadow}} + \hat{y}_{\text{rec, shadow}}$$
4. **Target Revelation:** True scalar $y_t$ is revealed.
5. **Loss Computation & Conditional Gains:**
   $$\ell_t = (y_t - \hat{y}_{t, \text{live}})^2$$
   $$G_{D|B, t} = (y_t - \hat{y}_{\text{BASE}})^2 - (y_t - \hat{y}_{\text{BASE}+D})^2$$
   $$G_{R|B, t} = (y_t - \hat{y}_{\text{BASE}})^2 - (y_t - \hat{y}_{\text{BASE}+R})^2$$
   $$G_{R|B+D, t} = (y_t - \hat{y}_{\text{BASE}+D})^2 - (y_t - \hat{y}_{\text{BASE}+D+R})^2$$
   $$G_{D|B+R, t} = (y_t - \hat{y}_{\text{BASE}+R})^2 - (y_t - \hat{y}_{\text{BASE}+D+R})^2$$
6. **Model Adaptation:** Active and shadow parameters are updated using true error signals.
7. **Lifecycle & Arbitration:** Promotion, retention, and eviction states update.

---

## 3. Success Gate Criteria (Mandatory Advancement Filters)

A topology passes integration evaluation only if it satisfies all 12 pre-registered gates:

- **GATE 1 — Memoryless Safety:**  
  Persistent temporal occupancy on I1 must be $\bar{K} \le 0.05$ active taps, $\bar{S} \le 0.02$ recurrent state.
- **GATE 2 — Static Nonlinear Safety:**  
  On I2, temporal mechanisms must not acquire persistent capacity ($\bar{K} \le 0.10, \bar{S} \le 0.05$). Approximation error must not trigger false temporal escalation.
- **GATE 3 — Discrete Specialization:**  
  On I3 and I4, discrete lag memory must capture $\ge 90\%$ of total predictable temporal gain, with recurrent conditional gain $G_{R|B+D} \le 0.01$.
- **GATE 4 — Recurrent Specialization:**  
  On I6, continuous recurrent state must capture $\ge 90\%$ of predictable temporal gain, with discrete conditional gain $G_{D|B+R} \le 0.01$.
- **GATE 5 — Hybrid Complementarity:**  
  On I9, both modules must achieve statistically significant positive conditional gain ($G_{D|B+R} > 0.01$ and $G_{R|B+D} > 0.01$, $p < 0.01$).
- **GATE 6 — Redundancy Control:**  
  On I10, redundant dual allocation rate must be $\le 5\%$ of evaluation steps.
- **GATE 7 — Order Robustness:**  
  The selected topology must not exhibit fixed order bias ($\rho_{\text{order}} \le 0.05$).
- **GATE 8 — Nonstationary Tracking:**  
  On switching tasks (I11–I13), obsolete modules must be evicted and newly relevant modules promoted within 1,500 steps.
- **GATE 9 — Quiescence Preservation:**  
  Active structures must survive 2,000 steps of silence with $\ge 85\%$ conditional retention on I7 and I8.
- **GATE 10 — Disaggregated Resource Transparency:**  
  All 4 channels (`FP_FLOPS`, `INTEGER_OPS`, `MEMORY_TRAFFIC`, `PERSISTENT_BYTES`) must be fully logged and disaggregated into live vs. shadow rent.
- **GATE 11 — Resource Feasibility:**  
  Mean live compute on single-memory regimes must not exceed 100 FP FLOPs/step; total persistent memory must not exceed 1024 Bytes.
- **GATE 12 — Prequential Integrity:**  
  Audit confirms zero target leakage across all components.

---

## 4. Statistical Testing Policy

- **Primary Unit:** $N=30$ paired independent seeds.
- **Statistical Tests:**
  - Non-parametric Wilcoxon signed-rank test (two-sided, method explicitly declared: exact or asymptotic);
  - 95% paired bootstrap confidence intervals (10,000 resamples);
  - Paired effect size: Cohen's $d_z = \frac{\bar{D}}{s_D}$;
  - Seed-level win rate ($W = \frac{1}{N} \sum_{i=1}^N \mathbb{I}(D_i > 0)$).
- **Prohibition of Pooling:** No aggregation of distinct timesteps, tasks, or candidate events as independent replicates.

---

## 5. Protocol Verification Checksum

This document locks the experimental protocol prior to benchmark code execution.
