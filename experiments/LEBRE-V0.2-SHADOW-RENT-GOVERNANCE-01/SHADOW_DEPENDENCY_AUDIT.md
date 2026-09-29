# Forensic Dependency & Removability Audit: Shadow-Path Operations

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** Operational Classification, Theoretical Minimum FLOP Floor, and Feasibility Verification  
**Author:** Independent Skeptical Senior Researcher  
**Status:** PHASE 0 GATE PASS  

---

## 1. Audit Scope & Invariant Principles

In accordance with Sections 6, 7, and 8 of the study charter, this audit performs an exhaustive line-by-line decomposition of the canonical LEBRE execution graph (`step()` method). Every computational step is strictly categorized into exactly one of five mutually exclusive functional classes:

1. `LIVE_REQUIRED`: Operations directly required to generate the current prequential prediction $\hat{y}_t$, compute the prequential loss $\ell_t$, or adapt active model components (scaler, base linear weights, active discrete taps, active recurrent weights). **Under no circumstances may any operation in this class be skipped or duty-cycled.**
2. `SHARED_REQUIRED`: State management infrastructure utilized by both live and shadow paths (circular ring buffer writes, memory pointer increments). Cannot be skipped when shadow sleeps.
3. `LIFECYCLE_REQUIRED`: Mandatory governance logic responsible for auditing active component health (leave-one-out tap retention evaluation, eviction checks, scheduler sentinels). Must execute at every timestep.
4. `SHADOW_REMOVABLE`: Speculative, counterfactual, or exploratory operations whose sole purpose is to evaluate candidate hypotheses, maintain shadow representations, update background correlation statistics, or arbitrate promotions into the active set. **These operations are genuine shadow rent and may be safely put to sleep.**
5. `BOOKKEEPING_REQUIRED`: Diagnostic counters, step tracking, and validation logging that incur zero floating-point FLOPs.

---

## 2. Operational Breakdown & Classification Matrix

The complete execution graph is partitioned in [SHADOW_OPERATION_LEDGER.csv](file:///d:/Projetos/Codinome%20Lebre/experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/SHADOW_OPERATION_LEDGER.csv) across 31 discrete operations. The summary by functional category is:

| Category | Operation Count | Per-Step FP FLOP Range | Mean Benchmark FP FLOPs | Primary Computational Components |
| :--- | :--- | :--- | :--- | :--- |
| **LIVE_REQUIRED** | 8 | $58.0$ – $114.5$ | **$77.8$ FLOPs** | Scaler transform, base predict/update, active tap predict/update, active rec forward/update, scaler update |
| **SHARED_REQUIRED** | 2 | $0.0$ | **$0.0$ FLOPs** | History buffer circular write, live delay queries |
| **LIFECYCLE_REQUIRED**| 5 | $2.0$ – $26.0$ | **$5.4$ FLOPs** | Tap leave-one-out gain EMA, eviction checks, Page-Hinkley sentinel |
| **SHADOW_REMOVABLE** | 12 | $64.0$ – $92.0$ | **$86.5$ FLOPs** | Counterfactual losses, gain EMAs, shadow rec forward/update/evidence, provisional candidate updates, 2-probe grid updates |
| **BOOKKEEPING_REQUIRED**| 4 | $0.0$ | **$0.0$ FLOPs** | Timestep counter, dual occupancy trackers, state flags |

---

## 3. Strict Removability Verification (Section 7 Compliance)

Section 7 explicitly dictates:
> *A computation may be duty-cycled only if skipping it does NOT alter: current live prediction, already-active tap updates, already-active recurrent updates, mandatory retention / eviction semantics, causal scaler updates, history-buffer updates, base-predictor learning.*

We mathematically verify that when `SHADOW_REMOVABLE` is put to sleep:
1. **Live Prediction Invariance:** $\hat{y}_t = \mathbf{w}_{\text{base}}^T \tilde{\mathbf{x}}_t + \sum_{k \in \mathcal{K}_{\text{live}}} w_k \tilde{x}_{t-k} + y_{\text{rec, live}}$. Every term is computed exclusively from live parameters and active history queries. Skipping shadow candidate predictions ($P_{\text{BASE\_D}}, P_{\text{BASE\_R}}$) has zero effect on $\hat{y}_t$.
2. **Active Filter Adaptation Invariance:** Active tap weights update via $w_k \leftarrow w_k + \mu e_{\text{live}} \tilde{x}_{t-k}$. The error $e_{\text{live}} = y_t - \hat{y}_t$ depends only on the live prediction. Base weights update via normalized LMS using $y_t - y_{\text{base}}$. Neither update accesses any shadow gain, candidate weight, or correlation grid cell.
3. **Active Retention / Eviction Invariance:** Tap eviction is governed by leave-one-out error: $e_{\text{without}} = y_t - (\hat{y}_t - w_k \tilde{x}_{t-k})$, updating tap evidence $R_k$. This calculation is classified as `LIFECYCLE_REQUIRED` and continues running every step. Hence, existing active taps can still be evicted during sleep if they cease to contribute.
4. **Causal Scaler Invariance:** `scaler.transform()` and `scaler.update()` are classified as `LIVE_REQUIRED` and execute on every timestep.
5. **No State Pollution:** While sleeping, shadow learner weights ($\mathbf{w}_{\text{shadow\_rec}}, \mathbf{w}_{\text{cand}}$) and correlation grid cells are frozen. No pseudo-observations, zeroes, or interpolated gains are fed into the shadow EMAs. Shadow exposure counters increment only when real shadow updates take place.

---

## 4. Analytical Feasibility Check (Section 8 Gate)

Using the sealed baseline metrics from `CORRECTED_SHADOW_RENT_BASELINE.json`:

$$\begin{aligned}
F_{\text{live}} &= 81.165 \text{ FP FLOPs/step} \\
F_{\text{shadow\_removable}} &= 86.533 \text{ FP FLOPs/step} \\
F_{\text{housekeeping}} &= F_{\text{scheduler}} \le 2.000 \text{ FP FLOPs/step}
\end{aligned}$$

The theoretical minimum online floating-point compute floor is:
$$F_{\text{min}} = F_{\text{live}} + F_{\text{housekeeping}} = 81.165 + 2.000 = 83.165 \text{ FP FLOPs/step}$$

Evaluating the Section 8 Feasibility Gate:
$$F_{\text{min}} = 83.165 \le 100.0 \implies \mathbf{PASS}$$

$$\text{SHADOW\_ONLY\_100FLOP\_RECOVERY\_THEORETICALLY\_FEASIBLE} = \mathbf{YES}$$

### Available Shadow Budget & Permissible Duty Fraction
With an upper limit of $100.0 \text{ FLOPs/step}$, the maximum allowable average shadow compute is:
$$\Delta F_{\text{shadow\_budget}} = 100.0 - F_{\text{min}} = 100.0 - 83.165 = 16.835 \text{ FP FLOPs/step}$$

The maximum permissible continuous shadow duty fraction $\delta_{\text{max}}$ is:
$$\delta_{\text{max}} = \frac{\Delta F_{\text{shadow\_budget}}}{F_{\text{shadow\_removable}}} = \frac{16.835}{86.533} \approx 0.1945 \quad (19.45\%)$$

This rigorously proves that any valid scheduler must achieve an average shadow duty cycle of $\le 19.45\%$ over the benchmark stream.
