# CAR_01_CONTRIBUTION_DECOMPOSITION.md — Layered Scientific Contribution Decomposition

**Protocol:** CAR-01  
**Milestone:** Contribution Assessment Review  
**Date:** September 19, 2026  
**Status:** Frozen Single-State Core Analysis  

---

## 1. Scientific Objective and Decomposition Framework

To determine the minimum scientifically defensible contribution of the frozen Track-B organization without overclaiming novelty, we partition the system into four analytical layers:
- **Layer 1: Known Primitives** (mathematical equations and standard online algorithms established in prior literature).
- **Layer 2: Known Mechanisms Used in a New Context** (techniques borrowed from adjacent domains such as control theory, feature selection, or bandit algorithms applied to recurrent stream learning).
- **Layer 3: Empirically Derived Interaction Logic** (specific couplings, thresholds, and transition policies developed directly to resolve observed failure modes).
- **Layer 4: Architectural Organization** (the overarching resource-governed structural lifecycle coordinating heterogeneous adaptive structures).

---

## 2. Layer 1 — Known Primitives

Every mathematical primitive operating in Track B is individually established in prior literature. No novelty is claimed for any primitive in this layer:

1. **Exact Scalar Real-Time Recurrent Sensitivity (RTRL):**
   - *Mathematical Formulation:* Accumulation of $\Lambda_t = \frac{\partial h_t}{\partial \theta} = \alpha \Lambda_{t-1} + h_{t-1}$ for feedback parameters.
   - *Prior Art:* Williams & Zipser (1989), *Neural Computation*; Jaeger (2002).
   - *Status:* **KNOWN_STANDARD**.

2. **Sparse Normalized Least Mean Squares (NLMS / $\ell_1$-regularized LMS):**
   - *Mathematical Formulation:* Normalized gradient step $\mu_t = \frac{\mu}{\|x_t\|_2^2 + \epsilon}$ combined with soft-threshold zero-attracting regularization.
   - *Prior Art:* Chen et al. (2009); Nagumo & Noda (1967).
   - *Status:* **KNOWN_STANDARD**.

3. **Running Parameter Utility and Gradient-Variance Traces:**
   - *Mathematical Formulation:* Exponential moving averages of parameter magnitude and contribution $\Delta U_t = |w_t| \cdot |\nabla_w \mathcal{L}_t|$.
   - *Prior Art:* Sutton (1988); Dohare et al. (Nature 2024, *Continual Backpropagation*).
   - *Status:* **KNOWN_STANDARD**.

4. **Maturation Protection Counters (Probation Windows):**
   - *Mathematical Formulation:* Counter $t_{\text{age}} < T_{\text{mature}}$ rendering newly initialized weights immune to pruning.
   - *Prior Art:* Fahlman & Lebiere (1990, *Cascade-Correlation*); Dohare et al. (2024).
   - *Status:* **KNOWN_STANDARD**.

5. **Structural Growth and Pruning Thresholds:**
   - *Mathematical Formulation:* Comparing running residual error against growth threshold $\theta_{\text{grow}}$ and parameter utility against eviction threshold $\theta_{\text{prune}}$.
   - *Prior Art:* Platt (1991, *Resource Allocating Networks*); RSONN (2017).
   - *Status:* **KNOWN_STANDARD**.

6. **Adaptive Filter Tap Length Adjustments:**
   - *Mathematical Formulation:* Expanding or shrinking FIR tap length based on trailing weight magnitudes.
   - *Prior Art:* Zhao, Man, & Khoo (2008, *Variable-tap LMS*).
   - *Status:* **KNOWN_STANDARD**.

---

## 3. Layer 2 — Known Mechanisms Used in a New Context

This layer identifies mechanisms that are established in external fields but repurposed within Track B to address recurrent streaming challenges:

1. **Controllability and Observability Gramian Proxies for Quiescent State Retention:**
   - *Context:* Derived from linear systems theory and balanced truncation (Moore, 1981, *IEEE TAC*; AIRE/LAST, 2024).
   - *New Use in Track B:* Instead of performing model order reduction on an offline transfer function, Track B computes an online recursive scalar proxy of reachability ($\mathcal{P}_t = \lambda \mathcal{P}_{t-1} + x_t^2$) and observability ($\mathcal{Q}_t = \lambda \mathcal{Q}_{t-1} + w_{\text{out}}^2$) to protect dormant recurrent states during zero-input intervals.
   - *Status:* **KNOWN_BUT_REPURPOSED**.

