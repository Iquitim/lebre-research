# Forensic Seal Audit Final Report
## Stage: LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01
## Target Parent Stage: LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01
## Lead Auditor: Independent Senior Scientific Software & Research Auditor
## Date of Audit: September 2026
## Epistemic Authority: Level 3 (Sealed Forensic Audit & Errata)

---

## Executive Summary

This forensic seal audit evaluated the empirical integrity, statistical validity, resource accounting, mechanistic attribution, and governance compliance of experimental stage `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`.

The parent stage introduced model $M_1^*$ (the Compact Correlation Frontier), designed to replace the dense $5 \times 32$ correlation search tables of baseline models $R_0$ and $R_1$ with a budget-constrained circular frontier buffer.

### Key Forensic Findings:
1. **Raw Data Integrity Certified:** The confirmatory dataset (`CORRELATION_SEARCH_FINAL_RESULTS.csv`) comprises exactly $1,260$ runs ($30\text{ seeds } \times 14\text{ tasks } \times 3\text{ models}$), with zero missing values, zero duplicates, and full cryptographic integrity across all $46$ parent artifacts.
2. **Statistical Lineage Discrepancy Reconciled:** The reported inferential statistic ($t = -4.57, p = 4.20 \times 10^{-5}$) was forensically traced to an unadjusted one-sample test of a non-inferiority margin ($\epsilon = +0.0100$) in an intermediate scratch script, mistakenly transcribed into the parent narrative as a test of superiority over zero. The true paired seed-level test against $H_0: \mu_{\Delta} = 0$ yields:
   $$t(29) = -2.4352, \quad p = 0.02126 \text{ (two-sided)}, \quad p = 0.01063 \text{ (one-sided)}, \quad d_z = -0.4446$$
   $M_1^*$ outperformed $R_1$ on $19$ seeds and underperformed on $11$ seeds ($63.3\%$ win rate).
3. **Compute Value Reconciled:** The reported compute figure ($110.82\text{ FP/step}$) was an analytical sum of rounded component estimates in a markdown table. The exact empirical mean across all $420$ runs of $M_1^*$ is $111.013591\text{ FP/step}$. $M_1^*$ consumes $+4.28\text{ FP/step}$ ($+4.00\%$) more compute than $R_1$ ($106.74\text{ FP/step}$), refuting the claim of strict Pareto dominance.
4. **Mechanistic Churn Claims Retracted:** Claims that candidate births were reduced by $\approx 57\%$ and probation waste by $\approx 70\%$ are completely ungrounded in empirical data. In reality, births increased by $+3.05\%$ ($90.22 \to 92.97$) and probation waste increased by $+3.39\%$ ($1.711 \to 1.769\text{ FP/step}$). The true causal driver of $M_1^*$'s accuracy gain was its $2\times$ faster queue sweep speed ($80\text{ steps}$ vs $160\text{ steps}$ in $R_1$), boosting true delay discovery recall from $66.55\%$ to $76.31\%$.
5. **Geometry & Latency Certified:** The physical buffer contains $165$ cells ($5 \times 33$), but lag 0 is the linear baseline, leaving $160$ searchable delay coordinates ($5 \times 32$). The queue is a uniform circular buffer with a deterministic revisit period of $T_{\text{revisit}} = \frac{160}{4} \times 2 = 80\text{ steps}$, disproving the stale narrative figure of $272\text{ steps}$.
6. **Governance & Gate Adjudication:** Because mandatory Gates G1 ($p < 0.01$), G2 (Pareto dominance), and G3 (churn reduction $\ge 30\%$) failed, the verdict is adjudicated as:
   - `GLOBAL_SEARCH_COMPACTION_VALIDATION = FAILED`
   - `CORRELATION_SEARCH_SPACE_COMPACTION_SUPPORTED = NO`
   - `DENSE_SEARCH_PERMANENTLY_DEPRECATED = NO`
   - `M1_STAR_CANONICAL_BASELINE = NO` (Designated: `PROMISING_EXPERIMENTAL_CANDIDATE`)
   - `OVERALL_STATUS = MULTIPLE_CORRECTABLE_ISSUES`

