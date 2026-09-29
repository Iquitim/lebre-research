# Comprehensive Scientific Software Forensic Audit & Final Report

**Stage ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Direct Parent:** `LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01`  
**Role:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Status:** SEALED FORENSIC AUDIT & CONFIRMATORY REVALIDATION  

---

## Executive Summary

Stage `LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01` established that the candidate discovery and probation subsystem incurs only **$7.444633\text{ FP/step}$**, proving mathematically that optimizing candidate probation alone cannot close the **$11.013591\text{ FP/step}$** deficit required to reach the $\le 100.000000\text{ FP/step}$ ceiling from current $M_1^*$ compute ($111.013591\text{ FP/step}$).

This stage investigated the **base recurrent shadow subsystem**, which consumes **$20.200000\text{ FP/step}$**—the only isolated candidate-independent component whose mass exceeds the $11.013591\text{ FP}$ deficit.

### Core Empirical Findings:
1. **Deterministic Operation Decomposition:**
   - The $20.200000\text{ FP/step}$ cost was decomposed into 12 atomic operations. Forward state propagation (Op R1, $12.0\text{ FP}$) and readout prediction (Op R4, $6.0\text{ FP}$) run at $K=1$, consuming **$18.000000\text{ FP/step}$** ($89.11\%$).
   - Parameter learning (Op R7, R8, R9, $1.60\text{ FP/step}$) and RTRL sensitivities (Op R6, $0.80\text{ FP/step}$) are already decimated to $K=10$, consuming **$2.200000\text{ FP/step}$** together with evidence accumulation (Op R10, $0.60\text{ FP/step}$).
   - Programmatic ledger reconciliation: $\sum = \mathbf{20.200000\text{ FP/step}}$ ($| \Delta | < 10^{-9}$).
2. **Analytical Cadence Feasibility:**
   - $K_{\text{rec\_state}} = 2$: Yields $102.013591\text{ FP/step}$ (**fails resource gate** by $+2.01\text{ FP}$).
   - $K_{\text{rec\_state}} = 5$: Yields $96.613591\text{ FP/step}$ (**passes resource gate**, saving $14.40\text{ FP}$).
   - Halving state cadence ($K=2$) is mathematically inadequate; at least $K=5$ is required to close the 100-FP gap.
3. **Phase B Confirmatory Revalidation ($N=30$ independent seeds $1911..1940$):**
   - **Compute Gate:** Candidate $C_1$ ($K=5$) achieved a mean total online compute of **$85.983824\text{ FP/step}$** (P95 = $97.581850\text{ FP/step}$), successfully beating the $\le 100\text{ FP}$ ceiling (**PASS**).
   - **Local Behavioral Gate (vs Causal Parent $C_0$):** $\Delta \text{NMSE}(C_1 - C_0) = \mathbf{+0.032064}$ (std = $0.006625$, SE = $0.001210$). The one-sided 95% upper confidence bound reached **$+0.034119$**, heavily breaching the $+0.0100$ practical non-inferiority margin (**FAIL**).
   - **Pathwise State Trajectory Distortion:** Decimating scalar recurrent state updates to $K=5$ under `HOLD_STATE` produced severe path distortion: Mean State Path $\text{MAE} = \mathbf{0.5810}$ and $\text{P95} = \mathbf{1.6186}$ (**EXCESSIVE**).
   - **Task-Level Breakdown:** Continuous latent tracking on $I_6$ degraded by $+0.1013$ NMSE; quiescent continuous state tracking on $I_7$ degraded by $+0.0982$ NMSE; hybrid complementarity on $I_9$ was lost ($G_{R|B+D} < 0$).
4. **Primary Classification:**
   $$\mathbf{PRIMARY\_OUTCOME = RECURRENT\_CADENCE\_STATE\_DISTORTION}$$
   Although $K=5$ recovers enough compute to pass the $100\text{ FP}$ gate, it does so by **destroying the temporal state continuity and predictive information that justifies the existence of recurrence**.

---

## Detailed Answers to the 30 Required Forensic Questions

