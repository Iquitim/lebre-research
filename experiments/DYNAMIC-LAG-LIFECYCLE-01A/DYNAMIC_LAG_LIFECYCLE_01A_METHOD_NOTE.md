# DYNAMIC-LAG-LIFECYCLE-01A: Methodological Audit Note
## Rigorous Foundations for Paired Inference, Ablation Isolation, and Benchmarking Hygiene

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01A`  
**Purpose:** Establish immutable methodological and statistical standards for the corrective mini-audit of `DYNAMIC-LAG-LIFECYCLE-01`.  
**Auditor Roles:** Skeptical Senior ML Researcher, Statistical Auditor, Experimental-Design Reviewer, Reproducibility Engineer.

---

## 1. Wilcoxon Signed-Rank Test: Foundations & Mathematical Properties

### 1.1 Paired-Data Structure & Null Hypothesis
The Wilcoxon signed-rank test (Wilcoxon, 1945) is a non-parametric statistical hypothesis test for paired, repeated-measurement, or matched-sample designs. Let $(X_1, Y_1), (X_2, Y_2), \dots, (X_N, Y_N)$ represent $N$ independent paired realizations (e.g., performance metric of Baseline $X$ vs Proposed Model $Y$ evaluated on identical random seed realizations $s \in \{1, \dots, N\}$).

The paired differences are defined as:
$$D_s = X_s - Y_s, \quad s = 1, \dots, N$$

The test evaluates the null hypothesis:
$$H_0: \text{The distribution of paired differences } D_s \text{ is symmetric about zero.}$$
Under the alternative hypothesis (two-sided):
$$H_1: \text{The distribution of paired differences } D_s \text{ is shifted from zero (median difference } \theta \neq 0\text{).}$$

### 1.2 Treatment of Zero Differences and Ties
1. **Zero Differences ($D_s = 0$):**
   - Under the standard Pratt (1959) or Wilcoxon (1945) procedures:
     - **Wilcoxon discard method (`zero_method="wilcox"` in `scipy.stats`):** All pairs with $D_s = 0$ are discarded before ranking. The effective sample size is reduced to $N_{\text{eff}} \le N$.
     - **Pratt's method (`zero_method="pratt"`):** Zero differences are included in the initial ranking, but their ranks are eliminated from the positive and negative rank sums.
     - **Z-split method (`zero_method="zsplit"`):** Zero differences are ranked and their ranks are evenly split between positive and negative sums.
   - When benchmarking distinct floating-point models on synthetic streams, zero differences are rare unless both models execute identical constant predictions.

2. **Ties in Absolute Differences ($|D_i| = |D_j|$):**
   - Tied absolute values are assigned average (mid-) ranks.
   - In floating-point arithmetic, true mathematical ties may be obscured by numerical noise at $10^{-16}$. Comparisons must verify that differences are not artifactually separated by round-off errors.

### 1.3 Exact vs. Asymptotic Inference
The test statistic $W$ is the smaller of the rank sums:
$$W = \min(W^+, W^-), \quad \text{where } W^+ = \sum_{D_s > 0} R_s, \quad W^- = \sum_{D_s < 0} R_s$$
where $R_s$ is the rank of $|D_s|$ among $\{|D_1|, \dots, |D_{N_{\text{eff}}}|\}$.

1. **Exact Combinatorial Distribution:**
   - Under $H_0$, each of the $N_{\text{eff}}$ ranks $1, 2, \dots, N_{\text{eff}}$ is equally likely to be positive or negative.
   - There are $2^{N_{\text{eff}}}$ equally probable sign assignments.
   - If all $N_{\text{eff}}$ differences have the same sign (e.g., $D_s > 0$ for all $s$), then $W = 0$ and $W^+ = \frac{N_{\text{eff}}(N_{\text{eff}}+1)}{2}$.
   - The exact two-sided p-value for $W = 0$ is:
     $$p_{\text{exact}} = 2 \times \frac{1}{2^{N_{\text{eff}}}} = \frac{1}{2^{N_{\text{eff}} - 1}}$$
   - **Crucial Combinatorial Lower Bound:** For $N_{\text{eff}} = 30$:
     $$p_{\text{min, exact}} = \frac{2}{2^{30}} = \frac{1}{2^{29}} = \frac{1}{536,870,912} \approx 1.862645149 \times 10^{-9}$$
   - Any reported p-value smaller than $1.86 \times 10^{-9}$ (such as $p < 10^{-15}$) **cannot mathematically arise from an exact 30-pair Wilcoxon signed-rank test**.

2. **Asymptotic Gaussian Approximation (`method="approx"`):**
   - For moderate-to-large $N$, the distribution of $W^+$ under $H_0$ approaches a normal distribution:
     $$\mu_W = \frac{N_{\text{eff}}(N_{\text{eff}}+1)}{4}, \quad \sigma_W = \sqrt{\frac{N_{\text{eff}}(N_{\text{eff}}+1)(2N_{\text{eff}}+1)}{24} - \frac{\sum (t_k^3 - t_k)}{48}}$$
   - For $N_{\text{eff}} = 30$: $\mu_W = \frac{30 \times 31}{4} = 232.5$, $\sigma_W = \sqrt{\frac{30 \times 31 \times 61}{24}} = \sqrt{2363.75} \approx 48.6184$.
   - With continuity correction ($|W - \mu_W| - 0.5$):
     $$z = \frac{0 - 232.5 + 0.5}{48.6184} = \frac{-232.0}{48.6184} \approx -4.77185$$
   - The two-sided standard normal p-value is:
     $$p_{\text{asymp}} = 2 \times \Phi(-4.77185) \approx \mathbf{1.734 \times 10^{-6}}$$
   - **Traceability Finding:** The reported value $p = 1.73 \times 10^{-6}$ in H1 corresponds **identically** to the asymptotic normal approximation computed by `scipy.stats.wilcoxon(diff, method='approx')`.

---

## 2. Machine Learning Benchmark Variance & Paired Design

### 2.1 Bouthillier et al. (MLSys 2021) Principles
Bouthillier et al. (*Accounting for Variance in Machine Learning Benchmarks*, MLSys 2021) demonstrated that empirical machine learning benchmarks exhibit substantial variance across random seeds, data ordering, and weight initializations.
- In causal comparative benchmarking, testing models on *unmatched* random seeds inflates error variance, obscuring true structural effect sizes.
- When two architectures are fed the **identical causal input-target realization** $(X_{s, t}, y_{s, t})$ generated by random seed $s$, their performance metrics are naturally and strictly **paired**.
- Discarding pairing (e.g., treating evaluation results as two independent two-sample pools) violates experimental design principles and discards statistical power.
- All comparative statistical tests in this audit must maintain strict seed-level pairing across architectures.

---

## 3. Ablation Integrity & Single-Component Isolation

### 3.1 Fostiropoulos & Itti (AutoML / PMLR 2023) Framework
Fostiropoulos & Itti (*ABLATOR: Robust Horizontal-Scaling of Machine Learning Ablation Experiments*, PMLR 2023) established that causal attribution of performance gains to a specific algorithmic mechanism requires **single-component isolation**:
1. **Shared Implementation Substrate:** The baseline and ablated variants must execute the identical codebase, candidate probing schedule, feature scaling, memory buffers, and numerical precision.
2. **Strict Single-Difference Principle:**
   - Variant B7: Two-timescale structural relevance with quiescence-aware gate.
   - Variant B7_E0: Instantaneous or magnitude-based eviction control.
   - All other hyperparameters ($L_{\max}=32, K_{\max}=2, M=2, \mu_{\text{base}}, \mu_{\text{lag}}$) must remain bitwise identical.
3. **Operational Efficacy:** An ablation flag that is never triggered, or logic that checks an un-decayed variable during silence, fails the criterion of an operational ablation. If $w$ does not decay when input is zero, checking $|w| < 0.05$ does not implement magnitude eviction.

---

## 4. Pseudoreplication & The True Experimental Unit

### 4.1 Hurlbert (1984) and the Experimental-Unit Principle
Stuart Hurlbert's seminal treatise (*Pseudoreplication and the Design of Ecological Field Experiments*, Ecological Monographs 1984) warned against treating subsamples or repeated measurements taken within a single experimental unit as independent replicates:
- In streaming system identification:
  - Individual time steps $t \in \{1, \dots, T\}$ within a run are serially correlated time series observations, **not** independent replicates.
  - Individual candidate probing events or tap promotions within a run are conditionally dependent on the trajectory history, **not** independent replicates.
  - Different synthetic tasks evaluated on the *same random seed* share common pseudorandom generator draws and cannot be treated as independent unless a hierarchical mixed-effects model is used.
- **The Independent Experimental Unit:** The independent unit of statistical inference is **one complete independent run driven by an independent random seed realization** ($N=30$).
- Pooling 90 task $\times$ seed observations ($3 \text{ tasks} \times 30 \text{ seeds}$) as if they were 90 independent experiments is a textbook instance of **pseudoreplication**, yielding spuriously tiny p-values ($p = 1.74 \times 10^{-16} < 10^{-15}$).

---

## 5. ASA Guidelines on P-Value Reporting (Wasserstein & Lazar, 2016)

The American Statistical Association (ASA) Statement on Statistical Significance and P-Values mandates:
1. P-values do not measure the probability that the studied hypothesis is true, nor the size of an effect.
2. Scientific conclusions should not be based solely on whether a p-value passes an arbitrary threshold (e.g., $p < 0.05$ or $p < 10^{-15}$).
3. Researchers must disclose full statistical procedures, exact sample sizes, test formulas, effect sizes (Cohen's $d_z$), and confidence intervals.
4. Selective reporting of the smallest available p-value (e.g., selecting pooled $p < 10^{-15}$ over seed-level $p = 1.73 \times 10^{-6}$ or exact $p = 1.86 \times 10^{-9}$) is scientifically unacceptable.
