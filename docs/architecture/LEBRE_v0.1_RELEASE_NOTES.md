# LEBRE Architecture Specification v0.1 — Release Notes

**Version:** 0.1  
**Status:** `FROZEN_WITH_SCOPE_LIMITS`  
**Release Date:** September 19, 2026  
**Stage:** `LEBRE-SPEC-FREEZE-01`  

---

## 1. What Is Frozen

This release formally freezes the **LEBRE Architecture Specification v0.1** along with its formal Portuguese edition, executive overviews, full diagram suite D1–D8, traceability matrices, normative parameter manifest, and derived condensed publication PDFs. All frozen documents have been hashed with SHA-256 and sealed against unauthorized mutation.

---

## 2. Core Architecture

**LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*) is an agile, online adaptive learning architecture designed for continuous streaming regression under extreme micro-resource constraints. Its foundation rests on four core pillars:
1. **Linear-First Parsimony:** Exhausts a sparse linear baseline before allocating non-linear or recurrent structures.
2. **Shadow Probation ($T_{\text{prob}} = 50$, $\theta_{\text{promote}} = 0.05$):** Candidate structures learn decoupled in shadow mode, shielding live inference from gradient shocks.
3. **Two-Timescale Quiescent Retention ($\alpha_{\text{slow}} = 0.005$, $\tau \approx 140$ steps):** Decouples fast instantaneous signal activity from slow structural credit ($U_{\text{ret}}$), bridging extended Poisson silent gaps.
4. **Asymmetric Obsolescence Eviction ($O_{\text{obs}} > 0.80$, $N_{\text{pat}} = 30$):** Implements an empirical $\approx 300:1$ cost asymmetry to eliminate cyclic eviction churn.

The structural lifecycle rigorously progresses through five discrete states:  
$$\text{DORMANT} \longrightarrow \text{PROVISIONAL} \longrightarrow \text{ACTIVE} \longrightarrow \text{MATURE} \longrightarrow \text{EVICTED}$$

---

## 3. Evidence Status

- **Evidence Classification:** `VALIDATED_WITH_SCOPE_LIMITS`
- **Primary Scientific Contribution:** `RESOURCE_GOVERNED_STRUCTURAL_LIFECYCLE`
- **Supporting Contributions:** `TWO_TIMESCALE_QUIESCENT_RETENTION` and `POSITIVE_OBSOLESCENCE_ASYMMETRIC_EVICTION`
- **Milestone Provenance:** Successfully reconciled across experimental phases M1, M2, BENCH-01B, and CAR-01.

---

## 4. Main Benchmark Results

Under the sealed 15-workload benchmark protocol (**BENCH-01B**, 30 random seeds, 450 evaluated runs):
- **Numerical Robustness:** **0.00% divergence rate** (0 divergences in 450 runs), outperforming Cascade Correlation and RZA-LMS which exhibited severe numerical blowups on real-world continuous streams.
- **Observed Mean Algorithmic Compute:** **90.44 FLOPs/step** (compliant with the $R_2\text{-FLOP} \le 100$ FLOPs/step mean benchmark ceiling).
- **Observed Persistent Model RAM:** **440.0 Bytes** (compliant with the $R_2\text{-MEM} \le 1024$ Bytes ceiling).

---

## 5. Known Limitations

1. **High-Order Pure Delay Regimes (Task A4):** Scalar recurrence ($N \le 1$) is fundamentally bounded when modeling high-order distributed lag dependencies, where dense RNN baselines (e.g., GRU, ESN) hold an inductive advantage.
2. **Multi-Frequency Continuous Nonlinear Dynamics (Task B4 - Silverbox):** Fixed random high-dimensional reservoir projections (Online ESN NMSE 0.91359) outperform minimal scalar state adaptation (LEBRE NMSE 0.99320).
3. **Simulation Boundary:** All metrics reflect bit-exact software simulation. Physical bare-metal deployment to microcontrollers has not been executed in v0.1.

---

## 6. What Is Explicitly Not Included

- **Multi-State Recurrent Graphs ($N \ge 2$):** Excluded from v0.1.
- **Nonlinear Multilayer Readout Heads:** Excluded; v0.1 utilizes strictly linear readout ($y_{\text{rec},t} = w_s s_t$).
- **Classification & Sequence-to-Sequence Modeling:** Not supported in this streaming regression specification.
- **Hardware/Battery Claims:** No claims of physical battery longevity, validated RTOS integration, or hardware execution latency are made.
- **Novelty Claims:** `NOVELTY_CLAIM_READY = NO`.

---

## 7. Future Research Boundary

Any future extension—specifically the investigation of multi-state recurrence under Milestone M3—will be conducted under separate experimental milestones and will require a subsequent specification version (v0.2 or higher). LEBRE v0.1 remains frozen as the single-state baseline reference.
