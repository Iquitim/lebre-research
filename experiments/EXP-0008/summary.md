# EXP-0008 — Candidate Information Channel Diagnostic
**Can a Cheap Micro-Intervention Reveal Whether a Candidate Actually Improves Future Prediction?**

---

## 0. Executive Summary & Diagnostic Decisions

| Field | Decision / Result | Status |
| :--- | :--- | :---: |
| **PRIMARY_DECISION** | **`CURRENT_MICRO_INTERVENTIONS_INSUFFICIENT`** | **CRITICAL FINDING** |
| **BEST_INFORMATION_CHANNEL** | **`EXCESS_CAUSAL_GAIN`** (Sham-subtracted predictive gain) | P@3 = 20.0%, P@5 = 16.0% |
| **MIN_USEFUL_MICRO_TESTS** | **`NONE`** | Fails $\ge 50\%$ Gate |
| **INFORMATION_STATUS** | **`INTERVENTIONAL_INFORMATION_INSUFFICIENT`** | Resolved |
| **EXP_0008_STATUS** | **`DIAGNOSIS_IDENTIFIED`** | **SUCCESSFUL DIAGNOSTIC** |
| **Q115 (Learn more via shadow trial?)** | **NO** (On natural stream, single/few-step shadow gain is swamped by noise variance) | Resolved |
| **Milestone M1 Gate** | **`M1_CANDIDATE = FALSE`** (Frozen diagnostic gate) | Preserved |
| **NEXT STEP** | **`ACTIVE_PROBE_DESIGN_DIAGNOSTIC`** | EXP-0009 |

---

## 1. Motivation & Context

In **EXP-0007**, passive candidate-residual correlation ($\bar{c}, |\bar{c}|, \gamma$) was shown to be **information-limited** at small sample counts ($n \le 5$). When 5 true features are omitted post-shift, prediction error variance spikes to $\sigma_e \approx 2.55$. Across 85 noise candidates, the extreme values of random Gaussian correlations regularly reach $2.5 - 3.5$, submerging true signals ($\mathbb{E}[c] \approx 1.0$).

**EXP-0008** was designed to test a fundamentally different physical information channel:
Instead of asking *"Does this candidate look correlated with current error?"*, ask:
> *"If I let this candidate make a small, temporary predictive contribution in shadow mode, does that contribution generalize to reduce error on future out-of-sample observations?"*

### Hypotheses Tested
1. **H1**: A true omitted candidate exhibits positive out-of-sample predictive gain after a small causal micro-update. (**CONFIRMED**: Mean gain = $+0.02011$, $P(\text{gain}>0) = 55.0\%$).
2. **H2**: A noise candidate may fit instantaneous residual, but fails to persist on future samples. (**CONFIRMED**: Mean gain = $-0.000075$, $P(\text{gain}>0) = 47.5\%$).
3. **H3**: A paired baseline-vs-provisional test over 2–3 samples provides useful candidate information. (**PARTIALLY CONFIRMED**: Paired 3-step gain raised true positive gain rate to $62.5\%$).
4. **H4**: Information quality must be judged by information gain per unit compute. (**EVALUATED**: Full compute and efficiency curves computed).

---

## 2. Experimental Setup & Verification Gate

### 2.1 Frozen Causal Baseline
- Learner: Exact accepted EXP-0006 J4 learner (`TieredEvidenceLearner` with `TieredEvidenceRatePolicy(mode="queue_multi_rate")`).
- Hyperparameters: $K_{\max}=10$, Sparse NLMS ($\mu=0.5, \epsilon=10^{-6}$), $n_{\min}=8, \theta_{\text{promote}}=0.40, \tau_{\text{mature}}=50$, Probe Bank (target 10,000 probes, $q \in [1, 8]$).
- Environment: $d=100, K^*=5$, shift at $t=1000$, seeds `[42, 123, 456, 789, 1024]`.

### 2.2 Baseline Reproduction Gate Verification
- **Seed 42 Exact Match**: Regime-2 MSE = **0.011546915**, Recall = **77.26%**, Occupancy = **57.80%** (100% exact match).
- **5-Seed Aggregate Match**: Regime-2 MSE = **0.013552460**, Recall = **81.324%**, Occupancy = **61.760%**, Total Probes = **10,000**, Compute = **142.80 FLOPs/step**.
- **Zero Perturbation**: `MicrotestDiagnosticObserver` evaluated 48,934 micro-test episodes on strictly future samples without mutating learner state, weights, active supports, queues, or PRNG streams.

