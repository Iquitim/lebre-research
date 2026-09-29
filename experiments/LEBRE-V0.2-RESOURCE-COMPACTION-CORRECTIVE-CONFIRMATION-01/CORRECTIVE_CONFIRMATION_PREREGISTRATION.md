# Corrective Confirmatory Preregistration Document

**Preregistration ID:** `LEBRE-V0.2-CORRECTIVE-PREREG-01`  
**Timestamp:** `2026-09-20T13:00:00Z`  
**Parent Study:** `LEBRE-V0.2-RESOURCE-COMPACTION-01`  
**Status:** FROZEN AND SEALED PRIOR TO STOCHASTIC CONFIRMATORY RUNS  

---

## 1. Preregistration Commitments

We formally freeze the experimental design, source code specifications, seed cohorts, statistical hypotheses, and decision thresholds for study `LEBRE-V0.2-RESOURCE-COMPACTION-CORRECTIVE-CONFIRMATION-01`.

### 1.1 Invariants & Non-Negotiables
1. **Bitwise Codebase Immutability:** Canonical files in `src/` (37 files) and `tests/` (124 tests) remain 100% bitwise immutable.
2. **Milestone Boundary:** Milestone M3 remains unopened (`M3_STATUS = UNOPENED`).
3. **No Novelty Claims:** `NOVELTY_CLAIM_READY = NO`.
4. **Single-Difference Invariant:** The ONLY intentional behavioral difference between $C_0$ and $C_1$ is `corr_grid` storage dtype (`np.float32` vs `np.float16`).
5. **Canonical Scaler Parity:** Both arms execute line 559 `self.scaler.update(x_raw, self.live_res)` on every timestep.
6. **Zero Post-Hoc Tuning:** Learning rates ($\mu=0.08, \eta=0.05$), probing schedule ($M=2$), and tolerance thresholds ($\theta_{\text{tol}}=0.015$) remain bitwise identical to preregistration.

---

## 2. Frozen Seed Allocations

A comprehensive repository audit confirmed that seeds `1501..1540` have never been used in any prior LEBRE study or experiment.

- **DEV Cohort (Unsealed):** Seeds `1501, 1502, 1503, 1504, 1505, 1506, 1507, 1508, 1509, 1510` ($N=10$).
  *Scope:* Used exclusively for pipeline verification, assertion checks, instrumentation sanity, and numerical diagnostics.
- **FINAL Cohort (Confirmatory Sealed):** Seeds `1511` through `1540` ($N=30$ independent seeds).
  *Scope:* Executed exactly once. All confirmatory inferential statistics, TOST tests, and figures are computed exclusively on this cohort.

---

## 3. Preregistered Statistical Hypotheses & Equivalence Margins

### Hypothesis H1: Aggregate Predictive Equivalence
- **Null Hypothesis ($H_{0,1}$):** Storing `corr_grid` in FP16 alters mean aggregate benchmark NMSE by more than $\Delta = \pm 0.0100$.
- **Alternative Hypothesis ($H_{1,1}$):** $|\bar{\Delta}_{\text{NMSE}}| < 0.0100$.
- **Statistical Test:** Two One-Sided Tests (TOST) on paired seed averages ($N=30$, $\alpha=0.05$).

### Hypothesis H2: Delay Regime Predictive Equivalence
- **Equivalence Margin:** Pure delay tasks ($I_3, I_4, I_5$) mean NMSE difference within $\pm 0.0150$.

### Hypothesis H3: Discrete Lag Support Recovery Preservation
- **Equivalence Margin:** Exact lag support recovery $F_1$ score on $I_3$ and $I_4$ within $\pm 0.0500$.

### Hypothesis H4: Arbitration Co-Activation Stability
- **Equivalence Margin:** Redundant stream $I_{10}$ dual active fraction (`frac_both`) difference within $\pm 0.0200$.

### Hypothesis H5: Regime Tracking Latency Preservation
- **Equivalence Margin:** Median discovery and retirement latencies on switching tasks ($I_{11}, I_{12}, I_{13}$) within $\pm 50.0$ steps.

### Hypothesis H6: Deterministic Physical Memory Reduction
- **Exact Criterion:** Measured `corr_grid` persistent memory footprint decreases by exactly $330.0$ Bytes ($660.0 \to 330.0$ Bytes), reducing total persistent capacity from $1,306$ Bytes to $976$ Bytes.

---

## 4. Execution Plan & Sign-Off

The confirmatory simulation script `scratch/run_v02_corrective_confirmation.py` will execute the deterministic parity check first, followed by the DEV cohort, and finally the sealed 840 confirmatory runs.
