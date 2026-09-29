# ABLATION_LOG.md

Log of systematic ablations and structural comparisons.

| Experiment | Component / Variant | Baseline Compared | Delta Metric | Conclusion |
| :--- | :--- | :--- | :--- | :--- |
| **EXP-0001** | Model C (Sparse NLMS + Random Probe) | Model A (Dense NLMS) | MSE $\Delta = +11.80$, Recall $\Delta = -100\%$, FLOPs $-91.4\%$ | **REMOVE**: Random probing under zero slack fails to acquire signal. |
| **EXP-0001** | Model D (Sparse NLMS + Round Robin) | Model A (Dense NLMS) | MSE $\Delta = +9.60$, Recall $\Delta = -84\%$, FLOPs $-91.4\%$ | **REMOVE (Current Variant)**: Systematic scanning is slightly better than random (16% vs 0%), but zero-slack swap mechanism is fundamentally broken. |

