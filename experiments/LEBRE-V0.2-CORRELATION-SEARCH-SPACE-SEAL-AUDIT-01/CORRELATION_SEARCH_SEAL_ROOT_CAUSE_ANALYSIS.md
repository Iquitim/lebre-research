# Root Cause Analysis: Forensics of Forensic Discrepancies
## Stage: LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01
## Target Parent: LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01

---

## 1. Executive Summary

This Root Cause Analysis (RCA) diagnoses the structural, procedural, and cognitive factors that caused multiple discrepancies, unsupported mechanistic claims, and governance misclassifications in `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`.

Although the core algorithmic artifact ($M_1^*$, the compact correlation frontier) achieved genuine tracking improvements over $R_1$ (mean NMSE delta $-0.01142$, $19/30$ seed wins) and reduced static accumulator memory by $41.8\%$, the parent report made several assertions that were directly contradicted by the raw data or ungrounded in empirical evidence.

The audit identifies **five primary root causes**, establishes the failure mode of each, and provides concrete procedural safeguards.

---

## 2. Forensic Breakdown by Root Cause

### Root Cause 1: Conflation of Margin Non-Inferiority Test with Test Against Zero
- **Location:** Section 5 ("Confirmatory Statistical Evaluation") of parent report.
- **Reported Claim:**
  $$\Delta_{\text{NMSE}}(M_1^* - R_1) = -0.011417, \quad t(29) = -4.57, \quad p = 4.20 \times 10^{-5}$$
  Presented as a two-sided paired $t$-test establishing statistically significant superiority over zero.
- **Empirical Ground Truth:**
  Running a one-sample $t$-test of the seed-level paired differences $\Delta_s = \text{NMSE}(M_1^*, s) - \text{NMSE}(R_1, s)$ against $H_0: \mu_{\Delta} = 0$ yields:
  $$\text{Mean } \Delta = -0.011417, \quad s_{\Delta} = 0.025679, \quad \text{SE} = 0.004688, \quad t(29) = -2.4352, \quad p = 0.02126$$
  The effect size is Cohen's $d_z = -0.4446$, with $19$ seed wins and $11$ seed losses ($63.3\%$ win rate).
- **Forensic Reconstruction:**
  In the parent repository's analysis scratch directory (`experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/scratch/postprocess_confirmatory_results.py`), the author conducted two separate hypothesis tests:
  ```python
  # Test 1: Superiority vs 0
  res_zero = stats.ttest_1samp(deltas, 0.0)
  # t = -2.4352, p = 0.02126

  # Test 2: Non-inferiority within margin epsilon = 0.0100
  res_margin = stats.ttest_1samp(deltas, 0.0100)
  # t = -4.56822, p = 4.2007e-05
  ```
  When copying the results into the markdown report, the author transcribed the $t$-statistic and $p$-value from `res_margin` instead of `res_zero`, but labeled the test as testing whether $M_1^*$ was superior to $R_1$ ($\Delta < 0$).
- **Impact:**
  The parent report presented an artificially inflated statistical confidence ($p < 0.0001$ vs true $p = 0.0213$) and exaggerated the robustness of the result across random seeds.
- **Root Failure Mode:** *Transcription ambiguity between intermediate script outputs and final report text without automated assert-linked verification.*

---

### Root Cause 2: Narrative Extrapolation of Design Intent (The "Epistemic Filter" Fabrication)
- **Location:** Section 6 ("Mechanistic Analysis") and Section 9 ("Synthesis").
- **Reported Claim:**
  The compact frontier was asserted to have reduced candidate births by $\approx 57\%$ ($90.22 \to 38.8$) and eliminated $\approx 70\%$ of failed probation waste ($1.71 \to 0.51\text{ FP/step}$), functioning as an "epistemic noise filter" that suppresses spurious candidates.
- **Empirical Ground Truth:**
  Auditing `CORRELATION_SEARCH_FINAL_RESULTS.csv` and `CORRELATION_SEARCH_DEV_RESULTS.csv` across all $1,260$ runs reveals:
  - Candidate Births in Confirmatory: $R_1 = 90.22 \pm 2.05$, $M_1^* = 92.97 \pm 2.06$ ($+3.05\%$ increase, not $-57\%$).
  - Failed Probation Compute: $R_1 = 1.711\text{ FP/step}$, $M_1^* = 1.769\text{ FP/step}$ ($+3.39\%$ increase, not $-70\%$).
  - Candidate Births in Phase 2 DEV: $R_1 = 89.94$, $M_1^* = 94.03$.
