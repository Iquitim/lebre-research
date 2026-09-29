# EXP-0004 — Diagnosis & Component Status

## 1. Primary Diagnosis

**`SCREENING_LATENCY_EVIDENCE_ACCUMULATION`**

In EXP-0003, post-promotion churn latency was identified as the dominant bottleneck ($T_{\text{post\_promotion}} = 208.80$ steps, 56.68% of total acquisition time).
In EXP-0004, the introduction of age-normalized victim scoring ($S_{\text{victim}}(j) = \frac{|w_j|}{\min(1, \text{age}_j / \tau_{\text{mature}})}$) reduced post-promotion latency to **60.84 steps** (a 70.86% reduction), dropping its share to 25.72%.

With post-promotion stabilization resolved, the bottleneck has shifted back to:
- **Screening Evidence Accumulation Latency**: $T_{\text{evidence}} = 129.28$ steps (**54.66% of total latency**).
- Total acquisition latency is now $T_{\text{total}} = 236.52$ steps (down 35.8% from 368.36 steps in EXP-0003 F4).

---

## 2. Component Status

### Components to KEEP:
1. **Age-Normalized Victim Scoring (`victim_strategy="age_normalized"`, $\tau_{\text{mature}}=50$)**:
   - Reduces $T_{\text{post\_promotion}}$ by 70.86% without blind immunity.
   - Boosts full-support occupancy from 47.70% to 65.36%.
   - Reduces spurious noise-to-true displacements by 40.4% (from 11.4 to 6.8).
   - Improves Regime-2 MSE to 0.01383 (outperforming Sparse Oracle 0.01480 and Dense 0.03386).
   - Incurs essentially zero additional compute overhead (17.15% vs 17.17% of Dense).
2. **Explore/Confirm Screening Policy (40% Forced Coverage)** (from EXP-0003):
   - Maintains continuous baseline coverage while concentrating probes on high-correlation features.
3. **Probe Bank Controller (Smoothed $q \in [1, 8]$ schedule, $\alpha=0.05$)** (from EXP-0003):
   - Keeps total probes strictly at 10,000 while redistributing probes post-shift.
4. **Welford Screening Statistics ($N_{\min}=5, \theta_{\text{promote}}=0.10$)** (from EXP-0003):
   - Reliably eliminates noise candidates ($0.0\%$ noise survival at step 50).
5. **Structural Slack ($K_{\max}=10$ for $K^*=5$)** (from EXP-0001b):
   - Foundational prerequisite preventing zero-slack eviction churn.

### Components to REJECT / REMOVE:
1. **Contribution-Aware Victim Scoring (`victim_strategy="contribution_aware"`)**:
   - **Reason**: Estimating feature contribution via EMA of $|w_j \cdot x_j|$ has excessive variance due to Gaussian inputs $x_j \sim \mathcal{N}(0, 1)$. Young features with developing weights produce noisy contribution estimates, driving $T_{\text{post\_promotion}}$ up to 291.6 steps and MSE up to 0.09385.
2. **Promotion Cooldown (`cooldown_steps > 0`)**:
   - **Reason**: A rigid cooldown between promotions prevents rapid filling of empty support slots following a regime shift, delaying structural recovery by hundreds of steps and causing MSE explosion (4.1827).
3. **Raw Weight Victim Scoring (without Maturation Adjustment)**:
   - **Reason**: In an active NLMS learner, newly promoted true features take $\sim 50$ steps to converge from $w \approx 0.1$ to $w \approx 1.0$. Evaluating unadjusted weights prematurely classifies these adapting features as the weakest support members, triggering repeated displacement cycles.

---

## 3. Experiment Status Verdict

**Status**: **PARTIAL_GO / NEAR GO**

### Metric Comparison vs Decision Gates:
- **$T_{\text{post\_promotion}} \le 80$ steps**: **PASS** (Achieved: **60.84 steps**, a 70.86% reduction vs baseline 208.80).
- **Full-Support Occupancy $\ge 70\%$**: **NEAR PASS** (Achieved: **65.36%**, up from 47.70% baseline, a +17.66 pp / +37% relative gain).
- **Regime-2 MSE $\le 0.05$**: **PASS** (Achieved: **0.01383**, surpassing Sparse Oracle 0.01480 and Dense 0.03386).
- **Mean Compute $\le 25\%$ Dense**: **PASS** (Achieved: **103.23 FLOPs/step = 17.15% of Dense**).
- **Total Probes = 10,000**: **PASS** (Achieved: **10,000 probes, $\Delta = 0$**).
- **No Blind Immunity ($t_{\text{protect}}=0$)**: **PASS** (Achieved: noise survival @ 50 = **0.0%**).

---

## 4. Next Step Direction

Having eliminated the post-promotion churn bottleneck, the newly exposed limiting factor is **Screening Evidence Accumulation ($T_{\text{evidence}} = 129.28$ steps, 54.7% of latency)**.
Subsequent investigations should focus on:
1. Reducing evidence accumulation time while maintaining noise rejection (e.g., adaptive evidence thresholds $N_{\min}$ that scale inversely with estimated SNR, or sequential Wald ratio tests).
2. Investigating whether initial parameter warm-starting or adaptive learning rates during the first 10 steps after promotion can further accelerate weight convergence towards $\tau_{\text{mature}}$.
