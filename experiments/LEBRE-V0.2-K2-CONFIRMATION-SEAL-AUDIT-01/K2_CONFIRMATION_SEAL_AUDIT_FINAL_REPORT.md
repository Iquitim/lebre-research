# Forensic Seal Audit Final Report: LEBRE-V0.2-K2-CONFIRMATION-SEAL-AUDIT-01

**Audit ID:** `LEBRE-V0.2-K2-CONFIRMATION-SEAL-AUDIT-01`  
**Audited Parent:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Date:** September 2026  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Primary Outcome:** `K2_BEHAVIOR_CONFIRMED_RESOURCE_STATUS_RECLASSIFIED`

---

## Executive Summary
Under strict, independent forensic recomputation from Level-1 raw prequential telemetry ($5,040,000$ steps across 840 runs and 30 fresh confirmatory seeds $1941..1970$), this audit confirms that **$K=2$ HOLD_STATE recurrent-state decimation constitutes a valid, robust local behavioral boundary**.
Specifically:
1. **Predictive Non-Inferiority is CONFIRMED:** Mean paired degradation is $\mu_\Delta = +0.002714$, with an upper one-sided 95% confidence bound of $+0.003955$, comfortably below the frozen practical margin $M = +0.010000$ ($t = -9.9798, p = 3.4621 \times 10^-11$).
2. **Critical Temporal Mechanisms are PRESERVED:** Long-memory ($I_6$), quiescent reactivation ($I_7$), dual-occupancy complementarity ($I_9$), and regime switching recovery latencies ($I_{11}..I_{14}$) all pass their preregistered guardrails.
3. **Resource Compliance Fails at Full Precision:** Mean total compute is $\mathbf{101.023283\text{ FP/step}}$. This strictly fails the budget ceiling $\le 100.000000\text{ FP}$ by $+1.023283\text{ FP}$ and narrowly fails the engineering near-miss gate $\le 101.000000\text{ FP}$ by $+0.023283\text{ FP}$. Display rounding ($101.0$) cannot be used to pass a decision gate.
4. **Reporting Defects Reconciled:** The reported "17.000 FP" compute saving was a stale text template error (true saving is $10.213\text{ FP/step}$, $-9.18\%$); the update/hold ratio $0.761$ is an empirical average of task ratios without theoretical derivation; $r = -0.5627$ represents a trade-off association; and prior early candidate rejection ($0.885\text{ FP}$) is arithmetically insufficient alone to close the $1.023\text{ FP}$ gap.
5. **Path Forward:** Minimal-composition research is justified, with **arbitration decimation ($K_{\text{arb}}=5 \to 10$, saving $2.800\text{ FP/step}$)** identified as the primary candidate lever capable of delivering $>1.7\text{ FP}$ of robust headroom below budget.

---

## Exhaustive Responses to Required Audit Questions (Section 76)

### 1. Are the 840 raw runs complete and unique?
**YES.** Level-1 `K2_FINAL_RESULTS.csv` contains exactly 840 rows corresponding to 30 seeds $\times$ 14 tasks $\times$ 2 models. All composite keys `(random_seed, task_id, model_type)` are strictly unique with zero duplicates and zero missing values in essential metrics.

### 2. Were seeds 1941..1970 fresh?
**YES.** An exhaustive audit of all CSV files across all historical experiment directories verified zero overlap with any prior experimental `seed` column. Seeds $1941..1970$ represent a 100% fresh confirmatory cohort.

### 3. Was the single-intervention invariant preserved?
**YES.** `C0_K2_CONFIG_DIFF_RECHECK.csv` confirms that the only authorized difference between $C_0$ and $C_2$ was $K_{\text{rec\_forward}}: 1 \to 2$ and its physical consequence `skip_semantics: HOLD_STATE`. All other parameters were bitwise identical.

### 4. Does +0.002714 reproduce?
**YES.** Mean paired $\Delta\text{NMSE} = +0.002714041$, reproducing $+0.002714$ exactly.

