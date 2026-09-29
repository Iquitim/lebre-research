# PROMOTION-POLICY-01: Preregistered Experimental Protocol

**Stage:** PROMOTION-POLICY-01 — Sequential Structural Evidence & False-Promotion Control  
**Protocol Version:** 1.0.0 (Preregistered before final evaluation)  
**Date:** 2026-09-19  
**Lead Auditor:** Skeptical Senior ML Researcher & Sequential Inference Specialist  
**Core Invariants:**
- `ARCHITECTURE = LEBRE`
- `FROZEN_SPEC_VERSION = 0.1` (`FROZEN_WITH_SCOPE_LIMITS`)
- `LEBRE_V0_1_FORMALLY_FROZEN = YES`
- `BENCH_01B_STATUS = SEALED`
- `LEBRE_DIAG_01_STATUS = COMPLETE`
- `M3_STATUS = UNOPENED`
- `NOVELTY_CLAIM_READY = NO`
- `src/` and `tests/` remain bitwise immutable.

---

## 1. Literature-Derived Hypotheses

- **$\mathcal{H}_1$ (Horizon Insufficiency):** The frozen 50-step window is merely too short; increasing the probation window to $T=150$ ($P1$) will substantially eliminate false promotions on A2–A4 without hurting A5/A7.
- **$\mathcal{H}_2$ (Threshold Conservatism):** The 0.05 gain threshold is too loose; tightening the threshold to 0.15 ($P2$) will resolve false promotions without missing useful structures.
- **$\mathcal{H}_3$ (Temporal Replication Value):** True causal recurrent structures persist over time, whereas noise overfitting decays. Requiring independent out-of-sample evidence in two sequential windows ($P3$) will drastically cut false promotions.
- **$\mathcal{H}_4$ (Anytime-Valid Stopping Efficiency):** Nonparametric empirical confidence sequences ($P4$) adaptively terminate poor candidates early while accumulating sufficient evidence for true states, optimizing decision latency and false promotion simultaneously.
- **$\mathcal{H}_5$ (Multiple-Opportunity Gating Value):** Repeated birth attempts create cumulative false-positive risk. Controlling opportunity wealth across births ($P5$) will curb late-stream structural churn.
- **$\mathcal{H}_6$ (Computational Rent):** Simple temporal replication ($P3$) achieves Pareto-superior false-promotion control at near-zero FLOP/memory overhead compared to complex martingale tracking.

---

## 2. Experimental Policy Specifications

1. **P0 (`LEBRE_v0.1_FIXED`):**
   - $T_{\text{prob}} = 50$, $\theta_{\text{promote}} = 0.05$ (Frozen reference baseline).
2. **P1 (`FIXED_LONG`):**
   - $T_{\text{prob}} = 150$, $\theta_{\text{promote}} = 0.05$.
3. **P2 (`FIXED_STRICT`):**
   - $T_{\text{prob}} = 50$, $\theta_{\text{promote}} = 0.15$.
4. **P3 (`TWO_WINDOW_CONFIRM`):**
   - Window A: $t \in [1, 50]$, require $G_A > 0.05$.
   - Window B: $t \in [51, 100]$, require $G_B > 0.02$ on subsequent prequential observations.
   - Promotion occurs only if both conditions pass.
5. **P4 (`CS_PROMOTION`):**
   - Lower Confidence Bound on paired prequential difference $D_t = e_{\text{base}, t}^2 - e_{\text{cand}, t}^2$:
     $$\text{LCB}_t(D) = \bar{D}_t - 1.96 \cdot \frac{\hat{\sigma}_t + 10^{-4}}{\sqrt{t}} \sqrt{1 + \frac{\ln(t + 1)}{t}}$$
   - Early promotion if $\text{LCB}_t > 0.02$ and $t \ge 30$.
   - Early futility stop if $\text{UCB}_t < 0.0$ and $t \ge 60$. Maximum horizon $T_{\text{max}} = 150$.
6. **P5 (`GLOBAL_ERROR_BUDGET`):**
   - Wealth tracker $W_k$ initialized to $1.0$.
   - Each birth deducts $0.10$. Promoted units that demonstrate positive gain refund $0.25$.
   - Births inhibited if $W_k < 0.10$.
7. **P6 (`CS_PLUS_BUDGET`):**
   - P4 within-candidate stopping coupled with P5 across-candidate wealth budgeting.
8. **Reference Control (`LEBRE_NO_REC_BIRTH`):**
   - Causal ablation with zero recurrent births.

---

## 3. Workloads & Seed Protocol

