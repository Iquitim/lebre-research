# PRA-01R: Closest-Combination Analysis & Integration Non-Triviality Audit

**Document ID:** PRA-01R-COMBINATION  
**Author:** Skeptical Literature Reconciler & Architecture Governance Auditor  
**Date:** September 19, 2026  
**Status:** RECONCILIATION COMPLETE — INTEGRATION AUDITED  
**Governing Standard:** Integration Non-Triviality Framework (Sections 55–59, 96)  

---

## 1. The Conceptual Reconstruction Problem

Per Section 56 of the governing protocol:
> *"If Track B can be reconstructed by a simple obvious union of existing methods, architectural distinctiveness may be weak even if no single paper contains the full system."*

To test this vulnerability, we adopt an adversarial posture: we attempt to construct Track B's complete architecture as an additive composite of a minimal set of established prior publications.

---

## 2. Minimal Reconstructing Prior-Art Portfolio

A panel of adversarial reviewers could assemble the following **six-paper portfolio** to argue that every theoretical component of Track B is already published:

```
+-------------------------------------------------------------------------------+
|                      ADVERSARIAL RECONSTRUCTION COMPOSITE                     |
|                                                                               |
|  [1] Recurrent Growth & Pruning         -->  MUSE-RNN (Das et al. 2019)       |
|  [2] Exact Scalar RTRL Credit           -->  CCN (Javed et al. JMLR 2023)     |
|  [3] Maturation & Utility Replacement   -->  Continual Backprop (Nature 2024) |
|  [4] Structural State Importance        -->  AIRE-Prune (Padhy et al. 2026)   |
|  [5] Budgeted Probe Screening           -->  Active Feature Acquisition (2025)|
|  [6] Adaptive Temporal Lag Expansion   -->  Variable-Tap LMS (Zhao et al. 2008)|
+-------------------------------------------------------------------------------+
```

### Detailed Portfolio Mapping:
1. **Component 1 (Recurrent Growth & Eviction):** Supplied by **MUSE-RNN (Das et al. 2019)**. Introduces dynamic creation and pruning of recurrent hidden neurons in response to streaming prediction error.
2. **Component 2 (Online Exact Recurrent Credit):** Supplied by **Columnar-Constructive Networks (Javed et al. 2023)** and **Williams & Zipser (1989)**. Proves that scalar recurrent self-connections allow exact RTRL forward sensitivity updates in $O(1)$ time per unit.
3. **Component 3 (Unit Maturation & Utility Eviction):** Supplied by **Continual Backpropagation (Dohare et al. 2021, 2024)**. Implements unit utility evaluation, unit age counters, and a maturity threshold $m$ protecting newly initialized units from replacement.
4. **Component 4 (State Controllability & Observability):** Supplied by **Balanced Truncation (Moore 1981)** and **AIRE-Prune (Padhy et al. 2026)**. Establishes that state retention should be determined by the product of controllability and observability ($C \times O$).
5. **Component 5 (Budgeted Candidate Screening):** Supplied by **Active Feature Acquisition (Saar-Tsechansky 2009; Guney 2025)**. Implements budgeted exploration and sequential testing before incorporating expensive features.
6. **Component 6 (Dynamic Temporal Lag Expansion):** Supplied by **Variable-Tap LMS (Zhao et al. 2008)**. Increments or decrements temporal filter length based on residual error gradients.

---

## 3. The Additive Combination Failure Experiment (Section 57)

We now address the central question:  
**Is Track B merely a "trivial additive composition" of these six papers?**

If one takes the naive, direct union of these six published methods—instantiating MUSE-RNN's error-growth, CCN's scalar RTRL, Continual Backprop's utility metric ($|w_{\text{out}}| \cdot \mathbb{E}[|h|]$), AIRE-Prune's Hankel metric, and Variable-Tap LMS—**the resulting system fails catastrophically** when subjected to realistic streaming environments.

The Track-B empirical development program (M1 through M2-R1) revealed that a naive additive combination suffers from five fatal interaction breakdowns:

### Breakdown 1: The "Newborn Shock" Breakdown (Discovered in M2-EXP-0002)
- *The Naive Union:* MUSE-RNN and RSONN add newly generated units directly into the active forward prediction loop. Continual Backprop uses a maturity threshold $m$, but the unit is already part of the forward pass.
- *The Empirical Failure:* In streaming autoregressive forecasting, newly initialized recurrent parameters have random or zero-initialized weights. Injecting them directly into the primary prediction path causes an immediate, massive transient regret spike ($+340\%$ regret overshoot) before parameters can adapt.
- *The Track B Resolution:* A decoupled **probationary shadow bank** where candidate states execute RTRL in shadow mode without downstream prediction authority, graduating to active status *only* if probationary error reduction proves statistically significant ($\ge 15\%$).

