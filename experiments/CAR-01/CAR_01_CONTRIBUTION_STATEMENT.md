# CAR_01_CONTRIBUTION_STATEMENT.md — Formal Scientific Contribution Statement

**Protocol:** CAR-01  
**Milestone:** Contribution Assessment Review  
**Date:** September 19, 2026  
**Status:** Pre-Publication Contribution Formulation  

---

## 1. Candidate Contribution Taxonomy Evaluation (K1–K10)

Each candidate contribution is evaluated independently against established literature and sealed empirical evidence:

| Candidate ID | Description | Literature Verdict | Empirical Support | Status | Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **K1** | New learning rule | Williams & Zipser (1989), Jaeger (2002) | Exact scalar RTRL validated in M2-EXP-0001 | **REJECTED_AS_KNOWN** | Mathematical formulation is classical exact scalar RTRL; zero novelty in update equations. |
| **K2** | New recurrent credit mechanism | Classical forward sensitivity accumulation | Verified in M2-EXP-0001 | **REJECTED_AS_KNOWN** | Sensitivity propagation is identical to standard 1D RTRL without truncation. |
| **K3** | New structural growth/pruning method | Platt (1991), RSONN (2017), Dohare (2024) | Validated across M1/M2 | **REJECTED_AS_KNOWN** | Growth via residual error and pruning via utility thresholds are widely known in neural literature. |
| **K4** | New adaptive capacity mechanism | Variable-tap LMS (2008), ACESN (2026), RAN | Validated across M1/M2 | **REJECTED_AS_KNOWN** | Adjusting model size dynamically in response to error is well-precedented in adaptive filtering and ESNs. |
| **K5** | New utility/maturity mechanism | Sutton (1988), Dohare et al. (Nature 2024) | M2-EXP-0002 | **REJECTED_AS_KNOWN** | Dual-metric utility tracking and maturity probation windows are established in Continual Backpropagation. |
| **K6** | Resource-governed structural lifecycle | Distinct lifecycle coordinating cost-bearing adaptive objects | Validated across M1/M2 and BENCH-01B | **STRONG_CANDIDATE** | Integrates physical cost accounting, shadow probation, and rent deductions into a cohesive state machine. |
| **K7** | Unified lifecycle across observable and latent structure | Cross-structural state machine (features, lags, recurrence) | M2-R1 validation | **MODERATE_CANDIDATE** | Applies an identical lifecycle across heterogeneous temporal mechanisms, but single-state scope limits claim. |
| **K8** | Two-timescale quiescent retention | Decoupling signal activity from structural necessity | M2-EXP-0003, Tasks A5/A7 | **MODERATE_CANDIDATE** | Prevents catastrophic forgetting during quiet intervals via structural Gramian tracking. |
| **K9** | Positive-obsolescence eviction under asymmetric cost | 300:1 false-eviction loss weighting | M2-EXP-0005r, BENCH-01B 0% divergence | **MODERATE_CANDIDATE** | Prevents destructive structural churn under low SNR via explicit asymmetric hysteresis. |
| **K10** | Empirically derived architecture for bounded online adaptation | Sub-100-FLOP streaming adaptation architecture | BENCH-01B Pareto frontier | **STRONG_CANDIDATE** | Validated operating point strictly dominating Minimal GRU and MUSE-RNN under 100 FLOPs. |

---

## 2. Final Selection of Contributions

In accordance with strict pre-publication discipline, the contribution is compressed to **one primary contribution** and **two supporting contributions**:

### Primary Scientific Contribution
**PRIMARY_CONTRIBUTION = RESOURCE_GOVERNED_STRUCTURAL_LIFECYCLE**
> *"A resource-governed online structural-learning architecture that treats observable features, temporal delays, and recurrent internal state as cost-bearing adaptive structures governed by a unified evidence-driven lifecycle under strict micro-resource budgets."*

### Supporting Scientific Contribution 1
**SUPPORTING_CONTRIBUTION_1 = TWO_TIMESCALE_QUIESCENT_RETENTION**
> *"A two-timescale structural retention mechanism that decouples instantaneous signal activity ($O_{\text{obs}}$) from structural necessity ($O_{\text{struct}}$) via an online observability Gramian proxy, preventing premature state annihilation during prolonged quiescent intervals."*

### Supporting Scientific Contribution 2
**SUPPORTING_CONTRIBUTION_2 = ASYMMETRIC_OBSOLESCENCE_GOVERNANCE**
> *"An evidence-driven structural eviction policy that requires positive statistical evidence of persistent disutility under a severe asymmetric loss weighting (300:1), eliminating destructive parameter churn and ensuring zero divergence across continuous online streams."*

---

## 3. Explicit Non-Contributions (Forbidden Claims)

The following mechanisms and properties are strictly classified as non-contributions and **MUST NOT** be claimed as novel or distinct in any manuscript or specification:

1. **Exact RTRL Formulas:** Classical scalar forward sensitivity equations must be cited directly to Williams & Zipser (1989).
2. **Sparse Filtering Primitives:** Normalized Least Mean Squares and soft-threshold regularization must be cited to standard signal processing literature (Nagumo & Noda, 1967; Chen et al., 2009).
3. **Running Utility and Maturation Counters:** Exponential utility smoothing and newborn immunity windows must be cited to Continual Backpropagation (Dohare et al., Nature 2024).
4. **Controllability and Observability Concepts:** Balanced truncation principles must be cited to Moore (1981) and linear systems control theory.
5. **Universal Sequence Modeling:** The architecture cannot be claimed as a replacement for multi-state RNNs, LSTMs, Transformers, or foundation models.
6. **Multi-State Scaling:** Scalability to multi-state recurrent architectures ($N > 1$) remains unvalidated and must not be asserted.
7. **Unconstrained Predictive Superiority:** The architecture must not be claimed as "state-of-the-art" or universally more accurate than unconstrained deep networks (RSONN, CCN).

---

## 4. Formal Publication-Safe Contribution Statement

The following single-sentence contribution statement is approved for abstract and introduction use (41 words, strictly evidence-bounded):

> **"We present a resource-governed online learning architecture that unifies feature selection, delay lines, and minimal recurrence as cost-bearing adaptive structures, demonstrating that an evidence-driven lifecycle with two-timescale retention and asymmetric eviction achieves robust, zero-divergence adaptation under strict sub-100-FLOP micro-resource budgets."**

---

## 5. Contribution Strength Audit

| Question | Evaluation | Evidence Reference |
| :--- | :---: | :--- |
| 1. Is every primitive already known? | **YES** | All mathematical equations confirmed in Layer 1 prior art. |
| 2. Is the organizational composition nontrivial? | **YES** | Naive combinations fail (gradient shock, churn, premature eviction). |
| 3. Is the organization empirically necessary? | **YES** | Each lifecycle mechanism resolved a specific falsified failure mode (M1/M2). |
| 4. Does it produce measurable external value? | **YES** | Strict Pareto dominance over Minimal GRU and MUSE-RNN in BENCH-01B. |
| 5. Is that value observable against close neighbors? | **YES** | 0% divergence vs 21% (LRU), 13% (Continual Backprop), 6.7% (CCN). |
| 6. Are its operational boundaries explicit? | **YES** | Falsified on high-order tapped delays (A2–A4) and dense chaos (B4). |

**Final Contribution Confidence: HIGH (with explicit scope limits).**
