# Authoritative Forensic Audit Final Report
## `LEBRE-V0.2-RECURRENT-SHADOW-SEAL-AUDIT-01`

**Stage ID:** `LEBRE-V0.2-RECURRENT-SHADOW-SEAL-AUDIT-01`  
**Milestone:** Forensic Seal Audit & Recurrent Decision Gate  
**Audited Parent:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Auditor:** Independent Skeptical Senior Scientific Software Auditor  
**Date:** September 2026  
**Primary Outcome:** **`RECURRENT_RESULT_VALID_WITH_REPORTING_CORRIGENDA`**  

---

### Detailed Answers to the 35 Required Audit Questions

1. **Did the 20.20-FP recurrent ledger reproduce?**  
   **YES.** All 12 atomic operations reproduce exactly: Forward state ($12.0\text{ FP}$), Readout prediction ($6.0\text{ FP}$), Sensitivities ($0.8\text{ FP}$), Learning ($0.8\text{ FP}$), Evidence ($0.6\text{ FP}$). Sum = $20.200000\text{ FP/step}$ ($|\Delta| < 10^{-9}$).

2. **Did C1 differ from C0 only in K_rec_forward?**  
   **YES.** The Single-Intervention Invariant passed completely. Search ($H=32, B=4, K_{\text{probe}}=2$), probation ($T_{\text{prob}}=15, \theta=0.02, 0.015$), learning clocks ($K_{\text{learn}}=10$), and precision are 100% identical.

3. **What was the true frozen DEV selection rule?**  
   The frozen protocol established $C_1$ ($K=5$) as the pre-authorized primary candidate arm, and $C_2$ ($K=2$) as a resource control. DEV was a screening stage to detect catastrophic failure before the $N=30$ confirmatory run.

4. **Was +0.031155 actually a DEV behavioral FAIL?**  
   **YES.** Relative to the $+0.0100$ practical non-inferiority margin, $+0.031155 > +0.0100$. The textual label `PASS` in the freeze document was an authoring template error.

5. **Was C1 legally eligible for FINAL under the preregistration?**  
   **YES, for confirmatory falsification.** $C_1$ was pre-authorized in Phase A for evaluation on DEV and FINAL.

6. **Is the FINAL run confirmatory or diagnostic?**  
   **CONFIRMATORY_WITH_REPORTING_CORRIGENDUM (FALSIFICATION_ONLY).** The confirmatory hypothesis that $K=5$ preserves performance was formally tested and decisively falsified.

7. **What are the authoritative FINAL C0/C1/R0 absolute NMSE values?**  
   - $C_0$ (Parent $M_1^*$): **0.317009**
   - $C_1$ ($K=5$ Candidate): **0.349072**
   - $R_0$ (Continuous Baseline): **0.295640**

8. **Where did 0.174582 / 0.206646 / 0.153214 come from?**  
   They originated from an intermediate offset copy in a narrative summary table. Pairwise deltas were identical to Level-1 data.

9. **What is the authoritative concurrent C0 compute?**  
   **110.891082 FP/step** across the 30 seeds of the confirmatory cohort ($1911..1940$).

10. **What is the authoritative R0 compute?**  
    **169.420720 FP/step**, accounting for continuous candidate descendant evaluations across the full $5 \times 32$ grid.

11. **What exactly does P95=97.581850 mean?**  
    It is the **95th percentile across the 420 individual run-level mean FP/step values** (`P95_OF_RUN_MEANS`).

12. **How much total compute did K5 actually save vs concurrent C0?**  
    **24.907258 FP/step** ($110.891082 - 85.983824$).

13. **How much was direct shadow-clock saving?**  
    **14.412655 FP/step** ($35.554018 - 21.141363$), matching the theoretical $14.40\text{ FP}$ projection.

14. **How much was indirect live-path saving?**  
    **10.494603 FP/step** ($75.337063 - 64.842460$).

15. **Why did live compute change?**  
    Decimating the recurrent shadow state caused evidence collapse and utility loss on latent tasks, resulting in promoted live recurrent units being evicted or failing to promote.

16. **Did structural occupancy change?**  
    **YES.** Live recurrent occupancy collapsed to $0\%$ on $I_6$ and $I_{10}$, eliminating the $34\text{ FP/step}$ live recurrent cost.

17. **Is the extra compute saving behaviorally costly?**  
    **YES.** It is **BEHAVIORALLY_COSTLY_STRUCTURE_LOSS (PATHOLOGICAL UNDERMODELING)**.

18. **Does K5 robustly fail local non-inferiority?**  
    **YES.** $\Delta \text{NMSE} = +0.032064$, one-sided 95% upper bound $= +0.034119 > +0.0100$ (**FAIL**).

19. **Does K5 robustly fail I6?**  
    **YES.** $I_6$ degraded by $+0.1013$ NMSE (**FAIL**).

20. **Does K5 robustly fail I7?**  
    **YES.** $I_7$ degraded by $+0.0982$ NMSE (**FAIL**).

21. **Does K5 robustly destroy I9 recurrent complementarity?**  
    **YES.** $G_{R|B+D} = -0.0005 < 0$ (**FAIL**).

22. **Does K5 actually fail the switching GATE, or merely worsen latency within tolerance?**  
    **FAILS THE GATE.** On $I_{11}$, recovery latency degraded by **+246.2 steps**, breaching the $\le +50$ step gate.

23. **Was the 12/14 task rule preregistered?**  
    **NO.** It was post-hoc and descriptive.

24. **Is HOLD_STATE the only valid semantic, or merely the tested one?**  
    It is **merely the tested design choice**, frozen for causal isolation.

25. **Is the fast-forward "no advantage" claim correctly scoped?**  
    **YES, under full RTRL learning.** State unrolling provides no FLOP advantage in non-quiescent streams.

26. **Does K2 DEV aggregate behavior reproduce?**  
    **YES.** $\Delta \text{NMSE} = +0.004208 \le +0.0100$ in DEV.

27. **What is the exact K2 compute excess above 100?**  
    **+0.701790 FP/step** ($100.702095 - 100.0$).

28. **What is the authoritative K2 path MAE?**  
    **Unmeasured in DEV.** The reported $0.082$ was derived from historical D9F.

29. **Does K2 have catastrophic task-level failures?**  
    **NO.** The largest degradation on any task in DEV was $+0.0214$ (on $I_{12}$).

30. **Is K2 eligible for future research?**  
    **YES, as a promising DEV boundary.**

31. **Is combined-resource research justified?**  
    **HUMAN_REVIEW_REQUIRED.** The $+0.702\text{ FP}$ deficit cannot be assumed to add linearly with early rejection.

32. **Is live-linear cost actually proven waste?**  
    **NO.** It is the largest component ($75.47\text{ FP}$), but not proven waste.

33. **What precise hypothesis has now been falsified?**  
    Fixed $K=5$ recurrent state decimation using `HOLD_STATE` preserves predictive fidelity while recovering compute.

34. **What hypotheses remain open?**  
    1. Mild $K=2$ decimation combined with an independent resource lever.
    2. Lazy state propagation during true quiescence ($x_t = 0$).
    3. Structural live-linear filter optimization.

35. **What is the scientifically justified next stage?**  
    **`HUMAN_REVIEW_REQUIRED`**, with options for formal combined-resource planning or live-linear decomposition.
