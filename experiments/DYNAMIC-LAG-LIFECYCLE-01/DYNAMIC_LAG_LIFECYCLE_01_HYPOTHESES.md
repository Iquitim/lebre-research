# DYNAMIC-LAG-LIFECYCLE-01: Hypotheses & Decisive Falsification Matrix
## Formal Predictions for Causal Sparse Delay Discovery & Lifecycle Governance

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Auditor:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, Reproducibility Auditor  
**Date:** September 2026  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Status:** PREREGISTERED & SEALED (Pre-Execution)

---

## 1. Overview & Epistemic Protocol

To prevent post-hoc rationalization, each hypothesis below specifies:
1. **Mathematical Rationale & Theoretical Prediction**;
2. **Evaluation Metric & Paired Counterfactual Baseline**;
3. **Decisive Confirmation Threshold**;
4. **Decisive Falsification Threshold**.

If a hypothesis does not meet its preregistered confirmation threshold, it must be labeled **REFUTED** or **NOT_SUPPORTED** in the final causal summary table.

---

## 2. Formal Hypotheses H1 Through H7

### Hypothesis H1: Online Support Discovery is Feasible Without Oracle Knowledge
- **Theoretical Rationale:** An online streaming learner receiving an informative error gradient can compute prequential cross-correlations between prediction residuals $e_t$ and past candidate features $x_{i, t-k}$. Even with a bounded candidate schedule, true delayed dependencies generate systematic non-zero covariance, allowing useful coordinate-lag pairs $(i, k)$ to be identified above chance.
- **Primary Metrics:** Support Recall ($\text{Recall} = \frac{|S_{\text{discovered}} \cap S_{\text{true}}|}{|S_{\text{true}}|}$) and Predictive Gap:
  $$\Delta \text{NMSE}_{\text{oracle}} = \text{NMSE}(\text{Dynamic}) - \text{NMSE}(\text{Oracle Sparse T5})$$
- **Decisive Confirmation Threshold:**
  - Mean Support Recall $\ge 70.0\%$ on static sparse delay benchmarks (D1, D2, D3).
  - $\Delta \text{NMSE}_{\text{oracle}} \le 0.100$ (closing $\ge 80\%$ of the gap between instantaneous linear and oracle sparse taps).
- **Decisive Falsification Threshold:**
  - Support Recall $< 40.0\%$ or $\Delta \text{NMSE}_{\text{oracle}} > 0.300$.

---

### Hypothesis H2: Non-Contiguous Sparsity Matters Over Contiguous Tap-Length
- **Theoretical Rationale:** Variable tap-length adaptive filters (Gong & Cowan 2005) adapt a contiguous filter order $L_t$. When relevant delays are widely separated (e.g. $k_1 = 2$ and $k_2 = 28$ in D3), contiguous adaptation must allocate $\ge 29$ active taps, accumulating gradient noise across 27 irrelevant intermediate coefficients. A sparse non-contiguous selector needs only 2 active taps.
- **Primary Metrics:** Active Tap Count ($K_{\text{active}}$) and Steady-State NMSE on widely separated delay workloads (D3).
- **Decisive Confirmation Threshold:**
  - Dynamic sparse lag selector achieves equal or lower NMSE than variable contiguous tap-length (B4) while consuming $\le 30\%$ of the active tap count ($K_{\text{active}} \le 0.30 \cdot L_{\text{contiguous}}$) and $\le 50\%$ of the mean FLOPs.
- **Decisive Falsification Threshold:**
  - Contiguous filter (B4) achieves superior NMSE with equal or fewer active taps, or sparse non-contiguous selection incurs excessive search regret that offsets its structural parsimony.

---

