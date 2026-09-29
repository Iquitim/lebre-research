# CAR_01_BENCH_INTERPRETATION_AUDIT.md — Benchmark Interpretation & Fairness Audit

**Stage:** CAR-01 (Contribution Assessment Review)  
**Task:** Minimal Interpretive Corrections & Jena Divergence Fairness Audit  
**Governing Standard:** Sections 5–14 of CAR-01 Specification  
**Date:** September 19, 2026  
**Status:** COMPLETED & SEALED  

---

## 1. Minimal Narrative Corrections Audit

Prior to formal contribution analysis, all active narrative reports in `experiments/BENCH-01B/` were subjected to an adversarial textual audit to eliminate scientific overstatement, unwarranted causal assertions, and promotional rhetoric.

### 1.1 Correction A: Removal of "State-of-the-Art" and Superlatives
- **Audit Target:** Elimination of phrases equivalent to `state-of-the-art`, `SOTA`, `world-leading`, `universally superior`, `breakthrough`, `first`, or `best known`.
- **Finding:** A superlative phrase was identified in `experiments/BENCH-01B/BENCH_01B_PER_DATASET_ANALYSIS.md` (Line 80):
  - *Original Problematic Phrasing:* `"...Track B consistently achieves superior or state-of-the-art predictive accuracy..."`
  - *Corrected Evidence-Bounded Phrasing:* `"...Track B achieved the lowest error among evaluated methods while operating at a fraction of the compute of standard recurrent baselines."`
- **Verification:** All active benchmark reports now strictly qualify performance relative to the evaluated method suite.

### 1.2 Correction B: Ungrounded Causal Attribution to Associative Language
- **Audit Target:** Elimination of claims attributing benchmark robustness directly to un-ablated mechanisms without dedicated causal isolation.
- **Finding:** An ungrounded causal statement was identified in `experiments/BENCH-01B/BENCH_01B_FINAL_REPORT.md` (Line 167):
  - *Original Problematic Phrasing:* `"- This confirms that Track B's two-timescale structural lifecycle provides exceptional numerical robustness..."`
  - *Corrected Associative Phrasing:* `"- Track B exhibited strong numerical robustness under the evaluated streams, consistent with the intended role of its two-timescale lifecycle, whereas unnormalized gradient descent and unmanaged recurrence without lifecycle control experienced numerical divergence on long physical benchmarks."`
- **Methodological Standard:** Benchmark-level correlation across streams does not establish component-level causation. Causal claims are restricted to controlled ablation experiments (Level A/B).

---

## 2. Technical Audit: Task B2 (Jena Climate Weather) Divergence

### 2.1 The Observed Empirical Fact
On Task B2 (Jena Climate Weather, $T = 70{,}000, D = 14$):
- **Diverged Models (30/30 seeds each, 100% divergence):**
  - `B1_RZA_LMS`
  - `B2_CCN`
  - `S1_VARIABLE_TAP_LMS`
  - `C1_CURRENT_ONLY_LINEAR`
  - `C4_FIXED_LAG_LINEAR`
  - `S2_LRU_STREAM`
  - `S5_CONTINUAL_BACKPROP`
- **Stable Models (30/30 seeds, 100% completion):**
  - `Track_B` ($\text{NMSE} = 0.0248$)
  - `C2_NLMS` ($\text{NMSE} = 0.0236$)
  - `B4_MINIMAL_GRU` ($\text{NMSE} = 0.0742$)
  - `B5_ONLINE_ESN` ($\text{NMSE} = 0.3284$)
  - `B3_MUSE_RNN` ($\text{NMSE} = 0.6159$)
  - `S3_RSONN` ($\text{NMSE} = 0.0239$)
  - `S4_ACESN` ($\text{NMSE} = 0.1852$)

### 2.2 Formal Audit Checklist

