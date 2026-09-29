# LEBRE-V0.2-INTEGRATION-DESIGN-01: Scientific Hypotheses & Falsification Criteria
## Formal Pre-Registered Hypotheses for Representational Escalation, Arbitration & Structural Interference

**Document ID:** `LEBRE-V0.2-HYP-2026-v1.0`  
**Status:** `PRE-REGISTERED_SCIENTIFIC_HYPOTHESES`  
**Phase:** Integration Design & Structural Arbitration  
**Lead Evaluator:** Skeptical Senior ML Systems Researcher, Adaptive-Filtering Specialist  

---

## 1. Executive Formulation

This document defines the 9 core scientific hypotheses governing the integration of instantaneous linear representation ($L$), sparse discrete lag memory ($D$), and continuous recurrent latent state ($R$) within the LEBRE streaming architecture. Each hypothesis is paired with strict quantitative falsification criteria and statistical tests evaluated on $N=30$ independent paired seeds.

---

## 2. Formal Hypotheses & Falsification Criteria

### H1 — Representational Specialization
- **Formal Statement:**  
  Discrete lag memory will dominate conditional predictive gain on pure discrete delay tasks (I3, I4), while continuous recurrent memory will dominate conditional predictive gain on continuous latent-state tasks (I6). Neither mechanism is a substitute for the other in its native domain.
- **Operational Metric:**  
  On I3/I4: $E[G_{D|B}] \gg E[G_{R|B}]$ and $E[G_{R|B+D}] \approx 0$.  
  On I6: $E[G_{R|B}] \gg E[G_{D|B}]$ and $E[G_{D|B+R}] \approx 0$.
- **Falsification Threshold:**  
  Falsified if recurrent state achieves $\ge 80\%$ of lag gain on multi-sparse delays (I4), OR if discrete lags achieve $\ge 80\%$ of recurrent gain on continuous latent state (I6).

---

### H2 — Hybrid Complementarity
- **Formal Statement:**  
  On composite hybrid systems (I9) where the data generating process contains both an unobserved discrete transport delay and a continuous latent dynamical state, both memory classes will retain statistically significant, durable positive conditional gain when controlling for the other:
  $$E[G_{D|B+R}] > \Delta_{\text{equiv}} \quad \text{AND} \quad E[G_{R|B+D}] > \Delta_{\text{equiv}}$$
- **Operational Metric:**  
  Paired prequential gain of the joint model relative to both single-memory models:
  $$\Delta_{\text{hybrid vs lag}} = \ell_{B+D} - \ell_{B+D+R} > 0$$
  $$\Delta_{\text{hybrid vs rec}} = \ell_{B+R} - \ell_{B+D+R} > 0$$
- **Falsification Threshold:**  
  Falsified if either $G_{D|B+R} \le 0.01$ or $G_{R|B+D} \le 0.01$ on task I9 across $N=30$ seeds ($p > 0.01$, Wilcoxon signed-rank).

---

### H3 — Fixed Order Bias in Cascades
- **Formal Statement:**  
  Evaluating structural capacity in a fixed sequential order (e.g. Linear $\to$ Lag $\to$ Recurrent in T1 vs. Linear $\to$ Recurrent $\to$ Lag in T1R) induces an order bias that distorts structural allocation: the upstream module absorbs shared residual variance, suppressing the downstream module.
- **Operational Metric:**  
  Order Sensitivity Rate ($\rho_{\text{order}}$): the proportion of seeds where T1 and T1R converge to materially different persistent structural allocations on ambiguous or redundant tasks (I10):
  $$\rho_{\text{order}} = \frac{1}{N} \sum_{s=1}^N \mathbb{I}(\text{Alloc}_{\text{T1}}(s) \ne \text{Alloc}_{\text{T1R}}(s))$$
- **Falsification Threshold:**  
  Falsified (i.e. order bias is absent) if $\rho_{\text{order}} \le 0.05$ across redundant and switching benchmarks.

---

### H4 — Symmetric Evidence Eliminates Order Bias
- **Formal Statement:**  
  Evaluating lag and recurrent candidates in parallel shadow mode against the *same* baseline residual (Topology T2 and T3) eliminates order bias, producing invariant allocation independent of candidate evaluation ordering.
- **Operational Metric:**  
  Disagreement rate between parallel shadow evidence and oracle model requirements.
- **Falsification Threshold:**  
  Falsified if symmetric shadow competition exhibits order sensitivity $\rho_{\text{order}} > 0.05$ when candidate evaluation order is shuffled.

---

### H5 — Resource-Aware Arbitration Controls Redundancy
- **Formal Statement:**  
  Conditioning structural promotion on both conditional marginal gain ($G_{D|B+R}, G_{R|B+D}$) and Pareto resource dominance (Topology T3) strictly reduces redundant dual allocation compared to unconstrained parallel addition (O_ALL) on redundant tasks (I10), without increasing predictive NMSE beyond $\Delta_{\text{equiv}}$.
- **Operational Metric:**  
  Redundant Dual Allocation Rate ($\rho_{\text{dual, I10}}$):
  $$\rho_{\text{dual}} = \text{Fraction of steps where BOTH modules are active on task I10}$$
- **Falsification Threshold:**  
  Falsified if T3 allocates dual capacity on task I10 in $\ge 20\%$ of evaluation steps, OR if T3 incurs a prediction regret $\Delta_{\text{NMSE}} > 0.05$ relative to O_ALL.

---

