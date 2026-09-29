# BENCH-01A-R: ELEC2 Canonical Task Audit, Provenance & Relabeling Specification

**Document ID:** BENCH-01A-R-ELEC2  
**Auditor:** Benchmark Methodology Auditor & Data Provenance Reviewer  
**Date:** September 19, 2026  
**Status:** AUDIT COMPLETE — TASK RELABELED & QUALIFIED  
**Governing Standard:** Sections 3–12, 59 of Protocol BENCH-01A-R  

---

## 1. Executive Summary & Verification Mandate

In the BENCH-01A preliminary specification, Candidate B1 was identified as the *"NSW Electricity Stream"* and configured as a continuous regression task predicting half-hourly electricity price ($/MWh). 

However, in the foundational streaming machine-learning literature, the dataset commonly designated **ELEC2** is overwhelmingly recognized as a **streaming binary classification benchmark**.

Per Section 3 of the governing protocol:
> *"The canonical ELEC2 / Electricity dataset is historically a STREAMING CLASSIFICATION benchmark... Therefore BENCH-01A must NOT silently present a custom continuous target as canonical ELEC2."*

This audit verifies primary sources, inspects the underlying data attributes, assesses causality, establishes formal qualification metadata, and enforces the mandatory relabeling standard.

---

## 2. Authoritative Primary Source Verification (Section 4)

### 2.1 Primary References
1. **Harries, M. (1999).** *Splice-2 Comparative Evaluation: Electricity Market Dataset*. Technical Report, School of Computer Science and Engineering, The University of New South Wales (UNSW).
2. **Bifet, A., Holmes, G., Pfahringer, B., Kirkby, R., & Gavaldà, R. (2010).** *MOA: Massive Online Analysis*. Journal of Machine Learning Research (JMLR), 11, 1601–1604.
3. **Australian Energy Market Operator (AEMO).** *National Electricity Market (NEM) Historical Data Archive*. URL: `https://www.aemo.com.au/`.

### 2.2 Source Verification Findings
- **CANONICAL_TASK_TYPE:** **Streaming Binary Concept-Drift Classification**.
- **CANONICAL_TARGET:** Column `class` $\in \{\text{UP}, \text{DOWN}\}$.  
  *Definition:* The binary label reflects whether the market clearing price moved UP or DOWN relative to a moving average of past prices over the preceding 24 hours (48 half-hour periods):
  $$\text{class}_t = \begin{cases} \text{UP}, & \text{if } p_t > \frac{1}{48} \sum_{k=1}^{48} p_{t-k} \\ \text{DOWN}, & \text{otherwise} \end{cases}$$
- **FIELDS_AVAILABLE_IN_SOURCE:**
  1. `date`: Calendar date / chronological day index (0.0000 to 1.0000 normalized or integer);
  2. `day`: Day of week (1 to 7);
  3. `period`: Half-hour interval index within the day (1 to 48);
  4. `nswprice`: Continuous clearing price in New South Wales ($/MWh);
  5. `nswdemand`: Continuous electricity demand in New South Wales (MW);
  6. `vicprice`: Continuous clearing price in Victoria ($/MWh);
  7. `vicdemand`: Continuous electricity demand in Victoria (MW);
  8. `transfer`: Continuous scheduled interstate electricity transfer between NSW and Victoria (MW);
  9. `class`: Canonical binary classification label (`UP` / `DOWN`).
- **WHETHER_RAW_CONTINUOUS_PRICE_EXISTS:** **YES**. The continuous spot clearing price is explicitly recorded in column `nswprice` in the original AEMO records and in the unthresholded ELEC2 files.
- **WHETHER_CURRENT_BENCH_TARGET_IS_CANONICAL:** **NO**. The canonical benchmark task is binary classification. Continuous price forecasting is a derived regression task.

---

## 3. Methodological Assessment of the Derived Regression Task (Sections 6–11)

### 3.1 Why Track B Cannot Be Evaluated on Canonical Classification (Section 11)
Track B is fundamentally an online linear/recurrent regression learner derived from system identification and adaptive filtering principles:
- State equations compute continuous real-valued state transitions $s_t \in \mathbb{R}$;
- Parameter updates rely on real-valued prediction residuals $e_t = y_t - \hat{y}_t$ and forward-sensitivity traces;
- The architecture possesses **no logistic/softmax activation, no cross-entropy loss function, and no margin classifier head**.
Per Section 11: *"Do NOT add a classification-specific architectural head if this would materially modify the frozen architecture."* Adding a classification head or heuristic sign-thresholding margin would break the architectural freeze certified under `M2_SINGLE_STATE_SPEC.md`.

### 3.2 Causality & Future-Leakage Audit of Continuous Price Regression (Sections 6 & 9)
We evaluate whether continuous price regression is scientifically valid and future-safe:
1. **Target Authenticity:** The continuous target $y_t = \text{nswprice}_{t+1}$ is a physically measured variable recorded by the market operator; it is **not reconstructed or synthesized** from class labels.
2. **Causal Directionality (Section 9):** Target $y_t$ is observed at step $t+1$. Predictions at step $t$ are formed using covariates observed at or prior to $t$.
3. **No Moving-Average Inversion:** The regression task predicts the raw continuous price directly; it does not use a centered, non-causal, or future-aware moving average.
4. **Chronological Preservation:** All 45,312 observations are processed in strict historical sequence without shuffling.

---

## 4. Mandatory Relabeling & Governance Metadata (Sections 7 & 8)

Per Section 7 and 8 of the protocol:
- **Mandatory Canonical Identifier:**  
  $$\mathbf{NSW\_ELECTRICITY\_DERIVED\_REGRESSION}$$
- **Formal Governance Metadata:**  
  $$\mathbf{TASK\_STATUS = NONCANONICAL\_DERIVED\_REGRESSION\_TASK}$$
- **Forbidden Language Enforcement (Section 8):**  
  Active specifications, configuration files, and benchmark reporting documents must **NEVER** refer to this task as the *"canonical ELEC2 benchmark"* or compare its predictive metrics (MSE, MAE) to published ELEC2 classification accuracy/error rates. It must always be reported with the explicit qualifier: *"Derived continuous price regression on AEMO NSW electricity market records"*.

---

## 5. Formal Table A: ELEC2 Dataset Audit Summary (Section 59)

| Canonical Dataset | Canonical Task | Canonical Target | BENCH Task | Derived? | Future-Safe? | Final Benchmark Label | Protocol Decision |
| :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| **ELEC2 (Harries 1999)** | Streaming Binary Classification | `class` (`UP`/`DOWN`) | One-step-ahead continuous spot price forecasting | **YES** (Derived) | **YES** (Strictly Causal) | `NSW_ELECTRICITY_DERIVED_REGRESSION` | **`ELEC2_DERIVED_REGRESSION_VALID`** |

---

## 6. Formal Final Verdict (Sections 5 & 63)

$$\mathbf{ELEC2\_DECISION = ELEC2\_DERIVED\_REGRESSION\_VALID}$$
$$\mathbf{ELEC2\_PROTOCOL = PASS\_WITH\_RELABEL}$$

The continuous price regression task is verified as causally valid, physically meaningful, and non-leaking. It is formally retained under the mandatory qualified label `NSW_ELECTRICITY_DERIVED_REGRESSION`.