- **Forensic Reconstruction:**
  The hypothesis that "restricting search to top-variance coordinates will naturally choke off spurious candidate generation" was conceived during algorithm design. When authoring the report, the author wrote this theoretical explanation into the text as an established empirical fact without actually querying the `candidate_births` or `failed_probation_compute` columns of the resulting CSV.
  The actual mechanism driving $M_1^*$'s superior NMSE was:
  - $M_1^*$ advanced by $B=4$ coordinates every $K=2$ steps, completing a full sweep of $160$ coordinates in $80\text{ steps}$.
  - $R_1$ advanced by $B=2$ coordinates every $K=2$ steps, requiring $160\text{ steps}$ per sweep.
  - $M_1^*$ traversed the search space twice as fast, resulting in significantly higher recall of true non-zero delay promotions ($76.31\%$ vs $66.55\%$), at the cost of slightly higher active candidate tracking compute ($111.01$ vs $106.74\text{ FP/step}$).
- **Impact:**
  Downstream researchers would have pursued optimization of a non-existent birth suppression mechanism rather than addressing the actual operational dynamics (sweep speed vs probation overhead).
- **Root Failure Mode:** *Confirmation bias and theoretical storytelling substituted for direct empirical metric extraction.*

---

### Root Cause 3: Component Rounding Sum vs Direct Empirical Array Mean
- **Location:** Section 7 ("Resource Accounting") and Executive Summary.
- **Reported Claim:**
  $M_1^*$ online compute is $110.82\text{ FP/step}$.
- **Empirical Ground Truth:**
  The true arithmetic mean of column `total_fp_mean` for model $M_1^*$ across all $420$ confirmatory runs in `CORRELATION_SEARCH_FINAL_RESULTS.csv` is:
  $$\mu_{\text{total\_fp}} = 111.013591\text{ FP/step}$$
- **Forensic Reconstruction:**
  The author built the markdown resource breakdown table by adding pre-rounded analytical module budgets:
  - Fixed Baseline: $88.45$
  - Probing (B=4, K=2): $12.00$
  - Maintenance & Aging: $5.37$
  - Active Probation Tracking: $5.00$
  - Sum: $88.45 + 12.00 + 5.37 + 5.00 = 110.82\text{ FP/step}$
  This theoretical sum ($110.82$) was then reported throughout the text as the empirical measurement, despite the instrumented runs logging an empirical average of $111.01\text{ FP/step}$.
- **Impact:**
  While the discrepancy is minor ($+0.19\text{ FP/step}$, $0.17\%$), relying on an analytical sum obscured the exact empirical comparison against $R_1$ ($106.74\text{ FP/step}$), concealing that $M_1^*$ incurs a $+4.28\text{ FP/step}$ penalty and therefore does not strictly Pareto-dominate $R_1$.
- **Root Failure Mode:** *Manual table-level synthetic arithmetic substituted for direct summary statistics of instrumented logs.*

---

### Root Cause 4: Specification vs Implementation Desynchronization (Queue Periodicity)
- **Location:** Section 4 ("Search Space Geometry") and Section 6.
- **Reported Claim:**
  The compact frontier queue guarantees coordinate revisit latency within $272\text{ stream steps}$.
- **Empirical Ground Truth & Code Reality:**
  In the executable code (`src/lebre/search/compact_frontier.py`), the queue is implemented as a single contiguous circular array:
  $$N_{\text{searchable}} = 5 \times 32 = 160\text{ delay coordinates}$$
  At each probe interval of $K_{\text{probe}} = 2$ steps, a block of $B = 4$ coordinates is evaluated, advancing pointer $p \leftarrow (p + B) \pmod{160}$.
  The exact deterministic revisit period for every coordinate is:
  $$T_{\text{revisit}} = \frac{160}{4} \times 2 = 80\text{ stream steps}$$
