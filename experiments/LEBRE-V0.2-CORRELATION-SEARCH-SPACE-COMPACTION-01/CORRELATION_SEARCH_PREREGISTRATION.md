# Preregistration Document: Correlation Search Space Compaction

**Study Identifier:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2, Non-Canonical T3)  
**Author:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Status:** FROZEN EXPERIMENTAL PREREGISTRATION  

---

## 1. Primary Preregistered Hypotheses

### Hypothesis 1: Search-Space Compaction Feasibility (Primary Inferential)
A bounded rotating correlation-search frontier of capacity $H \in \{16, 32\}$ hypotheses ($< 20\%$ of the ambient $165$-cell grid) combined with a round-robin exploration queue $B \in \{2, 4\}$ achieves predictive non-inferiority relative to the canonical continuous reference $R_0$:
$$\bar{\Delta}_{\text{NMSE}} + t_{0.95, N-1} \cdot \text{SE}(\Delta_{\text{NMSE}}) < +0.0100 \quad (N=30, \text{seeds } 1811..1840)$$
while reducing mean total online compute below the project ceiling:
$$\bar{\mathcal{C}}_{\text{total}} \le 100.00\text{ FP/step}$$

### Hypothesis 2: Lag-Score Locality Prerequisite (Diagnostic Gate)
Coarse-to-fine hierarchical search ($C_2$) is eligible for deployable candidate consideration **if and only if** the DEV lag-score locality audit demonstrates:
1. **Neighbor Rank Correlation:** $r(\text{score}(k), \text{score}(k \pm 1)) \ge 0.60$ across true temporal regimes;
2. **True-Lag Neighborhood Recall:** A coarse anchor within $\pm 1$ step of a true delay captures $\ge 70\%$ of the peak correlation magnitude.
If either condition fails, `COARSE_TO_FINE_ELIGIBLE = NO`, and $C_2$ is formally disqualified prior to candidate freezing.

### Hypothesis 3: Descendant Compute Decomposition (Mechanistic)
Search-space compaction saves compute through two distinct causal mechanisms:
1. **Direct Savings:** Fewer correlation inner products per stream step;
2. **Indirect Savings:** Substantial reduction in spurious candidate births ($|\rho| > 0.20$), thereby preventing expensive counterfactual probation observations ($K_{\text{obs}}=5$) and parameter updates ($K_{\text{learn}}=10$) on non-viable delays.

---

## 2. Statistical Analysis Plan

### 2.1 Primary Inferential Unit
The primary unit of statistical inference is the **independent random seed** ($N=30$, seeds $1811..1840$). Performance metrics are averaged across the 14 benchmark tasks ($I_1..I_{14}$) within each seed before evaluating inferential statistics. No task-level pooling or probe-level pooling is permitted for primary inference.

### 2.2 Primary Non-Inferiority Test
$$\Delta_{\text{seed}} = \text{NMSE}_{\text{candidate}}(\text{seed}) - \text{NMSE}_{R_0}(\text{seed})$$
$$\bar{\Delta} = \frac{1}{N} \sum_{s=1}^N \Delta_s, \quad s_{\Delta} = \sqrt{\frac{1}{N-1} \sum_{s=1}^N (\Delta_s - \bar{\Delta})^2}, \quad \text{SE} = \frac{s_{\Delta}}{\sqrt{N}}$$
$$\text{CI}_{95\%} = \bar{\Delta} + t_{0.95, 29} \cdot \text{SE}$$
Non-inferiority is formally supported if $\text{CI}_{95\%} < +0.0100$.

### 2.3 Secondary Inferential Families & Multiplicity Control
Secondary hypothesis testing is conducted across two preregistered families with Holm-Bonferroni step-down correction:
1. **Pure-Lag Preservation Family ($m=4$):** Tasks $I_3, I_4, I_5, I_8$ with non-inferiority margin $+0.0150$.
2. **Switching Latency Family ($m=4$):** Tasks $I_{11}, I_{12}, I_{13}, I_{14}$ with recovery latency margin $+50.0\text{ stream steps}$ vs. $R_0$.
Resource gates ($\le 100.00\text{ FP/step}$ and $\le 1024\text{ B}$) are deterministic accounting thresholds and require no $p$-value.

### 2.4 Data Exclusion Rules
Zero data exclusion. Every executed stream step across all 30 confirmatory seeds must be retained in the analysis. No post-hoc trimming, winsorizing, or outlier rejection is permitted.

---

## 3. Mandatory Invariant Commitments

1. **Frozen Multirate Clocks:** $K_{\text{probe}}=2, K_{\text{cand\_obs}}=5, K_{\text{cand\_learn}}=10, K_{\text{rec\_fwd}}=1, K_{\text{rec\_learn}}=10, K_{\text{arb}}=5$ remain constant.
2. **No Hidden Dense State:** If the candidate instantiates a dense $165$-cell array in memory, it is classified as `FAIL`.
3. **Single Candidate Freeze:** Exactly one candidate policy will be selected based on DEV screening ($1801..1810$) and frozen in `FINAL_SEARCH_CANDIDATE_FREEZE.md` before executing any confirmatory seeds ($1811..1840$).
4. **Hard Stop Enforcement:** Upon completion, no further stochastic runs, clock adjustments, or code mutations will be performed without human review.
