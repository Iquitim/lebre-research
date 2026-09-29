# Specification: Multirate Policy Candidates (MR1, MR2, MR3)

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Candidate Policy MR1: Fast Sensing, Slow Adaptation

### 1.1 Architectural Rationale
Structural discovery requires rapid scanning of the input space to detect newly emerged correlation signals, while parameter adaptation (LMS/RTRL) and arbitration filters operate over statistical distributions that integrate evidence over multiple timesteps.
- Probing is cheap ($8.0\text{ FP}$ for 2 pairs) and can execute relatively frequently ($K_{\text{probe}} = 2$).
- Recurrent state propagation is essential for dynamical continuity ($K_{\text{rec\_prop}} = 1$).
- Expensive RTRL parameter learning ($22.0\text{ FP}$) and candidate LMS updates ($8.0\text{ FP}$) are executed at a decimated cadence ($K_{\text{rec\_learn}} = 5$, $K_{\text{cand\_learn}} = 5$).
- Counterfactual arbitration evaluates every $K_{\text{arb}} = 5$ steps, conditioned on evidence freshness ($\tau \le 2$).

### 1.2 Clock & Cadence Specifications for MR1
- $K_{\text{probe}} = 2$ ($d_{\text{probe}} = 0.50$)
- $K_{\text{cand\_obs}} = 2$ ($d_{\text{cand\_obs}} = 0.50$)
- $K_{\text{cand\_learn}} = 5$ ($d_{\text{cand\_learn}} = 0.20$)
- $K_{\text{rec\_prop}} = 1$ ($d_{\text{rec\_prop}} = 1.00$, continuous)
- $K_{\text{rec\_learn}} = 5$ ($d_{\text{rec\_learn}} = 0.20$)
- $K_{\text{arb}} = 5$ ($d_{\text{arb}} = 0.20$, synchronized with candidate learning)
- $F_{\text{router}} = 0.0\text{ FP}$ (deterministic modulo integer counters)
- Expected compute: $81.17 + (0.50 \times 8.0) + (0.50 \times 2.0) + (0.20 \times 8.0) + (1.00 \times 12.0) + (0.20 \times 22.0) + (0.20 \times 28.0) = 81.17 + 4.0 + 1.0 + 1.6 + 12.0 + 4.4 + 5.6 = \mathbf{109.77\text{ FP/step}}$ (requires further decimation to fit $\le 100.0\text{ FP}$).
- Refined Feasible MR1 ($K_{\text{probe}} = 5, K_{\text{cand}} = 5, K_{\text{rec\_prop}} = 1, K_{\text{rec\_learn}} = 10, K_{\text{arb}} = 10$):
  $F_{\text{shadow}} = 1.6 + 0.4 + 1.6 + 12.0 + 2.2 + 2.8 = \mathbf{20.6\text{ FP}} \implies F_{\text{total}} \approx \mathbf{99.8\text{ FP/step}}$.

---

## 2. Candidate Policy MR2: Data-Selective Adaptation

### 2.1 Architectural Rationale (Inspired by Diniz, 2018)
Rather than decimating parameter updates blindly, candidate weights and recurrent weights are updated **only when active innovations exceed a noise threshold**:
- State propagation (`9A`) remains continuous ($K=1$).
- Probing executes periodically ($K_{\text{probe}} = 5$).
- Candidate and recurrent parameter updates execute only if candidate innovation satisfies:
  $$\Delta e_{\text{cand}}^2 = (y - \hat{y}_{\text{base}})^2 - (y - \hat{y}_{\text{cand}})^2 > \gamma_{\text{innov}} = 0.010$$
  If $\Delta e^2 \le \gamma_{\text{innov}}$, the update is skipped (`HOLD_STATE`, zero parameter update compute).
- Router cost: 1 FP subtraction + 1 FP comparison ($2\text{ FP/step}$).

---

## 3. Candidate Policy MR3: Temporal-Evidence Routed Multirate

### 3.1 Resolving the $I_2$ False-Wake Mechanism
Study $S_3$ failed on Task $I_2$ (static nonlinear control) because large prediction error ($\ell_{\text{live}} \approx 0.35$) tripped the Page-Hinkley sentinel, mistakenly interpreting static nonlinearity as a temporal regime shift.
To prevent this, MR3 introduces a cheap $\mathcal{O}(1)$ **causal temporal correlation statistic**:

$$r_e(t) = (1 - \beta) r_e(t-1) + \beta \left(e_{\text{live}}(t) \cdot e_{\text{live}}(t-1)\right)$$
$$C_{\text{temporal}}(t) = \frac{r_e(t)}{\sigma_e^2(t) + \epsilon}$$

### 3.2 Routing Logic
- If $C_{\text{temporal}} > \theta_{\text{temporal}} = 0.15$: Unresolved serial temporal structure is detected. Probing and candidate evaluation are activated at full rate.
- If $C_{\text{temporal}} \le \theta_{\text{temporal}}$: Residual is serially uncorrelated (white noise or memoryless static error as in $I_2$). Temporal exploration sleeps (`is_temporal_awake = False`).
- **Anti-Starvation Heartbeat:** If the router sleeps for $H = 100$ steps without waking, a forced single-step probe burst executes to ensure non-starvation.
- **Strict Boundary:** The router may **only authorize temporal shadow observation**. It is **strictly prohibited from directly promoting or evicting structures**. All promotions remain governed by counterfactual arbitration.

### 3.3 Router Resource Footprint
- Persistent memory: $r_e$ ($8\text{ B}$ float64), $e_{\text{prev}}$ ($8\text{ B}$ float64), heartbeat counter ($2\text{ B}$) = $18\text{ Bytes}$.
- Compute per step: 1 multiplication ($e_t \cdot e_{t-1}$) + 2 EMA operations ($4\text{ FP}$) + 1 ratio ($1\text{ FP}$) = **$6.0\text{ FP FLOPs/step}$**.
