# EXP-0001c: Diagnostic Answers to Required Questions (Section 45)

### 1. Why is B3 still far worse than Dense despite high final recall?
**Answer**: Because final recall (measured at $t=2000$) is a point estimate that masks temporal latency. Across Regime 2, full true support was active for only **21.3% of the steps**. In the remaining 78.7% of steps, at least one true feature was omitted. Each omitted feature carries an energy of beta^2 ≈ 1.0 - 2.5, dragging the average MSE up to ~0.74.

### 2. How much error comes from incomplete support?
**Answer**: **Approximately 65.8% of the total predictive error** comes directly from omitted feature energy (E_omit = 0.4860). When support is incomplete, MSE averages **1.8319**.

### 3. How much remains when all true features are active?
**Answer**: When all 5 true features are present in the active set, MSE drops to **0.0972** (and drops to **0.0139** in seeds that reached settled full support). In seeds 789 and 1024, B3 directly outperformed the Dense NLMS baseline.

### 4. Do extra buffer features materially pollute prediction?
**Answer**: **NO**. The Top-5 readout (C1) only reduced MSE from 0.7391 to 0.6764 (an 8.5% difference). False weight energy (E_false = 0.1257) is small because NLMS naturally contracts noise weights toward zero.

### 5. Does structural churn prevent convergence?
**Answer**: **NO**. Variant C3 (freezing structure after full acquisition) yielded R2 MSE of 0.7370, virtually identical to B3 (0.7391). Once true features are acquired, B3 holds them stably.

### 6. Can the sparse NLMS itself reach near-Dense error under oracle support?
**Answer**: **YES, IT BEATS DENSE**. Variant C4 (Oracle Support NLMS) achieves R2 MSE of **0.0148**, which is **2.3x lower error than Dense NLMS (0.0339)** at **18.8x lower compute** (32 FLOPs vs 602 FLOPs).

### 7. What is the single smallest next intervention?
**Answer**: **Accelerate the acquisition latency of the 5th true feature without increasing total compute**. Specifically: when a sudden surge in residual error indicates an environmental shift, temporarily concentrate candidate probing or allow error-adaptive probe allocation, rather than static round-robin scanning.
