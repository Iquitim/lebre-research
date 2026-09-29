# EXP-0008 — Diagnostic Analysis & Physical Mechanism
**Why Passive Micro-Interventions Fail in Ranking: The 93:1 Class Imbalance Trap and Out-of-Sample Variance**

---

## 1. The Core Empirical Finding

EXP-0008 directly addressed the question posed at the conclusion of EXP-0007:
> **"Can a cheap micro-intervention (shadow out-of-sample predictive gain) reveal whether a candidate actually improves future prediction, overcoming the small-sample passive correlation bottleneck?"**

**Answer: NO. Micro-interventions on the passive data stream are INSUFFICIENT for candidate ranking.**

Across 48,934 micro-test episodes collected from 5 evaluation seeds:
- **Single-step micro-update ($I_2$)**: Precision@3 = 0.0%, Precision@5 = 0.0%, ROC-AUC = 0.5655.
- **Paired shadow gain ($I_3$)**: Precision@3 = 0.0%, Precision@5 = 0.0%, ROC-AUC = 0.6241.
- **Multi-step micro-update ($I_4$)**: Precision@3 = 0.0%, Precision@5 = 0.0%, ROC-AUC = 0.5450.
- **Causal direction margin**: Precision@3 = 13.3%, Precision@5 = 8.0%, ROC-AUC = 0.5845.
- **Excess causal gain (sham-subtracted)**: Precision@3 = **20.0%**, Precision@5 = **16.0%**, ROC-AUC = 0.5768.

While `Excess Causal Gain` yielded an enrichment of **$18.31\times$** over the background base rate ($1.09\%$), it failed the preregistered operational gate ($\text{Precision@3} \ge 50\%$).

---

## 2. Mathematical Diagnosis: Why Theory Holds in Expectation but Fails in Ranking

### 2.1 Theoretical Expectations are Fully Confirmed
The mathematical expectations derived in the design phase were validated with remarkable precision by the empirical data:

1. **Out-of-Sample Predictive Gain ($I_2$)**:
   $$\mathbb{E}[\text{Gain}_{I_2} \mid \text{TRUE}] = +0.02011 > 0$$
   $$\mathbb{E}[\text{Gain}_{I_2} \mid \text{NOISE}] = -0.000075 < 0$$
   As predicted by linear least-squares theory, adding an omitted feature with a positive step size on average reduces out-of-sample squared error, whereas adding an orthogonal noise feature on average inflates out-of-sample generalization error by its parameter variance ($\approx \sigma_e^2 \mu^2 / \|x\|^2$).

2. **Causal Direction Margin (Sign Reversal Control)**:
   $$\mathbb{E}[\text{Margin} \mid \text{TRUE}] = \mathbb{E}[e_{\text{anti}}^2 - e_{\text{prov}}^2] = +0.0460 > 0$$
   $$\mathbb{E}[\text{Margin} \mid \text{NOISE}] = +0.0007 \approx 0$$
   Perturbing a true candidate in the anti-gradient direction strictly harms out-of-sample prediction, creating a positive margin. For a noise feature, both directions are symmetric zero-mean Gaussian perturbations.

3. **Excess Causal Gain (Sham Variable Control)**:
   $$\mathbb{E}[\text{Excess Gain} \mid \text{TRUE}] = \mathbb{E}[\text{Gain}_{\text{cand}} - \text{Gain}_{\text{sham}}] = +0.0297 > 0$$
   $$\mathbb{E}[\text{Excess Gain} \mid \text{NOISE}] = +0.0004 \approx 0$$

### 2.2 The 93:1 Class Imbalance Trap
If the expectations have the correct sign, why does ranking fail completely?

The fatal flaw lies in the **variance of single-step out-of-sample prediction** combined with **severe class imbalance**:
When 5 true features are omitted post-shift, the active model's residual variance is $\sigma_e^2 \approx 6.5$.
On step $t+1$, the out-of-sample observation is:
$$y_{t+1} = \sum_{j \in S^*} \beta_j x_{t+1, j} + \epsilon_{t+1}$$
For an unselected candidate $c$, its shadow prediction on $t+1$ is $e_{t+1}^{\text{cand}} = e_{t+1} - \tilde{w}_c x_{t+1, c}$.
The single-step gain is:
$$\Delta_c = e_{t+1}^2 - (e_{t+1}^{\text{cand}})^2 = 2 e_{t+1} \tilde{w}_c x_{t+1, c} - (\tilde{w}_c x_{t+1, c})^2$$

Because $x_{t+1, c} \sim \mathcal{N}(0, 1)$ is drawn from the natural environment stream independently for each candidate:
- For a **noise candidate** $c \notin S^*$, $x_{t+1, c}$ is independent of $e_{t+1}$. The linear term $2 e_{t+1} \tilde{w}_c x_{t+1, c}$ is symmetric with mean 0 and standard deviation $\approx 2 \times 2.55 \times 0.2 \approx 1.02$.
- The probability that a noise candidate's random input $x_{t+1, c}$ happens to have the same sign as $e_{t+1} \tilde{w}_c$ (and is large enough to exceed the tiny quadratic penalty $(\tilde{w}_c x_{t+1, c})^2$) is:
  $$P(\Delta_c > 0 \mid \text{NOISE}) = \mathbf{47.49\%}$$
- For a **true candidate** $j^* \in S^*$, the input $x_{t+1, j^*}$ has a slight positive alignment with $e_{t+1}$, shifting the probability to:
  $$P(\Delta_{j^*} > 0 \mid \text{TRUE}) = \mathbf{55.03\%}$$

Now examine the population counts in the post-shift candidate pool across our 48,934 microtest evaluations:
$$\text{Total True Episodes} = 387 \qquad \text{Total Noise Episodes} = 35,973$$
(Ratio of Noise to True = **92.95 : 1**).

