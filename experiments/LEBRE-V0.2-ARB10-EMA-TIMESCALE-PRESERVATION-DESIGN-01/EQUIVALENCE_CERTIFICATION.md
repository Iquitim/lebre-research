# Phases B & C — Equivalence Certification

Source computations: `POLE_EQUIVALENCE_VERIFICATION.csv`, `EMA_OPERATING_POINT_COMPARISON.csv`,
`TEN_STEP_MISMATCH_DERIVATION.md`, all produced by `generate_ema_timescale_design.py` in IEEE-754 double precision, with SymPy for the symbolic steps.

## Verified values

| Quantity | K5, α=.02 (B0/B1) | K10, α=.02 (B2) | K10, α=.0396 (B3) |
|---|---|---|---|
| q (per event) | 0.980000 | 0.980000 | 0.960400 |
| q per stream step | 0.995967611 | 0.997981769 | **0.995967611** |
| τ events | 49.498316 | 49.498316 | 24.749158 |
| τ stream steps | 247.491582 | 494.983165 | **247.491582** |
| half-life events | 34.309618 | 34.309618 | 17.154809 |
| half-life stream steps | 171.548092 | 343.096185 | **171.548092** |
| weight centre-of-mass age (stream steps) | 245.00 | 490.00 | 242.53 |
| effective gain samples (iid) | 99.0 | 99.0 | **49.5** |
| stationary EMA variance factor (iid) | 0.010101 | 0.010101 | **0.020200** |

`|τ_stream(B3) − τ_stream(K5)|` and `|half-life_stream(B3) − half-life_stream(K5)|` are below 1e-9, which is machine-level.
The computed α10 is `0.03960000000000008` in floating point. The preregistration pins the **literals**
`q = 0.9604`, `α = 0.0396` (`1 − 0.0396 == 0.9604` exactly in binary64).

## B7. Certified equivalent

- `STREAM_TIME_HOMOGENEOUS_POLE = EQUIVALENT`
- `STREAM_TIME_HALF_LIFE = EQUIVALENT`
- Steady-state mean under constant gain: equivalent (both unbiased, unit DC gain).

## B8. Certified not equivalent

- `EVENT_UPDATE_FREQUENCY = NOT_EQUIVALENT` (1 per 10 steps vs 1 per 5)
- `GAIN_OBSERVATION_FREQUENCY = NOT_EQUIVALENT`
- `DECISION_OPPORTUNITY_FREQUENCY = NOT_EQUIVALENT` (maximum scheduler wait is 9 vs 4 steps, unchanged by α)
- `INTERMEDIATE_EMA_TRAJECTORY = NOT_GENERALLY_EQUIVALENT` (B3 has no state at t+5; endpoints agree only if g5 = g10)
- `FULL_SUPERVISOR_STATE = NOT_EQUIVALENT`
- **Additional: `EMA_NOISE_LEVEL = NOT_EQUIVALENT`.** Under serially uncorrelated gains, B3's stationary EMA variance is
  ~2.0× K5's (SD ~1.41×), because it averages half as many samples over the same memory. B3 therefore restores the
  **lag** of the K5 supervisor but not its **noise level**. B2 kept the noise level and doubled the lag.

## C. Ten-step mismatch

Verified symbolically:
`E_K10_PP − E_K5 = α q (g10 − g5) = 0.0196 (g10 − g5)`. The difference is zero iff `g10 = g5`, and α10 = α(1+q).
Maximum numeric residual on fixed spot-check inputs: 2.1e-17.

Binding interpretation: B3 is endpoint-equivalent to K5 over a ten-step block only under constant gain within the
block. The residual is a sparse-evidence mismatch (midpoint-evidence omission, E2). It is **not** aliasing, because no
spectral analysis of the gain signal has been performed.