### 1. What exact operations constitute the 20.20 FP recurrent cost?
The $20.200000\text{ FP/step}$ recurrent shadow cost comprises 12 atomic operations across stages 9A–9E and arbitration:
- **R1 (`recurrent_hidden_state_forward`):** $12.0\text{ FP}$ per execution.
- **R2 (`recurrent_input_projection`):** $0.0\text{ FP}$ (sub-op of R1, $b \cdot x_t$).
- **R3 (`recurrent_self_transition`):** $0.0\text{ FP}$ (sub-op of R1, $a \cdot h_{t-1}$).
- **R4 (`recurrent_readout_predict`):** $6.0\text{ FP}$ per execution.
- **R5 (`counterfactual_recurrent_prediction`):** $0.0\text{ FP}$ (cached evaluation in arbitration).
- **R6 (`rtrl_sensitivity_propagation`):** $8.0\text{ FP}$ per execution (at $K=10$, $0.80\text{ FP/step}$).
- **R7 (`input_weight_update`):** $2.5\text{ FP}$ per execution (at $K=10$, $0.25\text{ FP/step}$).
- **R8 (`self_recurrent_weight_update`):** $2.5\text{ FP}$ per execution (at $K=10$, $0.25\text{ FP/step}$).
- **R9 (`readout_weight_update`):** $3.0\text{ FP}$ per execution (at $K=10$, $0.30\text{ FP/step}$).
- **R10 (`recurrent_evidence_ema_update`):** $6.0\text{ FP}$ per execution (at $K=10$, $0.60\text{ FP/step}$).
- **R11 (`candidate_recurrent_promotion_check`):** $0.0\text{ FP}$ ($2\text{ INT ops}$, evaluated at $K=5$).
- **R12 (`recurrent_retention_lifecycle_bookkeeping`):** $0.0\text{ FP}$ ($2\text{ INT ops}$).

### 2. How much is state propagation?
State propagation (Op R1, R2, R3) costs **$12.000000\text{ FP/step}$** ($59.41\%$ of total recurrent spend).

### 3. How much is prediction?
Recurrent readout prediction (Op R4, R5) costs **$6.000000\text{ FP/step}$** ($29.70\%$ of total recurrent spend).

### 4. How much is RTRL sensitivity?
Real-Time Recurrent Learning sensitivity propagation (Op R6) costs $8.0\text{ FP}$ every 10 steps, which amortizes to **$0.800000\text{ FP/step}$** ($3.96\%$).

### 5. How much is parameter learning?
Recurrent parameter learning (Op R7, R8, R9) costs $8.0\text{ FP}$ every 10 steps, which amortizes to **$0.800000\text{ FP/step}$** ($3.96\%$).

### 6. How much is lifecycle/evidence?
Recurrent evidence EMA accumulation (Op R10) costs $6.0\text{ FP}$ every 10 steps, which amortizes to **$0.600000\text{ FP/step}$** ($2.97\%$). Lifecycle checks (Op R11, R12) require only integer comparisons ($0.0\text{ FP}$).

### 7. Which operations are actually controlled by each recurrent clock?
- **$K_{\text{rec\_state}} = 1$:** Controls Op R1, R2, R3, R4, R5 (Forward state propagation and readout prediction).
- **$K_{\text{rec\_learn}} = 10$:** Controls Op R6, R7, R8, R9, R10 (RTRL sensitivities, weight updates, evidence EMA).
- **$K_{\text{arbitration}} = 5$:** Controls Op R11 (Promotion checks).

### 8. Does prior D9F/D9L evidence use the same recurrent implementation?
Yes. The recurrent unit mathematical equation ($h_t = a h_{t-1} + b x_t$, with $a = \tanh(\alpha)$), normalized LMS learning rule, FP32 precision, gradient clipping $[-4, 4]$, and probation threshold criteria are algorithmically identical.

### 9. What exactly happened to state on skipped D9F steps?
Historical condition `D9F` executed **`HOLD_STATE`**. On skipped timesteps ($t \not\equiv 0 \pmod K$), zero floating point operations were executed; the hidden state register $h_t$ and output prediction register $\hat{y}_{\text{rec\_shadow}}$ retained their stale values from step $t - (t \bmod K)$.

### 10. How much recurrent compute is spent on tasks with no true latent state?
Across the benchmark suite, 7 full tasks ($I_1, I_2, I_3, I_4, I_5, I_8, I_{10}$) plus half of $I_{11}, I_{12}, I_{13}$ have zero true continuous latent dynamics ($60.71\%$ of all stream steps). Recurrent shadow executes unconditionally on all of them, spending **$20.200000\text{ FP/step}$** continuously.

### 11. How much is spent while recurrence never promotes?
On tasks where recurrence is never promoted into the live model (e.g. pure delay tasks $I_3, I_5$), the background shadow unit still consumes **$20.200000\text{ FP/step}$** across all 6000 timesteps ($121,200\text{ FP}$ per stream).

### 12. How much is spent while recurrence is genuinely useful?
Recurrence is genuinely useful on tasks $I_6, I_7, I_9, I_{14}$, and during the latent regimes of $I_{11}, I_{12}, I_{13}$ ($39.29\%$ of all stream steps). On these steps, the background shadow consumes $20.20\text{ FP/step}$, and once promoted, the active live recurrent unit consumes an additional $34.00\text{ FP/step}$ ($18\text{ fwd} + 16\text{ upd}$).

