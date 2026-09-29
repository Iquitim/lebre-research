# Phase A — Artifact & Provenance Audit

**Stage:** `LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01`
**Stochastic streams executed:** 0
**Canonical `src/` / `tests/` modified:** NO

## A1. Parent artifacts located

All nine required seal-audit artifacts exist and were read in full:
`K2_ARB10_SEAL_AUDIT_FINAL_REPORT.md`, `K2_ARB10_SEAL_CORRIGENDUM.md`, `K2_ARB10_SEAL_ROOT_CAUSE_ANALYSIS.md`,
`SWITCHING_CONTRAST_RECONCILIATION.csv`, `A0_A1_A2_ORTHOGONAL_RESOURCE_LEDGER.csv`, `K2_ARB10_CLAIM_AUDIT.csv`,
`FUTURE_EMA_TIMESCALE_HYPOTHESIS.md`, `POST_SEAL_RESEARCH_BRANCH_DECISION.md`, `K2_ARB10_SEAL_AUDIT_MANIFEST.json`.

Parent `LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01` was inspected. The Level-1/Level-2 sources were
`K2_ARB10_FINAL_RESULTS.csv` (1260 rows, 420 per arm, seeds 1971..2000), `trans_windows_cache.json`,
`run_k2_arb10_composition.py` and the imported `scratch/run_v02_correlation_search_compaction.py`.

## A2. Hashes

`PARENT_HASHES.txt` gives SHA-256 hashes for 80 parent files: both parent stage directories plus the three imported scratch modules.
Every file listed in the seal manifest `K2_ARB10_SEAL_AUDIT_MANIFEST.json` was re-hashed and compared.
**Drift: none.** The sealed artifacts are byte-identical to their sealed state.

## A3. Level-1 / Level-2 re-verification performed here

| Check | Result |
|---|---|
| Sealed arm means of `total_fp_mean` (A0 / A1 / A2) | 111.188662 / 100.674818 / 96.957851, reproduced from `K2_ARB10_FINAL_RESULTS.csv` |
| Per-row identity `shadow_fp = search + recurrent_shadow + candidate_descendant` | residual within ±7.1e-15 on all 1260 rows, so the ledger identity holds at row level and is **not** tautological |
| Per-row identity `total_fp = live_fp + shadow_fp` | exact |
| `arb_executions` per run | 1200 (K5), 600 (K10), matching the cadence |

## A4. Authority conflicts found (higher level wins; recorded, not silently resolved)

| ID | Lower-authority statement | Higher-authority fact (Level 2 code) | Consequence for this design |
|---|---|---|---|
| PA-01 | Seal `A0_A1_A2_CONFIG_RECHECK.csv` (L5) and parent `K2_ARB10_CONFIRMATORY_FREEZE.md` (L4) give `theta_tol = 0.01` | `BaseLEBREArchitecture.__init__`: `self.theta_tol = 0.015` | The future freeze must cite **0.015**. The same value applied to all arms, so parent contrasts are unaffected. The parent `K2_ARB10_MECHANISM_ATTRIBUTION.md` narrative ("exceed θ_tol = 0.01") is imprecise. |
| PA-02 | Seal config recheck: `theta_promote = 0.03` | No `theta_promote` symbol exists in the executed path. Promotion uses candidate `evidence > 0.02` together with the EMA regime tests against `theta_tol` and the `0.015` conditional-pair threshold | Freeze by the executable rule, not by a named constant. |
| PA-03 | Seal config recheck: `T_probation = 300` | `obs_count >= 15` (T_prob = 15 observations). `300` is the **eviction warm-up guard** `step_count > 300` | Two distinct parameters. Both are frozen. |
| PA-04 | Seal config recheck: `K_rec_learning = 1` | Runner passes `K_rec_learn = 10`. The freeze doc says 10 | Use 10. |
| PA-05 | `POST_SEAL_RESEARCH_BRANCH_DECISION.md` proposes a **3-arm** trial (B0, B1, B2 with different semantics) | This stage's protocol (L8) specifies **4 arms** | The 4-arm design is adopted because it adds the concurrent negative control B2, which the clean B3−B2 contrast needs. The label mapping differs from the seal's, so readers must not cross-reference arm letters. |
| PA-06 | Result fields `g_db_mean`, `g_rb_mean`, `g_d_br_mean`, `g_r_bd_mean` are named "mean" | The runner stores `float(model.ema_G_D_B)` etc., i.e. the **terminal EMA value at step 6000** | The I9 complementarity gate reads the EMA itself. B3 changes the EMA coefficient, so the gate's **measuring instrument changes with the intervention** (see preregistration §I3). |
| PA-07 | — | EMA literals are hard-coded (`0.98 *`, `0.02 *`) in `CompositionSparseModel.step`, with no alpha parameter | B3 needs a code change. The preregistration requires a code-equivalence regression before any fresh execution. |
| PA-08 | — | Gain telemetry exists **only** as post-update EMA values of `G_D|B` and `G_R|B`, for seed 1971, tasks I11–I14, loop indices 2900..3299 | The Phase D diagnostic is necessarily partial (see `MEOE_DIAGNOSTIC_REPORT.md`). |
| PA-09 | — | `recurrent_shadow_fp` is written as the static formula `18/K_rec_forward + 2.2`. It agrees with measured shadow FP (row identity holds) | Acceptable, but the future runner should record measured recurrent FP directly. |
| PA-10 | — | Results do not contain `CAST_OPS`, `PERSISTENT_MEMORY` or `PEAK_WORKING_MEMORY`. `occupied_bytes` is computed per step but not saved | These are telemetry gaps against the resource-governance requirement. The future runner must log them without affecting behavior. |

None of PA-01..PA-10 changes a sealed pass/fail decision. None of them required new data.

## A5. Protocol-integrity note

The design protocol received for this stage was **truncated** partway through Phase I, section I4 ("recovery_latency(").
Every phase from I4 onward, including any required deliverables list and decision vocabulary, was not
received. Where the design needs content from those sections, this stage uses the parent's frozen rules
(for example the switching gate `≤ +50` stream steps against the original local reference) and marks the item
`PROTOCOL_TEXT_MISSING — PARENT RULE CARRIED FORWARD`.
