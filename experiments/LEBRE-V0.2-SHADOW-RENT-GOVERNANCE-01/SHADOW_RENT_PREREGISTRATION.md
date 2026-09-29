# Formal Preregistration Document: Shadow-Rent Governance

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Preregistration Hash:** TO BE RECORDED IN MANIFEST  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 21, 2026  
**Status:** SEALED BEFORE CONFIRMATORY EXECUTION  

---

## 1. Primary Research Hypotheses & Invariants

```
+----------------------------------------------------------------------------------------------------+
| PREREGISTERED SCIENTIFIC INVARIANTS                                                                |
+------------------------------------+---------------------------------------------------------------+
| Invariant Parameter                | Preregistered Value / Rule                                    |
+------------------------------------+---------------------------------------------------------------+
| Canonical Code Base                | Bitwise Immutable (src/ and tests/ frozen)                    |
| Historical Physical Ceiling        | RAM <= 1024 Bytes (Static Capacity + Peak Working)            |
| Historical Compute Ceiling         | Mean Total Online FP <= 100.0 FLOPs/step                      |
| Primary Inferential Unit           | Independent Seed (N = 30 pairs)                               |
| Practical Non-Inferiority Margin   | Delta_tol = +0.0100 NMSE                                      |
| Pure-Lag Group Margin              | Delta_tol = +0.0150 NMSE                                      |
| Switching Latency Tolerance        | Delta_lat <= +50.0 stream steps                               |
| Multiplicity Control               | Holm-Bonferroni across S2 vs S0 and S3 vs S0 (alpha = 0.05)   |
| Periodic Sampling Period           | K = 5 (Derived analytically from baseline)                    |
| Page-Hinkley Candidate Grid        | Frozen at 12 configurations (evaluated on DEV cohort only)     |
| Trigger During Wake Burst Rule     | IGNORE (Deterministic, no recursion)                          |
| Anti-Starvation Heartbeat          | Mandatory, bounded maximum silence interval                   |
| Gate 6 Redundancy Status           | Carried forward as FAIL (not intentionally repaired)           |
| Milestone Boundary                 | Milestone M3 remains UNOPENED; Novelty claims FORBIDDEN       |
+------------------------------------+---------------------------------------------------------------+
```

---

## 2. Statistical Analysis Plan

### 2.1 Seed-Level Aggregation & Prequential Metric
For each model run $(s, \tau)$ evaluating scheduler candidate $m \in \{S_0, S_1, S_2, S_3\}$ on task $\tau \in \{I_1, \dots, I_{14}\}$ with seed $s$:
$$\text{NMSE}_{s, \tau}(m) = \frac{\sum_{t=1}^{T} (y_t - \hat{y}_t)^2}{\sum_{t=1}^{T} (y_t - \bar{y}_{\tau})^2}$$

The aggregate benchmark metric for seed $s$ is the unweighted arithmetic mean across all 14 tasks:
$$\bar{Y}_s(m) = \frac{1}{14} \sum_{\tau=1}^{14} \text{NMSE}_{s, \tau}(m)$$

### 2.2 Non-Inferiority Testing
The paired seed-level difference against the continuous baseline $S_0$ is:
$$\Delta_s(m) = \bar{Y}_s(m) - \bar{Y}_s(S_0), \quad s \in \{1611, \dots, 1640\}$$

The one-sided non-inferiority hypothesis is:
$$H_0: \mathbb{E}[\Delta(m)] \ge +0.0100 \quad \text{vs.} \quad H_1: \mathbb{E}[\Delta(m)] < +0.0100$$
Evaluated via paired one-sided Student's $t$-test:
$$t = \frac{\bar{\Delta}(m) - 0.0100}{\text{SE}_{\Delta}(m)}, \quad \text{df} = 29$$
Non-inferiority is supported if the upper bound of the 95% one-sided confidence interval satisfies:
$$\bar{\Delta}(m) + t_{0.95, 29} \cdot \text{SE}_{\Delta}(m) < +0.0100$$

---

## 3. Disjoint Calibration Protocol (DEV Cohort)

A grid of 12 candidate configurations for $S_3$ is evaluated exclusively on the development cohort (`1601..1610`, $N_{\text{DEV}}=10$). The configuration achieving:
1. Mean total online compute $\le 100.0 \text{ FLOPs/step}$;
2. Minimum aggregate NMSE;
3. Minimum regime switching latency on $I_{11}$–$I_{14}$;
will be frozen and sealed into `EVENT_TRIGGER_CALIBRATION.md` prior to executing the 30 confirmatory seeds (`1611..1640`).
