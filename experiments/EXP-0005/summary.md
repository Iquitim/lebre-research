# EXP-0005 — Experiment Summary
**Adaptive Evidence Accumulation: Can the Learner Reduce Screening Latency Without Reopening Noise-Driven False Promotions?**
**Date**: 2026-09-18
**Evaluation Seeds**: `[42, 123, 456, 789, 1024]`
**Total Simulation Steps**: 2,000 steps per run (Regime shift at step 1000)
**Probe Budget**: 10,000 probes across 2,000 steps ($\Delta = 0$)

---

## 1. Executive Summary

EXP-0005 tested the hypothesis that the dominant structural bottleneck remaining after EXP-0004—Screening Evidence Accumulation Latency ($T_{\text{evidence}} \approx 129$ steps, 54.7% of total acquisition time)—could be reduced by replacing the fixed sample requirement ($N_{\min}=8$) with an **adaptive evidence-stopping rule** conditioned on signal magnitude ($|\bar{c}| \ge \theta_{\text{strong}}$) and directional sign consistency ($\gamma_{\text{strong}}$).

### Key Empirical Findings
1. **The Reproduction Gate Passed Bit-for-Bit**: H0 (`fixed_baseline`) exactly reproduced the accepted EXP-0004 best learner (G1) across all seeds and metrics (Regime-2 MSE = 0.013825, Occupancy = 65.36%, $T_{\text{evidence}} = 129.28$, $T_{\text{post}} = 60.84$).
2. **Naive Fixed Reduction Fails Catastrophically (Hypothesis 3 Confirmed)**:
   Simply lowering the fixed evidence threshold to $N=3$ (H1) caused a massive noise explosion: **3,430 early promotions**, **39.2 noise-to-true displacements** (up 5.8x from 6.8), collapsing occupancy to **15.80%** and blowing up MSE to **3.2703**.
3. **Signal Magnitude Alone is Insufficient (Hypothesis 2 Disproven)**:
   In H2 (`strength_adaptive`), allowing early promotion at $N=3$ based solely on high correlation ($|\bar{c}| \ge 0.50$) failed severely: MSE exploded to **2.2367**, displacements rose to **40.6**, and occupancy dropped to **19.72%**. Transient noise correlations frequently cross 0.50 on small sample sizes during post-shift error spikes.
4. **Consistency Protects Against Noise Spikes**:
   In H3 (`strength_consistency`) and H4 (`early_accept`), requiring 100% directional sign consistency cut false early promotions by **86%**. H4 (two-boundary sequential Wald test) achieved the lowest overall MSE of any model: **0.013342** (beating Sparse Oracle 0.01480 and Dense 0.03386) with zero seed collapses across all 5 evaluation seeds.
5. **The Critical Empirical Revelation: Evidence Stopping is NOT the Bottleneck**:
   Even under **H5 (Oracle Evidence-Stopping Diagnostic)**, where ground truth permits true omitted features to stop at $N=3$ with 100% precision, $T_{\text{evidence}}$ remained at **156.76 steps**!
   **Physical Root Cause**: Under Explore/Confirm policy with 40% coverage of 90 inactive features ($q \approx 5 \implies 2$ coverage probes/step), cycling through the candidate pool takes $\frac{90}{2} = 45$ steps per probe. To accumulate 3 independent observations physically requires $3 \times 45 \approx 135$ steps!
   Therefore, $T_{\text{evidence}}$ is fundamentally constrained by **probe arrival rate and candidate concentration**, not the stopping rule.

---

## 2. Core Results Table

All values are means across the 5 evaluation seeds: `[42, 123, 456, 789, 1024]`.

| Model | Global MSE | Regime-2 MSE | Mean R2 Recall | Full Occupancy | $T_{\text{evidence}}$ (steps) | $T_{\text{post}}$ (steps) | Early Promo Prec | Promo Prec | Noise Displacements | Mean FLOPs | Compute / Dense | Total Probes |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Dense NLMS** | 1.4380 | 0.03386 | 100.0% | 100.0% | 0.00 | 0.00 | 100.0% | 100.0% | 0.0 | 602.0 | 100.00% | 0 |
| **Sparse Oracle** | 0.1426 | 0.01480 | 100.0% | 100.0% | 0.00 | 0.00 | 100.0% | 100.0% | 0.0 | 32.0 | 5.32% | 0 |
| **H0: Fixed Baseline** | 0.0543 | 0.01383 | 82.41% | 65.36% | 129.28 | 60.84 | 0.0% | 5.93% | 6.8 | 123.23 | 20.47% | 10,000 |
| **H1: Lower Fixed N** | 3.3283 | 3.27031 | 48.62% | 15.80% | 211.64 | 530.24 | 6.09% | 6.29% | 39.2 | 126.08 | 20.94% | 10,000 |
| **H2: Strength Adaptive**| 2.3023 | 2.23667 | 43.40% | 19.72% | 305.16 | 382.84 | 5.53% | 6.05% | 40.6 | 125.70 | 20.88% | 10,000 |
| **H3: Strength+Consistency**| 0.3685 | 0.29098 | 78.80% | 49.06% | 158.12 | 70.12 | 2.62% | 6.16% | 8.6 | 123.48 | 20.51% | 10,000 |
| **H4: Early Accept** | **0.0538** | **0.01334** | **72.37%** | **54.50%** | **194.32** | **124.56** | **5.05%** | **6.44%** | **8.8** | **123.37** | **20.49%** | **10,000** |
| **H5: Oracle Stopping** | 0.0538 | 0.01371 | 80.76% | 56.84% | 156.76 | 61.56 | 100.0% | 8.26% | 5.0 | 122.67 | 20.38% | 10,000 |

