# EXP-0009 — Diagnostic Analysis & Physical Mechanism
**The Active Probing Equivalence Principle: Why Internal Perturbations Cannot Overcome Passive Input Variance**

---

## 1. The Core Diagnostic Resolution

EXP-0009 was designed to test whether the learner could overcome the passive small-sample information bottleneck diagnosed in EXP-0007 and EXP-0008 by actively creating its own observations:
> **"Can structured active probes (symmetric paired excitation, random-sign coding, orthogonal group coding, sham cancellation) create a high-SNR candidate information channel under fixed compute constraints?"**

**Answer: NO. Structured active probing of prediction hypotheses is INSUFFICIENT to achieve operational candidate separability.**

Across 56,265 active probe episodes evaluated on 5 evaluation seeds:
- **A1 (Symmetric Paired $\pm\delta$ Excitation)**: Precision@3 = 20.0%, Precision@5 = 16.0%, ROC-AUC = 0.5690, Active SNR = +0.254.
- **A2 (Random-Sign Coded Excitation, $R=4$)**: Precision@3 = 13.3%, Precision@5 = 12.0%, ROC-AUC = 0.5025, Active SNR = -0.008.
- **A3 (Orthogonal Group Coding, $G=4, R=4$)**: Precision@3 = 0.0%, Precision@5 = 8.0%, ROC-AUC = 0.5997, Active SNR = +0.191.
- **A3 (Orthogonal Group Coding, $G=8, R=8$)**: Precision@3 = 6.7%, Precision@5 = 12.0%, ROC-AUC = 0.5700, Active SNR = +0.218.
- **A4 (Paired + Sham Excess)**: Precision@3 = 20.0%, Precision@5 = 16.0%, ROC-AUC = 0.5443, Active SNR = +0.173.
- **A5 (Multi-Round Accumulation, $R=4$)**: Precision@3 = 20.0%, Precision@5 = 16.0%, ROC-AUC = 0.5122, Active SNR = +0.061.

The preregistered operational gate ($\text{Precision@3} \ge 50\%$ or $\text{Precision@5} \ge 40\%$) was **FAILED by all active channels**.

---

## 2. Mathematical Diagnosis: The Active Probing Equivalence Principle

### 2.1 The Derivation
In an active control setting (e.g., robotics, industrial plant identification), an active probe injects a signal into the physical plant $u_t \to y_t$, exciting the system state directly.
However, in **supervised dynamic regression**, the learner does not control the environment's feature inputs $x_t \in \mathbb{R}^d$. The environment draws $x_t \sim \mathcal{N}(0, I)$ independently.

When the learner introduces a shadow perturbation to its prediction hypothesis:
$$\hat{y}_{+} = \hat{y}_{\text{base}} + \delta x_{t+r, j} \qquad \hat{y}_{-} = \hat{y}_{\text{base}} - \delta x_{t+r, j}$$
The resulting squared prediction losses on the future sample are:
$$L_{+} = (e_{\text{base}, t+r} - \delta x_{t+r, j})^2 = e_{\text{base}}^2 - 2 \delta e_{\text{base}} x_{t+r, j} + \delta^2 x_{t+r, j}^2$$
$$L_{-} = (e_{\text{base}, t+r} + \delta x_{t+r, j})^2 = e_{\text{base}}^2 + 2 \delta e_{\text{base}} x_{t+r, j} + \delta^2 x_{t+r, j}^2$$

Subtracting the two losses yields:
$$L_{-} - L_{+} = 4 \delta \cdot (e_{\text{base}, t+r} x_{t+r, j})$$

### 2.2 Why Paired Cancellation Fails to Boost SNR
Symmetric paired excitation achieves an elegant mathematical cancellation:
- The common background squared loss $e_{\text{base}}^2$ cancels out completely.
- The quadratic self-interference term $\delta^2 x_j^2$ cancels out completely.

**However, the remaining signal is strictly a scalar multiple ($4\delta$) of the instantaneous residual-feature inner product $e_{\text{base}, t+r} x_{t+r, j}$.**
Dividing by $4\delta$ yields the exact passive observation:
$$\frac{L_- - L_+}{4\delta} = e_{\text{base}, t+r} x_{t+r, j}$$

Therefore, **an active predictive perturbation in supervised regression is mathematically equivalent to a single passive residual-correlation measurement.**
It cannot extract any new information that was not already present in the inner product $e \cdot x$.

---

## 3. Why Orthogonal Group Coding Collapsed in Streaming Data

In Channel A3, we hypothesized that Walsh-Hadamard orthogonal codes could screen $G \in \{4, 8\}$ candidates simultaneously over $R = G$ rounds without increasing compute.
Mathematically, the Hadamard matrix satisfies:
$$H H^T = R \cdot I \implies \frac{1}{R} \sum_{r=0}^{R-1} H[k, r] H[j, r] = \delta_{kj}$$

