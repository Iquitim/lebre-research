# Seed and split registry

Rule followed throughout: every measurement set is declared (seeds included) **before** it is run, and a seed range is never reused for a different measurement.

**Before choosing new seeds, check this table and search the repository** (`grep -rn "<seed>" experiments`).

## Data splits (v0.52 line)

| Seeds | Use | Where |
|---|---|---|
| 5201 / 5202 / 5203 | Seeded permutations for ONS / CAMELS-BR / BDG2 in the development + held-out split | `experiments/LEBRE-V0.52-DATA-01/make_split_v052.py` |
| (same permutations) | **Reserve 1** = held-out of `SPLIT_V052.json` (ONS 45, CAMELS-BR 50 [positions 10–59], BDG2 30 [positions 5–34]) — **consumed** | `LEBRE-V0.52-HELDOUT-01` |
| (same permutations) | **Reserve 2** = CAMELS-BR positions 60–79, BDG2 35–54 — **consumed** | `LEBRE-V0.52-HELDOUT-02/select_reserve2.py` |
| (same permutations) | **Reserve 3** = CAMELS-BR positions 80–109, BDG2 55–84 — **consumed** | `LEBRE-V0.52-HELDOUT-03/select_reserve3.py` |
| (same permutations) | **v0.53 final reserve** = CAMELS-BR positions 110–139, BDG2 85–114 — **consumed** by the final evaluation of 2026-10-09 | `experiments/LEBRE-V0.53-DATA-01/make_split_v053.py` |
| 5311 / 5312 | Draw of 8 solar / 8 wind ONS plants for the **v0.53 final reserve** (excluding the 12 plants used in the LEBRE Lab) | same |
| (same permutations) | **v0.54 final reserve** = CAMELS-BR positions 140–169, BDG2 115–144 | `experiments/LEBRE-V0.54-DATA-01/make_split_v054.py` |
| 5421 / 5422 | Draw of 8 wind ONS plants (2024–2025, excluding the 36 used in the LEBRE Lab and the 8 of the v0.53 reserve) / 8 solar ONS plants (Jan–Sep 2026, time split) for the **v0.54 final reserve** | same |
| — | **Still unused:** CAMELS-BR positions 170+, BDG2 positions 145+; 40 eligible wind plants of 2024–2025. Eligible ONS rivers and solar plants of 2024–2025 are exhausted. | — |

## v0.52 development and checks

| Seeds | Use |
|---|---|
| 6101–6103, 9101–9103 | Tuning sets (semi-synthetic SS0–SS4; pure synthetic) |
| 6201–6203, 9201–9203 | Measurement #2 (hierarchical version) |
| 6301–6303, 9301–9303 | Measurement #3 |
| 6401–6403, 9401–9403 | Measurement #4 |
| 6501–6503, 9501–9503 | Measurement #5 |
| 6601–6603, 9601–9603; nulls 6701–6730 | Measurement #6 |
| 6801–6803, 9701–9703; nulls 6901–6930 | Measurement #7 |
| 7001–7040 | Development null batches |
| 7101–7199 | Development replicas for smooth inputs |
| 7201–7240 (×3 values of μ) | Misadjustment verification (EXT-01) |
| 20260927 | E-process simulation (`PROTO-01/sim_evidence.py`) |
| 5290 | Illustrative synthetic example in the spec (`DOC-01/doc_examples.py`) |
| 8201 + 1000·scenario + 100·persistence + k (k < 50), i.e. within 8201–14250 | False-change simulation (`EXT-02/fdr_sim.py`) |

## Analysis seeds (bootstrap)

| Seed | Use |
|---|---|
| 8001 | Reserve 1 analysis |
| 8002 | Reserve 2 analysis |
| 8003 | Reserve 3 analysis; EXT-02 summaries; spec builder paired statistics |

## v0.53 line (LEBRE Lab and final evaluation)

