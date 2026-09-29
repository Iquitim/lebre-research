# Root Cause Analysis: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

### Issue 1: Switching Contrast Conflation on Task I11
- **Parent Claim:** Task $I_{11}$ passed switching latency tolerance with $\Delta = +19.83\text{ steps} \le +50\text{ steps}$.
- **Raw Level-1 Reality:** Mean latencies are $A0 = 385.27, A1 = 441.60, A2 = 461.43$. The preregistered end-to-end gate is $A2 - A0 \le +50\text{ steps}$. $A2 - A0 = +76.17\text{ steps} > +50\text{ steps} \implies \mathbf{FAIL}$.
- **Root Cause:** Contrast conflation. The parent report evaluated $A2 - A1$ ($+19.83$) against the $\le +50$ threshold instead of $A2 - A0$ ($+76.17$).
- **Impact:** Both $I_{11}$ and $I_{12}$ fail the end-to-end switching guardrail.

### Issue 2: Conflation of Historical and Concurrent Resource Projections
- **Parent Claim:** Narrative used $-1.265\text{ FP/step}$ and $+0.917\text{ FP/step}$ interchangeably as "indirect savings".
- **Raw Level-1 Reality:** $-1.265\text{ FP}$ is the residual relative to the historical projection ($98.22\text{ FP}$), whereas $+0.917\text{ FP}$ is the true concurrent causal indirect saving relative to Arm A1 ($100.67 - 2.80 = 97.87\text{ FP}$).
- **Root Cause:** Baseline conflation between cross-cohort historical design estimates and within-cohort concurrent causal attribution.

### Issue 3: Stale Narrative Live FP Values
- **Parent Claim:** Parent narrative cited $A1 = 74.25$ and $A2 = 73.34\text{ FP/step}$.
- **Raw Level-1 Reality:** Authoritative means are $A1 = 74.141956$ and $A2 = 73.222214\text{ FP/step}$ (difference $0.919742\text{ FP/step}$).
- **Root Cause:** Stale intermediate text drafting prior to finalized Level-1 aggregation.

### Issue 4: EMA Time Constant Rounding Discrepancy
- **Parent Claim:** Parent report cited $\tau_{\text{events}} = 49.4965\text{ events}$.
- **Raw Level-1 Reality:** Exact double-precision arithmetic gives $-1 / \ln(0.98) = 49.498316\text{ events}$.
- **Root Cause:** Rounding approximation of intermediate logarithmic values.

### Issue 5: Causal Mechanism Overreach
- **Parent Claim:** Narrative claimed the failure mechanism was "isolated" as EMA timescale distortion.
- **Raw Level-1 Reality:** The single intervention ($K_{\text{arb}}: 5 \to 10$ with $\alpha=0.02$) simultaneously halved evaluation frequency and doubled stream filter memory.
- **Root Cause:** Mechanism scope overreach. The two factors form a coupled mechanism and cannot be causally separated without a factorial trial.
