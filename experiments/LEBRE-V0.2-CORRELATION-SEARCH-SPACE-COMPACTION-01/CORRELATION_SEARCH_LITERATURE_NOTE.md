# Correlation Search Space Compaction: Literature Review and Theoretical Grounding

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Author:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Status:** PREREGISTERED SCIENTIFIC LITERATURE AUDIT  

---

## 1. Scope and Epistemological Discipline

This literature review evaluates external signal processing and adaptive filtering precedents for reducing the computational burden of temporal delay discovery in streaming systems. Every proposition imported from external literature is strictly classified under one of three epistemic labels:
1. **`ESTABLISHED_EXTERNAL_MECHANISM`**: A mathematically proven or empirically validated theorem in signal processing.
2. **`CONCEPTUAL_ANALOGY`**: A theoretical parallel that provides structural intuition but does not directly map to LEBRE's prequential streaming constraints.
3. **`LEBRE_SPECIFIC_HYPOTHESIS`**: An unproven empirical conjecture specific to the LEBRE architecture that must be experimentally evaluated.

No novelty claims are asserted.

---

## 2. Bibliographic Review and Algorithmic Analysis

### 2.1 Variable Tap-Length Adaptive Filters
- **Citation:** Gong, Y., & Cowan, C. F. N. (2005). *"An LMS style variable tap-length algorithm for structure adaptation."* **IEEE Transactions on Signal Processing**, 53(7), 2400–2407. [DOI: 10.1109/TSP.2005.849170]
- **Established Principle (`ESTABLISHED_EXTERNAL_MECHANISM`):** In finite impulse response (FIR) filtering, adaptive filters can adjust their structural filter order / tap-length $L(n)$ dynamically based on gradient estimates of the squared error with respect to filter length. This trades computational complexity against steady-state excess mean-square error (EMSE).
- **Critical LEBRE Architectural Limitation:** Variable tap-length algorithms inherently optimize a **contiguous filter horizon** $[1, L(n)]$. In LEBRE benchmark task $I_4$, the true generating system is a sparse, non-contiguous multi-delay process ($x_{0, t-3}, x_{1, t-7}, x_{2, t-12}$). An algorithm that truncates or expands a contiguous boundary would be forced to allocate all intermediate taps ($1..12$), destroying the sub-100-FP budget.
- **Epistemic Invariant:** $\text{VARIABLE\_TAP\_LENGTH} \neq \text{SPARSE\_SUPPORT\_SELECTION}$. Gong & Cowan provides precedent for dynamic structural sizing, but cannot be applied as a contiguous filter-length rule.

### 2.2 Tap Selection Algorithms
- **Citation:** Kawamura, A., & Hatori, M. (1986). *"A TAP selection algorithm for adaptive filters."* **IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP 1986)**, 11, 1168–1172. [DOI: 10.1109/ICASSP.1986.1168762]
- **Established Principle (`ESTABLISHED_EXTERNAL_MECHANISM`):** When the number of true active coefficients $M$ is substantially smaller than the ambient hypothesis horizon $N$ ($M \ll N$), selecting and updating only a subset of $M$ tap positions reduces filter arithmetic by approximately the factor $M/N$.
- **Relevance to LEBRE (`CONCEPTUAL_ANALOGY`):** Inactive structural locations cannot be permanently discarded; they must retain a mechanism to re-enter eligibility when the environment undergoes non-stationary regime shifts.
- **Architectural Implementation:** Kawamura & Hatori provides direct historical precedent for a **rotating exploration queue** coupled with a bounded **hot frontier**. Inactive cells are periodically revisited via round-robin queue scheduling with guaranteed maximum silence intervals.

### 2.3 Partial-Update LMS Algorithms
- **Citation:** Godavarti, M., & Hero, A. O. (2005). *"Partial update LMS algorithms."* **IEEE Transactions on Signal Processing**, 53(7), 2382–2399. [DOI: 10.1109/TSP.2005.849167]
- **Established Principle (`ESTABLISHED_EXTERNAL_MECHANISM`):** Partial-update LMS algorithms update only a fraction of filter coefficients at each iteration (either sequentially or through Max-LMS decimation). While steady-state MSE can be asymptotically preserved under stationary conditions, update scheduling alters convergence rates and tracking dynamics.
- **Warning for LEBRE Streaming (`ESTABLISHED_EXTERNAL_MECHANISM`):** Subsampling or decimating search updates is not purely a computational optimization; under non-stationary regime changes (tasks $I_{11}, I_{12}, I_{14}$), subsampling alters the detection latency and transient convergence trajectory. Therefore, search subsampling must be evaluated for **discovery fidelity**, not merely FLOP savings.

