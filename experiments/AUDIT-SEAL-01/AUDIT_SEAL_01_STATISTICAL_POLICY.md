# AUDIT-SEAL-01: Permanent Statistical Policy & Inferential Unit Lock
## Rigorous Standards for Streaming Learning & Comparative Benchmarking

**Policy ID:** `STAT-POLICY-2026-v1.0`  
**Effective Date:** September 19, 2026  
**Governing Authority:** Skeptical Senior ML Researcher, Statistical Reviewer, Reproducibility Auditor  
**Scope:** All past, present, and future experimental evaluations in the LEBRE research program.

---

## 1. Immutable Invariant: The Primary Inferential Unit

$$\mathbf{PRIMARY\_INFERENTIAL\_UNIT = INDEPENDENT\_SEED}$$

### 1.1 Definition of the Independent Experimental Unit
In streaming system identification and online adaptive learning, the independent experimental unit is **one complete simulation run initialized with an independent pseudorandom seed**.

### 1.2 Explicit Prohibitions against Pseudoreplication
Under no circumstances may the following within-run or within-seed observations be pooled and treated as independent degrees of freedom ($N$):
1. **Time Steps ($t \in \{1, \dots, T\}$):** Time-series residuals $e_t$ are serially correlated and conditionally dependent. Treating $T = 10,000$ steps as $N = 10,000$ independent samples is strictly prohibited.
2. **Structural / Tap Events:** Tap promotions, cooling transitions, and evictions within a run are serially dependent.
3. **Candidate Probes:** Rotating probe correlations across time steps share the underlying data realization.
4. **Multiple Tasks Evaluated on the Same Seed:** Different tasks run on the same random seed share generator draws and input structure. Pooling $K$ tasks across $N$ seeds ($K \times N$ rows) as independent samples constitutes **pseudoreplication** (Hurlbert, 1984) and artificially deflates p-values to infinitesimal values ($p < 10^{-15}$).

Unless a formal, preregistered hierarchical linear mixed-effects model with random intercepts/slopes per seed is explicitly specified, all hypothesis testing must aggregate performance per seed prior to hypothesis testing:
$$\bar{M}_s = \frac{1}{K} \sum_{k=1}^K M_{s, k}, \quad s = 1, \dots, N_{\text{seeds}}$$

---

## 2. Mandatory Reporting Standards for Comparative Tests

For any paired comparative claim between baseline $A$ and proposed model $B$:

1. **Sample Size Disclosure:** Explicitly report the number of independent evaluation seeds ($N_{\text{eff}}$), verifying zero overlap with prior development seeds.
2. **Paired Differences Vector:** Explicitly persist the paired differences $D_s = M_{A, s} - M_{B, s}$ for all $s \in \{1, \dots, N\}$.
3. **Wilcoxon Signed-Rank Reporting:**
   - Report the exact test statistic $W = \min(W^+, W^-)$.
   - For $N \le 50$, compute and report the **exact combinatorial two-sided p-value** ($p_{\text{exact}}$).
   - If an asymptotic Gaussian approximation is used (`method="approx"` in SciPy), it must be explicitly labeled as **asymptotic approximation** ($p_{\text{asymp}}$), noting continuity corrections.
   - Note the combinatorial lower bound for $N=30$: $p_{\text{min, exact}} = 2 / 2^{30} \approx 1.8626 \times 10^{-9}$.
4. **Effect Magnitude & Robustness Suite:**
   - **Paired Mean Delta ($\bar{D}$)** and **Paired Median Delta**.
   - **95% Bootstrap Confidence Interval:** Computed via 10,000 seed-level paired bootstrap resamples (resampling intact seed pairs together).
   - **Seed-Level Cohen's $d_z$:** Defined strictly as $d_z = \frac{\bar{D}}{s_D}$, where $s_D$ is the sample standard deviation of the paired differences.
   - **Seed Win Rate:** Fraction of evaluation seeds where $D_s > 0$.
   - **Two-Sided Sign Test:** Direction-only binomial test ($p = 2 \times 0.5^N$ for unanimous wins) as an assumption-free robustness check.

---

## 3. Disqualification & Corrigendum Policy

Any claim derived from unmodeled pseudoreplication, non-independent pooling, or transcription copy-paste errors must be formally retracted and expunged from executive summaries, replacing it with the certified seed-level inference.
