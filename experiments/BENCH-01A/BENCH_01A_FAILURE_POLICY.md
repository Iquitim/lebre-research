# BENCH-01A: Failure Handling, Numerical Stability & Anomaly Policy

**Document ID:** BENCH-01A-FAILURE  
**Auditor:** Quality Assurance Officer & Benchmark Governance Auditor  
**Date:** September 19, 2026  
**Status:** PROTOCOL LOCKED — DISQUALIFICATION RULES FIXED  
**Governing Standard:** Sections 143–147, 183–186, 216 of BENCH-01A Protocol  

---

## 1. Governance Principles for Execution Anomalies

In experimental machine learning benchmarks, models frequently encounter numerical instabilities (overflows, gradient explosions, NaN losses). In biased benchmarks, failing configurations are often quietly replaced, retuned, or discarded without documentation.

Per Sections 143–147 and 183–186:
1. **Divergence is Scientific Data (Section 147):** A configuration that diverges on an evaluation stream has failed. That failure is logged as empirical evidence of hyperparameter sensitivity.
2. **No Post-Hoc Architectural Patching (Section 184):** If Track B fails on a real-world stream (e.g., suffers premature eviction, misses a critical lag, or accumulates high regret), **zero modifications to Track B are permitted**. The failure must be recorded and reported as an authentic boundary of the frozen architecture.
3. **Negative Results are Publishable Research (Section 183):** If standard baselines (e.g., RZA-LMS or Minimal GRU) outperform Track B in both predictive accuracy and compute efficiency, this falsifies the practical-value hypothesis and constitutes valid scientific output.

---

## 2. Standardized Numerical Stability Criteria (Sections 145 & 146)

Every model executed in BENCH-01 is instrumented with identical, universal finite-value checks:

```python
# Universal Causal Finite-Value Instrument
if not np.isfinite(y_hat_t):
    record_anomaly(step=t, model=model_id, error="PREDICTION_NAN_OR_INF")
    y_hat_t = 0.0  # Safe fallback to prevent cascading runtime crash
```

### Anomaly Thresholds:
1. **Explosion Threshold:** If $|\hat{y}_t| > 10^4$ on standardized data, the step is logged as `UNBOUNDED_PREDICTION_ERROR`.
2. **Gradient Divergence:** If any weight update contains $\text{NaN}$ or $\pm\infty$, the model is flagged as `NUMERICAL_DIVERGENCE`.

---

## 3. Disqualification & Failure Logging Protocol (Section 144)

If any baseline or Track-B run triggers numerical divergence:
1. The run is **NOT quietly deleted or replaced**.
2. A structured `FAILURE_REPORT.json` is generated recording:
   - Model identifier and hyperparameter configuration;
   - Dataset name and random seed;
   - Time step $t$ at which divergence occurred;
3. The run is formally categorized as `FAILED_RUN` (`NUMERICAL_DIVERGENCE`). The arbitrary $1.5\times$ penalty is excised. Primary predictive metrics (MSE, MAE) are aggregated strictly over valid, complete runs. In ranking summaries requiring full completion, failed runs are scored as `FAILED_RUN` ($+\infty$). Algorithmic reliability is reported via explicit `DIVERGENCE_RATE`. All computation consumed prior to failure is fully accounted for.

---

## 4. Software Defect & Bug Policy (Sections 185 & 186)

If a genuine software implementation bug (e.g., array index out-of-bounds, incorrect sign in a baseline formula) is discovered after execution begins:
1. **Immediate Halt:** The affected benchmark suite is immediately halted.
2. **Audit Documentation:** The defect is documented in `experiments/BENCH-01A/DEFECT_LOG.md` detailing the root cause.
3. **Symmetric Invalidation (Section 185):** All previously executed runs for that model and affected tasks are formally invalidated.
4. **Strict Prohibition Against Selective Reruns (Section 186):**  
   > *"Never rerun only unfavorable seeds."*  
   The entire test suite across all 30 seeds must be re-executed from scratch under identical conditions.
