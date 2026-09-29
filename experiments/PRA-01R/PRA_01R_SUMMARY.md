# PRA-01R: Prior-Art Reconciliation & Benchmark Lock — Final Summary

**Document ID:** PRA-01R-SUMMARY  
**Author:** Skeptical Literature Reconciler, Pre-Publication Reviewer, and Benchmark Governance Auditor  
**Date:** September 19, 2026  
**Status:** RECONCILIATION COMPLETE — BENCHMARK FROZEN — HARD STOP ENFORCED  
**Governing Standard:** Sections 91–98, 107, 108 of PRA-01R Protocol  

---

## 1. Formal Reconciliation Decisions

Per the strict requirements of Sections 91–96 of the governing protocol, the definitive reconciliation verdicts are recorded:

```
===============================================================================
PRIMARY_PRIOR_ART_DECISION = COMBINATION_POSSIBLY_DISTINCT_SURVIVES
ARCHITECTURE_PRIOR_ART     = PARTIAL_MATCHES
NOVELTY_CLAIM_READY        = NO  (FROZEN)
EXTERNAL_BENCHMARK_READY   = YES
INTEGRATION_STATUS         = NONTRIVIAL_EMPIRICALLY_DERIVED_ORGANIZATION
NEXT_MILESTONE             = BENCH-01 (AWAITING REVIEW / EXECUTION UNOPENED)
===============================================================================
```

### Certified Maximum Conclusion (Section 107):
> *"After reconciliation, no close integrated precedent was found for the specific resource-governed organization of the frozen Track-B core, although its individual mechanisms and several partial combinations have substantial prior art. External benchmarking is required to establish whether the integration has empirical value."*

---

## 2. Answers to the 20 Required Final Questions (Section 97)

### Question 1: Does RSONN materially weaken the architectural claim?
**Answer:** **PARTIALLY.**  
*Justification:* RSONN demonstrates that online addition and sensitivity-based pruning of recurrent hidden nodes in streaming data has been established since 2013/2019. It weakens any broad, ungrounded claim of "online recurrent growth and pruning." However, RSONN operates on dense continuous control inputs, lacks probationary shadow testing (causing newborn shock), destroys quiescent state memory during silent gaps (because sensitivity drops to zero), and has no concept of budgeted sparse input or lag exploration.

### Question 2: Does CCN materially weaken state-construction distinctiveness?
**Answer:** **YES.**  
*Justification:* CCN (Javed et al. JMLR 2023) establishes that scalar recurrent units can be trained with exact $O(1)$ Real-Time Recurrent Learning (RTRL) forward sensitivity traces. CCN completely eliminates any claim of mathematical or algorithmic novelty for Track B’s scalar forward sensitivity credit assignment. However, CCN implements only *constructive growth* (adding columns permanently); it completely lacks an autonomous lifecycle (no pruning, no state death, no resource reclamation).

### Question 3: Does Continual Backprop invalidate maturation/utility as distinctive?
**Answer:** **YES.**  
*Justification:* Continual Backpropagation (Dohare et al. 2021, Nature 2024) formalizes unit utility ("structure must pay rent or be replaced") and explicitly implements unit age and maturity thresholds ($m$) to protect newly initialized units. Per Section 15 of the protocol, maturation and utility-based replacement are classified as **`KNOWN`** foundational techniques. They cannot be presented as novel.

### Question 4: Does ACESN invalidate adaptive-capacity language?
**Answer:** **YES.**  
*Justification:* ACESN proves that dynamically expanding and contracting a recurrent network’s effective capacity in response to streaming error demand is an established concept in reservoir computing. Broad marketing phrases such as "capacity is dynamically matched to task demand" are invalid. Track B remains distinct only in *physically allocating and evicting* recurrent parameters with online learned internal dynamics under a rigid sub-linear compute budget.

### Question 5: Do recurrent cascade-correlation systems invalidate state-birth claims?
**Answer:** **YES.**  
*Justification:* Recurrent Cascade-Correlation (Fahlman 1991) established more than three decades ago that recurrent units should be added when feedforward residual error stops improving. The principle of "birth of recurrent structure in response to residual failure" is **`KNOWN`** and has been permanently removed from novelty consideration.

