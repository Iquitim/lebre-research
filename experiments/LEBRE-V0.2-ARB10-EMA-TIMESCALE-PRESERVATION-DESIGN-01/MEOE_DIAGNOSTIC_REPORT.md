# Phase D — Existing-Trace Deterministic MEOE Diagnostic

**New stochastic trajectories:** none. The only input is the sealed `trans_windows_cache.json` (parent, SHA-256 in `PARENT_HASHES.txt`).

## D2. Telemetry availability

| Requirement | Available? |
|---|---|
| Raw per-event gains | **No.** Only post-update EMA values were logged. |
| `G_D|B`, `G_R|B` EMA trajectories | Yes, for **seed 1971 only**, tasks **I11–I14 only**, loop indices 2900..3299 (`step_count` 2901..3300) |
| `G_D|B+R`, `G_R|B+D` trajectories | **No** |
| Tasks I7, I9, I10 | **No** |
| STARTUP, QUIESCENCE, POST_QUIESCENCE_REACTIVATION windows | **No** (the window covers only ±~300 steps around the t = 3000 changepoint) |

**Gain recovery.** In the K5 arms (A0, A1) the arbitration EMA is updated only when `step_count % 5 == 0`, as
`E_n = 0.98 E_{n−1} + 0.02 g_n`. That makes the raw gain exactly recoverable: `g_n = (E_n − 0.98 E_{n−1}) / 0.02`.
I checked the index alignment (`step_count = loop index + 1`, since `live_step` increments first) against the data: on every
one of the 16 trajectories, the EMA is **held exactly** between events (`MEOE_TELEMETRY_INTEGRITY.csv`).

**Classification:**
`MEOE_DIAGNOSTIC = PARTIAL_FROM_EXISTING_TELEMETRY` (2 of 4 gains, 4 of 14 tasks, 1 seed, 40 blocks per trajectory, 320 blocks in total).

Caveat: A0 and A1 share the seed and much of the trajectory. For example, `G_D|B` on I11 and I13 is identical in A0 and A1.
The two arms are **not** independent replicates.

## D3–D4. MEOE = 0.0196 (g10 − g5)

Full per-block values: `MEOE_BLOCK_LEVEL.csv`. Mean, median, SD, P90, P95, P99 and max by task, arm, gain and window: `MEOE_BY_TASK_AND_WINDOW.csv`.

Magnitude relative to the executable decision thresholds (θ_tol = 0.015, eviction levels 0.005 / 0.008), for |MEOE| over the whole window, arm A1:

| Task | gain | mean | P95 | max |
|---|---|---|---|---|
| I11 | G_D\|B | 0.0174 | 0.0742 | 0.0764 |
| I12 | G_D\|B | 0.0062 | 0.0147 | 0.0176 |
| I12 | G_R\|B | 0.0087 | 0.0268 | 0.0421 |
| I14 | G_R\|B | 0.0145 | 0.0465 | 0.1069 |

The per-block sparse-evidence perturbation is often **of the same order as, or larger than, the decision
thresholds themselves**. The reason is that `g` is a single-step squared-error difference, which is very noisy. E2 is
therefore not negligible a priori.

## D5. By window (the only stratification possible)

Windows: `PRE_TRANSITION_STEADY` (blocks ending 2910..3000), `POST_TRANSITION_EARLY_0_100`, `POST_TRANSITION_LATE_100_300`.
STARTUP, QUIESCENCE and POST_QUIESCENCE_REACTIVATION: `UNAVAILABLE_FROM_EXISTING_TELEMETRY`.

## D7. Changepoint risk (decision rule fixed in the script header before first execution)

`R = mean|MEOE_max|(first 100 post-change steps) / mean|MEOE_max|(100 pre-change steps)`

| Task | Arm | R | ≥ 2.0 |
|---|---|---|---|
| I11 | A0 | 1.952 | no |
| I11 | A1 | 1.953 | no |
| I12 | A0 | 2.105 | yes |
| I12 | A1 | 1.958 | no |

**`SPARSE_EVIDENCE_CHANGEPOINT_RISK = MIXED (not established)`** under the pre-declared rule.
Descriptively, the mismatch magnitude roughly doubles right after the changepoint in every cell (R ≈ 1.95–2.11), which sits right at the pre-declared threshold.
That pattern is consistent with a changepoint-concentrated risk. It rests on one seed and 10 blocks per window, so it is only a flag for the confirmatory telemetry to check, not a finding.

## Supplementary: open-loop filter replay (not a counterfactual)

`OPEN_LOOP_FILTER_REPLAY.csv` passes the frozen K5 gain sequence through a B2 filter (α = .02 on 10-step endpoints) and a
B3 filter (α = .0396 on 10-step endpoints), both starting from the K5 EMA state. It then compares each filter against the actual K5 EMA.
Structure is held fixed, so this isolates the filter only. Per D8 it says nothing about B3's closed-loop behavior.

| Metric (16 trajectories) | B2 filter | B3 filter |
|---|---|---|
| threshold-side disagreements with K5 (θ_tol and eviction level, 1248 comparisons) | 130 | **97** |
| trajectories where B3's mean \|deviation\| < B2's | — | 9 / 16 |
| median B3/B2 mean-\|deviation\| ratio | — | 0.94 |

Over these 400-step windows, pole restoration reduces decision-side disagreement with the K5 supervisor by
about a quarter. It does **not** uniformly reduce trajectory deviation. On I11 `G_D|B` (both arms) and on I14 in some cells,
B3 deviates **more** than B2, which is the noise-inflation face of midpoint-evidence omission. B2's lag
disadvantage grows with window length, so a 400-step window probably understates the gap in B3's favor. This
diagnostic cannot size that effect.

## D8. Scope

None of these computations predicts B3's NMSE, switching latency or resource use. Once B3's structural
decisions differ, its gain sequence differs as well. The diagnostic motivates the experiment. It does not substitute for one,
and it did not feed back into α. α = 0.0396 is fixed analytically, and no sweep or selection happened.