### Breakdown 2: The Quiescent Memory Annihilation Breakdown (Discovered in M2-EXP-0004)
- *The Naive Union:* Continual Backprop defines utility as $U_i = |w_{out, i}| \cdot \mathbb{E}[|h_i|]$; MUSE-RNN uses $|h_t| \cdot |w_{out}|$. AIRE-Prune uses batch Gramians calculated over complete offline trajectories.
- *The Empirical Failure:* In streaming event-driven sequences (e.g., SET/RESET, Poisson cues, credit scoring), long silent gaps occur where input excitation ceases. During these gaps, $x_t \approx 0 \implies s_t \approx 0$. Continual Backprop's and MUSE-RNN's utility metrics collapse to zero. The model interprets this silence as obsolescence and immediately prunes the state. When the recall cue finally arrives, the stored memory is gone, causing catastrophic forgetting.
- *The Track B Resolution:* A causal, **two-timescale structural observability metric** ($O_{\text{struct}}$) that evaluates the transfer impulse energy of the recurrent parameters rather than the instantaneous activation magnitude, preserving silent states across arbitrary temporal gaps.

### Breakdown 3: The Asymmetric Eviction Catastrophe (Discovered in M2-EXP-0005)
- *The Naive Union:* Pruning in MRAN, RSONN, and Continual Backprop is symmetric: units are evicted as soon as utility drops below a threshold $\theta_{\text{prune}}$.
- *The Empirical Failure:* Empirical measurement revealed that the cost of premature eviction ($C_{\text{FE}}$) is more than **300 times higher** than the cost of stale retention ($C_{\text{FR}}$). Prematurely evicting a valid recurrent state forces the system through re-probation, re-initialization, and re-convergence, incurring catastrophic cumulative regret.
- *The Track B Resolution:* **Asymmetric hysteresis and positive obsolescence confirmation** ($O_{\text{obs}}$). A state is never evicted merely because utility is low; it requires confirmed, persistent zero-excitation across a statistically grounded confirmation window.

### Breakdown 4: The Lag-vs-State Boundary Breakdown (Discovered in M2-EXP-0001)
- *The Naive Union:* Variable-Tap LMS expands taps indefinitely; RCC adds recurrent units indiscriminately.
- *The Empirical Failure:* If a temporal dependency can be solved by a finite delay tap ($x_{t-d}$), allocating a recurrent state is wasteful (consumes state memory and introduces stability risks). Conversely, if the dependency spans an unknown, non-stationary long horizon, expanding explicit taps causes an explosion in probe budget and FLOPs.
- *The Track B Resolution:* A strict, empirically governed **parsimonious escalation boundary**: explicit temporal lags are probed first under a rigid budget $O(K_{\max}+Q)$; recurrent state allocation is triggered *only* when the lag exploration frontier ceases to reduce autocorrelation residuals.

### Breakdown 5: The Linear-First Parsimony Breakdown (Discovered in M2-EXP-0006)
- *The Naive Union:* Recurrent learners default to non-linear cells (tanh/LSTM/GRU).
- *The Empirical Failure:* Gated non-linear cells introduce multiple parameter sensitivities, non-convex gradient dynamics, and higher FLOP costs. On linear autoregressive drift, gated cells exhibit slower convergence and higher parameter variance than simple linear recurrence.
- *The Track B Resolution:* **Linear-first parsimony**. Linear recurrence is tested first; non-linear gated recurrence is instantiated only if linear probation fails by an empirical margin.

---

## 4. Formal Integration Classification (Sections 58 & 96)

Per Section 58 and Section 96, we evaluate the four candidate classifications:
1. `TRIVIAL_COMPOSITION`: The combination is an obvious, straightforward union of existing algorithms without novel interaction constraints.
2. `NONTRIVIAL_ENGINEERING_COMPOSITION`: The combination requires significant engineering effort to glue disparate software libraries together, but the algorithms function independently without modifying their governing principles.
3. `NONTRIVIAL_EMPIRICALLY_DERIVED_ORGANIZATION`: The combination addresses fundamental physical and statistical incompatibilities between components that only manifest when operating simultaneously in streaming environments. The governing rules (probationary shadow paths, two-timescale quiescent protection, asymmetric loss confirmation, parsimonious escalation) were derived through systematic empirical failure analysis.
4. `UNRESOLVED`: Evidence is insufficient to determine integration status.

### Reconciled Verdict:
$$\mathbf{INTEGRATION\_STATUS = NONTRIVIAL\_EMPIRICALLY\_DERIVED\_ORGANIZATION}$$

### Rigorous Justification:
- Track B is **not a trivial composition** because a direct union of MUSE-RNN, CCN, and Continual Backprop fails on standard Poisson-quiescent benchmarks due to catastrophic premature eviction and newborn shock.
- Track B is **not merely an engineering composition** because the solutions were not software interface wrappers; they required formulating new mathematical interaction constraints:
  - Defining structural observability decoupled from instantaneous state activation;
  - Formulating positive obsolescence counters calibrated against a 300:1 empirical loss asymmetry;
  - Structuring a two-tier parsimony test (linear-first vs gated).
- **Critical Disclaimer (Section 59):**  
  > *This classification is NOT a novelty claim. It describes architectural coherence and the presence of non-obvious interaction engineering, but does not substitute for empirical superiority. External benchmarking against these baselines remains mandatory.*
