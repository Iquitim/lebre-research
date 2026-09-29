# Preregistration DRAFT — LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-CONFIRMATION-01

**Status:** `DRAFT_PENDING_HUMAN_REVIEW`. **Not frozen. Execution: NOT AUTHORIZED.**
**Drafted by:** `LEBRE-V0.2-ARB10-EMA-TIMESCALE-PRESERVATION-DESIGN-01`
**Governance carried forward:** LEBRE v0.1 `FROZEN_WITH_SCOPE_LIMITS`; M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`;
`SAFE_FOR_INTEGRATED_VALIDATION = NO`; Gate 6 historical `FAIL` (frozen, no repair); search is not globally validated;
canonical `src/` and `tests/` are immutable.

---

## 1. Question

With E1 (decision-opportunity decimation) and E2 (gain-evidence subsampling) held at their K_arb = 10 values, does
restoring only E3 (the EMA stream-time pole) through α = 0.039600:

- **(Q-mech)** improve on the failed ARB10 condition? This is contrast **B3 − B2**.
- **(Q-accept)** recover enough to give a locally acceptable, resource-compliant architecture? This is contrast **B3 − B0** plus the resource gate and guardrails.

## 2. Arms (F2)

| Arm | K_rec_forward | K_arb | α_gain_EMA | EMA literals (q, α) | Role |
|---|---|---|---|---|---|
| B0 | 1 | 5 | 0.020000 | 0.98, 0.02 | Original local v0.2 reference (**not** "canonical v0.1") |
| B1 | 2 | 5 | 0.020000 | 0.98, 0.02 | Confirmed K2 reference |
| B2 | 2 | 10 | 0.020000 | 0.98, 0.02 | Concurrent negative ARB10 control |
| B3 | 2 | 10 | **0.039600** | **0.9604, 0.0396** | Pole-preserved ARB10 candidate |

**Scope of α_gain_EMA:** α applies to **exactly** the four arbitration conditional-gain EMAs
(`ema_G_D_B`, `ema_G_R_B`, `ema_G_D_BR`, `ema_G_R_BD`). It does **not** apply to:
`rec_evidence` (0.98/0.02 at K_rec_learn = 10), candidate `evidence` (0.95/0.05), tap `R` (0.999/0.001), or the frontier `corr` EMA
(0.95/0.05). Those stay bit-identical across all arms.

**No other α values** are allowed (F9). There is no DEV cohort (F10).

## 3. Single-intervention invariants (F7), asserted programmatically before execution

- `B3 − B2`: exactly one differing key, `alpha_gain_EMA`. Asserted in `generate_ema_timescale_design.py::arm_config()`, with output in
  `FUTURE_ARM_CONFIG_DIFF.csv`.
- `B2 − B1`: exactly one differing key, `K_arbitration`.
- The runner must re-assert both invariants on its own configuration objects at start-up and abort if either fails.

## 4. Frozen parameters (F8), cited from executable code (Level 2), not from the seal's config table

H = 32, B = 4, K_probe = 2, K_cand_obs = 5, K_cand_learn = 10, candidate promotion requires `evidence > 0.02` and
`obs_count ≥ 15` (T_prob), candidate prune `stream_age > 150 and evidence < 0.02`, **θ_tol = 0.015**, conditional-pair
threshold 0.015, lag eviction `G_D|B < 0.005`, recurrent eviction `G_R|B < 0.008`, eviction warm-up guard `step_count > 300`,
tap learning rate 0.08, K_rec_learn = 10, HOLD_STATE, 28 FP per arbitration event, 6000 steps per run, tasks from
`scratch/bench_v02_integration.BENCHMARK_TASKS`, normalization, fp16 history and frontier, winner/promotion/retention/eviction logic unchanged.
(See `ARTIFACT_PROVENANCE_AUDIT.md` PA-01..PA-04 for the seal-table discrepancies these values supersede.)

## 5. Implementation requirements (must be satisfied before any fresh-seed execution)

1. **Parameterize without perturbing references.** Replace the hard-coded EMA literals with arm-supplied `(q, α)`. For
   B0–B2 the arithmetic must stay `0.98 * E + 0.02 * g`, in that operand order, so the results are bit-identical to the parent.
2. **Code-equivalence regression (requires explicit human authorization, because it re-executes a sealed seed).** The new runner's
   B0, B1 and B2 on seed 1971 × 14 tasks must reproduce the corresponding A0, A1 and A2 rows of `K2_ARB10_FINAL_RESULTS.csv` **exactly**
   (nmse, total_fp_mean, promotions, evictions, terminal EMAs). The result is used only as a software check. It never enters inference.
3. **Non-interfering telemetry** (all arms, all runs), logged outside the FP ledger and asserted not to mutate model state:
   - raw per-event gains `g_d, g_r, g_d_br, g_r_bd` at every executed arbitration event, with step index;
   - for the K10 arms, the **shadow midpoint gains** at `step_count % 10 == 5`, computed read-only from values already present in
     the step (`y_base`, `y_lag_eval`, `y_rec_shadow_val`). This allows direct, cohort-wide MEOE and closes the Phase D gap;
   - EMA threshold-crossing times (θ_tol and eviction levels), and promotion and eviction timestamps by type;
   - `CAST_OPS`, `PERSISTENT_MEMORY` (max `occupied_bytes`), `PEAK_WORKING_MEMORY`, and measured recurrent FP.
4. **Seed rescan at execution time** (§6), recorded in the execution manifest.

## 6. Cohort (F11, F12)

- The suggested block **2001..2030 is REJECTED**. Seeds 2026..2030 were used by `experiments/M1-R1` (`all_runs.csv`) and are
  referenced in `tests/test_m2_exp_0001.py`. Seed 2024 appears in `tests/test_m2_exp_0002.py`. See `SEED_BLOCK_OVERLAP_2001_2030.csv`.
- **Proposed block: 2056..2085** (N = 30). This is the first fully unused contiguous block ≥ 2001 under a repository-wide scan of CSV seed columns,
  `range(a, b)` literals, `a..b` ranges and `seed=` literals. The scan must be re-run right before execution. If any seed in
  2056..2085 is in use by then, reject the whole block and take the next fully unused one.
- 30 seeds × 14 tasks × 4 arms = **1680 runs**. At 6000 steps each, that is **10,080,000 model-stream steps**.
- Stream RNG is `np.random.RandomState(seed)`. The same seed drives all four arms, so the design is paired.

## 7. Statistical plan (G1–G12)

**Inferential unit:** seed (N = 30). For each seed and arm, NMSE is first averaged over I1..I14, and then paired differences are formed across seeds.
Rows at the task, step and event level are never treated as independent samples (G12).

| ID | Contrast | Test | Decision role |
|---|---|---|---|
| P-A | **B3 − B0** | One-sided 95% upper bound < **+0.010000** (NI) | **Primary acceptance** |
| P-M | **B3 − B2** | H0 μ ≥ 0 vs H1 μ < 0; one-sided 95% upper bound < **0** | **Primary mechanistic rescue** |
| S-1 | B1 − B0 | NI at +0.010000 | K2 replication diagnostic |
| S-2 | B2 − B0 | NI at +0.010000; expected to FAIL | Negative-control replication. If it unexpectedly passes: `NEGATIVE_CONTROL_REPLICATION_ANOMALY`, B3 results are kept, and mechanism claims need human review |
| S-3 | B3 − B1 | descriptive | Residual K10 effect after pole compensation, attributable **jointly** to E1 + E2 (not separable in this design) |
| S-4 | B2 − B1 | descriptive | Replicates the sealed ARB10 causal effect |

For every contrast, report: mean, median, SD, SE, one-sided bound where applicable, two-sided 95% CI, paired t versus 0,
p-value, Cohen's dz, and wins / losses / ties (G11).

**Multiplicity.** Q-accept is an intersection-union decision: every component gate (P-A, resource, guardrails) must
pass, so no α adjustment is needed. Q-mech is a separate scientific question tested at one-sided α = .05.
The secondary contrasts are diagnostic and do not gate either decision.

**Detectability (planning arithmetic, not a power guarantee).** The SD of the B3 − B0 differences is unknown. It lies between the
sealed K2-like SD (0.0041) and the ARB10-like SD (0.0182):

| Assumed SD(B3 − B0) | P-A requires mean(B3 − B0) < | Implied residual B3 − B1 < | Share of sealed A2 − A1 penalty (0.011352) that must be recovered |
|---|---|---|---|
| 0.0041 | 0.00872 | 0.00552 | ≥ 51% |
| 0.0080 | 0.00752 | 0.00432 | ≥ 62% |
| 0.0120 | 0.00628 | 0.00308 | ≥ 73% |
| 0.0182 | 0.00434 | 0.00115 | ≥ 90% |

(Uses t₀.₉₅,₂₉ = 1.6991 and assumes B1 − B0 ≈ +0.003196, as sealed.)
P-M power (one-sided α = .05, N = 30) if B3 recovers a fraction f of the sealed penalty: with SD(B3 − B2) = 0.0181, the power is
0.21 / 0.51 / 0.81 / 0.96 for f = .25 / .50 / .75 / 1.0. With SD = 0.012 it is 0.35 / 0.81 / 0.98 / 1.00.
**A partial rescue of around 25% would probably go undetected at N = 30.** A null P-M therefore does **not** show that E3 is irrelevant.

## 8. Resource plan (H1–H8)

- **H1 (binding):** B3 mean total online FP ≤ **100.000000** FP/step, unrounded.
- **H2:** direct arbitration FP is 28/10 = **2.800000** in both B2 and B3. The α value does not change the operation count, so any B3 − B2 difference is indirect.
- **H3–H5:** there is no fixed expected B3 value. For planning only: if B3's structural activity matched B1, total ≈ 100.674818 − 2.8 = 97.87.
  If B3 matched B0's live-FP level (75.64) with B1's search and recurrent costs, total ≈ 99.38. The only threat to the gate is **overactivation beyond the B0 level**,
  which is the resource face of the threshold-noise risk.
- **H6:** report for all arms: live, search, recurrent, candidate direct, arbitration, candidate descendant, total FP; integer ops;
  casts; memory traffic; persistent memory; peak working memory.
- **H7:** `candidate_descendant_fp` is inclusive (direct + arbitration). The orthogonal identity is
  `TOTAL = LIVE + SEARCH + RECURRENT + CANDIDATE_DESCENDANT`. Its residual must be reported for every row.
- **H8 (backfill classification, rule fixed here).** Define churn = (lag + recurrent promotions + evictions) per run. If mean FP(B3) > mean FP(B2):
  - `BENIGN_BEHAVIORAL_BACKFILL`: P-M rescue supported **and** churn(B3) ≤ 1.25 × churn(B1).
  - `PATHOLOGICAL_OVERACTIVATION`: P-M not supported **and** churn(B3) > 1.25 × churn(B1).
  - `MIXED`: exactly one of the two conditions above holds.
  - `UNRESOLVED`: telemetry is missing or inconsistent.

## 9. Temporal guardrails (I1–I4 onward)

The judging contrast for every guardrail is **B3 − B0**. B3 − B2 and B3 − B1 are reported alongside.

| Guardrail | Rule |
|---|---|
| I6 | mean ΔNMSE(B3 − B0) ≤ +0.010000 |
| I7 | mean ΔNMSE(B3 − B0) ≤ +0.010000. Also report reactivation latency (existing `quiescent_reactivation_steps` definition), EMA threshold-crossing times and active-duty changes |
| I9 | B3 must satisfy G_D\|B+R > 0 **and** G_R\|B+D > 0 under **both** (a) the historical instrument (seed-mean terminal EMA) and (b) an **α-invariant instrument**: the seed-mean of raw per-event conditional gains over steps 3001..6000. Reason: the historical gate reads the EMA that B3 changes (PA-06). Adding (b) is a change from the parent rule and needs human approval |
| I11–I14 | *`PROTOCOL_TEXT_MISSING — PARENT RULE CARRIED FORWARD`*: mean switching recovery latency (existing runner definition: first 100-step rolling post-change MSE ≤ 0.15·Var(y[3000:]), censored at 3000), **B3 − B0 ≤ +50 stream steps** for each task |
| I10 / Gate 6 | Report only. Gate 6 stays historically `FAIL` and is not re-evaluated as a repair target |
| I2 | Report the false-temporal-wake sentinel descriptively (promotions on I2), because B3's noisier EMA could raise spurious wakes |

## 10. Outcome interpretation (fixed before data)

| P-M (B3 < B2) | P-A (NI vs B0) | Resource ≤ 100 | Guardrails | Label |
|---|---|---|---|---|
| any | pass | pass | all pass | `LOCAL_RESOURCE_COMPLIANT_CANDIDATE`, local to this benchmark only: not globally validated, M3 not opened, no novelty or energy claim |
| supported | fail, or a guardrail fails | — | — | `E3_CAUSALLY_CONTRIBUTES_INSUFFICIENT_ALONE`, with the residual attributed to E1 + E2 jointly |
| not supported, point estimate < 0 | — | — | — | `E3_RESCUE_UNDETECTED_AT_N30` (not "refuted") |
| not supported, point estimate ≥ 0 | — | — | — | `E3_RESCUE_NOT_SUPPORTED`. Check threshold-noise churn (§8 H8, I2) |
| — | — | fail | — | `RESOURCE_FAIL`. Classify per H8 |

If B3 passes P-A while P-M is not supported, the candidate label stands, but no mechanism claim is made.

## 11. Explicitly out of scope

Separating E1 from E2 would need a further mechanistic arm, for example gains accumulated every 5 steps with decisions every 10. That arm is not
resource-compliant as a candidate and is **not** part of this four-arm design. It is a possible later stage. Event-triggered
arbitration, hysteresis, early rejection, search changes and any α sweep are also out of scope.
