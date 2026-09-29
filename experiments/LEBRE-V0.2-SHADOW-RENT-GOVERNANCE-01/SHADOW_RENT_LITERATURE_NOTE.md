# Methodological & Theoretical Foundation: Shadow-Rent Governance and Budgeted Counterfactual Scheduling

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** Periodic vs. Event-Triggered Shadow Scheduling, Cumulative Change Detection, and Compute-Ceiling Recovery  
**Author:** Independent Skeptical Senior Researcher  
**Status:** SEALED DESIGN REFERENCE  

---

## 1. Context and Problem Formulation

In online adaptive filtering and stream learning, architectures such as LEBRE ($T_3$) maintain two parallel computation paths:
1. A **Live Path** executing the current active hypothesis (standard scaling, base linear filtering, active discrete delay taps, and active recurrent scalar filtering).
2. A **Shadow Path** conducting counterfactual exploration (background 2-probe correlation grid estimation, provisional candidate LMS updates, shadow recurrent unit simulation, counterfactual prediction evaluations, and conditional-gain EMA filtering).

In the corrected canonical $T_3$ baseline (`CORRECTED_SHADOW_RENT_BASELINE.json`), live execution incurs a benchmark average of $81.17$ floating-point operations per step ($\text{FLOPs/step}$), while continuous shadow exploration incurs an unoptimized average of $86.53$ $\text{FLOPs/step}$. The resulting aggregate online compute is:
$$\text{Total Online Compute} = 81.17 + 86.53 = 167.70 \text{ FLOPs/step}$$

This continuous burden breaches the historical $R2$ compute ceiling:
$$\mathbb{E}[\text{Total Online FP}] \le 100 \text{ FLOPs/step}$$

Because live execution is fixed near $81.17$ $\text{FLOPs/step}$, the remaining allowable budget for shadow exploration is:
$$\text{Available Shadow Budget} = 100 - 81.17 \approx 18.83 \text{ FLOPs/step}$$
To achieve compliance, continuous shadow computation must be sparsified by approximately $78.2\%$.

The scientific question of this study is:
> **How often must the already-validated shadow mechanism execute in order to preserve structural discovery and regime adaptation without degrading predictive performance?**

---

## 2. Literature Review & Claim Classification Discipline

In accordance with strict methodological rigor, every cited theoretical concept and algorithmic mechanism is classified into one of three distinct epistemic categories:
1. `ESTABLISHED_MECHANISM`: Well-characterized mathematical or algorithmic method with formal guarantees in its original domain.
2. `CONCEPTUAL_ANALOGY`: Cross-disciplinary principle providing motivation and structural heuristics, but lacking automatic transfer guarantees to streaming online filtering.
3. `LEBRE_SPECIFIC_HYPOTHESIS`: Empirical hypothesis specific to LEBRE's architecture, requiring experimental validation within this study.

```
+-----------------------------------------------------------------------------------------------+
| CITATION TAXONOMY & EPISTEMIC CLASSIFICATION                                                  |
+------------------------------+---------------------------+------------------------------------+
| Source Citation              | Foundational Principle    | Epistemic Classification           |
+------------------------------+---------------------------+------------------------------------+
| Heemels, Johansson &         | Event-Triggered and       | CONCEPTUAL_ANALOGY                 |
| Tabuada (2012)               | Self-Triggered Control    |                                    |
| Page (1954)                  | Cumulative Sum (CUSUM)    | ESTABLISHED_MECHANISM (Statistics) |
|                              | Continuous Inspection     | / CONCEPTUAL_ANALOGY (TinyML)      |
| Hinkley (1971)               | Sequential Change-Point   | ESTABLISHED_MECHANISM (Statistics) |
|                              | Inference                 |                                    |
| Bifet & Gavaldà (2007)       | Adaptive Windowing        | CONCEPTUAL_ANALOGY                 |
|                              | (ADWIN) Drift Detection   |                                    |
| Diniz (2018)                 | Data-Selective Adaptive   | ESTABLISHED_MECHANISM (DSP)        |
|                              | Filtering                 |                                    |
| Umlauft & Hirche (2020)      | Event-Triggered Online    | CONCEPTUAL_ANALOGY                 |
|                              | Learning / GP Updates     |                                    |
| LEBRE S2 / S3 Scheduling     | Periodic / Event Shadow   | LEBRE_SPECIFIC_HYPOTHESIS          |
|                              | Duty Cycling              |                                    |
+------------------------------+---------------------------+------------------------------------+
```

