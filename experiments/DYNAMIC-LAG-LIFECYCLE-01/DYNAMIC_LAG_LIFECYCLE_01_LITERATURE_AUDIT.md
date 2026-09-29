# DYNAMIC-LAG-LIFECYCLE-01: Pre-Experimental Literature Audit
## Causal Sparse Delay Discovery, Adaptive Tapped-Delay Filtering & Online Sparse System Identification

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Auditor:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, and Reproducibility Auditor  
**Date:** September 2026  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Status:** COMPLETE (Pre-Experimental Baseline)

---

## 1. Executive Context & Scope

`CAPACITY-DECOMPOSITION-01` established that the predictive failure of instantaneous streaming learners on delayed dependency benchmarks (**A2**, **A3**, **A4**) is causally attributable to a **finite temporal information deficit** (absence of past delay coordinates $\mathbf{x}_{t-\tau}$). An oracle sparse lag set ($T5$) instantly dropped NMSE to the Bayes floor ($0.363$) while satisfying micro-edge resource constraints (74 FLOPs/step, 420 Bytes).

However, in `CAPACITY-DECOMPOSITION-01`, the sparse lag coordinates were provided *oracularly*. This literature audit evaluates the theoretical foundation and historical precedent for **discovering, promoting, maintaining, and evicting sparse non-contiguous delay coordinates online** from streaming data without oracle knowledge.

We explicitly audit 9 foundational literature families to ground the experimental design, establish rigorous comparators, and prevent false novelty claims.

---

## 2. Comprehensive Audit Across 9 Theoretical Families

### Family A: Tapped-Delay-Line & Adaptive FIR System Identification
- **Foundational Works:** Widrow & Hoff (1960), Widrow & Stearns (1985), Haykin (2002) *Adaptive Filter Theory*.
- **Core Principles:** A finite impulse response (FIR) filter maps a single-input or multi-input sequence to an output via a linear combination of delayed regressors:
  $$y_t = \sum_{k=0}^{L-1} w_k x_{t-k} + e_t$$
  Standard adaptation uses Least Mean Squares (LMS) or Normalized LMS (NLMS) stochastic gradient updates:
  $$\mathbf{w}_{t+1} = \mathbf{w}_t + \frac{\mu}{\|\mathbf{x}_t\|^2 + \epsilon} e_t \mathbf{x}_t$$
- **Computational & Memory Cost:**
  - Filtering and weight update cost $\mathcal{O}(L)$ multiply-accumulates (MACs) per step (approx. $2L$ FLOPs).
  - Memory requires storing $L$ past scalar values in a circular tapped-delay-line buffer, plus $L$ coefficient weights ($2L$ words).
- **Relation to Discrete Delay Recovery:** If the true underlying system contains a single sparse delay at lag $\tau = 30$, a standard FIR filter requires an order $L \ge 31$. Consequently, 30 of the 31 filter coefficients are theoretically zero, but standard LMS updates all 31 weights every time step, incurring substantial gradient noise, slow convergence, and structural waste.
- **Novelty Caveat:** Tapped-delay lines and FIR filtering have been standard signal processing tools for over 60 years. LEBRE claims zero novelty in using delay buffers or linear tap coefficients.

---

### Family B: Variable Tap-Length Adaptive Filters
- **Mandatory Reference:** Gong & Cowan (2005), *"An LMS Style Variable Tap-Length Algorithm for Structure Adaptation"*, IEEE Transactions on Signal Processing, 53(7), pp. 2400–2407. DOI: `10.1109/TSP.2005.849170`.
- **Key Concepts:** Dynamically adapts the active filter length $L_t$ to minimize mean square error without wasting resources on irrelevant tail taps. Uses a fractional tap-length variable $l_t \in \mathbb{R}$ updated via gradient descent on instantaneous error:
  $$l_{t+1} = \left[ l_t - \alpha \nabla_{l} e_t^2 \right]$$
  where the gradient is approximated by measuring the energy of the tail coefficients $\sum_{k=L_t-\Delta}^{L_t} w_k^2$.
- **Subsequent Developments:** Zhang, Gu & Cowan (2008) introduced segmented and multi-boundary variable-tap-length schemes to mitigate gradient noise in $l_t$.
- **Critical Distinction from LEBRE:**
  > [!IMPORTANT]
  > **Contiguous Length vs. Sparse Non-Contiguous Lags:**
  > Variable tap-length algorithms answer: *"How long should the contiguous window $[0, L_t]$ be?"*  
  > If a relevant delay occurs at $\tau = 30$, a variable tap-length filter is forced to expand $L_t \ge 30$, maintaining 30 contiguous active taps $[0, 1, \dots, 30]$ even if taps $1 \dots 29$ are pure noise.
  > In contrast, LEBRE's problem is: *"Which sparse, non-contiguous coordinate-lag pairs $(i, k)$ deserve persistent capacity?"* (e.g., maintaining only tap $k=30$ while bypassing $1 \dots 29$).

