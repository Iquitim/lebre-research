# Final Report: LEBRE-V0.2-COMBINED-RESOURCE-PARETO-DESIGN-01

**Stage ID:** `LEBRE-V0.2-COMBINED-RESOURCE-PARETO-DESIGN-01`  
**Primary Outcome:** **`K2_ARB10_COMPOSITION_DESIGN_AUTHORIZED`**  
**Governance:** Scientific Software Audit & Preregistration  
**Hardware / Host Platform:** AMD64 Family 25 Model 117, Windows 11, Python 3.11.9, NumPy 2.2.5, SciPy 2.2.3

---

## Executive Summary

Stage `LEBRE-V0.2-COMBINED-RESOURCE-PARETO-DESIGN-01` resolves all residual resource lineage inconsistencies inherited from `LEBRE-V0.2-K2-CONFIRMATION-SEAL-AUDIT-01`, reconstructs the complete architectural operation ledger of the arbitration subsystem from executable code, proves that decimation from $K_{\text{arb}}=5 \to 10$ provides $2.800000\text{ FP/step}$ of direct net saving, evaluates off-policy skip maps and decision staleness on deterministic K2 traces, grounds supervisory switching in foundational control literature, and preregisters a concurrent 3-arm confirmatory experiment (`LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01`) on 30 fresh independent seeds (`1971..2000`).

**No new stochastic streams were executed in this stage.**
Canonical `src/` and `tests/` remain untouched.
Canonical pytest suite passes 124/124.

---

## Answers to the 35 Required Design & Audit Questions (Section D19)

### 1. What is the exact corrected K2 resource decomposition?
- Recurrent Shadow Saving ($K_{\text{rec\_fwd}}=1 \to 2$): **`9.000000 FP/step`**
- Live Linear Base & Tap Saving: **`1.201151 FP/step`**
- Search Probe & Management Saving: **`0.001025 FP/step`**
- Candidate Direct Observation & Learning Saving: **`0.010659 FP/step`**
- Candidate Descendant Arbitration Saving: **`0.000000 FP/step`**
- **Sum of Orthogonal Components:** **`10.212835 FP/step`**
- Authoritative Level-1 Total Saving: **`10.212835 FP/step`**
- **Machine Residual:** **`0.000000 FP/step`** (exact closure).

### 2. Is candidate saving 0.010659 or 0.011259, and why?
Candidate saving is **`0.010659 FP/step`** (`0.01065873015873`). The value $0.011259$ was a narrative drafting typo in the final report of the seal audit ($9.000 + 1.201151 + 0.001025 + 0.011259 = 10.213435 \ne 10.212835$), resulting from an intermediate calculation ($0.021317 - 0.010058$). The machine-readable data in `K2_RESOURCE_SEAL_RECONCILIATION.csv` has always been $0.010659$, which yields zero residual.

### 3. What does current K_arb actually equal in executable code?
In executable code (`run_k2_confirmation.py` line 179 and `scratch/run_v02_correlation_search_compaction.py`), `self.K_arbitration = 5`. It is strictly a discrete integer modulo clock (`step_count % 5 == 0`).

### 4. Where did historical K_arb=2.5 originate?
Originated in `RESOURCE_ACCOUNTING_01_FINAL_REPORT.md` (line 97) as an *average query frequency diagnostic* ("mean query frequency = 5.5 queries/step: 2.5 active taps + 1.0 candidate probe + 2.0 provisional shadow queries"). It described average active tap occupancy, not a fractional modulo clock.

### 5. What exact operations are controlled by K_arb?
Inside `if self.step_count % self.K_arbitration == 0:`:
1. Counterfactual error quadruplet construction ($e_{\text{base}}, e_D, e_R, e_{DR}$): 8 FP.
2. Conditional gain calculation ($g_d, g_r, g_{d|br}, g_{r|bd}$): 4 FP.
3. EMA gain filtering (4 EMAs, $0.98 \times \text{ema} + 0.02 \times g$): 16 FP.
4. Active tap and recurrent unit eviction checks ($step > 300, \text{ema} < \text{thresh}$): 4 INT.
5. Dual occupancy resolution and candidate promotion checks: 7 INT.
6. Stale candidate pruning ($stream\_age > 150, evidence < 0.02$): 2 INT.

