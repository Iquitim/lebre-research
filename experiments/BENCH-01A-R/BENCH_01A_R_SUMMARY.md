# BENCH-01A-R: Surgical Benchmark Protocol Correction & Re-Hash — Final Summary

**Document ID:** BENCH-01A-R-SUMMARY  
**Auditor:** Benchmark Methodology Auditor & Reproducibility Reviewer  
**Date:** September 19, 2026  
**Status:** SURGICAL CORRECTIONS COMPLETE — PROTOCOL RE-LOCKED  
**Governing Standard:** Sections 59–73, 79 of Protocol BENCH-01A-R  

---

## 1. Executive Summary & Formal Verdicts (Sections 63–70)

The four targeted methodological corrections mandated for BENCH-01A have been fully executed without altering architecture specifications, modifying code, expanding search spaces, or executing competitive models:

```
========================================================================================
FINAL CORRECTION VERDICTS:
  ELEC2_PROTOCOL           = PASS_WITH_RELABEL
  RESOURCE_MATCHING        = PASS_AFTER_CORRECTION
  DIVERGENCE_POLICY        = PASS_AFTER_CORRECTION
  MUSE_RNN_COMPATIBILITY   = MINIMAL_ADAPTATION

OVERALL AUDIT STATUS:
  BENCH_01A_R_STATUS       = BENCH_01A_R_CORRECTIONS_COMPLETE
  BENCHMARK_FAIRNESS       = PASS
  TEMPORAL_LEAKAGE_AUDIT   = PASS
  RESOURCE_ACCOUNTING_READY= YES
  REPRODUCIBILITY_READY    = YES
  BENCH_01B_READY          = YES (AUTHORIZED FOR REVIEW; COMPETITIVE RUN UNOPENED)
========================================================================================
```

---

## 2. Table A: ELEC2 Dataset Audit Summary (Section 59)

| Canonical Dataset | Canonical Task | Canonical Target | BENCH Task | Derived? | Future-Safe? | Final Benchmark Label | Protocol Decision |
| :--- | :--- | :---: | :--- | :---: | :---: | :--- | :---: |
| **ELEC2 (Harries 1999)** | Streaming Binary Classification | `class` (`UP`/`DOWN`) | One-step continuous spot price forecasting ($/MWh) | **YES** (Derived) | **YES** (Causal) | `NSW_ELECTRICITY_DERIVED_REGRESSION` | **`PASS_WITH_RELABEL`** |

*Qualification Note:* In all active specifications, this task is designated with the formal metadata:  
`TASK_STATUS = NONCANONICAL_DERIVED_REGRESSION_TASK`. It is never referred to as canonical ELEC2 classification.

---

## 3. Table B: Architecture-Neutral Resource Matching Envelopes (Section 60)

Universal resource matching in Regime R2 is strictly decoupled from Track B's internal structural parameters ($K \le 10, N \le 1$) and governed by observable physical envelopes:  
**`R2-FLOP Ceiling`:** $\le 100\text{ FLOPs/step}$; **`R2-MEM Ceiling`:** $\le 1{,}024\text{ Bytes}$.

| Baseline | Natural Internal Capacity (R1) | Natural Mean FLOPs | Natural P95 FLOPs | Allocated Memory (Bytes) | Active Parameters | R2-FLOP Eligible ($\le 100$ FLOPs)? | R2-MEM Eligible ($\le 1024$ B)? | Architecture-Specific Constraint Applied? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Track B (Frozen)** | $K \le 10, N \le 1$ | 52.4 | 72.0 | 200 | 3–13 | **YES** | **YES** | **NO** |
| **B1: RZA-LMS** | $D$ linear taps | $6D + 1$ | $6D + 1$ | $8D + 64$ | $D$ | **CONDITIONAL** ($D \le 16$) | **YES** ($D \le 120$) | **NO** |
| **B2: CCN** | $C \in \{1, 2\}$ columns | $4CD + 22C$ | $4CD + 22C$ | $16CD + 80$ | $C(D+3)$ | **CONDITIONAL** ($C=1, D \le 18$) | **YES** | **NO** |
| **B3: MUSE-RNN** | $N_t \in [1, 5]$ nodes | $2DN_t + 2N_t^2$ | Varies | $16DN_t + 128$ | $N_t(D+N_t)$ | **CONDITIONAL** (Tuned $N_t \le 2$) | **YES** ($N_t \le 4$) | **NO** |
| **B4: Minimal GRU** | $N = 1$ cell | $6D + 88$ | $6D + 88$ | $72 + 64$ | 9 | **CONDITIONAL** ($D \le 2$) | **YES** | **NO** |
| **B5: Online ESN** | $N_{\text{res}} = 20$ nodes | $\sim 2800$ | $\sim 2800$ | $\sim 3600$ | 20 | **NO (R1 Only)** | **NO (R1 Only)** | **NO** |
| **B6: Variable-Tap LMS** | $L_t \in [1, 20]$ taps | $2L_t + 1$ | $2L_{\max} + 1$ | $8L_{\max} + 64$ | $L_t$ | **YES** ($L_t \le 40$) | **YES** | **NO** |
| **B7: LRU Streaming** | $N = 1$ diagonal state | $4D + 12$ | $4D + 12$ | $16D + 64$ | $2D + 2$ | **YES** ($D \le 22$) | **YES** | **NO** |

*Verification:* Zero universal constraints on internal structural parameters ($K, N$, columns, nodes) are imposed.

---

## 4. Table C: Failure Handling & Divergence Reporting Matrix (Section 61)

The arbitrary $1.5\times$ penalty is completely excised. Algorithmic reliability and predictive performance are reported as independent dimensions:

| Execution Outcome | Predictive Reporting | Resource Reporting | Failure Flag | Suite Aggregation Rule |
| :--- | :--- | :--- | :--- | :--- |
| **Complete Run** | Full prequential MSE, MAE, NMSE computed over entire test segment ($t \in [0.30T, T]$). | Full mean FLOPs, P95 FLOPs, persistent memory, and wall-clock latency recorded. | `SUCCESS` | Included in primary predictive distributions and Pareto frontiers. |
| **Numerical Divergence** | Pre-divergence loss recorded with `CENSORED_AT_FAILURE` flag. Full-run loss marked `FAILED_RUN` ($+\infty$). | All FLOPs and runtime consumed prior to $t_{\text{fail}}$ fully accounted for. | `NUMERICAL_DIVERGENCE` | Excluded from complete-run MSE; scored as failed seed in Divergence Rate. |
| **Execution Exception** | Marked `FAILED_RUN` ($+\infty$). | Consumed FLOPs up to exception accounted for. | `RUNTIME_EXCEPTION` | Excluded from complete-run MSE; logged in Defect Manifest. |
| **Runtime Timeout** | Marked `FAILED_RUN` ($+\infty$). | All FLOPs and time consumed up to timeout accounted for. | `TIMEOUT_EXCEEDED` | Excluded from complete-run MSE; scored as computational failure. |

---

## 5. Table D: MUSE-RNN Task Compatibility Summary (Section 62)

| Original Task | Original Loss | Growth Rule | Pruning Rule | Classification-Specific Dependency | Regression Adaptation Needed | Adaptation Severity | Applicable Benchmark Tasks |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- |
| Data Stream Classification | Multi-Class Cross-Entropy / 0-1 Loss | Residual error exceeds sliding window: $e_t > \mu_e + 2\sigma_e$ | Outgoing weight norm below threshold: $\|w_{\text{out}, i}\| < \theta_{\text{prune}}$ | **NONE** (Statistical error monitor is label-agnostic) | Linear readout scalar $\hat{y} = w^\top h$; Squared error loss $e_t = y_t - \hat{y}_t$ | **`MINIMAL_ADAPTATION`** | All BENCH-01 regression streams (Block A & Block B) |

*Retention:* MUSE-RNN is retained as mandatory under the qualified label `B3_MUSE_RNN_MINIMAL_REGRESSION_ADAPTATION`.

---

## 6. Answers to Final Scientific Questions (Sections 71 & 72)

### Primary Scientific Question (Section 71):
> *"After these corrections, can the final benchmark compare methods without advantaging Track B through dataset redefinition, internal structural constraints, or artificial failure penalties?"*

**Answer:** **`YES`**.  
*Justification:*
1. The NSW electricity stream is explicitly qualified as a non-canonical derived continuous regression task;
2. Universal resource matching operates strictly on observable FLOP and memory envelopes, eliminating Track-B-specific structural constraints ($K \le 10, N \le 1$);
3. The arbitrary $1.5\times$ penalty is excised; failed runs are reported transparently via categorical divergence rates and penalized as incomplete ($+\infty$) without fabricating synthetic loss values.

### Second Scientific Question (Section 72):
> *"Is every deviation from a canonical dataset or baseline now explicitly labeled and justified?"*

**Answer:** **`YES`**.  
*Justification:* Every deviation is documented with explicit provenance metadata: `NSW_ELECTRICITY_DERIVED_REGRESSION` (`NONCANONICAL_DERIVED_REGRESSION_TASK`) and `MUSE_RNN_REGRESSION_MINIMAL_ADAPTATION`.

---

## 7. Cryptographic Hash Reconciliation Summary (Sections 52 & 53)

- **`BENCH_01_SPEC.md` SHA-256:**  
  `f516914da4d511e9ed58c2eb575d628bf3e01ebaab9f8bf63f9da0ebfe0e0c28`
- **`experiments/BENCH-01A/bench_01_locked_config.json` SHA-256:**  
  `cb0d696e3e2775afa802a5a037ddf58ad3887252e4ac302e62b7e6162d334f7a`

### 7.1 Chronological Stream Split Reconciliation (15/15/70)
- **Documented in Spec (`BENCH_01_SPEC.md` Sec 19):** 0%–15% Calibration ($0.15$), 15%–30% Validation ($0.15$), 30%–100% Test ($0.70$).
- **Encoded in Config (`bench_01_locked_config.json`):** `0.15` / `0.15` / `0.70`.
- **Methodological Selection:** Reconciled and confirmed at **`15 / 15 / 70`**. 15% calibration provides sufficient excitation cycles on short synthetic streams ($T=10{,}000$) to screen 16 baseline candidates without noisy selection transients; 15% validation provides adequate stability confirmation; and 70% test quarantines the majority of the stream for out-of-sample evaluation.
- **Automated Tests:** `tests/test_bench_01_protocol.py` explicitly asserts exact fractions `0.15`, `0.15`, and `0.70`.
- **Audit Reference:** [`experiments/BENCH-01A-R/SPLIT_RECONCILIATION_AUDIT.md`](file:///d:/Projetos/Codinome%20Lebre/experiments/BENCH-01A-R/SPLIT_RECONCILIATION_AUDIT.md).

---

## 8. Section 79 Hard Stop Compliance

- Competitive execution of BENCH-01B remains **UNOPENED**;
- Zero competitive results have been gathered or inspected;
- Track B architecture code in `src/` and specifications in `M1_SPEC.md` and `M2_SINGLE_STATE_SPEC.md` remain 100% frozen;
- Milestone M3 remains **UNOPENED**;
- No novelty claims or architecture names have been assigned;
- Awaiting explicit authorization for next steps.