However, in streaming regression, the observation on round $r$ is:
$$\text{response}_r = 4 \delta \sum_{j \in G} H[j, r] \cdot (e_{\text{base}, r} x_{t+r, j})$$
When we decode candidate $k$ by projecting onto row $k$:
$$\text{GROUP\_SCORE}_k = \frac{1}{R} \sum_{r=0}^{R-1} H[k, r] \cdot \text{response}_r$$
$$= 4 \delta \left[ \frac{1}{R} \sum_{r=0}^{R-1} e_{\text{base}, r} x_{t+r, k} + \sum_{j \ne k} \underbrace{\left( \frac{1}{R} \sum_{r=0}^{R-1} H[k, r] H[j, r] \cdot (e_{\text{base}, r} x_{t+r, j}) \right)}_{\text{Cross-Talk from Candidate } j} \right]$$

### The Root Cause of Group Failure
Hadamard cancellation $\sum_r H[k, r] H[j, r] = 0$ works **if and only if the underlying quantity being modulated is constant across rounds**.
In a dynamic stream:
- The residual $e_{\text{base}, r}$ fluctuates on every step.
- The feature vector $x_{t+r}$ is redrawn randomly from $\mathcal{N}(0, I)$ on every step.
Because $e_{\text{base}, r} x_{t+r, j}$ varies stochastically from step to step, the cross-talk sum does **NOT** vanish over small code lengths ($R=4$ or $R=8$):
$$\operatorname{Var}(\text{CrossTalk}_{k, j}) = \frac{1}{R} \sigma_e^2 \approx \frac{6.5}{4} \approx 1.63$$
With $G=4$ candidates, candidate $k$ suffers interference from 3 competitors with variance $3 \times 1.63 \approx 4.88$.
This massive cross-talk completely destroyed candidate identifiability, reducing Precision@3 to **0.0%** for $G=4$ and **6.7%** for $G=8$.

---

## 4. The Unified Physical Bottleneck: The Three Diagnostics Synthesis

Across the three consecutive diagnostic experiments, Track B has mapped the complete empirical landscape of candidate discovery:

| Diagnostic | Mechanism Evaluated | Result | Fatal Bottleneck |
| :--- | :--- | :---: | :--- |
| **EXP-0007** | **Passive Small-Sample Statistics** ($|\bar{c}|, \gamma, \text{Welford}$) | **FAILED** (P@3 $\le 26.7\%$) | Extreme Value Swamping: $\sigma_e \approx 2.55$ causes noise sample means across 85 candidates to regularly hit $2.5 - 3.5$, submerging true signals ($\mathbb{E}[c] \approx 1.0$). |
| **EXP-0008** | **Passive Shadow Micro-Interventions** ($I_2, I_3, I_4$, Sham) | **FAILED** (P@3 $\le 20.0\%$) | 93:1 Class Imbalance Trap: $47.5\%$ of noise candidates accidentally reduce single-step out-of-sample squared error, contaminating positive-gain candidates with $98.8\%$ noise. |
| **EXP-0009** | **Active Structured Probing** ($\pm\delta$ Paired, Coded, Hadamard Group) | **FAILED** (P@3 $\le 20.0\%$) | Active Equivalence Principle: Predictive perturbations cannot alter passive input variance ($L_- - L_+ = 4\delta e x$). Noise P99 tails ($1.67$) remain $30\times$ larger than median true signal ($0.05$). |

### The Core Conclusion
The bottleneck in Track B is **NOT**:
- A parameter estimation bottleneck (disproved by Sparse NLMS in EXP-0001c).
- A post-promotion churn bottleneck (solved by age-normalized victim scoring in EXP-0004).
- A rate allocation bottleneck (solved by queue multi-rate scheduling in EXP-0006).
- An evidence-interpretation bottleneck (disproved by EXP-0007, EXP-0008, EXP-0009).

**The bottleneck is a FUNDAMENTAL INFORMATION-SOURCE LIMITATION of the passive streaming regression benchmark itself.**
When 85 noise features with unit variance compete against 5 omitted features under residual variance $\sigma_e^2 \approx 6.5$, extracting reliable candidate identity within $n \le 5$ samples is mathematically impossible under passive input generation.

---

## 5. Formal Decisions & Next Steps

- **PRIMARY_DECISION**: `ACTIVE_PROBING_INSUFFICIENT`
- **BEST_ACTIVE_CHANNEL**: `A1` (Symmetric Paired $\pm\delta$ Excitation, signed)
- **MIN_ACTIVE_ROUNDS**: `NONE`
- **GROUP_PROBING**: `NOT_USEFUL`
- **INFORMATION_STATUS**: `ACTIVE_INFORMATION_INSUFFICIENT`
- **EXP_0009_STATUS**: `DIAGNOSIS_IDENTIFIED`
- **NEXT**: `STRUCTURAL_IDENTIFIABILITY_REASSESSMENT` (Section 108)

---

## 6. Section 112 Hard Stop Enforcement

Under Section 112 constraints:
- All active channels remain offline in diagnostic mode.
- Production J4 learner remains bit-for-bit unchanged.
- No bandits, reinforcement learning, neural networks, or nonlinear tasks have been introduced.
- Experimental report and diagnostics are submitted for user review.
