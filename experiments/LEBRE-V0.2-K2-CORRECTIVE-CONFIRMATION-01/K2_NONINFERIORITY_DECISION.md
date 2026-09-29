# K=2 Non-Inferiority Decision Deliverable

**Stage:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Preregistered Margin:** $\epsilon = +0.0100$  
**Evaluation Standard:** Upper bound of one-sided 95% Confidence Interval on paired seed-level $\Delta \text{NMSE}(C_2 - C_0) < +0.0100$.  
**Sample Cohort:** $N = 30$ fresh independent seeds ($1941..1970$).

---

## 1. Statistical Scorecard

| Metric | Measured Value | Preregistered Criterion | Status |
| :--- | :--- | :--- | :--- |
| **Mean $\Delta \text{NMSE}$** | `+0.002714` | Point estimate | Informational |
| **Std Dev $SD(\Delta \text{NMSE})$** | `0.003999` | Sample dispersion | Informational |
| **Std Error $SE(\Delta \text{NMSE})$** | `0.000730` | Standard error ($N=30$) | Informational |
| **One-Sided 95% CI Upper Bound** | **`+0.003955`** | **$< +0.0100$** | **PASS** |
| **Two-Sided 95% CI** | `[+0.001221, +0.004207]` | Exact interval | Informational |
| **Paired t-statistic** | `3.7169` | $t_{29}$ | $p = 8.5794e-04$ |
| **Wilcoxon signed-rank $p$** | `1.0382e-03` | Non-parametric test | Informational |
| **Cohen's $d_z$** | `0.6786` | Effect size | Informational |
| **Seed Wins / Ties / Losses** | `5 / 0 / 25` | Win count ($\Delta < 0$) | Informational |

---

## 2. Formal Adjudication

> [!IMPORTANT]
> **RULING: NON-INFERIORITY CONFIRMED (PASS)**
> 
> The upper bound of the one-sided 95% confidence interval on paired seed-level $\Delta \text{NMSE}$ across 30 fresh confirmatory seeds is **`+0.003955`**, which falls strictly below the preregistered non-inferiority margin of $+0.0100$.
> Decimating recurrent state propagation to every second stream step ($K_{\text{rec\_forward}}=2$) introduces negligible predictive distortion across the 14 benchmark tasks.