### 5. Does +0.003955 reproduce?
**YES.** One-sided 95% upper confidence bound $= +0.003954531$, reproducing $+0.003955$ exactly.

### 6. What is the correct p-value for testing Delta=0?
**$p_{\text{zero}} = 8.5794 \times 10^-4 \approx 8.58 \times 10^-4$** ($t(29) = +3.7175$, two-sided).

### 7. What is the correct p-value for non-inferiority against +0.0100?
**$p_{\text{NI}} = 3.4621 \times 10^-11$** ($t(29) = -9.9798$, one-sided lower tail).

### 8. Why were conflicting p-values reported?
Narrative text in Section 1 printed `8.58e-14`, which was a typographical error conflating the mantissa of the zero-test ($8.58$) with an exponent typo. The statistical CSV correctly stored $3.4621 \times 10^-11$.

### 9. Can K2 be both statistically worse and practically non-inferior?
**YES.** $C_2$ has a statistically detectable degradation relative to $C_0$ ($p_{\text{zero}} < 0.001$), but the degradation is bounded well below the practical tolerance of $+0.0100$ ($p_{\text{NI}} < 10^-10$).

### 10. Do 5 wins / 25 losses reproduce?
**YES.** Exactly 5 seeds exhibited lower error under $C_2$ and 25 seeds exhibited lower error under $C_0$.

### 11. What is the exact C0 total compute?
**$111.236118\text{ FP/step}$**.

### 12. What is the exact K2 total compute?
**$101.023283\text{ FP/step}$**.

### 13. What is the true total compute saving?
**$10.212835\text{ FP/step}$** ($111.236118 - 101.023283$).

### 14. Where did 17.000 FP come from?
The generator script hardcoded a stale theoretical estimate of $34.0 \to 17.0\text{ FP}$ recurrent forward compute into the markdown template.

### 15. Is -9.18% correct?
**YES.** $10.212835 / 111.236118 \times 100\% = 9.1812\% \approx 9.18\%$. The percentage was computed from the true saving.

### 16. Does strict <=100 pass?
**NO.** $101.023283 > 100.000000$ by $+1.023283\text{ FP/step}$ (**FAIL**).

### 17. Does formal <=101 near-miss pass at full precision?
**NO.** $101.023283 > 101.000000$ by $+0.023283\text{ FP/step}$ (**FAIL**).

### 18. Can rounding change the gate?
**NO.** Rounding to one decimal place ($101.0$) is permissible for display formatting only; decision gates must be evaluated on unrounded full precision.

### 19. What is the exact residual deficit to 100?
**$+1.023283\text{ FP/step}$**.

### 20. Does the 9-FP direct recurrent saving reproduce?
**YES.** Recurrent shadow forward execution ($18.0\text{ FP}$) runs every 2 steps instead of every step, reducing forward compute from $18.0$ to $9.0\text{ FP/step}$ ($20.20 \to 11.20\text{ FP/step}$ total recurrent shadow).

### 21. How much indirect live change exists?
**$1.201151\text{ FP/step}$** ($75.684417 - 74.483266$).

### 22. Does component accounting close exactly?
**YES.** Recurrent saving ($9.000$) + live saving ($1.201151$) + search saving ($0.001025$) + candidate saving ($0.011259$) $= 10.212835\text{ FP/step}$. Residual is $0.000000\text{ FP/step}$.

### 23. Is indirect live change pathological?
**NO.** It reflects a mild reduction in recurrent active duty ($-4.33$ percentage points) and normal stochastic tap occupancy variation without loss of critical task gains.

### 24. What units do promotion/eviction deltas use?
**Events per run** (e.g., recurrent promotion delta is $-0.488095\text{ events/run}$; eviction delta is $-0.447619\text{ events/run}$).

### 25. Does I6 pass?
**YES.** $\Delta\text{NMSE} = +0.002708 \le +0.010000$.

