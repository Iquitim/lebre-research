# BENCH-01A: Comprehensive Dataset Audit & Evaluation Suite Freeze

**Document ID:** BENCH-01A-DATASETS  
**Auditor:** Adversarial Benchmark Reviewer, Reproducibility Auditor & Data Integrity Officer  
**Date:** September 19, 2026  
**Status:** AUDIT COMPLETE — SUITE FROZEN WITH SCOPE LIMITS  
**Governing Standard:** Sections 12–41, 187, 190, 208 of BENCH-01A Protocol  

---

## 1. Executive Summary & Audit Mandate

Per Sections 2 and 12 of the governing protocol:
> *"BENCH-01 must be designed to FALSIFY the practical-value hypothesis. Do not choose datasets, metrics, baselines, budgets, or splits because they make Track B look favorable."*

The PRA-01R preliminary candidate list was subjected to an adversarial data-integrity audit. This audit identified critical ambiguities in the initial candidates, resolved conflated dataset identities, classified recurrence demand, verified causal streaming properties, and established a balanced task suite spanning **Block A (Controlled Mechanistic & Synthetic Holdout Diagnostics)** and **Block B (External Real-World Continuous Streams)**.

---

## 2. Comprehensive Audit of Public Real-World Candidates (Block B)

### 2.1 Public Dataset Candidate 1: AEMO NSW Electricity Stream (ELEC2 Audit)
- **NAME & CANONICAL BENCHMARK IDENTIFIER:** `NSW_ELECTRICITY_DERIVED_REGRESSION`.
- **METADATA:** `TASK_STATUS = NONCANONICAL_DERIVED_REGRESSION_TASK`.
- **SOURCE:** Australian Energy Market Operator (AEMO) / Canonical ELEC2 record (Harries 1999; MOA / River repository). URL: `https://www.aemo.com.au/`.
- **LICENSE:** Open Government Data / Creative Commons Attribution 4.0 International (CC BY 4.0).
- **CANONICAL FORMULATION IN ML LITERATURE (Section 13):**  
  In the streaming machine-learning literature (e.g., Harries 1999; Bifet et al. 2010), ELEC2 is canonically treated as a **binary classification task** (`class` $\in \{\text{UP}, \text{DOWN}\}$), predicting whether the half-hourly spot price will rise or fall relative to a 24-hour moving average.
- **AUDIT FOR REGRESSION LEARNER (Sections 14 & 21):**  
  Track B is fundamentally an online linear/recurrent regression learner trained via squared-error loss and forward-sensitivity gradient updates. It possesses no sigmoid/softmax head or log-loss objectives. Forcing Track B to solve classification via an ad-hoc sign-thresholding wrapper would distort the evaluation. However, the underlying physical dataset consists of raw continuous physical covariates: `nswprice` ($/MWh), `nswdemand` (MW), `vicprice`, `vicdemand`, and `transfer`. In energy economics (e.g., Weron 2014), the canonical task is **continuous half-hourly spot price forecasting**.
- **RECONCILIATION DECISION (Section 14):**  
  **`ELEC2_DERIVED_REGRESSION_VALID`** (under explicit relabeling). The benchmark locks the **continuous regression formulation** of the NSW electricity stream: predicting the continuous next-period clearing price $y_{t} = \text{nswprice}_{t+1}$ ($/MWh) given current and past market covariates.
- **N (Total Steps):** $45{,}312$ chronological half-hourly observations (spanning May 1996 to December 1998).
- **D (Ambient Features):** 5 continuous covariates (`nswdemand`, `vicprice`, `vicdemand`, `transfer`, `scheduled_reserve`).
- **ORDERING:** Strictly chronological, contiguous time series ($t = 1, \dots, 45312$). Shuffling is strictly forbidden.
- **TEMPORAL GRANULARITY:** Exactly 30-minute intervals.
- **MISSINGNESS:** Zero missing records; minor negative prices during extreme off-peak generation surplus (physically meaningful market phenomena, retained as raw).
- **PREPROCESSING (Causal):** Online exponential running z-score normalization ($\alpha_{\text{norm}} = 10^{-4}$); target is standardized using running statistics updated *strictly after* prediction.
- **TARGET AVAILABILITY (Section 7):** Immediate at $t+1$ (clearing prices published at close of the 30-minute market window).
- **RECURRENCE CLASS (Section 32):** **`TEMPORAL_HELPFUL`**. Strong 48-step daily and 336-step weekly diurnal cycles, with short-term price autocorrelation and supply momentum.
- **DRIFT CLASS:** Severe non-stationarity: seasonal weather shifts, deregulation shocks, supply bidding spikes, and market regime transitions.
- **LEAKAGE RISKS:** Pre-computing global min/max price across the full 2.5-year span leaks future deregulation inflation. Must use purely online normalization.
- **BASELINE APPLICABILITY:** All regression baselines (RZA-LMS, CCN, MUSE-RNN, Minimal GRU, Online ESN, Variable-Tap LMS, LRU).
- **AUDIT STATUS (Section 190):** **`LOCKED_WITH_SCOPE_LIMIT`** (Non-canonical derived continuous regression task).

