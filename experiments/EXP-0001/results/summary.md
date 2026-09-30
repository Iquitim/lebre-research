# EXP-0001: Baseline Comparison on Dynamic Sparse Linear Regression

## 1. Setup
- **Dimensions**: $D = 100$, True Sparsity: $K^* = 5$
- **Capacity constraint**: $|S_t| \le 5$
- **Probe budget**: $q = 5$ features per step
- **Shift**: abrupt disjoint support change at $t = 1000$
- **Seeds**: [42, 123, 456, 789, 1024]

## 2. Quantitative Results (Mean ± Std over 5 seeds)

| Model | Overall MSE | Regime 1 MSE (t∈[800,1000]) | Regime 2 MSE (t∈[1800,2000]) | Recovery Latency (steps) | Final Recall | FLOPs / Step | Compute Ratio vs Dense |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Model_A_Dense** | 1.4380 ± 0.0127 | 0.0218 ± 0.0028 | 0.0339 ± 0.0071 | 931.2 ± 41.2 | 100.0% ± 0.0% | 602.0 | 1.000x |
| **Model_B_Fixed** | 11.1320 ± 0.7589 | 11.1002 ± 2.3175 | 12.2683 ± 2.3760 | 1000.0 ± 0.0 | 4.0% ± 8.9% | 32.0 | 0.053x |
| **Model_C_RandomProbe** | 9.4219 ± 0.6181 | 9.6555 ± 1.6984 | 11.8390 ± 2.6990 | 1000.0 ± 0.0 | 0.0% ± 0.0% | 52.0 | 0.086x |
| **Model_D_RoundRobin** | 9.2093 ± 0.1715 | 9.4332 ± 2.0358 | 9.6363 ± 0.9518 | 1000.0 ± 0.0 | 16.0% ± 21.9% | 52.0 | 0.086x |

## 3. Key Findings & Empirical Analysis

1. **Failure of Zero-Slack Immediate Swapping**:
   - Models C and D imposed $|S_t| \le 5$, exactly equal to the ground-truth sparsity $K^*=5$.
   - Because capacity was tight with zero slack, every candidate promotion forced an immediate eviction of an active feature.
   - Newly promoted features start with $w=0$. When competing with mature features or under transient noise, they are at immediate risk of premature eviction before gradient adaptation can grow their magnitude (Churn Trap).

2. **Probe Sample Variance across 95 Candidates**:
   - With $q=5$ probes per step across $D-K=95$ candidates, each candidate is probed sporadically (once every 19 steps).
   - Instantaneous correlation updates $e_t \cdot x_{t, c}$ had high sample variance ($\sigma_e \approx 2.7$), producing an EMA noise standard deviation of $\approx 0.43$.
   - Across 95 candidates, random noise fluctuations regularly exceeded the swap threshold ($0.05$), producing **53 noise feature promotions vs only 3 true promotions** in diagnostic tracking.

3. **Stochastic vs Systematic Exploration**:
   - Model C (Random) achieved 0.0% final recall.
   - Model D (Round-Robin) achieved 16.0% final recall.
   - Systematic circular scanning performed slightly better than uniform random sampling, but the flawed zero-slack swap mechanism bottlenecked both learners.

## 4. GO/NO-GO Verdict

**VERDICT: NO-GO (FAIL)**

- Criteria 1 (Final Recall $\ge$ 80%): **FAIL** (Model C: 0.0%, Model D: 16.0%)
- Criteria 2 (Regime 2 MSE $\le$ 2x Dense = 0.0678): **FAIL** (Model C: 11.84, Model D: 9.64)
- Criteria 3 (FLOPs $\le$ 25% of Dense = 150.5): **PASS** (52.0 FLOPs/step, 0.086x of Dense)

## 5. Next Step: EXP-0001b

Do not protect the failed mechanism. Implement the minimal intervention solving the identified root causes:
1. **Structural Growth Slack ($K_{\max}=10$)**: Decouple candidate promotion from immediate eviction. Allow the support to grow up to $K_{\max}=10$ to incubate promising features.
2. **Magnitude Pruning with Grace Period**: Prune mature active features whose learned weight magnitude $|w_i| < \theta_{\text{prune}}$ after $\tau_{\min}$ steps.
3. **Multi-Probe Candidate Evidence**: Require candidates to accumulate statistical evidence over multiple probes ($n_{\min}$ probes) before promotion.