### 26. Does I7 pass?
**YES.** $\Delta\text{NMSE} = +0.006712 \le +0.010000$.

### 27. Does I9 complementarity pass?
**YES.** $G_{D|B+R} = 0.245842 > 0$ and $G_{R|B+D} = 0.076891 > 0$.

### 28. Does switching pass?
**YES.** Recovery latency deltas are $+4.50, -11.13, -1.77, -1.67\text{ stream steps}$, all well within the $\le +50\text{ steps}$ guardrail.

### 29. What is authoritative path MAE?
**$0.343444$** (grand mean across 420 paired runs).

### 30. What are authoritative update/hold MAEs?
Update-step MAE: **$0.383609$**; Hold-step MAE: **$0.303278$**.

### 31. What is the correct hold/update ratio?
Ratio of grand means: **$0.790592 \approx 0.791$**; Average of per-task ratios: **$0.761409 \approx 0.761$**.

### 32. Was a theoretical ZOH ratio actually derived?
**NO.** No theoretical derivation was conducted; it is an empirical descriptive observation.

### 33. Does compute saving correlate with predictive degradation?
**YES.** Cross-seed Pearson correlation is $r = +0.5627$ ($p = 0.0012$).

### 34. What is the correct correlation sign when saving is positive?
**Positive ($r = +0.5627$).** Greater compute saving was associated with greater predictive degradation across seeds.

### 35. Were K3 and K4 ever tested?
**NO.** $K=3$ and $K=4$ are strictly `UNTESTED` in this experimental stream.

### 36. What exactly can be concluded about K>=3?
Only that $K=5$ failed confirmatory testing under HOLD_STATE. No universal conclusion about $K=3$ or $K=4$ is supported.

### 37. Is K2 a confirmed behavioral boundary?
**YES.** Local predictive non-inferiority and all temporal mechanisms are conclusively proven.

### 38. Is K2 a resource-compliant architecture?
**NO.** It requires $101.023\text{ FP/step}$, exceeding the strict $100.0\text{ FP}$ budget.

### 39. Is K2 globally validated against R0?
**NO.** $R_0$ was not rerun in this local confirmatory study.

### 40. Can previous early rejection alone close the current K2 deficit?
**NO.** Retrospective max saving ($0.8845\text{ FP}$) is smaller than the strict deficit ($1.0233\text{ FP}$). Net projected compute remains $100.139\text{ FP} > 100.0\text{ FP}$.

### 41. What minimum auxiliary saving is required?
**$+1.023283\text{ FP/step}$**.

### 42. What saving should be targeted to provide 0.5 / 1 / 2 FP headroom?
- 0.5 FP headroom: **$1.523283\text{ FP/step}$**
- 1.0 FP headroom: **$2.023283\text{ FP/step}$**
- 2.0 FP headroom: **$3.023283\text{ FP/step}$**

### 43. Which known auxiliary lever has sufficient resource mass?
**Arbitration Decimation ($K_{\text{arb}}=5 \to 10$)**, providing an analytical saving of **$2.800000\text{ FP/step}$** ($>1.7\text{ FP}$ headroom).

### 44. Is combined-resource research justified?
**YES.** Because $K=2$ behavior is confirmed and a plausible auxiliary lever with sufficient resource mass exists.

### 45. Is K2 + early rejection specifically sufficient?
**NO.** Early rejection alone cannot close the gap.

### 46. Should live linear filtering be modified next?
**NO.** Base live linear filtering is the predictive backbone of the model and has zero proven waste.

### 47. Should arbitration be decomposed first?
**YES.** Arbitration decimation has large resource leverage ($2.8\text{ FP}$) and high causal independence.

### 48. What is the next scientifically justified stage?
**`LEBRE-V0.2-COMBINED-RESOURCE-PARETO-DESIGN-01`** (a preregistered design stage evaluating $K=2$ paired with arbitration decimation).