---

### 2.2 Public Dataset Candidate 2: MPI Jena Climate Weather Stream (Weather Audit)
- **NAME:** Max Planck Institute for Biogeochemistry Jena Climate Dataset (MPI Jena Climate).
- **SOURCE & RESOLUTION (Section 15):**  
  The phrase *"NOAA Jena Weather"* conflated two separate entities: the US NOAA Global Historical Climatology Network (GHCN) and the Max Planck Institute Jena Weather Station. We explicitly resolve the source to the **MPI Jena Climate Record** recorded by the Max Planck Institute for Biogeochemistry at the Saale river valley weather station in Jena, Germany.  
  DOI: `10.17617/1.76`. Canonical repository: MPI-BGC / Keras Time-Series Archive.
- **LICENSE:** Open Access / Creative Commons Attribution 4.0 International (CC BY 4.0).
- **TASK (Section 16):** Strictly defined as **single-step continuous time-series regression**.
- **TARGET VARIABLE (Section 16):** Atmospheric Temperature $T$ (in $^\circ\text{C}$).  
  *Audit Justification:* Temperature reflects continuous thermal momentum and multi-timescale thermodynamic inertia, providing a representative physical dynamical target without cherry-picking.
- **FORECAST HORIZON (Section 17):** **One-step ahead ($h=1$, representing 10 minutes ahead)**.
- **N (Total Steps):** $70{,}000$ consecutive 10-minute intervals (subsampled chronologically from the 2014–2016 continuous monitoring segment).
- **D (Ambient Features):** 13 continuous meteorological covariates: atmospheric pressure ($p$), relative humidity ($rh$), vapor pressure ($vp$), dew point ($T_{\text{dew}}$), wind speed ($wv$), max wind speed, wind direction, potential temperature, air density ($\rho$).
- **ORDERING:** Strictly chronological time series ($t = 1, \dots, 70000$).
- **TEMPORAL GRANULARITY:** 10 minutes between successive measurements.
- **MISSINGNESS:** Handled via online causal forward-fill; no future interpolation.
- **PREPROCESSING:** Online adaptive standard scaler ($x_{t} \leftarrow (x_{t} - \hat{\mu}_{t}) / \hat{\sigma}_{t}$) updated post-prediction.
- **TARGET AVAILABILITY:** Immediate at step $t+1$.
- **RECURRENCE CLASS (Section 32):** **`TEMPORAL_HELPFUL`**. Thermal inertia benefits from short autoregressive state, while solar radiation and barometric pressure provide strong instantaneous predictive signals.
- **DRIFT CLASS:** Diurnal cycles, seasonal solar irradiance transitions, and rapid meteorological front passages (concept drift).
- **LEAKAGE RISKS:** Batch seasonal detrending or centered moving averages would cause fatal future leakage. Prohibited.
- **BASELINE APPLICABILITY:** Fully compatible with all primary and secondary baselines.
- **AUDIT STATUS (Section 190):** **`LOCKED`**.

---

### 2.3 Public Dataset Candidate 3: UCI Dynamic Gas Mixture Concentration Stream (Gas Sensor Audit)
- **NAME:** Gas Sensor Array Under Dynamic Gas Mixtures (UCI Gas Dynamic Mixture Stream).
- **SOURCE & RESOLUTION (Sections 18–20):**  
  The original Vergara et al. (2012) *Gas Sensor Array Drift Dataset* consists of 10 discrete batches spanning 36 months, canonically framed as a 6-class chemical classification problem. Per Section 21 of the protocol, forcing a 6-class classification problem on a regression architecture without dedicated softmax heads is unacceptable.  
  We audit and adopt the extension: **Fonollosa, Rodriguez-Lujan, Huerta, & Marco (2015)**, *Gas sensor array under dynamic gas mixtures*, published in *IEEE Sensors Journal* (DOI: `10.1109/JSEN.2015.2407457`) and hosted at the UCI Machine Learning Repository.
