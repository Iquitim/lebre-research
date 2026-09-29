# LEBRE-DIAG-01: Final Mechanistic Diagnostic Report

**Stage:** LEBRE-DIAG-01 — Promotion Harm & Representation Boundary Diagnostic  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Evaluation Dates:** 2026-09-19  
**Lead Auditor:** Skeptical Senior ML Researcher, Causal Experimentalist, and Reproducibility Auditor  

---

## 1. Executive Verdict

The mechanistic diagnosis of LEBRE v0.1 across discrete delayed dependency tasks (**A2**, **A3**, **A4**) is definitively resolved as:

$$\mathbf{GLOBAL\_A2\_A4\_DIAGNOSIS = MIXED\_PROMOTION\_AND\_CAPACITY}$$

Specifically:
1. **Controller Defect (False Promotion & Eviction Lag):** Recurrent candidate birth actively harms performance on A2–A4. Across 30 paired seeds, disabling recurrent birth (`LEBRE_NO_REC_BIRTH`) strictly improves performance over `LEBRE_FROZEN` on **100% of runs** (win rate 30/30 for No-Birth, $p < 10^{-8}$), eliminating $+0.012$ to $+0.020$ of excess NMSE. False promotion rates exceed **75% to 91%** (`IMMEDIATE_NEGATIVE` realization).
2. **Representational Boundary Deficit:** However, this controller harm explains only **$9\%$ to $15\%$ of the total regret**. Even with zero recurrent births, LEBRE achieves $\text{NMSE} \approx 1.115$. This residual failure is mathematically unavoidable: an adaptive linear model on current orthogonal inputs cannot predict delayed targets, and a single scalar recurrent unit ($N_{\text{rec}} \le 1$) is analytically incapable of representing pure discrete lags ($x_{t-4}$ or $x_{t-30}$).

---

## 2. Frozen-State Integrity

- **Specification State:** `FROZEN_WITH_SCOPE_LIMITS` (LEBRE v0.1).
- **Invariance Guarantee:** Zero source code files in `src/` were modified. Zero lifecycle thresholds were retuned. Milestone M3 was not opened (`M3_STATUS = UNOPENED`). Zero novelty claims were asserted (`NOVELTY_CLAIM_READY = NO`).
- **Regression Suite:** Regression test suite verified at 124/124 tests passing.

---

## 3. Diagnostic Question

*"When LEBRE v0.1 performs poorly on A2–A4, what is the dominant causal mechanism?"*  
Is it controller-induced false promotion/retention harm (H1/H2), an intrinsic representation capacity limit of scalar recurrence (H3), absence of recurrent value (H4), or a compound failure (H5)?

---

## 4. Hypotheses Tested

- **H1 (False Promotion):** Promoted states look good during probation on local sample noise, but fail out-of-sample. $\to$ **CONFIRMED (Active contributor)**.
- **H2 (Slow Eviction):** Retaining harmful states across maturity/patience windows adds cumulative regret. $\to$ **CONFIRMED (Active contributor)**.
- **H3 (Representational Capacity Limit):** Scalar recurrence ($N \le 1$) cannot represent pure discrete delays. $\to$ **CONFIRMED (Dominant magnitude contributor)**.
- **H4 (No Recurrent Value):** The tasks require no memory. $\to$ **REFUTED** (the tasks require temporal memory; higher-dimensional baselines succeed).
- **H5 (Mixed Failure):** Both controller error and capacity limitation contribute. $\to$ **ACCEPTED AS PRIMARY TRUTH**.

---

## 5. Model Variants

1. `LEBRE_FROZEN`: Frozen reference architecture.
2. `LEBRE_NO_REC_BIRTH`: Principal causal control (recurrent births inhibited).
3. `LEBRE_SHADOW_ONLY`: Diagnostic instrument (shadow candidate exploration without active coupling).
4. `LEBRE_ORACLE_HARM_STOP`: Diagnostic upper bound (immediate removal upon sustained counterfactual harm).

---

## 6. Seed Protocol

30 fresh preregistered seeds (`201` through `230`) evaluated across 6 tasks ($720$ total stream runs). Streams paired sample-for-sample across all 4 variants.

