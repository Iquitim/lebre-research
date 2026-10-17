# lebre-research — research record of the LEBRE online forecaster

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23049102.svg)](https://doi.org/10.5281/zenodo.23049102)

This repository answers one question: **how were the LEBRE results obtained?** It holds the complete research record: implementations, experiment scripts, pre-registrations, results, frozen versions with SHA-256 manifests, documents and the tools needed to re-run them.

> **LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*) is an online, one-step-ahead forecaster for time series with inputs, at a fixed cost per step. Its structural core accepts each structural change by an anytime-valid sequential test (e-process) of predictive improvement — removals included — against the forecast each unit can improve (external inputs against the core forecast, which already contains the target's own past); layer M1 adds a precision expert that sleeps while it carries no weight, and layer M2 starts the forecast from a declared trivial reference.
>
> The current state is **LEBRE v0.55**, **promoted** on 2026-10-17 by a pre-registered binding rule in a single evaluation on a new reserve of 84 series (no family worse than v0.54 beyond the margin, ratios 0.993 to 1.008; placebo random-walk inputs in the final structure on 0 of 84 series, against 4 for v0.54; median per-series cost 0.989 of v0.54's). It has declared scope limits (a small significant loss on basins, where a recursive-least-squares ARX of the same cost class is better): see `docs/architecture/LEBRE_v0.55_FREEZE_RECORD.md`. Its self-contained specification and technical report is `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_{EN,PTBR}.pdf`. The previous version, v0.54 (promoted 2026-10-13), remains frozen.

The installable library [`lebre`](https://github.com/Iquitim/lebre) (0.3.0 implements v0.54; 0.2.0, v0.53; 0.1.0, v0.52-r1) and the paper (`paper/`, which describes v0.52) point back to this repository. Development and validations of v0.53, v0.54 and v0.55 were run in the public [LEBRE Lab](https://github.com/Iquitim/lebre-lab).

## Where to start

| You want to… | Go to |
|---|---|
| Read what LEBRE v0.55 is and how it was evaluated | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_EN.pdf` (PT-BR: `…_v0.55_SPEC_PTBR.pdf`) |
| Read the earlier, frozen v0.52 (the structural core) | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_EN.pdf` (PT-BR: `…_r1_PTBR.pdf`) |
| Read the paper (English, arXiv format; describes v0.52) | `paper/main.pdf` (source and build in `paper/`) |
| Know how each reported number was produced | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| Browse the experiment folders | [`experiments/INDEX.md`](experiments/INDEX.md) |
| See every random seed and data split used | [`docs/research/SEEDS.md`](docs/research/SEEDS.md) |
| Get the canonical model configuration | v0.55: [`configs/lebre_v055_canonical.json`](configs/lebre_v055_canonical.json); v0.54: [`configs/lebre_v054_canonical.json`](configs/lebre_v054_canonical.json); v0.53: [`configs/lebre_v053_canonical.json`](configs/lebre_v053_canonical.json); v0.52: [`configs/lebre_v052_canonical.json`](configs/lebre_v052_canonical.json) |
| Set up the environment and toolchains | [`environment/`](environment/), [`tools/README.md`](tools/README.md), [`data/README.md`](data/README.md) |
| Check integrity of the frozen versions | `python scripts/verify_integrity.py` |
| Check that results still regenerate | `python scripts/reproduce_smoke.py` |
| Check the library (0.1.0, the core) against published predictions | `python scripts/check_lebre_package.py` |
| Use the installable library | `pip install lebre` (0.2.0 = v0.53; [repository](https://github.com/Iquitim/lebre), [doi:10.5281/zenodo.23073983](https://doi.org/10.5281/zenodo.23073983)) |

## Repository layout

The physical layout is **historical and intentionally preserved**:
- frozen versions are verified by SHA-256 manifests that record relative paths;
- experiment scripts import each other through relative paths.

Moving files would break both. Organisation is therefore provided by the indexes above rather than by relocation.

| Path | Content |
|---|---|
| `experiments/<STAGE-ID>/` | One folder per experiment or stage (103). Each has its scripts, pre-registration (when applicable), logs, result tables and a report. The v0.52 line is `LEBRE-V0.52-*` and `PRA-0[45]`; the v0.53 line is `LEBRE-V0.53-*` (prototype, design notes and literature audits PRA-06 to PRA-10, reserve, final evaluation); the v0.54 line is `LEBRE-V0.54-*` (prototype, design notes and literature audit PRA-11, reserve, final evaluation, stress audit); the v0.55 line is `LEBRE-V0.55-*` (research programme, design note and formal note F1, prototype, validation, reserve, final evaluation, external comparison). |
| `experiments/LEBRE-V0.55-PROTO-01/` | **Python implementation of v0.55**, frozen at commit `b0522a0`, variant `B10` (`lebre055/`: v0.54 copied byte for byte from `f9906c4`; the anchored core in `anchored.py`, variants in `model055.py`), with its tests. Frozen. |
| `experiments/LEBRE-V0.55-FINAL-01/` | Pre-registered final evaluation of v0.55, with placebo inputs as a negative control. |
| `experiments/LEBRE-V0.55-COMP-01/` | Comparison with 12 external models (reference only). |
| `experiments/LEBRE-V0.54-PROTO-01/` | **Python implementation of v0.54**, frozen at commit `f9906c4` (promoted code `cfe72ce` + errata 01; `lebre054/`: the v0.53 files are byte-for-byte copies of `lebre==0.2.0`; M5a in `dormancy.py`, M5b in `screening.py`, M4 in `removal.py`; `cycle.py` is present and off), with its tests. Frozen. |
| `experiments/LEBRE-V0.54-FINAL-01/` | Pre-registered final evaluation of v0.54 (pre-registration, scripts, rehearsal, run notes, results, errata 01). |
| `experiments/LEBRE-V0.54-AUDIT-01/` | Post-promotion stress audit of v0.54 (plan, scripts, report). |
| `experiments/LEBRE-V0.53-PROTO-01/` | **Python implementation of v0.53**, promoted at commit `4a2620e` (`lebre053/`: the core files are byte-for-byte copies of `lebre==0.1.0`; M1 in `precisao.py`, M2 in `agregacao.py` and `model053.py`), with its tests. Frozen. |
| `experiments/LEBRE-V0.53-FINAL-01/` | Pre-registered final evaluation of v0.53 (pre-registration, scripts, run notes, results, per-series predictions). |
| `experiments/LEBRE-V0.52-PROTO-01/` | **Python reference implementation** of v0.52 (`lebre_v052h.py`, `change_engine.py`, `lebre_v052.py`), plus data loader, comparators and development log. Frozen. |
| `experiments/LEBRE-V0.52-EXT-01/lebre_c/` | **C99 port of the core** (float64/float32) and its host build. `mcu/` holds the Cortex-M4F firmware and the Renode simulation scripts. M1 and M2 have no C port. |
| `docs/research/` | Seed registry and the manifest of artifacts kept out of git. |
| `docs/architecture/` | Specifications (v0.1, v0.3.2, v0.51, v0.52 and its r1, v0.53 and its self-contained r1, v0.54, v0.55), freeze records, SHA-256 manifests, release notes, PDF builders (`pdf_source/`). |
| `configs/` | Canonical configurations of v0.52, v0.53, v0.54 and v0.55, machine-readable. |
| `paper/` | The preprint (LaTeX), with its asset generator and arXiv package. |
| `packages/lebre/` | Snapshot of the installable library `lebre` 0.1.0 (implements v0.52-r1; bit for bit in the reference environment). The library is developed at https://github.com/Iquitim/lebre, where 0.3.0 implements v0.54. |
| `scripts/` | Repository-level tools: integrity check, smoke reproduction, artifact manifest. |
| `data/` | Loaders and checksum lists of the public datasets. Raw data are **not** in git (see `data/README.md`). |
| `src/`, `tests/`, `docs/history/phase-v0.1/` | Early-phase code and documents (v0.1 era), kept as the historical record. |
| `scratch/` | Helper scripts imported by some builders and analyses (tracked). QA renders are ignored. |

## What is not in git

The following are listed with size and SHA-256 in [`docs/research/ARTIFACTS_MANIFEST.tsv`](docs/research/ARTIFACTS_MANIFEST.tsv):
- raw datasets;
- per-series prediction arrays (`*.npz`);
- toolchain archives;
- firmware and build binaries;
- four very large early event logs.

In total, 802 files and about 3 GB. The experiment outputs are published as a separate archive, [doi:10.5281/zenodo.23082357](https://doi.org/10.5281/zenodo.23082357) (eight zip parts `lebre-research-v0.52-r1-artifacts-part*.zip`, built by `scripts/make_artifact_archive.py`; contents in [`docs/research/ARCHIVE_CONTENTS.tsv`](docs/research/ARCHIVE_CONTENTS.tsv)). Raw data are downloaded from the original publishers, and toolchains are installed as in `environment/TOOLCHAIN.md`. See [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md), section 0.

## Status and honesty notes

**v0.55** (freeze record, §5; specification, §22):

- One-step forecasting. On basins, a small significant loss against v0.54 (1.008, 95% CI 1.003–1.014, within the 1.02 margin), and an ARX with recursive least squares of the same cost class errs 11% to 13% less (external comparison, reference only).
- The gain of carrying a true input's information to the forecast on integrated series was shown on synthetic data only; on the real ECB level series it did not appear (1.000).
- Weak real relations are registered as structure more slowly (fewer series end with an external input).
- The formal note F1 (validity under any predictable learner) has a single author and was not independently reviewed; its erratum 01 records that the v0.54 test scale was not strictly predictable. The joint bound on structural changes is 2α (two engines); structural false-change control remains empirical.
- Memory and cost are estimated by the analytical model, not measured on a microcontroller. No component is original.

**v0.54** (freeze record, §5; specification, §22):

- One-step forecasting. v0.54 keeps v0.53's accuracy (0.989 to 1.000 per family) and costs less where M1 carries no weight; where M1 helps (basins) the cost is the same. The 30% cost cut cited as an example in the design note was not reached.
- A relation that disappears for more than ~5,200 steps and returns is removed and must be re-detected: +5% to +10% error on series with that pattern (declared in errata 01, not fixed).
- Spurious inputs in level series are still accepted (M3 left for v0.55); the cycle must still be declared (M6 left out).
- The cheap equivalence report raised the per-step peak cost with many inputs in the promoted code; errata 01 fixed it with identical forecasts.
- The event log grows without bound (already in v0.53). No component is original.

**v0.53** (freeze record, §5; specification, §22):

- One-step forecasting. The gain came from basins and FX; in solar, wind and load v0.53 is identical to v0.52.
- It costs more than v0.52 on every series: in the final evaluation, +476 operations per step at the median (maximum +918, within the pre-registered ceiling of 1,100), a median total of 919, about twice v0.52.
- Evidence of the accuracy × cost frontier (F6) on new data comes from one validation; the memory figure (~83 KB) is an estimate.
- No formal error guarantee in the original scale for M1 and M2; the shock addenda of the evaluation ruler were decided during development.
- Development and validations were run in the LEBRE Lab (https://github.com/Iquitim/lebre-lab). No component is original.

**v0.52-r1** (the structural core):

- Results cover two domains (hydrology, buildings) with 1–5 inputs and one-step forecasting.
- The declared cost contract was **not met** (+3.7% mean, +2.0% peak).
- The microcontroller results come from a **simulator**.
- The testing mechanism did **not** improve accuracy over an "all inputs on" ablation.
- The core mechanism is **not original**.

See §19 of the v0.52 specification for the full list.

## Licence

- **Code:** Apache-2.0 (`LICENSE`).
- **Documents, reports, figures and result tables:** CC-BY-4.0 (`LICENSE-CC-BY-4.0.txt`).
- **Exclusions:** third-party data keep their own licences; the logo is excluded from both licences.

Details are in `NOTICE`.

## Citation

Lima, S. (2026). *LEBRE research record — v0.55* [Software]. Zenodo. https://doi.org/10.5281/zenodo.23443154

- `10.5281/zenodo.23443154`: version v0.55 (promoted).
- `10.5281/zenodo.23376152`: version v0.54 (promoted, with errata 01).
- `10.5281/zenodo.23282527`: version v0.53 (promoted).
- `10.5281/zenodo.23049103`: version v0.52-r1.
- `10.5281/zenodo.23049102`: all versions; resolves to the latest.

Experiment artifacts (dataset): Lima, S. (2026). *LEBRE research record v0.52-r1: experiment artifacts* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23082357

See also `CITATION.cff`.

---

*Documentação em português: [`README.pt-BR.md`](README.pt-BR.md). Most internal experiment logs are written in Portuguese.*
