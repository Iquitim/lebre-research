# CAR_01_FAILURE_TO_MECHANISM_TRACE.md — Empirical Failure-to-Mechanism Lineage

**Stage:** CAR-01 (Contribution Assessment Review)  
**Task:** Chronological Lineage Audit of Failure Modes and Derived Mechanisms  
**Governing Standard:** Sections 75–77 of CAR-01 Specification  
**Date:** September 19, 2026  
**Status:** COMPLETED & SEALED  

---

## 1. Scientific Purpose

A major challenge in architectural review is distinguishing a coherent, principled system from an arbitrary "bag of tricks" assembled post-hoc. 

This document traces the rigorous experimental lineage of Track B across Milestones M1 and M2. It documents every major empirical failure, the corresponding controlled ablation experiment, the mechanism derived to overcome the failure, and the mechanisms that were tested and rejected.

---

## 2. Milestone M1: Sparse Feature Lifecycle & Bounded Probing

Milestone M1 established the sparse linear core operating under strict compute bounds ($K_{\max} = 10$ active features out of $D$ ambient dimensions, with probing budget $Q = 2$).

| Experiment ID | Observed Failure Mode | Causal Finding / Root Cause | Mechanism Introduced | Status / Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **M1-EXP-0001** | **Zero-Slack Churn:** Instantaneous feature eviction caused high parameter variance and cycling. | Evicting features immediately when utility dropped caused thrashing on noisy inputs. | Minimum probation window before eviction eligibility. | **FROZEN IN M1** |
| **M1-EXP-0002** | **Maturity Traps Noise:** Newborn features initialized with random weights were prematurely evicted. | New features require gradient steps to reach functional utility; evaluating them immediately killed useful candidates. | Protected newborn probation window ($T_{\text{prob}} = 80$ steps). | **FROZEN IN M1** |
| **M1-EXP-0003** | **Stale Protection Barrier:** Protected noise features degraded predictions during probation. | While protected, bad features drove prediction error up. | Shadow probing: candidates learn in background without affecting main output until promoted. | **FROZEN IN M1** |
| **M1-EXP-0004** | **Probe Opportunity Bottleneck:** Random candidate probing ($Q=2$) took too long to discover informative features in high $D$. | Uniform random sampling over $D=50$ features required hundreds of steps to hit true support. | Error-correlated candidate priority queue. | **FROZEN IN M1** |
| **M1-EXP-0005** | **Evidence Latency & False Entry:** High-variance single-step losses triggered spurious feature births. | Single-step error spikes do not indicate persistent structural need. | Exponentially weighted moving average error accumulator ($EMA(e^2)$) with birth threshold. | **FROZEN IN M1** |
| **M1-EXP-0006** | **Tier-Entry Insufficiency:** Features entered active set but failed to contribute meaningful gain. | Raw magnitude $|w_j|$ does not equal marginal predictive contribution. | Counterfactual paired delta-loss ($U_j = \Delta \mathcal{L}_j$). | **FROZEN IN M1** |
| **M1-EXP-0007** | **Identifiability Frontier on Collinear Inputs:** Collinear features split weights, diluting utility. | Correlated features caused both to appear low-utility, triggering premature eviction of both. | Two-timescale structural excitation counter. | **FROZEN IN M1** |
| **M1-EXP-0008** | **Eligibility Trace Non-Benefit:** Eligibility traces added FLOPs without improving sparse linear tracking. | Traces added 4 FLOPs/dim without measurable MSE reduction on linear streams. | **REJECTED:** Traces excised from base linear filter. | **EXCISED** |
| **M1-R1** | **M1 Freeze Review:** Certified sparse linear filter under strict bounds. | Proved $O(K_{\max} + Q)$ scaling with ambient dimension $D$. | Frozen in `M1_SPEC.md`. | **FROZEN** |

---

## 3. Milestone M2: Scalar Recurrent Lifecycle & Quiescent Memory