---

## 3. Primary Empirical Results

### 3.1 Table 1: Information Channels Diagnostic
*Evaluated across 48,934 micro-test episodes in Regime 2 post-shift.*

| Channel | Score Column | PR-AUC | ROC-AUC | P@1 | P@2 | P@3 | P@5 | P@10 | Enrichment@3 | P(Gain>0\|True) | P(Gain>0\|Noise) | FLOPs / Test | State Bytes | Info Efficiency |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **I0 Passive Corr** | `abs_mean_corr` | 0.0362 | 0.7472 | 20.0% | 20.0% | 13.3% | 12.0% | 8.0% | $13.45\times$ | 92.0% | 95.6% | 0 | 0 | 13.451 |
| **I1 Delayed Corr** | `score_i1` | 0.0333 | 0.6263 | 20.0% | 10.0% | 13.3% | 12.0% | 8.0% | $13.45\times$ | 55.3% | 47.6% | 2 | 4 | 6.725 |
| **I2 Single Micro-Update** | `normalized_gain_i2` | 0.0135 | 0.5655 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | $0.00\times$ | 55.0% | 47.5% | 18 | 16 | 0.000 |
| **I3 Paired Shadow Gain** | `normalized_gain_i3` | 0.0208 | 0.6241 | 0.0% | 0.0% | 0.0% | 0.0% | 2.0% | $0.00\times$ | 62.5% | 47.8% | 30 | 24 | 0.000 |
| **I4 Multi-Step Micro** | `normalized_gain_i4` | 0.0105 | 0.5450 | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | $0.00\times$ | 52.2% | 45.4% | 36 | 32 | 0.000 |
| **Causal Direction Margin** | `causal_direction_margin` | 0.0336 | 0.5845 | 20.0% | 10.0% | 13.3% | 8.0% | 4.0% | $13.45\times$ | 55.3% | 47.6% | 24 | 16 | 0.560 |
| **Excess Causal Gain** | `excess_causal_gain` | 0.0332 | 0.5768 | 20.0% | 20.0% | **20.0%** | **16.0%** | **10.0%** | **$18.31\times$** | **57.6%** | **49.1%** | 36 | 32 | 0.509 |
| **Oracle** | `Oracle` | 1.0000 | 1.0000 | 100.0% | 100.0% | 100.0% | 100.0% | 76.0% | $97.63\times$ | 100.0% | 0.0% | 0 | 0 | 97.629 |

---

### 3.2 Table 2: Performance by Passive Probe Count $n \in [1, 5]$
| $n$ | Best Channel | Precision@3 | Precision@5 | Base Rate | Enrichment@3 | Extra FLOPs | True Count | Noise Count |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | I0 Passive Corr / Excess Gain | 13.33% | 8.00% | 1.88% | $5.63\times$ | 0 | 42 | 2,192 |
| **2** | I0 Passive Corr / Excess Gain | 20.00% | 12.00% | 1.88% | $13.85\times$ | 0 | 42 | 2,195 |
| **3** | I0 Passive Corr / Excess Gain | 20.00% | 12.00% | 1.97% | $13.46\times$ | 0 | 43 | 2,145 |
| **4** | I0 Passive Corr | 26.67% | 16.00% | 2.27% | $16.71\times$ | 0 | 37 | 1,592 |
| **5** | I0 Passive Corr | 20.00% | 16.00% | 2.24% | $14.96\times$ | 0 | 35 | 1,526 |

---

### 3.3 Table 3: Temporal Stratification Across Post-Shift Windows
| Window | Steps Post-Shift | True Count | Noise Count | Base Rate | Best Channel | Best Precision@3 | Best Precision@5 | Best PR-AUC |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: |
| **A** | 0–20 | 29 | 688 | 4.04% | Causal Direction Margin | 20.00% | 12.00% | 0.0862 |
| **B** | 21–50 | 38 | 1,030 | 3.56% | Causal Direction Margin | 13.33% | 8.00% | 0.0465 |
| **C** | 51–100 | 71 | 1,714 | 3.98% | Excess Causal Gain | 13.33% | 12.00% | 0.0556 |
| **D** | 101–250 | 157 | 4,957 | 3.07% | I0 Passive Corr | 20.00% | 16.00% | 0.0579 |
| **E** | >250 | 92 | 27,584 | 0.33% | Causal Direction Margin | 6.67% | 8.00% | 0.0265 |

