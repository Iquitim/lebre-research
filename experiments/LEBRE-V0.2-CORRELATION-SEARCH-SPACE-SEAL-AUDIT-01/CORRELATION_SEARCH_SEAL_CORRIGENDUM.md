# Official Corrigendum & Forensic Errata Notice
## Stage: LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01
## Target Document: experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/CORRELATION_SEARCH_SPACE_COMPACTION_FINAL_REPORT.md
## Authority Level: Level 3 (Sealed Forensic Corrigendum)

---

## 1. Notice of Errata

An independent forensic audit conducted under stage `LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01` identified multiple empirical discrepancies, statistical transcription errors, ungrounded narrative extrapolations, and governance non-compliances in the parent report `CORRELATION_SEARCH_SPACE_COMPACTION_FINAL_REPORT.md`.

In accordance with LEBRE Epistemic Governance Rules, this document issues formal, binding corrections and retractions. The original parent artifact remains preserved and sealed for evidentiary auditability (`experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/`), but its claims are formally superseded by the corrections specified herein.

---

## 2. Summary Table of Formal Errata

| Item | Original Parent Claim | Corrected Ground Truth | Impact & Adjudication |
|:---|:---|:---|:---|
| **Erratum 1** | $t(29) = -4.57, p = 4.20 \times 10^{-5}$ vs $R_1$ | $t(29) = -2.4352, p = 0.02126$ ($d_z = -0.445$) | Corrected. Margin test conflation retracted. |
| **Erratum 2** | $M_1^*$ compute = $110.82\text{ FP/step}$ | $M_1^*$ empirical mean = $111.013591\text{ FP/step}$ | Reconciled ($+0.19$ delta from rounded table sum). |
| **Erratum 3** | Pareto dominance over $R_1$ (lower compute) | $M_1^*$ increases compute by $+4.28\text{ FP/step}$ over $R_1$ | Pareto dominance claim refuted. |
| **Erratum 4** | Candidate births reduced by $\approx 57\%$ | Births increased $+3.05\%$ ($90.22 \to 92.97$) | Retracted. Mechanism ungrounded in data. |
| **Erratum 5** | Failed probation waste reduced by $\approx 70\%$ | Waste increased $+3.39\%$ ($1.711 \to 1.769$) | Retracted. Mechanism ungrounded in data. |
| **Erratum 6** | "Epistemic noise filter" suppression | Causal mechanism is $2\times$ faster sweep ($80$ steps) | Narrative reclassified to rapid sweep discovery. |
| **Erratum 7** | Queue revisit latency $= 272\text{ steps}$ | Exact deterministic revisit period $= 80\text{ steps}$ | Stale specification value corrected to code reality. |
| **Erratum 8** | Searchable space $= 165\text{ coordinates}$ | $160\text{ delay coordinates}$ ($165$ physical buffer cells) | Geometry clarified: Lag 0 is linear baseline. |
| **Erratum 9** | Dense search permanently deprecated | Dense search remains active canonical reference | Governance corrected: `DENSE_DEPRECATED = NO`. |
| **Erratum 10** | Compaction Validation = PASSED / SUPPORTED | Compaction Validation = FAILED / NOT SUPPORTED | Reclassified under preregistered gates (G1..G4). |

---

## 3. Detailed Forensic Errata

### Erratum 1: Statistical Inferential Test of $M_1^*$ vs $R_1$
- **Original Statement:**
  > "Across the 30 confirmatory seeds, $M_1^*$ achieved a statistically significant NMSE reduction over $R_1$ ($\Delta_{\text{NMSE}} = -0.011417, t(29) = -4.57, p = 4.20 \times 10^{-5}$), demonstrating decisive superiority."
- **Correction:**
  The values $t = -4.56822$ and $p = 4.2007 \times 10^{-5}$ correspond to a one-sample test of the non-inferiority margin $+0.0100$ (`ttest_1samp(deltas, 0.0100)`), not a test against zero.
  The true paired seed-level test against $H_0: \mu_{\Delta} = 0$ is:
  $$\Delta_{\text{NMSE}} = -0.011417, \quad s_{\Delta} = 0.025679, \quad \text{SE} = 0.004688, \quad t(29) = -2.4352, \quad p = 0.02126$$
  The one-sided $p$-value is $p = 0.01063$. The effect size is Cohen's $d_z = -0.4446$ (medium effect). $M_1^*$ achieved a lower NMSE on 19 seeds and a higher NMSE on 11 seeds ($63.3\%$ win rate).
- **Status:** **CORRECTED AND RE-ADJUDICATED**.

---

### Erratum 2: Online Operational Compute of Model $M_1^*$
- **Original Statement:**
  > "Total online operational compute for $M_1^*$ is certified at $110.82\text{ FP/step}$."
- **Correction:**
  $110.82$ was derived by summing rounded theoretical component budgets in the markdown summary table ($88.45 + 12.00 + 5.37 + 5.00$). The direct arithmetic mean of `total_fp_mean` in `CORRELATION_SEARCH_FINAL_RESULTS.csv` across all 420 runs of $M_1^*$ is:
  $$\text{Mean Total Compute} = 111.013591\text{ FP/step} \quad (\approx 111.01\text{ FP/step})$$
  The empirical compute breakdown across cohorts is:
  - Baseline $R_0$: $88.45\text{ FP/step}$
  - Baseline $R_1$: $106.74\text{ FP/step}$
  - Compact Frontier $M_1^*$: $111.01\text{ FP/step}$
- **Status:** **RECONCILED**.

---

### Erratum 3: Strict Pareto Dominance Claim
- **Original Statement:**
  > "$M_1^*$ Pareto-dominates $R_1$, offering superior accuracy, reduced memory, and lower computational cost."
