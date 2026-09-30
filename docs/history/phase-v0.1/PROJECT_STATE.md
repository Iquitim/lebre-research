# PROJECT_STATE.md

## Current Status
- **Phase**: Track B — Practical Online Learning System
- **Current Milestone**: CAR-01 — Contribution Assessment Review (COMPLETED)
- **Last Milestone Completed**: CAR-01 (Contribution Assessment Review) — **CAR_01_COMPLETE**
- **Last Audits Completed**:
  - PRA-01 (Adversarial Prior-Art Audit) — **COMBINATION_POSSIBLY_DISTINCT**
  - PRA-01R (Prior-Art Reconciliation & Benchmark Lock) — **COMBINATION_POSSIBLY_DISTINCT_SURVIVES**
  - BENCH-01A (Benchmark Protocol Audit, Fairness Review & Freeze) — **BENCH_01_PROTOCOL_FROZEN**
  - BENCH-01A-R (Surgical Protocol Correction & Re-Hash) — **BENCH_01A_R_CORRECTIONS_COMPLETE**
  - BENCH-01B (Competitive Benchmark Execution) — **COMPLETED, AUDITED & SEALED**
  - CAR-01 (Contribution Assessment Review) — **CAR_01_COMPLETE**
- **Contribution Assessment Summary (CAR-01)**:
  - **Primary Contribution**: `RESOURCE_GOVERNED_STRUCTURAL_LIFECYCLE`
  - **Supporting Contribution 1**: `TWO_TIMESCALE_QUIESCENT_RETENTION`
  - **Supporting Contribution 2**: `ASYMMETRIC_OBSOLESCENCE_GOVERNANCE`
  - **Architecture Classification**: `NONTRIVIAL_EMPIRICALLY_DERIVED_ARCHITECTURE`
  - **Integration Status**: `NONTRIVIAL_EMPIRICALLY_DERIVED_ARCHITECTURE`
  - **Paper Contribution Framing**: `YES_WITH_LIMITATIONS`
  - **Architecture Spec v0.1 Readiness**: `YES`
  - **Architecture Naming Readiness**: `YES`
  - **Next Recommended Stage**: `ARCH-SPEC-01`
- **Benchmark Evaluation Summary (BENCH-01B Empirical Findings)**:
  - **Execution Scope**: 15 Workloads (Block A mechanistic A1–A8, holdouts H1–H2, Block B real-world B1–B5) across 30 seeds ($N=30$, seeds 101–130), 6,750 total competitive runs.
  - **Overall Mean Performance**:
    - **Track B (Frozen M2)**: Mean NMSE = **0.7023**, FLOPs = **90.44**, Memory = **440.0 Bytes**, Completion Rate = **100.0%** (0 divergences).
    - **B1_RZA_LMS**: Mean NMSE = **0.7631**, FLOPs = **179.60**, Completion Rate = **93.3%** (diverged on Jena Weather).
    - **B2_CCN**: Mean NMSE = **0.6490**, FLOPs = **317.07**, Completion Rate = **93.3%** (diverged on Jena Weather).
    - **B3_MUSE_RNN**: Mean NMSE = **1.0010**, FLOPs = **157.89**, Completion Rate = **100.0%**.
    - **B4_MINIMAL_GRU**: Mean NMSE = **0.8730**, FLOPs = **281.80**, Completion Rate = **100.0%**.
    - **B5_ONLINE_ESN**: Mean NMSE = **0.8161**, FLOPs = **1683.67**, Memory = **6112.0 Bytes**, Completion Rate = **100.0%**.
  - **Resource Ceilings**:
    - R2-FLOP ($\le 100$ FLOPs/step): Track B is the **only evaluated adaptive recurrent architecture to pass** (90.44 FLOPs).
    - R2-MEM ($\le 1024$ Bytes): Track B comfortably passes (440.0 Bytes).
  - **Pareto Inhabitation**: Track B strictly Pareto-dominates Minimal GRU and MUSE-RNN in overall benchmark trade-offs; non-dominated within the sub-100 FLOP envelope.
  - **Statistical Significance**: Track B achieved statistically significant superiority in **53.3%** (40/75) of all competitive paired tests across the suite ($p_{\text{FDR}} < 0.05$).
  - **Stability Manifest**: 319 divergences recorded (S2: 109, S5: 60, B1/B2/S1/C1/C4: 30 each); Track B: **0 divergences**.
- **Milestone M2 Status**:
  - **Specification Frozen**: Milestone M2 formally frozen under [`M2_SINGLE_STATE_SPEC.md`](file:///d:/Projetos/Codinome%20Lebre/M2_SINGLE_STATE_SPEC.md). Track B code in `src/` remains 100% bitwise immutable.
- **Milestone M3 Status**: `UNOPENED` (Multi-State Capacity is NOT yet opened).
- **Novelty Claim Readiness**: `NO` (FROZEN).
- **Section 144 Hard Stop**: `ENFORCED` — Architecture unnamed; M3 unopened; novelty claims withheld; CAR-01 completed and awaiting human review.




## LEBRE v0.51 — Research Baseline Freeze (2026-09-25)
- **Stage**: `LEBRE-V0.51-FREEZE-01` — **Status**: `FROZEN_RESEARCH_BASELINE_WITH_SCOPE_LIMITS`
- **Scope**: research line (structural expert S + memory expert M + dynamic model averaging + quantile interval). Does **not** replace the canonical v0.1 (`FROZEN_WITH_SCOPE_LIMITS`); `src/` and `tests/` untouched.
- **Records**: `docs/architecture/LEBRE_v0.51_FREEZE_RECORD.md`, `docs/architecture/LEBRE_v0.51_FREEZE_MANIFEST.yaml`, `docs/architecture/LEBRE_v0.51_SHA256SUMS.txt` (52 files verified).
- **Known limitations frozen with it**: single-latent pole lock; search-throughput latency; partial multi-lag recovery; quantile cadence phase aliasing; memory NLMS without epsilon; no real input-driven structural evidence.
- **Next**: any v0.52 change is compared against this baseline, one isolated pre-registered change per experiment. `NOVELTY_CLAIM_READY = NO`; `M3 = UNOPENED`.
- **Errata 01 (2026-09-25)**: `docs/architecture/LEBRE_v0.51_ERRATA_01.md` — text-only corrections (promotion guarantee holds only under H₀ "S already correct without the candidate"; memory M inspired by, not equivalent to, airline/Holt-Winters; mean-reversion ≠ SES; per-episode error control only). Prior art: `experiments/PRA-02-V051/`.
- **Spec revision 1 (2026-09-25)**: `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.51_SPEC_r1_{PTBR,EN}.pdf` + `ARQUITETURA_V051_r1.md` incorporate Errata 01 (text only); checksums in `docs/architecture/LEBRE_v0.51_r1_SHA256SUMS.txt`; original freeze intact (52/52).