---

## Section 1: Raw Data Integrity & Cardinality Certification

A complete census of all raw simulation records was conducted across `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/`.

### 1.1 Dataset Cardinality Verification
- **Target File:** `CORRELATION_SEARCH_FINAL_RESULTS.csv`
- **Total Record Count:** Exactly $1,260$ rows (excluding header).
- **Factorial Grid:**
  $$\text{Seeds } (30) \times \text{Tasks } (14) \times \text{Models } (3) = 30 \times 14 \times 3 = 1,260 \text{ rows}$$
  - Seeds: $\{1811, 1812, \dots, 1840\}$ ($30$ unique integers).
  - Tasks: $\{I_1, I_2, \dots, I_{14}\}$ ($14$ tasks covering stationary, non-stationary, sparse, dense, and cointegrated streams).
  - Models: $\{R_0, R_1, M_1^*\}$ ($420$ runs per model).
- **Duplicate Checks:** Zero duplicate `(seed, task, model)` tuples exist.
- **Null / NaN Checks:** Zero missing, NaN, or infinite entries across all $28$ numerical columns.
- **Phase 2 DEV Dataset:** `CORRELATION_SEARCH_DEV_RESULTS.csv` contains exactly $980$ rows ($10\text{ seeds} \times 14\text{ tasks} \times 7\text{ candidate configurations}$), representing $840$ screening runs plus $140$ aligned baseline runs.

### 1.2 Cryptographic Seal
All 46 parent artifacts were hashed using SHA-256 and verified against `PARENT_ARTIFACT_HASHES.txt`. No artifact was modified or corrupted.

---

## Section 2: Statistical Lineage & Discrepancy Reconciliation

### 2.1 The Origin of $t = -4.57, p = 4.20 \times 10^{-5}$
In Section 5 of the parent report, the statistical comparison of $M_1^*$ vs $R_1$ was cited as:
$$\Delta_{\text{NMSE}} = -0.011417, \quad t(29) = -4.57, \quad p = 4.20 \times 10^{-5}$$
The audit investigated `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/scratch/postprocess_confirmatory_results.py` and `PREDICTIVE_NONINFERIORITY.csv` and uncovered the script lines:
```python
deltas_r1 = m1_means - r1_means
# Non-inferiority margin test (+0.0100):
t_margin, p_margin = stats.ttest_1samp(deltas_r1, 0.0100)
# Outputs: t = -4.568218, p_one_sided = 4.2039e-05

# Two-sided paired test against zero:
t_zero, p_zero = stats.ttest_1samp(deltas_r1, 0.0)
# Outputs: t = -2.435228, p_two_sided = 0.021265
```
The author copied the results of `ttest_1samp(deltas_r1, 0.0100)` into the report and incorrectly labeled them as testing whether $M_1^*$ had lower NMSE than $R_1$ ($H_0: \mu_{\Delta} = 0$).

### 2.2 Reconciled Seed-by-Seed Paired Inference
A rigorous, certified seed-level aggregation was executed, computing the mean NMSE for $M_1^*$ and $R_1$ across all 14 tasks for each seed $s \in \{1811..1840\}$:
$$\Delta_s = \overline{\text{NMSE}}(M_1^*, s) - \overline{\text{NMSE}}(R_1, s)$$

The reconciled statistical parameters are:
- **Mean Difference ($\overline{\Delta}$):** $-0.011417$ (parent reported $-0.011417$)
- **Standard Deviation ($s_{\Delta}$):** $0.025679$
- **Standard Error ($\text{SE}_{\Delta}$):** $0.004688$
- **$t$-Statistic ($t(29)$):** $-2.435228$
- **Two-Sided $p$-Value:** $p = 0.021265$
- **One-Sided $p$-Value:** $p = 0.010632$
- **Cohen's $d_z$ Effect Size:**
  $$d_z = \frac{\overline{\Delta}}{s_{\Delta}} = \frac{-0.011417}{0.025679} = -0.44461 \quad (\text{Medium effect size})$$
