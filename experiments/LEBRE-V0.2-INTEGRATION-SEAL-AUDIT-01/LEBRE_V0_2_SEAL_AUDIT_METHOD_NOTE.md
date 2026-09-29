# Methodological Foundations for Forensic Seal Audit

**Study Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Audited Subject:** `LEBRE-V0.2-INTEGRATION-DESIGN-01` (`T3_RESOURCE_AWARE_CONDITIONAL_ARBITRATION`)  
**Role:** Independent Skeptical Senior Reviewer  
**Status:** METHODOLOGICAL REFERENCE NOTE  

---

## 1. Overview & Purpose

This document establishes the scientific, statistical, and software verification standards governing the forensic seal audit of the architectural integration study `LEBRE-V0.2-INTEGRATION-DESIGN-01`.

The objective of a seal audit is **not** to rehabilitate an imperfect result or find ad-hoc justifications for candidate architectures. The objective is to determine whether the reported claims are mathematically sound, reproducible from sealed artifacts, traceable to preregistered protocols, and compliant with historical resource governance.

---

## 2. Theoretical & Methodological Foundations

### 2.1 Preregistration and Confirmatory Integrity
- **Literature References:**
  - Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). *The preregistration revolution*. Proceedings of the National Academy of Sciences (PNAS), 115(11), 2600–2606. DOI: 10.1073/pnas.1708274114.
  - Nosek, B. A., Beck, E. D., Campbell, L., Flake, J. K., Hardwicke, T. E., Mellor, D. T., van 't Veer, A. E., & Vazire, S. (2019). *Preregistration is hard, and worthwhile*. Trends in Cognitive Sciences, 23(10), 815–818.
- **Methodological Principle Applied:**
  Confirmatory claims derive statistical validity exclusively from decision criteria, exclusion thresholds, evaluation windows, and analysis plans established **prior** to observing confirmatory test data. Any alteration made after data inspection—even if technically motivated—relinquishes confirmatory status. In this audit, all post-hoc modifications must be formally isolated and labeled as:
  - `POST_HOC`
  - `EXPLORATORY`
  - `GOVERNANCE_REVISION`
  Silent substitution of criteria between protocol and final report is strictly prohibited.

---

### 2.2 Analytical Flexibility and Researcher Degrees of Freedom
- **Literature Reference:**
  - Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). *False-positive psychology: Undisclosed flexibility in data collection and analysis allows presenting anything as significant*. Psychological Science, 22(11), 1359–1366.
- **Methodological Principle Applied:**
  Undisclosed flexibility in metric selection, aggregation windows, threshold definitions, or baseline definitions can artificially generate apparent statistical significance or apparent gate compliance. 
  *(Note: We do not transfer psychology-specific numerical false-positive rates to machine learning; rather, we adopt the general epistemic warning that undisclosed flexibility invalidates nominal significance).*
  In this audit, every threshold (e.g., $\Delta_{\text{equiv}}$, $\theta_{\text{tol}}$, eviction cutoffs, RAM limits) is audited for provenance and timeline alignment.

---

### 2.3 Accounting for Variance in Machine Learning Benchmarks
- **Literature Reference:**
  - Bouthillier, X., Delaunay, P., Bronzi, M., Trofimov, A., Nichyporuk, B., Szeto, J., Sepahvand, N., Raff, E., Madan, K., Voleti, V., Ebrahimi, S., Belilovsky, E., Vincent, P., Lacoste, A., & Varoquaux, G. (2021). *Accounting for variance in machine learning benchmarks*. Proceedings of Machine Learning and Systems (MLSys), 3, 747–769.
- **Methodological Principle Applied:**
  Point estimates of streaming performance (e.g., single-seed NMSE) are inherently stochastic. Scientifically valid benchmarking requires:
  1. Independent seed-level replication;
  2. Paired statistical testing when multiple algorithms are evaluated on identical realization streams;
  3. Explicit reporting of variance, distributions, and confidence intervals;
  4. Complete provenance preservation for hyperparameter and stream generation seeds.
  Pseudoreplication (treating consecutive timesteps or pooled task runs as independent replicates) is statistically invalid.

