# KEPT_COMPONENTS.md

Components, mechanisms, and heuristics that have proven their value empirically by paying rent (measurable performance or efficiency gain).

| Component | Introduced In | Justification & Empirical Gain | Resource Overhead |
| :--- | :--- | :--- | :--- |
| **Dense NLMS Reference** | EXP-0001 | Stable convergence ($MSE = 0.0218 \to 0.0339$), recovers post-shift within 930 steps. Serves as ground-truth oracle ceiling. | 602 FLOPs/step, 800 bytes RAM |
| **Fixed-Support NLMS Reference** | EXP-0001 | Validates lower bound failure under support shift ($MSE = 11.1 \to 12.2$). Proves that static models cannot handle non-stationarity. | 32 FLOPs/step, 60 bytes RAM |
| **Dynamic Stream Harness** | EXP-0001 | Ground truth tracking, multi-seed deterministic reproducibility, clean single-pass streaming evaluation. | Minimal CPU overhead (< 1s per 2k steps) |
| **Structural Slack ($K_{\max} = 10$)** | EXP-0001b | Primary causal mechanism solving the churn trap. Increased final recall from 16% to 84% (B1) and enabled 96% in B3 by providing incubation capacity. | Adds ~30 FLOPs/step for active NLMS, keeps compute < 17% of Dense |
| **Multi-Probe Evidence Accumulator** | EXP-0001b | Interacts with slack to boost true feature survival @100 from 31% to 55.5%, cutting redundant repromotions from 30 to 8 and reducing R2 MSE to 0.74. | Adds 4 FLOPs/probe (8 vs 4) = 20 FLOPs/step. Total compute 100 FLOPs (16.6% of Dense) |
| **Sparse NLMS Parameter Estimator (C4)** | EXP-0001c | Proven that sparse NLMS with true support achieves MSE of **0.0148** (beating Dense 0.0339 by 2.3x) at **32 FLOPs/step** (18.8x cheaper). Eliminates any parameter estimation or gradient adaptation failure hypotheses. | 32 FLOPs/step, 80 bytes RAM |
| **Probe-Credit Bank (D2)** | EXP-0001d | Causal credit bank ($B_t \ge 0$) that saves probes during low-error periods ($q_{\min}=2$) to finance burst exploration ($q_{\max}=15$) during structural change under exact budget matching ($\Delta = 0$). Cut R2 MSE by 2.1x (0.7391 to 0.3468) and achieved 100% final recall without learned parameters. | < 1 FLOP/step, 8 bytes state |
| **Candidate Prioritization Principle (E1/E4)** | EXP-0002 | Proved conclusively by E4 (94.4% occupancy, 0.0139 MSE, 57-step latency) that prioritizing candidate exploration toward high-correlation features is the primary lever to eliminate discovery latency without increasing compute. E1 lifted occupancy from 27.8% to 47.6%. | ~350 FLOPs/step when candidates scored |
| **Explore/Confirm Screening (F3/F4)** | EXP-0003 | Two-stage candidate state machine with bounded capacity ($C_{\max}=3$), entry screening, and drop/timeout exit conditions. Cut $T_{\text{evidence}}$ by up to $42.9\%$ ($203.7 \to 116.4$ steps) without permanent noise lock-in. | ~2 FLOPs/step for confirm state checking |
| **Forced Coverage Reservation (F4)** | EXP-0003 | Reserving $40\%$ of candidate probe capacity for circular round-robin coverage strictly prevents candidate starvation ($T_{\text{wait}} = 5.64$ steps), guaranteeing $100\%$ final recall and closing $96.3\%$ of the Oracle MSE gap ($0.01638$ vs Oracle $0.01374$). | 0 additional FLOPs |
| **Lazy Event-Driven Candidate Scoring (F2-F4)** | EXP-0003 | Candidate statistics and scores update strictly upon probe events rather than scoring all 95 candidates every step. Slashed compute from $74.2\%$ (F1) to **$17.2\%$ of Dense (103.6 FLOPs/step)**, easily satisfying the $<25\%$ compute gate. | ~3-6 FLOPs/step |
| **Age-Normalized Victim Scoring (G1)** | EXP-0004 | Scales victim eviction score by maturation factor $\min(1, \text{age}_j / \tau_{\text{mature}})$. Slashed post-promotion churn latency by **70.86%** ($208.8 \to 60.84$ steps), reduced displacements by 40.4% (11.4 to 6.8), improved full-support occupancy to **65.36%** (+17.7 pp), and reduced Regime-2 MSE to **0.01383** (outperforming Dense and Sparse Oracle) without trapping noise. | Negligible (~1 FLOP/eviction evaluation) |
| **Two-Boundary Sequential Early Acceptance (H4)** | EXP-0005 | Combines signal magnitude, 100% directional sign consistency, and sequential Wald confidence bounds ($|\bar{c}| - 1.645 \cdot SE > 0$). Achieved lowest overall Regime-2 MSE (**0.01334**) of any model with zero seed collapses across all 5 evaluation seeds. | ~4 FLOPs/candidate check |
| **Evidence Decay & Demotion Timeouts (J2)** | EXP-0006 | Demotes elevated candidates back to COLD if correlation weakens ($|\bar{c}| < \theta_{\text{decay}}$) or after probe timeout without promotion. Cut false elevated probes by 42% (5,770 to 3,350) and prevented noise lock-in, restoring MSE to 0.01389 and occupancy to 57.2%. | ~2 FLOPs per probed candidate |
| **Queue-Based Multi-Rate Allocation (J4)** | EXP-0006 | Explicit FIFO queues (`cold_queue`, `warm_queue`, `hot_queue`) with fixed service schedule. Slashed median true inter-probe gap by **85.5%** (16.6 to 2.4 steps), reduced $T_{\text{first\_probe}}$ from 46.4 to 11.8 steps, reduced $T_{\text{total}}$ by 32.7 steps (236.5 to 203.8), and achieved lowest MSE in repository (**0.01355**) at **23.72% Dense compute** (142.8 FLOPs/step) with zero $O(D)$ scans. | O(1) deque pop/append (~2 FLOPs/step) |