- **Correction:**
  $M_1^*$ consumes $111.01\text{ FP/step}$ compared to $R_1$'s $106.74\text{ FP/step}$. $M_1^*$ incurs a $+4.28\text{ FP/step}$ ($+4.00\%$) compute increase over $R_1$. While $M_1^*$ improves NMSE ($-0.0114$) and static accumulator RAM ($-41.8\%$), it does not dominate on compute. It represents an engineering tradeoff, not strict Pareto dominance.
- **Status:** **REFUTED AND RETRACTED**.

---

### Erratum 4 & 5: Candidate Churn and Failed Probation Reduction Claims
- **Original Statements:**
  > "Candidate births dropped by $\approx 57\%$ ($90.22 \to 38.8$), and failed probation compute was reduced by $\approx 70\%$ ($1.71 \to 0.51\text{ FP/step}$)."
  > "The compact frontier acts as an epistemic noise filter, suppressing spurious candidates before probation."
- **Correction:**
  Both statements are completely ungrounded in the empirical data and are formally retracted. The raw telemetry across all 420 runs per model shows:
  - Candidate Births: $R_1 = 90.22 \pm 2.05$ vs $M_1^* = 92.97 \pm 2.06$ ($+3.05\%$ increase).
  - Failed Probation Compute: $R_1 = 1.711\text{ FP/step}$ vs $M_1^* = 1.769\text{ FP/step}$ ($+3.39\%$ increase).
  The mechanism driving $M_1^*$'s superior NMSE is not candidate birth suppression, but rather faster queue sweep dynamics ($T_{\text{revisit}} = 80\text{ steps}$ vs $160\text{ steps}$ in $R_1$), which increased true non-zero delay promotion recall from $66.55\%$ to $76.31\%$.
- **Status:** **FORMALLY RETRACTED**.

---

### Erratum 6: Frontier Queue Revisit Latency
- **Original Statement:**
  > "The frontier queue guarantees that all coordinates are revisited within at most $272\text{ stream steps}$."
- **Correction:**
  The figure $272\text{ steps}$ was an unexecuted draft specification for a partitioned queue ($136 \times 2$). The implemented code in `src/lebre/search/compact_frontier.py` operates as a uniform circular buffer over $160$ searchable delay coordinates with probe block size $B = 4$ and probe interval $K_{\text{probe}} = 2$.
  The exact deterministic revisit latency is:
  $$T_{\text{revisit}} = \frac{160}{4} \times 2 = 80\text{ stream steps}$$
- **Status:** **CORRECTED**.

---

### Erratum 7: Search Space Geometry Disambiguation
- **Original Statement:**
  > "The search space consists of $165$ delay coordinates across 5 channels."
- **Correction:**
  The physical multi-rate delay buffer contains $5 \times 33 = 165$ cells ($k \in 0..32$). However, lag $k = 0$ corresponds to the synchronous linear baseline filter ($5$ taps) and is excluded from correlation probing.
  The searchable delay coordinate space consists of:
  $$N_{\text{searchable}} = 5 \times 32 = 160\text{ coordinates}$$
  The dense accumulator table in $R_0/R_1$ allocates $165 \times 2\text{B} = 330\text{ bytes}$ of FP16 memory. The compact frontier allocates 32 active candidate tracking slots at $6\text{ bytes}$ each ($192\text{ bytes}$), plus 68 bytes of queue/energy overhead ($260\text{ bytes}$ total state).
- **Status:** **CLARIFIED AND RECONCILED**.

---

### Erratum 8: Dense Search Deprecation Status
- **Original Statement:**
  > "`DENSE_SEARCH_PERMANENTLY_DEPRECATED = YES`. Dense correlation tables $R_0$ and $R_1$ are obsolete and retired from future stages."
- **Correction:**
  Because $M_1^*$ consumes more compute than $R_1$ ($111.01$ vs $106.74$) and failed 3 of 4 preregistered gates, dense search cannot be retired. Retaining dense search is essential for benchmark fidelity, failure isolation, and algorithmic comparison.
  $$DENSE\_SEARCH\_PERMANENTLY\_DEPRECATED = NO$$
- **Status:** **OVERRULED AND RETRACTED**.

---

### Erratum 9: Overall Compaction Verdict
- **Original Statement:**
  > "`CORRELATION_SEARCH_SPACE_COMPACTION_SUPPORTED = YES`"
  > "`GLOBAL_SEARCH_COMPACTION_VALIDATION = PASSED`"
- **Correction:**
  Under the preregistered Protocol G-Gates, Gate G1 ($p < 0.01$), Gate G2 (Pareto dominance), and Gate G3 (churn reduction $\ge 30\%$) failed.
  Under the preregistered 5-way Outcome Taxonomy, when mandatory criteria fail, the verdict must be recorded as:
  $$CORRELATION\_SEARCH\_SPACE\_COMPACTION\_SUPPORTED = NO$$
  $$GLOBAL\_SEARCH\_COMPACTION\_VALIDATION = FAILED$$
  $$OVERALL\_STATUS = MULTIPLE\_CORRECTABLE\_ISSUES$$
  Model $M_1^*$ is designated a **PROMISING EXPERIMENTAL CANDIDATE** rather than a certified canonical baseline.
- **Status:** **OVERRULED AND FORMALLY CORRECTED**.

---

## 4. Epistemic Governance Sign-Off

This Corrigendum is sealed under stage `LEBRE-V0.2-CORRELATION-SEARCH-SEAL-AUDIT-01`. All subsequent stages (`LEBRE-V0.2-CANDIDATE-PROBATION-COST-01` onward) must reference the reconciled values and findings certified herein.
