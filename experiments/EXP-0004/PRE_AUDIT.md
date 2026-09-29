# EXP-0004: Pre-Experiment Baseline Reproducibility Audit

**Audit Status**: **PASSED** (Root cause identified, mathematically isolated, and verified bit-for-bit).

---

## 1. Audit Objective

Before initiating **EXP-0004**, investigate and explain the empirical discrepancy between the accepted baselines in previous experiments:
- **EXP-0002 D2 / E0 Baseline**:
  - Regime-2 MSE: $\approx 0.3468$
  - Full-Support Occupancy: $\approx 27.8\%$
- **EXP-0003 F0 Baseline**:
  - Regime-2 MSE: $\approx 0.0842$
  - Full-Support Occupancy: $\approx 39.3\%$

If both are supposed to represent the same frozen learner (`B3 + Probe-Credit Bank + Round-Robin probing`), the cause of this divergence must be rigorously explained before proceeding.

---

## 2. Investigation and Root Cause Identification

We performed an exhaustive line-by-line code, config, and simulation audit across `EXP-0001d`, `EXP-0002`, and `EXP-0003`.

### A. Environment, Seeds, and NLMS Learner
- **Environment**: `DynamicSparseLinearStream` is identical across all experiments ($d=100$, $K^*=5$, noise std $0.10$, shift at $t=1000$).
- **Random Stream**: Identical seeds `[42, 123, 456, 789, 1024]`, identical initial support selection (`np.random.RandomState(seed).choice`).
- **Learner Core**: `AblationSparseLearner` (variant B3, $K_{\max}=10$, NLMS $\mu=0.5$, $\epsilon=10^{-6}$, $n_{\min}=8$, $\theta_{\text{promote}}=0.40$, grace period $15$, swap threshold $0.05$) is identical.
- **Standalone Reproduction**: When run with identical inputs, the learner is bit-for-bit identical across all 2,000 steps.

### B. The Culprit: Probe-Bank Controller Schedule Drift
Comparison of `config.json` between `EXP-0002` and `EXP-0003` revealed an unintentional drift in the 5 temporal probe-bank controller parameters:

| Parameter | EXP-0001d (D2) & EXP-0002 (E0) | EXP-0003 (F0) | Effect of Drift |
| :--- | :---: | :---: | :--- |
| `q_min` | **2** | **1** | Minimum probe allocation during quiescent periods |
| `q_max` | **15** | **8** | Maximum burst capacity during shock transitions |
| `tau_low` | **0.08** | **0.05** | Error threshold below which probes are saved |
| `tau_high` | **0.25** | **0.50** | Error threshold above which burst probes fire |
| `ema_alpha` | **0.85** | **0.05** | Smoothing factor of the causal residual tracker |

### C. Mechanism of the Discrepancy
1. **In EXP-0002 (Aggressive Bursts: $q \in [2, 15]$, $\alpha=0.85$)**:
   When the structural shift occurs at $t=1001$, high instantaneous error caused $q_t$ to spike immediately to $15$ probes/step. Under uniform round-robin probing across 95 inactive candidates, injecting 15 probes/step during the high-residual transition phase caused multiple noisy candidates to accumulate $\ge 8$ probes and cross $\theta_{\text{promote}} = 0.40$ by chance. On Seed 42, this triggered 7 spurious noise swaps, displacing true incumbents and collapsing Seed 42 occupancy to $7.7\%$ (Regime-2 MSE $1.3742$). Across all 5 seeds, average occupancy was **$27.78\%$** and Regime-2 MSE was **$0.3468$**.
2. **In EXP-0003 (Smoothed Bursts: $q \in [1, 8]$, $\alpha=0.05$)**:
   Because $q_{\max}$ was capped at $8$ and the EMA tracker was smoothed ($\alpha=0.05$), the probe distribution was less bursty. Fewer noisy candidates accumulated $\ge 8$ probes in the immediate transition shock window. On Seed 42, all 5 true features were successfully acquired, increasing occupancy to $50.5\%$ and lowering Regime-2 MSE to $0.0119$. Across all 5 seeds, average occupancy reached **$39.26\%$** and Regime-2 MSE was **$0.0842$**.

---

## 3. Exact Reproduction Verification

To verify that parameter drift completely explains the discrepancy:
We re-ran the exact baseline learner on the 5 evaluation seeds under both sets of controller parameters:

1. **Baseline with EXP-0002 parameters (`q_min=2, q_max=15, tau_low=0.08, tau_high=0.25, alpha=0.85`)**:
   - Regime-2 MSE: **$0.3468$** (Exact bit-for-bit reproduction of EXP-0002 accepted D2/E0 baseline).
   - Full-Support Occupancy: **$27.78\%$** (Exact bit-for-bit reproduction of EXP-0002 accepted D2/E0 baseline).
2. **Baseline with EXP-0003 parameters (`q_min=1, q_max=8, tau_low=0.05, tau_high=0.50, alpha=0.05`)**:
   - Regime-2 MSE: **$0.0842$** (Exact bit-for-bit reproduction of EXP-0003 F0 baseline).
   - Full-Support Occupancy: **$39.26\%$** (Exact bit-for-bit reproduction of EXP-0003 F0 baseline).

### Conclusion:
There is zero code drift, zero random-stream bug, and zero metric-definition divergence. The difference is 100% attributable to the probe-bank controller schedule ($q \in [2, 15]$ vs $q \in [1, 8]$).

---

## 4. Frozen Baseline for EXP-0004

Per Sections 6 and 11 of the EXP-0004 specification:
> "Freeze the exact accepted EXP-0003 F4 learner as the EXP-0004 baseline."
> "Use exact accepted EXP-0003 F4: Explore/Confirm + Forced Coverage + Probe Bank + K_max = 10 + same NLMS + same n_min + same theta_promote + same candidate states + same q schedule + same total probe budget."

Therefore, for EXP-0004:
- The frozen baseline is **G0 (accepted EXP-0003 F4)**.
- Controller schedule is frozen at the accepted EXP-0003 values: `q_min=1, q_max=8, tau_low=0.05, tau_high=0.50, ema_alpha=0.05`, total budget = $10,000$ probes exact ($\Delta = 0$).
- Baseline G0 reference performance:
  - Regime-2 MSE $\approx 0.0164$
  - Full-Support Occupancy $\approx 47.70\%$
  - $T_{\text{post\_promotion}} \approx 208.8$ steps
  - Compute $\approx 103.6$ FLOPs/step ($17.2\%$ Dense).