---

### 2.1 Event-Triggered Resource Allocation
- **Citation:** Heemels, W. P. M. H., Johansson, K. H., & Tabuada, P. (2012). *An Introduction to Event-Triggered and Self-Triggered Control*. IEEE Conference on Decision and Control (CDC), pp. 3270–3285. DOI: [10.1109/CDC.2012.6425820](https://doi.org/10.1109/CDC.2012.6425820).
- **Relevant Principle:** In embedded and resource-constrained control loops, continuous state sensing, communication, and actuation waste computational and bandwidth resources when the system remains close to its equilibrium manifold. Event-triggered mechanisms replace periodic execution by evaluating a low-cost Lyapunov-based or error-based triggering condition $\|\mathbf{e}(t)\| > \sigma \|\mathbf{x}(t)\|$, executing heavy computational updates only when state deviation breaches an admissibility threshold.
- **Epistemic Classification:** `CONCEPTUAL_ANALOGY`.
- **Methodological Boundary:** This principle originates in dynamical control systems where plant dynamics and stability criteria are known a priori. In streaming machine learning and adaptive filtering, data distributions are non-stationary, plant dynamics are unknown, and stability is asymptotic rather than exponential. Therefore, event-triggered control provides a design analogy, not formal proof that event triggering preserves structural adaptation in LEBRE.

---

### 2.2 Sequential Change Detection (CUSUM)
- **Citations:**
  - Page, E. S. (1954). *Continuous Inspection Schemes*. Biometrika, 41(1/2), 100–115. DOI: [10.1093/biomet/41.1-2.100](https://doi.org/10.1093/biomet/41.1-2.100).
  - Hinkley, D. V. (1971). *Inference about the Change-Point from Cumulative Sum Tests*. Biometrika, 58(3), 509–523. DOI: [10.1093/biomet/58.3.509](https://doi.org/10.1093/biomet/58.3.509).
- **Relevant Principle:** The Page CUSUM inspection scheme accumulates sequential log-likelihood ratios or score deviations to detect sudden shifts in the parameter of a stochastic process:
  $$S_t = \max(0, S_{t-1} + (X_t - \mu_0 - \delta))$$
  where $\mu_0$ is the in-control parameter, $\delta$ is a reference slack parameter, and an alarm is signaled when $S_t > \lambda$. Page and Hinkley proved that this sequential test minimizes detection delay for a specified average run length (ARL) to false alarm.
- **Epistemic Classification:** `ESTABLISHED_MECHANISM` in statistical process control; `CONCEPTUAL_ANALOGY` when applied to TinyML prequential loss filtering.
- **Methodological Boundary:** Page and Hinkley derived optimal detection boundaries under independent and identically distributed (i.i.d.) Gaussian or exponential observations. In online learning, prequential squared prediction errors $\ell_t = (y_t - \hat{y}_t)^2$ exhibit temporal autocorrelation, heteroscedasticity, and transient learning spikes. Thus, classic ARL formulas do not transfer directly, and thresholds must be empirically calibrated using historical development data.

---

### 2.3 Adaptive Stream Change Detection (ADWIN)
- **Citation:** Bifet, A., & Gavaldà, R. (2007). *Learning from Time-Changing Data with Adaptive Windowing*. SIAM International Conference on Data Mining (SDM), pp. 443–448. DOI: [10.1137/1.9781611972771.42](https://doi.org/10.1137/1.9781611972771.42).
- **Relevant Principle:** ADWIN maintains an adaptive sliding window of observations, dynamically adjusting window length by evaluating statistically significant mean differences across all sub-window splits via Hoeffding bounds.
- **Epistemic Classification:** `CONCEPTUAL_ANALOGY`.
- **Methodological Boundary:** While ADWIN provides distribution-free guarantees with bounded false positive rates, its memory footprint (storing hierarchical bucket summaries) and variable per-step compute ($\mathcal{O}(\log W)$ FLOPs and integer operations) exceed the rigid TinyML constraints of LEBRE (where persistent memory allowance is $\le 40$ Bytes and compute allowance is $\le 2$ FLOPs). Hence, ADWIN serves as an architectural comparator, but cannot be directly deployed as the always-on LEBRE sentinel.

---

### 2.4 Data-Selective Adaptive Filtering
- **Citation:** Diniz, P. S. R. (2018). *On Data-Selective Adaptive Filtering*. IEEE Transactions on Signal Processing, 66(16), 4239–4252. DOI: [10.1109/TSP.2018.2847657](https://doi.org/10.1109/TSP.2018.2847657).
- **Relevant Principle:** Data-selective adaptive filtering algorithms (such as set-membership LMS and selective-updating affine projection) update filter weights only when the instantaneous error exceeds a predetermined threshold $\gamma$, or when the incoming observation vector provides sufficient "innovation":
  $$\mathbf{w}_{t+1} = \begin{cases} \mathbf{w}_t + \mu \frac{e_t}{\|\mathbf{x}_t\|^2} \mathbf{x}_t, & \text{if } |e_t| > \gamma \\ \mathbf{w}_t, & \text{otherwise} \end{cases}$$
  Diniz demonstrates that under stationary or piecewise-stationary noise, skipping updates on 70–90% of samples yields final mean-squared error performance comparable to full-cadence filtering while slashing computational load.
- **Epistemic Classification:** `ESTABLISHED_MECHANISM` in DSP; `LEBRE_SPECIFIC_HYPOTHESIS` for counterfactual shadow exploration.
- **Methodological Boundary:** Diniz evaluates data selectivity for primary linear filter updates. In LEBRE, the live filter weights continue updating at every step; what is being made selective is the *counterfactual shadow probing and hypothesis generation pipeline*.

---

### 2.5 Event-Triggered Online Learning
- **Citation:** Umlauft, J., & Hirche, S. (2020). *Feedback Linearization Based on Gaussian Processes with Event-Triggered Online Learning*. IEEE Transactions on Automatic Control, 65(10), 4154–4169. DOI: [10.1109/TAC.2019.2958840](https://doi.org/10.1109/TAC.2019.2958840).
- **Relevant Principle:** In online nonparametric Gaussian Process modeling, adding every new observation to the kernel dictionary causes $\mathcal{O}(N^3)$ computational explosion. Umlauft & Hirche introduce an event-triggered trigger condition based on GP predictive variance and state trajectory error to selectively query the high-cost update mechanism only when model uncertainty breaches a safety bound.
- **Epistemic Classification:** `CONCEPTUAL_ANALOGY`.
- **Methodological Boundary:** This establishes academic precedent for selective learning trigger design, but provides no formal guarantees for LEBRE's discrete delay and recurrent multi-objective arbitration.

---

## 3. Scientific Invariants and Hypotheses

### 3.1 Non-Superiority A Priori
We explicitly do **not** claim that event-triggered scheduling ($S_3$) is inherently superior to simple periodic scheduling ($S_2$). A periodic schedule provides uniform, predictable sampling without risk of "change blindness." An event-triggered schedule concentrates compute at points of innovation, but risks false alarms or missed quiet transitions. Determining which schedule dominates under matched computational budgets is an empirical scientific question.

### 3.2 Core Hypotheses
1. **$H_{\text{RESOURCE}}$ (Compute Ceiling Recovery):**  
   Budgeted shadow scheduling ($S_2$ and/or $S_3$) can reduce mean total online floating-point compute to $\le 100 \text{ FLOPs/step}$ across the 14-task benchmark while accounting for all sentinel and heartbeat overheads.
2. **$H_{\text{PREDICTIVE}}$ (Non-Inferiority):**  
   The aggregate NMSE under the selected budgeted scheduler is non-inferior to continuous shadow exploration ($S_0$) within a one-sided practical margin of $\Delta_{\text{tol}} \le +0.0100$ at family $\alpha = 0.05$.
3. **$H_{\text{EVENT}}$ (Adaptive Trigger Utility):**  
   Under comparable total online compute budgets, event-triggered scheduling ($S_3$) provides lower post-change regret and shorter structural recovery latency than uniform periodic scheduling ($S_2$) during non-stationary regime transitions ($I_{11}$–$I_{14}$).
4. **$H_{\text{MEMORY}}$ (Memory Envelope Preservation):**  
   The state footprint of the scheduler satisfies the available physical memory allowance ($\le 40$ Bytes peak working memory), keeping the compacted architecture strictly within the $1,024$ Byte ceiling.
