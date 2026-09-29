# DYNAMIC-LAG-LIFECYCLE-01A: Statistical Re-Audit Report
## Traceability, Combinatorial Resolution & Seed-Level Inference

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01A`  
**Parent Milestone:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Audited Sample:** $N = 30$ Independent Evaluation Seeds (`801`–`830`) on Tasks D1, D2, D3  
**Bootstrap Iterations:** 10,000 Seed-Level Paired Resamples  
**Software Environment:** Python 3.14.2, NumPy 2.3.x, SciPy 1.16.x, Pandas 2.2.x

---

## 1. Mathematical Resolution & Traceability of Motivating Inconsistency B

In `DYNAMIC-LAG-LIFECYCLE-01`, the executive summary reported:
$$\text{STATISTICAL\_SIGNIFICANCE} = p < 10^{-15}$$
while Section 3 (Hypothesis H1) reported:
$$\text{Wilcoxon signed-rank: } W = 0, p = 1.73 \times 10^{-6}, \quad N = 30$$

### 1.1 Combinatorial Impossibility of $p < 10^{-15}$ at $N=30$
For an independent sample of $N=30$ paired differences where all differences share the identical sign (zero negative differences, zero ties, $W=0$), the number of possible sign vectors under the sharp null hypothesis is $2^{30} = 1,073,741,824$.
The exact two-sided combinatorial probability resolution is:
$$p_{\text{exact, min}} = \frac{2}{2^{30}} = \frac{1}{2^{29}} = \frac{1}{536,870,912} \approx \mathbf{1.862645149 \times 10^{-9}}$$
Therefore, an exact paired Wilcoxon signed-rank test on 30 pairs **cannot mathematically generate a p-value below $1.86 \times 10^{-9}$**.

### 1.2 Computational Lineage of Reported Values
Through source code and data lineage tracing:

1. **Origin of $p = 1.73 \times 10^{-6}$:**  
   Computed by `scipy.stats.wilcoxon(diff, method='approx')` on the 30 independent seed-level mean differences (averaged across D1–D3).  
   - Mean rank sum: $\mu_W = 232.5$, standard deviation: $\sigma_W = 48.6184$.
   - Continuity-corrected z-score: $z = \frac{-232.0}{48.6184} = -4.77185$.
   - Two-sided asymptotic p-value: $2 \times \Phi(-4.77185) = \mathbf{1.734398 \times 10^{-6}}$.  
   - **Verdict:** Exact computational match to `scipy.stats.wilcoxon` asymptotic mode.

2. **Origin of $p < 10^{-15}$:**  
   Computed by pooling all 90 task $\times$ seed observations ($3 \text{ tasks } [\text{D1, D2, D3}] \times 30 \text{ seeds} = 90 \text{ rows}$) into `scipy.stats.wilcoxon`.  
   - For $N=90$ pooled pairs: $W = 0, z = -8.243$, yielding:
     $$p_{\text{pooled}} = \mathbf{1.743790 \times 10^{-16}} < 10^{-15}$$
   - **Classification:** **`PSEUDOREPLICATION_DETECTED = YES`**.
   - **Scientific Assessment:** Treating 90 observations from 30 seeds as independent replicates violates the experimental-unit principle. This value is **formally disqualified and removed** from all scientific claims.

---

## 2. Definitive Seed-Level Statistical Robustness Suite (H1: B7 vs B1)

All statistics below are computed strictly at the independent experimental unit level ($N = 30$ evaluation seeds, each evaluated on the mean performance across D1, D2, and D3):

| Statistical Metric | Evaluated Value | Formulation / Method | Interpretation / Threshold |
| :--- | :---: | :--- | :--- |
| **Sample Size ($N$)** | **30** | Independent Random Seeds (`801`–`830`) | Primary Experimental Unit |
| **Paired Mean Delta ($\bar{D}$)** | **0.5404** | $\frac{1}{N} \sum (\text{NMSE}_{B1} - \text{NMSE}_{B7})$ | B7 reduces NMSE by 0.5404 |
| **Paired Median Delta** | **0.5697** | $\text{median}(\text{NMSE}_{B1} - \text{NMSE}_{B7})$ | Robust central advantage |
| **Paired Delta Std ($s_D$)** | **0.0732** | Sample standard deviation ($N-1$ ddof) | Tight seed variance |
| **95% Bootstrap CI** | **[0.5129, 0.5640]** | 10,000 paired seed-level resamples | Excludes 0 by 0.5129 units |
| **Cohen's $d_z$ (Seed-Level)** | **7.3799** | $d_z = \frac{\bar{D}}{s_D} = \frac{0.540424}{0.073229}$ | Extraordinarily large effect ($> 0.8$) |
| **Reported Cohen's $d_z$** | 18.42 | Task-by-seed pooled calculation | Corrected to 7.38 |
| **Seed Win Rate** | **100.0% (30 / 30)** | Count($D_s > 0$) / $N$ | Unanimous advantage |
| **Wilcoxon $W$ Statistic** | **0.0** | $\min(W^+, W^-)$ | Minimal possible rank sum |
| **Wilcoxon $p$-value (Exact)** | **$1.8626 \times 10^{-9}$** | Exact combinatorial ($2 / 2^{30}$) | Decisively rejects $H_0$ |
| **Wilcoxon $p$-value (Asymptotic)** | **$1.7344 \times 10^{-6}$** | Gaussian approximation ($z = -4.772$) | Decisively rejects $H_0$ |
| **Two-Sided Sign Test $p$-value** | **$1.8626 \times 10^{-9}$** | Exact binomial ($2 \times 0.5^{30}$) | Direction-only robustness |

---

## 3. Inferential Conclusion

The correction of $p < 10^{-15}$ to exact seed-level inference ($p = 1.86 \times 10^{-9}$, $d_z = 7.38$, win rate 30/30) has **zero negative impact** on the central scientific conclusion. The predictive superiority of the dynamic sparse lag discovery architecture (B7) over the memoryless linear baseline (B1) is mathematically incontrovertible, robust across all 30 evaluation seeds, and completely immune to the removal of pseudoreplicated pooling.