### Hypothesis H3: Structural Lifecycle Governance Suppresses Structural Waste
- **Theoretical Rationale:** In unconstrained sparse linear regression (e.g. $\ell_0$-LMS or ZA-NLMS), every candidate in the dictionary is continuously adapted with a penalty term. Under high input dimensionality or noisy streaming conditions, spurious taps frequently fluctuate around the threshold. LEBRE's discrete lifecycle states (DORMANT $\to$ PROVISIONAL $\to$ ACTIVE $\to$ MATURE $\to$ EVICTED) require persistent paired counterfactual gain before promotion, suppressing spurious persistent tap allocations.
- **Primary Metrics:** False Promotion Count ($N_{\text{FP}}$) and False Tap Dwell Time on Memoryless Negative Control (D9).
- **Decisive Confirmation Threshold:**
  - On D9 (pure instantaneous linear, zero delays), lifecycle governance achieves $\ge 80\%$ reduction in persistent active tap count compared to $\ell_0$-LMS (B5), with mean active taps $K_{\text{active}} < 0.5$.
- **Decisive Falsification Threshold:**
  - Lifecycle governance accumulates persistent false taps on D9 ($K_{\text{active}} \ge 1.5$) or provides no meaningful false-promotion suppression over continuous $\ell_0$ shrinkage.

---

### Hypothesis H4: Time-Varying Support Can Be Tracked Online
- **Theoretical Rationale:** When the physical data-generating process undergoes an abrupt regime switch (D4: $S_1 \to S_2 \to S_3$) or tap death (D6), the predictive correlation of obsolete taps drops to zero. Two-timescale relevance tracking steadily decays their retention score, triggering eviction, while rotating candidate probes detect the newly relevant lag coordinates.
- **Primary Metrics:** Support Relocation Latency ($T_{\text{reloc}}$) and Post-Change Regret ($R_{\text{post}}$):
  $$T_{\text{reloc}} = t_{\text{discover}}(\text{new}) - t_{\text{switch}}, \quad T_{\text{evict}} = t_{\text{evict}}(\text{old}) - t_{\text{switch}}$$
- **Decisive Confirmation Threshold:**
  - Old obsolete taps are evicted ($T_{\text{evict}} < 1,500$ steps).
  - New active taps are discovered and promoted ($T_{\text{reloc}} < 1,500$ steps).
  - Post-switch steady-state NMSE returns to within $0.08$ of oracle support switch (O2).
- **Decisive Falsification Threshold:**
  - System suffers catastrophic latching (old taps permanently retained) or fails to discover new support ($T_{\text{reloc}} > 4,000$ steps).

---

### Hypothesis H5: Quiescence Must Not Equal Obsolescence
- **Theoretical Rationale:** If a true delayed dependency becomes temporarily inactive (e.g. an intermittent signal or bursty Poisson driver in D7), instantaneous magnitude-based pruning will evict the tap during the silent interval. When the signal returns, the model suffers large predictive error while re-adapting. Two-timescale structural relevance with an explicit obsolescence gate prevents premature eviction during quiescent intervals.
- **Primary Metrics:** Quiescent Survival Rate ($P_{\text{survive}}$) and Re-Discovery Error Spike ($\Delta \text{MSE}_{\text{return}}$) on D7.
- **Decisive Confirmation Threshold:**
  - Quiescent tap survival rate $\ge 80\%$ under slow relevance + obsolescence gating (E2), whereas instantaneous magnitude pruning (E0) exhibits $\le 20\%$ survival.
  - Re-activation MSE spike reduced by $\ge 50\%$ compared to a model that evicted the tap.
- **Decisive Falsification Threshold:**
  - Two-timescale relevance prematurely evicts quiescent taps at the same rate as magnitude pruning, or holding quiescent taps causes excessive false retention on genuinely dead taps.

---

### Hypothesis H6: Discovery Cost is the Real Resource Bottleneck
- **Theoretical Rationale:** The active coefficient count in a sparse model is small ($K \le 4$), but storing historical features ($D \cdot L_{\max}$ floats) and scanning candidate correlations consumes substantially more memory and compute than the active linear predictor itself.
- **Primary Metrics:** Ratio of Discovery Resources to Active Prediction Resources:
  $$\rho_{\text{MEM}} = \frac{\text{MEM}_{\text{hist}} + \text{MEM}_{\text{cand}}}{\text{MEM}_{\text{active}}}, \quad \rho_{\text{FLOP}} = \frac{\text{FLOP}_{\text{probe}} + \text{FLOP}_{\text{scan}}}{\text{FLOP}_{\text{active}}}$$
