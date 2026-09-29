# Gate 6 Recomputation & Governance Reconciliation

**Document Identifier:** `GATE6_RECONCILIATION.md`  
**Audit Context:** `LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`  
**Auditor:** Independent Scientific-Software Auditor  
**Date:** September 2026  
**Status:** Sealed Governance Finding  

---

## 1. Executive Summary

This document establishes the definitive governance evaluation of **Gate 6 (Redundancy Control)** under the frozen preregistration of `LEBRE-V0.2-INTEGRATION-DESIGN-01`.

Evaluating the sealed 30-seed confirmatory dataset (`LEBRE_V0_2_SEED_RESULTS.csv`, seeds `1311`..`1340`) strictly against the frozen preregistered definition yields:
- **`GATE_6_PREREGISTERED_STATUS = FAIL`** ($\overline{\rho}_{\text{dual}} = 0.108467 > 0.05$; $22/30$ seeds exceed the threshold);
- **`T3_I10_ARBITRATION_EFFECTIVENESS = SUPPORTED`** (Arbitration reduces dual occupancy from $100.0\%$ in $T_2$ to $10.85\%$ in $T_3$, an $89.2\%$ reduction in dual allocation, while saving $22.2\%$ in live compute and improving accuracy).

Any substitution of `redundant_dual_rate` ($0.0000$) to claim a "PASS" on Gate 6 is formally rejected as an unpreregistered metric alteration.

---

## 2. Preregistered Rule vs. Empirical Values

### 2.1 Frozen Preregistration
In `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (line 61) and `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (lines 68–71):
$$\rho_{\text{dual, I10}} = \text{Fraction of steps where BOTH modules are active on task } I_{10} \le 0.05$$
This operationalizes as `frac_both` over the steady-state evaluation window ($t \in [1000, 6000)$).

### 2.2 Recomputed Confirmatory Values on Task $I_{10}$

All quantities derived directly from `GATE6_BY_SEED.csv` ($N=30$ paired seeds):

| Topology | Mean `frac_both` | Median `frac_both` | 95% Bootstrap CI | Max `frac_both` | Seeds $> 0.05$ | Mean Live FLOPs | Mean NMSE |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$T_1$ (Lag Cascade)** | $0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $0.0000$ | $0 / 30$ | $88.8$ | $0.2574$ |
| **$T_{1R}$ (Rec Cascade)** | $0.0000$ | $0.0000$ | $[0.0000, 0.0000]$ | $0.0000$ | $0 / 30$ | $88.8$ | $0.2590$ |
| **$T_2$ (Unarbitrated)** | **$1.0000$** | **$1.0000$** | $[1.0000, 1.0000]$ | **$1.0000$** | **$30 / 30$** | **$118.8$** | **$0.4940$** |
| **$T_3$ (Arbitrated)** | **$0.1085$** | **$0.0793$** | **$[0.0764, 0.1463]$** | **$0.5002$** | **$22 / 30$** | **$92.4$** | **$0.4173$** |
| **$O_{\text{ALL}}$ (Oracle Bound)**| **$1.0000$** | **$1.0000$** | $[1.0000, 1.0000]$ | **$1.0000$** | **$30 / 30$** | **$118.8$** | **$0.4940$** |

---

## 3. Disambiguation & Rejection of Metric Substitution

In the simulation codebase `scratch/run_v02_integration_experiments.py`:
- `frac_both` measured empirical simultaneous occupancy: $\frac{1}{T}\sum \mathbb{I}(\text{Lag} \land \text{Recurrent})$.
- `redundant_dual_rate` was a diagnostic sub-filter: $\frac{1}{T}\sum \mathbb{I}(\text{Lag} \land \text{Recurrent} \land G_D < 0.015 \land G_R < 0.015)$.

Because $T_3$'s conditional arbitration ensures that whenever both modules are active, at least one is actively providing empirical marginal gain, $T_3$ achieves:
$$\text{redundant\_dual\_rate}(T_3) = 0.000000 \quad (0.0\%)$$

However, `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (line 69) explicitly defined the operational metric for $\rho_{\text{dual}}$ as:
$$\rho_{\text{dual}} = \text{Fraction of steps where BOTH modules are active on task I10}$$
without any secondary gain gating. Substituting `redundant_dual_rate` for `frac_both` to declare Gate 6 a "PASS" violates scientific preregistration integrity (Simmons et al., 2011; Nosek et al., 2018).

---

## 4. Governance Verdict & Scientific Synthesis

### 4.1 Strict Governance Verdict
Applying the preregistered threshold literally:
- Threshold: $\rho_{\text{dual}} \le 0.05$
- Observed Mean: $0.108467$
- Observed Violations: 22 out of 30 seeds exceed $0.05$
- **Verdict:** **`GATE_6_PREREGISTERED_STATUS = FAIL`**

### 4.2 Decoupled Algorithmic Assessment
While $T_3$ fails the rigid 5% ceiling, the algorithmic arbitration mechanism is demonstrably effective:
1. **89.2% Dual Allocation Suppression:** $T_2$ keeps both modules active on $100.0\%$ of evaluation steps. $T_3$ suppresses dual occupancy down to $10.85\%$, restricting dual allocation to transient exploratory windows.
2. **Compute Savings:** $T_3$ consumes $92.4$ live FP FLOPs/step on $I_{10}$ compared to $118.8$ for $T_2$ (a $22.2\%$ savings in live evaluation FLOPs).
3. **Accuracy Improvement:** Despite spending $89.2\%$ less time in dual state, $T_3$ achieves NMSE of $0.4173$, outperforming $T_2$ ($0.4940$).
4. **Zero Useless Co-Allocation:** Thresholded redundant dual allocation is exactly $0.0000$.

Therefore:
$$\mathbf{T3\_I10\_ARBITRATION\_EFFECTIVENESS = SUPPORTED}$$
$$\mathbf{GATE\_6\_PREREGISTERED\_STATUS = FAIL}$$

The preregistered 5% threshold was set too conservatively for an online adaptive learner that must maintain finite probe windows to track dynamic task statistics. This failure is a resource-governance finding to be addressed in subsequent optimization stages, not an invalidation of the arbitration architecture.