- **95% Confidence Interval for $\mu_{\Delta}$:** $[-0.021006, -0.001828]$
- **Seed-Level Win/Loss Distribution:**
  - $M_1^* < R_1$ (Wins): $19\text{ seeds } (63.33\%)$
  - $M_1^* > R_1$ (Losses): $11\text{ seeds } (36.67\%)$

### 2.3 Evaluation Against Gate G1
Preregistered Gate G1 required:
$$\Delta_{\text{NMSE}}(M_1^* - R_1) < 0 \quad \text{with } p < 0.0100$$
Because the two-sided $p$-value is $0.02126$ (and the one-sided $p$-value is $0.01063 > 0.0100$), **Gate G1 FAILED**.

---

## Section 3: Computational Cost Decomposition & Reconciled Figures

### 3.1 Reconciliation of the $110.82$ vs $111.01$ Compute Value
- **Parent Reported Figure:** $110.82\text{ FP/step}$
- **True Empirical Average:** $111.013591\text{ FP/step}$
- **Lineage Analysis:**
  The parent report constructed an analytical budget table by summing rounded module estimates:
  $$\text{Baseline } (88.45) + \text{Probing } (12.00) + \text{Frontier } (5.37) + \text{Probation } (5.00) = 110.82\text{ FP/step}$$
  The direct arithmetic mean of `total_fp_mean` from the raw instrumented logs across all 420 runs is $111.013591\text{ FP/step}$. The delta ($+0.19\text{ FP/step}$) stems from dynamic variation in active probation candidate durations across tasks.

### 3.2 Confirmatory Cohort Compute Comparison
Across the 420 confirmatory runs per model:

| Model Cohort | Mean Total FP/step | Std Dev | Min | Max | Delta vs R0 | Delta vs R1 |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **$R_0$ (Static Baseline)** | $88.450000$ (static) / $169.46$ (active) | - | - | - | $0.00$ | - |
| **$R_1$ (Dense Correlation)** | $106.735848$ | $0.8112$ | $104.92$ | $108.66$ | - | $0.00$ |
| **$M_1^*$ (Compact Frontier)** | $111.013591$ | $1.0245$ | $108.74$ | $113.82$ | - | **$+4.28$** |

### 3.3 Strict Pareto Dominance Refutation
$M_1^*$ consumes $111.01\text{ FP/step}$, which is $+4.28\text{ FP/step}$ ($+4.01\%$) greater than $R_1$.
Therefore:
- $M_1^*$ is superior to $R_1$ in accuracy ($-0.0114$ NMSE).
- $M_1^*$ is superior to $R_1$ in static memory ($-41.8\%$ RAM).
- $M_1^*$ is **inferior** to $R_1$ in operational compute ($+4.01\%$ FP/step).
Because $M_1^*$ is not superior or equal across all objectives, **Claim C26 (Pareto Dominance) and Gate G2 (Strict Pareto Dominance) are REFUTED and FAILED**.

---

## Section 4: Churn & Search Mechanism Re-evaluation

### 4.1 Retraction of the "Epistemic Filter" and Churn Reduction Claims
The parent report asserted that candidate births were reduced by $\approx 57\%$ and failed probation compute by $\approx 70\%$, attributing $M_1^*$'s success to an "epistemic noise filter" that suppresses spurious candidates.

The audit extracted the exact birth and probation metrics across all $1,260$ confirmatory runs:

| Model | Candidate Births (Mean $\pm$ Std) | Failed Probation Flushes | Failed Probation FP/step | Promotion Recall |
|:---|:---:|:---:|:---:|:---:|
| **$R_1$** | $90.22 \pm 2.05$ | $68.44 \pm 2.11$ | $1.711 \pm 0.053$ | $66.55\%$ |
| **$M_1^*$** | $92.97 \pm 2.06$ | $70.78 \pm 2.14$ | $1.769 \pm 0.054$ | $76.31\%$ |
| **Delta ($M_1^* - R_1$)** | **$+2.75$ ($+3.05\%$)** | **$+2.34$ ($+3.42\%$)** | **$+0.058$ ($+3.39\%$)** | **$+9.76\%$** |

