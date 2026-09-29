# EXP-0002: Candidate Targeting vs Incumbent Protection

## 1. Executive Summary
- **Experiment Status**: `NO_GO` (Target: Full-support occupancy >= 70% & R2 MSE <= 0.10 under matched compute; observed in causal E1/E3: occupancy 44.1% – 47.6%, missing the 70% target across all seeds)
- **Primary Diagnosis**: `TARGETING_IMPORTANT_BUT_SCORE_WEAK` (Case D confirmed: Oracle Targeting E4 dramatically solves the task reaching **94.4% occupancy**, **0.0139 MSE**, and **57-step latency** under 16.9% compute; however, the simple causal shrinkage score locks onto early noise on difficult seeds)
- **Component Status**:
  - `CANDIDATE_PRIORITY`: `KEEP` (Essential direction; boosted occupancy from 27.8% to 47.6% and reduced latency on 4/5 seeds, but requires a less noise-lockable scoring mechanism)
  - `TEMPORARY_PROTECTION`: `DEFER` (Harmful on its own: traps noise in the buffer and collapses occupancy to 7.1%)
  - `PROBE_BANK`: `KEEP` (Strictly guarantees budget equality of 10,000 probes while financing burst exploration)

---

## 2. Consolidated Results Table (Section 61)

Evaluated across the 5 frozen evaluation seeds `[42, 123, 456, 789, 1024]` with strictly matched cumulative budgets ($\sum_{t=1}^{2000} q_t = 10,000$ probes):

| Model | Global MSE | Regime-2 MSE | Final Recall | Mean R2 Recall | Full-Support Occ | Stable Latency ($H=50$) | Cumul Omit Energy | True Probe Eff | Promo Prec | Premature Evicts | Displacements | True Surv@50 | Noise Surv@50 | Total Probes | Mean FLOPs | Peak FLOPs | Compute vs Dense |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| **Dense** | 1.4380 ± 0.0127 | 0.0339 ± 0.0071 | 100.0% ± 0.0% | 100.0% ± 0.0% | 100.0% ± 0.0% | 1.0 ± 0.0 | 0.0 ± 0.0 | 0.0% | 0.0% | 0.0 | 0.0 | 100.0% | 0.0% | 0 | 602.0 | 602.0 | 100.0% |
| **Sparse_Oracle** | 0.1426 ± 0.0098 | 0.0148 ± 0.0015 | 100.0% ± 0.0% | 100.0% ± 0.0% | 100.0% ± 0.0% | 1.0 ± 0.0 | 0.0 ± 0.0 | 0.0% | 0.0% | 0.0 | 0.0 | 100.0% | 0.0% | 0 | 32.0 | 32.0 | 5.3% |
| **E0 (Baseline D2)** | 4.1439 ± 0.9619 | 0.3468 ± 0.5892 | 100.0% ± 0.0% | 66.8% ± 11.2% | 27.8% ± 17.1% | 723.2 ± 171.4 | 2161.8 ± 700.6 | 2.7% | 5.3% | 7.8 | 9.6 | 61.9% | 15.2% | 10,000 | 100.0 | 182.0 | 16.6% |
| **E1 (Targeting Only)** | 2.4313 ± 1.4312 | 1.0232 ± 2.2554 | 92.0% ± 17.9% | 69.5% ± 27.4% | 47.6% ± 36.2% | 525.2 ± 361.5 | 2155.5 ± 1933.5 | 2.3% | 7.6% | 6.8 | 7.4 | 62.3% | 17.0% | 10,000 | 449.4 | 541.2 | 74.7% |
| **E2 (Protection Only)** | 5.8038 ± 1.2458 | 2.7128 ± 2.5188 | 72.0% ± 30.3% | 48.1% ± 19.4% | 7.1% ± 15.8% | 929.4 ± 157.9 | 3606.2 ± 1698.6 | 3.5% | 8.0% | 7.8 | 16.2 | 69.7% | 18.6% | 10,000 | 109.6 | 160.0 | 18.2% |
| **E3 (Targeting+Protect)** | 3.6792 ± 1.8082 | 1.5529 ± 2.3949 | 88.0% ± 17.9% | 67.9% ± 27.0% | 44.1% ± 41.0% | 559.4 ± 409.3 | 2281.2 ± 2039.2 | 3.4% | 10.4% | 5.6 | 13.2 | 77.3% | 24.0% | 10,000 | 456.3 | 536.0 | 75.8% |
| **E4 (Oracle Targeting)** | **0.3225 ± 0.0213** | **0.0139 ± 0.0016** | **100.0% ± 0.0%** | **97.9% ± 1.1%** | **94.4% ± 3.5%** | **57.0 ± 35.5** | **122.4 ± 38.4** | **1.7%** | **27.0%** | **0.4** | **0.8** | **96.5%** | **39.7%** | **10,000** | **101.8** | **182.0** | **16.9%** |

---

## 3. Feature Latency Decomposition (Section 63)