2. **Non-Interfering Shadow Probation for Recurrent State Candidates:**
   - *Context:* Derived from active feature acquisition and multi-armed bandit shadow testing.
   - *New Use in Track B:* A candidate recurrent state is instantiated in a parallel "shadow buffer" where its sensitivities and parameters update, but its output is disconnected from the active model until empirical correlation indicates error reduction over a statistical window.
   - *Status:* **KNOWN_BUT_REPURPOSED**.

3. **Economic Rent Imposition per Computational Parameter:**
   - *Context:* Derived from economic resource allocation and Minimum Description Length (MDL) principles (Rissanen, 1978).
   - *New Use in Track B:* Each active parameter pays an explicit continuous "rent" deduction against its accumulated utility ($U_t \leftarrow U_t - c_{\text{rent}}$) directly tied to its FLOP and memory cost.
   - *Status:* **KNOWN_BUT_REPURPOSED**.

---

## 4. Layer 3 — Empirically Derived Interaction Logic

This layer documents the specific coordination policies developed across Milestones M1 and M2 to overcome empirical failure modes when simpler mechanisms interacted:

| Interaction ID | Observed Failure Mode | Earlier Experiment | Mechanism Introduced | Causal / Ablation Evidence | Final Frozen Role | External Benchmark Support | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **INT-1: Newborn Shock** | Initializing candidate recurrent state directly into output layer caused catastrophic transient error spikes. | M2-EXP-0001 | Non-interfering shadow probe validation buffer. | Direct insertion produced 4.8× higher transient MSE than shadow probing (p < 1e-6). | Decouples candidate evaluation from live prediction until evidence of utility. | Prevented transient error spikes on regime shifts in A8 and B2. | **EMPIRICALLY_DERIVED_COMBINATION** |
| **INT-2: Premature Eviction** | High initial gradient noise caused newborn units to be evicted before learning stable representations. | M2-EXP-0002 | Maturation probation counter ($T_{\text{mature}} = 200$ steps). | Ablation without probation resulted in 86% of viable recurrent states evicted within 15 steps. | Provides temporary immunity to allow convergence of feedback sensitivities. | Critical for survival of recurrent units under continuous streaming. | **KNOWN_STANDARD** |
| **INT-3: Quiescent Annihilation** | Standard utility decay evicted dormant states during long zero-signal pauses, destroying burst memory. | M2-EXP-0003 | Two-timescale structural Gramian tracking ($O_{\text{struct}}$ vs $O_{\text{obs}}$). | Single-timescale decay lost 100% of dormant states on A5/A7; dual-timescale retained 100%. | Decouples signal activity tracking from structural necessity. | Preserved memory on A5 (Intermittent Burst) and A7 (Poisson Gaps). | **EMPIRICALLY_DERIVED_COMBINATION** |
| **INT-4: Linear-First Escalation** | Spurious recurrent state birth on pure linear shifts increased FLOPs without improving accuracy. | M2-EXP-0004 | Strict hierarchical gating: sparse linear adaptation precedes recurrent escalation. | Forcing recurrent growth on A1 increased FLOPs by 2.3× with 0% NMSE improvement. | Restricts recurrent container allocation to unresolved residual autocorrelation. | Maintained 76.8 FLOPs on linear regime of A8, scaling only when needed. | **EMPIRICALLY_DERIVED_COMBINATION** |
| **INT-5: Asymmetric Eviction Cost** | Evicting a necessary state incurred a massive retraining latency penalty, triggering destructive churn. | M2-EXP-0005r | Positive obsolescence confirmation with 300:1 false-eviction loss weighting. | Equal-weighted eviction caused 34 churn cycles; 300:1 weighting reduced churn to zero. | Enforces strict statistical evidence of persistent disutility before structural destruction. | Ensured zero divergence across all 450 evaluation runs in BENCH-01B. | **POSSIBLY_DISTINCT** |
| **INT-6: Physical Resource Reclamation** | Masking unused parameters retained full compute/memory cost, violating strict micro-resource budgets. | M1-EXP-0008 | Physical buffer slice deallocation and loop-bound contraction upon state eviction. | Profiling confirmed FLOPs immediately dropped from 94.6 to 76.8 upon state deallocation. | Enforces hard sub-100-FLOP operation by zeroing compute cost of obsolete units. | Passed R2-FLOP (mean 90.44) and R2-MEM (440 bytes) across all 15 workloads. | **EMPIRICALLY_DERIVED_COMBINATION** |

