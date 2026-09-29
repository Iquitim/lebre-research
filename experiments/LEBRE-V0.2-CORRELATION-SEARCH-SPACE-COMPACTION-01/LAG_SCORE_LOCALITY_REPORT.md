# Lag-Score Locality Audit Report

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Phase 1 Diagnostic Gate  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Locality Verdict:** **`LAG_SCORE_LOCALITY_NOT_SUPPORTED`**  
**Coarse-to-Fine Eligibility:** **`COARSE_TO_FINE_ELIGIBLE = NO`**  

---

## 1. Objective and Predeclared Criteria

Hierarchical coarse-to-fine delay search relies on the assumption of **lag-score locality**: that an evidence peak at lag $k$ produces an elevated correlation signature at neighboring lags $k \pm 1$ or $k \pm 2$. Under Section 19 of the Protocol and Section 1 of the Preregistration, hierarchical search is eligible if and only if:
1. **Neighbor Rank Correlation:** $r(\text{score}(k), \text{score}(k \pm 1)) \ge 0.60$;
2. **True-Lag Neighborhood Recall:** A coarse anchor within $\pm 1$ of a true delay captures $\ge 70\%$ of the peak correlation magnitude in $\ge 70\%$ of evaluated regimes.

---

## 2. Empirical Findings from DEV Streams (Seeds 1801..1810)

Across $N=10$ independent DEV streams on discrete delay tasks ($I_3, I_4, I_5, I_8, I_9, I_{11..14}$), a total of **4915 active correlation samples** ($|\rho| \ge 0.20$) on true delay coordinates were audited:

| Metric | Preregistered Threshold | Observed DEV Value | Status |
| :--- | :--- | :--- | :--- |
| **True Lag Mean Peak Score** | Reference | **0.7706** | Peak Signal |
| **Immediate Neighbor Mean Score ($k \pm 1$)** | $> 0.70 \times \text{Peak}$ | **0.1398** | Near Noise Floor |
| **Mean Neighbor Recall Ratio** | $\ge 0.70$ | **0.2650 (26.5%)** | **FAIL** |
| **Neighbor Rank Correlation ($r$)** | $\ge 0.60$ | **0.2176** | **FAIL** |
| **Fraction Capturing $\ge 70\%$ of Peak** | $\ge 70.0\%$ | **3.64%** | **FAIL** |

---

## 3. Physical and Mathematical Root Cause

The mathematical basis of this failure is fundamental to digital signal processing:
- In LEBRE's prequential streaming benchmark, observable input features $X_t$ are drawn from Gaussian white innovations with near-zero temporal autocorrelation ($E[X_{i, t} X_{i, t-k}] \approx 0$ for $k \ne 0$).
- When the target contains an exact discrete delay $y_t = w \cdot X_{i, t-k^*} + \dots$, the cross-correlation between the linear base residual $e_{\text{base}}(t)$ and $X_{i, t-k}$ evaluates to:
  $$E[e_{\text{base}}(t) X_{i, t-k}] = \begin{cases} w \cdot \sigma_X^2, & k = k^* \\ 0, & k \ne k^* \end{cases}$$
- Consequently, the correlation landscape over lag index is a **Kronecker delta spike** $\delta(k - k^*)$, not a smoothed Gaussian or Lorentzian peak.
- Immediate neighbors $k^* \pm 1$ reflect only sample estimation noise (approx 0.02 to 0.05).
- A coarse grid that evaluates only coarse anchors (e.g. $k \in \{2, 4, 8, 12, \dots\}$) registers near-zero correlation whenever the true delay falls on an odd lag (such as $k^*=3$ on $I_4$ or $k^*=5$ on $I_3$). The coarse anchor never crosses the refinement threshold, resulting in **catastrophic, irreversible false negatives**.

---

## 4. Governance Verdict and Invariant Decision

- **`LAG_SCORE_LOCALITY_STATUS`:** **`NOT_SUPPORTED`**
- **`COARSE_TO_FINE_ELIGIBLE`:** **`NO`**
- **Mandatory Decision:** Candidate family $C_2$ (Hierarchical Coarse-to-Fine Search) is **formally disqualified** from proceeding to the FINAL confirmatory evaluation.
- The project will focus deployable screening and confirmatory evaluation exclusively on **$C_1$ (Rotating Sparse Frontier)**, which does not rely on lag-score smoothness and provides guaranteed non-zero visit coverage via its exploration queue.
