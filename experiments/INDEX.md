# Experiment index

The 90 folders are grouped by research phase. Each folder is self-contained: scripts, logs, result tables and a report (mostly in Portuguese from v0.3 on).

**Status legend:**
- **F**: covered by a frozen SHA-256 manifest in `docs/architecture/`;
- **P**: covered by the post-freeze record `LEBRE_v0.52_POSTFREEZE_SHA256SUMS.txt`;
- **R**: pre-registered evaluation;
- **H**: historical, superseded by later versions (kept as record and as ablation source).

## LEBRE v0.54 (from 10 Oct 2026) — in design

Scope (project owner, 10 Oct 2026): finish the consolidation — cost proportional to use (M5a layers, M5b core), removals and non-stationary interpretation (M4 + M3), cycle as hypothesis (M6). Baseline in the LEBRE Lab (`diagnosticos/E23_RESULTADO.md`).

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.54-DESIGN-NOTE-01` | Design note 01: failures, measured baseline, changes, criteria, process, reserve decisions | design |
| `LEBRE-V0.54-DATA-01` | Final-evaluation reserve (drawn 10 Oct 2026, before any v0.54 code): CAMELS-BR 140–169, BDG2 115–144, 8 wind plants (seed 5421), 8 solar plants Jan–Sep 2026 (seed 5422, time split), 17 non-stationary level series (EIA, US Treasury); raw-data snapshot hashes, guard | F |

## LEBRE v0.54 (10–14 Oct 2026) — promoted

Promoted on 13 Oct 2026 by a pre-registered binding rule; errata 01 on 14 Oct 2026 (freeze record `docs/architecture/LEBRE_v0.54_FREEZE_RECORD.md` and addendum 01; self-contained spec `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.54_SPEC_{EN,PTBR}.pdf`). Development, validations 6 and 7, the errata measurements and the bench part of the audit are in the public LEBRE Lab: [github.com/Iquitim/lebre-lab](https://github.com/Iquitim/lebre-lab).

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.54-DESIGN-NOTE-01` | Design note, specification drafts of M5a (drafts 0–2), M5b (drafts 0–2), M4 (drafts 0–1) and M6 (drafts 0–1), M3 diagnosis, literature audit PRA-11 (in Portuguese) | F |
| `LEBRE-V0.54-DATA-01` | Final-evaluation reserve (drawn 10 Oct 2026, before any v0.54 code), raw-data snapshot hashes, guard | F |
| `LEBRE-V0.54-PROTO-01` | **v0.54 implementation** (frozen code: commit `f9906c4`; final evaluation run with `cfe72ce`, identical forecasts): v0.53 copied byte for byte from `lebre==0.2.0` + M5a (`dormancy.py`) + M5b (`screening.py`) + M4 (`removal.py`); M6 (`cycle.py`) present and off; tests | F |
| `LEBRE-V0.54-FINAL-01` | Final evaluation (93 reserved series): pre-registration, loaders, run and analysis scripts, rehearsal, run notes, results, errata 01 | F, R |
| `LEBRE-V0.54-AUDIT-01` | Post-promotion stress audit: plan, scripts, numerical summary and report | F |

