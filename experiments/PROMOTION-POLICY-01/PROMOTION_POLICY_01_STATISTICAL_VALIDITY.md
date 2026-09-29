# PROMOTION-POLICY-01: Formal Statistical Validity & Assumptions Audit

**Stage:** PROMOTION-POLICY-01 — Sequential Structural Evidence & False-Promotion Control  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Purpose:** Rigorous audit of formal inferential guarantees versus empirical heuristics for all evaluated promotion policies, ensuring zero ungrounded mathematical claims.

---

## 1. Primary Inferential Validity Audit Table

| Policy | Statistical Object | Core Formal Assumptions | Are Assumptions Verified in Online LEBRE? | Formal Guarantee Applies? | What Guarantee? | Classification |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| **P0: Frozen Baseline** | Fixed empirical ratio $G_{\text{cand}}(50)$ | Stationary loss, single hypothesis test | **NO** (loss is non-stationary; multiple tests occur) | **NO** | None (heuristic point threshold) | `HEURISTIC_POINT_ESTIMATE` |
| **P1: Fixed Long** | Fixed empirical ratio $G_{\text{cand}}(150)$ | Stationary loss over 150 steps | **NO** (same limitations as P0) | **NO** | None (sample size expansion only) | `HEURISTIC_POINT_ESTIMATE` |
| **P2: Fixed Strict** | Fixed empirical ratio $G_{\text{cand}}(50) > 0.15$ | Stationary loss | **NO** | **NO** | None (conservatism threshold) | `HEURISTIC_CONSERVATIVE` |
| **P3: Two-Window Confirm** | Bivariate out-of-sample joint test $(G_A, G_B)$ | Independent validation split | **PARTIAL** (prequential causality holds, but errors are serially correlated) | **NO** | Empirical replication; no exact tail bound | `EMPIRICAL_REPLICATION_HEURISTIC` |
| **P4: Confidence Sequence** | Empirical-Bernstein stitching LCB $\text{LCB}_t(D)$ | Conditionally sub-Gaussian martingale difference sequence | **APPROXIMATE** (clipped loss differences have finite conditional variance, but serial autocorrelation violates strict independence) | **NO** (approximate asymptotic validity only) | Time-uniform bounded false discovery under sub-Gaussianity | `EMPIRICAL_CS_INSPIRED` |
| **P5: Global Error Budget** | Alpha-investing wealth tracker $W_k$ | Super-uniform valid $p$-values under null ($\mathbb{P}(p_k \le u) \le u$) | **NO** (exact $p$-values unavailable for adaptive online filter) | **NO** | Formal mFDR theorem requires valid $p$-values; acts as empirical opportunity budget | `ERROR_BUDGET_INSPIRED_HEURISTIC` |
| **P6: CS + Budget** | Composite anytime bound + wealth tracker | Sub-Gaussianity + super-uniformity | **APPROXIMATE / NO** | **NO** | Compound heuristic combining early stopping with churn throttling | `COMPOUND_HEURISTIC` |

---

## 2. Explicit Grounding on Formal FDR & Anytime Validity

### 2.1 Why Formal Online FDR (LORD/SAFFRON/Alpha-Investing) Cannot Be Formally Claimed
- The classical theorems of Foster & Stine (2008) and Ramdas et al. (2018) require that for every hypothesis $\mathcal{H}_{0, k}$, the system provides a valid $p$-value $p_k$ satisfying:
  $$\mathbb{P}(p_k \le \alpha \mid \mathcal{H}_{0, k}) \le \alpha \quad \forall \alpha \in (0, 1)$$
- In a continual, non-stationary adaptive filter, the predictive error difference $D_t = e_{\text{base}, t}^2 - e_{\text{cand}, t}^2$ depends on evolving weights $\mathbf{w}_t$, input covariance shifts, and nonlinear target dependencies. Deriving exact, non-conservative conditional $p$-values without asymptotic normal assumptions or offline permutation tests is an open statistical problem.
- **Auditor Mandate:** We explicitly declare: **FORMAL FDR CONTROL IS NOT CLAIMED**. Policy $P5$ is evaluated and reported strictly as an **Online-Testing-Inspired Structural Opportunity Budget**.

### 2.2 Why Time-Uniform Confidence Sequences (CS) Are Labeled "Empirical CS-Inspired"
- Howard et al. (2021) and Waudby-Smith & Ramdas (2023) established that stitching and betting bounds yield exact anytime-valid nonasymptotic coverage $\mathbb{P}(\forall t \ge 1, \mu_t \in C_t) \ge 1 - \alpha$ under conditionally 1-sub-Gaussian or bounded increments.
- In LEBRE, while inputs are normalized via `CausalStandardScaler`, squared errors $(y_t - \hat{y}_t)^2$ can be heavy-tailed during sudden target innovations. Although clipping $D_t \in [-c, c]$ guarantees boundedness, serial dependence between successive gradient updates means increments are not martingale differences under the standard marginal filtration.
- **Auditor Mandate:** Policy $P4$ is labeled `EMPIRICAL_CS_INSPIRED_ONLY`. It is not claimed to be a mathematically certified anytime-valid test under unverified conditions.

---

## 3. Scientific Integrity Conclusion

All policy variants are judged by their **empirical Pareto performance** across:
1. True false-promotion suppression on negative controls (A2–A4).
2. Useful structural recall on positive controls (A5/A7).
3. Micro-edge computational and memory overhead ($\le 100$ FLOPs/step).

No statistical textbook claims are asserted without established assumptions.