### Question 6: Do evolving recurrent/neuro-fuzzy systems provide a closer historical integrated precedent than MUSE-RNN?
**Answer:** **NO.**  
*Justification:* While evolving recurrent neuro-fuzzy systems (e.g., SOFNN, eTS) have combined online growth, pruning, and feedback rules since 2004, their reliance on fuzzy antecedent hyper-boxes suffers from exponential curse-of-dimensionality in high dimensions. MUSE-RNN remains a closer structural analog because it operates directly on high-dimensional vector embeddings with continuous recurrent activation matrices.

### Question 7: Does variable-order adaptive filtering weaken the lag/state-capacity framing?
**Answer:** **YES.**  
*Justification:* Variable-tap LMS (Zhao et al. 2008) and adaptive-order FIR/IIR filtering demonstrate that dynamically adjusting temporal memory depth based on prediction error gradients is standard classical signal processing. Track B cannot claim novelty for expanding temporal lag capacity; its distinction lies only in the non-contiguous probe bank and the parsimonious escalation boundary from explicit lags to an internal recurrent state.

### Question 8: Does C7 survive?
**Answer:** **`POSSIBLY_DISTINCT` SURVIVES.**  
*Justification:* While multi-model adaptive control combines linear and non-linear models in parallel, the autonomous, single-pass probationary escalation from a cheap scalar linear state to a selective gated state upon empirical failure has no direct precedent in streaming recurrent learners.

### Question 9: Does C8 survive?
**Answer:** **`POSSIBLY_DISTINCT` SURVIVES (at the lifecycle integration level).**  
*Justification:* The underlying metric (controllability $\times$ observability) is **`KNOWN`** from balanced truncation (Moore 1981) and AIRE-Prune (Padhy et al. 2026). However, its formulation as a two-timescale online structural relevance metric that actively prevents premature eviction during quiescent Poisson event gaps is distinct from offline post-training pruning.

### Question 10: Does C9 survive?
**Answer:** **`POSSIBLY_DISTINCT` SURVIVES.**  
*Justification:* Requiring positive statistical evidence of zero-excitation obsolescence ($O_{\text{obs}}$) under an empirical 300:1 asymmetric loss penalty ($C_{\text{FE}} / C_{\text{FR}} > 300:1$) before triggering state death has no direct precedent in the online pruning or continual learning literature, which relies on instantaneous or short-window symmetric thresholds.

### Question 11: Does C10 survive?
**Answer:** **`POSSIBLY_DISTINCT` SURVIVES (as the primary architectural claim).**  
*Justification:* No single published system unifies sparse observable input feature discovery, temporal lag exploration, and recurrent state birth/death under an identical lifecycle (*Probe $\to$ Mature $\to$ Promote $\to$ Retain $\to$ Evict $\to$ Reclaim*) governed by a rigid sub-linear FLOP budget.

### Question 12: What is the single closest paper after reconciliation?
**Answer:** **MUSE-RNN (Das et al. 2019)** remains the closest single architectural neighbor for online recurrent birth/death. **CCN (Javed et al. JMLR 2023)** is the closest neighbor for exact scalar RTRL credit assignment.

### Question 13: What combination of prior papers reconstructs most of Track B?
**Answer:** A six-paper conceptual composite:
1. **MUSE-RNN (Das et al. 2019)** — Recurrent node growth and pruning.
2. **CCN (Javed et al. 2023)** — Exact scalar RTRL credit assignment.
3. **Continual Backprop (Dohare et al. 2024)** — Maturation threshold and utility-driven replacement.
4. **AIRE-Prune (Padhy et al. 2026)** — State controllability and observability importance.
5. **Active Feature Acquisition (Guney et al. 2025)** — Budgeted candidate exploration and screening.
6. **Variable-Tap LMS (Zhao et al. 2008)** — Dynamic temporal lag expansion.

### Question 14: Is that combination trivial or does Track B contain empirically derived interaction logic absent from those works?
**Answer:** **`NONTRIVIAL_EMPIRICALLY_DERIVED_ORGANIZATION`.**  
*Justification:* A naive additive combination of these papers collapses catastrophically in streaming non-stationary environments. Specifically, it suffers from:
- *Newborn shock* (prevented in Track B by probationary shadow evaluation);
- *Quiescent memory annihilation* (prevented by two-timescale structural observability);
- *Asymmetric eviction failure* (prevented by positive obsolescence confirmation under 300:1 loss asymmetry);
- *Unbudgeted input explosion* (prevented by unified probe budgeting).  
These governing mechanisms were derived through systematic empirical failure isolation across M1 through M2-R1.

