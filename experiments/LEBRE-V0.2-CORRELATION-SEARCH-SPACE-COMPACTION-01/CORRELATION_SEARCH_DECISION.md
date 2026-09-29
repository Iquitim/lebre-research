# Correlation Search Space Compaction Decision

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Phase 4 Governance Adjudication  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Final Governance Verdict:** **`CONDITIONALLY_SEALED_MULTIRATE_ENHANCEMENT`**  

---

## 1. Formal Hypotheses Adjudication Matrix

All hypotheses are evaluated against the sealed preregistration (`CORRELATION_SEARCH_PREREGISTRATION.md`) using confirmatory data from $N=30$ independent streams (Seeds $1811..1840$, 14 benchmark tasks, $2,520,000$ steps):

| Hypothesis ID | Pre-Declared Criterion | Empirical Result | Status | Epistemic Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **H1: Search Resource Reduction** | Search RAM $\le 200\text{ B}$, FP $\le 100\text{ FP/step}$ | RAM = $192\text{ B}$, Total FP = $110.82\text{ FP}$ | **PARTIALLY SUPPORTED** | RAM bound met; total FP constrained by live floor ($88.45\text{ FP}$) |
| **H2: Lag-Score Locality** | Rank corr $r \ge 0.60$, recall $\ge 70.0\%$ | $r = 0.2176$, recall = $26.50\%$ | **REJECTED** | Locality fails; Kronecker delta confirms coarse-to-fine disqualified |
| **H3: Non-Inferiority vs. $R_0$** | Upper $95\%$ CI of $\Delta\text{NMSE} < +0.0100$ | Mean $\Delta = +0.0130$, Upper CI = $+0.0194$ | **REJECTED** | Continuous reference $R_0$ retains slight predictive advantage |
| **H3b: Superiority vs. Multirate $R_1$**| $\Delta\text{NMSE} < 0$ vs. dense multirate | Mean $\Delta = -0.0114$ ($p = 4.2 \times 10^{-5}$) | **SUPPORTED** | $M_1^*$ decisively outperforms dense multirate reference |
| **H4: Pure-Lag Preservation** | $\Delta\text{NMSE} \le +0.0150$ on $I_3, I_4, I_5, I_8$ | Passed on $I_5 (+0.0070)$, $I_8 (-0.0024)$; Failed on $I_3, I_4$ | **PARTIALLY SUPPORTED** | Delays recovered, but decimation introduces small discovery lag |
| **H5: Switching Preservation** | Recovery latency $\Delta \le +50\text{ steps}$ on $I_{11..14}$ | Passed on $I_{13} (+6.1)$, $I_{14} (+18.9)$; Failed on $I_{11}, I_{12}$ | **PARTIALLY SUPPORTED** | Abrupt switches require more steps to refresh background queue |
| **H6: Anti-Starvation Guarantee**| Max silence $\le 80\text{ steps}$ across all cells | Max silence $= 80.00\text{ steps}$ (100% compliance) | **SUPPORTED** | Zero coordinates starved; circular exploration holds strictly |
| **H7: Dense Array Elimination** | Zero 160-cell arrays retained in RAM | Exactly 0 dense arrays allocated (FP16 RAM = 192 B) | **SUPPORTED** | Physical RAM footprint reduced by $63.6\% - 67.6\%$ |

---

## 2. Epistemic Syntheses and Forensic Insights

### 2.1 The Kronecker Delta Reality and Hierarchical Search Failure
Phase 1 auditing definitively resolved a longstanding theoretical question: Can discrete streaming time-delay search be conducted via hierarchical coarse-to-fine approximation?
- **Theoretical Finding:** In white-innovation streaming environments, cross-correlation with lagged target residuals forms a discrete Kronecker delta peak $\delta(k - k^*)$.
- **Empirical Finding:** Neighbors at $k^* \pm 1$ exhibit only baseline estimation noise ($r = 0.2176$, recall $= 26.5\%$).
- **Architectural Conclusion:** Coarse-to-fine search is structurally blind to discrete delays falling between coarse anchors, resulting in a disastrous $3.64\%$ capture rate and NMSE deterioration ($0.3563$ vs $0.3135$). Hierarchical search is **permanently rejected** for LEBRE discrete delay identification.

### 2.2 Superiority Over Dense Multirate ($R_1$)
While $M_1^*$ does not achieve statistical non-inferiority relative to the continuous baseline $R_0$ ($\Delta\text{NMSE} = +0.0130 > +0.0100$), it **statistically and decisively outperforms the dense multirate reference $R_1$** ($\Delta\text{NMSE} = -0.0114$, $t = -4.57$, $p = 4.2 \times 10^{-5}$).
- **Mechanism:** In $R_1$, probing all 160 cells uniformly produces a high rate of noise crossings (12,592 candidate births), wasting $1.45\text{ MFLOPs}$ on failed probations and injecting spurious weights into the arbitration pool.
- In $M_1^*$, restricting the search space to 32 active slots acts as an **epistemic low-pass filter**, slashing candidate births by $57.0\%$ and improving true delay promotion recall from $66.5\%$ to $76.3\%$.

---

## 3. Deployment and Seal Adjudication

```text
======================================================================
SEARCH SPACE COMPACTION SEAL VERDICT: CONDITIONALLY SEALED
======================================================================
1. Candidate M1* (Rotating Sparse Frontier: H=32, B=4) is adopted as
   the frozen delay search mechanism for LEBRE v0.2.
2. Dense 160-cell correlation state matrices are permanently deprecated
   and purged from the v0.2 runtime architecture.
3. Hierarchical coarse-to-fine search (C2) is disqualified and permanently
   excluded from the canonical codebase.
4. Non-inferiority vs continuous R0 is bounded at Delta NMSE = +0.0130;
   users requiring sub-0.0100 accuracy must deploy R0 with continuous compute.
======================================================================
```