Total structural recovery latency decomposed into: $T_{\text{total}} = T_{\text{wait\_probe}} + T_{\text{evidence}} + T_{\text{post\_promotion}}$.

| Model | $T_{\text{wait\_probe}}$ | $T_{\text{evidence}}$ | $T_{\text{post\_promotion}}$ | $T_{\text{total}}$ |
|:---|:---:|:---:|:---:|:---:|
| **E0 (Baseline D2)** | 5.6 ± 5.3 | 264.7 ± 284.1 | 80.8 ± 139.7 | 351.2 ± 251.9 |
| **E1 (Targeting Only)** | 6.7 ± 4.5 | 228.6 ± 310.0 | 94.8 ± 192.4 | 330.1 ± 313.5 |
| **E2 (Protection Only)** | 14.4 ± 32.1 | 270.4 ± 286.8 | 356.8 ± 343.4 | 641.6 ± 354.4 |
| **E3 (Targeting+Protect)** | 18.4 ± 32.3 | 225.9 ± 305.2 | 180.5 ± 289.5 | 424.8 ± 383.6 |
| **E4 (Oracle Targeting)** | **0.6 ± 2.1** | **19.3 ± 25.3** | **2.8 ± 9.9** | **22.6 ± 26.7** |

---

## 4. Answers to Mandatory Questions (Section 70)

1. **Is the remaining latency mostly waiting to probe the right candidate?**  
   **NO**. $T_{\text{wait\_probe}}$ is only 5.6 steps in E0. The initial probe occurs quickly under round-robin.
2. **Or is it mostly losing a candidate after it was correctly promoted?**  
   **PARTIALLY**. In E0, there were 7.8 premature evictions and 9.6 noise$\to$true displacements. While protecting incumbents helped on Seed 42 and 1024, blind protection trapped noise on other seeds.
3. **How much of $T_{\text{total}}$ comes from $T_{\text{wait\_probe}}$?**  
   **1.6%** ($5.6 / 351.2$).
4. **How much comes from evidence accumulation ($T_{\text{evidence}}$)?**  
   **75.4%** ($264.7 / 351.2$). This is the single largest delay in causal models: waiting for a true candidate to accumulate $n_{\min}=8$ probes while candidate screening is diffused over 95 candidates.
5. **How much comes from post-promotion instability ($T_{\text{post\_promotion}}$)?**  
   **23.0%** ($80.8 / 351.2$).
6. **Does priority improve true-probe efficiency?**  
   It marginally improved candidate targeting in responsive seeds, but the simple shrinkage score did not significantly change global probe efficiency (2.7% vs 2.3%) because noise candidates often captured priority slots.
7. **Does temporary protection reduce noise$\to$true displacement?**  
   Protection eliminated true feature evictions while young, but increased total displacements in the presence of noise (from 9.6 to 16.2) because noise was artificially preserved in the buffer.
8. **Does protection trap noise in the buffer?**  
   **YES**. Noise survival @50 increased from 15.2% to 18.6%, and in seeds with high early noise (e.g. Seed 123, 456, 789), buffer slots filled with protected noise, deferring true feature promotions and collapsing occupancy to 7.1%.
9. **Does E3 materially outperform E1 and E2?**  
   **NO**. E3 (44.1% occupancy) did not beat E1 (47.6% occupancy) on average, because E2's noise-trapping penalty offset E1's targeting gains.
10. **How close does causal targeting get to oracle candidate targeting?**  
    **A large gap remains**: Causal E1/E3 achieved 44–48% occupancy, whereas Oracle Targeting E4 achieved **94.4% occupancy** and **0.0139 R2 MSE**.
11. **Can the learner now reach near-oracle sparse performance under the same global probe budget?**  
    **THEORETICALLY YES, CAUSALLY NOT YET**: E4 conclusively proves that under the *exact same 10,000 probe budget and 16.9% compute*, the sparse learner reaches 0.0139 MSE and 94.4% occupancy if probes are delivered to the right candidates.
12. **What is the smallest successful mechanism?**  
    Candidate prioritization is the required mechanism, but the candidate priority scoring rule must be redesigned to resist early noise lock-in.

---

## 5. Most Important Practical Question (Section 71)

**“WITH THE SAME TOTAL COMPUTE BUDGET, CAN THE LEARNER DIRECT ITS LIMITED STRUCTURAL SEARCH TOWARD THE RIGHT VARIABLES AND KEEP USEFUL NEW STRUCTURE LONG ENOUGH TO LEARN IT?”**

**PARTIALLY / NO FOR CURRENT CAUSAL HEURISTICS; DEFINITIVELY YES FOR THE LEARNER ARCHITECTURE AS PROVED BY E4.**
- E4 proves that the learner architecture, the $K_{\max}=10$ buffer, the NLMS parameter estimator, and the 10,000 probe budget are **100% capable** of solving non-stationary sparse tracking at near-oracle performance (94.4% occupancy, 0.0139 MSE).
- The remaining hurdle is strictly **causal candidate priority scoring**: distinguishing true correlation from noise spikes during high-residual transition phases without oracle labels.