## Towards v0.56 (from 25 Oct 2026)

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.56-DIAG-01` | Basin diagnosis (exploratory, consumed reserves only: CAMELS-BR positions 140–169 for discovery, 110–139 for replication; v0.55 data excluded, unused basins sealed): which ingredient of the recursive-least-squares ARX explains its advantage over v0.55 on basins. Result: second-order adaptation and the autoregressive dynamics of the memory, both replicated; acceptance delay and forgetting rejected | F |
| `LEBRE-V0.56-DIAG-02` | M1 diagnosis on the same consumed basin reserves: M1 is already an RLS ARX, but updated every 8 targets, clipped around the core forecast and with two target lags; the three removed together close most of the gap to the RLS ARX (D-A 1.124 → 1.016; D-B 1.053 → 0.959), replicated, at ~2.7× the cost | F |
| `LEBRE-V0.56-DATA-01` | Source of new basins for the v0.56 final evaluation, decided before any download: CAMELS-CL 2018 (PANGAEA, CC-BY-4.0) | decision |

## LEBRE v0.55 (16–17 Oct 2026) — promoted

Promoted on 17 Oct 2026 by a pre-registered binding rule (freeze record `docs/architecture/LEBRE_v0.55_FREEZE_RECORD.md`; self-contained spec `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_{EN,PTBR}.pdf`). Development rounds D1 to D4, the fixed bench (round D5) and the confirmation C1 are in the public LEBRE Lab: [github.com/Iquitim/lebre-lab](https://github.com/Iquitim/lebre-lab) (`analises/`).

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.55-FRONTIERS-01` | Audit of the v0.54 architecture and research programme for four candidate frontiers (sequential validity under adaptive NLMS, memory–structure cascade, memory of intermittent relations, high-dimensional discovery): evidence already on record, deductions, literature, decision matrix, roadmap (in Portuguese). No new measurement | design |
| `LEBRE-V0.55-DESIGN-NOTE-01` | Design note 01 (draft 0) of the memory-anchored core with a slow test reference: theoretical target (structural FDR <= 2 alpha + P(reference error event)), specification, development measurement D1 to pre-register; formal note F1 (validity of the e-processes under any predictable learner; e-LOND with asynchronous decisions; joint bound 2 alpha) with a numerical sanity check (in Portuguese). No measurement | design |
| `LEBRE-V0.55-PROTO-01` | v0.55 development prototype: v0.54 copied byte for byte (`f9906c4`) + `anchored.py` (levers ANCHOR, SLOW, REF_CORE; drafts 0-2) and `model055.py` (variants A, A0, B, B1, B2, B4, B5); tests (bit-for-bit identity of the rewrite with v0.54, no leakage, slow-reference alignment); smoke record that chose the D1 variants (cascade on the live forecast and slow reference alone are negative development results) | dev |
| `LEBRE-V0.55-DATA-01` | Validation series of v0.55 drawn from metadata only (CAMELS-BR positions 170-189, BDG2 145-174; 47 basins and 591 meters left for the final evaluation) | data |
| `LEBRE-V0.55-VAL-01` | Pre-registered validation of the anchored core (B10, frozen at `b0522a0`) against v0.54 on the never-used real series | val |
| `LEBRE-V0.55-DATA-02` | Final-evaluation reserve of v0.55 (rules committed before any download; metadata-only draw): CAMELS-BR 190-219, BDG2 175-204, 8 wind (seed 5521), 8 solar Jan-Sep 2026 (seed 5522), 8 ECB euro reference rates outside the Fed H.10; commercial paper rates excluded by the coverage rule; raw-data hashes | F |
| `LEBRE-V0.55-FINAL-01` | Pre-registered final evaluation of v0.55 (B10 vs v0.54, real inputs and placebo random-walk inputs as a negative control; binding promotion rule R1-R5) | F |
| `LEBRE-V0.55-COMP-01` | Comparison of v0.55 with external models on the v0.55 reserve (reference only, outside the promotion): online linear (ARX NLMS/RLS, NLinear, DLinear), SARIMAX-X, gradient boosting, Chronos-2 (with and without covariates), Chronos-Bolt, TTM (zero-shot and fine-tuned with inputs); paired block bootstrap, Holm correction | ref |

## LEBRE v0.53 (5–9 Oct 2026) — promoted