---

### 2.4 Reproducible Computational Artifacts and Provenance
- **Literature References:**
  - Association for Computing Machinery (ACM). *ACM Artifact Review and Badging Version 1.1* (Artifacts Evaluated: Reusable / Reproducible).
  - NeurIPS Conference. *Reproducibility Checklist & Guidelines for Benchmark Datasets*.
- **Methodological Principle Applied:**
  Computational research must provide a complete, deterministic, and exercisable lineage connecting raw outputs to published claims:
  $$\text{Raw Stream Outputs} \longrightarrow \text{Documented Transformations} \longrightarrow \text{Aggregated Metrics} \longrightarrow \text{Statistical Tests} \longrightarrow \text{Table Cells / Figures}$$
  Every number reported in a paper or technical report must be recomputable via automated scripts from sealed data files without manual intervention or hard-coded constants.

---

### 2.5 Multidimensional Benchmarking for Resource-Constrained Systems
- **Literature Reference:**
  - Banbury, C., Reddi, V. J., Torelli, P., Holleman, J., Natarajan, N., Lam, M., Cowan, D., Wang, X., Wang, Z., Jeffries, P., et al. (2021). *MLPerf Tiny Benchmark*. Proceedings of the Neural Information Processing Systems (NeurIPS) Track on Datasets and Benchmarks, 1.
- **Methodological Principle Applied:**
  In edge and TinyML computing, system performance cannot be compressed into a single scalar predictive score (e.g., NMSE). Evaluation requires simultaneous, disaggregated characterization across orthogonal resource axes:
  - Predictive accuracy (prequential error);
  - Floating-point compute expenditure (live vs. shadow);
  - Integer indexing overhead;
  - Memory bus traffic (bytes read/written per step);
  - Static and dynamic RAM footprints.
  Aggregate temporal averages must not conceal burst costs, peak transients, or worst-case regime expenditures.

---

### 2.6 Benchmark Configuration Integrity & Benchmarking Crimes
- **Literature Reference:**
  - van der Kouwe, E., Andriesse, D., Bos, H., Giuffrida, C., & Heiser, G. (2018). *Benchmarking crimes: An emerging threat in systems security*. arXiv:1801.02381.
- **Methodological Principle Applied:**
  Systematic benchmarking vulnerabilities include:
  1. Comparing selective subset metrics of one system against full-pipeline metrics of another;
  2. Shifting measurement boundaries post-hoc;
  3. Selectively evaluating baselines under suboptimal configurations;
  4. Conflating diagnostic reference baselines with actual theoretical oracles.
  In this audit, measurement boundaries for $T_1, T_{1R}, T_2, T_3,$ and $O_{\text{ALL}}$ are strictly standardized.

---

### 2.7 Multi-Objective Vector Pareto Dominance
- **Formal Definition:**
  Let $\mathbf{f}(\mathbf{x}) = [f_1(\mathbf{x}), f_2(\mathbf{x}), \dots, f_M(\mathbf{x})]^\top$ be a vector of $M$ objective functions to be minimized.
  Candidate $A$ **strictly Pareto-dominates** candidate $B$ ($A \prec B$) if and only if:
  $$\forall m \in \{1, \dots, M\}, \quad f_m(A) \le f_m(B) \quad \land \quad \exists m \in \{1, \dots, M\}, \quad f_m(A) < f_m(B)$$
- **Methodological Restriction:**
  If $A$ is superior to $B$ on accuracy ($f_1(A) < f_1(B)$) but inferior on total compute ($f_2(A) > f_2(B)$), $A$ and $B$ are **non-dominated mutual trade-offs**. 
  Claiming that $A$ "strictly vector Pareto-dominates" $B$ when $f_2(A) > f_2(B)$ is mathematically false. A candidate may be *preferred* under a specific scalarization or live-path filtering, but it cannot be described as strictly dominating the full objective vector.