In Phase 2 DEV, candidate births were $89.94$ ($R_1$) vs $94.03$ ($M_1^*$).
At no point in DEV or Confirmatory did candidate births drop to $38.8$ or probation waste to $0.51$.

### 4.2 Causal Attribution of $M_1^*$'s Performance Gain
The true causal mechanism explaining why $M_1^*$ achieved lower NMSE is:
1. **Sweep Traversal Speed:** $M_1^*$ evaluated $B=4$ coordinates every $K=2$ steps ($2.0\text{ coords/step}$), traversing all $160$ coordinates in $80\text{ steps}$. $R_1$ evaluated $B=2$ coordinates every $K=2$ steps ($1.0\text{ coords/step}$), taking $160\text{ steps}$.
2. **Promotion Recall:** In switching and non-stationary tasks ($I_2, I_5, I_{11}, I_{12}$), $M_1^*$ discovered active non-zero delay shifts in half the time, raising promotion recall from $66.55\%$ to $76.31\%$.
3. **Compute Overhead:** Maintaining active probation tracking for more rapidly detected candidates slightly increased active compute ($+4.28\text{ FP/step}$).

The "epistemic noise filter" claim was pure narrative fabrication. The actual mechanism was rapid search traversal.

---

## Section 5: Memory Layout & Queue Geometry Formal Proof

### 5.1 Disambiguation of Coordinate Cardinality: 165 vs 160
- The multi-rate delay line stores $5$ input channels over $33$ time taps ($k \in [0, 32]$), yielding $5 \times 33 = 165\text{ physical buffer cells}$.
- Lag $k = 0$ represents the synchronous linear baseline filter ($5$ taps), which is permanently resident in the primary linear filter and never probed by the correlation search engine.
- The searchable delay hypothesis space consists strictly of non-zero lags:
  $$N_{\text{searchable}} = 5 \text{ channels} \times 32 \text{ delay taps } (k \in [1, 32]) = 160\text{ delay coordinates}$$

### 5.2 Static and Dynamic Memory Decomposition
- **Dense Baseline ($R_0 / R_1$):**
  - Accumulator Table: $165\text{ cells} \times 2\text{ bytes (FP16)} = 330\text{ bytes}$.
  - State overhead: $0\text{ bytes}$ queue state.
  - Total Search Memory: $330\text{ bytes}$.
- **Compact Frontier ($M_1^*$):**
  - Frontier Candidate Table: $32\text{ slots} \times 6\text{ bytes } (\text{FP16 val, uint8 ch, uint8 lag, uint16 age}) = 192\text{ bytes}$.
  - State & Queue Overhead: $68\text{ bytes}$ ($1\text{B pointer}, 3\text{B probe config}, 64\text{B channel energy monitors}$).
  - Total Active Search State: $260\text{ bytes}$.
- **Certified Memory Delta:**
  $$\text{Table Memory: } \frac{192 - 330}{330} = -41.82\% \quad (\text{Passed Gate G4})$$
  $$\text{Total State Memory: } \frac{260 - 330}{330} = -21.21\%$$
- **Dense Array Elimination:** Certified that $M_1^*$ allocates exactly zero dense correlation arrays in RAM.

### 5.3 Formal Revisit Period Proof & The 272-Step Discrepancy
In `src/lebre/search/compact_frontier.py`, the probing loop is:
```python
def probe_step(self, t):
    if t % self.K_probe == 0:
        for i in range(self.B):
            coord = (self.pointer + i) % 160
            self._probe_coordinate(coord)
        self.pointer = (self.pointer + self.B) % 160
```
- Total searchable coordinates: $N = 160$.
- Block size per probe: $B = 4$.
- Number of probe events per complete cycle: $\frac{N}{B} = \frac{160}{4} = 40\text{ probe events}$.
- Steps between probe events: $K_{\text{probe}} = 2\text{ stream steps}$.
- Revisit Period:
  $$T_{\text{revisit}} = \frac{N}{B} \times K_{\text{probe}} = 40 \times 2 = 80\text{ stream steps}$$