- **LICENSE:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **TASK (Section 20):** Continuous multi-sensor regression under continuous physical drift and chemical transport dynamics.
- **TARGET VARIABLE:** Continuous concentration of Carbon Monoxide (CO in parts-per-million, ppm) under dynamic binary gas exposure.
- **N (Total Steps):** $20{,}000$ contiguous time steps (sampled at 1 Hz from continuous 12-hour continuous exposure monitoring).
- **D (Ambient Features):** 16 chemical metal-oxide semiconductor (MOS) sensor conductivity channels (8 Figaro TGS 2602, 8 Figaro TGS 2600).
- **ORDERING:** Continuous chronological physical time stream ($t = 1, \dots, 20000$).
- **TEMPORAL GRANULARITY:** Continuous sampling at 1.0 second intervals.
- **MISSINGNESS:** None.
- **PREPROCESSING:** Causal logarithmic conductance transform followed by online recursive mean/variance scaling.
- **TARGET AVAILABILITY:** Immediate at step $t+1$.
- **RECURRENCE CLASS (Section 32):** **`TEMPORAL_HELPFUL`**. MOS sensors exhibit significant chemical adsorption/desorption tail dynamics (exponential decay memory kernels) that cannot be captured by instantaneous sensor readings alone.
- **DRIFT CLASS:** Physical sensor poisoning, baseline conductance drift, thermal fluctuation, and turbulent chemical plume arrival.
- **LEAKAGE RISKS:** Pre-centering baseline resistances across the entire 12-hour block leaks baseline degradation. Prohibited.
- **BASELINE APPLICABILITY:** Fully compatible with all streaming regression baselines.
- **AUDIT STATUS (Section 190):** **`LOCKED`**.

---

### 2.4 Public Dataset Candidate 4: Silverbox Nonlinear Dynamical Benchmark (Silverbox Audit)
- **NAME:** Silverbox Benchmark for Nonlinear System Identification (IEEE Silverbox).
- **SOURCE (Sections 22–24):**  
  Wigren, T., & Schoukens, J. (2013). *Three free benchmark problems for identification of nonlinear systems*. European Control Conference (ECC), pp. 1148–1153. Canonical data repository: `http://www.nonlinearbenchmark.org/`.
- **LICENSE:** Public Open Research Benchmark (Free for Academic and Comparative Evaluation).
- **TASK:** Prequential one-step-ahead prediction of an experimental electronic physical system exhibiting Duffing-type nonlinear resonance.
- **TARGET VARIABLE:** Output voltage $V_{\text{out}}(t)$ (in Volts).
- **N (Total Steps):** $40{,}000$ samples representing the canonical continuous evaluation segment (comprising arrow-head test excitations and Gaussian multisine sequences).
- **D (Ambient Features):** Exactly 1 continuous input signal: Generator excitation voltage $V_{\text{in}}(t)$.
- **ORDERING:** Strict physical sampling order ($t = 1, \dots, 40000$).
- **TEMPORAL GRANULARITY:** Sampled at $f_s = 610.35\text{ Hz}$ ($T_s \approx 1.6384\text{ ms}$).
- **MISSINGNESS:** None.
- **PREPROCESSING:** **`STATIC_SAFE`**. Exact physical volt-scaling (multiplied by 1.0); zero normalization filtering applied to preserve natural physical resonance.
- **TARGET AVAILABILITY:** Immediate at $t+1$.
- **RECURRENCE CLASS (Sections 23 & 32):** **`STATE_CRITICAL`**. The circuit physically realizes a second-order nonlinear Duffing oscillator:
  $$m \ddot{y}(t) + d \dot{y}(t) + a y(t) + b y^3(t) = u(t)$$
  Predicting $y_t$ given only $u_t$ is mathematically impossible without internal temporal memory/state. Static linear filters fail completely.
- **DRIFT CLASS:** Stationary nonlinear dynamics with non-stationary excitation regimes (arrow-head amplitude modulation testing amplitude-dependent resonance).
- **LEAKAGE RISKS:** Offline non-causal filtering (e.g., zero-phase forward-backward Butterworth filtering) would destroy causality. Prohibited.
- **BASELINE APPLICABILITY:** Mandatory test of recurrence capability for all baselines.
- **AUDIT STATUS (Section 190):** **`LOCKED`** (Top-Priority State-Critical Benchmark).