---

## 5. Layer 4 — Architectural Organization

### 5.1 The Common Structural Lifecycle
Track B coordinates its structural components through a formal state machine:

$$\text{DORMANT} \longrightarrow \text{PROVISIONAL} \longrightarrow \text{ACTIVE} \longrightarrow \text{MATURE} \longrightarrow \text{OBSOLESCENCE\_CONFIRMATION} \longrightarrow \text{EVICTED}$$

```
   [ Residual Error > Theta_grow ]
DORMANT -------------------------> PROVISIONAL (Shadow Buffer)
                                       |
                                       | [ Correlation Confirmed & U > Rent ]
                                       v
                                    ACTIVE (Coupled to Output)
                                       |
                                       | [ t_age >= T_mature ]
                                       v
                                    MATURE (Full Economic Rent)
                                       |
                                       | [ Sustained Disutility & O_struct Decayed ]
                                       v
                                 CONFIRM_OBSOLESCENCE (300:1 Penalty Guard)
                                       |
                                       | [ Irreversible Evidence of Zero Utility ]
                                       v
                                    EVICTED (Physical Resource Reclaimed)
```

### 5.2 Multi-Object Unification Verification
Does this lifecycle apply with genuine mechanistic correspondence across:
1. **Observable Feature Taps** ($x_{t, i}$),
2. **Temporal Delay Lags** ($x_{t-k}$),
3. **Internal Recurrent States** ($h_t$)?

**Mechanistic Audit:**
- **Observable Features:** Inactive input features reside in DORMANT state; enter PROVISIONAL state via gradient correlation probing; transition to ACTIVE and MATURE; face eviction via soft-threshold rent deductions.
- **Temporal Lags:** Potential delay indices $k$ are probed in shadow registers; enter ACTIVE status when lag correlation reduces residual variance; pay per-tap memory rent; evicted upon obsolescence.
- **Recurrent State:** A candidate 1D scalar state ($h_t$) enters shadow probation; matures under parameter protection; pays compute rent; requires 300:1 asymmetric obsolescence confirmation before eviction.

### 5.3 Primary C10 Evaluation
> *Does evidence support treating features, lags, and recurrent state as instances of a more general class: COST-BEARING ADAPTIVE COMPUTATIONAL STRUCTURE?*

**Verdict: YES**

The structural object schema formalizes this common abstraction:
```
STRUCTURAL_OBJECT j:
  state:               { DORMANT, PROVISIONAL, ACTIVE, MATURE, EVICTED }
  cost (c_j):          Operational FLOPs/step and memory bytes allocated
  evidence (E_j):      Correlation between candidate activation and current residual
  utility (U_j):       Running dual-metric contribution trace
  retention (R_j):     Structural Gramian / observability proxy
  obsolescence (O_j):  Accumulated evidence of disutility relative to rent
  resource (B_j):      Hard physical slice in persistent state memory
```

---

## 6. Resource-Governed Structural Learning Definition

Track B implements **Resource-Governed Structural Learning**, defined as:
> *"A streaming learning framework in which computational mechanisms (features, delays, recurrent states) are modeled as cost-bearing adaptive objects whose investigation, activation, retention, and removal are jointly controlled by online evidence and explicit operational resource constraints."*

Track B genuinely satisfies this definition because:
1. Structural mutations are not driven solely by loss gradients, but by cost-benefit trade-offs against explicit maintenance rent ($c_j$).
2. Resource reclamation is physical: deallocation contractually lowers computational FLOPs and memory footprint.
3. Complexity escalates strictly on demand: from sparse linear to scalar recurrence, remaining within a rigid sub-100-FLOP micro-resource budget.

---

## 7. Integration Classification

How should this total organization be scientifically classified?
- A. Learning rule? **NO** (incorporates multiple rules and structural policies).
- B. Algorithm? **NO** (coordinates multiple asynchronous lifecycle processes).
- C. Adaptive mechanism? **NO** (broader than a single mechanism).
- D. Architectural organization? **YES**.
- E. Resource-governance framework? **YES**.

**Final Classification: NONTRIVIAL_EMPIRICALLY_DERIVED_ARCHITECTURE (Hybrid of D + E).**

The system cannot be reduced to a single mathematical update equation. It is a persistent organization of computational information flow, parameter lifecycles, and physical resource governance.
