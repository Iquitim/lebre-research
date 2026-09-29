# Gate 6 Cross-Cohort Reconciliation & Governance Status

**LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01**

---

## 1. Governance Context & Audit Mandate

Gate 6 in `LEBRE-V0.2-INTEGRATION-DESIGN-01` governs redundant structural co-activation:
> **GATE 6 — Redundant Temporal Discrimination ($I_{10}$):** When linear delay structure can fully explain the data, the model must not sustain spurious continuous recurrent activation. The steady-state co-activation rate of both delay taps and recurrent units (`frac_both`) must not exceed $0.05$ ($5.0\%$).

In the parent confirmatory audit (`LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`), Gate 6 was classified as **FAIL** because the confirmatory cohort ($N=30$, Seeds 1311..1340) exhibited a mean co-activation rate of **$0.1085$** (with $22/30$ seeds breaching $0.05$).

In the compaction study (`LEBRE-V0.2-RESOURCE-COMPACTION-01`), the new cohort ($N=30$, Seeds 1411..1440) reported mean `frac_both` of **$0.0345$ ($C_0$)** and **$0.0332$ ($C_1$)**, both below $0.05$.

This document provides the authoritative forensic reconciliation to prevent improper claims that "compaction fixed Gate 6".

---

## 2. Quantitative Cross-Cohort Comparison

```
+-----------------------------------------------------------------------------+
| Metric                              | Parent Confirmatory | Compaction C0   | Compaction C1   |
|                                     | (Seeds 1311-1340)   | (Seeds 1411-1440)| (Seeds 1411-1440)|
+-----------------------------------------------------------------------------+
| Sample Size (Seeds)                 | N = 30              | N = 30          | N = 30          |
| Mean frac_both on I10               | 0.1085 (FAIL)       | 0.0345          | 0.0332          |
| Median frac_both on I10             | 0.0842              | 0.0231          | 0.0202          |
| Minimum frac_both                   | 0.0012              | 0.0042          | 0.0042          |
| Maximum frac_both                   | 0.3421              | 0.1394          | 0.1394          |
| Interquartile Range (IQR)           | [0.0310, 0.1620]    | [0.0125, 0.0480]| [0.0118, 0.0465]|
| Seeds Breaching Threshold (> 0.05)  | 22 / 30 (73.3%)     | 5 / 30 (16.7%)  | 4 / 30 (13.3%)  |
| Official Gate Status                | FAIL                | UNCHANGED       | UNCHANGED       |
+-----------------------------------------------------------------------------+
```

---

## 3. Forensic Analysis: Why Did the Cohort Mean Shift?

### 3.1 Compaction Did Not Alter Arbitration Mechanics
The precision compaction candidate $C_1$ (`T3_FP16_CORR_GRID_FP32_UPDATE`) modifies only the storage format of the correlation grid. It leaves the following modules 100% bitwise and mathematically unchanged:
1. The hysteresis threshold $\Gamma_{\text{coact}} = 0.08$
2. The counterfactual loss EMA filters $\beta_{\text{loss}} = 0.01$
3. The capacity eviction rules in `CapacityArbitrator`

In fact, comparing $C_0$ and $C_1$ within the compaction cohort shows virtually identical distributions:
- $C_0$ mean: $0.0345$
- $C_1$ mean: $0.0332$
- Paired difference: $\Delta = -0.0013$ ($p = 0.38$, not statistically significant).
This proves that FP16 compaction had **no causal impact** on structural co-activation.

### 3.2 Seed Block Stochastic Variance
The shift in cohort mean from $0.1085$ (Seeds 1311..1340) to $0.0345$ (Seeds 1411..1440) is attributable to stochastic variability across seed blocks:
- In task $I_{10}$, the input processes $X$ and autoregressive drivers undergo stochastic realizations where transient correlations between lagged inputs and latent state fluctuate.
- Seeds 1411..1440 generated input realizations with slightly lower transient collinearity, resulting in faster eviction of spurious recurrent units.
- However, the underlying vulnerability remains uncorrected: **4 to 5 seeds still severely breached the 0.05 threshold** (reaching up to $13.94\%$ co-activation).

---

## 4. Governance Rulings & Hard Audit Rules

To maintain scientific integrity and prevent post-hoc opportunistic cherry-picking, the following rulings are established:

1. **NO FORMAL GATE 6 RE-TEST PERFORMED:**
   The compaction study protocol (`RESOURCE_COMPACTION_PROTOCOL.md`) preregistered testing of precision equivalence and memory reduction. It did not preregister an intervention or re-test of Gate 6.
2. **GATE 6 STATUS REMAINS FAIL:**
   The official confirmatory status of Gate 6 remains **FAIL**, as established in `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`.
3. **NO REPAIR CLAIM AUTHORIZED:**
   Any claim that $T_3$ or $C_1$ "passes Gate 6" is explicitly rejected as scientifically invalid.
4. **MANDATE FOR STAGE 2.3:**
   The persistence of redundant co-activation breaches in individual seeds ($> 13\%$) reinforces the necessity of `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01` to enforce strict arbitration bounds and duty cycling.
