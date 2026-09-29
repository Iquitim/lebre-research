# BENCH-01A: Causal Online Preprocessing Specification & Temporal Leakage Audit

**Document ID:** BENCH-01A-PREPROCESSING  
**Auditor:** Data Integrity Officer & Online Learning Systems Auditor  
**Date:** September 19, 2026  
**Status:** PROTOCOL LOCKED — ZERO LEAKAGE VERIFIED  
**Governing Standard:** Sections 6–11, 195, 196, 211 of BENCH-01A Protocol  

---

## 1. Governing Prequential Streaming Protocol (Section 6)

In strict accordance with the prequential streaming principle, every evaluation step across all 15 benchmark streams follows an immutable, strictly causal 5-phase execution loop:

```
+-----------------------------------------------------------------------------+
|                     PREQUENTIAL STREAMING EXECUTION CYCLE                   |
|                                                                             |
|  Step 1: RECEIVE OBSERVATION       -->  x_t received from data source       |
|  Step 2: CAUSAL PREPROCESSING      -->  x_t_norm = Scale(x_t; State_{t-1})  |
|  Step 3: EMIT PREDICTION           -->  y_hat_t = Model.predict(x_t_norm)   |
|  Step 4: RECORD PREQUENTIAL LOSS   -->  Loss_t = (y_t - y_hat_t)^2          |
|  Step 5: REVEAL TARGET & UPDATE    -->  Model.update(x_t_norm, y_t);        |
|                                         State_t = UpdateScaler(x_t, y_t)    |
+-----------------------------------------------------------------------------+
```

### Absolute Invariant:
**No model or preprocessing scaler may observe target $y_t$ or update internal statistics until AFTER prediction $\hat{y}_t$ is emitted and recorded.**

---

## 2. Temporal Leakage Audit & Prohibition Matrix (Section 8)

The following operations are classified as **`FUTURE_LEAKING`** and are strictly prohibited across all benchmark tasks:

| Operation Category | Specific Prohibited Technique | Leakage Rationale & Scientific Consequence | Audit Status |
| :--- | :--- | :--- | :---: |
| **Global Scaling** | Full-dataset MinMax or Z-Score scaling before train/test split. | Leaks global range and future non-stationarities; artificially depresses regret. | **PROHIBITED** |
| **Stream Shuffling** | Random k-fold cross-validation or train/test dataset shuffling. | Destroys chronological causality; converts autoregressive prediction to interpolation. | **PROHIBITED** |
| **Non-Causal Filtering** | Forward-backward Butterworth or zero-phase digital filtering (`filtfilt`). | Uses future samples $t+1, \dots, t+k$ to smooth current sample $t$. | **PROHIBITED** |
| **Centered Windows** | Centered rolling averages ($\frac{1}{2k+1} \sum_{i=-k}^k x_{t+i}$). | Peeks into future time window $t+1, \dots, t+k$. | **PROHIBITED** |
| **Future Imputation** | Spline or linear interpolation over missing values using future points. | Leaks future recovery trajectory during sensor dropouts. | **PROHIBITED** |
| **Change-Point Oracle** | Informing models of ground-truth regime change timestamps. | Grants unfair advantage by artificially bypassing drift detection latencies. | **PROHIBITED** |

---

## 3. Preprocessing Operation Classification (Sections 9–11)

Every data transformation utilized in BENCH-01 is explicitly classified:

### 3.1 `STATIC_SAFE` Transformations (Section 10)
Operations whose governing parameters are mathematically fixed constants, physical unit conversions, or canonical architectural constants independent of dataset realizations:
1. **Physical Voltage Scaling (Silverbox):** Multiplied by $1.0$ (raw Volts). Fixed physical unit.
2. **Conductance Log-Transform (Gas Mixture):** $x_{\text{log}} = \log_{10}(G / G_0)$ where $G_0 = 1.0\text{ mS}$. Fixed chemical baseline.
3. **Delay Line Buffering:** Causal FIFO delay registers ($x_{j, t-d}$). Causal state memory.

### 3.2 `ONLINE_ADAPTIVE` Transformations (Section 11)
Operations whose normalization parameters evolve dynamically over time, updating strictly *after* step prediction:
1. **Online Recursive Welford Scaler:**  
   Maintains running estimates of mean $\hat{\mu}_t$ and variance $\hat{\sigma}_t^2$ using an exponential forgetting factor $\alpha_{\text{norm}} \in [10^{-5}, 10^{-3}]$:
   $$\hat{\mu}_t = (1 - \alpha_{\text{norm}}) \hat{\mu}_{t-1} + \alpha_{\text{norm}} x_t$$
   $$\hat{\sigma}_t^2 = (1 - \alpha_{\text{norm}}) \hat{\sigma}_{t-1}^2 + \alpha_{\text{norm}} (x_t - \hat{\mu}_t)^2$$
   $$x_{t, \text{norm}} = \frac{x_t - \hat{\mu}_{t-1}}{\sqrt{\hat{\sigma}_{t-1}^2 + \epsilon_{\text{scale}}}}$$
   *Critical Causal Timing:* Normalization at step $t$ uses parameters $\hat{\mu}_{t-1}, \hat{\sigma}_{t-1}$. Updates to $\hat{\mu}_t, \hat{\sigma}_t$ occur exclusively in Phase 5.
2. **Causal Forward-Fill Imputation:**  
   If a sensor channel suffers a dropout at step $t$, the missing value is replaced by the last known valid observation:
   $$x_{j, t} = x_{j, t-1}$$
   Zero interpolation with future timestamps $t+k$ is permitted.

---

## 4. Dataset-by-Dataset Preprocessing Audit

| Dataset / Stream | Preprocessing Pipeline | Scaler Type | Update Timing | Leakage Audit Status |
| :--- | :--- | :---: | :---: | :---: |
| **A1–A8 (Mechanistic)** | Raw synthetic signals; zero pre-scaling needed. | `STATIC_SAFE` | None | **PASS (Zero Leakage)** |
| **H1 (Damped Resonator)**| Raw driving white noise and state response. | `STATIC_SAFE` | None | **PASS (Zero Leakage)** |
| **H2 (Switching Volterra)**| Raw quadratic lag signals. | `STATIC_SAFE` | None | **PASS (Zero Leakage)** |
| **B1 (NSW Electricity)** | Online Welford scaling on continuous demand/price. | `ONLINE_ADAPTIVE` | Post-Prediction | **PASS (Zero Leakage)** |
| **B2 (Jena Weather)** | Online Welford scaling on 13 meteorological covariates.| `ONLINE_ADAPTIVE` | Post-Prediction | **PASS (Zero Leakage)** |
| **B3 (Gas Mixture Stream)**| Conductance log transform + Online Welford scaler. | `ONLINE_ADAPTIVE` | Post-Prediction | **PASS (Zero Leakage)** |
| **B4 (Silverbox System ID)**| Raw voltage inputs and outputs. Zero normalization. | `STATIC_SAFE` | None | **PASS (Zero Leakage)** |
| **B5 (Household Control)**| Online Welford scaling on sub-metering features. | `ONLINE_ADAPTIVE` | Post-Prediction | **PASS (Zero Leakage)** |

---

## 5. Formal Certification of Question 4 (Section 196)

- **Audit Question 4:** *Are all preprocessing operations causal?*
- **Audit Verdict:** **`YES`**.
- **Certification Statement:**  
  Every transform in the BENCH-01 evaluation suite operates strictly on past and current observations ($t' \le t$). No future information, global statistics, or non-causal smoothing windows are utilized anywhere in the pipeline.
