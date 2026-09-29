# Design Decision Report — LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01

**Stage type:** deterministic design + audit + preregistration. **Stochastic streams executed: 0.**
**Canonical `src/` / `tests/` modified: NO.** M3 `UNOPENED`. `NOVELTY_CLAIM_READY = NO`. Gate 6 `FAIL` (frozen).

## Decision

```
FRESH_CONFIRMATION_SCIENTIFICALLY_JUSTIFIED   = YES  (as a mechanism-isolation experiment)
CAUSALLY_INTERPRETABLE                        = YES  for E3 via B3−B2; E1+E2 remain jointly confounded in B3−B1
RESOURCE_FEASIBLE (projection)                = LIKELY  (fails only under overactivation beyond the B0 level)
SUFFICIENTLY_PREREGISTERED                    = NOT YET — draft pending human review (see blocking items)
PRIOR_EXPECTATION_OF_FULL_BEHAVIORAL_RECOVERY = UNCERTAIN / MODEST
EXECUTION_AUTHORIZED                          = NO
```

## Why the experiment is justified

1. **The derivation is exact and non-empirical.** α = 0.0396 reproduces the K5 stream-time pole, τ and half-life to machine
   precision, and it was not selected on any data (`EQUIVALENCE_CERTIFICATION.md`). A fresh cohort can test it without a
   selection-bias problem.
2. **B3 − B2 is a clean single-parameter contrast** (asserted in `FUTURE_ARM_CONFIG_DIFF.csv`), and it answers a question the
   sealed study could not: whether E3 contributes causally to the ARB10 penalty.
3. **E3 is a plausible large contributor.** The sealed threshold-crossing delays (median 175, P95 248.5 stream steps) are on
   the scale of the K5 crossing times themselves, which is what doubling the stream-time pole predicts. Under a step change in gain, B3 reaches any
   threshold at the K5 crossing time rounded up to the 10-step grid, i.e. within +5 steps of K5 (`LEBRE_SPECIFIC_HYPOTHESIS`).

## Why full recovery is not the expected outcome

1. **Noise-equivalence is not preserved.** B3 restores the K5 lag but averages about half as many gain samples. Its stationary EMA variance is
   ~2× K5 under iid gains, and it faces hard thresholds (θ_tol = 0.015, evictions at 0.005 / 0.008).
2. **The sparse-evidence mismatch is threshold-scale.** On the sealed seed-1971 transition windows, per-block |MEOE| has P95
   values up to 0.074, several times θ_tol. The changepoint concentration is borderline (R ≈ 1.95–2.11; pre-declared verdict
   `MIXED`).
3. **The open-loop filter replay is only partly favorable.** B3 cuts threshold-side disagreement with K5 from 130 to 97 of 1248 comparisons, but it deviates *more* than
   B2 in 7 of 16 trajectories.
4. **The acceptance bar is steep.** Depending on the unknown paired SD, B3 must recover about 51–90% of the sealed A2 − A1 penalty to pass
   non-inferiority against B0.
5. **E1 is untouched.** The maximum scheduler wait stays at 9 steps, and decision opportunities stay halved.

The most probable informative outcome is `E3_CAUSALLY_CONTRIBUTES_INSUFFICIENT_ALONE`. A full pass is possible but should
not be presumed. Either outcome is scientifically useful, which is the justification for running the experiment.

## Blocking items before the preregistration can be frozen (human review)

| # | Item | Source |
|---|---|---|
| BI-1 | Approve the seed block **2056..2085** (2001..2030 rejected for overlap) and re-scan at execution time | `SEED_BLOCK_OVERLAP_2001_2030.csv` |
| BI-2 | Correct the frozen parameter values to the executable code (θ_tol = 0.015, T_prob = 15 obs, warm-up 300, K_rec_learn = 10) | `ARTIFACT_PROVENANCE_AUDIT.md` PA-01..04 |
| BI-3 | Approve the α-invariant I9 instrument alongside the historical terminal-EMA instrument | PA-06, prereg §9 |
| BI-4 | Authorize the seed-1971 code-equivalence regression (software check only; it re-executes a sealed seed) | prereg §5.2 |
| BI-5 | Approve the non-interfering telemetry additions (raw gains, shadow midpoint gains, casts, memory) | prereg §5.3 |
| BI-6 | Supply the truncated remainder of the stage protocol (from I4 onward), or accept the parent switching rule carried forward | `ARTIFACT_PROVENANCE_AUDIT.md` §A5 |
| BI-7 | Accept the H8 backfill classification thresholds (churn 1.25 × B1) | prereg §8 |

## Claim limits

No claim of global validation, novelty, energy efficiency, hardware feasibility or optimality. FP counts are
operation accounting, not energy. All MEOE and replay numbers are single-seed descriptive diagnostics on sealed telemetry.

## Outputs of this stage

| File | Phase |
|---|---|
| `PARENT_HASHES.txt` | A2 |
| `ARTIFACT_PROVENANCE_AUDIT.md` | A |
| `POLE_EQUIVALENCE_VERIFICATION.csv`, `EMA_OPERATING_POINT_COMPARISON.csv`, `EQUIVALENCE_CERTIFICATION.md` | B |
| `TEN_STEP_MISMATCH_DERIVATION.md` | C |
| `MEOE_BLOCK_LEVEL.csv`, `MEOE_BY_TASK_AND_WINDOW.csv`, `MEOE_CHANGEPOINT_RISK.csv`, `MEOE_TELEMETRY_INTEGRITY.csv`, `OPEN_LOOP_FILTER_REPLAY.csv`, `MEOE_DIAGNOSTIC_REPORT.md` | D |
| `EMA_TIMESCALE_PRESERVATION_LITERATURE_NOTE.md` | E |
| `FUTURE_ARM_CONFIG_DIFF.csv`, `SEED_BLOCK_OVERLAP_2001_2030.csv`, `CONFIRMATION_01_PREREGISTRATION_DRAFT.md` | F–I |
| `generate_ema_timescale_design.py`, `DESIGN_COMPUTATION_SUMMARY.json`, `run_log.txt`, `DESIGN_MANIFEST.json` | reproducibility |
