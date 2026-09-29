# Operational Metric Dictionary: Temporal Allocation & Redundancy on Task $I_{10}$

**Audit Identifier:** `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Focus:** Exact Semantics, Numerators, Denominators, Windows, and Lineage for Co-Allocation Metrics on Task $I_{10}$ (Redundant Temporal Structure)  
**Author:** Independent Skeptical Scientific Auditor  
**Date:** September 2026  

---

## 1. Context & Need for Disambiguation

In the parent study `LEBRE-V0.2-INTEGRATION-DESIGN-01` and previous audit documents, multiple terms were used interchangeably:
- "Redundant Dual Allocation Rate"
- "Dual Occupancy Rate"
- "Co-allocation Frequency"
- "Double Payment Rate"
- `frac_both`
- `redundant_dual_rate`

This semantic blurring created severe ambiguity: $T_2$ was simultaneously described as having a "48.2% redundant dual allocation rate" while its confirmatory output shows `frac_both = 1.000` (100% steady-state dual occupancy) and `redundant_dual_rate = 0.0015` (0.15% thresholded redundant steps).

This document establishes the authoritative mathematical and software definitions of every related metric.

---

## 2. Definitional Taxonomy & Formulas

### 2.1 Metric 1: Steady-State Dual Occupancy Rate (`frac_both`)
- **Code Symbol:** `frac_both` in `LEBRE_V0_2_SEED_RESULTS.csv` (line 643 of `run_v02_integration_experiments.py`).
- **Mathematical Formula:**
  $$\text{frac\_both} = \frac{1}{T_{\text{eval}}} \sum_{t=T_{\text{warmup}}+1}^{T} \mathbb{I}(\text{AllocatedState}_t == \text{"BOTH"})$$
  where:
  - $\text{AllocatedState}_t == \text{"BOTH"} \iff (\text{len}(\text{active\_taps}_t) > 0) \land (\text{active\_rec}_t \ne \text{None})$;
  - Evaluation Window: Steady-state timesteps $t \in [1000, 6000)$ ($T_{\text{warmup}} = 1000, T = 6000$);
  - Denominator: $T_{\text{eval}} = 5,000$ steps;
  - Numerator: Count of evaluation steps where both module classes are simultaneously active.
- **Physical Meaning:** The proportion of mature evaluation time where the model maintains both discrete delay taps and a continuous recurrent unit on the live prediction path.
- **Topology Applicability:** Universal across all topologies ($T_1, T_{1R}, T_2, T_3, O_{\text{ALL}}$).

### 2.2 Metric 2: Thresholded Redundant Dual Rate (`redundant_dual_rate`)
- **Code Symbol:** `redundant_dual_rate` in `LEBRE_V0_2_SEED_RESULTS.csv` (lines 553–557 and line 667 of `run_v02_integration_experiments.py`).
- **Mathematical Formula:**
  $$\text{redundant\_dual\_rate} = \frac{\text{model.redundant\_dual\_steps}}{T_{\text{total}}}$$
  where:
  - Evaluation Window: Entire streaming run $t \in [1, 6000)$ ($T_{\text{total}} = 6,000$ steps);
  - Increment Condition (per timestep $t$):
    $$\text{redundant\_dual\_steps}_{t} = \text{redundant\_dual\_steps}_{t-1} + \mathbb{I}\Big(\text{has\_lag}_t \land \text{has\_rec}_t \land \big(\text{decision}_t == \text{"REDUNDANT"} \lor (EMA(G_{D|B+R})_t \le \theta_{\text{tol}} \land EMA(G_{R|B+D})_t \le \theta_{\text{tol}})\big)\Big)$$
  - Tolerance Threshold: $\theta_{\text{tol}} = 0.015$;
  - Denominator: $T_{\text{total}} = 6,000$ steps.
- **Physical Meaning:** The proportion of total streaming time where both modules were actively allocated *and* met the formal software test of structural redundancy (either explicit arbitration decision or joint marginal gains both falling below threshold).
- **Topology Asymmetry:** 
  - In $T_3$, when mutual redundancy is detected, arbitration immediately evicts one module (`decision = "REDUNDANT"`), preventing persistent accumulation of dual occupancy.
  - In $T_2$, `decision` is *never* set to `"REDUNDANT"` (it remains `"NONE"`). Furthermore, on $I_{10}$, $EMA(G_{R|B+D})$ averages $\approx 0.487 \gg 0.015$. Consequently, the condition $(EMA(G_{D|B+R}) \le 0.015 \land EMA(G_{R|B+D}) \le 0.015)$ evaluates to **False** on almost all timesteps, resulting in `redundant_dual_steps` near zero, despite $T_2$ maintaining both modules on 100% of timesteps.

### 2.3 Metric 3: Protocol Preregistered Redundant Dual Allocation Rate ($\rho_{\text{dual, I10}}$)
- **Source:** `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (lines 68–71) & `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (Gate 6, line 61).
- **Preregistered Text:**
  $$\rho_{\text{dual}} = \text{Fraction of steps where BOTH modules are active on task } I_{10}$$
- **Evaluation Window:** Evaluation steps ($t \ge 1000$).
- **Formal Target & Gate:** $\rho_{\text{dual, I10}} \le 0.05$ for $T_3$; Gate 6 passes if redundant dual rate $\le 5\%$.
- **Crucial Equivalence:** The text of the preregistered protocol explicitly defines $\rho_{\text{dual}}$ as **the fraction of steps where BOTH modules are active on task $I_{10}$**. Therefore, under the frozen protocol definition, **$\rho_{\text{dual, I10}} \equiv \text{frac\_both}$**!

### 2.4 Metric 4: Dual Active Steps (`dual_active_steps`)
- **Code Symbol:** `self.dual_active_steps` in `IntegratedLEBREModel` (line 554).
- **Formula:**
  $$\text{dual\_active\_steps} = \sum_{t=1}^{6000} \mathbb{I}(\text{has\_lag}_t \land \text{has\_rec}_t)$$
- **Denominator:** $T_{\text{total}} = 6,000$ steps if normalized.
- **Physical Meaning:** Raw count of streaming timesteps where both module classes had active parameters.

---

## 3. Cross-Topology Summary on Task $I_{10}$ (Confirmatory Seeds 1311..1340)

| Topology | Description | Steady-State Dual Occupancy (`frac_both`) | Measured `redundant_dual_rate` | Actual Structural Behavior on $I_{10}$ |
|:---|:---|:---:|:---:|:---|
| **$T_1$** (Cascade) | L $\to$ D $\to$ R | **100.0%** ($1.000 \pm 0.000$) | $0.000 \pm 0.000$ | Both modules promoted and retained persistently on all 30 seeds. |
| **$T_{1R}$** (Rev. Cascade) | L $\to$ R $\to$ D | **100.0%** ($1.000 \pm 0.000$) | $0.000 \pm 0.000$ | Both modules promoted and retained persistently on all 30 seeds. |
| **$T_2$** (Symmetric Comp.) | Independent Probing | **100.0%** ($1.000 \pm 0.000$) | $0.0015 \pm 0.005$ | Promotes both independently; lacks arbitration to evict redundant module. |
| **$T_3$** (Arbitration) | Conditional + Pareto | **10.8%** ($0.108 \pm 0.082$) | $0.000 \pm 0.000$ | Successfully arbitrates: 86.4% pure Recurrent, 2.6% pure Lag, only 10.8% transient dual. |
| **$O_{\text{ALL}}$** (Control) | Always-On Control | **100.0%** ($1.000 \pm 0.000$) | $0.0023 \pm 0.006$ | Both modules permanently active by diagnostic construction. |

---

## 4. Resolution of the 48.2% Contradiction

1. **The 48.2% claim was NOT a measurement of `frac_both` or `redundant_dual_rate` in the confirmatory dataset.**
   - In confirmatory data, $T_2$ spends **100.0%** of steady-state evaluation time in the `BOTH` state, not 48.2%.
2. **Double Payment in $T_2$ is Real and Severe, but its True Rate is 100%, Not 48.2%:**
   - Unarbitrated symmetric competition ($T_2$) suffers persistent dual co-allocation on $100\%$ of evaluation steps on $I_{10}$.
   - It burns $118.8$ live FLOPs (compared to $92.4$ FLOPs for $T_3$, a $+28.6\%$ compute penalty) while achieving a strictly worse NMSE ($0.4940$ vs. $0.4173$ for $T_3$).
   - The assertion that $T_2$ exhibits double payment is therefore **empirically supported**, but the headline numerical figure of 48.2% was a reporting copy-forward error from developmental screening logs.