- **Forensic Reconstruction:**
  The figure $272\text{ steps}$ originated from an earlier design document draft proposing a dual-rate partitioned queue:
  - Track Queue ($H_{\text{track}} = 24$ slots, probed every $4$ steps)
  - Explore Queue ($136$ slots, probed $1$ slot every $2$ steps $\implies 136 \times 2 = 272\text{ steps}$)
  This partitioned architecture was discarded during implementation in favor of a uniform circular pointer, but the draft document specification ($272\text{ steps}$) was never updated in the parent report narrative.
- **Impact:**
  Theoretical latency was overstated by a factor of $3.4\times$ ($272$ vs $80$). The rapid revisit period ($80$ steps) was precisely why $M_1^*$ adapted faster than $R_1$ to switching non-stationarities.
- **Root Failure Mode:** *Failure to synchronize report documentation with architectural simplifications made during code implementation.*

---

### Root Cause 5: Premature Declaration of "Supported" Despite Gate Failures
- **Location:** Section 8 ("Preregistration Adjudication") and Section 10 ("Decision").
- **Reported Claim:**
  `CORRELATION_SEARCH_SPACE_COMPACTION_SUPPORTED = YES`
  `GLOBAL_SEARCH_COMPACTION_VALIDATION = PASSED`
- **Empirical Ground Truth & Protocol Reality:**
  Under the preregistered Protocol G-Gates:
  - **Gate G1 (Statistical Superiority over R1 with $p < 0.01$):** FAILED (true $p = 0.02126 > 0.0100$).
  - **Gate G2 (Strict Pareto Dominance over R1):** FAILED ($M_1^*$ consumes $111.01$ vs $106.74\text{ FP/step}$, $+4.00\%$ compute increase).
  - **Gate G3 (Candidate Churn Reduction $\ge 30\%$):** FAILED (births $+3.05\%$, probation waste $+3.39\%$).
  - **Gate G4 (Static Memory Reduction $\ge 40\%$):** PASSED ($330\text{B} \to 192\text{B}$, $-41.8\%$).
  Since 3 of 4 mandatory confirmatory gates failed, the preregistered governance outcome taxonomy explicitly mandates:
  $$\text{Outcome} = \text{FAILED / MULTIPLE CORRECTABLE ISSUES}$$
- **Forensic Reconstruction:**
  The author justified the "SUPPORTED" verdict by introducing a post-hoc reclassification, arguing that because NMSE improved by $13.2\%$ and memory decreased by $41.8\%$, the compute penalty ($+4.0\%$) and lack of churn reduction were "acceptable engineering tradeoffs." While this may be true pragmatically, overriding preregistered binary pass/fail gates without formal errata or protocol amendment violates scientific governance integrity.
- **Impact:**
  Erosion of preregistration governance, falsely signaling that compact correlation search was a settled, fully validated baseline ready for canonical replacement.
- **Root Failure Mode:** *Post-hoc dilution of preregistered falsification criteria to accommodate partial empirical success.*

---

## 3. Organizational & Procedural Recommendations

To ensure future LEBRE experimental stages do not replicate these failure modes, the following binding protocols are established:

1. **Assert-Linked Report Generation:**
   Scientific markdown reports must not contain hardcoded numerical claims or $p$-values. All statistical tables, test statistics, and compute totals must be generated directly from sealed CSVs via verified Python scripts with explicit regression tests.

2. **Decoupling Intent from Observation:**
   Mechanistic explanations (e.g., "epistemic noise filter", "reduced churn") must have explicit corresponding telemetry columns in the raw data (e.g., `candidate_births`, `failed_probations`). Hypotheses without logged telemetry must be explicitly labeled as *speculative interpretations*, not empirical findings.

3. **Code-to-Doc Parameter Binding:**
   Algorithmic constants mentioned in reports (such as queue revisit periods or memory allocations) must be dynamically derived from the active source code constants (e.g., `SEARCHABLE_COORDINATES / PROBE_BLOCK_SIZE * PROBE_INTERVAL`).

4. **Strict Gate Governance:**
   If any preregistered Gate fails, the stage verdict must be declared `FAILED` or `PARTIALLY_SUPPORTED_WITH_RESERVATIONS`. A stage cannot be declared `PASSED` or `SUPPORTED` via post-hoc narrative reframing.
