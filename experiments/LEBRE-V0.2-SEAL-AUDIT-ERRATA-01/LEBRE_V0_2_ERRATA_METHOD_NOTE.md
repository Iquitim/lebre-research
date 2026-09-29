# LEBRE v0.2 Errata Audit Methodological Note

**Audit Identifier:** `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Parent Studies:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`, `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Scientific Auditor  
**Date:** September 2026  
**Status:** Methodological Framework Locked  

---

## 1. Purpose and Guiding Philosophy

This errata audit does not introduce new model architectures, tune hyperparameters, optimize resources, or modify canonical source code (`src/` and `tests/` remain 100% bitwise immutable). Its sole purpose is **forensic claim-lineage reconciliation**: ensuring that every substantive statistical and architectural claim asserted in support of Topology $T_3$ (Resource-Aware Conditional Arbitration) traces without gap, ambiguity, or numerical contamination to the sealed raw confirmatory dataset ($N=30$ paired seeds, `1311`..`1340`).

In accordance with rigorous scientific software auditing:
$$\text{RAW CONFIRMATORY CSV} \longrightarrow \text{FROZEN SCRIPT} \longrightarrow \text{TRANSFORMATION} \longrightarrow \text{EXPLICIT STATISTIC} \longrightarrow \text{SCOPED CLAIM}$$
no report text, markdown table, or derived claim is treated as ground truth. If a published figure of merit cannot be programmatically regenerated from raw data under a preregistered formula, it is classified as unverified and corrected.

---

## 2. Core Literature Foundations

### 2.1 Preregistration and Discovery Boundaries
- **Reference:** Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). *The Preregistration Revolution*. **Proceedings of the National Academy of Sciences (PNAS)**, 115(11), 2600–2606. DOI: [10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114).
- **Methodological Principle Applied:** Confirmatory inference requires that decision rules, target tasks, and statistical test families be specified *prior* to data inspection. When an analysis is conducted *post-hoc*—such as selecting the maximum discrepancy task across 14 benchmark streams or altering a metric definition—the resulting observation represents exploratory discovery. Exploratory findings may generate valuable scientific hypotheses, but they cannot retrospectively inherit the epistemic status of an a priori confirmatory test without adjusting for post-selection multiplicity.

### 2.2 Analytical Flexibility and Researcher Degrees of Freedom
- **Reference:** Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). *False-Positive Psychology: Undisclosed Flexibility in Data Collection and Analysis Allows Presenting Anything as Significant*. **Psychological Science**, 22(11), 1359–1366. DOI: [10.1177/0956797611417632](https://doi.org/10.1177/0956797611417632).
- **Methodological Principle Applied:** Undisclosed flexibility in selecting:
  1. *Metrics* (e.g., substituting total co-allocation rate for thresholded redundant co-allocation rate);
  2. *Subsets* (e.g., reporting a maximum discrepancy on a selected single task rather than aggregate task performance);
  3. *Aggregation procedures* (e.g., conflating the difference of means $|\bar{T}_1 - \bar{T}_{1R}|$ with the mean absolute paired difference $\overline{|T_1 - T_{1R}|}$);
  artificially inflates evidential certainty. In this errata audit, all metric definitions, numerators, denominators, and aggregation levels are explicitly decoupled, formalized in an operational dictionary, and reported side-by-side.

### 2.3 Benchmark Variance and Seed Independence
- **Reference:** Bouthillier, X., Laurent, C., & Vincent, P. (2021). *Accounting for Variance in Machine Learning Benchmarks*. **Proceedings of Machine Learning and Systems (MLSys)**, 3, 747–769.
- **Methodological Principle Applied:** Machine learning evaluations in online and streaming domains are stochastic processes driven by signal realizations, noise sequences, and weight initializations. Comparing algorithms requires preserving the independent random seed as the primary inferential unit ($N=30$, seeds `1311`..`1340`). Timesteps, candidate events, and task instances cannot be pooled as independent replicates. Furthermore, developmental screening seeds (specifically Seed 1301) must be strictly quarantined from confirmatory recomputations through automated software assertions (`assert seed != 1301`).

### 2.4 Paired Nonparametric Comparison
- **Reference:** Demšar, J. (2006). *Statistical Comparisons of Classifiers over Multiple Data Sets*. **Journal of Machine Learning Research (JMLR)**, 7, 1–30.
- **Methodological Principle Applied:** For evaluating whether two adaptive filtering topologies (e.g., $T_1$ vs. $T_{1R}$) perform differently on a given streaming task, the two-sided Wilcoxon signed-rank test is the standard non-parametric paired comparison. However, Demšar emphasizes that:
  - Within-problem paired comparisons over independent random runs (seeds) test algorithm stability and stochastic dominance on that specific data-generating process;
  - Testing multiple tasks constitutes a family of hypotheses, requiring multiplicity control (e.g., Holm-Bonferroni correction);
  - A small p-value on a large sample or a tiny effect size ($|\Delta| < \Delta_{\text{equiv}}$) does not establish practical or engineering significance. Magnitude (effect size $d_z$, bootstrap confidence interval) must be reported alongside inferential p-values.

### 2.5 Computational Reproducibility Rules
- **Reference:** Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). *Ten Simple Rules for Reproducible Computational Research*. **PLOS Computational Biology**, 9(10), e1003285. DOI: [10.1371/journal.pcbi.1003285](https://doi.org/10.1371/journal.pcbi.1003285).
- **Methodological Rules Applied:**
  - *Rule 1 (Keep track of how every result was produced):* Every number in the errata report must be generated by an executable script (`generate_errata_outputs.py`).
  - *Rule 2 (Avoid manual data manipulation steps):* No value may be manually transcribed or copy-pasted.
  - *Rule 3 (Archive exact raw data and code):* Cryptographic SHA256 hashes must seal all parent files prior to errata computation.
  - *Rule 7 (Always store raw data behind plots):* All plots are rendered directly from generated summary CSVs.

### 2.6 Artifact Badging Principles (ACM / NeurIPS)
- **Framework:** ACM Artifact Review and Badging (v1.1) / NeurIPS Artifact Evaluation Guidelines.
- **Lineage Verification:**
  $$\text{Raw Data (Level 1)} \xrightarrow{\text{Script}} \text{Summary (Level 2)} \xrightarrow{\text{Statistical Engine}} \text{Table/Figure (Level 4)} \xrightarrow{\text{Narrative}} \text{Claim (Level 5)}$$
  If a conflict exists between Level 5 (narrative) and Level 1 (raw confirmatory data), Level 1 governs absolutely.

---

## 3. Methodological Execution Rules for this Errata Audit

1. **The Markdown Value is the Object of the Audit, Not the Truth:** When evaluating whether $T_1$ and $T_{1R}$ differ by $0.1654$ or whether $T_2$ exhibits $48.2\%$ redundant allocation, the markdown report value is treated as an unverified assertion. The auditor computes the value from Level 1 data first, and only compares with the markdown text second.
2. **Strict Separation of Descriptive vs. Inferential Claims:** Descriptive sample statistics (means, medians, maximums) describe the sample in hand. Inferential p-values test null hypotheses against defined sampling distributions. Conflating a descriptive sample maximum with an inferential hypothesis test is prohibited.
3. **Strict Separation of Architectural Symmetry from Cascade Discrepancy:** The claim that $T_3$ possesses internal evaluation-order invariance ($D \to R \equiv R \to D$) is an intrinsic architectural property that is mathematically and experimentally verified on $T_3$ independently of whether $T_1$ and $T_{1R}$ differ on any specific task.
4. **Distinguishing Dual Occupancy from Redundant Dual Occupancy:** Two modules simultaneously active in an online model is not inherently wasteful (e.g., on hybrid task $I_9$, joint occupancy is necessary and complementary). Redundancy is a context-dependent property requiring both concurrent live cost and negligible conditional predictive contribution ($G_{\text{cond}} \le \theta_{\text{tol}}$).
