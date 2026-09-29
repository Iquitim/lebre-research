# BENCH-01A: Statistical Analysis Specification & Pareto Dominance Framework

**Document ID:** BENCH-01A-STATS  
**Auditor:** Statistical Reviewer & Experimental Data Analyst  
**Date:** September 19, 2026  
**Status:** STATISTICAL SPECIFICATION LOCKED  
**Governing Standard:** Sections 94–106, 168–173, 214 of BENCH-01A Protocol  

---

## 1. Governing Statistical Philosophy

Per Section 75 and Section 168 of the protocol:
1. **Rejection of Arbitrary Scalar Ranking:**  
   There is **no single "winner score"** in BENCH-01. Algorithmic trade-offs across prediction accuracy, adaptation latency, compute operations, memory footprint, and runtime latency are intrinsically multi-objective.
2. **Paired Non-Parametric Inference:**  
   Because all models are evaluated on identical, chronologically locked data streams across matched random seeds, all statistical evaluations use **paired difference distributions** rather than independent sample t-tests.
3. **Distributional Reporting (Section 98):**  
   Reporting only sample means is prohibited. Every metric must report the full statistical summary: **Mean, Median, Standard Deviation, Interquartile Range (IQR), and 95% Bootstrap Confidence Intervals**.

---

## 2. Seed Policy & Stochastic Replication Protocol (Sections 94–97)

- **Number of Evaluation Seeds (Section 95):** Exactly **$N = 30$ independent random seeds** are pre-registered for every stochastic model on every benchmark stream:
  $$\mathcal{S} = \{101, 102, 103, \dots, 130\}$$
- **Deterministic Baselines (Section 94):** Models with zero random initialization (e.g., RZA-LMS initialized at $w_0 = 0$) are evaluated once per stream with exact bitwise reproduction verified.
- **Strict Prohibition Against Stream Shuffling (Section 97):**  
  > *"For fixed ordered datasets, seeds affect: parameter initialization, random model components, sampling internal to algorithm, NOT data ordering."*  
  Data streams remain 100% fixed, chronological, and identical across all models and seeds.

---

## 3. Paired Difference & Bootstrap Confidence Interval Protocol (Sections 99–101)

### 3.1 Paired Metric Differences
For any metric $M$ (e.g., MSE, FLOPs), the paired difference for seed $i \in \{1, \dots, 30\}$ between Track B and Baseline $B$ is:
$$\Delta_i = M(\text{Track B}, s_i) - M(B, s_i)$$

### 3.2 Paired Bootstrap Confidence Intervals (Section 100)
- **Bootstrap Replicates:** Exactly **$B = 10{,}000$ bootstrap resamples** drawn with replacement from the paired difference vector $\vec{\Delta} = (\Delta_1, \dots, \Delta_{30})$.
- **Confidence Level:** 95% two-sided confidence interval $[\Delta_{0.025}^*, \Delta_{0.975}^*]$ computed via the percentile bootstrap method.
- **Significance Criterion:** A difference is statistically significant at $\alpha = 0.05$ if and only if the 95% bootstrap CI excludes zero.

### 3.3 Effect Size Quantification (Section 101)
To ensure practical relevance beyond sample-size artifacts, effect size is quantified using:
1. **Cohen's $d_z$ (Paired Effect Size):**
   $$d_z = \frac{\bar{\Delta}}{s_{\Delta}}$$
   $|d_z| \ge 0.8$ classified as a large practical effect.
2. **Cliff's Delta (Non-Parametric Probability of Superiority):**
   $$\delta = \frac{1}{N^2} \sum_{i=1}^N \sum_{j=1}^N \text{sign}(M_{\text{Track\_B}, i} - M_{B, j})$$

### 3.4 Multiple Comparison Correction (Section 102)
Across all pairwise baseline comparisons on a dataset, p-values are adjusted using the **Benjamini-Hochberg False Discovery Rate (FDR) procedure** at $q = 0.05$.

