# Experimental Protocol: Corrective Confirmatory Evaluation of Resource Compaction

**Protocol ID:** `LEBRE-V0.2-CORRECTIVE-CONFIRMATION-PROTOCOL-01`  
**Parent Studies:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`, `LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01`  
**Target Milestone:** Milestone M2.5 (Corrective Confirmatory Resource Baselines)  
**Governance Standard:** Confirmatory Empirical Audit (Simmons et al. 2011; Nosek et al. 2018)  
**Status:** FROZEN PRIOR TO CONFIRMATORY EXECUTION  

---

## 1. Context & Scientific Objective

Following the discovery of the inadvertent omission of `scaler.update` in the compaction runner of study `LEBRE-V0.2-RESOURCE-COMPACTION-01`, this protocol specifies the experimental and statistical procedures required to reconfirm FP16 correlation-grid compaction inside the exact canonical $T_3$ execution pipeline.

The scientific objective is to determine:
> **Whether storing the background correlation grid `corr_grid` in IEEE 754 half precision (`float16`) with transient single-precision (`float32`) arithmetic introduces any statistically significant degradation in predictive performance (NMSE), structural support recovery, or arbitration dynamics relative to full single precision (`float32`) across the 14 benchmark tasks under canonical causal scaling.**

---

## 2. Experimental Design & Invariants

### 2.1 Experimental Arms
- **$C_0$ (`C0_CANONICAL_FP32`):** Canonical $T_3$ topology with `corr_grid` stored in `float32` ($660$ Bytes). Causal scaler updated every timestep ($4D = 20.0$ FLOPs/step).
- **$C_1$ (`C1_CANONICAL_FP16`):** Canonical $T_3$ topology with `corr_grid` stored in `float16` ($330$ Bytes). Transient update math executed in `float32`, rounded back to `float16`. Causal scaler updated identically.

### 2.2 Canonical Reference Parity Gate (Pre-Execution)
Before running stochastic experiments, $C_0$ must pass a deterministic parity test against the previously sealed canonical `IntegratedLEBREModel(topology="T3")` across all 14 benchmark tasks for 6,000 steps:
- **Requirement:** 100% Bitwise identity on `y_hat`, `loss`, `scaler.mean`, `scaler.var`, `active_taps`, `provisional_cands`, `corr_grid`, and resource counters.
- Discrepancy threshold: 0 mismatches.

### 2.3 Cohort Structure & Fresh Seeds
- **DEV Cohort:** Seeds `1501..1510` ($N=10$ seeds $\times$ 14 tasks $\times$ 2 arms = 140 runs). Used strictly for numerical sanity, assertion verification, and counter validation.
- **FINAL Confirmatory Cohort:** Seeds `1511..1540` ($N=30$ independent seeds $\times$ 14 tasks $\times$ 2 arms = 840 runs). Executed exactly once.

---

## 3. Preregistered Equivalence Margins & Hypotheses

All margins are frozen directly from the parent study prior to confirmatory execution:

| Metric | Target Scope | Equivalence Bound ($\pm \Delta_{\text{tol}}$) | Statistical Test | Alpha |
| :--- | :--- | :--- | :--- | :--- |
| **Aggregate Benchmark NMSE** | All 14 Tasks | $\pm 0.0100$ | Paired Two One-Sided Tests (TOST) | $\alpha = 0.05$ |
| **Pure Delay NMSE** | $I_3, I_4, I_5$ | $\pm 0.0150$ | Paired TOST | $\alpha = 0.05$ |
| **Lag Support Recovery F1** | $I_3, I_4$ | $\pm 0.0500$ | Paired TOST | $\alpha = 0.05$ |
| **Arbitration Co-Activation** | $I_{10}$ (`frac_both`) | $\pm 0.0200$ | Paired Difference Bound | $\alpha = 0.05$ |
| **Hybrid Conditional Gains** | $I_9$ ($G_{D\|BR}, G_{R\|BD}$) | $\pm 0.0050$ | Paired Difference Bound | $\alpha = 0.05$ |
| **Regime Switch Latency** | $I_{11}, I_{12}, I_{13}$ | $\pm 50.0$ steps | Paired Difference Bound | $\alpha = 0.05$ |

### 3.1 Unit of Statistical Inference
To avoid pseudoreplication ($N=420$ pooling non-independent tasks), the primary inferential sampling unit for the aggregate benchmark is the **Independent Seed ($N=30$)**, where each seed's observation is the mean NMSE averaged across the 14 benchmark tasks:
$$\bar{Y}_{s, C} = \frac{1}{14} \sum_{i=1}^{14} \text{NMSE}_{i, s, C}$$
$$\Delta_s = \bar{Y}_{s, C_1} - \bar{Y}_{s, C_0}$$

---

## 4. Resource Governance & Accounting Invariants

1. **Live Floating-Point Compute:** Live compute must explicitly account for online causal scaling:
   $$\text{LIVE\_FP}_{\text{step}} = \text{Base} + \text{Taps} + \text{Recurrent} + \text{Scaler Update} (20 \text{ FLOPs})$$
2. **Shadow Floating-Point Compute:** Shadow exploration is un-optimized in this milestone ($M=2$ grid probing, candidate updates, shadow recurrent filtering, counterfactual losses).
3. **Integer Operations:** Explicitly account for FP16 conversion/cast overhead: $2 \times M = 4$ cast operations per step in $C_1$.
4. **Memory Ledgers:** Formally report:
   - `OCCUPIED_PERSISTENT_BYTES`: Dynamic heap footprint.
   - `ALLOCATED_CAPACITY_BYTES`: Preallocated memory pool ($1,306$ B for $C_0$, $976$ B for $C_1$).
   - `TRANSIENT_WORKSPACE_BYTES`: Stack workspace during execution ($4$ B for $C_0$, $8$ B for $C_1$).
   - `PEAK_WORKING_BYTES`: Maximum combined working memory.

---

## 5. Decision Rules

- **EQUIVALENCE_CONFIRMED:** If $p_{\text{TOST}} < 0.05$ for Aggregate NMSE within $\pm 0.0100$, pure delay NMSE within $\pm 0.0150$, support F1 within $\pm 0.0500$, and zero numerical anomalies (NaN/Inf/stagnation) are observed.
- **EQUIVALENCE_REJECTED:** If any confirmatory 90% confidence interval falls outside the preregistered equivalence margins.