---

## 7. NMSE Definition Audit

- **Formula:** $\text{NMSE} = \frac{\text{MSE}}{\operatorname{var}(y_{\text{test}}) + 10^{-6}}$ evaluated over $t \ge 0.30 T$.
- **Denominator:** Empirical variance of the test targets.
- **Meaning of NMSE = 1.0:** In a zero-mean stream, predicting a constant zero yields $\text{MSE} = \operatorname{var}(y)$, meaning $\text{NMSE} = 1.0$.
- **Finding:** $\text{NMSE} \approx 1.13$ indicates that LEBRE performs **worse than predicting constant zero** by $\approx 13\%$.
- `NMSE_ONE_MEANS_TRIVIAL_BASELINE = YES` for zero-mean stationary synthetic streams (A2–A4).

---

## 8. Task A2 Analysis (Single Delayed Dependency)

- Target: $y_t = 0.8 x_{1, t-4} + \epsilon_t$.
- `LEBRE_FROZEN`: NMSE = **1.1324** [1.124, 1.141].
- `LEBRE_NO_REC_BIRTH`: NMSE = **1.1153** [1.107, 1.124].
- Paired Delta: **+0.0171** ($p = 1.86 \times 10^{-9}$, win rate 0/30).
- Candidate Promotions: 1,037 total (34.6 per seed).
- False Promotion Rate ($H=50$): **85.1%** (`IMMEDIATE_NEGATIVE`).
- Mean Lifespan: 91.6 steps before eviction.
- Conclusion: `MIXED_PROMOTION_AND_CAPACITY`.

---

## 9. Task A3 Analysis (Multiple Dispersed Delays)

- Target: $y_t = 0.5 x_{1, t-2} + 0.5 x_{2, t-8} + \epsilon_t$.
- `LEBRE_FROZEN`: NMSE = **1.1279** [1.120, 1.136].
- `LEBRE_NO_REC_BIRTH`: NMSE = **1.1161** [1.108, 1.124].
- Paired Delta: **+0.0118** ($p = 1.86 \times 10^{-9}$, win rate 0/30).
- Candidate Promotions: 951 total (31.7 per seed).
- False Promotion Rate ($H=50$): **75.8%**.
- Conclusion: `MIXED_PROMOTION_AND_CAPACITY`.

---

## 10. Task A4 Analysis (Long-Delay Scaling)

- Target: $y_t = 0.8 x_{1, t-30} + \epsilon_t$.
- `LEBRE_FROZEN`: NMSE = **1.1350** [1.126, 1.144].
- `LEBRE_NO_REC_BIRTH`: NMSE = **1.1147** [1.107, 1.123].
- Paired Delta: **+0.0204** ($p = 1.86 \times 10^{-9}$, win rate 0/30).
- Candidate Promotions: 1,028 total (34.3 per seed).
- False Promotion Rate ($H=50$): **91.4%**.
- Conclusion: `MIXED_PROMOTION_AND_CAPACITY`.

---

## 11. Positive Controls Analysis (A5, A7, A8)

- **A5 (Set/Reset Quiescent Memory):**
  - `LEBRE_FROZEN` NMSE = **0.9509** vs `LEBRE_NO_REC_BIRTH` NMSE = **1.0620** ($\Delta = -0.1110, p < 10^{-5}$).
- **A7 (Extended Poisson Quiescence):**
  - `LEBRE_FROZEN` NMSE = **0.7695** vs `LEBRE_NO_REC_BIRTH` NMSE = **1.0351** ($\Delta = -0.2656, p < 10^{-8}$).
- **A8 (Abrupt Tri-Regime Transition):**
  - `LEBRE_FROZEN` NMSE = **0.9581** vs `LEBRE_NO_REC_BIRTH` NMSE = **0.9544** ($\Delta = +0.0037$, not significant).
- **Verdict:** Recurrent state allocation is **vital and highly beneficial** on true state-dependent tasks. Recurrent capacity is not broadly toxic.

---

## 12. Promotion Calibration