- **Decisive Confirmation Threshold:**
  - $\rho_{\text{MEM}} \ge 2.0$ (history storage exceeds active tap storage by at least $2\times$).
  - A naive full candidate scan per step exceeds R2-FLOP ($\ge 100$ FLOPs), necessitating bounded search scheduling (e.g. $M \le 4$ probes/step).
- **Decisive Falsification Threshold:**
  - History storage and candidate search are negligible ($\rho_{\text{MEM}} < 0.5$ and full scan costs $\le 20$ FLOPs).

---

### Hypothesis H7: Discrete Lag Memory and Recurrent Memory Coexist Without Interference
- **Theoretical Rationale:** Discrete shift-register delays and continuous latent dynamical memory represent orthogonal inductive biases. When dynamic lag allocation is paired with LEBRE's scalar recurrent unit, the lag discovery mechanism will activate on discrete delays (D1–D3), the recurrent unit will activate on continuous latch/Poisson dynamics (D11), and both will activate synergistically on hybrid workloads (D12) without mutual suppression.
- **Primary Metrics:** Allocation Ratio and Cross-Interference $\Delta \text{NMSE}$:
  - On D11 (Continuous): Lag allocations $\approx 0$, recurrent NMSE matches isolated recurrent baseline.
  - On D1–D3 (Pure Delay): Recurrent allocation suppressed or neutral, lag discovery matches isolated lag baseline.
  - On D12 (Hybrid): Combined model achieves strictly lower NMSE than either pure lag or pure recurrent model alone.
- **Decisive Confirmation Threshold:**
  - Coexistence confirmed on D12 with $\text{NMSE}(\text{Hybrid}) < \min(\text{NMSE}_{\text{lag}}, \text{NMSE}_{\text{rec}}) - 0.05$.
  - Zero performance degradation on D11 compared to frozen LEBRE.
- **Decisive Falsification Threshold:**
  - Lag allocation cannibalizes recurrent learning on D11, or recurrence prevents lag discovery on D1–D3.

---

## 3. Summary Falsification Matrix

| Hypothesis | Key Metric | Decisive Confirmation Criteria | Decisive Falsification Criteria |
| :--- | :--- | :--- | :--- |
| **H1: Support Discovery** | Support Recall & $\Delta \text{NMSE}_{\text{oracle}}$ | Recall $\ge 70\%$, $\Delta \text{NMSE} \le 0.10$ | Recall $< 40\%$, $\Delta \text{NMSE} > 0.30$ |
| **H2: Non-Contiguous Sparsity** | $K_{\text{active}}$ & NMSE on D3 | $K \le 0.3 \cdot L_{\text{contig}}$ with equal/better NMSE | Contiguous FIR matches taps and compute |
| **H3: Lifecycle Governance** | Active taps on D9 (no delay) | $K_{\text{active}} < 0.5$ ($\ge 80\%$ cut vs $\ell_0$-LMS) | $K_{\text{active}} \ge 1.5$ (spurious tap latching) |
| **H4: Support Tracking** | $T_{\text{reloc}}$ & $T_{\text{evict}}$ on D4/D6 | $T_{\text{reloc}} < 1,500$ steps, $T_{\text{evict}} < 1,500$ steps | $T_{\text{reloc}} > 4,000$ steps (tracking failure) |
| **H5: Quiescence $\ne$ Obsolescence** | Tap survival rate on D7 | Survival $\ge 80\%$ (vs $\le 20\%$ for magnitude) | Survival $< 40\%$ under two-timescale |
| **H6: Discovery Bottleneck** | $\rho_{\text{MEM}}$ and Scan FLOPs | $\rho_{\text{MEM}} \ge 2.0$, full scan $> 100$ FLOPs | $\rho_{\text{MEM}} < 0.5$, full scan $< 20$ FLOPs |
| **H7: Discrete/Recurrent Coexistence**| NMSE on Hybrid D12 & D11 | Hybrid NMSE drops by $> 0.05$; no loss on D11 | Mutual suppression or degradation on D11 |
