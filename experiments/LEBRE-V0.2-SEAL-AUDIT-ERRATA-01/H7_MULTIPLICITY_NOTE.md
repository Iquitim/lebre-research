# Methodological Note: Task-Level Multiplicity, Post-Selection Diagnostics & Hypothesis 7

**Audit Identifier:** `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Focus:** Statistical Lineage, Multiplicity Adjustments, and Confirmatory Status of Hypothesis 7 (Cascade Order Bias)  
**Author:** Independent Skeptical Scientific Auditor  
**Date:** September 2026  

---

## 1. Executive Summary of Findings

1. **The Headline Narrative Claim for $I_4$ is Fictitious:**
   - The assertion that *"On Task $I_4$, $|NMSE(T_1) - NMSE(T_{1R})| = 0.1654$ with $p = 1.86 \times 10^{-9}$"* is **arithmetically, statistically, and forensically false**.
   - On the sealed 30-seed confirmatory dataset (`LEBRE_V0_2_SEED_RESULTS.csv`):
     - $\text{Mean NMSE}(T_1) = 0.688941$
     - $\text{Mean NMSE}(T_{1R}) = 0.688169$
     - $\text{Difference of Means} = 0.000772$
     - $\text{Mean Absolute Paired Difference} = 0.047750$
     - Paired Wilcoxon Signed-Rank Test: $W = 225.0, \mathbf{p = 0.8872}$ (strictly non-significant!).
2. **Tripartite Lineage of the Spurious Headline:**
   The erroneous claim arose from a three-way compounding copy-forward error:
   - *Component A (DEV Table Paste):* In the pasted DEV Seed 1301 table, $I_4$ showed $T_1 = 0.4124$ and $T_{1R} = 0.5778$. The difference $|0.4124 - 0.5778| = 0.1654$.
   - *Component B (Borrowing the Benchmark Maximum from $I_8$):* In `scratch/compute_v02_statistics.py`, the code computed `max_bias = max(order_biases)` across all 14 tasks. The maximum occurred on **Task $I_8$** (`I8_Quiescent_Discrete_Delay`), where $\overline{|T_1 - T_{1R}|} = 0.165426$. The narrative report mistakenly attributed this maximum to $I_4$.
   - *Component C (Borrowing the $T_3$ vs. $T_1$ p-value):* In Section 4 of `LEBRE_V0_2_STATISTICAL_REPORT.md`, the win of $T_3$ over $T_1$ on $I_4$ had $W=0.0, p = 1.86 \times 10^{-9}$. The author transposed this p-value onto the comparison between $T_1$ and $T_{1R}$.

---

## 2. Preregistered Definition of $\rho_{\text{order}}$ vs. Post-Hoc Reformulation

In the frozen preregistered document `LEBRE_V0_2_INTEGRATION_HYPOTHESES.md` (lines 43–51), Hypothesis 3 / 7 was explicitly defined as:

$$\rho_{\text{order}} = \frac{1}{N} \sum_{s=1}^N \mathbb{I}(\text{Alloc}_{\text{T1}}(s) \ne \text{Alloc}_{\text{T1R}}(s))$$
*Text:* "the proportion of seeds where $T_1$ and $T_{1R}$ converge to materially different persistent structural allocations on ambiguous or redundant tasks ($I_{10}$)."
*Falsification Boundary:* "Falsified if $\rho_{\text{order}} \le 0.05$ across redundant and switching benchmarks."

**Audit Classification:**
- On task $I_{10}$, both $T_1$ and $T_{1R}$ converge to `Alloc = BOTH` ($\bar{K}=4.0, \bar{S}=1.0$) on **100% of seeds** ($s=1311..1340$).
- Therefore, under the strictly preregistered structural allocation formula:
  $$\rho_{\text{order}, I10} = \frac{0}{30} = \mathbf{0.000} \le 0.05$$
- Under the preregistered definition, **Hypothesis 7 is FALSIFIED**.
- During result analysis, the authors abandoned this structural definition and post-hoc substituted a predictive error metric:
  $$\max_{i \in \{1..14\}} |\text{NMSE}_i(T_1) - \text{NMSE}_i(T_{1R})|$$

---

## 3. Family-Wise Multiplicity Analysis Across Tasks $I_1$..$I_{14}$

Evaluating whether $T_1$ and $T_{1R}$ differ across 14 tasks constitutes a family of 14 non-independent hypotheses. Applying the step-down Holm-Bonferroni adjustment at family-wise error rate $\alpha = 0.05$:

| Rank | Benchmark Task | Diff of Means $|\bar{T}_1 - \bar{T}_{1R}|$ | Mean Abs Paired Diff $\overline{\|D\|}$ | Wilcoxon $W$ | Raw $p$-value | Holm $\alpha_{\text{crit}}$ | Holm Significant? |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | `I1_Memoryless_Linear` | 0.00012 | 0.00012 | 1.0 | 0.00444 | 0.00357 | **NO** |
| 2 | `I11_Regime_Switch_Delay_To_Latent` | 0.02464 | 0.03393 | 104.0 | 0.00711 | 0.00385 | **NO** |
| 3 | `I3_Single_Exact_Delay` | 0.07342 | 0.15864 | 155.0 | 0.11418 | 0.00417 | **NO** |
| 4 | `I8_Quiescent_Discrete_Delay` | 0.09321 | 0.16543 | 158.0 | 0.12935 | 0.00455 | **NO** |
| 5 | `I14_Intermittent_Hybrid` | 0.01192 | 0.03169 | 163.0 | 0.15795 | 0.00500 | **NO** |
| 6 | `I12_Regime_Switch_Latent_To_Delay` | 0.00114 | 0.00297 | 165.0 | 0.17060 | 0.00556 | **NO** |
| 7 | `I2_Static_Nonlinear_Negative_Control` | 0.00548 | 0.01731 | 167.0 | 0.18397 | 0.00625 | **NO** |
| 8 | `I7_Quiescent_Continuous_State` | 0.00175 | 0.00387 | 174.0 | 0.23665 | 0.00714 | **NO** |
| 9 | `I5_Moving_Delay_Support` | 0.02020 | 0.05852 | 182.0 | 0.30852 | 0.00833 | **NO** |
| 10 | `I10_Redundant_Temporal_Structure` | 0.00163 | 0.00517 | 189.0 | 0.38180 | 0.01000 | **NO** |
| 11 | `I6_Continuous_Latent_State` | 0.00046 | 0.00128 | 189.0 | 0.38180 | 0.01250 | **NO** |
| 12 | `I13_Regime_Switch_Hybrid_To_Memoryless`| 0.00395 | 0.02228 | 190.0 | 0.39305 | 0.01667 | **NO** |
| 13 | `I9_Hybrid_Delay_Plus_Latent_State` | 0.00846 | 0.04229 | 207.0 | 0.61201 | 0.02500 | **NO** |
| 14 | `I4_Multi_Sparse_Delay` | 0.00077 | 0.04775 | 225.0 | 0.88719 | 0.05000 | **NO** |

---

## 4. Key Takeaways & Claim Status

1. **Zero Tasks Survive Multiplicity Control:** After adjusting for family-wise testing across 14 tasks, **not a single task** exhibits a statistically significant difference between $T_1$ and $T_{1R}$ under the two-sided Wilcoxon signed-rank test.
2. **Substantial Descriptive Discrepancies Exist on Specific Tasks:** While inferential significance is absent after multiplicity correction, descriptive discrepancies between $T_1$ and $T_{1R}$ are practically meaningful on specific tasks:
   - On $I_8$ (`I8_Quiescent_Discrete_Delay`), the mean absolute paired difference is $0.1654$, and difference of means is $0.0932$;
   - On $I_3$ (`I3_Single_Exact_Delay`), the mean absolute paired difference is $0.1586$, and difference of means is $0.0734$.
   On these tasks, the order of module cascading creates stochastic divergence across individual runs.
3. **Formal Status of H7:**
   - Confirmatory status: **`DESCRIPTIVE_ONLY`** (or **`NOT_SUPPORTED_CONFIRMATORILY`** under preregistered structural criteria).
   - The headline claim of universal or extreme statistical significance ($p < 10^{-6}$) is **withdrawn**.
