# EXP-0002: Final Diagnosis

## Primary Diagnosis
`TARGETING_IMPORTANT_BUT_SCORE_WEAK`

## Detailed Causal Analysis

### 1. The Oracle Proof: Candidate Targeting Is the True Frontier
The diagnostic control **E4 (Oracle Candidate Targeting)** delivers the most profound result of the entire project so far:
- Full-Support Occupancy: **94.4% ± 3.5%** (vs E0: **27.8% ± 17.1%**)
- Regime-2 MSE: **0.0139 ± 0.0016** (vs Dense NLMS: **0.0339 ± 0.0071**, a **2.4x advantage**)
- Stable Full-Support Latency: **57.0 ± 35.5 steps** (vs E0: **723.2 steps**)
- Cumulative Omitted Energy: **122.4 ± 38.4** (an **18-fold reduction** over E0's 2,161.8)
- Average Compute: **16.9% of Dense** (101.8 FLOPs/step)
- Total Cumulative Probes: **10,000** (Identically budget-matched, $\Delta = 0$).

**Conclusion**: Structural capacity ($K_{\max}=10$), parameter estimation (NLMS), evidence accumulation ($n_{\min}=8$), and the 10,000 probe budget are **completely sufficient**. If candidate probes are directed to omitted true features, structural recovery takes fewer than 60 steps, and predictive error immediately matches the theoretical sparse noise floor.

---

### 2. Why Incumbent Protection (E2) Failed: Case F Confirmed
Section 54 specified:
> *If protection improves retention but worsens discovery because noise fills the buffer: protection duration / victim eligibility is a tradeoff.*

In E2:
- Full-support occupancy collapsed from **27.8% down to 7.1% ± 15.8%**.
- Regime-2 MSE exploded to **2.7128 ± 2.5188**.
- When structural change occurs, residual error is high. Spurious noise candidates cross the promotion threshold and are granted 40 steps of immunity. Because all 10 buffer slots quickly fill with protected noise features, Option A full-buffer deferral blocks newly discovered true features from entering.
- **Verdict on Incumbent Protection**: `DEFER` / `REMOVE`. Blind protection creates buffer congestion.

---

### 3. Why Causal Targeting (E1) Succeeded Partially but Stalled: Case D Confirmed
Section 52 specified:
> *If E4 dramatically outperforms E1, then current priority score remains poor even if targeting itself is important.*

- In Seeds 42, 789, and 1024, E1 lifted full-support occupancy to **42% – 85%** and slashed R2 MSE to **0.0113 – 0.0160**.
- However, on Seed 123, E1 scored 0.0% occupancy because the simple score $\text{score}_j = |\overline{\text{corr}}_j| \cdot \frac{n_j}{n_j+2}$ locked onto early noise candidates that accumulated misleading correlations during the initial error spike.
- With 60% of probes committed to priority candidates, true candidates 7 and 92 were starved of probes, preventing them from reaching $n_{\min}=8$.

---

### 4. Component Status & Next Steps
- `CANDIDATE_PRIORITY`: `KEEP` (Proved by E4 to be the definitive bottleneck to reaching 94% occupancy at 17% compute; the priority scoring formula must be upgraded to resist early noise lock-in).
- `TEMPORARY_PROTECTION`: `DEFER` (Traps noise and locks the buffer).
- `PROBE_BANK`: `KEEP` (Maintains strict budget compliance).
- **Status**: `NO_GO` for the current priority heuristic; **CLEAR ARCHITECTURAL PATHWAY ESTABLISHED**.
