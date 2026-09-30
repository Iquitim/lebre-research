# REMOVED_COMPONENTS.md

Ideas, mechanisms, and modules tested and discarded due to lack of measurable gain or disproportionate resource overhead.

| Component | Tested In | Reason for Removal | Alternative Adopted |
| :--- | :--- | :--- | :--- |
| **Instantaneous Zero-Slack Swap ($|S|=K^*$)** | EXP-0001 | 1-in-1-out swap without slack forces newborn features ($w=0$) to compete immediately with established weights, creating extreme structural churn. | Bounded slack capacity ($K_{\max} = 10 \ge 2 K^*$) with decoupled growth and pruning. |
| **Sparse Single-Probe Correlation EMA** | EXP-0001 | Updating candidate EMA on single sporadic probes ($q=5 \ll D=100$) leaves extreme sample variance across 95 candidates, triggering 94% noise promotions. | Multi-probe evidence accumulation or block screening before promotion. |
| **Evidence Accumulation Without Slack (B2)** | EXP-0001b | Multi-probe evidence accumulation with $|S|=5$ still produced 8.0% recall. Evidence cannot rescue a model choked by zero slack. | Combine evidence accumulation with structural slack (B3). |
| **Maturity-Aware Explicit Pruning (B4)** | EXP-0001b | Pruning low-weight features did not improve MSE (0.85 vs 0.74 in B3) or recall (92% vs 96%), and caused severe transient gradient shocks (Global MSE 89.28). | Case D: Discard explicit pruning. Prefer simpler B3. |
| **Readout Top-5 Selection (C1)** | EXP-0001c | Pruning prediction readout to top-5 weights reduced MSE by only 8.5% (from 0.74 to 0.68). Buffer pollution accounts for only ~17% of error, not the primary gap. | Focus on accelerating support acquisition latency rather than filtering readout. |
| **Post-Acquisition Structural Freezing (C3)** | EXP-0001c | Freezing structural changes once full support is found changed MSE by only -0.0021 (0.737 vs 0.739). Churn after acquisition is negligible. | No hysteresis or locking mechanism needed. |
| **Unbanked Error-Adaptive Governor (D1)** | EXP-0001d | Spending extra probes early without previously banked savings exhausted budget (7,808 probes in R1), starving the learner in R2 ($q \approx 2$, 0% occupancy). | Hard Probe Credit Bank (D2) where credits must be earned before spending. |
| **Fixed-Window Post-Shift Bursts (D4 style)** | EXP-0001d | Concentrating probes into an arbitrary fixed window (e.g. 200 steps) post-shift without feedback leads to starvation if recovery is not complete. | Causal error-driven bank discharge. |
| **Temporal Probe Allocation as Standalone Latency Fix** | EXP-0001d | Timing probe bursts alone cannot overcome uniform round-robin candidate screening across 95 features; noise features still cause spurious swaps and evictions. | Candidate selection prioritization / non-uniform screening. |
| **Blind Temporary Incumbent Protection (E2)** | EXP-0002 | Granting immunity to newborn features without high-precision candidate targeting traps spurious noise features in the buffer for 40 steps, filling the buffer and deferring newly discovered true features. Collapsed occupancy to 7.1% and increased MSE to 2.71 (Case F). | Focus on noise-resistant candidate targeting so only true features enter the buffer. |
| **Full-Array Candidate Scoring and Ranking (F1)** | EXP-0003 | Scoring and sorting all 95 candidates every observation consumed $446.4$ FLOPs/step ($74.2\%$ of Dense compute), violating the $<25\%$ compute limit. | Lazy event-driven scoring updating only probed candidates upon probe events ($17.2\%$ compute). |
| **Pure Confirmation Greediness Without Coverage (F3)** | EXP-0003 | Allocating all probes to confirmed candidates starved the unconfirmed pool ($T_{\text{wait\_probe}} = 205.4$ steps on Seed 1024), causing final recall collapse ($96\%$) and MSE explosion ($0.3289$). | Forced coverage reservation (F4) reserving $40\%$ of probes strictly for oldest unprobed candidates. |
| **Contribution-Aware Victim Scoring (G3)** | EXP-0004 | Instantaneous $|w \cdot x|$ EMA has extreme sample variance due to Gaussian inputs. Young developing weights produce noisy estimates, increasing $T_{\text{post\_promotion}}$ by $39.7\%$ ($291.6$ steps) and MSE to $0.09385$. | Age-normalized weight scoring (G1). |
| **Rigid Promotion Cooldown (G4)** | EXP-0004 | Forcing a fixed 20-step cooldown between promotions artificially throttles structural adaptation post-shift, delaying support recovery by hundreds of steps and causing MSE to explode to $4.1827$. | Immediate promotion upon evidence confirmation without cooldown. |
| **Naive Lower Fixed Sample Requirement (H1)** | EXP-0005 | Globally lowering $N_{\min}$ from 8 to 3 reopens noise instability: triggered 3,430 early noise promotions, 39.2 displacements, and exploded MSE to 3.2703. | Retain conservative $N_{\min}=8$ or require sequential Wald bounds (H4). |
| **Correlation Magnitude Alone Early Stopping (H2)**| EXP-0005 | Early stopping based solely on $|\bar{c}| \ge 0.50$ fails because small-sample noise correlations frequently exceed 0.50 by chance, driving displacements to 40.6 and MSE to 2.2367. | Require directional sign consistency and sequential confidence bounds. |
| **Two-Tier Allocation Without Decay (J1)** | EXP-0006 | Static two-tier allocation without decay traps spurious noise candidates in WARM slots permanently, consuming 5,770 elevated probes, collapsing full-support occupancy to 13.70% and spiking MSE to 0.7114. | Tier decay and probe timeouts (J2) or Queue-Based Multi-Rate Allocation (J4). |






