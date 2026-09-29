# EXP-0007 — Diagnostic Analysis & Physical Mechanism
**Why Small-Sample Causal Statistics Fail to Separate True Candidates: The Extreme Value Bottleneck**

---

## 1. The Core Empirical Finding

EXP-0007 provides an unequivocal answer to the central empirical question:
> **"Do the currently available candidate statistics contain enough information at $n \in [1, 5]$ probes to discriminate true omitted candidates from noise candidates?"**

**Answer: NO. The bottleneck is strictly INFORMATION-LIMITED.**

Across 17,990 candidate snapshots collected from 5 evaluation seeds:
- At $n=1$: Precision@3 = 13.3%, Precision@5 = 8.0%.
- At $n=2$: Precision@3 = 20.0%, Precision@5 = 12.0%.
- At $n=3$: Precision@3 = 20.0%, Precision@5 = 12.0%.
- At $n=4$: Precision@3 = 26.7%, Precision@5 = 16.0%.
- At $n=5$: Precision@3 = 20.0%, Precision@5 = 16.0%.

The preregistered gate for operational separability (Precision@3 $\ge 50\%$ or Precision@5 $\ge 40\%$) was **FAILED at all $n \le 5$**.

---

## 2. Mathematical Diagnosis: Why Current Statistics Fail

### 2.1 The Extreme Value Problem Under High Residual Variance
When structural change occurs at $t=1000$, 5 true features are omitted from the learner's active support. The active model's prediction error $e_t = y_t - \hat{y}_t$ experiences a massive variance spike:
$$\sigma_e^2 = \sum_{j \in S^*} \beta_j^2 + \sigma_{\text{noise}}^2 \approx 1.4^2 + 1.0^2 + 1.1^2 + 1.6^2 + 0.9^2 + 0.01 \approx 6.5 \implies \sigma_e \approx 2.55$$

For any irrelevant noise feature $j \notin S^*$, the input $x_{t, j} \sim \mathcal{N}(0, 1)$ is independent of $e_t$. The instantaneous correlation observation $z_{t, j} = e_t x_{t, j}$ is a zero-mean random variable with variance:
$$\operatorname{Var}(z_{t, j}) = \sigma_e^2 \approx 6.5$$

After $n$ probes, the sample mean correlation $\bar{c}_j = \frac{1}{n} \sum_{k=1}^n z_{t_k, j}$ has standard error:
$$\operatorname{SE}(\bar{c}_j) = \frac{\sigma_e}{\sqrt{n}} \approx \frac{2.55}{\sqrt{n}}$$
- At $n=1$: $\operatorname{SE} \approx 2.55$
- At $n=2$: $\operatorname{SE} \approx 1.80$
- At $n=3$: $\operatorname{SE} \approx 1.47$
- At $n=4$: $\operatorname{SE} \approx 1.28$
- At $n=5$: $\operatorname{SE} \approx 1.14$

### 2.2 Submergence of the True Signal
For a true omitted feature $j^* \in S^*$ with true weight $\beta_{j^*} \approx 1.0$, its expectation is:
$$\mathbb{E}[z_{t, j^*}] = \beta_{j^*} \approx 1.00$$

At $n=2$, the true feature's sample mean $\bar{c}_{j^*} \sim \mathcal{N}(1.0, 1.80^2)$.
Meanwhile, in the inactive pool there are $D - K = 90$ candidates, of which **85 are noise features**.
Under the Gaussian tail approximation, the expected maximum of 85 standard normal variables is:
$$\mathbb{E}\left[\max_{1 \le i \le 85} Z_i\right] \approx \sqrt{2 \ln 85} \approx 2.98$$

Therefore, the maximum noise correlation among the 85 candidates at $n=2$ has expectation:
$$\mathbb{E}\left[\max_{j \in \text{Noise}} |\bar{c}_j|\right] \approx 2.98 \times 1.80 \approx \mathbf{5.36}$$

Even considering two-sided tails and moderate correlations, drawing 85 candidates with standard deviation 1.80 guarantees that multiple noise features will have sample means exceeding **2.5 to 3.5**.
Because the true feature has mean 1.0 (with standard error 1.80), its observed sample mean is frequently $0.5 - 2.0$.
**Result**: The extreme noise candidates systematically outrank the true candidates at small $n$!

