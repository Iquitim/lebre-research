# Gate 6 Preregistered Definition & Semantic Reconstruction

**Document Identifier:** `GATE6_PREREGISTERED_DEFINITION.md`  
**Audit Context:** `LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`  
**Author:** Independent Scientific-Software Auditor  
**Date:** September 2026  

---

## 1. Primary Preregistered Source Citations

The exact formulation of Gate 6 and its associated hypothesis are preserved in the frozen study repository:

### 1.1 Source 1: Protocol Document
*File:* `experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (lines 60–61)
> **GATE 6 — Redundancy Control:**  
> On I10, redundant dual allocation rate must be $\le 5\%$ of evaluation steps.

### 1.2 Source 2: Hypotheses Document
*File:* `experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (lines 64–71)
> ### H5 — Resource-Aware Arbitration Controls Redundancy  
> **Formal Statement:** Conditioning structural promotion on both conditional marginal gain ($G_{D|B+R}, G_{R|B+D}$) and Pareto resource dominance (Topology T3) strictly reduces redundant dual allocation compared to unconstrained parallel addition (O_ALL) on redundant tasks (I10), without increasing predictive NMSE beyond $\Delta_{\text{equiv}}$.  
> **Operational Metric:** Redundant Dual Allocation Rate ($\rho_{\text{dual, I10}}$):  
> $$\rho_{\text{dual}} = \text{Fraction of steps where BOTH modules are active on task I10}$$  
> **Falsification Threshold:** Falsified if T3 allocates dual capacity on task I10 in $\ge 20\%$ of evaluation steps, OR if T3 incurs a prediction regret $\Delta_{\text{NMSE}} > 0.05$ relative to O_ALL.

---

## 2. Parameter Specification Table

From these primary documents, the preregistered parameters governing Gate 6 are mapped as follows:

| Field | Preregistered Value | Source Document | Line Reference |
|:---|:---|:---|:---|
| **Target Task** | `I10_Redundant_Temporal_Structure` | `INTEGRATION_PROTOCOL.md` | Line 61 |
| **Preregistered Metric Name** | `redundant dual allocation rate` / $\rho_{\text{dual, I10}}$ | `INTEGRATION_PROTOCOL.md` / `INTEGRATION_HYPOTHESES.md` | Line 61 / Line 68 |
| **Preregistered Mathematical Definition** | $\rho_{\text{dual}} = \frac{1}{T_{\text{eval}}} \sum_{t=1000}^{6000} \mathbb{I}(\text{Lag Active}_t \land \text{Recurrent Active}_t)$ | `INTEGRATION_HYPOTHESES.md` | Line 69 |
| **Operational Column Name** | `frac_both` | `scratch/run_v02_integration_experiments.py` | Line 356 |
| **Evaluation Window** | Steady-state steps $t \in [1000, 6000)$ ($T_{\text{eval}} = 5,000$ steps) | `INTEGRATION_PROTOCOL.md` | Line 47 |
| **Preregistered Gate Threshold** | $\le 0.05$ ($5.0\%$ of evaluation steps) | `INTEGRATION_PROTOCOL.md` | Line 61 |
| **Denominator** | $T_{\text{eval}} = 5,000$ (Evaluation steps) | `INTEGRATION_PROTOCOL.md` | Line 47 |

---

## 3. Disambiguation of `frac_both` vs. `redundant_dual_rate`

In the simulation codebase `scratch/run_v02_integration_experiments.py`, two distinct metrics were tracked:

1. **`frac_both` (Operational Dual Occupancy Rate):**
   - *Code:* `frac_both = np.mean(steps_both[t_eval:])`
   - *Semantics:* The exact empirical proportion of steady-state steps where both the discrete lag filter and continuous recurrent filter were simultaneously allocated and active in the model.
   - *Matches Preregistration:* Matches the literal mathematical definition given in `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` line 69.
2. **`redundant_dual_rate` (Software-Thresholded Diagnostic Metric):**
   - *Code:* `redundant_steps = np.sum((steps_both) & (g_d_br < theta_tol) & (g_r_bd < theta_tol))`
   - *Semantics:* Steps where BOTH were active AND neither module provided marginal gain above $\theta_{\text{tol}} = 0.015$.
   - *Relation to Preregistration:* This was an internal algorithmic diagnostic introduced inside the simulation script. It was NOT the preregistered definition of $\rho_{\text{dual, I10}}$.

**Binding Audit Rule:** Substituting `redundant_dual_rate` (which was $0.0000$ for $T_3$) for `frac_both` to declare Gate 6 a PASS is a post-hoc metric substitution. The audit must evaluate Gate 6 strictly against `frac_both`.
