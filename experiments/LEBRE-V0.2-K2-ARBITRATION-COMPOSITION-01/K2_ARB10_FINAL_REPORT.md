# Final Report: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Stage ID:** `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01`  
**Primary Outcome:** **`K2_ARB10_RESOURCE_PASS_END_TO_END_NI_FAIL`**  
**Governance:** Confirmatory 3-Arm Experimental Study  
**Hardware / Host Platform:** AMD64 Family 25 Model 117, Windows 11, Python 3.11.9, NumPy 2.2.5, SciPy 2.2.3  
**Execution Runtime:** 1,260 runs in 125.16 seconds (2.09 minutes) across 16 parallel CPU workers.

---

## Executive Summary

Stage `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01` executed a preregistered, fresh-seed, 3-arm confirmatory experiment evaluating whether combining confirmed $K_{\text{rec}}=2$ decimation with $K_{\text{arb}}=10$ arbitration decimation crosses the strict $100.0\text{ FP/step}$ resource boundary while preserving end-to-end predictive non-inferiority relative to the local reference ($A0$).

The experiment yielded an unambiguous, rigorous scientific result:
1. **Resource Closure Succeeded:** Arm A2 achieved a grand mean total compute of **`96.957851 FP/step`**, passing the strict budget ceiling ($\le 100.000000	ext{ FP/step}$) with **`+3.042149 FP/step`** of headroom.
2. **K2 Recurrent Replication Succeeded:** Arm A1 reproduced K2 practical non-inferiority on the new cohort ($N=30$, seeds `1971..2000`): mean $\Delta = +0.003196$, 95% upper bound = **`+0.004477 < +0.010000`** ($p_{\text{NI}} = 3.21 \times 10^{-10}$).
3. **Primary End-to-End Behavioral Non-Inferiority Failed:** Arm A2 exhibited a mean degradation of **`+0.014548`**, with a one-sided 95% upper bound of **`+0.020204 > +0.010000`** ($p_{\text{NI}} = 0.9088$).
4. **Switching Guardrail Failed:** On task $I_{12}$ (`Latent_To_Delay`), recovery latency increased by **`+213.63 stream steps`**, violating the $\le +50$-step guardrail.
5. **Causal Mechanism Isolated:** The failure was caused by **`EMA_TIMESCALE_DISTORTION combined with DECISION_STALENESS`**. Holding $lpha = 0.02$ fixed while decimating the clock doubled the effective stream-time filter memory from $\sim 250$ to $\sim 500$ steps, making supervisory evidence accumulation sluggish and delaying necessary delay-tap promotions.

---

## Answers to the 40 Required Final Questions (Section 16)

### Q1. Were all 1260 expected runs completed?
**YES.** Exactly 1,260 runs were completed (30 seeds $	imes$ 14 tasks $	imes$ 3 arms = 1,260 runs, 7,560,000 stream steps).

### Q2. Were all confirmatory seeds fresh?
**YES.** Seeds `1971..2000` ($N=30$) were independently verified to have zero overlap across all prior experiment manifests.

### Q3. Did A2 differ from A1 only by K_arb=5->10?
**YES.** Single-intervention invariant programmatically verified in `A0_A1_A2_CONFIG_DIFF.csv`.

### Q4. Was alpha_EMA kept exactly fixed?
**YES.** Fixed at 0.020000 across all three arms.

### Q5. What are the exact effective EMA time constants at K5 and K10?
- Event time constant: $	au_{\text{events}} = 49.4965	ext{ events}$.
- At $K=5$: $	au_{\text{stream}} = \mathbf{247.4827	ext{ stream steps}}$ (half-life: $171.5481	ext{ steps}$).
- At $K=10$: $	au_{\text{stream}} = \mathbf{494.9654	ext{ stream steps}}$ (half-life: $343.0962	ext{ steps}$).

### Q6. Did A1 reproduce the confirmed K2 behavioral boundary?
**YES.** Paired $A1 - A0$ mean $\Delta 	ext{NMSE} = +0.003196$, one-sided 95% upper bound = **`+0.004477 < +0.010000`** ($p_{\text{NI}} = 3.21 \times 10^{-10}$).

### Q7. What is mean Delta NMSE A2-A0?
**`+0.014548`**.

### Q8. What is its one-sided 95% upper CI?
**`+0.020204`**.

### Q9. Does end-to-end non-inferiority pass?
**FAIL.** $+0.020204 > +0.010000$.

### Q10. What is the incremental behavioral effect A2-A1?
Mean $\Delta = \mathbf{+0.011352}$, one-sided 95% upper bound = **`+0.016960`**.

### Q11. What is empirical A2 mean total FP?
**`96.957851 FP/step`**.

### Q12. Does strict <=100 pass?
**PASS.** `96.957851 \le 100.000000	ext{ FP/step}`.

### Q13. What is empirical resource headroom?
**`+3.042149 FP/step`** below budget.

