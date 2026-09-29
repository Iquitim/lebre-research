# Confirmatory Protocol: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Stage ID:** `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01`  
**Governance:** Strict 3-Arm Confirmatory Protocol  
**Cohort:** $N=30$ fresh seeds (`1971..2000`), 14 benchmark tasks ($I_1..I_{14}$), 3 concurrent arms ($A0, A1, A2$). Total runs: 1,260.

## Core Rules:
1. Single new intervention: $A2$ differs from $A1$ only by $K_{\text{arb}}: 5 \to 10$.
2. Primary decision gate: End-to-end non-inferiority ($A2 - A0 < +0.010000$ 95% upper bound).
3. Primary resource gate: Arm A2 total compute $\le 100.000000\text{ FP/step}$ (unrounded).
4. No DEV phase, no grid searching, no parameter tuning.