---

### 2.5 Public Dataset Candidate 5: Friedman Drift Stream (Audit & Reclassification)
- **NAME:** Friedman Drift Concept-Drift Stream.
- **SOURCE & AUDIT (Sections 25–26):**  
  PRA-01R tentatively listed Friedman Drift under Block B. However, Friedman Drift is derived from Jerome Friedman's 1991 MARS paper and implemented as an **algorithmic synthetic generator** (e.g., in the River streaming library):
  $$y = 10 \sin(\pi x_1 x_2) + 20 (x_3 - 0.5)^2 + 10 x_4 + 5 x_5 + \sum_{j=6}^{10} 0 \cdot x_j + \epsilon_t$$
  where coefficients or feature indices drift over time.
- **RECLASSIFICATION MANDATE (Section 26):**  
  Per Section 26: *"If Friedman drift is generated synthetically: classify it as: BLOCK A / CONTROLLED EXTERNAL GENERATOR not as a real-world public dataset."*
- **AUDIT STATUS (Section 190):** **`RECLASSIFIED_TO_BLOCK_A`**. It is moved out of Block B to ensure Block B contains strictly real-world physical datasets.

---

### 2.6 Dedicated Real-World Negative Control Dataset: Household Power Static Stream (Negative Control Audit)
- **NAME:** Individual Household Electric Power Consumption Sub-Metering Control Stream (UCI Household Negative Control).
- **SOURCE (Sections 34–35):**  
  Hebrail, G., & Berard, A. (2012). UCI Machine Learning Repository. DOI: `10.24432/C58K54`.
- **TASK (Section 35):** Real-world negative control regression where the target is heavily dominated by concurrent instantaneous sub-metering features, rendering recurrent state largely unnecessary.
- **TARGET VARIABLE:** Global Active Power ($kW$).
- **N (Total Steps):** $25{,}000$ consecutive 1-minute measurements.
- **D (Ambient Features):** 6 concurrent electrical measurements (`Global_reactive_power`, `Voltage`, `Global_intensity`, `Sub_metering_1`, `Sub_metering_2`, `Sub_metering_3`).
- **RECURRENCE CLASS (Section 32):** **`MOSTLY_CURRENT_INPUT` (NEGATIVE CONTROL)**. Because $P_{\text{active}} \approx V \cdot I \cdot \cos(\phi) \approx \text{Sub}_1 + \text{Sub}_2 + \text{Sub}_3 + P_{\text{other}}$, the instantaneous physical relation accounts for $>95\%$ of target variance. Temporal recurrence provides negligible predictive advantage.
- **PURPOSE (Section 35):** Tests whether Track B successfully detects that temporal state is unneeded and avoids wasteful state allocation and compute overhead.
- **AUDIT STATUS (Section 190):** **`LOCKED`** (Negative Control).

---

## 3. Block A: Controlled Mechanistic Tasks & Synthetic Holdout Generators

Per Section 38, Block A tasks provide mechanistic interpretation, controlled resource accounting, and failure localization. 

### 3.1 Mechanistic Diagnostic Suite (A1–A8)
| Task ID | Task Formal Name | Mathematical Formulation | Development Overlap (Section 37) | Primary Diagnostic Purpose |
| :--- | :--- | :--- | :---: | :--- |
| **A1** | Sparse Support Shift | $y_t = w_{S_t}^\top x_{S_t, t} + \epsilon_t$; $D=50, K=3$; support shifts at $t=5000$. | YES (M1) | Sparse feature discovery & prompt eviction. |
| **A2** | Single Delayed Dependency | $y_t = 0.8 x_{1, t-4} + \epsilon_t$; $D=20, Q=2$. | YES (M2-EXP-0001) | Exact lag discovery without state birth. |
| **A3** | Multiple Dispersed Delays | $y_t = 0.5 x_{1, t-2} + 0.5 x_{2, t-8} + \epsilon_t$. | YES (M2-EXP-0002) | Multi-tap non-contiguous delay exploration. |
| **A4** | Long-Delay Scaling | $y_t = 0.8 x_{1, t-d} + \epsilon_t$; $d \in \{5, 15, 30, 50\}$. | YES (M2-EXP-0003) | Empirical phase boundary: tap vs state. |
| **A5** | SET/RESET Quiescent Memory | Bistable latch toggled by Poisson event pulses. | YES (M2-EXP-0004) | Gated recurrence birth & discrete retention. |
| **A6** | Context Routing | Binary context feature switches feedforward vs AR path. | YES (M2-EXP-0005) | Context-gated temporal structural allocation. |
| **A7** | Extended Poisson Quiescence | Cues followed by Poisson gaps ($L_{\text{gap}} \sim \text{Poisson}(150)$). | YES (M2-EXP-0006) | Quiescent structural retention ($C \times O$). |
| **A8** | Abrupt Tri-Regime Transition | Cycle: Linear ($t \le 3333$) $\to$ Lag ($t \le 6666$) $\to$ Recurrent ($t \le 10000$). | YES (M2-R1) | Closed-loop expansion and contraction. |

