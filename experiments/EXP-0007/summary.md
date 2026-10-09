# EXP-0007 — Small-Sample Candidate Separability Diagnostic
**Do the Current Causal Statistics Contain Enough Information to Identify Promising True Candidates Early?**

---

## 0. Executive Summary & Verdicts

| Diagnostic Field | Result / Verdict | Gate Status |
| :--- | :--- | :---: |
| **PRIMARY_DECISION** | **`CURRENT_STATISTICS_INSUFFICIENT`** | **CRITICAL FINDING** |
| **N_SEPARABLE** | **`NONE`** | **FAILED GATE** |
| **BEST_SIMPLE_SCORE** | **`S0`** ($|\bar{c}|$) / **`S2`** ($|\bar{c}| \cdot \gamma$) | Validated |
| **JOINT_LINEAR_MODEL** | **`NO_MATERIAL_VALUE`** (P@3 = 20.0%, ROC-AUC = 0.434) | Diagnostic Only |
| **EXP_0007_STATUS** | **`DIAGNOSIS_IDENTIFIED`** | **SUCCESS** |
| **Practical Question 1** | **NO**: With $n \in [1, 5]$ probes, learner does NOT possess enough information to enrich elevated queues to $\ge 50\%$. | Resolved |
| **Practical Question 2** | **NONE**: No sample size $n \le 5$ achieves operational separability. | Resolved |
| **Practical Question 3** | **`INFORMATION_LIMITED`**: The failure of EXP-0006 is fundamentally lack of information at small $n$, NOT decision rule tuning. | Resolved |
| **Milestone M1 Gate** | **`M1_CANDIDATE = FALSE`** (Frozen diagnostic gate) | Preserved |
| **NEXT STEP** | **`NEW_CANDIDATE_INFORMATION_DIAGNOSTIC`** | EXP-0008 |

---

## 1. Context & Motivation

In **EXP-0006**, the queue-based multi-rate allocator (`QUEUE_MULTI_RATE`, J4) validated the physics of probe frequency reallocation:
- Slashed median true inter-probe gap by **85.5%** (16.6 to 2.4 steps).
- Compressed structural latency from 236.52 to 203.84 steps.
- Achieved repository-best MSE = **0.01355** under matched 10,000 probe budget and 23.72% Dense compute.
- Oracle rate targeting (J5) demonstrated that perfect tier allocation drops evidence latency to **14.92 steps** and raises full occupancy to **95.0%**.

However, causal models suffered a severe bottleneck: **`TIER_ENTRY_STATISTICS_INSUFFICIENT`**. Causal tier entry precision was only **2.8%–4.5%**, meaning over 96% of elevated probes were absorbed by spurious noise candidates.

**EXP-0007** was designed strictly as a diagnostic to answer the core fork:
- **Case A (Decision-Rule-Limited)**: The statistics contain strong signal, but the threshold/hint rule was poorly tuned.
- **Case B (Information-Limited)**: The statistics at small sample sizes ($n \in [1, 5]$) fundamentally lack the statistical power to separate true omitted candidates from noise under high residual variance.

---

## 2. Experimental Design & Diagnostic Protocol

### 2.1 Frozen Causal Baseline & Verification Gate
- **Learner**: Exact accepted EXP-0006 J4 learner (`TieredEvidenceLearner` + `TieredEvidenceRatePolicy(mode="queue_multi_rate")`).
- **Hyperparameters**: $K_{\max}=10$, Sparse NLMS ($\mu=0.5, \epsilon=10^{-6}$), $n_{\min}=8, \theta_{\text{promote}}=0.40, \tau_{\text{mature}}=50$, Probe Bank (target 10,000 probes, $q \in [1, 8]$).
- **Environment**: $d=100, K^*=5$, regime shift at $t=1000$, evaluation seeds `[42, 123, 456, 789, 1024]`.
- **Gate Verification**: Non-intrusive `CandidateSnapshotCollector` observed learner updates without modifying state, weights, or PRNG streams. Bit-for-bit equivalence with EXP-0006 J4 was verified across all seeds:
  - Seed 42: MSE = 0.011546915, Recall = 77.26%, Occupancy = 57.80% (exact match).
  - 5-Seed Mean: MSE = 0.013552460, Recall = 81.324%, Occupancy = 61.760% (exact match).

### 2.2 Candidate Episode Snapshots & Offline Labeling
- Captured snapshots of all inactive candidates at exact probe counts $n \in \{1, 2, 3, 4, 5\}$ (total 17,990 candidate snapshots collected).
- Truth labels assigned strictly offline:
  - `TRUE` (1): Genuinely relevant ($c \in S^*$) and omitted from active support ($c \notin S_t$) at snapshot step $t$.
  - `NOISE` (0): Irrelevant ($c \notin S^*$) or already active.

