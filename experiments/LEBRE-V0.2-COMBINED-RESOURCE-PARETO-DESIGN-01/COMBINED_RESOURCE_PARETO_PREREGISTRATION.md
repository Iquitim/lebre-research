# Preregistration: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

**Stage ID:** `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01`  
**Governance:** Strict Confirmatory Experimental Protocol  
**Status:** PREREGISTERED — NOT YET EXECUTED

---

## 1. Experimental Rationale & Three-Arm Concurrent Pairing (C4, C5)

To establish whether combining K=2 recurrent decimation with K=10 arbitration decimation achieves strict resource compliance ($\le 100.0\text{ FP/step}$) without exceeding the canonical behavioral degradation margin ($+0.0100$), three concurrent arms must be executed on the **same fresh seed cohort**:

1. **`Arm A0` (Original Reference):** $K_{\text{rec\_forward}}=1, K_{\text{arb}}=5$.
   - Re-establishes the un-decimated baseline on the new cohort.
2. **`Arm A1` (Confirmed K2 Parent):** $K_{\text{rec\_forward}}=2, K_{\text{arb}}=5$.
   - Confirms that K2 behavior and resource characteristics replicate.
3. **`Arm A2` (Combined Candidate):** $K_{\text{rec\_forward}}=2, K_{\text{arb}}=10$.
   - Evaluates the combined candidate architecture.

### Why Three Arms are Imperative:
- **`A1 vs A0` (Replication Contrast):** Confirms that K2 maintains non-inferiority on fresh seeds ($\Delta \approx +0.0027$).
- **`A2 vs A1` (Local Causal Contrast):** Isolates the pure incremental behavioral and computational effect of arbitration decimation ($K=5 \to 10$).
- **`A2 vs A0` (Primary End-to-End Gate):** Tests whether the total compound degradation of both interventions remains within the frozen $+0.0100$ practical non-inferiority margin. Historical cross-cohort arithmetic is forbidden.

---

## 2. Statistical Cohort & Inferential Design (C12, C13, D10, D11)

- **Inferential Unit:** The independent random seed ($N=30$).
- **Cohort Block:** Fresh independent contiguous seeds **`1971..2000`** ($N=30$). (Verified: completely disjoint from previous seeds $1401..1970$).
- **Benchmark Coverage:** All 14 canonical benchmark tasks ($I_1..I_{14}$).
- **Total Executions:** $30\text{ seeds} \times 14\text{ tasks} \times 3\text{ arms} = \mathbf{1,260\text{ runs}}$ ($7,560,000\text{ model-stream steps}$).
- **Primary Behavioral Test Statistic:**
  $$\Delta_{\text{end-to-end}, s} = \frac{1}{14} \sum_{i=1}^{14} \text{NMSE}_{A2, s, i} - \frac{1}{14} \sum_{i=1}^{14} \text{NMSE}_{A0, s, i}.$$
  - Test: Paired one-sided Student's $t$-test ($H_0: \mu_{\Delta} \ge +0.0100$ vs $H_1: \mu_{\Delta} < +0.0100$).
  - Decision Rule: Reject $H_0$ if $t < -1.6991$ and upper 95% CI bound $< +0.010000$.

---

## 3. Strict Resource Gate (C18, C19)

- **Metric:** Grand mean total online compute of Arm A2 across all $420$ runs:
  $$\text{Mean Total Online FP}_{A2} \le \mathbf{100.000000\text{ FP/step}}.$$
- **No Rounding Permitted:** Stored double precision determines pass/fail.

---

## 4. Mandatory Secondary & Temporal Mechanism Gates (C23–C27)

1. **Continuous Latent Tracking ($I_6$):** $\text{NMSE}_{A2} - \text{NMSE}_{A0} \le +0.010000$.
2. **Quiescent Retention ($I_7$):** $\text{NMSE}_{A2} - \text{NMSE}_{A0} \le +0.010000$.
3. **Hybrid Complementarity ($I_9$):** $G_{D|B+R} > 0$ and $G_{R|B+D} > 0$ on A2.
4. **Directional Switching Latency ($I_{11}..I_{14}$):**
   $$\text{Switching Latency}_{A2} - \text{Switching Latency}_{A0} \le \mathbf{+50\text{ stream steps}}.$$

---

## 5. Non-Interfering Off-Policy K5 Oracle Diagnostic (C29–C31)

Arm A2 will execute an optional diagnostic oracle during simulation:
- Evaluates what the $K=5$ arbitration decision would have been at odd steps ($step \% 10 == 5$).
- **Strict Isolation Invariant:** The oracle produces telemetry only. It NEVER mutates model state, never triggers promotions/evictions, and never affects predictions.
- **Resource Accounting:** All oracle operations are excluded from deployable resource accounting (`DEPLOYED_FP`).