The parent report's claim of $272\text{ steps}$ originated from an unexecuted specification for a partitioned queue ($136 \text{ explore slots} \times 2 = 272$). The implemented uniform queue operates at $80\text{ steps}$.

---

## Section 6: Gate Evaluation & Preregistered Success Criteria Re-adjudication

The parent experiment preregistered four primary confirmatory gates (G1..G4) and four secondary operational criteria (G5..G8).

| Gate ID | Description | Threshold / Condition | Empirical Result | Audit Adjudication |
|:---|:---|:---|:---:|:---:|
| **G1** | Statistical Superiority vs $R_1$ | $\Delta_{\text{NMSE}} < 0$ and $p < 0.0100$ | $t=-2.435, p=0.02126$ | **FAILED** |
| **G2** | Strict Pareto Dominance vs $R_1$ | $\Delta_{\text{NMSE}} \le 0$, $\Delta_{\text{FP}} \le 0$, $\Delta_{\text{RAM}} < 0$ | $\Delta_{\text{FP}} = +4.28\text{ FP/step}$ | **FAILED** |
| **G3** | Candidate Churn Suppression | Birth reduction $\ge 30\%$ | Births $+3.05\%$ | **FAILED** |
| **G4** | Memory Compaction | Accumulator RAM reduction $\ge 40\%$ | $-41.82\%$ ($330\text{B} \to 192\text{B}$) | **PASSED** |
| **G5** | Fast Non-Stationary Re-locking | Delay identification within $100$ steps | Mean lock latency $82.4$ steps | **PASSED** |
| **G6** | Tracking Stability under Noise | No divergence on noisy streams ($I_3, I_7$) | Zero divergences across 60 runs | **PASSED** |
| **G7** | Memory Safety & Leaks | Zero dynamic allocation leaks | Zero leaks certified | **PASSED** |
| **G8** | Baseline Preservation | $R_0$ non-inferiority maintained | $M_1^*$ beats $R_0$ by $-0.0982$ NMSE | **PASSED** |

### Adjudication Under Preregistered Governance Taxonomy
The preregistered protocol mandates that if any mandatory confirmatory gate G1..G3 fails, the overall experiment outcome cannot be declared successful:
- Preregistered Condition: "All mandatory gates G1..G4 must pass to declare `GLOBAL_SEARCH_COMPACTION_VALIDATION = PASSED`."
- Result: 3 of 4 mandatory gates failed.
- Forensic Verdict:
  $$GLOBAL\_SEARCH\_COMPACTION\_VALIDATION = FAILED$$
  $$CORRELATION\_SEARCH\_SPACE\_COMPACTION\_SUPPORTED = NO$$
  $$AUDIT\_TAXONOMY\_CLASSIFICATION = MULTIPLE\_CORRECTABLE\_ISSUES$$

---

## Section 7: Scope of Theoretical Analogies & Governance

1. **Matching Pursuit Analogy (C16):** The parent report analogized $M_1^*$ to Orthogonal Matching Pursuit (OMP). This is formally classified as an *active-set selection heuristic analogy*, not an algorithmic equivalence. OMP performs orthogonal projection onto a dictionary; $M_1^*$ performs streaming gradient correlation tracking with heuristic threshold promotion.
2. **Kronecker Delta & Coarse-to-Fine Search (C15):** The assertion that Kronecker delta delay profiles are "optimally identified" was contradicted on task $I_4$ (odd lags $[1, 3, 5]$). Subsampled even-lag search suffered odd-lag blindness, requiring fallback to uniform probing.
3. **Compute Floor Claim (C17):** The constant compute floor of $88.45\text{ FP/step}$ is valid only under frozen $M_1$ multirate clocks and an active linear filter size of $5$ taps. It is not an absolute hardware floor.
4. **Dense Search Deprecation Governance (C27):** The declaration that dense correlation search is permanently deprecated is **overruled**. Because $M_1^*$ increases compute by $+4.28\text{ FP/step}$ and failed G1..G3, dense search ($R_0, R_1$) must remain an active reference baseline in the codebase.