---

### 3.4 Table 4: Residual Stratification Across Smoothed Residual Quantiles
| Quantile | Residual Range | True Count | Noise Count | Base Rate | Best Channel | Best Precision@3 | Best Precision@5 | Effect Size | P(Gain>0\|True) | P(Gain>0\|Noise) |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| **Q1** | Lowest (Settled) | 0 | 9,095 | 0.00% | NONE | 0.00% | 0.00% | 0.000 | 0.0% | 0.0% |
| **Q2** | Low-Mid | 0 | 9,086 | 0.00% | NONE | 0.00% | 0.00% | 0.000 | 0.0% | 0.0% |
| **Q3** | Mid-High | 68 | 9,024 | 0.75% | Causal Direction Margin | **26.67%** | **20.00%** | +0.447 | 72.1% | 46.5% |
| **Q4** | Highest (Burst) | 319 | 8,768 | 3.51% | Excess Causal Gain | 20.00% | 16.00% | +0.071 | 51.4% | 45.1% |

---

## 4. Mathematical & Empirical Diagnosis: Why Micro-Interventions Fail in Ranking

### 4.1 The Theoretical Expectations Are Confirmed
The experimental data confirms the theoretical derivations:
$$\mathbb{E}[\text{GAIN}_{\text{true}}] = +0.02011 > 0 \quad \text{vs} \quad \mathbb{E}[\text{GAIN}_{\text{noise}}] = -0.000075 < 0$$
$$\mathbb{E}[\text{CAUSAL\_DIRECTION\_MARGIN}_{\text{true}}] = +0.0460 > 0 \quad \text{vs} \quad \mathbb{E}[\text{MARGIN}_{\text{noise}}] = +0.0007 \approx 0$$
$$\mathbb{E}[\text{EXCESS\_CAUSAL\_GAIN}_{\text{true}}] = +0.0297 > 0 \quad \text{vs} \quad \mathbb{E}[\text{EXCESS}_{\text{noise}}] = +0.0004 \approx 0$$

### 4.2 The Class Imbalance Trap: Why Positive Mean Fails to Rank
While the true candidate population has positive mean gain, the variance of single-step out-of-sample prediction is large ($\sigma_e^2 \approx 6.5$):
- $P(\text{Gain} > 0 \mid \text{TRUE}) = 55.03\%$
- $P(\text{Gain} > 0 \mid \text{NOISE}) = 47.49\%$

Notice the numbers:
In the post-shift candidate pool, there are **387 TRUE test events** and **35,973 NOISE test events** (a 93:1 noise-to-true ratio!).
- Number of true events with positive gain: $387 \times 0.5503 = \mathbf{213}$.
- Number of noise events with positive gain: $35,973 \times 0.4749 = \mathbf{17,084}$.

When ranking the pool by predictive gain, **out of the 17,297 candidates with positive gain, 17,084 are NOISE (98.8% noise)**!
Because noise features have independent Gaussian inputs $x_{t+1}[j]$, there is a 47.5% chance that a random noise feature's inner product accidentally aligns with the direction of the error on that single future sample.
When 85 noise features are tested simultaneously, multiple noise features will randomly produce large positive gains ($+0.5$ to $+2.0$) purely by chance, pushing all true features out of the top 3 or 5!

### 4.3 Sham Control & Direction Margin Help, But Not Enough
Subtracting the sham control (`Excess Causal Gain`) cancels background residual volatility and improves ranking:
- Achieved **Precision@3 = 20.0%** and **Precision@5 = 16.0%** (Enrichment = **$18.31\times$**).
- But it still falls far short of the preregistered 50% operational threshold.

---

## 5. Answers to the 15 Preregistered Final Questions

1. **Does future predictive gain separate true candidates from noise better than passive residual correlation?**
   **NO**. While its expected value is positive for true and negative for noise, in ranking precision across 85 candidates, passive correlation ($I_0$) achieves higher ROC-AUC (0.747 vs 0.565) because passive correlation averages over several samples, whereas single-sample predictive gain is swamped by single-step variance.
2. **Does a single micro-update suffice?**
   **NO**. $I_2$ achieved Precision@3 = 0.0% in ranking.
3. **Does paired evaluation improve robustness?**
   **YES**. Paired 3-step evaluation ($I_3$) raised $P(\text{gain}>0|\text{TRUE})$ from 55.0% to 62.5% and ROC-AUC from 0.565 to 0.624.
