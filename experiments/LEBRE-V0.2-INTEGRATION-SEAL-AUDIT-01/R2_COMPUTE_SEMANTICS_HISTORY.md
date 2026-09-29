# Historical Provenance Audit: R2-FP Compute Semantics & Measurement Boundaries

**Study Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Subject:** Reconstruction of the Normative `R2_FP <= 100` Constraint Across Project Milestones  
**Auditor:** Independent Skeptical Senior Reviewer  
**Classification:** `SEMANTIC_AMBIGUITY_RECONCILED`  

---

## 1. Executive Summary

Audit Question C asks:
> **Determine what the historical `R2_FP <= 100` constraint was intended to bound: `LIVE_ONLY`, `TOTAL_ONLINE`, `STEADY_STATE_AFTER_DISCOVERY`, `AMORTIZED_WITH_DUTY_CYCLE`, or something else.**

The historical audit across Milestone 1, Milestone 2, and the post-M2 reconciliations establishes:
1. **The Historical Intent:** In Milestone 1 and Milestone 2 (`bench_01_locked_config.json`, `BENCH_01B_FINAL_REPORT.md`), `R2_FP <= 100` was defined as the **mean online floating-point operation count per streaming step across the evaluation stream**. It was an **aggregate online average**, encompassing both the active baseline and the ongoing candidate exploration overhead (e.g., the $Q=5$ probe bank in M1 or the $T_{\text{prob}}=50$ probation unit in M2).
2. **The V0.2 Disaggregation:** In `LEBRE-V0.2-INTEGRATION-DESIGN-01`, the architecture disaggregated compute into **Live Path** ($81.4$ FLOPs) and **Shadow Exploration Rent** ($26.8$ FLOPs), totaling **$108.2$ FP FLOPs/step**.
3. **The Semantic Conflict:** 
   - Under `LIVE_ONLY`, $T_3$ consumes **$81.4$ FLOPs/step**, which is strictly $\le 100$ (**PASS**).
   - Under `TOTAL_ONLINE` (the strict historical interpretation), $T_3$ consumes **$108.2$ FLOPs/step**, which is $> 100$ (**FAIL**).
   - In Gate 11 of `LEBRE_V0_2_INTEGRATION_PROTOCOL.md`, the author specifically formulated the text as: *"Mean live compute on single-memory regimes must not exceed 100 FP FLOPs/step"*, thereby restricting the constraint to the live path without explicitly acknowledging that Total Online compute exceeds the historical 100-FLOP budget.

---

## 2. Stage-by-Stage Semantic Evolution

| Project Stage | Governing Document | Metric Formulation | Probing / Shadow Included? | Mean or Hard Peak? | Reported Result | Legacy R2 Status |
|:---|:---|:---|:---:|:---:|:---:|:---:|
| **M1: Sparse Observable Memory** | `M1_SPEC.md`, `bench_01_locked_config.json` | Total floating-point ops per streaming step | **YES** ($Q=5$ feature probes included) | Stream Mean | 68.2 FLOPs | **PASS** ($\le 100$) |
| **M2: Minimal Latent Recurrence** | `M2_SINGLE_STATE_SPEC.md`, `M2-EXP-0005` | Total algorithmic FLOPs per step | **YES** (Provisional state RTRL included) | Stream Mean | 82.4 FLOPs | **PASS** ($\le 100$) |
| **BENCH-01B Benchmark Audit** | `BENCH_01B_FINAL_REPORT.md` | Mean FLOPs / step across 450 runs | **YES** (All background routines included) | Stream Mean (Peak = 206) | 90.44 FLOPs | **PASS** ($\le 100$) |
| **Resource Reconciliation** | `RESOURCE_ACCOUNTING_RECONCILIATION-01` | Disaggregated 4-channel vector | **YES** (Disaggregated into baseline vs exploration) | Stream Mean | 82 vs 125 reconciled | **PASS** ($\le 100$) |
| **V0.2 Pre-registered Protocol** | `LEBRE_V0_2_INTEGRATION_PROTOCOL.md:71` | *"Mean live compute on single-memory regimes"* | **NO** (Restricted to Live Path only!) | Stream Mean | Preregistered $\le 100$ | **SEMANTIC SHIFT** |
| **V0.2 Confirmatory Result** | `LEBRE_V0_2_FINAL_REPORT.md` | Live: 81.4, Shadow: 26.8, Total: 108.2 | Disaggregated | Live: 81.4, Total: 108.2 | Live: PASS, Total: **FAIL** |

