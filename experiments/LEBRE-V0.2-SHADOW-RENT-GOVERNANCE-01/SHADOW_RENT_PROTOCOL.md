# Experimental Protocol: Shadow-Rent Governance and Budgeted Counterfactual Scheduling

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Protocol Version:** 1.0 (Frozen Preregistration Standard)  
**Methodological Guidelines:** Simmons et al. (2011), Nosek et al. (2018), Banbury et al. (MLPerf Tiny, 2021)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 21, 2026  
**Status:** SEALED PROTOCOL  

---

## 1. Governance & Environmental Envelope

1. **Governing Architecture:** Canonical LEBRE v0.1 (`CANONICAL_VERSION = 0.1`, `LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`).
2. **Experimental Candidate:** $T_3$ Resource-Aware Conditional Arbitration (`EXPERIMENTAL_NON_CANONICAL`).
3. **Memory Representation:** Sealed FP16 persistent correlation grid with transient FP32 arithmetic (`C1_CANONICAL_FP16`).
4. **Milestone Boundaries:** Milestone M3 remains unopened (`M3_STATUS = UNOPENED`). No novelty claims may be made (`NOVELTY_CLAIM_READY = NO`).
5. **Codebase Immutability:** Canonical files in `src/` (37 files) and `tests/` (124 unit tests) are strictly immutable. All experimental models, schedulers, and harnesses reside strictly in `experiments/` and `scratch/`.

---

## 2. Experimental Arms & Interventions

| Candidate ID | Name | Exploration Cadence | Governing Mechanism | Target Duty Cycle | Expected Total Online FP |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$S_0$** | `CONTINUOUS_SHADOW_REFERENCE` | $100\%$ (Every step) | Canonical $T_3$ with continuous shadow | $1.000$ ($100\%$) | $\approx 167.70$ FLOPs/step |
| **$S_1$** | `SHADOW_OFF_NEGATIVE_CONTROL` | $0\%$ (Disabled) | Live path only; shadow asleep | $0.000$ ($0\%$) | $\approx 81.17$ FLOPs/step |
| **$S_2$** | `PERIODIC_BUDGETED_SHADOW` | $20\%$ (1 in 5 steps)| Static integer period $K=5$ | $0.200$ ($20\%$) | $\approx 98.47$ FLOPs/step |
| **$S_3$** | `EVENT_TRIGGERED_HEARTBEAT` | Adaptive ($\approx 15$–$20\%$) | Page-Hinkley cumulative deviation + heartbeat | $\approx 0.15$–$0.20$ | $\le 100.0$ FLOPs/step |

---

## 3. Benchmark Suite & Task Taxonomy

The primary evaluation suite comprises all 14 frozen canonical benchmark tasks:

1. **Negative Controls:**
   - $I_1$: `I1_Memoryless_Linear` (No temporal dependence)
   - $I_2$: `I2_Static_Nonlinear_Negative_Control` (Static cross-terms)
2. **Pure Discrete Delay Streams:**
   - $I_3$: `I3_Single_Exact_Delay` (Single tap at $k=5$)
   - $I_4$: `I4_Multi_Sparse_Delay` (Sparse taps at $k=3, 11, 27$)
   - $I_5$: `I5_Moving_Delay_Support` (Time-varying delay tap)
   - $I_8$: `I8_Quiescent_Discrete_Delay` (Active tap followed by silence)
3. **Continuous Latent State Streams:**
   - $I_6$: `I6_Continuous_Latent_State` (AR(1) latent state)
   - $I_7$: `I7_Quiescent_Continuous_State` (Latent state followed by silence)
4. **Hybrid Complementary Stream:**
   - $I_9$: `I9_Hybrid_Delay_Plus_Latent_State` (Simultaneous delay and recurrent structure)
5. **Redundant Structure Stream:**
   - $I_{10}$: `I10_Redundant_Temporal_Structure` (Identical information in delay and recurrent pathways)
6. **Non-Stationary Switching Streams:**
   - $I_{11}$: `I11_Regime_Switch_Delay_To_Latent` (Abrupt transition at $t=3,000$)
   - $I_{12}$: `I12_Regime_Switch_Latent_To_Delay` (Abrupt transition at $t=3,000$)
   - $I_{13}$: `I13_Regime_Switch_Hybrid_To_Memoryless` (Abrupt transition at $t=3,000$)
   - $I_{14}$: `I14_Intermittent_Hybrid` (Alternating multi-segment regimes)

---

## 4. Primary Research Hypotheses & Success Gates

### Gate 1: Compute Ceiling Recovery ($H_{\text{RESOURCE}}$)
- **Criterion:** Over the complete 14-task benchmark, mean total online floating-point compute must satisfy:
  $$\mathbb{E}[\text{Total Online FP}] \le 100.0 \text{ FLOPs/step}$$
- **Accounting Invariant:** Total compute must explicitly include live path, mandatory housekeeping, scheduler sentinel evaluation, heartbeat logic, and all shadow executions. Analytical projections alone are invalid; measured execution is mandatory.

### Gate 2: Predictive Non-Inferiority ($H_{\text{PREDICTIVE}}$)
- **Criterion:** At the independent seed level ($N=30$), the paired difference $\Delta_s = \bar{Y}_{s, \text{sched}} - \bar{Y}_{s, S_0}$ must establish non-inferiority within the frozen margin $\Delta_{\text{tol}} \le +0.0100$ NMSE:
  $$\text{Upper 95\% CI}(\Delta) \le +0.0100$$
- **Multiplicity Control:** Holm-Bonferroni correction applied across the primary family ($S_2$ vs $S_0$ and $S_3$ vs $S_0$) at family-wise $\alpha = 0.05$.

### Gate 3: Memory Envelope Compliance ($H_{\text{MEMORY}}$)
- **Criterion:** Peak working memory must remain strictly within the physical budget:
  $$\text{Peak Working Memory} \le 1,024 \text{ Bytes}$$
  $$\text{Persistent Capacity} \le 1,024 \text{ Bytes}$$
- **Allowance:** Total scheduler state must consume $\le 40$ Bytes.

### Gate 4: Switching Latency Preservation
- **Criterion:** On regime switching streams ($I_{11}$–$I_{14}$), the median structural recovery latency increase relative to $S_0$ must satisfy:
  $$\text{Latency}_{\text{sched}} - \text{Latency}_{S_0} \le +50.0 \text{ steps}$$

### Gate 5: Hybrid Complementarity Preservation
- **Criterion:** On $I_9$, the qualitative finding of dual complementary utility ($G_{D|BR} > \theta_{\text{tol}}$ and $G_{R|BD} > \theta_{\text{tol}}$) must survive under duty-cycled exploration.

### Gate 6: Quiescent Reactivation
- **Criterion:** On $I_7$ and $I_8$, the scheduler must sleep efficiently during silence without becoming permanently blind when dynamics reactivate.

---

## 5. Candidate Selection Rule

1. Any candidate failing ANY mandatory gate is immediately disqualified.
2. If only one budgeted candidate satisfies all gates, that candidate is selected.
3. If both $S_2$ and $S_3$ pass all mandatory gates, they are compared via the vector:
   $$\mathbf{v} = \left[\text{Mean Total FP}, \text{Aggregate NMSE}, \text{Post-Change Regret}, \text{Switch Latency}, \text{Persistent Bytes}\right]$$
4. If one strictly Pareto-dominates the other across this vector, it is selected.
5. If neither strictly dominates, the verdict must return `MULTIPLE_VALID_SCHEDULERS` and require human review. No post-hoc weighting or scalar scoring is permitted.