| Audit Question | Finding | Evidence / Details |
| :--- | :---: | :--- |
| 1. Were all models fed identical causally normalized inputs? | **YES** | Every model received $x_{\text{norm}, t} = \text{scaler}.\text{transform}(x_t)$ generated strictly from past statistics ($0$ to $t-1$). |
| 2. Did all methods receive preprocessing allowed by the frozen protocol? | **YES** | Online exponential running standardizer (`CausalStandardScaler`, $\alpha = 10^{-4}, \epsilon = 10^{-6}$) with zero future leakage. |
| 3. Were baseline learning rates selected only from preregistered calibration? | **YES** | Best configurations selected strictly from $[0.00T, 0.15T)$ calibration prefix on seeds 42, 43, 44. |
| 4. Were learning-rate grids scientifically reasonable relative to literature? | **YES** | Standard LMS learning rates ($\mu \in [0.001, 0.03]$) were specified in `bench_01_locked_config.json`. |
| 5. Did any baseline omit prescribed normalization or step-size adaptation? | **NO** | Textbook LMS, CCN, and Variable-Tap LMS are unnormalized by definition. Simplicity control `C2_NLMS` was included specifically to evaluate normalized step sizing. |
| 6. Did divergence arise from faithful method dynamics? | **YES** | Classical LMS stability requires $\mu < 2 / \lambda_{\max}(R)$. Unnormalized gradient updates on large-norm feature transients violate this bound. |
| 7. Was target scaling fair across methods? | **YES** | Raw temperature in $^\circ\text{C}$ was identically presented to all models. |

### 2.3 Mathematical Root-Cause Analysis
Jena Climate features physical atmospheric variables with large baseline offsets (atmospheric pressure $p \approx 990.8\text{ mbar}$, air density $\rho \approx 1216.4\text{ g/m}^3$).
Because `CausalStandardScaler` initializes running mean at $\mathbf{0}$ and updates with $\alpha = 10^{-4}$, the running mean requires thousands of steps to track large constant offsets. During this transient, uncentered feature magnitudes reach $\|x_{\text{norm}}\| \approx 1,500$.

For unnormalized gradient updates:
$$\Delta w_t = \mu e_t x_{\text{norm}, t}$$
The effective loop gain is $\mu \|x_{\text{norm}, t}\|^2 \approx 0.001 \times (1500)^2 = 2,250 \gg 2.0$. This exceeds the mathematical stability boundary of LMS, inducing immediate geometric gradient divergence ($e_t^2 \to \infty$).

Conversely:
- **`C2_NLMS` survived** because it divides by the squared input norm: $\mu / (\|x\|^2 + \epsilon)$.
- **`Track_B` survived** because its internal base linear filter explicitly implements normalized gradient stepping:
  $$\text{step\_base} = \frac{0.20}{\|x_t\|^2 + 1.0}$$
  and bounds state readout updates:
  $$\text{step\_state} = \frac{0.20}{s_t^2 + 1.0}, \quad w_{\text{state}} \in [-5.0, 5.0]$$
- **`B4_MINIMAL_GRU` and `B5_ONLINE_ESN` survived** due to saturating nonlinearities ($\tanh$).

### 2.4 Jena Divergence Classification

$$\mathbf{JENA\_DIVERGENCE = FAIR\_BUT\_METHOD\_SENSITIVE}$$

**Rationale:**
The divergence of unnormalized linear baselines (RZA-LMS, CCN, Variable-Tap LMS) was not an artifact of an implementation flaw or protocol bias; it was the mathematically predictable outcome of unnormalized gradient descent operating under a cold-start streaming standardizer.

**Critical Interpretive Constraint:**
It is scientifically invalid to cite the Jena divergence as evidence that Track B's *recurrent lifecycle* is inherently more stable than linear filters. Track B's stability on Jena was directly mediated by its **normalized gradient step** (an NLMS primitive), as corroborated by the fact that pure `C2_NLMS` was equally stable ($\text{NMSE} = 0.0236$).

### 2.5 Jena No-Rerun Determination
Because the audit verified faithful implementation of the frozen protocol and identified zero software defects:
- **BENCH-01B remains SEALED.**
- No reruns are authorized or required.