---

## 3. Disaggregated Compute Profiling of $T_3$

### 3.1 Steady-State Live Regimes
- **Memoryless Regime ($I_1, I_2$):** Linear base only ($58.0$ FLOPs/step).
- **Pure Discrete Delay Regime ($I_3, I_4, I_5$):** Linear base + active taps ($86.8$ – $88.9$ FLOPs/step).
- **Pure Continuous State Regime ($I_6, I_7$):** Linear base + recurrent unit ($81.0$ – $91.8$ FLOPs/step).
- **Hybrid Regime ($I_9$):** Linear base + 4 taps + recurrent unit = **$127.2$ FLOPs/step**!
  *(Note: In the hybrid regime $I_9$, even the Live Path alone exceeds 100 FLOPs!)*

### 3.2 Shadow Exploration Rent
- Correlation Grid Probing ($M=2$ pairs/step): $4.0$ FLOPs.
- Provisional Candidate Scoring ($C \le 3$ candidates): $4.0$ to $12.0$ FLOPs.
- Shadow Recurrent Unit Training ($N=1$ unit with RTRL): $18.0$ FLOPs.
- Capacity Arbitrator Loss Grid ($P_B, P_{BD}, P_{BR}, P_{BDR}$): $16.0$ FLOPs.
- **Mean Shadow Rent:** **$26.8$ FLOPs/step**.

---

## 4. Counterfactual Duty-Cycling Analysis

In an embedded edge deployment, shadow exploration does not necessarily need to execute at every single time step ($100\%$ duty cycle). If environmental transitions occur on a timescale of thousands of steps, shadow probing can be duty-cycled:

| Shadow Probing Duty Cycle | Live FLOPs (Mean) | Shadow Rent (FLOPs) | Total Online FLOPs | Legacy R2-FP Compliance ($\le 100$) |
|:---:|:---:|:---:|:---:|:---:|
| **100% (Continuous Search - Current $T_3$)** | 81.4 | 26.8 | **108.2** | **FAIL** ($> 100$) |
| **70% Duty Cycle** | 81.4 | 18.8 | **100.2** | **MARGINAL** |
| **50% Duty Cycle (Alternate Steps)** | 81.4 | 13.4 | **94.8** | **PASS** ($\le 100$) |
| **25% Duty Cycle (1 step in 4)** | 81.4 | 6.7 | **88.1** | **PASS** ($\le 100$) |
| **10% Duty Cycle (1 step in 10)** | 81.4 | 2.7 | **84.1** | **PASS** ($\le 100$) |

### Methodological Rule:
While duty cycling is technically feasible and brings total compute below 100 FLOPs, **no duty-cycling schedule was part of the preregistered $T_3$ algorithm in `LEBRE-V0.2-INTEGRATION-DESIGN-01`**. Therefore, duty cycling cannot be retroactively claimed as a basis for confirmatory compliance. Under the sealed algorithm, total compute is $108.2$ FLOPs.

---

## 5. Audit Verdict on Compute Compliance

- **`LEGACY_R2_FP_LIVE_COMPLIANCE`:** **YES** ($81.4 \le 100$).
- **`LEGACY_R2_FP_TOTAL_ONLINE_COMPLIANCE`:** **NO** ($108.2 > 100$).
- **`HYBRID_REGIME_LIVE_COMPLIANCE` (on $I_9$):** **NO** ($127.2 > 100$).

The report must transparently declare that $T_3$ complies with $\le 100$ FLOPs **strictly as a live-path metric**, and that total continuous online execution consumes $108.2$ FLOPs/step (with hybrid peaks reaching $154.0$ FLOPs).