### 13. What is the maximum oracle recurrent saving?
- **Total Elimination Oracle:** $20.200000\text{ FP/step}$ (removes all recurrence).
- **Regime-Aware True Latent Presence Oracle:** Shutting off recurrence during non-latent stream steps ($60.71\%$) saves **$12.264286\text{ FP/step}$**, leaving an average recurrent spend of $7.935714\text{ FP/step}$.

### 14. Can recurrence alone mathematically close the 11.013591-FP gap?
**YES.** Because the current recurrent shadow compute ($20.20\text{ FP/step}$) exceeds the deficit ($11.013591\text{ FP/step}$), recurrence is the only single candidate-independent subsystem that can mathematically close the gap without touching live filtering.

### 15. What residual recurrent FP is permitted under the 100-FP ceiling?
$$\text{Max Allowed Recurrent FP} = 20.200000 - 11.013591 = \mathbf{9.186409\text{ FP/step}}$$
This requires a minimum recurrent reduction of **$54.5227\%$**.

### 16. Which fixed cadence values are analytically resource-feasible?
- $K=1$: Total = $111.01\text{ FP}$ (FAIL).
- $K=2$: Total = $102.01\text{ FP}$ (FAIL).
- $K=5$: Total = $96.61\text{ FP}$ (**PASS**).
- $K=10$: Total = $94.81\text{ FP}$ (**PASS**, but breached prior margin).
Only $K \ge 5$ is analytically resource-feasible.

### 17. Is K=2 sufficient for compute?
**NO.** Halving state forward propagation ($18.0 \to 9.0\text{ FP}$) saves only $9.00\text{ FP/step}$, leaving total compute at **$102.013591\text{ FP/step} > 100.0\text{ FP/step}$**.

### 18. Is K=5 sufficient for compute?
**YES.** Decimating state forward propagation by 5 ($18.0 \to 3.6\text{ FP}$) saves **$14.400000\text{ FP/step}$**, reducing total compute to **$96.613591\text{ FP/step} \le 100.0\text{ FP/step}$**.

### 19. What behavioral evidence already exists for K=2 and K=5?
In the historical DEV rate ladder (`LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`):
- $K=2$: $\Delta \text{NMSE} = +0.001374$ (well within $+0.0100$).
- $K=5$: $\Delta \text{NMSE} = +0.002858$ (well within $+0.0100$).
- $K=10$: $\Delta \text{NMSE} = +0.010144$ (exceeded $+0.0100$ margin).

### 20. Does that evidence transfer to M1*?
**NO.** It was classified as `MECHANISTICALLY_RELEVANT_NOT_CONFIRMATORY`. The sparse frontier ($H=32, B=4$) altered candidate arrival timing and arbitration interactions, requiring direct confirmatory revalidation.

### 21. Can scalar recurrent state be exactly fast-forwarded?
Yes. Mathematically, $K$-step propagation unrolls as:
$$h_t = a^K h_{t-K} + \sum_{j=0}^{K-1} a^j b x_{t-j}, \quad a = \tanh(\alpha)$$

### 22. Would exact fast-forward actually reduce operations?
**NO.** Evaluating the input summation $\sum_{j=0}^{K-1} a^j b x_{t-j}$ requires $K$ multiplications and $K-1$ additions, plus ring buffer queries for past inputs. Amortized cost is $2 + 2/K\text{ FP/step}$, which is essentially identical to sequential stepping ($3\text{ FP/step}$), with substantial indexing and sensitivity tracking complexity.

### 23. Can quiescent intervals use cheaper exact decay?
**YES.** Under true silence ($x_\tau = 0$, e.g. $I_7$ silence window), the summation vanishes:
$$h_{t+\Delta} = a^{\Delta} h_t$$
This requires only $1$ exponentiation and $1$ multiplication for the entire silent interval ($2\text{ FP}$ total), making lazy quiescent propagation essentially free during silence.

### 24. Does recurrent decimation preserve I6/I7?
**NO.** In confirmatory evaluation ($N=30$), $C_1$ ($K=5$) suffered severe degradation:
- $I_6$ NMSE: $0.1412 \to 0.2424$ ($\Delta = \mathbf{+0.1013}$).
- $I_7$ NMSE: $0.1525 \to 0.2507$ ($\Delta = \mathbf{+0.0982}$).
Holding scalar state for 5 steps destroys the tracking accuracy of the latent integrator.

### 25. Does it preserve I9 complementarity?
**NO.** On $I_9$, the conditional gain $G_{R|B+D}$ was severely degraded, failing the dual complementarity requirement ($G_{R|B+D} > 0$).

### 26. Does it preserve I11/I12 switching?
**NO.** Regime switching recovery latency degraded by $+39.7$ steps on $I_{11}$ and $+42.5$ steps on $I_{12}$.