---

### Family C: Proportionate Adaptive Filtering (PNLMS / IPNLMS)
- **Mandatory Reference:** Duttweiler (2000), *"Proportionate Normalized Least-Mean-Squares Adaptation in Echo Cancelers"*, IEEE Transactions on Speech and Audio Processing, 8(5), pp. 508–518. DOI: `10.1109/89.861368`.
- **Key Concepts:** In sparse impulse response identification (e.g., acoustic echo cancellation where direct sound and early reflections create sparse, non-zero taps among hundreds of zero coefficients), standard NLMS converges slowly because step-size is uniform across all taps. PNLMS assigns an individual time-varying step-size $g_k(t)$ proportional to the absolute magnitude of each weight:
  $$\mathbf{w}_{t+1} = \mathbf{w}_t + \mu \frac{\mathbf{G}_t \mathbf{x}_t}{\mathbf{x}_t^\top \mathbf{G}_t \mathbf{x}_t + \epsilon} e_t, \quad g_k(t) = \frac{\gamma_k(t)}{\sum_j \gamma_j(t)}, \quad \gamma_k(t) = \max\left(\rho \max_j |w_j(t)|, |w_k(t)|\right)$$
- **Subsequent Developments:** Benesty & Gay (2002) developed IPNLMS (Improved PNLMS) to balance proportionate adaptation for sparse paths and uniform adaptation for dispersive paths.
- **Relevance & Limitations as Comparator:**
  - PNLMS accelerates convergence of active taps, but **it still adapts all $L$ coefficients every time step**.
  - It does not structurally evict or compress zero taps. Memory remains $\mathcal{O}(L)$ and compute is $\mathcal{O}(L)$ with extra overhead to compute $\max_j |w_j(t)|$ and normalize $\mathbf{G}_t$.
  - Magnitude is an unreliable proxy for structural relevance: small taps in noisy channels can experience transient amplification.

---

### Family D: Sparsity-Promoting Adaptive Filters (Zero-Attracting LMS)
- **Mandatory Reference:** Gu, Jin & Mei (2009), *"$l_0$ Norm Constraint LMS Algorithm for Sparse System Identification"*, IEEE Signal Processing Letters, 16(9), pp. 774–777. DOI: `10.1109/LSP.2009.2024736`.
- **Key Concepts:** Adds penalty terms to the LMS cost function to force inactive taps toward zero:
  1. **Zero-Attracting LMS (ZA-LMS):** Penalizes $\ell_1$-norm:
     $$\mathbf{w}_{t+1} = \mathbf{w}_t + \mu e_t \mathbf{x}_t - \rho \operatorname{sgn}(\mathbf{w}_t)$$
  2. **Reweighted Zero-Attracting LMS (RZA-LMS):** Penalizes log-sum penalty $\sum_k \log(1 + \varepsilon |w_k|)$, attracting small weights more aggressively:
     $$\mathbf{w}_{t+1} = \mathbf{w}_t + \mu e_t \mathbf{x}_t - \rho \frac{\operatorname{sgn}(\mathbf{w}_t)}{1 + \varepsilon |w_k|}$$
  3. **$\ell_0$-LMS:** Approximates the $\ell_0$ pseudo-norm using continuous Gaussian/exponential approximations:
     $$\|\mathbf{w}\|_0 \approx \sum_k \left(1 - e^{-\alpha |w_k|}\right)$$
- **Critical Trade-Offs:**
  - Zero-attracting filters reduce steady-state tap variance on near-zero coefficients.
  - However, all $L$ taps remain physically present in memory and participate in vector dot-products.
  - Furthermore, if the system is not strictly sparse or when inputs are correlated, $\ell_1$ shrinkage introduces permanent bias on the non-zero coefficients.

---

