# BENCH-01A-R: Numerical Divergence Policy Correction & Failure Reporting Protocol

**Document ID:** BENCH-01A-R-DIVERGENCE  
**Auditor:** Statistical Reviewer & Benchmark Governance Auditor  
**Date:** September 19, 2026  
**Status:** PROTOCOL CORRECTED — ARBITRARY PENALTY REMOVED  
**Governing Standard:** Sections 26–39, 61 of Protocol BENCH-01A-R  

---

## 1. Executive Summary & Defect Identification (Section 26)

In the preliminary BENCH-01A failure policy (`BENCH_01A_FAILURE_POLICY.md`), Section 3 stipulated:
> *"For cumulative regret scoring, a diverged run is assigned a penalty equal to the maximum observed regret among non-diverged runs on that stream multiplied by 1.5, preventing diverging runs from escaping statistical aggregation."*

### The Methodological Flaw:
The $1.5\times$ penalty is an **arbitrary synthetic value** with zero statistical or mathematical justification:
1. It manufactures fictional numerical losses that never occurred in the physical run;
2. It distorts paired bootstrap distributions and non-parametric confidence intervals;
3. It obscures algorithmic fragility by converting categorical execution collapse into an arbitrary numeric point.

Per Section 26:
> *"The current failure policy contains a reported: 1.5× penalty for divergence. This is not acceptable unless a clear mathematical/statistical justification exists independent of benchmark results. Default action: REMOVE IT."*

The $1.5\times$ penalty is **permanently eliminated**.

---

## 2. New Neutral Failure Reporting Protocol (Sections 27–32)

### 2.1 The Failure Principle (Section 27)
A diverged run is a **FAILED RUN**. Predictive performance and algorithmic stability must be reported as distinct, non-conflated dimensions:
- **Predictive Metrics (MSE, MAE, NMSE):** Computed and aggregated **strictly over valid, complete runs**;
- **Algorithmic Reliability:** Measured and reported via explicit **failure and divergence rates**.

### 2.2 Deterministic Divergence Criteria (Section 28)
A run is formally classified as a `NUMERICAL_DIVERGENCE` if and only if any of the following deterministic conditions occur:
1. Non-finite prediction: $\hat{y}_t \notin \mathbb{R}$ (`np.isnan` or `np.isinf`);
2. Non-finite parameter/state: $\exists \theta \in \Theta_t \text{ s.t. } \neg\text{np.isfinite}(\theta)$;
3. Magnitude overflow: $|\hat{y}_t| > 10^4$ or $\|s_t\| > 10^4$ on standardized data;
4. Irrecoverable numerical exception (e.g., singular matrix inversion, floating-point exception).

---

## 3. Divergence Logging & Diagnostic Audit Schema (Section 29)

Whenever divergence occurs, execution halts immediately for that seed/stream, and a structured diagnostic manifest (`FAILURE_MANIFEST.json`) is recorded containing:
```json
{
  "failure_type": "NUMERICAL_DIVERGENCE",
  "model_identifier": "B3_MUSE_RNN",
  "dataset_identifier": "B1_NSW_Electricity",
  "seed": 108,
  "config_id": "cfg_07",
  "step_of_failure": 14205,
  "total_stream_steps": 45312,
  "fraction_stream_completed": 0.3135,
  "cumulative_loss_before_failure": 342.18,
  "last_finite_loss": 1.452,
  "state_norm_at_failure": 1.042e5,
  "parameter_norm_at_failure": 2.185e4,
  "consumed_flops_before_failure": 5234120
}
```

### Resource Accounting Invariant (Section 38):
Compute and time spent prior to failure are **never erased**. All FLOPs and CPU cycles consumed up to step $t_{\text{fail}}$ are fully charged and included in computational budget reports.

---

## 4. Benchmark Aggregation & Ranking Rules (Sections 30–35)

### 4.1 Primary Reliability Metrics (Sections 30 & 31)
1. **`DIVERGENCE_RATE`:**
   $$\text{Divergence Rate} = \frac{\text{Number of Failed Runs}}{\text{Total Runs Executed}}$$
2. **`FAILURE_FREE_SEED_RATE`:**
   $$\text{Failure-Free Seed Rate} = 1 - \text{Divergence Rate}$$
3. **`MEDIAN_COMPLETION_FRACTION`:** Median of $t_{\text{fail}} / T$ among diverged runs.

### 4.2 Handling in Comparative Tables & Pareto Fronts (Sections 32 & 35)
1. **Predictive Reporting:** Comparative loss tables (MSE, MAE) report the mean across complete runs accompanied by the exact count of successful seeds (e.g., $\text{MSE} = 0.0412 \text{ [28/30 seeds completed]}$).
2. **Ranking & Pareto Policy (Section 35):** In ranking summaries where complete execution is mandatory, diverged configurations receive the explicit categorical label:
   $$\mathbf{FAILED\_RUN \quad (\text{or } +\infty)}$$
   No synthetic loss is fabricated. A model with low error on a subset of surviving seeds but high divergence rate is classified as **`UNSTABLE`** and does not achieve Pareto dominance over reliable models.

---

## 5. Formal Table C: Comprehensive Failure Reporting Matrix (Section 61)

| Execution Outcome | Predictive Reporting | Resource Reporting | Failure Flag | Suite Aggregation Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Complete Run** | Full prequential MSE, MAE, NMSE computed over entire test segment ($t \in [0.30T, T]$). | Full mean FLOPs, P95 FLOPs, persistent memory, and wall-clock latency recorded. | `SUCCESS` | Included in primary predictive distributions and Pareto frontiers. |
| **Numerical Divergence** | Pre-divergence loss recorded with `CENSORED_AT_FAILURE` flag. Full-run loss marked `FAILED_RUN` ($+\infty$). | All FLOPs and runtime consumed prior to $t_{\text{fail}}$ fully accounted for. | `NUMERICAL_DIVERGENCE` | Excluded from complete-run MSE; scored as failed seed in Divergence Rate. |
| **Execution Exception** | Marked `FAILED_RUN` ($+\infty$). | Consumed FLOPs up to exception accounted for. | `RUNTIME_EXCEPTION` | Excluded from complete-run MSE; logged in Defect Manifest. |
| **Runtime Timeout** | Marked `FAILED_RUN` ($+\infty$). | All FLOPs and time consumed up to timeout accounted for. | `TIMEOUT_EXCEEDED` | Excluded from complete-run MSE; scored as computational failure. |

---

## 6. Formal Final Verdict (Section 63)

$$\mathbf{DIVERGENCE\_POLICY = PASS\_AFTER\_CORRECTION}$$

The arbitrary $1.5\times$ penalty is completely excised. The failure policy is now mathematically neutral, transparently reporting categorical failure states and decoupling predictive loss from divergence rates.