Multiplying by the positive gain probabilities:
$$\text{Number of True candidates with positive gain} = 387 \times 0.5503 = \mathbf{213}$$
$$\text{Number of Noise candidates with positive gain} = 35,973 \times 0.4749 = \mathbf{17,084}$$

**In the pool of candidates that exhibit positive out-of-sample predictive gain, 98.77% are NOISE!**

When the learner ranks candidates by observed predictive gain on step $t+1$, drawing 85 noise candidates guarantees that the extreme right-tail of the noise distribution will produce gains of $+0.5$ to $+2.5$ purely by environmental luck. The true candidates (whose typical single-step gain is $+0.05$ to $+0.3$) are completely pushed out of the top 3 and top 5.

---

## 3. Why Paired and Multi-Step Evaluations Did Not Rescue Ranking

### 3.1 Paired 3-Step Evaluation ($I_3$)
In $I_3$, the shadow weight was tested over a 3-step window:
$$\text{Gain}_{I_3} = \sum_{k=1}^3 (e_{t+k}^2 - (e_{t+k}^{\text{prov}})^2)$$
Averaging over 3 steps helped increase true signal probability:
$$P(\text{Gain}_{I_3} > 0 \mid \text{TRUE}) = \mathbf{62.5\%} \quad (\text{vs } 55.0\% \text{ in } I_2)$$
$$P(\text{Gain}_{I_3} > 0 \mid \text{NOISE}) = \mathbf{47.8\%}$$
However, 3 samples is still far too few to suppress Gaussian extreme value statistics across 85 candidates:
$$\mathbb{E}\left[\max_{1 \le i \le 85} Z_i\right] \approx 2.98$$
Even over 3 steps, several noise candidates out of 85 will accumulate positive inner products purely by chance, resulting in Precision@3 = 0.0%.

### 3.2 Multi-Step Micro-Updates ($I_4$)
In $I_4$, the shadow candidate was updated on each step $k \in \{1, 2, 3\}$.
This actually degraded ROC-AUC (0.5450 vs 0.6241 for $I_3$).
Why? Because updating an unconfirmed candidate on consecutive samples allows noise features to overfit recent residual fluctuations, creating higher variance in the shadow prediction and increasing the likelihood of extreme spurious gains.

---

## 4. Why Causal Controls (Sham and Direction) Help, and What They Reveal

### 4.1 Direction Margin (`causal_direction_margin`)
By computing $e_{\text{anti}}^2 - e_{\text{prov}}^2$, direction margin cancels the common base error $e_{t+1}^2$:
$$e_{\text{anti}}^2 - e_{\text{prov}}^2 = 4 e_{t+1} \tilde{w}_c x_{t+1, c}$$
This completely eliminates the quadratic penalty and isolates the linear alignment.
- ROC-AUC: 0.5845.
- In post-shift Window A ($t \in [1000, 1020]$), it achieved Precision@3 = **20.0%** (vs 4.04% base rate).
- In high-residual Quantile Q3, it achieved Precision@3 = **26.67%** (vs 0.75% base rate, an enrichment of **$35.5\times$**).

### 4.2 Excess Causal Gain (`excess_causal_gain`)
By injecting a synthetic sham feature $s_{t} \sim \mathcal{N}(0, 1)$ alongside candidate $c$ and taking $\Delta_c - \Delta_{\text{sham}}$, the learner cancels the shared instantaneous environmental shock on step $t+1$:
- Achieved **Precision@3 = 20.0%** and **Precision@5 = 16.0%** over the aggregate dataset.
- Enrichment = **$18.31\times$**.
- This proves that controlling for environmental baseline fluctuation is mathematically superior to raw predictive gain.

### 4.3 Why They Still Fall Short of 50%
Even with sham control, candidate evaluation is conducted on **passive natural inputs** $x_{t+1, c}$ supplied by the environment.
The signal-to-noise ratio of a single observation is:
$$\text{SNR}_1 = \frac{|\beta_{j^*}|}{\sigma_e} \approx \frac{1.0}{2.55} \approx 0.39$$
To achieve 95% confidence that $\bar{\Delta} > 0$ against 85 competitors requires an SNR of at least $3.0$, which demands:
$$n_{\text{req}} \approx \left(\frac{3.0}{0.39}\right)^2 \approx 59 \text{ samples}$$
A passive shadow trial of 1 to 3 steps cannot bridge this gap because the learner has no control over what input the environment presents.

---

## 5. The Core Diagnostic Resolution (Answers to Final Questions)

1. **Information Channel Hierarchy**:
   `EXCESS_CAUSAL_GAIN` > `CAUSAL_DIRECTION_MARGIN` > `I0_PASSIVE_CORR` > `I3_PAIRED_SHADOW` > `I2_SINGLE_MICRO` > `I4_MULTI_STEP`.
2. **Failure Classification**:
   The failure is strictly an **INFORMATION-SOURCE LIMITATION**, not an algorithmic decision-rule failure.
3. **Verdict on Q115**:
   On the passive natural stream, shadow micro-tests cannot solve the small-sample candidate separability problem.
4. **Primary Decision**:
   `PRIMARY_DECISION = CURRENT_MICRO_INTERVENTIONS_INSUFFICIENT`.
5. **Next Step**:
   `ACTIVE_PROBE_DESIGN_DIAGNOSTIC` (EXP-0009).

---

## 6. Section 118 Hard Stop Enforcement

As stipulated in the experimental protocol (Section 118):
- Do NOT deploy the winning channel into production.
- Do NOT alter probe budgets or rate policies.
- Do NOT introduce multi-armed bandits, RL, or neural mechanisms.
- Retain the baseline frozen state bit-for-bit.
- Submit this diagnostic for user review.
