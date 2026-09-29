# K=2 Concurrent Resource Accounting Decision Deliverable

**Stage:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Ceiling Target:** Mean Total Floating-Point Operations $\le 100.0\text{ FP/step}$.  
**Engineering Tolerance:** Near-miss interval defined as $100.0 < \text{Mean Total FP} \le 101.0\text{ FP/step}$.  
**Sample Cohort:** $N = 30$ fresh seeds ($1941..1970$), 14 tasks (420 streams per model).

---

## 1. Resource Accounting Summary

| Model Arm | Mean Total FP/step | Mean Shadow FP/step | Mean Live FP/step | Mean Int Ops/step | Mean Bytes Moved/step |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$C_0$ (Parent, $K=1$)** | `111.236` | `35.552` | `75.684` | `22.875` | `343.003` |
| **$C_2$ (Candidate, $K=2$)** | `101.023` | `26.540` | `74.483` | `23.569` | `329.022` |
| **Net Difference ($\Delta$)** | **`-10.213`** | **`-9.012`** | **`-1.201`** | **`+0.694`** | **`-13.981`** |
| **Percent Reduction** | **`-9.18%`** | — | — | — | — |

---

## 2. Resource Gate Ruling

> [!NOTE]
> **RESOURCE CLASSIFICATION: `OVER_BUDGET`**
> 
> - Strict $\le 100.0\text{ FP/step}$ Gate: **FAIL** (Observed: `101.023\text{ FP/step}`).
> - Engineering Tolerance $\le 101.0\text{ FP/step}$: **FAIL**.
> 
> Decimating recurrent forward propagation from every step to every second step removes exactly $17.000\text{ FP/step}$ from recurrent forward compute ($34.0 \to 17.0\text{ FP/step}$).
> The remaining total of **`101.023\text{ FP/step}`** leaves an unclosed deficit of **`1.023\text{ FP/step}`** against the strict 100.0 FP ceiling.
> In accordance with preregistration governance, this is strictly recorded as an **`OVER_BUDGET`**, preserving transparent separation between predictive validity and compute closure.