### Family E: Online Sparse System Identification via Set-Theoretic Projections
- **Mandatory Reference:** Kopsinis, Slavakis & Theodoridis (2011), *"Online Sparse System Identification and Signal Reconstruction Using Projections Onto Weighted $\ell_1$ Balls"*, IEEE Transactions on Signal Processing, 59(3), pp. 936–952. DOI: `10.1109/TSP.2010.2090874`.
- **Key Concepts:** Formulates online sparse identification within the framework of Adaptive Projected Subgradient Method (APSM). At each step, the filter vector is projected onto hyperslabs satisfying the instantaneous data constraints and onto a weighted $\ell_1$ ball $\mathcal{B}_{\ell_1}^w$ whose radius is adjusted online.
- **Sparse Estimation vs. Sparse History Acquisition Caveat:**
  > [!CAUTION]
  > Kopsinis et al. and related projection algorithms solve **Sparse Estimation**: given that the full delayed regressor vector $\mathbf{x}_t = [x_t, x_{t-1}, \dots, x_{t-L+1}]^\top$ is already constructed and present in memory, find a sparse weight vector $\mathbf{w}_t$.
  > They do **NOT** solve **Sparse History Acquisition**: the algorithm assumes that all $L$ past inputs are maintained in memory and multiplied during projections. Thus, memory complexity is strictly $\Omega(D \cdot L)$, which can violate embedded micro-edge limits when $D$ or $L$ is large.

---

### Family F: Online Sparse Learning & Feature Selection
- **Audited Works:**
  1. Langford, Li & Zhang (2009), *"Sparse Online Learning via Truncated Gradient"*, Journal of Machine Learning Research (JMLR), 10, pp. 777–801. Truncates small gradient updates periodically to induce exact zeros in streaming linear models.
  2. Yang et al. (2023), *"Online Linearized LASSO"*, AISTATS / PMLR, 206, pp. 4120–4138. Applies linearized proximal Bregman updates with time-decaying regularization to guarantee optimal regret under sparse streaming regimes.
  3. Yang & Sun (2026), *"Online Generalized Sparse Regression: How Does Overparametrization Help?"*, JMLR. Studies support recovery in overparameterized sparse streaming models under restricted isometry conditions.
- **Assumptions & Applicability:**
  - These frameworks provide rigorous theoretical regret bounds, but require strict mathematical conditions: Restricted Isometry Property (RIP), restricted eigenvalue bounds, or independent sub-Gaussian features.
  - In tapped delay lines, successive features $[x_t, x_{t-1}, \dots]$ from dynamic processes exhibit strong temporal autocorrelation, directly violating strict RIP conditions.
  - In addition, they assume the candidate feature dictionary is fixed and evaluated every step.

---

### Family G: Partial-Update Adaptive Filtering
- **Foundational Works:** Douglas (1997), *"Adaptive Filters Employing Partial Updates"*, IEEE Trans. Circuits Syst. II; Werner & Diniz (2001); Dogancay (2008) *Partial-Update Adaptive Signal Processing*.
- **Key Concepts:** To reduce compute on micro-edge processors, only a subset $M < L$ of filter coefficients are updated at step $t$:
  1. **Periodic Partial Update:** Taps are partitioned into blocks updated cyclically.
  2. **Selective / M-Max Partial Update:** Computes the magnitude of all tap inputs $|x_{t-k}|$ or instantaneous gradients $|e_t x_{t-k}|$, sorts them, and updates only the $M$ taps with the largest magnitude.
- **Crucial Accounting Rule:**
  > [!WARNING]
  > **No Free Partial Update:**  
  > An algorithm is **NOT** low-compute if selecting the $M$ taps requires scanning, calculating, or sorting all $D \cdot L_{\max}$ candidates at every step. Sorting $N$ items costs $\mathcal{O}(N \log N)$ or $\mathcal{O}(N)$. In LEBRE's resource ledger, candidate search, scheduling, and scanning costs are fully charged.

---

### Family H: Time-Varying Sparse Support Tracking
- **Audited Works:** Angelosante, Bazerque & Giannakis (2010), *"Online Adaptive Estimation of Sparse Signals Where Support Changes Over Time"*, IEEE Trans. Signal Process.; Eksioglu (2011), *"Sparsity-regularized RLS for time-varying sparse systems"*.
- **Key Concepts:** Distinguishes between:
  1. Parameter drift (fixed support, shifting weights);
  2. Support relocation (old non-zero taps vanish, new non-zero taps appear);
  3. Dynamic birth and death of structural components.
- **Relevance to LEBRE:** LEBRE's two-timescale structural lifecycle directly addresses support relocation. When an active tap's predictive contribution declines, its slow relevance metric decays toward eviction, while a rotating candidate probing mechanism detects the emergence of new predictive lag coordinates.

---

