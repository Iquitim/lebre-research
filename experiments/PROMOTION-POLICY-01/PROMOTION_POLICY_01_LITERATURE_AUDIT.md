# PROMOTION-POLICY-01: Formal Literature Audit

**Stage:** PROMOTION-POLICY-01 — Sequential Structural Evidence & False-Promotion Control  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Purpose:** Audit sequential inference, prequential evaluation, anytime-valid statistics, online multiple testing, and dynamic structural growth literature to establish principled evidence mechanisms for structural candidate promotion in resource-governed adaptive systems.

---

## 1. Executive Framing: Candidate Promotion as Sequential Hypothesis Testing

In an online continual learner, the allocation of permanent architectural capacity (e.g., admitting a recurrent hidden unit $s_t$ into the live prediction path) is structurally irreversible or costly to evict. When a provisional structural candidate is spawned into shadow probation, the system must decide sequentially between:
- **Null Hypothesis ($\mathcal{H}_{0, j}$):** The candidate provides no durable predictive gain over the current live model ($\mathbb{E}[D_t] \le 0$ or $\le \delta_{\text{min}}$).
- **Alternative Hypothesis ($\mathcal{H}_{1, j}$):** The candidate provides sustained out-of-sample predictive improvement ($\mathbb{E}[D_t] > \delta_{\text{min}}$).

A **false structural promotion** (Type S1 error) allocates resources to a spurious unit, inducing parameter interference, gradient noise, and excess FLOP consumption. A **missed structural promotion** (Type S2 error) leaves the model under-parameterized, permanently missing discoverable temporal dependencies.

Below, we audit the nine foundational literature families relevant to this decision.

---

## 2. Comprehensive Method-by-Method Audit Across 9 Families

### Family A: Fixed-Horizon Effect Thresholds

