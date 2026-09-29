# EXP-0001d: Final Diagnosis

## Primary Diagnosis
`CANDIDATE_SELECTION_LIMITING`

## Mechanistic Analysis & Empirical Evidence

### 1. The Core Empirical Test: Interpretation C Triggered
Section 38 defines the diagnostic criteria:
> **Interpretation C**: *If D4 also barely improves: timing is not the main remaining limitation. Look next at candidate targeting or evidence cost.*

Our observed empirical results:
- **D0 (Fixed Baseline)**: Full-Support Occupancy = **21.3% ± 20.1%**, R2 MSE = **0.7391 ± 0.8739**.
- **D4 (Oracle Timing Diagnostic)**: Full-Support Occupancy = **22.6% ± 37.0%**, R2 MSE = **1.0382 ± 1.1497**.
- **D2 (Adaptive Bank)**: Full-Support Occupancy = **27.8% ± 17.1%**, R2 MSE = **0.3468 ± 0.5892**.

Even with perfect oracle knowledge of when the structural shift occurs ($t=1000$) and a massive burst of $q_{\max} = 15$ probes per step for 200 consecutive steps (3,000 probes), D4 achieved only **22.6%** full-support occupancy—virtually indistinguishable from D0's 21.3%!

### 2. Why Did Timing Fail to Solve Acquisition Latency?
Detailed audit of Seed 42 event traces reveals the exact causal failure chain:
1. **Uniform Candidate Inefficiency**: With Round-Robin scanning over $D - K = 95$ candidates, even at $q=15$, each candidate is probed only once every $95 / 15 \approx 6.3$ steps. Reaching $n_{\min} = 8$ probes takes $\ge 50$ steps under ideal conditions.
2. **Premature Eviction of True Features**: During high-residual transition periods ($e_t \approx 2.0 - 3.0$), spurious noise candidates easily cross the promotion threshold $\theta_{\text{promote}} = 0.40$. When buffer slots fill up ($K_{\max} = 10$), newly promoted true features (which start with $w = 0$ and have only grown to $|w| \approx 0.10$ after the 15-step grace period) are identified as the smallest-weight features and are **evicted by subsequent spurious candidates**!
   - In Seed 42: True feature 49 was promoted at $t=1102$, then evicted at $t=1119$ by noise feature 31.
   - True feature 66 was promoted at $t=1109$, then evicted at $t=1131$ by noise feature 28.
   - True feature 24 was promoted at $t=1088$, then evicted at $t=1159$ by noise feature 89.
3. **Post-Burst Starvation in D4**: Because D4 exhausted 3,000 probes in the first 200 steps post-shift, it was forced to drop to $q = 2.5$ for the remaining 800 steps. In seeds where the true support was not completely locked in by $t=1200$, the learner was starved of exploration probes for the rest of the run, resulting in 0% occupancy for Seeds 42, 123, and 456.

### 3. Why D2 (Adaptive Bank) Is the Best Practical Mechanism
- D2 avoids the blind starvation trap of D4 and D1 by tying probe rates to ongoing causal error.
- In 3 out of 5 seeds (123, 789, 1024), D2 successfully locked in all 5 true features and achieved **0.0115 – 0.0166 R2 MSE** (2x to 3x better than Dense NLMS 0.0339!).
- Across all seeds, D2 achieved **100.0% final recall** and cut mean R2 MSE by **53%** (0.7391 -> 0.3468).
- However, because round-robin candidate screening treats all 95 inactive candidates identically, D2 cannot reach the required 70% occupancy target across all seeds.

### 4. Verdict
`NO_GO` for temporal allocation as a standalone solution to structural acquisition latency.
The experimental campaign conclusively proves that **temporal probe allocation alone is insufficient** when candidate screening is uniform and incubation is unprotected against spurious swaps.