### Q14. Does arbitration compute fall from 5.6 to 2.8 as expected?
**YES.** Exactly $5.600000 	o 2.800000	ext{ FP/step}$ (direct saving = $2.800000	ext{ FP/step}$).

### Q15. What is the projection residual vs 98.223283?
**`-1.265432 FP/step`** (A2 consumed $1.265	ext{ FP}$ less than projected due to fewer live taps).

### Q16. Did slower arbitration increase live compute?
**NO.** Live linear compute decreased from $74.25$ to $73.34	ext{ FP/step}$ ($-0.905	ext{ FP/step}$) because delayed promotion reduced active tap duty.

### Q17. Did it increase dual occupancy duration?
Across all tasks, dual occupancy duty cycle slightly decreased ($0.1245 	o 0.1227$); on $I_{10}$, episodes were fewer but slightly prolonged.

### Q18. Did it alter candidate compute?
Candidate direct compute slightly decreased from $1.826$ to $1.814	ext{ FP/step}$ ($-0.012	ext{ FP/step}$).

### Q19. Did I6 pass?
**PASS.** Paired $\Delta 	ext{NMSE} = +0.005277 \le +0.010000$.

### Q20. Did I7 pass?
**FAIL.** Paired $\Delta 	ext{NMSE} = +0.017118 > +0.010000$.

### Q21. Did I9 preserve both conditional gains?
**PASS.** $G_{D|BR} = 0.3647 > 0$ and $G_{R|BD} = 0.0352 > 0$.

### Q22. Did all I11-I14 switching gates pass?
**FAIL.** Task $I_{12}$ latency delta was $+213.63	ext{ steps} > +50	ext{ steps}$.

### Q23. What was the actual incremental recovery latency from A2-A1?
On $I_{12}$: $+167.97	ext{ steps}$. On $I_{11}$: $+19.83	ext{ steps}$. On $I_{13}$: $+0.53	ext{ steps}$. On $I_{14}$: $-428.13	ext{ steps}$.

### Q24. Did meaningful structural decisions become delayed?
**YES.** Lag promotions on A2 dropped from $2.205$ to $1.776$ per run due to delayed evidence crossing past $	heta_{\text{tol}}$.

### Q25. How much did gain-EMA threshold crossing shift?
Threshold crossing in regime transitions shifted by approximately $150$ to $250$ stream steps.

### Q26. Did slower EMA evolution materially affect promotions or evictions?
**YES.** Doubling the stream-time memory window from $\sim 250$ to $\sim 500$ steps prevented timely structural adaptation to fast changepoints.

### Q27. Were the previously "99.55% unchanged" evaluations truly irrelevant to future decisions?
**NO.** The empirical findings prove those evaluations were NOT computationally irrelevant; they accumulated the continuous gain gradient necessary for agile switching.

### Q28. Did churn decline?
**YES.** Structural transitions declined on A2 ($1.776$ lag promotions vs $2.205$ on A1; $1.305$ lag evictions vs $1.736$ on A1).

### Q29. If churn declined, was behavior preserved?
**NO.** Reduced churn was accompanied by significant predictive degradation and switching latency failure.

### Q30. Did structural dwell time increase?
**YES.** Mean dwell time increased from $\sim 350$ to $\sim 480$ steps.

### Q31. Was any compute saving caused by behaviorally costly under-modeling?
**YES.** The extra saving below $98.22	ext{ FP}$ ($96.96	ext{ FP}$) was directly caused by delayed promotions and suppressed tap occupancy.

### Q32. What happened on I10?
On $I_{10}$, NMSE degraded by $+0.029732$, with dual structures taking longer to resolve.

### Q33. Did Gate 6 remain historically unchanged?
**YES.** Gate 6 status remains permanently `FAIL`. No repair was attempted or claimed.

### Q34. Does A2 occupy a resource-compliant local behavioral point?
**NO.** It is resource-compliant, but behaviorally non-compliant.

### Q35. Can A2 be called globally validated?
**NO.**

### Q36. If A2 succeeds, what remains before integrated validation?
(A2 did not succeed).

### Q37. If A2 fails, is the failure more consistent with decision staleness, EMA-timescale distortion, resource backfill, or another mechanism?
The failure is most consistent with **`EMA-timescale distortion combined with decision staleness`** (sluggish evidence integration leading to delayed structural promotion and under-modeling), NOT resource backfill.

### Q38. Is event-triggered arbitration justified as a future hypothesis?
**YES.** `EVENT_TRIGGERED_ARBITRATION_STATUS = FUTURE_HYPOTHESIS_ONLY`.

### Q39. Is EMA-timescale-preserving arbitration justified as a future hypothesis?
**YES.** `EMA_TIMESCALE_PRESERVATION_STATUS = FUTURE_HYPOTHESIS_ONLY` (rescaling per-event $lpha$ to preserve stream-time time constants).

### Q40. What exact next stage is scientifically justified?
`LEBRE-V0.2-K2-ARB10-COMPOSITION-SEAL-AUDIT-01` to seal these confirmatory findings under forensic governance.
