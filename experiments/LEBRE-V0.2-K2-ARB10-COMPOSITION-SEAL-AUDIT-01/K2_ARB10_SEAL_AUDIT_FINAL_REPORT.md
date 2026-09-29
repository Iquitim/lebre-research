# Forensic Seal Audit Final Report: LEBRE-V0.2-K2-ARB10-COMPOSITION-SEAL-AUDIT-01

**Stage ID:** `LEBRE-V0.2-K2-ARB10-COMPOSITION-SEAL-AUDIT-01`  
**Direct Parent:** `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01`  
**Primary Audit Verdict:** **`K2_ARB10_NEGATIVE_RESULT_VALID_WITH_REPORTING_CORRIGENDA`**  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor & Adaptive Learning Researcher  
**Pytest Canonical Suite:** **`124 / 124 PASSED`**  

---

## 1. Executive Summary & Resolution of the 7 Central Seal Questions

### Q-A. Statistical Reproduction from Level-1 Raw Telemetry
**YES.** Using seed ($N=30$) as the independent inferential unit, all three paired contrasts reproduce exactly:
- **K2 Replication ($A1 - A0$):** Mean $\Delta = +0.003196$, 95% Upper Bound = **`+0.004477 < +0.010000`** ($p_{\text{NI}} = 3.21 \times 10^{-10}$) $\implies \mathbf{PASS}$.
- **Incremental Arbitration ($A2 - A1$):** Mean $\Delta = +0.011352$, 95% Upper Bound = **`+0.016960`**.
- **Primary End-to-End ($A2 - A0$):** Mean $\Delta = +0.014548$, 95% Upper Bound = **`+0.020204 > +0.010000`** ($p_{\text{NI}} = 0.9088$) $\implies \mathbf{FAIL}$.
The confirmatory negative result is statistically robust.

### Q-B. Certified End-to-End Switching Failures
Under the preregistered end-to-end gate ($A2 - A0 \le +50.0\text{ stream steps}$):
- **Task $I_{11}$:** $A0 = 385.27, A1 = 441.60, A2 = 461.43 \implies A2 - A0 = \mathbf{+76.17\text{ steps}} > +50.0 \implies \mathbf{FAIL}$.
- **Task $I_{12}$:** $A0 = 1859.30, A1 = 1904.97, A2 = 2072.93 \implies A2 - A0 = \mathbf{+213.63\text{ steps}} > +50.0 \implies \mathbf{FAIL}$.
- **Task $I_{13}$:** $A2 - A0 = \mathbf{-1.73\text{ steps}} \le +50.0 \implies \mathbf{PASS}$.
- **Task $I_{14}$:** $A2 - A0 = \mathbf{-398.27\text{ steps}} \le +50.0 \implies \mathbf{PASS}$.  
**Finding:** Both $I_{11}$ and $I_{12}$ fail switching. Parent reporting conflated $A2 - A1$ ($+19.83$) with $A2 - A0$ on $I_{11}$.

### Q-C. Exact Concurrent Causal Resource Saving
- Arm A1 Total FP: **`100.674818 FP/step`**.
- Arm A2 Total FP: **`96.957851 FP/step`**.
- Total Incremental Saving ($A1 - A2$): **`3.716967 FP/step`** ($100.0\%$).
- Direct Arbitration Saving: **`2.800000 FP/step`** ($75.33\%$).
- Downstream Indirect Structural Saving: **`0.916967 FP/step`** ($24.67\%$).

### Q-D. Double-Count Prevention & Field Semantics
Executable code audit confirms:
$$\text{candidate\_descendant\_fp} = \text{candidate\_direct\_fp} + \text{arbitration\_fp}$$
`candidate_descendant_fp` is an **inclusive field**. Summing exclusive components gives exactly total FP with **$0.000000\text{ FP}$ residual**. Double counting is completely prevented.

### Q-E. Mechanism Adjudication: Coupled Dynamics
The parent claim of an "isolated" mechanism is **too strong**. Decimating $K_{\text{arb}}: 5 \to 10$ holding $\alpha=0.02$ fixed simultaneously changed decision cadence (10 steps) and doubled effective stream memory ($\sim 250 \to \sim 500$ steps). These form a **strongly supported coupled mechanism**, but they cannot be causally separated from this experiment alone.

### Q-F. Task-Conditional Structural Under-Modeling
Under-modeling is **task-conditional**, not universal:
- On $I_{12}$ (`Latent_To_Delay`), delay-tap promotion was suppressed and delayed by $+168\text{ steps}$, causing severe switching error.
- On $I_{10}$, recurrent latching failed, dropping live compute by $8.2\text{ FP}$ but degrading NMSE by $+0.0297$.
- On $I_7$, degradation occurred with *higher* live compute ($83.66 \to 85.03$) and spurious lag duty.

### Q-G. Post-Seal Research Branch Recommendation
The most scientifically justified next step is **Branch A**:  
**`LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01`**  
Investigating $\alpha_{10} = 0.039600$ to preserve the stream-time filter pole ($247.49\text{ steps}$) under $K=10$, prior to introducing complex event-triggered routers.