### H6 — No False Temporal Escalation on Static Non-Linearity
- **Formal Statement:**  
  On memoryless controls (I1) and static nonlinear negative controls (I2), neither temporal mechanism will acquire persistent capacity merely because the linear baseline exhibits steady-state approximation error. Model inadequacy must not be misclassified as temporal memory requirement.
- **Operational Metric:**  
  Temporal False Promotion Rate ($\rho_{\text{FP}}$) and mean persistent temporal occupancy on I1 and I2:
  $$\bar{K}_{\text{active}} \le 0.10 \quad \text{AND} \quad \bar{S}_{\text{active}} \le 0.05$$
- **Falsification Threshold:**  
  Falsified if either discrete taps or recurrent state remain persistently active for $> 100$ steps on task I2 in $> 10\%$ of evaluation seeds.

---

### H7 — Non-Stationary Regime Tracking
- **Formal Statement:**  
  When the data generating process undergoes an unannounced regime shift (I11: discrete delay $\to$ continuous state; I12: continuous state $\to$ discrete delay; I13: hybrid $\to$ memoryless), the architecture will retire the obsolete structure and discover/promote the newly relevant structure within finite prequential latency.
- **Operational Metric:**  
  Retirement Latency ($\tau_{\text{retire}}$) and Discovery Latency ($\tau_{\text{discover}}$) measured in post-transition steps.
- **Falsification Threshold:**  
  Falsified if mean transition recovery exceeds 1,500 steps, or if the obsolete module fails to be evicted within 2,500 steps post-shift.

---

### H8 — Preservation of Quiescent Retention
- **Formal Statement:**  
  Integrating recurrent and discrete lifecycle mechanisms preserves the two-timescale quiescent gating validated in `DYNAMIC-LAG-LIFECYCLE-01A`: during channel silence (I7, I8), previously promoted active structures are shielded from eviction and achieve $\ge 85\%$ survival upon signal resumption.
- **Operational Metric:**  
  Quiescent Tap Retention Rate ($\rho_{\text{quiesc}}$) across 4,000 steps of zero-input silence.
- **Falsification Threshold:**  
  Falsified if conditional retention of active taps falls below $85\%$ on task I8, or if post-quiescence NMSE increases by $> 20\%$ compared to the pre-quiescent baseline.

---

### H9 — Integrated Resource Feasibility
- **Formal Statement:**  
  The primary selected integration topology evaluated with `FP16_EXACT_ADDRESSABLE_RING` satisfies the legacy resource constraints on single-memory regimes:
  $$\text{Mean Live FP FLOPs} \le 100 \quad \text{AND} \quad \text{Persistent RAM} \le 1024 \text{ Bytes}$$
  When both memory modules are active simultaneously in the hybrid regime (I9), the live execution footprint is explicitly bounded and does not exceed $150$ FP FLOPs and $512$ Bytes RAM.
- **Operational Metric:**  
  4-channel resource trace $[\text{FP\_FLOPS}, \text{INT\_OPS}, \text{MEM\_TRAFFIC}, \text{RAM}]$ measured at mean, P95, and peak steps.
- **Falsification Threshold:**  
  Falsified if live mean compute exceeds 100 FP FLOPs on single-memory tasks, or if persistent memory exceeds 1024 Bytes on any task.

---

## 3. Pre-Registration Summary Matrix

| Hypothesis | Key Metric | Target / Expectation | Falsification Boundary | Success Gate Link |
| :--- | :--- | :--- | :--- | :--- |
| **H1: Specialization** | Domain Conditional Gain Ratio | $G_{D} \gg G_{R}$ (I3/I4), $G_{R} \gg G_{D}$ (I6) | Cross-domain overlap $\ge 80\%$ | Gate 3 & Gate 4 |
| **H2: Hybrid Complementarity** | Joint Conditional Gain | $G_{D|B+R} > 0.01$, $G_{R|B+D} > 0.01$ | Either conditional gain $\le 0.01$ | Gate 5 |
| **H3: Fixed Order Bias** | Order Sensitivity Rate $\rho_{\text{order}}$ | $\rho_{\text{order}} \ge 0.25$ for T1 vs T1R | $\rho_{\text{order}} \le 0.05$ | Gate 7 |
| **H4: Symmetric Robustness** | Symmetric Order Invariance | $\rho_{\text{order}} = 0.00$ for T2/T3 | $\rho_{\text{order}} > 0.05$ | Gate 7 |
| **H5: Redundancy Control** | Redundant Dual Allocation Rate | $\rho_{\text{dual, I10}} \le 0.05$ for T3 | $\rho_{\text{dual, I10}} \ge 0.20$ | Gate 6 |
| **H6: Nonlinear Safety** | False Temporal Occupancy | $\bar{K}_{\text{active}} = 0.00, \bar{S}_{\text{active}} = 0.00$ | Persistent occupancy $> 100$ steps | Gate 1 & Gate 2 |
| **H7: Regime Tracking** | Transition Latency | $\tau_{\text{retire}} \le 1000, \tau_{\text{discover}} \le 800$ | Recovery $> 1500$ steps | Gate 8 |
| **H8: Quiescent Retention** | Silence Survival Rate | $\rho_{\text{quiesc}} \ge 85\%$ on I7/I8 | Survival $< 85\%$ | Gate 9 |
| **H9: Resource Feasibility** | 4-Channel Vector Footprint | $\le 100$ FP FLOPs, $\le 1024$ B RAM | $> 100$ FP FLOPs (single memory) | Gate 10 & Gate 11 |