### 2.3 Why Sign Consistency $\gamma$ Fails at Small $n$
Sign consistency was introduced in EXP-0003 to combat noise churn. At large $n$ (e.g. $n \ge 8$), requiring $\gamma \ge 0.75$ imposes a powerful binomial filter: the probability that a zero-mean symmetric noise variable produces $\ge 6$ out of 8 positive signs is $\approx 14\%$.
However, at small $n$:
- At $n=1$: $\gamma = 1.00$ for 100% of candidates (both true and noise).
- At $n=2$: A noise variable has sign agreement with probability $P(\text{same sign}) = 0.50$. Thus, **50% of all noise candidates (approx. 42 candidates!) have $\gamma = 1.00$**.
- At $n=3$: $\gamma \ge 0.67$ for **100% of candidates** (since $\max(pos, neg) \ge 2$ always for $n=3$).
Thus, sign consistency provides **zero discriminative filtering** at $n \in \{1, 3\}$ and only a trivial 50% coin-flip filter at $n=2$.

---

## 3. Why Threshold Tuning Cannot Solve This Problem

In EXP-0006, the hint elevation rule used:
$$n \ge 2 \land |\bar{c}| \ge 0.15 \land \gamma \ge 0.60$$
One might hypothesize: "Can we simply raise $\theta_{\text{hint}}$ from 0.15 to 0.50 or 0.80?"
EXP-0007 disproves this hypothesis completely:
- If $\theta$ is raised to 0.80 at $n=2$:
  - The probability that a true candidate with mean 1.0 and std 1.80 exceeds 0.80 is $\Phi((1.0 - 0.8)/1.8) \approx 54\%$.
  - The probability that a noise candidate with mean 0.0 and std 1.80 exceeds 0.80 is $2 \times (1 - \Phi(0.8/1.8)) \approx 65\%$.
  - Because there are 85 noise candidates and only 5 true candidates:
    $$\text{Expected True Passing} = 5 \times 0.54 = 2.7$$
    $$\text{Expected Noise Passing} = 85 \times 0.65 = 55.3$$
    $$\text{Precision} = \frac{2.7}{2.7 + 55.3} = \mathbf{4.65\%}$$
No threshold on sample mean correlation can escape this ratio at $n \le 3$. The noise population is 17 times larger than the true population, and its standard error is larger than the true signal itself.

---

## 4. The Diagnostic Crossroads: What Track B Needs Next

Because the failure is **INFORMATION-LIMITED**, the learner cannot solve structural acquisition latency simply by adjusting the queue entry policy on the existing statistics.

The learner needs a fundamentally different source of observation or a restructured screening protocol. Potential candidate directions for future exploration include:

1. **Variance-Normalized / Studentized Correlation**:
   Standardizing candidate inner products by instantaneous residual magnitude:
   $$r_c = \frac{\sum e_t x_{t, c}}{\sqrt{\sum e_t^2 \sum x_{t, c}^2}}$$
   Dividing by instantaneous error prevents massive single-step residual spikes from dominating the Welford sum.

2. **Prediction-Improvement Probing (Hypothetical NLMS Test)**:
   Rather than asking "does candidate $c$ correlate with residual $e_t$?", ask "if candidate $c$ were temporarily included in a 1-step NLMS weight update, does the residual strictly decrease on step $t+1$?"
   A true omitted feature provides consistent directional variance reduction; noise increases out-of-sample variance.

3. **Multi-Stage Confirmation Before Rate Elevation**:
   Instead of jumping a candidate directly from circular scanning (1 probe / 45 steps) to elevated service (1 probe / 2 steps) at $n=2$, introduce an intermediate verification stage that requires consecutive consistency without granting full queue elevation until $n \approx 5-6$.

4. **Residual Orthogonalization / Gram-Schmidt Filtering**:
   Projecting candidate features orthogonal to current active support before computing correlations, ensuring that candidate statistics reflect strictly novel variance.

---

## 5. Preregistered Conclusion

- **PRIMARY_DECISION**: `CURRENT_STATISTICS_INSUFFICIENT`
- **N_SEPARABLE**: `NONE`
- **BEST_SIMPLE_SCORE**: `S0` ($|\bar{c}|$)
- **JOINT_LINEAR_MODEL**: `NO_MATERIAL_VALUE`
- **EXP_0007_STATUS**: `DIAGNOSIS_IDENTIFIED`
- **FAILURE_TYPE**: `INFORMATION_LIMITED`
- **NEXT**: `NEW_CANDIDATE_INFORMATION_DIAGNOSTIC`

Under Section 98 Hard Stop: all changes are halted, and results are submitted for review.