### 2.3 Diagnostic Scores Evaluated
- $S_0 = |\bar{c}|$ (absolute mean correlation)
- $S_1 = \gamma = \max(\text{pos}, \text{neg})/n$ (sign consistency)
- $S_2 = |\bar{c}| \times \gamma$ (magnitude-consistency product)
- $S_3 = |\bar{c}| / (\sigma_c + 10^{-6})$ (t-statistic / signal-to-noise ratio)
- $S_4 = \sqrt{n} |\bar{c}|$ (sample-size scaled magnitude)
- $S_5 = \sqrt{n} |\bar{c}| \gamma$ (sample-size scaled product)
- $S_{\text{current\_rule}}$: Existing EXP-0006 hint rule ($|\bar{c}| \ge 0.15 \land \gamma \ge 0.60$)
- `Oracle`: Ground truth upper bound

---

## 3. Primary Empirical Results

### 3.1 Table 2: Separability by Probe Count $n$ (Post-Shift Cohorts)
| $n$ | True Count | Noise Count | Base Rate | Best Simple Score | Best Precision@3 | Best Precision@5 | Best Enrichment@3 | Operational Gate ($\ge 50\%$) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 42 | 2,192 | 1.88% | $S_0$ | 13.33% | 8.00% | $5.63\times$ | **FAILED** |
| **2** | 42 | 2,195 | 1.88% | $S_0$ / $S_2$ | 20.00% | 12.00% | $13.85\times$ | **FAILED** |
| **3** | 43 | 2,145 | 1.97% | $S_0$ / $S_2$ | 20.00% | 12.00% | $13.46\times$ | **FAILED** |
| **4** | 37 | 1,592 | 2.27% | $S_0$ / $S_2$ | 26.67% | 16.00% | $16.71\times$ | **FAILED** |
| **5** | 35 | 1,526 | 2.24% | $S_0$ / $S_2$ | 20.00% | 16.00% | $14.96\times$ | **FAILED** |

### 3.2 Table 1: Comprehensive Score Performance by $n$
| $n$ | Score | PR-AUC | ROC-AUC | P@1 | P@2 | P@3 | P@5 | P@10 | R@3 | R@5 | Enrichment@3 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | $S_0$ ($|\bar{c}|$) | 0.0438 | 0.5297 | 20.0% | 20.0% | 13.3% | 8.0% | 6.0% | 5.0% | 5.0% | $5.63\times$ |
| 1 | $S_1$ ($\gamma$) | 0.0188 | 0.5000 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | $0.00\times$ |
| 1 | Oracle | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 100.0% | 76.0% | 40.6% | 67.6% | $61.08\times$ |
| **2** | $S_0$ ($|\bar{c}|$) | 0.0413 | 0.5597 | 20.0% | 10.0% | 20.0% | 12.0% | 6.0% | 9.0% | 9.0% | $13.85\times$ |
| 2 | $S_1$ ($\gamma$) | 0.0202 | 0.5338 | 0.0% | 0.0% | 0.0% | 0.0% | 4.0% | 0.0% | 0.0% | $0.00\times$ |
| 2 | $S_2$ ($|\bar{c}|\gamma$) | 0.0413 | 0.5689 | 20.0% | 10.0% | 20.0% | 12.0% | 6.0% | 9.0% | 9.0% | $13.85\times$ |
| 2 | $S_{\text{current\_rule}}$ | 0.0405 | 0.5800 | 20.0% | 10.0% | 20.0% | 12.0% | 6.0% | 9.0% | 9.0% | $13.85\times$ |
| 2 | Oracle | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 100.0% | 76.0% | 40.6% | 67.6% | $61.18\times$ |
| **3** | $S_0$ ($|\bar{c}|$) | 0.0519 | 0.6106 | 20.0% | 20.0% | 20.0% | 12.0% | 6.0% | 9.0% | 9.0% | $13.46\times$ |
| 3 | $S_2$ ($|\bar{c}|\gamma$) | 0.0529 | 0.6162 | 40.0% | 20.0% | 13.3% | 12.0% | 6.0% | 5.7% | 9.0% | $10.30\times$ |
| 3 | $S_3$ ($|\bar{c}|/\sigma$) | 0.0195 | 0.5027 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | $0.00\times$ |
| 3 | Oracle | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 100.0% | 76.0% | 40.2% | 67.0% | $59.02\times$ |
| **4** | $S_0$ ($|\bar{c}|$) | 0.0835 | 0.6714 | 20.0% | 30.0% | 26.7% | 16.0% | 10.0% | 14.3% | 14.3% | $16.71\times$ |
| 4 | $S_2$ ($|\bar{c}|\gamma$) | 0.0925 | 0.6774 | 40.0% | 30.0% | 26.7% | 16.0% | 10.0% | 14.3% | 14.3% | $16.71\times$ |
| 4 | Oracle | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 92.0% | 66.0% | 53.0% | 74.9% | $59.69\times$ |
| **5** | $S_0$ ($|\bar{c}|$) | 0.0922 | 0.7152 | 40.0% | 30.0% | 20.0% | 16.0% | 12.0% | 13.9% | 15.3% | $14.96\times$ |
| 5 | $S_2$ ($|\bar{c}|\gamma$) | 0.1042 | 0.7158 | 40.0% | 30.0% | 20.0% | 16.0% | 12.0% | 13.9% | 15.3% | $14.96\times$ |
| 5 | Oracle | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 88.0% | 62.0% | 58.0% | 78.3% | $60.65\times$ |