### 2.4 Sparsity-Aware Adaptive Filtering
- **Citations:**
  - Martin, R. K., Sethares, W. A., Williamson, R. C., & Johnson, C. R. (2002). *"Exploiting sparsity in adaptive filters."* **IEEE Transactions on Signal Processing**, 50(8), 1883–1894. [DOI: 10.1109/TSP.2002.800414]
  - Chen, Y., Gu, Y., & Hero, A. O. (2009). *"Sparse LMS for system identification."* **IEEE International Conference on Acoustics, Speech, and Signal Processing (ICASSP 2009)**, 4397–4400. [DOI: 10.1109/ICASSP.2009.4960286]
- **Established Principle (`ESTABLISHED_EXTERNAL_MECHANISM`):** When the true parameter vector is sparse, incorporating $L_1$ or zero-attracting (ZA-LMS) penalties accelerates convergence and improves parameter estimation accuracy.
- **Critical Distinction for LEBRE:** Sparsity regularization penalizes live parameter weights; it does **not** eliminate the computational cost of evaluating cross-correlations across the ambient 165-cell search space to discover where those sparse non-zero coefficients reside. Regularization is an update penalty, not a hypothesis search-space compaction mechanism.
- **Epistemic Invariant:** Sparsity of the underlying plant does not imply that unvisited cells can be permanently pruned without ongoing exploration.

### 2.5 Matching Pursuit and Sparse Approximation
- **Citation:** Mallat, S. G., & Zhang, Z. (1993). *"Matching pursuits with time-frequency dictionaries."* **IEEE Transactions on Signal Processing**, 41(12), 3397–3415. [DOI: 10.1109/78.258082]
- **Conceptual Analogy (`CONCEPTUAL_ANALOGY`):** Candidate delay taps in LEBRE can be conceptualized as atoms in a discrete temporal dictionary $\mathcal{D} = \{x_{i, t-k} : i \in [0, 4], k \in [1, 32]\}$. Prequential correlation probing greedily correlates atoms against the current residual $e_{\text{base}}(t) = y(t) - \hat{y}_{\text{base}}(t)$.
- **Computational Limitation:** Standard Matching Pursuit requires exhaustive inner products across all $|\mathcal{D}| = 165$ dictionary atoms at each step. Applying Matching Pursuit naively would retain the full 165-cell dense search cost. The research challenge is specifically **dictionary-search subsampling**.

### 2.6 Time-Delay Estimation and Coarse-to-Fine Search
- **Citation:** Knapp, C., & Carter, G. C. (1976). *"The generalized correlation method for estimation of time delay."* **IEEE Transactions on Acoustics, Speech, and Signal Processing**, 24(4), 320–327. [DOI: 10.1109/TASSP.1976.1162830]
- **Established Principle (`ESTABLISHED_EXTERNAL_MECHANISM`):** Generalized cross-correlation estimates time delays by finding the peak of the cross-correlation function. In bandlimited or smoothed systems, multi-scale or coarse-to-fine search evaluates a coarse grid of delays and refines only around correlation peaks.
- **The Central Coarse-to-Fine Danger for LEBRE (`LEBRE_SPECIFIC_HYPOTHESIS`):** Coarse-to-fine search strictly relies on the assumption of **lag-score locality**:
  $$\text{score}(k) \gg 0 \implies \text{score}(k \pm 1) \gg 0$$
  In discrete-time streaming systems with white or weakly autocorrelated inputs, an exact delay $y(t) = x(t-5)$ produces a sharp Kronecker delta peak $\delta(k-5)$, where $\text{score}(4) \approx 0$ and $\text{score}(6) \approx 0$. A coarse grid testing only even lags $k \in \{2, 4, 6, 8\}$ would register near-zero correlation at $k=4$ and $k=6$, completely missing the true delay at $k=5$.
- **Governance Mandate:** Hierarchical search cannot be deployed based on theoretical optimism; it requires an empirical **Lag-Score Locality Audit** on DEV data before eligibility can be established.

---

## 3. Summary of Design Invariants for LEBRE v0.2

1. **Rotating Sparse Frontier ($C_1$):** Primary candidate architecture. Maintains a bounded hot frontier of $H \ll 165$ cells, fed by a deterministic exploration queue $B$ ensuring bounded silence $\text{MAX\_UNOBSERVED\_INTERVAL} < \infty$.
2. **Hierarchical Coarse-to-Fine ($C_2$):** Strictly conditional on empirical verification of lag-score locality on DEV data.
3. **No Hidden Dense State:** If an algorithm stores the full $5 \times 33$ correlation matrix in RAM, memory compaction is classified as `FAIL`.
4. **Descendant Cost Accounting:** Search cost includes all downstream candidate probation FLOPs triggered by search false positives.