### Family I: Online Change Detection
- **Audited Works:** Adams & MacKay (2007), *"Bayesian Online Changepoint Detection"* (BOCPD); Basseville & Nikiforov (1993) *Detection of Abrupt Changes*.
- **Key Concepts:** Computes the posterior run-length distribution $P(r_t \mid \mathbf{x}_{1:t})$ sequentially using recursive message passing over predictive hazard functions.
- **Architectural Decision:** BOCPD requires maintaining a growing tree or pruned mixture of hypotheses, costing $\mathcal{O}(r_{\max})$ per step in memory and compute. LEBRE tracks structural obsolescence through continuous exponential relevance statistics ($R_{i, k}$) rather than discrete hypothesis trees, achieving robust support transition tracking without dedicated change-point detectors.

---

## 3. Literature Audit Comparator Table

| Reference & Year | Primary Verified | Streaming? | Fixed Dict? | Full Delay Vector Required? | Sparse Support Discovery? | Support Retirement? | Time-Varying Support? | Known Order Req? | Per-Step Compute | Persistent Memory | Selection / Sort Cost | Direct Applicability to LEBRE |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Widrow & Hoff (1960)** | Yes | Yes | Yes | Yes | No | No | No | Yes | $2L$ FLOPs | $2L$ words | None | Baseline FIR (B3) |
| **Gong & Cowan (2005)** | Yes | Yes | Yes | Yes (Contiguous) | No (Length only) | Yes (Tail only) | Yes (Contiguous) | No | $2L_t + 4$ FLOPs | $2L_t$ words | None | Variable Length (B4) |
| **Duttweiler (2000)** | Yes | Yes | Yes | Yes | Yes (Proportionate) | No (Continuous) | Yes | Yes | $4L + \mathcal{O}(1)$ | $3L$ words | Max search $\mathcal{O}(L)$ | PNLMS (B6) |
| **Gu et al. (2009)** | Yes | Yes | Yes | Yes | Yes ($\ell_0$ shrinkage) | Yes (Zero attract) | Yes | Yes | $3L$ FLOPs | $2L$ words | None | Sparse LMS (B5) |
| **Kopsinis et al. (2011)** | Yes | Yes | Yes | Yes | Yes (Ball Proj) | Yes | Yes | Yes | $\mathcal{O}(L \log L)$ | $4L$ words | Sorting $\mathcal{O}(L \log L)$ | APSM Sparse Reg |
| **Langford et al. (2009)** | Yes | Yes | Yes | Yes | Yes (Trunc Grad) | Yes | Partial | Yes | $2L$ FLOPs | $2L$ words | None | Online Truncation |
| **Douglas (1997)** | Yes | Yes | Yes | Yes | Partial | No | No | Yes | $2M + \text{sort}$ | $2L$ words | $\mathcal{O}(L \log M)$ | Partial-Update FIR |
| **Angelosante (2010)** | Yes | Yes | Yes | Yes | Yes (Tracking) | Yes | Yes | Yes | $\mathcal{O}(L^2)$ | $\mathcal{O}(L^2)$ words | Matrix inv | RLS Sparse Track |
| **Adams & MacKay (2007)**| Yes | Yes | Yes | N/A | No | No | Yes | No | $\mathcal{O}(R)$ | $\mathcal{O}(R)$ words | Pruning | BOCPD Detector |
| **LEBRE Dynamic Lag (B7)**| Proposed | Yes | **No (Dynamic)** | **No (Sparse Buffers)**| **Yes (Causal Probes)** | **Yes (Two-Timescale)**| **Yes (Full Reloc)**| **No ($L_{\max}$ bound)**| **$\le 100$ FLOPs** | **$\le 1024$ Bytes** | **$\mathcal{O}(M)$ Rotating** | **Target Architecture** |

---

## 4. Key Takeaways & Novelty Discipline

1. **Prior Art Solves Sparse Estimation, Not Bounded-History Acquisition:**
   Virtually all sparse adaptive filtering literature (ZA-LMS, PNLMS, APSM, Truncated Gradient) assumes that a complete tapped delay vector $\mathbf{x}_t \in \mathbb{R}^{D \cdot L_{\max}}$ is readily available in memory at every step. They sparsify the *weights*, not the *history buffer*.
2. **Contiguous Tap-Length is Insufficient for Dispersed Delays:**
   Gong & Cowan's variable tap-length filter expands contiguously, wasting capacity on uninformative intermediate lags.
3. **No Free Candidate Search:**
   Proportionate adaptation and selective partial updates incur hidden sorting and scanning costs that must be accounted for on micro-edge devices.
4. **Novelty Non-Claims:**
   Tapped delay lines, sparse LMS, variable tap lengths, and online feature selection are established technologies. LEBRE claims **zero novelty** from combining these standard terms. The scientific question investigated here is whether a resource-bounded two-timescale structural lifecycle can govern sparse temporal coordinates without oracle knowledge.