### Workloads:
- **Negative Controls (False-Promotion Assessment):**
  - `A2_Single_Delayed_Dependency` ($y_t = 0.8 x_{1, t-4} + \epsilon_t$)
  - `A3_Multiple_Dispersed_Delays` ($y_t = 0.5 x_{1, t-2} + 0.5 x_{2, t-8} + \epsilon_t$)
  - `A4_Long_Delay_Scaling` ($y_t = 0.8 x_{1, t-30} + \epsilon_t$)
- **Positive Controls (Useful Structure Recall):**
  - `A5_Set_Reset_Quiescent_Memory` (Bistable latch under sparse Poisson triggers)
  - `A7_Extended_Poisson_Quiescence` (Long-gap quiescent retention)
- **Neutral / Mixed Transition Control:**
  - `A8_Abrupt_Tri_Regime_Transition` (Linear $\to$ Lag $\to$ Recurrent)

### Seed Discipline:
- **Development Seeds:** $N=10$, seeds `301` through `310`.
  - Used strictly for sanity checks, numerical verification, and setting hyperparameters of experimental policies.
- **Confirmatory Evaluation Seeds:** $N=30$, seeds `401` through `430`.
  - Hashed and frozen. Evaluated paired sample-for-sample across all 8 variants $\times$ 6 tasks ($1,440$ stream evaluations).

---

## 4. Evaluated Metrics & Formal Definitions

1. **Prequential Paired Difference:**
   $$D_t = (y_t - \hat{y}_{\text{base}, t})^2 - (y_t - \hat{y}_{\text{cand}, t})^2$$
   evaluated before parameter updates.
2. **Post-Promotion Realized Gain at Horizon $H$:**
   $$G_{\text{post}}(H) = 1 - \frac{\sum_{i=1}^H (y_{t_{\text{prom}} + i} - \hat{y}_{\text{live}, t_{\text{prom}} + i})^2}{\sum_{i=1}^H (y_{t_{\text{prom}} + i} - \hat{y}_{\text{base}, t_{\text{prom}} + i})^2}$$
3. **Structural False Promotion Rate ($\text{FPR}_{250}$):**
   $$\text{FPR}_{250} = \frac{\sum \mathbb{I}(G_{\text{post}}(250) < 0)}{\text{Total Evaluated Promotions at } H=250}$$
4. **Structural Recall on Positive Controls:**
   $$\text{Recall}_{\text{useful}} = \frac{\text{Number of Seeds with } \ge 1 \text{ Durably Useful Promotion } (G_{\text{post}} > 0)}{\text{Total Evaluated Seeds (30)}}$$
5. **Structural Precision:**
   $$\text{Precision}_{\text{struct}} = \frac{\text{Durably Useful Promotions } (G_{\text{post}}(250) > 0)}{\text{Total Evaluated Promotions}}$$
6. **Harmful Retention Regret ($R_{\text{harm}}$):**
   $$R_{\text{harm}} = \sum_{t=t_{\text{harm}}}^{t_{\text{evict}}} (L_{\text{live}, t} - L_{\text{no\_rec}, t})$$
7. **Algorithmic Compute & Memory:**
   - Mean FLOPs/step, Peak FLOPs/step, Persistent state bytes.

---

## 5. Lexicographic Decision Framework

1. **Prerequisite Gate 1 (Recall Floor):** Must retain at least **85%** of frozen LEBRE's NMSE improvement on positive controls A5 and A7.
2. **Prerequisite Gate 2 (False-Promotion Reduction):** Must reduce structural false promotions ($\text{FPR}_{250}$) on A2–A4 by at least **50% relative to frozen LEBRE v0.1**.
3. **Selection Gate 3 (Computational Rent & Simplicity):**
   - Overhead $\le 20$ FLOPs/step and $\le 64$ bytes state.
   - If a simpler empirical policy achieves statistically indistinguishable recall and FPR compared to complex martingale tracking, **the simpler policy is selected**.

---

## 6. Statistical Analysis Plan

- Paired differences across seeds computed with 10,000 bootstrap resamples.
- 95% bootstrap confidence intervals for all primary metrics.
- Paired Cohen's $d_z$ effect sizes.
- Two-sided Wilcoxon signed-rank tests for paired significance with Holm-Bonferroni correction across the policy family.

---

## 7. Preregistration Cryptographic Seal

- **Protocol Hash (SHA-256):** `feb14c3e339df023d8db84f58ac0d84e2120e7172d0a0744020833bda36d2d3d`
- **Timestamp:** 2026-09-19T22:00:14-03:00
- **Status:** SEALED BEFORE CONFIRMATORY RUNS