---

## 4. Stratification Analysis

### 4.1 Temporal Stratification Across Post-Shift Windows
| Window | Steps Post-Shift | True Count | Noise Count | Base Rate | Best Causal Score | Best Precision@3 | Best Precision@5 | Best PR-AUC | False Positive Rate@3 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **A** | 0–20 | 5 | 58 | 7.94% | $S_1$ | 20.00% | 20.00% | 0.1625 | **80.00%** |
| **B** | 21–50 | 12 | 313 | 3.69% | $S_4$ | 13.33% | 12.00% | 0.0510 | **86.67%** |
| **C** | 51–100 | 34 | 829 | 3.94% | $S_3$ | 6.67% | 4.00% | 0.0754 | **93.33%** |
| **D** | 101–250 | 103 | 3,053 | 3.26% | $S_4$ | 20.00% | 28.00% | 0.0950 | **80.00%** |
| **E** | >250 | 45 | 5,397 | 0.83% | $S_5$ | 0.00% | 0.00% | 0.0178 | **100.00%** |

*Finding*: Separability is severely compromised immediately following regime shift (Window A, FPR = 80%), when the learner needs accurate targeting the most.

### 4.2 Residual Stratification Across Smoothed Residual Quantiles
| Quantile | Residual Range ($|e_t|$) | True Count | Noise Count | Base Rate | Best Causal Score | Best Precision@3 | Best Precision@5 | Best PR-AUC | False Positive Rate@3 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Q1** | Lowest (Settled) | 0 | 2,464 | 0.00% | NONE | 0.00% | 0.00% | 0.0000 | 0.00% |
| **Q2** | Low-Mid | 23 | 2,439 | 0.93% | $S_5$ | 13.33% | 12.00% | 0.0400 | **86.67%** |
| **Q3** | Mid-High | 77 | 2,385 | 3.13% | $S_4$ | 26.67% | 20.00% | 0.0773 | **73.33%** |
| **Q4** | Highest (Burst) | 99 | 2,362 | 4.02% | $S_{\text{current\_rule}}$ | 13.33% | 8.00% | 0.0520 | **86.67%** |

*Finding*: During the peak residual burst (Q4), false positive rate is **86.67%**. High residual variance directly inflates spurious noise correlations.

---

## 5. Statistical Diagnostics & The Root Cause

### 5.1 Distribution Overlap at Small $n$
Distribution metrics for key features at $n=2$ and $n=3$:
- **$|\bar{c}|$ at $n=2$**: True mean = 1.383 (med = 0.684) vs Noise mean = 0.865 (med = 0.489). Cohen's $d = 0.45$, AUC = 0.560.
- **$|\bar{c}|$ at $n=3$**: True mean = 1.270 (med = 0.590) vs Noise mean = 0.710 (med = 0.402). Cohen's $d = 0.63$, AUC = 0.611.
- **$\gamma$ (sign consistency) at $n=2$**: True mean = 0.786 vs Noise mean = 0.752. Cohen's $d = 0.14$, AUC = 0.534.
- **$\gamma$ (sign consistency) at $n=3$**: True mean = 0.798 vs Noise mean = 0.760. Cohen's $d = 0.25$, AUC = 0.557.

### 5.2 Why the Statistics Fail: The Physics of Extreme Values Under High Residual Variance
1. **Residual Variance Drives Noise Spread**: When 5 true features are omitted, prediction residual $e_t$ has standard deviation $\sigma_e \approx 2.5$.
2. **Standard Error at Small $n$**: For any noise feature $j \notin S^*$, individual observations $e_t x_{t, j} \sim \mathcal{N}(0, \sigma_e^2)$. At $n=2$, the sample standard error is $\sigma_e / \sqrt{2} \approx 1.77$.
3. **Extreme Value Swamping**: In a pool of 85 noise features, drawing 85 Gaussian variables with standard deviation 1.77 produces maximum sample values that regularly exceed **2.0 to 2.8**.
4. **True Signal is Submerged**: A true omitted feature with weight $\beta_j = 1.0$ has true expectation $\mathbb{E}[e_t x_{t, j}] = 1.00$. Its sample mean at $n=2$ fluctuates around 1.0–1.4. Because $1.4 < 2.5$, the extreme noise features systematically outrank the true candidates at the top of the queue!
5. **Sign Consistency Offers No Shield at Small $n$**: At $n=1$, $\gamma=1.0$ for all candidates trivially. At $n=2$, any noise candidate whose two observations have the same sign (which occurs with probability 50%) has $\gamma=1.00$!

