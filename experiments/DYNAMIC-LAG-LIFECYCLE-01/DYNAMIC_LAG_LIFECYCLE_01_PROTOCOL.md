# DYNAMIC-LAG-LIFECYCLE-01: Preregistered Experimental Protocol
## Causal Sparse Delay Discovery, Lifecycle Governance & Bounded-History Temporal Memory

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01`  
**Auditor:** Skeptical Senior ML Researcher, Adaptive Filtering Specialist, Reproducibility Auditor  
**Date:** September 2026  
**Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Status:** PREREGISTERED & SEALED  
**Protocol Hash:** `544ba1928c0806699908377e6f381855adfad1adb09ae909b5f6ca5153de62a6`

---

## 1. Scientific Objective & Epistemic Boundaries

This protocol governs the empirical investigation of whether an online, resource-bounded streaming learner can dynamically discover, promote, retain, evict, and rediscover sparse temporal coordinates $(i, k)$ without oracle knowledge of their locations, while adhering strictly to LEBRE's micro-edge resource envelope ($\le 100$ FLOPs/step, $\le 1024$ bytes persistent state).

### Strict Immutability & Scope Limits:
1. `src/` and `tests/` remain 100% bitwise immutable throughout this experiment.
2. Milestone M3 (multi-state recurrence $N \ge 2$) remains **UNOPENED**.
3. No novelty claims will be made (`NOVELTY_CLAIM_READY = NO`).
4. Canonical LEBRE v0.1 core remains frozen (`LEBRE_V0_1_STATUS = FROZEN_WITH_SCOPE_LIMITS`).

---

## 2. Benchmark Suite: Hidden-Support Tasks (D1–D12)

To prevent benchmark memorization or oracle leakage, hidden supports are generated dynamically using seeded pseudorandom distributions over allowed delays $\{1 \dots L_{\max}\}$ with $L_{\max} = 32$. Stream length $T = 10,000$ steps; evaluation split $t \ge 3,000$ (70% test horizon).

| Task ID | Task Name | Description & Generative Mechanism | Primary Hypothesis Tested |
| :--- | :--- | :--- | :--- |
| **D1** | Single Static Delay | $y_t = 0.8 x_{i_1, t-k_1} + \epsilon_t$, where $k_1 \in \{2 \dots 16\}$ | H1 (Basic Discovery) |
| **D2** | Multi-Tap Sparse Delay | $y_t = 0.5 x_{i_1, t-k_1} + 0.5 x_{i_2, t-k_2} + \epsilon_t$, non-contiguous $k_1 \ne k_2$ | H1, H2 (Non-Contiguous) |
| **D3** | Widely Separated Support | $y_t = 0.6 x_{1, t-2} + 0.6 x_{1, t-28} + \epsilon_t$ | H2 (Sparse vs Contiguous FIR) |
| **D4** | Abrupt Support Relocation| 3 Regimes: $S_1 (t < 3.3k) \to S_2 (3.3k \le t < 6.6k) \to S_3 (t \ge 6.6k)$ | H4 (Support Tracking) |
| **D5** | Tap Birth | Irrelevant delay suddenly becomes active at $t = 5,000$ | H4 (Dynamic Birth) |
| **D6** | Tap Death | Active predictive delay permanently becomes noise at $t = 5,000$ | H4 (Dynamic Eviction) |
| **D7** | Quiescent Tap | Active delay becomes zero for $3,000 \le t < 7,000$, then reactivates | H5 (Quiescence Survival) |
| **D8** | Amplitude Drift | Support fixed, but coefficients follow slow random walk ($w_j(t)$ drifts) | Parameter Drift |
| **D9** | Memoryless Negative Control| Pure instantaneous linear stream $y_t = \mathbf{w}^\top \mathbf{x}_t + \epsilon_t$ (Zero true delays) | H3 (False-Discovery Rate) |
| **D10**| Dense FIR Control | Dense autoregressive decaying FIR filter ($\sum_{k=1}^8 0.5^k x_{t-k}$) | Sparse vs Dense Limit |
| **D11**| Continuous-State Control | Bistable latch / Poisson quiescent memory (A5/A7 equivalent) | H7 (Recurrent Protection) |
| **D12**| Hybrid Memory | Combined sparse delay ($x_{1, t-6}$) AND continuous latent state ($s_t$) | H7 (Discrete/Recurrent Coexistence) |

---

## 3. Disjoint Seed Protocol

To ensure structural generalization:
- **Phase 1: Development Verification (DEV):**
  - Seeds: `701, 702, 703, 704, 705, 706, 707, 708, 709, 710` ($N=10$).
  - Purpose: Verify candidate probing stability, verify scheduler memory, confirm bug-free execution.
- **Phase 2: Confirmatory Evaluation (EVAL):**
  - Seeds: `801` through `830` ($N=30$).
  - Purpose: Formal paired hypothesis testing, bootstrap confidence intervals, decision gate auditing.
  - All variants evaluated on identical sample-for-sample streams.

---

## 4. Preregistered Architectural Parameters

All parameters are frozen prior to Phase 2 evaluation:
- Maximum search horizon: $L_{\max} = 32$
- Maximum active tap capacity: $K_{\max} = 4$
- Candidate probe rate: $M = 2$ candidate pairs per step (rotating schedule)
- Provisional probation window: $W_{\min} = 50$ steps
- Promotion threshold: $\theta_{\text{promote\_lag}} = 0.10$
- Replacement regret margin: $\theta_{\text{replace\_margin}} = 0.05$
- Slow relevance smoothing factor: $\gamma_{\text{rel}} = 0.001$
- Active tap learning rate: $\mu_{\text{lag}} = 0.08$
- Eviction threshold: $\theta_{\text{evict}} = 0.01$
- Grace period before eviction: $W_{\text{grace}} = 200$ steps

---

## 5. Candidate Generation & Search Scheduling Rule

To comply with the mandatory **"No Full Scan for Free"** rule:
- Evaluating or correlating all $D \cdot L_{\max}$ candidates every step is strictly prohibited.
- At each step $t$, the rotating scheduler tests exactly $M = 2$ candidate pairs $(i, k)$, cycling sequentially through $\{1 \dots D\} \times \{1 \dots L_{\max}\}$.
- Probing FLOPs are fixed at 12 FLOPs/step and fully charged in the compute ledger.

---

## 6. Primary Decision Gates (Audited in Final Report)

1. **GATE 1 (Support Discovery):** Support recall $\ge 70.0\%$ on static sparse delay benchmarks (D1–D3).
2. **GATE 2 (Oracle Gap):** $\Delta \text{NMSE}_{\text{oracle}} \le 0.100$ compared to oracle sparse lags (O0).
3. **GATE 3 (False Discovery Control):** Active taps on memoryless control (D9) $K_{\text{active}} < 0.5$.
4. **GATE 4 (Support Relocation Tracking):** Relocation latency $T_{\text{reloc}} < 1,500$ steps on D4.
5. **GATE 5 (Quiescence Survival):** Quiescent tap survival rate $\ge 80.0\%$ on D7.
6. **GATE 6 (Continuous State Preservation):** No degradation on continuous control D11 compared to frozen LEBRE.
7. **GATE 7 (History Accounting):** Full accounting of history and candidate memory; report $\rho_{\text{MEM}}$.
8. **GATE 8 (Micro-Edge Envelope):** Mean FLOPs $\le 100$ (R2-FLOP) and persistent state $\le 1024$ bytes (R2-MEM).

---

## 7. Statistical Protocol
- Paired differences $\Delta_i = m_{A, i} - m_{B, i}$ computed across all $N=30$ EVAL seeds.
- 10,000 bootstrap resamples for 95% confidence intervals on means and paired deltas.
- Cohen's $d_z = \bar{\Delta} / s_{\Delta}$ reported for effect sizes.
- Seed win rates ($P(m_A < m_B)$) reported for all primary comparisons.