| Seeds | Use | Where |
|---|---|---|
| 20261007–20261052 | Bootstrap and classification seeds of the v0.53 development measurements, validations 1 to 5 and diagnostics, each declared in the plan of its measurement | LEBRE Lab, [github.com/Iquitim/lebre-lab](https://github.com/Iquitim/lebre-lab) (`analises/*_PLANO.md`, `diagnosticos/*_PLANO.md`) |
| 20261053 / 20261054 | Classification / measurement bootstrap of the v0.53 final evaluation | `experiments/LEBRE-V0.53-FINAL-01/final_analise.py` |

## v0.54 line (LEBRE Lab, final evaluation, audit and errata)

| Seeds | Use | Where |
|---|---|---|
| 5600–5609 | Prototype tests of M5a and exploration for M5b (no registered measurement) | `experiments/LEBRE-V0.54-PROTO-01/tests/`, M5b spec |
| 20261060–20261249 | Bootstrap seeds, scenario seeds and validation-6 synthetic seeds of the M5a measurements, each declared in its plan | LEBRE Lab (`analises/M5A_*_PLANO.md`, `VALIDACAO6_PLANO.md`) |
| 20261300–20261343 | Prototype tests of M5b, M4 and M6 (20261300–04), explorations without registered measurement (20261310–39), bootstrap of M4_E1, M6_E1, M4_E2, M6_E2 (20261340–43) | prototype tests; specs; LEBRE Lab plans |
| 2026101200–2026101293 | Validation 7 synthetic families (…200–…289) and bootstrap (…290); v0.54 final evaluation classification / measurement / cost bootstrap (…291 / …292 / …293) | LEBRE Lab `VALIDACAO7_PLANO.md`; `experiments/LEBRE-V0.54-FINAL-01/final_analise.py` |
| 2026101300–2026101469 | Stress audit series streams `default_rng([2026101300, test, type, k])` and bootstrap (…301); errata 01 checks (`[2026101400, …]`) and second errata measurement (…410–…469) | `experiments/LEBRE-V0.54-AUDIT-01/`; LEBRE Lab `ERRATA01_V054_E2_PLANO.md` |

## v0.55 line (LEBRE Lab, validation, final evaluation and comparison)

| Seeds | Use | Where |
|---|---|---|
| 5202 / 5203 | v0.52 permutations of CAMELS-BR / BDG2, reused: positions 170–189 / 145–174 (validation) and 190–219 / 175–204 (final reserve) | `experiments/LEBRE-V0.55-DATA-01/`, `LEBRE-V0.55-DATA-02/` |
| 5521 / 5522 | Draw of the 8 wind / 8 solar ONS plants of the v0.55 reserve | `experiments/LEBRE-V0.55-DATA-02/make_split_v055.py` |
| 2026101590–2026101920 | Development rounds D1 to D4: series streams, bootstrap and rehearsal seeds, each declared in its plan (range 2026101500–2026102999 checked as unused on 16 Oct 2026) | LEBRE Lab `analises/D1_V055_PLANO.md` to `D4_V055_PLANO.md` |
| 2026101950–2026102130 | Fixed bench: round D5 (2026102000–2026102022, 2026101950, 2026102030) and confirmation C1 (2026102100–2026102122, 2026102070, 2026102130) | LEBRE Lab `analises/BANCO_V055_PLANO.md` |
| 2026102210 | Bootstrap of the real validation | `experiments/LEBRE-V0.55-VAL-01/val_analise.py` |
| 2026102500 | Placebo random-walk inputs of the final evaluation, `[2026102500, family, series]` | `experiments/LEBRE-V0.55-FINAL-01/final_run.py` |
| 2026102600 | Bootstrap of the final evaluation | `experiments/LEBRE-V0.55-FINAL-01/final_analise.py` |
| 2026102700 | Bootstrap of the external comparison (TTM fine-tuning uses seed 0) | `experiments/LEBRE-V0.55-COMP-01/comp_analise.py`, `ttm_gpu.py` |

## Earlier lines (v0.3–v0.51), for collision avoidance

These ranges were used in earlier lines: 2176–2265, 2401–2430, 2501–2530, 2561–2590 and 7301–7613. See the corresponding `experiments/LEBRE-V0.4*`, `LEBRE-V0.46*` and `LEBRE-V0.51*` folders.
