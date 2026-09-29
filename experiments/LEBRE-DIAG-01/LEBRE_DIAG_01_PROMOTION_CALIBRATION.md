# LEBRE-DIAG-01: Promotion Calibration & False-Promotion Analysis

**Protocol:** LEBRE-DIAG-01  
**Target:** Candidate Promotion Mechanism ($	heta_{\text{promote}} = 0.05$, $T_{\text{prob}} = 50$)  
**Date:** 2026-09-19  

---

## 1. Executive Summary: The False-Promotion Pathology

Across primary diagnostic tasks (**A2**, **A3**, **A4**), candidate recurrent units pass probation at extraordinarily high frequencies due to opportunistic noise-fitting during short probation windows ($T_{\text{prob}}$). However, these promoted units exhibit a **75.5% to 90.9% immediate negative realization rate** ($G_{\text{post}, 50} < 0$) upon coupling to active inference.

| Task | Total Promotions | Evaluated at $H=50$ | False Promotion Rate (FPR) | Mean $G_{\text{prob}}$ | Mean $G_{\text{post}, 50}$ | Correlation $r(G_{\text{prob}}, G_{\text{post}})$ |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **A2** (Single Delay) | 1,037 | 1,031 | **85.1%** | +0.0612 | **-0.0482** | -0.042 (p=0.177) |
| **A3** (Multiple Delays) | 951 | 947 | **75.8%** | +0.0588 | **-0.0344** | -0.018 (p=0.584) |
| **A4** (Long Delay) | 1,028 | 1,022 | **91.4%** | +0.0645 | **-0.0608** | -0.031 (p=0.320) |
| **A5** (Set/Reset) | 504 | 502 | **36.3%** | +0.1420 | **+0.1231** | +0.482 (p < 1e-10) |
| **A7** (Poisson Gap) | 635 | 632 | **32.0%** | +0.1844 | **+0.1937** | +0.512 (p < 1e-10) |
| **A8** (Tri-Regime) | 581 | 578 | **73.9%** | +0.0715 | **-0.0231** | +0.114 (p = 0.006) |

---

## 2. Uncalibrated Probation Gain

In tasks A2–A4, the Pearson correlation between probation gain ($G_{\text{prob}}$) and out-of-sample realized gain ($G_{\text{post}}$) is statistically indistinguishable from zero ($r \approx -0.02$ to $-0.04$). A higher probation score provides zero predictive validity regarding durable future benefit.

In stark contrast, on positive control tasks (A5, A7), $G_{\text{prob}}$ strongly and significantly correlates with durable post-promotion gain ($r > +0.48, p < 10^{-10}$).

---

## 3. Promotion Trajectory Breakdown

Promoted candidates are categorized into 5 trajectories:
1. **`IMMEDIATE_NEGATIVE`:** $G_{\text{post}, 50} < 0$ (immediately degrades prediction).
2. **`SIGN_FLIP`:** $G_{\text{post}, 50} > 0$ but later turns negative before $H=250$.
3. **`DECAYING_POSITIVE`:** $G_{\text{post}}$ remains positive but decays over time.
4. **`STABLE_POSITIVE`:** $G_{\text{post}}$ remains positive and stable ($G_{250} \ge G_{50}$).
5. **`INDETERMINATE`:** Candidate evicted before reaching $H=50$.

| Task | Immediate Negative (%) | Sign Flip (%) | Decaying Positive (%) | Stable Positive (%) | Indeterminate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **A2** | **84.57%** | 0.00% | 0.00% | **0.00%** | 15.43% |
| **A3** | **75.50%** | 0.00% | 0.00% | **0.00%** | 24.50% |
| **A4** | **90.86%** | 0.00% | 0.00% | **0.00%** | 9.14% |
| **A5** | 36.11% | 3.57% | 5.75% | **14.29%** | 40.28% |
| **A7** | 31.81% | 0.16% | 7.72% | **9.61%** | 50.71% |
| **A8** | 73.49% | 0.00% | 1.72% | **1.03%** | 23.75% |

### Key Diagnostic Takeaway:
On A2, A3, and A4, **zero candidates (0.00%)** achieved `STABLE_POSITIVE` trajectory across 3,016 promotions. Over 80% are immediately detrimental, and the rest are evicted rapidly.