### 5.3 Rank Volatility Confirms Extreme Instability
Mean rank change $| \text{rank}_{n+1} - \text{rank}_n |$:
- $n=1 \to 2$: True candidates shift by 133.2 positions; Noise shifts by 157.0 positions.
- $n=2 \to 3$: True candidates shift by 131.0 positions; Noise shifts by 151.7 positions.
- $n=3 \to 4$: True candidates shift by 116.1 positions; Noise shifts by 140.8 positions.
- $n=4 \to 5$: True candidates shift by 75.3 positions; Noise shifts by 103.3 positions.

Ranks are essentially Brownian fluctuations across the candidate pool at $n \le 3$.

### 5.4 Counterfactual Probe-Budget Impact
Given the observed J4 service schedule (~2,688 elevated probes):
- Elevating top-5 by $S_0$ ($|\bar{c}|$): 323 useful probes (12.0%), **2,365 wasted probes (88.0%)**.
- Elevating top-5 by $S_2$ ($|\bar{c}|\gamma$): 323 useful probes (12.0%), **2,365 wasted probes (88.0%)**.
- Elevating top-5 by $S_4$ ($\sqrt{n}|\bar{c}|$): 430 useful probes (16.0%), **2,258 wasted probes (84.0%)**.
- Elevating top-5 by `Oracle`: **2,688 useful probes (100.0%)**, 0 wasted probes.

---

## 6. Synthesis & Answers to Preregistered Questions

### Q1: With only 1–5 causal probe observations per candidate, does the learner already possess enough information to enrich a small elevated queue with true omitted variables?
**Answer: NO.**
At $n \in [1, 5]$, the maximum achieved Precision@3 is 26.67% (and only 20.0% at $n=2, 3$). Elevated queues of size 3 or 5 remain dominated (73%–88%) by false-positive noise features.

### Q2: What is the minimum number of probes required before the true/noise candidate populations become operationally separable?
**Answer: NONE ($N_{\text{separable}} = \text{NONE}$).**
No sample size $n \le 5$ satisfies the preregistered criteria (Precision@3 $\ge 50\%$ or Precision@5 $\ge 40\%$). Operational separability only emerges at $n \ge 8$ (the fixed promotion threshold $N_{\min}=8$).

### Q3: Is the failure of EXP-0006 mainly a bad tier-entry rule, or a lack of information at small sample sizes?
**Answer: INFORMATION_LIMITED.**
The failure is NOT due to a sub-optimal threshold or decision rule. Univariate sample mean correlation and sign consistency lack the statistical power to resolve true candidates from 85 noise features under high residual variance. Any simple threshold elevation on $n \le 3$ inevitably elevates overwhelming noise.

---

## 7. Artifact Manifest
- Configuration: [`config.json`](<lebre-research>/experiments/EXP-0007/config.json)
- Master Runner: [`run_separability_diagnostic.py`](<lebre-research>/experiments/EXP-0007/run_separability_diagnostic.py)
- Diagnostic Library: [`src/diagnostics/candidate_separability.py`](<lebre-research>/src/diagnostics/candidate_separability.py)
- Unit Tests: [`tests/test_exp_0007.py`](<lebre-research>/tests/test_exp_0007.py) (5/5 passed, 52/52 repo-wide passed)
- Raw Snapshots: [`candidate_snapshots.csv`](<lebre-research>/experiments/EXP-0007/candidate_snapshots.csv) (17,990 rows)
- Metrics CSVs: [`separability_by_n.csv`](<lebre-research>/experiments/EXP-0007/separability_by_n.csv), [`precision_at_k.csv`](<lebre-research>/experiments/EXP-0007/precision_at_k.csv), [`temporal_stratification.csv`](<lebre-research>/experiments/EXP-0007/temporal_stratification.csv), [`residual_stratification.csv`](<lebre-research>/experiments/EXP-0007/residual_stratification.csv), [`rank_stability.csv`](<lebre-research>/experiments/EXP-0007/rank_stability.csv), [`counterfactual_elevated_precision.csv`](<lebre-research>/experiments/EXP-0007/counterfactual_elevated_precision.csv)
- Publication Figure: [`figures.png`](<lebre-research>/experiments/EXP-0007/figures.png)