---

### 3.2 Two Novel Mechanistic Holdout Generators (Sections 40 & 41)

To ensure Block A contains rigorous tests not contaminated by Track-B development, two completely new synthetic generators are locked:

#### Holdout Generator H1: Multi-Frequency Damped Resonator (Harmonic Drift)
- **Mathematical Formulation:**  
  A continuous second-order linear dynamical system driven by white noise $u_t \sim \mathcal{N}(0, 1)$, where the natural frequency $\omega_t$ and damping ratio $r_t$ drift over time:
  $$s_{1, t} = 2 r_t \cos(\omega_t) s_{1, t-1} - r_t^2 s_{2, t-1} + u_t$$
  $$s_{2, t} = s_{1, t-1}$$
  $$y_t = s_{1, t} + \sum_{j=1}^{48} 0 \cdot x_{j, t} + \epsilon_t$$
  where $r_t \in [0.85, 0.98]$ and $\omega_t \in [\pi/12, \pi/4]$ undergo continuous sinusoidal drift. Total ambient dimension $D = 50$.
- **Audit Characteristics:** Never seen during Track-B development. Tests whether scalar recurrence can track drifting resonance without discrete latching.

#### Holdout Generator H2: Asymmetric Switching Delayed Volterra Stream
- **Mathematical Formulation:**  
  A non-linear quadratic Volterra memory kernel with state-dependent structural switching:
  $$y_t = \begin{cases} 0.6 x_{1, t-3}^2 + 0.4 x_{2, t-7} + \epsilon_t, & \text{if } x_{\text{switch}, t} > 0 \\ 0.8 s_t + 0.2 x_{3, t} + \epsilon_t, & \text{if } x_{\text{switch}, t} \le 0 \end{cases}$$
  where $s_t = 0.92 s_{t-1} + x_{4, t-1}$, with $D=40$ noise distractors.
- **Audit Characteristics:** Tests whether the unified probe lifecycle can discover non-linear lag interactions and switch between lag-dominated and state-dominated memory paths.

---

## 4. Benchmark Suite Balance Audit (Sections 233 & 234)

Per Section 233, the balance of the complete BENCH-01 evaluation suite is audited:

```
+-------------------------------------------------------------------------------+
|                      BENCH-01 OVERALL SUITE BALANCE AUDIT                    |
+------------------------------------+------------------------------------------+
| Dimension                          | Count / Distribution                     |
+------------------------------------+------------------------------------------+
| Total Evaluation Streams           | 15 Distinct Streams                      |
| Block A (Mechanistic & Synthetic)  | 10 Streams (8 Diagnostic + 2 Holdout)    |
| Block B (Public Real-World Streams)| 5 Real-World Datasets                    |
| Task Formulation                   | 100% Continuous Prequential Regression   |
| System Identification Tasks        | 2 Streams (Silverbox, H1 Resonator)      |
| Recurrence: STATE_CRITICAL         | 4 Streams (A5, A8-R3, Silverbox, H1)     |
| Recurrence: TEMPORAL_HELPFUL       | 7 Streams (A2, A3, A4, A7, NSW, Jena, Gas)|
| Recurrence: MOSTLY_CURRENT_INPUT   | 4 Streams (A1, Negative Control, H2, Sub)|
| Non-Stationary Drift Profiles      | 13 Streams (Abrupt, Gradual, Seasonal)   |
| Stationary Controlled Profiles     | 2 Streams (A2, Silverbox Baseline)       |
+------------------------------------+------------------------------------------+
```

### Balance Verdict (Section 234):
**`SUITE_BALANCED`**. The benchmark avoids over-concentration in synthetic toy environments ($5$ real-world public streams representing $>185{,}000$ real-world steps), balances recurrence difficulty (4 state-critical, 7 temporal-helpful, 4 low-memory negative controls), and subjects all models to diverse physical and market non-stationarities.