Promoted on 9 Oct 2026 by a pre-registered binding rule (freeze record `docs/architecture/LEBRE_v0.53_FREEZE_RECORD.md`; self-contained spec `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_{EN,PTBR}.pdf`). Development, validations 1 to 5 and diagnostics are in the public LEBRE Lab: [github.com/Iquitim/lebre-lab](https://github.com/Iquitim/lebre-lab).

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.53-DESIGN-NOTE-01` | Design note, specification drafts of M1 (drafts 0–5) and M2 (drafts and candidates D, S, M, P, Q, Q2), decidability ruler and its addenda, literature audits PRA-06 to PRA-10 (in Portuguese) | F |
| `LEBRE-V0.53-DATA-01` | Final-evaluation reserve (drawn 5 Oct 2026, before any v0.53 code), raw-data snapshot hashes, guard | F |
| `LEBRE-V0.53-DIAG-F9-01` | Diagnosis of F9 (spurious inputs on price levels) | exploratory |
| `LEBRE-V0.53-PROTO-01` | **v0.53 implementation** (promoted code: commit `4a2620e`): frozen v0.52 core copied byte for byte + M1 (`precisao.py`) + M2 (`agregacao.py`, `model053.py`); tests | F |
| `LEBRE-V0.53-FINAL-01` | Final evaluation (104 reserved series): pre-registration, loaders, run and analysis scripts, tests without the reserve, rehearsal, run notes, results, SARIMAX addendum | F, R |

## LEBRE v0.52 (25–29 Sep 2026)

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.52-DATA-01` | Dataset selection, licences, download, seeded split (`SPLIT_V052.json`) | F |
| `LEBRE-V0.52-DESIGN-NOTE-01` | Design notes and algorithm specification drafts (§0–§13) | F |
| `LEBRE-V0.52-PROTO-01` | **Python reference implementation** (`lebre_v052h.py`, `change_engine.py`, `lebre_v052.py`); data loader; comparators; development measurements #1–#7; ablations; stress test; `DEV_LOG.md` | F |
| `LEBRE-V0.52-HELDOUT-01` | Reserve 1 (125 series) — revealed the target-gap failure | F, R |
| `LEBRE-V0.52-HELDOUT-02` | Reserve 2 (40 series) — confirmed the fix; canonical configuration defined here | F, R |
| `PRA-03-PREDICTIVE-GROWTH`, `PRA-04-V052` | Prior-art audits (v0.52) | F |
| `LEBRE-V0.52-EXT-01` | Post-freeze extension: misadjustment note, ultralight/TTM comparators, **C99 port** (`lebre_c/`), **simulated Cortex-M4F** (`mcu/`) | P |
| `LEBRE-V0.52-HELDOUT-03` | Reserve 3 (60 series): ultralight, TTM, C port, MCU | P, R |
| `LEBRE-V0.52-DOC-01` | Documentation support (illustrative runs, trace breakdown, MCU profile; development data only) | F (spec r0 manifest) |
| `LEBRE-V0.52-EXT-02` | Spec r1 checks: false-change simulation, exploratory "all on" ablation, literature audit PRA-05 | F (spec r1 manifest) |

## v0.51 (23–25 Sep 2026) — frozen research baseline

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.51-LEAN-01` | v0.51 implementation and pre-registered evaluation | F |
| `LEBRE-V0.51-EXTERNAL-CRITIQUE-FORENSIC-INVESTIGATION-01` | Forensic answers to an external critique (memory expert dominates on real data) | F |
| `PRA-02-V051` | Prior-art audit of v0.51 | H |

## v0.3–v0.5 (22–23 Sep 2026)

| Folder | Role | Status |
|---|---|---|
| `LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01` | v0.3.x design and code audits (v0.3.2 research spec) | H |
| `LEBRE-V0.3-EXTERNAL-BENCH-02` | External benchmark of v0.3.2 | H |
| `LEBRE-V0.4-EXTERNAL-BENCH-04`, `LEBRE-V0.4-PROMOTION-01` | v0.4 benchmark and promotion study | H |
| `LEBRE-V0.45-ROBUST-GUARD-01` | v0.4.5 (input-contract quarantine) | H |
| `LEBRE-V0.46-STABLE-COMPETITIVE-01` | v0.5 (three online experts, exponential aggregation) | H |

## v0.2 line (20–22 Sep 2026)

All folders here have status H.
- **Resource and seal audits:** `LEBRE-V0.2-INTEGRATION-DESIGN-01`, `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`, `LEBRE-V0.2-RESOURCE-COMPACTION-01`, `…-RESOURCE-COMPACTION-CORRECTIVE-CONFIRMATION-01`, `…-RESOURCE-COMPACTION-SEAL-01`, `…-SEAL-ARTIFACT-RECONCILIATION-01`, `…-SEAL-AUDIT-ERRATA-01`, `RESOURCE-ACCOUNTING-RECONCILIATION-01`.
- **Shadow/rent governance, multirate and arbitration studies:** `…-SHADOW-RENT-GOVERNANCE-01`, `…-SHADOW-RENT-SEAL-ERRATA-01`, `…-SHADOW-MULTIRATE-DECOMPOSITION-01`, `…-MULTIRATE-SEAL-AUDIT-01`, `…-RECURRENT-SHADOW-COST-RECONCILIATION-01`, `…-RECURRENT-SHADOW-SEAL-AUDIT-01`, `…-K2-ARBITRATION-COMPOSITION-01`, `…-K2-ARB10-COMPOSITION-SEAL-AUDIT-01`, `…-K2-CONFIRMATION-SEAL-AUDIT-01`, `…-K2-CORRECTIVE-CONFIRMATION-01`, `…-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01`.
- **Search-space and resource design:** `…-CORRELATION-SEARCH-SPACE-COMPACTION-01`, `…-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`, `…-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01`, `…-COMBINED-RESOURCE-PARETO-DESIGN-01`.

## Foundation — v0.1 era (18–19 Sep 2026)

The v0.1 specification remains the project's canonical reference; its freeze is recorded in `docs/architecture/LEBRE_v0.1_*`. All folders here have status H.
- **Early experiments:** `EXP-0001b` … `EXP-0010`, `M1-R1`, `M2-EXP-0001` … `M2-EXP-0006`, `M2-EXP-0005R`, `M2-R1`, `LEBRE-DIAG-01`.
- **Benchmark protocol:** `BENCH-01A`, `BENCH-01A-R`, `BENCH-01B`, `CAR-01`, `PRA-01`, `PRA-01R`.
- **Architecture specification and seal:** `ARCH-NAME-01`, `ARCH-SPEC-01`, `…-01R`, `…-01R2`, `…-01R2a`, `AUDIT-SEAL-01`, `LEBRE-SPEC-FREEZE-01`.
- **Mechanism studies:** `CAPACITY-DECOMPOSITION-01`, `BOUNDED-HISTORY-LAG-INTEGRATION-01`, `DYNAMIC-LAG-LIFECYCLE-01`, `DYNAMIC-LAG-LIFECYCLE-01A`, `PROMOTION-POLICY-01`.
- **Shared benchmark code:** `bench01/`, imported as `experiments.bench01` by later lines, e.g. the causal input scaler. `EXP-0001/` holds the first experiment runner with its configuration and results.

Early-phase documents (`BENCH_01_SPEC.md`, `M1_SPEC.md`, `M2_*.md`, `PROJECT_STATE.md`, `FAILURE_LOG.md`, …) are in `docs/history/phase-v0.1/`; reports of this phase still cite them by file name. The packages `src/` and `tests/` also belong to this phase; they stay at the root because 43 early scripts import `src`.
