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

## Earlier lines (v0.3–v0.51), for collision avoidance

These ranges were used in earlier lines: 2176–2265, 2401–2430, 2501–2530, 2561–2590 and 7301–7613. See the corresponding `experiments/LEBRE-V0.4*`, `LEBRE-V0.46*` and `LEBRE-V0.51*` folders.