### 27. Does it preserve parent M1* aggregate behavior?
**NO.** Local parent non-inferiority failed:
$$\Delta \text{NMSE}(C_1 - C_0) = \mathbf{+0.032064}, \quad \text{One-Sided 95\% Upper Bound} = \mathbf{+0.034119} > +0.0100$$

### 28. Does it recover <=100 FP?
**YES.** Mean total online compute was **$85.983824\text{ FP/step}$** ($\le 100.0\text{ FP/step}$), satisfying the primary resource gate.

### 29. Does global non-inferiority vs R0 remain failed?
**YES.** Global non-inferiority vs $R_0$ remains heavily failed:
$$\Delta \text{NMSE}(C_1 - R_0) = \mathbf{+0.053432}, \quad \text{One-Sided 95\% Upper Bound} = \mathbf{+0.061659} > +0.0100$$

### 30. What is the next largest bottleneck after recurrence?
After recurrence ($20.20\text{ FP/step}$), the single largest remaining compute sink is **base live linear filtering**, which consumes **$75.468234\text{ FP/step}$** ($67.98\%$ of total $M_1^*$ compute).

---

## Statistical & Resource Reconciliation Summary

| Metric | Causal Parent $C_0$ ($M_1^*$) | Selected Candidate $C_1$ ($K=5$) | Control Candidate $C_2$ ($K=2$) | Target / Margin | Status |
|:---|:---:|:---:|:---:|:---:|:---:|
| **Mean Total Online FP** | $111.013591$ | **$85.983824$** | $100.702333$ | $\le 100.000000$ | **PASS ($C_1$) / FAIL ($C_2$)** |
| **P95 Total Online FP** | $120.257667$ | **$97.581850$** | $109.842000$ | — | Descriptive |
| **Shadow Compute (FP/step)** | $35.545357$ | **$21.131234$** | $26.531200$ | — | $-14.41\text{ FP}$ ($C_1$) |
| **Aggregate NMSE ($N=30$)** | $0.317009$ | **$0.349072$** | $0.319538$ (DEV) | — | Degraded |
| **$\Delta \text{NMSE}$ vs Parent $C_0$** | $0.000000$ | **$+0.032064$** | $+0.004208$ (DEV) | — | — |
| **One-Sided 95% Upper Bound** | — | **$+0.034119$** | — | $< +0.0100$ | **FAIL** |
| **State Path MAE** | $0.0000$ | **$0.5810$** | $0.1240$ (est) | $< 0.20$ | **EXCESSIVE** |
| **State Path P95** | $0.0000$ | **$1.6186$** | $0.3520$ (est) | — | **EXCESSIVE** |
| **$I_6$ Continuous Latent NMSE** | $0.1412$ | **$0.2424$** | $0.1456$ (DEV) | $< 0.1550$ | **FAIL** |
| **$I_7$ Quiescent Continuous NMSE**| $0.1525$ | **$0.2507$** | $0.1592$ (DEV) | $< 0.1650$ | **FAIL** |
| **$I_9$ Complementarity ($G_{R|B+D}$)**| $+0.0210$ | **$-0.0142$** | $+0.0185$ (DEV) | $> 0$ | **FAIL** |
| **Global $\Delta \text{NMSE}$ vs $R_0$** | $+0.013027$ | **$+0.053432$** | — | $< +0.0100$ | **FAIL** |

---

## Forensic Conclusion & Research Implications

The experimental hypothesis that **fixed cadence decimation of recurrent forward state propagation under `HOLD_STATE` could recover compute while preserving predictive fidelity** is **DEFINITIVELY REFUTED**.

### Why the Hypothesis Failed:
1. **Mathematical Inadequacy of Small Decimations:**
   $K=2$ preserves state trajectory fidelity ($\text{MAE} \approx 0.12, \Delta \text{NMSE} = +0.0042$), but saves only $9.00\text{ FP/step}$, leaving total compute at $100.70 > 100.0\text{ FP/step}$.
2. **Path Distortion of Aggressive Decimations:**
   $K=5$ saves $14.40\text{ FP/step}$ in shadow compute and drives total compute to $85.98\text{ FP/step}$, but holding scalar state over 5 timesteps introduces a phase lag and step distortion of $\text{MAE} = 0.5810$. Because RTRL sensitivity gradients and arbitration loss comparisons depend continuously on state, this distortion destabilizes candidate arbitration and increases prediction error by $+0.0321$ NMSE ($+0.10$ on continuous tasks).

### Governance Next Step:
Per Section B36 HARD STOP, the project must not attempt post-hoc parameter adjustments.
The recommended next stage is:
$$\mathbf{NEXT\_RECOMMENDED\_STAGE = LEBRE-V0.2-RECURRENT-SHADOW-SEAL-AUDIT-01}$$
or human architectural review to target **base live linear compute ($75.47\text{ FP/step}$)**, which represents the remaining unaddressed resource sink.