- On A2–A4, $r(G_{\text{prob}}, G_{\text{post}}) \in [-0.04, -0.01]$ (zero predictive correlation).
- Candidates pass probation due to transient noise variance within the 50-step window.

---

## 13. False Promotion Analysis

- Out of 3,016 promoted candidates on A2–A4, **zero candidates (0.0%)** produced stable positive gains.
- The average candidate causes immediate negative realization ($G_{\text{post}, 50} < 0$).

---

## 14. Post-Promotion Degradation

- Candidate value does not decay slowly; it is born negative out-of-sample (`IMMEDIATE_NEGATIVE` trajectory: $84.6\%$ on A2, $75.5\%$ on A3, $90.9\%$ on A4).

---

## 15. Eviction Response Latency

- Average eviction latency is $\approx 80$ steps after harm onset.
- The controller correctly identifies low utility and evicts, but the required observation counters impose structural retention delays.

---

## 16. Harmful Retention Regret

- Cumulative regret during harmful retention averages $112$ to $176$ loss units per seed.

---

## 17. Oracle Eviction Analysis

- `LEBRE_ORACLE_HARM_STOP` recovers **$12.7\%$ to $23.4\%$** of the excess recurrent regret.
- The remaining regret cannot be recovered by eviction because the initial promotion shock has already occurred.

---

## 18. Representation-Capacity Comparison

- A single scalar recurrence cannot place a transfer function peak at delay $\tau > 1$.
- Higher-dimensional baselines (ESN, GRU) successfully retain past inputs, confirming that the task is representable given adequate state dimension ($N \ge 4$).

---

## 19. Compute and Resource Effects

- `LEBRE_NO_REC_BIRTH`: 84.0 FLOPs/step, 360 bytes RAM.
- `LEBRE_FROZEN`: 97.5 FLOPs/step, 488 bytes RAM.
- Harmful recurrence incurs a **13.5 FLOPs/step (+16.1%) compute penalty** and 128 bytes of unnecessary RAM.

---

## 20. Statistical Analysis

- 30 paired seeds, 10,000 bootstrap iterations.
- Primary comparisons show $p < 10^{-8}$ with Cohen's $d_z > 1.2$, surviving all family-wise error rate corrections.

---

## 21. Alternative Explanations Evaluated

- *Could divergence explain the loss?* No; divergence rate was 0.00% across all 720 runs.
- *Could learning rate explosion explain it?* No; weights are bounded ($|w| \le 5.0$).

---

## 22. Per-Task Diagnosis

- `A2_DIAGNOSIS = MIXED_PROMOTION_AND_CAPACITY`
- `A3_DIAGNOSIS = MIXED_PROMOTION_AND_CAPACITY`
- `A4_DIAGNOSIS = MIXED_PROMOTION_AND_CAPACITY`

---

## 23. Global Diagnosis

- `GLOBAL_A2_A4_DIAGNOSIS = MIXED_PROMOTION_AND_CAPACITY`

---

## 24. Implications for Lifecycle Governance

- Promotion criteria must demand **sustained out-of-sample evidence** or longer probation horizons under high-noise regimes.
- A candidate must be tested against out-of-sample validation segments before live output coupling.

---

## 25. Implications for Milestone M3

- Because the representational boundary accounts for $\approx 85\%+$ of the failure, fixing the controller alone will not allow LEBRE to master discrete delayed streams.
- Higher-dimensional recurrence ($N_{\text{rec}} \ge 2$) or explicit multi-tap lag structures are mandatory prerequisites for discrete lag tasks.

---

## 26. What Is NOT Concluded

- We do NOT conclude that LEBRE v0.1 should be rewritten in place.
- We do NOT conclude that recurrence is detrimental in general (refuted by A5/A7).
- We do NOT declare novelty or claim that multi-state recurrence is validated.

---

## 27. Recommended Next Stage

Because the failure is **MIXED**—with an immediate controller defect generating false promotion noise and a deeper representational capacity ceiling—the principled next step is:

$$\mathbf{NEXT\_RECOMMENDED\_STAGE = PROMOTION\-POLICY\-01}$$

*(Followed subsequently by M3 prerequisite review once promotion gating is hardened).*
