# Locality Diagnostic Gate Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Diagnostic Gate Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **CHRONOLOGY & AUDIT METHOD VALIDATED**  

---

## 1. Chronology Verification

We audited whether the prerequisite conditions for coarse-to-fine hierarchical search eligibility were preregistered prior to empirical inspection:
1. **Preregistration Timing:** In `CORRELATION_SEARCH_PREREGISTRATION.md` (Section 1, Hypothesis 2) and `CORRELATION_SEARCH_PROTOCOL.md` (Section 19), the criteria were formally specified:
   - Rank correlation $r(\text{score}(k), \text{score}(k \pm 1)) \ge 0.60$;
   - Neighborhood recall: coarse anchor within $\pm 1$ of true delay captures $\ge 70\%$ of peak magnitude in $\ge 70\%$ of regimes.
2. **Deterministic Gate Rule:** Both documents explicitly stated:
   `If either condition fails, COARSE_TO_FINE_ELIGIBLE = NO, and C2 is formally disqualified.`
3. **Execution Sequence:**
   `run_phase0_phase1_audit.py` was executed after protocol freezing, writing `LAG_SCORE_LOCALITY_AUDIT.csv`, `LAG_SCORE_LOCALITY_REPORT.md`, and `HIERARCHICAL_SEARCH_ELIGIBILITY.md` with the formal rejection.
4. **Audit Finding:** The diagnostic gate was **frozen before inspection** and executed with complete governance compliance.

---

## 2. Empirical Findings vs. Frozen Thresholds

Audited across 4,915 active delay instances on DEV streams ($N=10$, tasks $I_3, I_4, I_5, I_8, I_9, I_{11..14}$):

| Locality Diagnostic Metric | Frozen Threshold | Measured Value | Gate Verdict |
| :--- | :--- | :--- | :--- |
| **Neighbor Rank Correlation ($r$)** | $\ge 0.60$ | **$0.2176$** | **FAIL** |
| **Mean Neighbor Recall Ratio** | $\ge 0.70$ ($70.0\%$) | **$0.2650$ ($26.5\%$)** | **FAIL** |
| **Regimes Capturing $\ge 70\%$ of Peak**| $\ge 70.0\%$ | **$3.64\%$** | **FAIL** |
| **Coarse-to-Fine Eligibility Decision**| Mandatory Pass | **`COARSE_TO_FINE_ELIGIBLE = NO`** | **DISQUALIFIED** |

---

## 3. Epistemic Status

- **Status:** **`NOT_SUPPORTED`**
- The empirical data conclusively reject lag-score locality for discrete delays in LEBRE streaming benchmarks.
- The decision to exclude Candidate family $C_2$ from confirmatory evaluation adhered strictly to the preregistered decision rule.