---

## Section 8: Forensic Claim-by-Claim Adjudication Matrix

All 34 parent claims were forensically evaluated and certified in `CORRELATION_SEARCH_CLAIM_AUDIT.csv`.

- **Total Claims Audited:** 34
- **Confirmed / Verified:** 16 ($47.1\%$)
- **Qualified / Reconciled:** 9 ($26.5\%$)
- **Refuted / Retracted:** 9 ($26.5\%$)

Key Retractions:
- Claims C5, C6, C7, C13, C14 (Candidate Churn & Epistemic Noise Filter) $\implies$ **REFUTED & RETRACTED**.
- Claim C12 (Compute Savings) $\implies$ **REFUTED & RETRACTED**.
- Claim C26 (Pareto Dominance) $\implies$ **REFUTED & RETRACTED**.
- Claim C27 (Permanent Dense Deprecation) $\implies$ **OVERRULED & RETRACTED**.
- Claim C28 & C29 (Compaction Supported & Canonical Adoption) $\implies$ **OVERRULED & RECLASSIFIED**.

---

## Section 9: Root Cause Summary & Corrective Actions

The five root causes identified in `CORRELATION_SEARCH_SEAL_ROOT_CAUSE_ANALYSIS.md` are:
1. Conflation of margin non-inferiority test ($p = 4.2 \times 10^{-5}$) with test against zero ($p = 0.0213$).
2. Narrative extrapolation of design intent without checking empirical birth/probation counters.
3. Reporting rounded table component sums ($110.82$) instead of empirical mean array logs ($111.01$).
4. Retaining preliminary specification numbers ($272$ steps) instead of actual code reality ($80$ steps).
5. Overriding preregistered gate failures with post-hoc narrative justifications.

### Mandatory Corrective Protocols:
- All future reports must be generated via assert-linked Python scripts directly parsing sealed raw data.
- Speculative interpretations must be quarantined from empirical observations.
- Protocol gate failures must trigger automatic `FAILED` or `PARTIAL` designations.

---

## Section 10: Final Seal Determination & Next Stage Directives

### 10.1 Model Classification
Model $M_1^*$ demonstrates genuine algorithmic merit: it achieves lower NMSE than $R_1$ on $63.3\%$ of seeds and reduces static accumulator memory by $41.8\%$, driven by rapid queue traversal. However, because it incurs a $+4.00\%$ compute penalty and failed G1..G3, it cannot be certified as the canonical baseline.

Model $M_1^*$ is classified as:
$$\mathbf{PROMISING\_EXPERIMENTAL\_CANDIDATE}$$

### 10.2 Next Stage Directives
1. **Next Recommended Stage:** `LEBRE-V0.2-CANDIDATE-PROBATION-COST-01`
   - Target the candidate probation engine, which accounts for the failed churn assumptions and unnecessary active tracking overhead.
   - Investigate adaptive probation thresholds to eliminate the $+4.28\text{ FP/step}$ compute penalty.
2. **Alternative Directive:** `HUMAN_REVIEW_REQUIRED` if architectural redesign of the correlation queue is prioritized.
3. **Reference Invariance:** Dense baselines $R_0$ and $R_1$ must remain intact and runnable in `src/lebre/search/` and `tests/`.

---

## Section 11: Audit Certification Sign-Off

The forensic seal audit `LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01` is hereby **COMPLETE, CERTIFIED, AND SEALED**.
All artifacts, errata, and proofs are archived in `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01/`.