#### A1. Conventional Prequential Empirical Threshold
- **Citation:** Dawid, A. P. (1984). *Present position and potential developments: Some personal views: Statistical theory: The prequential approach*. Journal of the Royal Statistical Society: Series A, 147(2), 278–292. [DOI: 10.2307/2981683](https://doi.org/10.2307/2981683).
- **Problem Setting:** Streaming model selection where candidate predictors are scored prequentially over a fixed horizon of $T$ samples.
- **Evidence Statistic:** Cumulative empirical relative gain $G_{\text{cand}}(T) = 1 - \frac{\sum_{t=1}^T L_{\text{cand}, t}}{\sum_{t=1}^T L_{\text{base}, t}}$.
- **Decision Mechanism:** Promote if $G_{\text{cand}}(T) > \theta_{\text{promote}}$ at fixed $t = T$.
- **Error-Control Target:** Heuristic point-estimate separation; no formal false-positive rate guarantee.
- **Assumptions:** Stationarity of the loss process over the evaluation window $[1, T]$.
- **Adaptive Data:** Compatible with adaptive streams, but does not account for parameter adaptation during the window.
- **Repeated Decisions Controlled:** **NO**. Applying a fixed threshold repeatedly across sequential candidate births inflates family-wise false discoveries.
- **Computational Complexity:** $\mathcal{O}(1)$ per step (sum accumulation).
- **Memory Complexity:** $\mathcal{O}(1)$ (2 scalar accumulators).
- **Direct Applicability to LEBRE:** Direct. This is the exact frozen baseline policy $P0$ ($T=50, \theta=0.05$).
- **Inclusion/Exclusion:** **INCLUDED** as frozen reference comparator ($P0$) and fixed-length control ($P1$).

---

### Family B: Two-Stage & Repeated Temporal Confirmation

#### B1. Progressive Temporal Validation / Hold-Out Split
- **Citation:** Stone, M. (1974). *Cross-validatory choice and assessment of statistical predictions*. Journal of the Royal Statistical Society: Series B, 36(2), 111–133; Prechelt, L. (1998). *Early stopping—but when?* Neural Networks: Tricks of the Trade, Springer, 55–69.
- **Problem Setting:** Guarding against overfitting to local sample noise by requiring performance replication on a subsequent disjoint temporal block.
- **Evidence Statistic:** Dual-window gains: $G_A = 1 - \frac{\sum_{t \in W_A} L_{\text{cand}, t}}{\sum_{t \in W_A} L_{\text{base}, t}}$ and $G_B = 1 - \frac{\sum_{t \in W_B} L_{\text{cand}, t}}{\sum_{t \in W_B} L_{\text{base}, t}}$.
- **Decision Mechanism:** Promote if $G_A > \theta_A$ AND $G_B > \theta_B$, where $W_A = [1, T_A]$ and $W_B = [T_A + 1, T_A + T_B]$.
- **Error-Control Target:** Heuristic empirical replication; sharp reduction in false positives caused by transient noise bursts.
- **Assumptions:** The predictive signal persists across regime transitions between $W_A$ and $W_B$.
- **Adaptive Data:** Compatible with online learning. Candidate continues adapting or is frozen during $W_B$.
- **Repeated Decisions Controlled:** Partially; requires independent temporal confirmation, drastically lowering noise pass-through.
- **Computational Complexity:** $\mathcal{O}(1)$ per step.
- **Memory Complexity:** $\mathcal{O}(1)$ (separate accumulators for Window A and Window B).
- **Direct Applicability to LEBRE:** High. Fits directly within LEBRE's streaming budget without buffer replay.
- **Inclusion/Exclusion:** **INCLUDED** as Policy $P3$ (`TWO_WINDOW_CONFIRM`).

---

### Family C: Sequential Probability Ratio Testing (SPRT)

#### C1. Classical Wald SPRT
- **Citation:** Wald, A. (1945). *Sequential tests of statistical hypotheses*. The Annals of Mathematical Statistics, 16(2), 117–186. [DOI: 10.1214/aoms/1177731118](https://doi.org/10.1214/aoms/1177731118).
- **Problem Setting:** Testing between two simple hypotheses $\mathcal{H}_0: \theta = \theta_0$ vs $\mathcal{H}_1: \theta = \theta_1$ with minimal sample size.
- **Evidence Statistic:** Log-likelihood ratio $\Lambda_t = \sum_{i=1}^t \ln \frac{f(x_i; \theta_1)}{f(x_i; \theta_0)}$.
- **Decision Mechanism:** Accept $\mathcal{H}_1$ if $\Lambda_t \ge \ln(B)$; accept $\mathcal{H}_0$ if $\Lambda_t \le \ln(A)$; continue otherwise.
- **Error-Control Target:** Exact Type I ($\alpha$) and Type II ($\beta$) error bounds at stopping times.
- **Assumptions:** **Strict i.i.d. observations** under exact known parametric densities $f(x; \theta)$.
- **Adaptive Data:** **VIOLATED**. Adaptive online gradient updates induce serial correlation and non-stationarity in prediction errors.
- **Repeated Decisions Controlled:** **NO**. Valid only for a single hypothesis test.
- **Computational Complexity:** $\mathcal{O}(1)$ per step.
- **Memory Complexity:** $\mathcal{O}(1)$.
- **Direct Applicability to LEBRE:** Low. True loss distributions are unknown, non-Gaussian, and serially dependent.
- **Inclusion/Exclusion:** **EXCLUDED** from primary implementations due to violated i.i.d. assumptions, but serves as conceptual foundation for anytime-valid martingales.

---

### Family D: Time-Uniform Confidence Sequences (CS)

#### D1. Nonparametric Time-Uniform Confidence Sequences
- **Citation:** Howard, S. R., Ramdas, A., McAuliffe, J., & Sekhon, J. (2021). *Time-uniform, nonparametric, nonasymptotic confidence sequences*. The Annals of Statistics, 49(2), 1055–1080. [DOI: 10.1214/20-AOS1991](https://doi.org/10.1214/20-AOS1991); Waudby-Smith, I., & Ramdas, A. (2023). *Estimating means of bounded random variables by betting*. Journal of the Royal Statistical Society: Series B, 86(1), 1–27.
- **Problem Setting:** Constructing confidence intervals $C_t = [\text{LCB}_t, \text{UCB}_t]$ for the mean $\mu$ of an adaptive process such that $\mathbb{P}(\forall t \ge 1, \mu \in C_t) \ge 1 - \alpha$.
- **Evidence Statistic:** Nonparametric stitching bound or empirical-Bernstein confidence sequence on paired differences $D_t = L_{\text{live}, t} - L_{\text{shadow}, t}$:
  $$\text{LCB}_t(D) = \bar{D}_t - \hat{\sigma}_t \sqrt{\frac{2(t v + 1) \ln(\frac{\ln(t v + 1) + 1}{\alpha})}{t^2 v}}$$
- **Decision Mechanism:** Promote when $\text{LCB}_t(D) > \delta_{\text{min}}$ (evidence that candidate is durably beneficial); discard when $\text{UCB}_t(D) < 0$ (futility).
- **Error-Control Target:** Anytime-valid Type I error control: $\mathbb{P}(\exists t: \text{promote} \mid \mu \le \delta_{\text{min}}) \le \alpha$.
- **Assumptions:** Conditionally sub-Gaussian or bounded random variables with known scale bound $c$.
- **Adaptive Data:** **YES**. Valid under adaptive filtrations (martingale differences).
- **Repeated Decisions Controlled:** Controlled within each candidate's lifetime; requires adjustment across multiple candidate births.
- **Computational Complexity:** $\mathcal{O}(1)$ per step (running mean, running variance, and scalar evaluation).
- **Memory Complexity:** $\mathcal{O}(1)$ (mean, variance, step counter).
- **Direct Applicability to LEBRE:** Very High. Provides principled adaptive stopping without fixed $T=50$.
- **Inclusion/Exclusion:** **INCLUDED** as Policy $P4$ (`CS_PROMOTION`).

---

### Family E: e-Processes & Betting Martingales

#### E1. Testing by Betting / e-Values
- **Citation:** Shafer, G., & Vovk, V. (2019). *Game-Theoretic Foundations for Probability and Finance*. John Wiley & Sons; Grünwald, P., de Heide, R., & Koolen, W. M. (2024). *Safe testing: safe anytime-valid inference with e-processes*. Journal of the Royal Statistical Society: Series B.
- **Problem Setting:** Testing sequential hypotheses by accumulating wealth in a game against the null hypothesis $\mathcal{H}_0: \mu \le \delta_{\text{min}}$.
- **Evidence Statistic:** Nonnegative supermartingale (e-process) $E_t = \prod_{i=1}^t (1 + \lambda_i (D_i - \delta_{\text{min}}))$, where $\lambda_i \in [0, 1/c)$ is a predictable betting fraction.
- **Decision Mechanism:** Promote when $E_t \ge 1/\alpha$ (by Ville's inequality, $\mathbb{P}(\exists t: E_t \ge 1/\alpha) \le \alpha$).
- **Error-Control Target:** Formal nonasymptotic, anytime-valid significance without requiring pre-specified sample size.
- **Assumptions:** Bounded differences $D_t \in [-c, c]$ and predictable $\lambda_t$.
- **Adaptive Data:** **YES**. Specifically designed for interactive and adaptive environments.
- **Repeated Decisions Controlled:** Within-candidate; e-values can be multiplied or averaged across streams.
- **Computational Complexity:** $\mathcal{O}(1)$ per step (scalar multiplication).
- **Memory Complexity:** $\mathcal{O}(1)$ (wealth scalar $E_t$).
- **Direct Applicability to LEBRE:** High, provided paired differences $D_t$ are clipped to a known range $[-c, c]$.
- **Inclusion/Exclusion:** Evaluated in comparative audit; because empirical CS ($P4$) provides direct scale-adaptive intervals, $P4$ is selected as the primary anytime-valid vehicle.

---

### Family F: Online Multiple Testing & FDR Control

#### F1. Alpha-Investing
- **Citation:** Foster, D. P., & Stine, R. A. (2008). *$\alpha$-investing: a strategy for controlling false discovery rate with applications to sequential variable selection*. Journal of the Royal Statistical Society: Series B, 70(2), 429–444. [DOI: 10.1111/j.1467-9868.2007.00643.x](https://doi.org/10.1111/j.1467-9868.2007.00643.x).
- **Problem Setting:** Testing a potentially infinite sequence of hypotheses arrival over time, controlling the marginal False Discovery Rate (mFDR).
- **Evidence Statistic:** Test $p$-value $p_k$ for candidate $k$ against assigned budget fraction $\alpha_k$.
- **Decision Mechanism:** Candidate $k$ is allocated $\alpha_k \le W_{k-1}$. If $p_k \le \alpha_k$, declare discovery (promote), and wealth increases by $\omega$ (earned return). If $p_k > \alpha_k$, candidate is rejected, and wealth decreases by $\alpha_k / (1 - \alpha_k)$.
- **Error-Control Target:** Proven mFDR control over arbitrary sequences of candidate tests.
- **Assumptions:** Valid $p$-values satisfying $\mathbb{P}(p_k \le u \mid \mathcal{H}_{0, k}) \le u$ conditionally on past filtration.
- **Adaptive Data:** Valid under adaptive hypotheses provided $p$-values are super-uniform under null.
- **Repeated Decisions Controlled:** **YES**. This explicitly solves the multiple-opportunity problem observed in LEBRE-DIAG-01 (35 attempts per seed).
- **Computational Complexity:** $\mathcal{O}(1)$ per candidate decision.
- **Memory Complexity:** $\mathcal{O}(1)$ (scalar wealth $W_k$).
- **Direct Applicability to LEBRE:** High as an *opportunity budgeting heuristic*. True formal $p$-values are difficult to guarantee without exact null distribution, but the wealth dynamics provide a natural control on candidate churn.
- **Inclusion/Exclusion:** **INCLUDED** as Policy $P5$ (`GLOBAL_ERROR_BUDGET`).

#### F2. LORD / LORD++ and SAFFRON
- **Citation:** Javanmard, A., & Montanari, A. (2018). *Online rules for control of false discovery rate*. IEEE Transactions on Information Theory, 64(2), 522–545; Ramdas, A., Zrnic, T., Wainwright, M. J., & Jordan, M. I. (2018). *SAFFRON: an adaptive algorithm for online control of the false discovery rate*. ICML 2018.
- **Problem Setting:** Online FDR control where testing levels $\alpha_k$ decay over time and increase upon discoveries.
- **Evidence Statistic:** $p$-values $p_k$ compared against candidate thresholds $\alpha_k = \sum_{j: \tau_j < k} \gamma_{k - \tau_j} W_0$.
- **Decision Mechanism:** Promote when $p_k \le \alpha_k$.
- **Error-Control Target:** Time-uniform FDR $\mathbb{E}[\text{FDP}_t] \le \alpha$.
- **Assumptions:** Independent or locally dependent valid $p$-values.
- **Direct Applicability to LEBRE:** Requires exact conditional $p$-values. Without exact $p$-values, alpha-investing wealth budgeting ($P5$) is more robust and natural for reinforcement-style evidence allocation.
- **Inclusion/Exclusion:** Synthesized into $P5$.

---

### Family G: Adaptive Sequential Multiple Testing

#### G1. Asynchronous and Structure-Adaptive Online Testing
- **Citation:** Tian, J., & Ramdas, A. (2021). *Online control of the familywise error rate for asynchronous and structured testing*. Journal of Machine Learning Research, 22(220), 1–38.
- **Problem Setting:** Sequential testing where candidate evaluation windows overlap in time (e.g., multiple candidates in probation simultaneously).
- **Evidence Statistic:** Asynchronous decay weights with conflict resolution.
- **Direct Applicability to LEBRE:** Frozen LEBRE v0.1 enforces $N_{\text{prov}} \le 1$ (at most one candidate on probation at any time). Hence, candidate tests are strictly sequential, making complex asynchronous graph routing unnecessary.
- **Inclusion/Exclusion:** EXCLUDED from primary code (not needed under $N_{\text{prov}} \le 1$).

---

### Family H: Progressive & Prequential Model Selection

#### H1. Interleaved Test-Then-Train Scoring
- **Citation:** Rissanen, J. (1984). *Universal coding, information, prediction, and estimation*. IEEE Transactions on Information Theory, 30(4), 629–636; Dawid, A. P. (1984).
- **Problem Setting:** Assessing model complexity and capacity expansion purely through predictive prequential code length / accumulated loss.
- **Evidence Statistic:** Cumulative predictive loss difference $\sum_{t=1}^T (L_{\text{base}, t} - L_{\text{cand}, t}) - \mathcal{R}(\text{complexity})$.
- **Decision Mechanism:** Promote if candidate's prequential loss reduction exceeds the structural complexity penalty (MDL principle).
- **Direct Applicability to LEBRE:** Forms the bedrock of LEBRE's prequential evaluation cycle.

---

### Family I: Dynamic Architecture Growth Policies

#### I1. Dynamically Expandable Networks (DEN) & Neurogenesis
- **Citation:** Yoon, J., Yang, E., Lee, J., & Hwang, S. J. (2018). *Lifelong Learning with Dynamically Expandable Networks*. ICLR 2018; Mocanu, D. C. et al. (2018). *Scalable training of artificial neural networks with dynamic sparse training*. Nature Communications, 9(1), 2383.
- **Problem Setting:** Allocating new units or synapses when task loss exceeds a threshold after retraining.
- **Evidence Statistic:** Stalled loss reduction on current capacity.
- **Decision Mechanism:** Train candidate subnetwork on replay buffer; add units if validation error drops below threshold.
- **Assumptions:** Availability of offline validation sets and replay buffers.
- **Direct Applicability to LEBRE:** Highlights why LEBRE's problem is strictly harder: LEBRE has **no replay buffer, no offline validation set, and no batch retraining**. Decisions must be made causal-prequentially in real time.

---

## 3. Comparative Synthesis & Architectural Applicability Matrix

| Family | Method | Formally Anytime Valid? | Handles Dependent Adaptive Data? | Controls Repeated Churn? | FLOP Overhead | Memory Overhead | Applicability to LEBRE |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A. Fixed-Horizon** | P0 (v0.1: $T=50, \theta=0.05$) | NO | Heuristic | NO | 0 | 0 | **Baseline Reference** |
| **A. Fixed-Horizon** | P1 (Long: $T=150$) | NO | Heuristic | NO | 0 | 0 | **Control (Sample Size)** |
| **A. Fixed-Horizon** | P2 (Strict: $\theta=0.15$) | NO | Heuristic | NO | 0 | 0 | **Control (Conservatism)** |
| **B. Two-Stage** | P3 (`TWO_WINDOW_CONFIRM`) | NO | Empirical Replication | Partial | $< 1$ FLOP | 8 Bytes | **High (Simplicity Candidate)** |
| **D. Confidence Seq.** | P4 (`CS_PROMOTION`) | **YES** (Approx sub-Gaussian) | **YES** | Within-unit | $\approx 6$ FLOPs | 24 Bytes | **High (Anytime Stopping)** |
| **F. Error Budget** | P5 (`GLOBAL_ERROR_BUDGET`) | Heuristic / Empirical | **YES** | **YES** | $< 2$ FLOPs | 16 Bytes | **High (Multiple-Opportunity)** |
| **D + F. Combined** | P6 (`CS_PLUS_BUDGET`) | Approx Anytime + Budget | **YES** | **YES** | $\approx 8$ FLOPs | 32 Bytes | **High (Compound Defense)** |

---

## 4. Conclusion of Literature Audit

1. **Root Cause Isolated:** Fixed 50-step empirical thresholds (Family A) are fundamentally vulnerable to two distinct statistical phenomena:
   - *Intra-candidate noise spikes:* Over a 50-step window, random fluctuations in orthogonal noise streams can easily yield transient $G_{\text{cand}} > 0.05$.
   - *Inter-candidate opportunity accumulation:* When birth attempts occur repeatedly ($\approx 35$ times per seed), uncorrected hypothesis testing guarantees structural false discoveries.
2. **Actionable Families:** Two-window temporal confirmation (Family B), empirical confidence sequences (Family D), and online error budgeting (Family F) directly target these two failure modes while respecting LEBRE's strict micro-edge constraints ($\le 100$ FLOPs, bounded memory, zero replay).