4. **Is repeated micro-testing necessary?**
   **NO**. Multi-update shadow tracking ($I_4$) did not solve the ranking bottleneck (ROC-AUC = 0.545).
5. **Does correct-sign perturbation outperform wrong-sign perturbation for true candidates?**
   **YES**. Mean direction margin was $+0.0460$ for true candidates vs $+0.0007$ for noise.
6. **Does sham normalization remove residual-burst contamination?**
   **PARTIALLY**. Sham subtraction (`Excess Causal Gain`) was the best interventional channel (P@3 = 20.0%, Enrichment = 18.3x), but still failed the 50% threshold.
7. **Which channel achieves best Precision@3?**
   `Excess Causal Gain` (20.0%), tied with passive correlation at $n \ge 2$ (20.0%).
8. **Which channel achieves best Precision@5?**
   `Excess Causal Gain` (16.0%), tied with passive correlation at $n \ge 4$ (16.0%).
9. **What is the minimum useful micro-test count?**
   `NONE` (no tested channel reached the 50% operational gate).
10. **Does the winning channel remain informative during high residual Q4?**
    In Q4, Excess Causal Gain achieved Precision@3 = 20.0%, but false positive rate was 80.0%.
11. **Is the signal robust across seeds?**
    **NO**. Precision@3 is 0% on Seeds 42 and 1024, and 33.3% on Seeds 123, 456, 789.
12. **What is the estimated deployment compute cost?**
    $I_2$: ~18 FLOPs/test; $I_3$: ~30 FLOPs/test; Excess Causal Gain: ~36 FLOPs/test.
13. **Does the information channel plausibly fit under 25% Dense total compute?**
    **YES**. Selective candidate testing adds ~10–15 FLOPs/step, remaining under 155 FLOPs/step ($\le 25.7\%$ Dense).
14. **Does the result indicate decision-rule limitation or information-source limitation?**
    **INFORMATION-SOURCE LIMITATION**. Passive testing on the natural stream lacks sufficient signal-to-noise ratio per candidate under 90:1 noise dilution.
15. **What should be causally tested next?**
    `ACTIVE_PROBE_DESIGN_DIAGNOSTIC` (EXP-0009).

---

## 6. Most Important Practical Question (Section 115)

> **“CAN THE LEARNER LEARN MORE ABOUT A CANDIDATE BY BRIEFLY TRYING IT IN SHADOW MODE AND MEASURING WHETHER IT IMPROVES FUTURE PREDICTION, RATHER THAN RELYING ONLY ON PASSIVE CORRELATION?”**

### **Answer: NO.**
On the natural passive data stream, single-step or few-step predictive gain is swamped by environmental noise variance. The learner cannot reliably distinguish a true omitted variable from 85 noise candidates using passive shadow micro-tests.

---

## 7. Artifact Manifest
- Configuration: [`config.json`](<lebre-research>/experiments/EXP-0008/config.json)
- Master Runner: [`run_information_diagnostic.py`](<lebre-research>/experiments/EXP-0008/run_information_diagnostic.py)
- Diagnostic Module: [`src/diagnostics/candidate_microtest.py`](<lebre-research>/src/diagnostics/candidate_microtest.py)
- Unit Tests: [`tests/test_exp_0008.py`](<lebre-research>/tests/test_exp_0008.py) (4/4 passing, 56/56 repo-wide passing)
- Raw Events: [`microtest_events.csv`](<lebre-research>/experiments/EXP-0008/microtest_events.csv) (48,934 rows)
- Metrics CSVs: [`information_channels.csv`](<lebre-research>/experiments/EXP-0008/information_channels.csv), [`precision_at_k.csv`](<lebre-research>/experiments/EXP-0008/precision_at_k.csv), [`temporal_stratification.csv`](<lebre-research>/experiments/EXP-0008/temporal_stratification.csv), [`residual_stratification.csv`](<lebre-research>/experiments/EXP-0008/residual_stratification.csv), [`causal_controls.csv`](<lebre-research>/experiments/EXP-0008/causal_controls.csv), [`counterfactual_queue.csv`](<lebre-research>/experiments/EXP-0008/counterfactual_queue.csv), [`information_efficiency.csv`](<lebre-research>/experiments/EXP-0008/information_efficiency.csv)
- 12-Panel Publication Figure: [`figures.png`](<lebre-research>/experiments/EXP-0008/figures.png)
