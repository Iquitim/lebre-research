# LEBRE v0.2 Errata Audit Protocol

**Audit Identifier:** `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Parent Studies:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`, `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Governing Authority:** Independent Skeptical Scientific Auditor  
**Date:** September 2026  
**Status:** Protocol Frozen Prior to Errata Execution  

---

## 1. Audit Scope & Mandate

This protocol governs the narrow errata audit designed to resolve two residual inconsistencies identified in `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`:
1. **Motivating Inconsistency A (H7 / Order Sensitivity):** Incompatibility between reported task NMSE means on $I_4$ ($T_1=0.6889, T_{1R}=0.6882$, diff $\approx 0.0007$) and reported order-bias discrepancy ($0.1654, p = 1.86 \times 10^{-9}$).
2. **Motivating Inconsistency B (I10 / Redundant Dual Allocation):** Provenance and operational definition of the headline claim "$T_2$ redundant dual allocation on $I_{10} = 48.2\% \pm 0.112$".

Under this mandate, no models are re-tuned, no source code in `src/` or `tests/` is altered, no seeds are changed, and no new benchmark simulations are executed. The audit strictly evaluates whether the empirical evidence in sealed raw confirmatory artifacts supports the claims.

---

## 2. Data Authority Hierarchy

When evaluating any numerical value or claim, conflicts are adjudicated using this strict hierarchy:

- **LEVEL 1 (Highest Authority):** Raw confirmatory seed outputs (`LEBRE_V0_2_SEED_RESULTS.csv`, `LEBRE_V0_2_RESOURCE_TRACE.csv`, `LEBRE_V0_2_CONDITIONAL_GAINS.csv`, `LEBRE_V0_2_STRUCTURAL_EVENTS.csv` for seeds `1311`..`1340`).
- **LEVEL 2:** Run manifests and raw structural transition logs.
- **LEVEL 3:** Frozen execution scripts (`scratch/run_v02_integration_experiments.py`, `scratch/bench_v02_integration.py`).
- **LEVEL 4:** Generated statistical tables and computed summary CSVs.
- **LEVEL 5 (Lowest Authority):** Narrative reports (`FINAL_REPORT.md`, `STATISTICAL_REPORT.md`, `INTEGRATION_DECISION.md`).

**Governing Rule:** Level 1 controls absolutely. When Level 5 contradicts Level 1, Level 5 is classified as an erratum unless a transparent, documented transformation fully explains the discrepancy.

---

## 3. Confirmatory Dataset Specification

The confirmatory evaluation suite is strictly bounded to:
- **Seeds:** Exactly $N=30$ paired independent runs ($s \in \{1311, 1312, \dots, 1340\}$).
- **Tasks:** All 14 benchmark tasks ($I_1$ through $I_{14}$).
- **Topologies:** $T_1$ (Ordered Cascade), $T_{1R}$ (Reversed Cascade), $T_2$ (Symmetric Competition), $T_3$ (Resource-Aware Conditional Arbitration), and $O_{\text{ALL}}$ (Unarbitrated Control).
- **Quarantine Assertion:** The developmental seed $1301$ (and any seed $s < 1311$) must never enter confirmatory recomputations. All errata scripts must enforce:
  ```python
  assert (df["seed"] >= 1311).all() and (df["seed"] <= 1340).all()
  assert (df["seed"] != 1301).all()
  ```

---

## 4. Operational Protocols for Disputed Items

### 4.1 Protocol for Hypothesis 7 (Cascade Order Sensitivity)
1. **Raw Extraction:** For each task $I_1$..$I_{14}$ and each seed $s \in \{1311..1340\}$, extract paired vectors:
   $$D(s) = \text{NMSE}_{T1}(s) - \text{NMSE}_{T1R}(s)$$
2. **Task-Level Metrics:** For each task, compute:
   - $\text{Mean}(T_1)$ and $\text{Mean}(T_{1R})$;
   - Difference of Means: $\Delta_{\text{means}} = |\text{Mean}(T_1) - \text{Mean}(T_{1R})|$;
   - Mean Paired Difference: $\bar{D} = \frac{1}{N}\sum_{s=1}^N (T_1(s) - T_{1R}(s))$;
   - Median Paired Difference;
   - Mean Absolute Paired Difference: $\overline{|D|} = \frac{1}{N}\sum_{s=1}^N |T_1(s) - T_{1R}(s)|$;
   - Median Absolute Paired Difference;
   - 10,000-resample bootstrap 95% confidence interval of $\bar{D}$;
   - Paired effect size: Cohen's $d_z = \bar{D} / s_D$;
   - Seed win rates: $W_{T1} = \frac{1}{N}\sum \mathbb{I}(T_1 < T_{1R})$, $W_{T1R} = \frac{1}{N}\sum \mathbb{I}(T_{1R} < T_1)$.
3. **Statistical Testing:** Paired two-sided Wilcoxon signed-rank test on $D(s)$ for each task, declaring effective $N$, statistic $W$, zero handling (`wilcox`), and exact/asymptotic p-value.
4. **Lineage Tracing of 0.1654:** Trace the exact origin of 0.1654 across all artifacts to determine whether it is a confirmatory statistic from another task (e.g., $I_8$), a DEV seed artifact, or a narrative paste error.
5. **Multiplicity Policy:** Evaluate whether the reported p-value ($p < 10^{-6}$) represented a pre-specified single-task confirmatory test or an unadjusted post-hoc test on the task exhibiting the maximum sample discrepancy. Report both raw p-values and Holm-Bonferroni adjusted p-values across the 14-task family.

### 4.2 Protocol for Task $I_{10}$ Redundant Allocation & 48.2% Lineage
1. **Metric Standardization:** Formulate `I10_METRIC_DICTIONARY.md` defining:
   - `frac_both`: Fraction of steady-state evaluation steps ($t \ge 1000$) where both discrete lags and recurrent unit are simultaneously active.
   - `redundant_dual_rate`: Fraction of steps where both modules are active *and* conditional gains satisfy redundancy ($G_{D|B+R} \le \theta_{\text{tol}}$ and $G_{R|B+D} \le \theta_{\text{tol}}$).
2. **Reconstruction of 48.2%:** Systematically search all columns, transformations, and developmental runs to locate the exact provenance of $48.2\% \pm 0.112$. If no valid executable formula links 48.2% to confirmatory dual allocation on $I_{10}$, formally classify the claim as unverified/erroneous.
3. **True Confirmatory Audit:** Compute per-seed and pooled values of `frac_both` and `redundant_dual_rate` for $T_2, T_3, O_{\text{ALL}}$ on $I_{10}$.
4. **Conditional Gain Cross-Check:** Recompute empirical distributions of $G_{D|B}, G_{R|B}, G_{D|B+R}, G_{R|B+D}$ on $I_{10}$ to verify whether simultaneous occupancy in $T_2$ is structurally redundant or conditionally complementary.
5. **Double Payment & Compute Waste Recomputation:** Recompute the actual live FLOP difference between $T_2$ and $T_3$ on $I_{10}$ alongside the predictive NMSE difference.

### 4.3 Protocol for $T_3$ Internal Order Invariance
1. **Separation from Cascade Sensitivity:** Audit the claim of $T_3$ internal symmetry independently of whether $T_1$ and $T_{1R}$ differ.
2. **Deterministic Microtest:** On frozen simulation snapshots across 4 diagnostic tasks ($I_1, I_3, I_6, I_9$), evaluate candidate ordering $D \to R$ versus $R \to D$ holding all inputs, weights, and tie-breakers bitwise identical. Compare counterfactual losses, conditional gains, and arbitration decisions.

---

## 5. Error Classification Taxonomy

Every identified discrepancy in this errata audit must be categorized using one or more of these standard error classes:

1. `REPORT_COPY_FORWARD_ERROR`: A value from an exploratory, developmental, or adjacent task was copied forward into a narrative table without updating to the confirmatory dataset.
2. `STATISTICAL_LINEAGE_ERROR`: A test statistic or p-value was evaluated on one quantity (or task) but attributed to another.
3. `METRIC_DEFINITION_ERROR`: A metric was named or interpreted in narrative text in a manner that does not match its underlying mathematical implementation.
4. `DENOMINATOR_ERROR`: Ambiguity or error in the evaluation window or reference population (e.g., all steps vs. steady-state steps vs. active steps).
5. `AGGREGATION_ERROR`: Incompatible aggregation (e.g., difference of means vs. mean of paired differences; pooled rate vs. mean of per-seed rates).
6. `POST_SELECTION_INFERENCE_ERROR`: Attaching an unadjusted confirmatory hypothesis test to a post-hoc selected sample maximum without multiplicity control.
7. `TERMINOLOGY_OVERSTATEMENT`: Exaggerating the generality of an empirical finding beyond what the data support.
8. `NO_ERROR`: The original claim is reproduced bitwise and conforms strictly to protocol.

---

## 6. Errata Seal Gates

This errata audit passes and seals only if all 10 gates are satisfied:
1. Complete provenance of the value `0.1654` is established.
2. Arithmetic on Task $I_4$ is completely resolved and verified.
3. Every H7 Wilcoxon test is reproduced from paired seed-level observations.
4. Multiplicity and post-selection adjustments are transparently documented.
5. $T_3$ internal evaluation order invariance is empirically verified via deterministic microtest.
6. The lineage of `48.2%` is either reproduced with an explicit formula or formally withdrawn and replaced with verified confirmatory numbers.
7. Dual occupancy (`frac_both`) is rigorously distinguished from redundant dual occupancy (`redundant_dual_rate`).
8. All corrected claims, tables, and figures are generated automatically by `generate_errata_outputs.py`.
9. Zero unexplained DEV Seed 1301 contamination remains in the audit record.
10. The candidate selection of $T_3$ is re-evaluated using **only surviving evidence**.
