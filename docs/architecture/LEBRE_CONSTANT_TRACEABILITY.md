# LEBRE Architecture: Normative Constant Traceability Audit
**Specification Version:** 0.1  
**Audit Stage:** ARCH-SPEC-01R2  
**Status:** Internally Audited Reference Specification / Reconciled with Frozen Code & Benchmark Artifacts  

---

## 1. Audit Taxonomy

Every numeric threshold, horizon, and hyperparameter referenced in the LEBRE Architecture Specification is audited and classified into one of four formal categories:

1. `CODE_VERIFIED_FROZEN`: Hardcoded or configured parameter actively verified in the frozen codebase (`src/models/`, `src/learners/`, or `bench_01_locked_config.json`).
2. `CURRENT_IMPLEMENTATION_POLICY`: Deliberately selected policy parameter frozen for v0.1 single-state instantiation, subject to future revision under formal governance.
3. `EXPERIMENT_SPECIFIC`: Measurement, empirical cost ratio, or diagnostic threshold derived from a specific experimental protocol.
4. `ILLUSTRATIVE`: Representative or conceptual number used purely for didactic clarity (not normative).

---

## 2. Comprehensive Constant Traceability Matrix

| Symbol / Constant | Canonical Value | Used In | Source File / Specification | Classification Status | Architectural vs. Implementation | Empirical / Mathematical Notes |
| :--- | :---: | :--- | :--- | :--- | :--- | :--- |
| $\text{MAX\_ACTIVE\_STATES}$ | $1$ | Recurrent Core | `M2_SINGLE_STATE_SPEC.md`, `state_lifecycle.py:42` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Core boundary for v0.1 ($N \le 1$); multi-state ($N > 1$) deferred to M3. |
| $\text{MAX\_PROVISIONAL\_STATES}$ | $1$ | Shadow Probation | `state_lifecycle.py:49` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Limits shadow exploration overhead to a single candidate. |
| $\text{STATE\_DIM}$ | $1$ | Recurrent State | `minimal_state.py:12`, `M2-EXP-0005` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Scalar internal state representation. |
| $T_{\text{prob}}$ | $50$ steps | Probation Window | `candidate_probation.py`, `LEBRE_ARCHITECTURE_SPEC` | `SPEC_VERIFIED` | Canonical Specification Standard | Evaluated probation horizon (historical dev tested 20–80 steps). |
| $\tau_{\text{mature}}$ | $100$ steps | Maturation Window | `state_lifecycle.py:22`, `LEBRE_ARCHITECTURE_SPEC` | `SPEC_VERIFIED` | Canonical Specification Standard | Active grace period granting immunity from early eviction (120 in code default). |
| $\theta_{\text{birth}}$ | $0.15$ | Birth Trigger | `state_lifecycle.py:23`, `M2-EXP-0005` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Residual error threshold triggering provisional state synthesis. |
| $N_{\text{birth}}$ | $30$ steps | Birth Persistence | `state_lifecycle.py:56`, `M2_SINGLE_STATE_SPEC` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Consecutive steps error must exceed $\theta_{\text{birth}}$ before birth. |
| $\theta_{\text{promote}}$ | $0.05$ ($5\%$) | Promotion Trigger | `candidate_probation.py`, `state_lifecycle.py:24` | `CODE_VERIFIED_FROZEN` | Canonical Specification Standard | Minimum relative counterfactual MSE gain required (>5%) (historical dev explored 15%). |
| $\theta_{\text{ret}}$ | $0.02$ | Eviction Retention | `state_lifecycle.py:25` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Lower threshold for two-timescale structural relevance. |
| $\theta_{\text{obs}}$ | $0.80$ | Eviction Obsolescence | `M2_SINGLE_STATE_SPEC.md:114` | `SPEC_VERIFIED` | Current Implementation Policy | Accumulated positive evidence of environmental absence. |
| $N_{\text{pat}}$ | $30$ steps | Eviction Patience | `state_lifecycle.py:26`, `M2-R1` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Consecutive steps satisfying dual eviction criteria before deallocation (30–40 in dev). |
| $\alpha_{\text{slow}}$ | $0.005$ | Relevance Accumulator | `M2_SINGLE_STATE_SPEC.md:104` | `SPEC_VERIFIED` | Current Implementation Policy | Time constant $\tau_{\text{ret}} \approx 140$ steps, bridging Poisson silence. |
| $\beta_{\text{obs}}$ | $0.02$ | Obsolescence Accumulator | `M2_SINGLE_STATE_SPEC.md:110` | `SPEC_VERIFIED` | Current Implementation Policy | Smoothing rate for persistent silence detection. |
| $\epsilon_x, \epsilon_y$ | $0.10, 0.05$ | Silence Gating | `M2_SINGLE_STATE_SPEC.md:110` | `SPEC_VERIFIED` | Implementation Detail | Gating thresholds for input and recurrent output silence. |
| $K_{\max}$ | $10$ | Active Support | `M1_SPEC.md`, `bench_01_locked_config.json` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Upper ceiling of active sparse observable features. |
| $Q$ | $5$ | Probe Bank Size | `AdaptiveEvidenceLearner.py:26` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Number of unallocated dimensions probed per streaming step. |
| $n_{\text{min}}$ | $5$ | Feature Promotion | `AdaptiveEvidenceLearner.py:29` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | Minimum probe samples before evaluating feature readiness. |
| $\text{Wald } \alpha$ | $0.10$ | Feature Readiness | `AdaptiveEvidenceLearner.py:123` | `CODE_VERIFIED_FROZEN` | Current Implementation Policy | One-sided 90% confidence lower bound ($z = 1.645$) for early accept. |
| $300:1$ | $300\times$ | Asymmetry Semantics | `M2-EXP-0005`, `CAR_01_FINAL_REPORT.md` | `EXPERIMENT_SPECIFIC` | Empirical Ratio (Not Literal Code Weight) | Measured empirical ratio of false-eviction cost vs. stale-retention cost. |
| $250 - 350$ steps | $250 - 350$ steps | Eviction Latency | `M2_SINGLE_STATE_SPEC.md:143` | `EXPERIMENT_SPECIFIC` | Empirical Horizon | Measured steps required to clear hysteresis after true regime shift. |
| $\ge 500$ steps | $\ge 500$ steps | Stationary Horizon | `M2_SINGLE_STATE_SPEC.md:141` | `EXPERIMENT_SPECIFIC` | Scope Limit Boundary | Certified operational regime duration for stationary phase tracking. |
| $p_{\text{event}} \ge 0.003$ | $0.003$ | Poisson Event Density | `M2_SINGLE_STATE_SPEC.md:148` | `EXPERIMENT_SPECIFIC` | Scope Limit Boundary | Minimum event frequency observed to sustain retention without premature eviction. |
| Mean Compute | $90.44$ FLOPs/step | Benchmark Result | `BENCH_01B_FINAL_REPORT.md` | `CODE_VERIFIED_FROZEN` | Empirical Benchmark Result | Mean algorithmic compute across 450 runs (peak observed: 206 FLOPs). |
| Peak Compute | $\approx 206$ FLOPs/step | Transient Peak | `BENCH_01B_RESOURCE_ANALYSIS.md` | `CODE_VERIFIED_FROZEN` | Empirical Benchmark Result | Maximum observed per-step FLOPs during simultaneous probing and shadow update. |
| Persistent RAM | $440.0$ Bytes | Benchmark Result | `BENCH_01B_FINAL_REPORT.md` | `CODE_VERIFIED_FROZEN` | Empirical Benchmark Result | Mean persistent model-state memory footprint (base weights + state structures). |
| R2-FLOP Ceiling | $100.0$ FLOPs/step | Protocol Metric | `bench_01_locked_config.json` | `CODE_VERIFIED_FROZEN` | Protocol Benchmark Ceiling | Standard requiring mean compute $\le 100$ FLOPs/step across stream. |
| R2-MEM Ceiling | $1024.0$ Bytes | Protocol Metric | `bench_01_locked_config.json` | `CODE_VERIFIED_FROZEN` | Protocol Benchmark Ceiling | Standard requiring persistent model RAM $\le 1024$ bytes. |
| $[■■□□□□]$ | $38 - 95$ FLOPs | Elasticity Visual | `LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md` | `ILLUSTRATIVE` | Didactic Visual Only | Conceptual representation of compute scaling; not telemetry hardware. |

---

## 3. Normative Audit Verdicts

1. **R2-FLOP Threshold:** Formally verified as a **mean benchmark threshold** ($\le 100$ FLOPs/step), not a hard per-step worst-case bound. Peak compute during shadow candidate evaluation reaches approximately 206 FLOPs/step for brief intervals.
2. **300:1 Ratio:** Formally audited as an **empirical cost ratio** (measuring the operational penalty of destroying needed state vs carrying an inactive scalar state), rather than an explicit mathematical constant inside the codebase. The codebase realizes this conservatism through hysteresis patience ($\text{patience} = 30$) and dual-gated thresholding.
3. **Hardware & Energy:** No numeric constant certifies battery life, milliwatts, or specific MCU clock cycles. All numbers represent algorithmic operation counts and array byte allocations.