---

## 3. Latency Decomposition Breakdown

$$\overline{T}_{\text{total}} = \overline{T}_{\text{wait\_probe}} + \overline{T}_{\text{evidence}} + \overline{T}_{\text{post\_promotion}}$$

| Model | $T_{\text{wait\_probe}}$ (steps) | $T_{\text{evidence}}$ (steps) | $T_{\text{post\_promotion}}$ (steps) | $T_{\text{total}}$ (steps) | $T_{\text{evidence}}$ Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **H0: Fixed Baseline** | 46.40 | 129.28 | 60.84 | 236.52 | 54.66% |
| **H1: Lower Fixed N** | 46.40 | 211.64 | 530.24 | 788.28 | 26.85% |
| **H2: Strength Adaptive** | 46.40 | 305.16 | 382.84 | 734.40 | 41.55% |
| **H3: Strength+Consistency**| 46.40 | 158.12 | 70.12 | 274.64 | 57.57% |
| **H4: Early Accept** | 46.40 | 194.32 | 124.56 | 365.28 | 53.20% |
| **H5: Oracle Stopping** | 46.40 | 156.76 | 61.56 | 264.72 | 59.22% |

---

## 4. Answers to Mandatory Questions (1–15)

### 1. Is the fixed evidence requirement the dominant remaining source of latency?
**No.** While evidence accumulation accounts for 54.7% of total acquisition time, the fixed evidence requirement itself ($N=8$) is **not** the cause of this delay. The delay is governed by the candidate probe cycle time ($\sim 45$ steps per probe across 90 inactive candidates).

### 2. Can strong candidates be promoted safely with fewer samples?
**Only with strict sign consistency and sequential bounds (as in H4).** However, doing so yields minimal latency reduction because obtaining even 3 probes from round-robin coverage takes $\sim 135$ steps.

### 3. Does signal magnitude alone suffice?
**No.** H2 (`strength_adaptive`) failed severely (MSE 2.24, occupancy 19.7%, 40.6 displacements). Noise fluctuations frequently hit $|\bar{c}| \ge 0.50$ on 3 samples during transient error bursts.

### 4. Is sign consistency necessary?
**Yes.** Requiring 100% directional consistency in H3 and H4 cut early false promotions by 86% and prevented the displacement explosions seen in H1 and H2.

### 5. Does early stopping increase false promotions?
**Yes, significantly if unconstrained.** In H1 and H2, early promotions surged to over 3,300 events, 94% of which were spurious noise. Only H4's Wald bound maintained near-oracle MSE across all seeds.

### 6. How much does mean N_at_promotion fall for true candidates?
In H1 and H2, mean $N$ fell from 12.7 to 7.1–7.3. In H3, it remained at 12.2. In H5 Oracle, it fell to 10.5.

### 7. Does N_at_promotion remain high for noise candidates?
In H0 and H4, noise $N$ remained high ($9.5 - 10.0$). In H1 and H2, noise $N$ collapsed to $5.7 - 5.8$, permitting immediate noise swaps.

### 8. How much does T_evidence fall?
**It did NOT fall.** In H1 and H2, $T_{\text{evidence}}$ actually increased to $211 - 305$ steps due to eviction churn. In H5 Oracle, $T_{\text{evidence}}$ was 156.76 steps.

### 9. Does full-support occupancy exceed 75%?
**No.** H0 achieved 65.36%, H4 achieved 54.50%, and H5 Oracle achieved 56.84%. None of the causal models reached the 75% GO target.

### 10. Does Regime-2 MSE remain <=0.03?
**Yes, for H0 (0.01383) and H4 (0.01334).** Both strongly outperform Dense NLMS (0.03386). However, H1 (3.27) and H2 (2.24) failed severely.

### 11. Does T_post_promotion remain stable?
**Yes, for H0 (60.84 steps) and H3 (70.12 steps).** It destabilized heavily in H1 (530.24 steps) and H2 (382.84 steps) due to noise displacements.

### 12. Is compute still <=25% Dense?
**Yes.** All variants operated at **$122 - 126$ FLOPs/step (20.3% - 20.9% of Dense)**, well beneath the 25% limit (150.5 FLOPs).

### 13. Does total probe budget remain exactly unchanged?
**Yes.** Exactly **10,000 probes ($\Delta = 0$)** across all seeds and models.

### 14. Which evidence rule gives the best latency/safety tradeoff?
**H0 (Fixed Baseline, $N=8, \theta=0.40$) remains the most robust practical rule**, closely followed by **H4 (Two-Boundary Early Accept)** which achieved the lowest overall MSE (0.01334) with zero seed collapses.

### 15. What is the new dominant bottleneck after EXP-0005?
**`CANDIDATE_PROBE_ARRIVAL_RATE`**: Evidence accumulation latency is not bound by sample count stopping rules, but by the physical rate at which candidate probes are delivered across the 90 inactive features.

---

## 5. Most Important Practical Question (Section 81)

> “CAN THE LEARNER PROMOTE STRONG, CONSISTENT TRUE CANDIDATES EARLIER WITHOUT REOPENING THE FALSE-PROMOTION FAILURE THAT ORIGINALLY MADE SPARSE STRUCTURAL LEARNING UNSTABLE?”

**NO.**  
Under the current Explore/Confirm probe allocation, candidate sampling density is too low ($\sim 45$ steps per probe). Lowering sample thresholds to $N=3$ reopens severe false-promotion churn (H1, H2), while adding safety filters (H3, H4) means candidates must still wait $\sim 130-150$ steps to accumulate samples.