Milestone M2 extended the architecture from purely feedforward sparse linear modeling to temporal sequence learning, subject to the single-state constraint ($N=1$).

| Experiment ID | Observed Failure Mode | Causal Finding / Root Cause | Mechanism Introduced | Status / Outcome |
| :--- | :--- | :--- | :--- | :--- |
| **M2-EXP-0001** | **Unmanaged RTRL Instability:** Continuously updated recurrent state without bounds caused gradient explosion. | Real-Time Recurrent Learning sensitivities accumulate unbounded feedback without damping. | Exact bounded forward sensitivity for scalar state; normalized readout updates. | **FROZEN IN M2** |
| **M2-EXP-0002** | **Recurrent State Parasitism:** Scalar state consumed compute on stationary linear streams where state was unnecessary. | A permanent state incurs 18 FLOPs/step even when $y_t$ is purely feedforward linear. | "State Must Pay Rent": State is created provisionally and evicted unless it achieves $\ge 5\%$ marginal error reduction. | **FROZEN IN M2** |
| **M2-EXP-0003** | **Quiescent-Memory Annihilation:** State was evicted during silent gaps between Poisson events (Tasks A5/A7). | Standard loss utility ($e_{\text{base}}^2 - e_t^2$) drops to zero when input signals are zero; decay evicted dormant latches. | Two-timescale structural observability: separating instantaneous excitation from structural relevance ($O_{\text{struct}}$). | **FROZEN IN M2** |
| **M2-EXP-0004** | **State-Free Stale-Retention Trade-off:** Naive retention counters retained obsolete states indefinitely after regime shifts. | A pure observability metric without obsolescence detection preserves useless states forever. | Positive evidence of obsolescence ($O_{\text{obs}}$) under 300:1 asymmetric false-eviction weighting. | **FROZEN IN M2** |
| **M2-EXP-0005** | **Gated Over-Parameterization:** Gated scalar state added unnecessary FLOPs on simple autoregressive lags. | A linear scalar state ($s_t = \alpha s_{t-1} + u_t$) is sufficient for AR(1) dynamics; gating added 6 FLOPs with zero MSE gain. | Parsimonious Linear-First Escalation: Linear state tested first; gated state explored only if linear fails probation. | **FROZEN IN M2** |
| **M2-EXP-0006** | **Sensitivity Trace Saturation:** Sensitivity traces $\frac{\partial s}{\partial \theta}$ drifted under unnormalized inputs. | Input normalization drift destabilized sensitivity accumulation. | Causal standardization coupled with NLMS normalized gradient stepping. | **FROZEN IN M2** |
| **M2-R1** | **M2 Freeze Review:** Certified single-state lifecycle Pareto freeze. | Proved dynamic compute elasticity and quiescent retention. | Frozen in `M2_SINGLE_STATE_SPEC.md`. | **FROZEN** |

---

## 4. Synthesis: Empirical Mechanism Derivation

The historical trace refutes the hypothesis that Track B is an arbitrary concatenation of literature techniques:
1. **Every mechanism corresponds to an explicit empirical failure:**
   - *Probation window* was introduced because instantaneous eviction caused churn.
   - *Shadow probing* was introduced because unprotected testing degraded live predictions.
   - *Rent-based eviction* was introduced because permanent states wasted compute on linear streams.
   - *Two-timescale observability ($O_{\text{struct}}$)* was introduced because utility decay annihilated bistable latches during Poisson quiescence.
   - *Positive obsolescence ($O_{\text{obs}}$)* was introduced because unmanaged retention preserved dead states across regime shifts.
   - *Linear-first escalation* was introduced because gating was wasteful on simple exponential lags.
2. **Successive Rejections:** Mechanisms that failed to justify their resource cost (e.g., eligibility traces in M1, premature vector state expansion, symmetric eviction weighting) were explicitly audited, rejected, and excised.