### Question 15: Which claims must never be presented as novel?
**Answer:**
- **Claim C3 (Temporal lag expansion):** Standard in TDNN and Variable-Tap LMS.
- **Claim C4 (Recurrent state birth from residual error):** Established in Recurrent Cascade-Correlation (1991).
- **Claim C5 (Scalar forward sensitivity RTRL):** Established in Williams & Zipser (1989) and CCN (2023).
- **Claim C6 (Unit maturation thresholds & utility replacement):** Established in Continual Backprop (2021, 2024) and MRAN (1999).

### Question 16: Which claims may still be described as possibly distinctive?
**Answer:**
- **Claim C7:** Parsimonious linear-first vs gated recurrence hierarchy.
- **Claim C8:** Two-timescale structural relevance for online quiescent retention.
- **Claim C9:** Positive obsolescence evidence accumulation under asymmetric eviction loss.
- **Claim C10:** Unified resource-governed structural lifecycle across inputs, lags, and recurrent states.

### Question 17: Which baselines are mandatory?
**Answer:** Five baselines are formally frozen as mandatory for BENCH-01:
1. **`B1_RZA_LMS`** (Reweighted Zero-Attracting LMS; sparse linear baseline);
2. **`B2_CCN`** (Columnar-Constructive Networks; constructive scalar RTRL baseline);
3. **`B3_MUSE_RNN`** (Online recurrent node birth/death baseline);
4. **`B4_MINIMAL_GRU`** (Static, permanently active 1-state gated unit);
5. **`B5_ONLINE_ESN`** (Echo State Network with online adaptive readout).

### Question 18: Which external/public benchmark families should be locked?
**Answer:** Five public streaming datasets are locked:
1. **NSW Electricity Pricing Stream** (AEMO; non-stationary demand/price shocks);
2. **NOAA Jena Weather Stream** (Max Planck; multi-timescale dynamical system);
3. **UCI Gas Sensor Array Drift Stream** (Severe real-world physical drift);
4. **Silverbox Nonlinear System ID Benchmark** (IEEE; physical resonant oscillator);
5. **Friedman Concept Drift Stream** (River ML; non-linear feature drift).

### Question 19: Is the benchmark now scientifically ready?
**Answer:** **`EXTERNAL_BENCHMARK_READY = YES`.**  
*Justification:* The nearest-neighbor map is reconciled, claims C1–C10 are audited with downgrades applied, 5 mandatory and 2 recommended baselines are frozen, 8 mechanistic and 5 public tasks are frozen, Pareto metrics are defined, and success/failure interpretations (Cases A–E) are pre-registered.

### Question 20: Has any evidence emerged that requires reopening M2?
**Answer:** **`NO` (STRICT GOVERNANCE RESTRICTION).**  
*Justification (Section 98):* Milestone M2 was certifiably frozen under `M2_SINGLE_STATE_SPEC.md` following exhaustive empirical validation in M2-R1 (116/116 unit tests passing). The literature review confirmed that Track B’s credit assignment (RTRL), maturation, and utility concepts are mathematically and operationally sound. Similarity to prior art is an expected scientific reality, not an architectural defect. Reopening M2 or modifying the frozen architecture prior to external benchmarking is strictly prohibited.

---

## 3. Mandatory Governance Stop Enforcement (Section 108)

All goals of milestone **PRA-01R** have been fulfilled:
- `PRA_01R_SEARCH_DELTA.md` authored;
- `PRA_01R_RECONCILED_MATRIX.csv` authored;
- `PRA_01R_CLAIM_RECONCILIATION.md` authored;
- `PRA_01R_TOP_THREATS.md` authored;
- `PRA_01R_COMBINATION_ANALYSIS.md` authored;
- `PRA_01R_BASELINE_LOCK.md` authored;
- `PRA_01R_BENCHMARK_LOCK.md` authored;
- `PRA_01R_SUMMARY.md` authored.

**HARD STOP ENFORCED:**  
In strict accordance with Section 108 of the user protocol:
- Milestone M3 remains **UNOPENED**;
- Benchmark execution (BENCH-01) is **UNOPENED**;
- No architecture code or specification has been altered;
- No architecture name or acronym has been assigned;
- No draft abstract or publication claims have been written;
- Awaiting formal review and instruction.