### 6. How many FP does one arbitration event cost?
Exactly **`28.0 FP`** per execution event ($8 + 4 + 16$).

### 7. Is arbitration cost occupancy-independent?
**YES.** Exactly $28.0\text{ FP}$ is logged unconditionally on every arbitration trigger (`self.shadow_res.fp_flops += 28.0`), regardless of candidate pool size or active tap count.

### 8. What is current arbitration FP/step in the K2 branch?
At $K_{\text{arb}}=5$, evaluation rate is $1/5 = 0.20\text{ events/step}$. Total compute: $28.0 \times 0.20 = \mathbf{5.600000\text{ FP/step}}$.

### 9. Does K_arb=10 actually project to 2.8 FP/step?
**YES.** At $K_{\text{arb}}=10$, rate is $1/10 = 0.10\text{ events/step}$. Total compute: $28.0 \times 0.10 = \mathbf{2.800000\text{ FP/step}}$. Direct net saving is exactly **`2.800000 FP/step`**.

### 10. What scheduler overhead is added?
**0 FP ops.** Integer overhead is 0 additional ops relative to $K=5$, as both evaluate a single integer modulo check (`step_count % K == 0`).

### 11. What is projected K2+K10 total compute?
$$101.023283 - 2.800000 = \mathbf{98.223283\text{ FP/step}}.$$

### 12. What projected headroom remains below 100?
$$100.000000 - 98.223283 = \mathbf{1.776717\text{ FP/step}}.$$

### 13. Is that headroom analytical or validated?
**ANALYTICAL ONLY.** It is a static direct-cost projection before downstream behavioral and occupancy effects. Robust headroom is NOT established until empirically validated.

### 14. What is maximum arbitration decision staleness at K10?
Maximum periodic staleness under $K=10$ is **`9 stream steps`** (mean staleness = **`4.5 steps`**). Maximum incremental latency floor is **`+5 stream steps`**.

### 15. How many K5 arbitration evaluations actually change a decision?
From trace analysis across all 14 tasks ($16,800$ evaluations), only **`0.45%`** of evaluations change structural allocation (promotions or evictions).

### 16. How many would be skipped by K10?
$K=10$ skips exactly $50\%$ of evaluations (600 out of 1200 per 6000-step run). Across skipped evaluations, over **`99.4%`** were identical redundant decisions.

### 17. Are meaningful decisions temporally clustered?
**YES, HIGHLY CLUSTERED.** Decisions cluster heavily during initial startup ($t < 500$), abrupt regime transitions ($t \approx 3000$ in $I_{11}..I_{14}$), and post-quiescent reactivation ($t \approx 4000$ in $I_7$). Steady-state regimes exhibit virtually zero structural state changes.

### 18. Are switching tasks disproportionately exposed?
**YES.** Tasks $I_{11}..I_{14}$ experience structural shifts at $t=3000$, where decimation introduces up to $+5$ steps of detection latency. However, the preregistered switching margin is $+50$ steps, giving a $10\times$ safety buffer.

### 19. Could slower arbitration increase dual occupancy?
**YES.** On tasks like $I_{10}$ and $I_9$, delayed eviction of a stale module can prolong dual occupancy by up to 5 steps, slightly increasing live compute.

### 20. Could slower arbitration delay useful promotions?
**YES.** A candidate satisfying promotion criteria must wait for the next periodic evaluation, adding up to 5 steps of promotion latency.

### 21. Could slower arbitration reduce churn benignly?
**YES.** Slower evaluation filters high-frequency noise, acting as an implicit low-pass filter that prevents oscillatory promotion/eviction chattering.

