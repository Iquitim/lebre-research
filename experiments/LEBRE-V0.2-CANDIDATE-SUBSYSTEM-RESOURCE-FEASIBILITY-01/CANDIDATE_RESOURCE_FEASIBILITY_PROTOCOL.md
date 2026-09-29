# Experimental Protocol: Candidate Subsystem Resource Feasibility
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Authority Level: Level 4 (Active Experimental Protocol)

---

## 1. Protocol Purpose & Scope

The purpose of this study is to determine whether the complete candidate discovery, probation, and evaluation subsystem contains sufficient theoretically removable computational work to justify a new stochastic experimental stage (`LEBRE-V0.2-CANDIDATE-PROBATION-COST-01`).

### Scope Boundaries & Invariants:
1. **No New Stochastic Streams:** No new simulations, benchmark runs, or random seeds are permitted. All analyses are deterministic and derived from sealed Level 1 data.
2. **Canonical Codebase Immutability:** `src/` and `tests/` remain 100% frozen.
3. **Search Space Invariants:** The search frontier parameters ($H = 32, B = 4, K_{\text{probe}} = 2$) and circular queue sweep order are frozen.
4. **Multirate Clocks Invariant:** Candidate observation cadence ($K_{\text{obs}} = 5$), candidate learning cadence ($K_{\text{learn}} = 10$), recurrent cadences, and arbitration cadences are frozen.
5. **Promotion Criterion Invariant:** The utility threshold $\theta_{\text{promote}}$ and probation horizon ($T_{\text{prob}} = 15$ shadow observations) remain frozen.
6. **Eviction Out of Scope:** Mature retention, quiescence, and structural eviction mechanisms are strictly out of scope.

---

## 2. Resource Accounting Bounds & Feasibility Framework

### 2.1 The 100 FP/step Resource Gap
- **Target Online Compute:** $\text{Target}_{\text{FP}} = 100.000000\text{ FP/step}$.
- **Current Empirical Mean ($M_1^*$):** $\text{Current}_{\text{FP}} = 111.013591\text{ FP/step}$.
- **Required Compute Saving:**
  $$\Delta_{\text{req}} = \text{Current}_{\text{FP}} - \text{Target}_{\text{FP}} = \mathbf{11.013591\text{ FP/step}}$$

### 2.2 Three Savings Ceilings
1. **Impossible Oracle Ceiling ($\text{Bound}_{\text{oracle}}$):**
   - Assumes that *all* operations causally attributable to the candidate subsystem (direct observation, parameter learning, counterfactual loss, and descendant arbitration) are eliminated or cost zero FLOPs.
   - Purpose: Establish the mathematical maximum possible leverage of the candidate subsystem.
2. **Semantically Mandatory Floor ($\text{Bound}_{\text{semantic}}$):**
   - Retains all operations logically required to maintain the existence of candidate testing (discovery, minimum observation, counterfactual scoring, and promotion decision), subtracting only failed probation waste.
   - Purpose: Quantify the upper bound achievable without disabling structural discovery.
3. **Plausible Engineering Bound ($\text{Bound}_{\text{retrospective}}$):**
   - Evaluates retrospective zero-false-negative early rejection on existing candidate traces.
   - Purpose: Determine whether real candidates can be safely separated from failures early in their lifecycle.

### 2.3 Feasibility Ratios & Decision Logic
For each bound $i \in \{\text{oracle}, \text{semantic}, \text{retrospective}\}$:
$$\text{Closure Ratio}_i = \frac{\text{Saving}_i}{\Delta_{\text{req}}}$$
$$\text{Residual Compute}_i = \text{Current}_{\text{FP}} - \text{Saving}_i$$

- **Mathematical Infeasibility Condition:**
  If $\text{Bound}_{\text{oracle}} < \Delta_{\text{req}}$, then:
  $$\mathbf{CANDIDATE\_SUBSYSTEM\_CAN\_CLOSE\_100FP\_GAP = MATHEMATICALLY\_NO}$$
  $$\mathbf{CANDIDATE\_PROBATION\_COST\_STAGE\_AUTHORIZED = NO}$$
- **Authorization Condition:**
  A future experimental stage (`LEBRE-V0.2-CANDIDATE-PROBATION-COST-01`) is authorized if and only if:
  1. The candidate subsystem has sufficient plausible leverage ($\text{Closure Ratio} \ge 1.0$ or $>2.0\text{ FP/step}$ safety margin below 100);
  2. Retrospective trajectories show early-decision separability with zero false rejection of useful candidates;
  3. A future online rule can be designed without privileged knowledge or prohibitive computational overhead.

---

## 3. Retrospective Diagnostics Discipline

All retrospective early-stopping and futility curves constructed in this stage are **feasibility diagnostics only**. They must never be used to train an empirical decision threshold that is subsequently evaluated on the same confirmatory cohort. Any future deployable decision rule requires design on separate DEV tasks and confirmation on fresh seeds.