---

## 4. Multi-Objective Pareto Dominance Framework (Sections 168–173)

### 4.1 Formal Definition of Pareto Dominance (Section 169)
For two models $A$ and $B$ evaluated across an objective vector $\vec{f} = (f_1, \dots, f_m)$ where all objectives are to be minimized (e.g., Error, FLOPs, Memory):
$$\mathbf{A \prec B} \iff \forall j \in \{1, \dots, m\}, \; f_j(A) \le f_j(B) \quad \land \quad \exists k \in \{1, \dots, m\}, \; f_k(A) < f_k(B)$$

### 4.2 Standardized 2D Pareto Projections (Sections 170–173)
To ensure scientific interpretability without high-dimensional distortion, BENCH-01 defines three canonical 2D Pareto views:

#### View 1 (Primary Efficiency Frontier; Section 171):
- **Horizontal Axis ($X$):** Mean Operational FLOPs / step (Algorithmic Compute).
- **Vertical Axis ($Y$):** Normalized Mean Squared Error (NMSE), defined as:
  $$\text{NMSE} = \frac{\sum_{t=1}^T (y_t - \hat{y}_t)^2}{\sum_{t=1}^T (y_t - \bar{y}_t)^2}$$
- **Interpretation:** Highlights whether Track B achieves lower or comparable error at a lower computational footprint than dense baselines.

#### View 2 (Memory Efficiency Frontier; Section 172):
- **Horizontal Axis ($X$):** Persistent Deployment Memory ($M_{\text{STATIC}} + M_{\text{STATE}} + M_{\text{AUX}}$ in Bytes).
- **Vertical Axis ($Y$):** Normalized Mean Squared Error (NMSE).
- **Interpretation:** Tests whether Track B’s dynamic state allocation avoids the memory footprint of fixed-capacity baselines.

#### View 3 (Adaptation Velocity Frontier; Section 173):
- **Horizontal Axis ($X$):** Mean Operational FLOPs / step.
- **Vertical Axis ($Y$):** Post-Change Cumulative Regret ($R_{\text{post}}$, error accumulated over the first 500 steps following an abrupt regime shift).
- **Interpretation:** Evaluates whether Track B’s structural exploration accelerates recovery from concept drift without ballooning compute.

---

## 5. Pre-Registered Decision Criteria Mapping (Section 177)

| Empirical Benchmark Outcome | Pareto Classification | Pre-Registered Scientific Conclusion |
| :--- | :--- | :--- |
| **Case A** | Track B is on the Pareto frontier: matches predictive accuracy of ESN/GRU with $\ge 50\%$ lower FLOPs/memory. | **Efficiency Justification:** Dynamic lifecycle provides empirical computational parsimony. |
| **Case B** | Track B dominates static baselines in post-change recovery ($p < 0.01$) at resource parity (Regime R2). | **Continual Adaptation Justification:** Structural birth accelerates non-stationary tracking. |
| **Case C** | Track B uses fewer resources, but predictive loss is materially worse ($>25\%$ higher NMSE). | **Tradeoff Only:** Architectural parsimony degrades predictive fidelity; no superiority. |
| **Case D** | Static baselines (RZA-LMS, Minimal GRU) or CCN dominate Track B in both error and resources. | **Hypothesis Falsified:** Track B's complex lifecycle is not empirically justified. |
| **Case E** | Mixed, non-dominated outcomes across synthetic vs real-world tasks. | **Pareto Tradeoff:** Domain-dependent specialization; no universal advantage claim. |

---

## 6. Formal Certification of Statistical Plan Readiness (Section 252)

- **Audit Status:** **`STATISTICAL_PLAN_READY = YES`**.
- **Certification Statement:**  
  The statistical analysis plan is complete, non-parametric, multi-objective, and fully locked. It eliminates single-score manipulation, enforces 10,000-replicate bootstrap comparisons across 30 seeds, and pre-registers exact Pareto interpretation criteria.
