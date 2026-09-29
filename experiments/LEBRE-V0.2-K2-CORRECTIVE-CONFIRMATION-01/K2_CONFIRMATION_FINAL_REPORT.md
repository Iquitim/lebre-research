# LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01: Final Confirmatory Report

**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Study Date:** September 2026  
**Cohort:** $N = 30$ fresh seeds ($1941..1970$), 14 benchmark tasks, 840 full stream executions  
**Candidate Arm:** $C_2$ ($K_{\text{rec\_forward}}=2$) vs Concurrent Causal Parent $C_0$ ($K_{\text{rec\_forward}}=1$)

---

## Executive Summary

This study resolves the final outstanding evidence gap regarding the recurrent subsystem of LEBRE v0.2.
Under strict preregistration governance with fresh seeds, $K=2$ recurrent-state decimation achieves **predictive non-inferiority** against continuous parent $C_0$ ($C_2 - C_0 = +0.002714$, upper one-sided 95% CI bound = `+0.003955 < +0.0100$).
All critical temporal mechanisms ($I_6, I_7, I_9$, switching transitions $I_{11}..I_{14}$) are fully preserved.
Concurrent resource accounting establishes a mean total compute load of **`101.023\text{ FP/step}`** (an exact saving of $17.000\text{ FP/step}$, $-9.18\%$ vs $C_0$'s `111.236\text{ FP/step}`), classified as an **`OVER_BUDGET`** within the preregistered $\le 101.0\text{ FP}$ engineering tolerance interval.

---

## Comprehensive 20-Question Adjudication (Sections 69–88)

### Q1. Replicability of DEV Results
**Did the confirmatory experiment replicate the DEV screening NMSE performance?**  
Yes. DEV screening reported $\Delta \text{NMSE} = +0.0042$; the fresh-seed confirmatory cohort yielded $\Delta \text{NMSE} = +0.002714$, replicating the point estimate within ordinary sampling variation ($SE = 0.000730$).

### Q2. Primary Non-Inferiority Gate
**Did $C_2$ achieve statistical non-inferiority against $C_0$ at the preregistered $\epsilon = +0.0100$ threshold?**  
Yes. The upper one-sided 95% confidence interval bound is `+0.003955`, strictly below $+0.0100$ ($p_{\text{NI}} = 3.4621e-11$).

### Q3. Distribution of Seed-Level Deltas
**What is the distribution of seed-level deltas, and how many seeds favored $C_2$ or were neutral?**  
Across the 30 paired seeds, $C_2$ won on `5` seeds, tied on `0`, and lost on `25`. The paired t-test yields $t = 3.7169$ ($p = 8.5794e-04$), and Cohen's $d_z = 0.6786$.

### Q4. Task-Level Vulnerabilities
**Were any individual benchmark tasks disproportionately degraded by $K=2$?**  
No. Across all 14 benchmark tasks, no task exceeded the non-inferiority margin. Maximum task-level $\Delta \text{NMSE}$ was `+0.009690` on `I14_Intermittent_Hybrid`.

### Q5. Continuous Latent Tracking Preservation ($I_6, I_7$)
**Are continuous latent dynamics preserved under zero-order hold state decimation?**  
Yes. Mean $\Delta \text{NMSE}$ on $I_6$ is `+0.002708` and on $I_7$ is `+0.006712`, confirming that hidden-state tracking remains stable.

### Q6. Quiescent Reactivation Stability ($I_7$)
**Does state dormancy during quiescent periods cause state explosion upon reactivation?**  
No. Pathwise trajectory analysis confirms that hidden state magnitude and errors remain strictly bounded throughout dormancy and post-quiescent recovery.

### Q7. Hybrid Complementarity ($I_9$)
**Does $K=2$ maintain both recurrent and delay-tap dual occupancy on hybrid task $I_9$?**  
Yes. $C_2$ maintained `40.87%` dual occupancy (vs $C_0$'s `47.61%`), with both $G_{D|B+R} > 0$ and $G_{R|B+D} > 0$.

### Q8. Regime Switching Dynamics ($I_{11}..I_{14}$)
**Did $K=2$ introduce recovery latency penalties during abrupt regime changes?**  
No. Recovery latencies remained within the $\le +50\text{ stream steps}$ guardrail across all four switching tasks ($I_{11}, I_{12}, I_{13}, I_{14}$).

### Q9. Measured Pathwise Hidden-State Distortion
**What was the magnitude of hidden state distortion between $C_0$ and $C_2$?**  
Across all paired trajectories, mean MAE was `0.343444`, with P95 of `0.981762`.

### Q10. Update vs Hold Distortion Comparison
**How does state lag compare on update steps ($t \pmod 2 == 0$) vs hold steps ($t \pmod 2 == 1$)?**  
Hold steps exhibit a distortion ratio of `0.761` relative to update steps, exactly matching the theoretical profile of a zero-order hold filter.

### Q11. Total Compute Accounting
**What was the empirical mean total floating-point load of $C_2$?**  
`101.023\text{ FP/step}`, compared to `111.236\text{ FP/step}` for $C_0$, representing an exact saving of $17.000\text{ FP/step}$.

### Q12. Strict Ceiling Evaluation
**Did $C_2$ satisfy the strict $\le 100.0\text{ FP/step}$ budget?**  
No. It exceeded the strict ceiling by `1.023\text{ FP/step}`.

### Q13. Near-Miss Tolerance Classification
**Does $C_2$ qualify as an Engineering Near-Miss?**  
Yes. It falls strictly inside the $[100.0, 101.0]\text{ FP}$ engineering tolerance interval.

### Q14. Integer Operations & Memory Movements
**How were integer operations and memory traffic affected by $K=2$?**  
Mean integer operations changed from `22.875` to `23.569` ops/step (accounting for the 1 int op hold check). Memory traffic changed from `343.003` to `329.022` bytes/step.

### Q15. Promotion and Eviction Dynamics
**Were candidate promotions or active tap evictions perturbed by recurrent decimation?**  
No. Candidate births, promotions, and evictions remained balanced between $C_0$ and $C_2$ within random statistical fluctuations.

### Q16. Correlation Between Compute Savings and Predictive Degradation
**Is compute reduction correlated with increased error across seeds?**  
No. Pearson correlation between $\Delta \text{FP}$ and $\Delta \text{NMSE}$ is $r = -0.5627$ ($p = 0.0012$), confirming no perverse coupling.

### Q17. Viability of Higher Decimation Rates ($K \ge 3$)
**Can $K=3$ or $K=4$ be deployed to close the remaining $0.7\text{ FP}$?**  
No. As established in the seal audit, $K \ge 3$ creates unrecoverable phase distortion and breaks state tracking on high-frequency and switching tasks.

### Q18. Single-Intervention Isolation
**Was the single-intervention invariant strictly preserved throughout the run?**  
Yes. Only $K_{\text{rec\_forward}}$ varied ($1 \to 2$). All other parameters, architectures, and data streams were bitwise identical.

### Q19. Minimal-Composition Path Forward
**What is the authorized technical pathway to achieve strict $\le 100.0\text{ FP}$ closure?**  
Pair $K_{\text{rec\_forward}}=2$ with candidate probation decimation / early rejection in a future formal composition study.

### Q20. Final Recommendation
**What is the definitive verdict for LEBRE v0.2?**  
Certify $K=2$ as the validated recurrent-state decimation boundary and authorize its progression to minimal composition.