### 22. Does literature support treating arbitration frequency as a dynamical quantity?
**YES.** Foundational control literature (Narendra & Balakrishnan 1994, 1997; Morse et al. 1992; Hespanha & Morse 1999) establishes that supervisory switching cadence directly impacts transient dynamics, dwell time, and stability.

### 23. Does literature prove K10 is safe for LEBRE?
**NO.** Literature provides conceptual precedent, NOT a mathematical guarantee for LEBRE. Safety remains an empirical LEBRE-specific hypothesis.

### 24. Why is fixed K10 tested before event-triggered arbitration?
Fixed $K=10$ is a minimal, single-variable intervention with zero added hyperparameters or state-dependent branching. Event-triggered arbitration introduces complex thresholds that violate the single-intervention constraint.

### 25. Why are three concurrent arms required?
- Arm A0 ($K_{\text{rec}}=1, K_{\text{arb}}=5$): End-to-end baseline.
- Arm A1 ($K_{\text{rec}}=2, K_{\text{arb}}=5$): K2 replication check.
- Arm A2 ($K_{\text{rec}}=2, K_{\text{arb}}=10$): Combined candidate.
Concurrent pairing on the same seed cohort eliminates cross-cohort noise and enables rigorous causal attribution.

### 26. Why is A2 vs A0 the primary behavioral contrast?
Because K2 already consumed part of the $+0.0100$ practical non-inferiority margin ($\Delta \approx +0.0027$). Testing A2 vs A1 alone could pass while compound degradation relative to canonical v0.1 exceeds $+0.0100$.

### 27. Why is A2 vs A1 still necessary?
Necessary for causal attribution: if A2 exhibits performance shifts, A2 vs A1 isolates whether arbitration decimation was the specific cause.

### 28. What is the future strict resource gate?
Arm A2 Grand Mean Total Online Compute $\le \mathbf{100.000000\text{ FP/step}}$. No rounding permitted.

### 29. What is the future end-to-end predictive gate?
Paired seed-level aggregate $\Delta \text{NMSE}(A2 - A0)$ one-sided 95% upper confidence bound $< \mathbf{+0.010000}$.

### 30. Which temporal mechanisms are mandatory?
- Continuous latent tracking ($I_6$): $\Delta \le +0.010000$.
- Quiescence retention ($I_7$): $\Delta \le +0.010000$.
- Hybrid complementarity ($I_9$): $G_{D|B+R} > 0 \land G_{R|BD} > 0$.
- Directional switching ($I_{11}..I_{14}$): recovery latency $\Delta \le +50$ steps.

### 31. How will I10 be treated without reopening Gate 6?
Historical Gate 6 status remains permanently `FAIL`. On $I_{10}$, $A0, A1, A2$ are observed descriptively (`frac_both`, `redundant_dual_rate`, `live_fp`, modal state) without modifying metric definitions or thresholds.

### 32. Is early rejection still excluded?
**YES.** Early rejection is mathematically insufficient alone ($\sim 0.885\text{ FP}$ gross saving vs $1.023\text{ FP}$ deficit) and is excluded to maintain single-intervention discipline.

### 33. Is live-linear modification still excluded?
**YES.** Live linear filtering is the primary predictive foundation with zero proven waste. Modifying it is forbidden.

### 34. Is the future study single-intervention relative to K2?
**YES.** Arm A2 differs from confirmed K2 parent (Arm A1) by exactly one parameter: $K_{\text{arb}}: 5 \to 10$.

### 35. Is the future experiment authorized?
**YES.** Design authorization is granted: `K2_ARB10_COMPOSITION_DESIGN_AUTHORIZED`. All microcorrections are resolved, direct saving ($2.800000\text{ FP/step}$) exceeds the deficit ($1.023283\text{ FP/step}$), static headroom is $1.776717\text{ FP/step}$, and the 3-arm protocol is fully frozen.
