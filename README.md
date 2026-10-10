# lebre-research — research record of the LEBRE online forecaster

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23049102.svg)](https://doi.org/10.5281/zenodo.23049102)

This repository answers one question: **how were the LEBRE results obtained?** It holds the complete research record: implementations, experiment scripts, pre-registrations, results, frozen versions with SHA-256 manifests, documents and the tools needed to re-run them.

> **LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*) is an online, one-step-ahead forecaster for time series with inputs, at a fixed cost per step. Its structural core accepts each structural change by an anytime-valid sequential test (e-process) of predictive improvement; layer M1 adds a precision expert, and layer M2 starts the forecast from a declared trivial reference.
>
> The current state is **LEBRE v0.53**, **promoted** on 2026-10-09 by a pre-registered binding rule in a single evaluation on data reserved before any v0.53 code (no harm in any family; v0.53/v0.52 = 0.955, 95% CI 0.951–0.960, on 104 reserved series). It has declared scope limits: see `docs/architecture/LEBRE_v0.53_FREEZE_RECORD.md`. Its self-contained specification and technical report (structural core + M1 + M2) is `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_{EN,PTBR}.pdf`.

The installable library [`lebre`](https://github.com/Iquitim/lebre) (0.2.0 implements v0.53; 0.1.0 implements v0.52-r1) and the paper (`paper/`, which describes v0.52) point back to this repository. Development and validations of M1 and M2 were run in the public [LEBRE Lab](https://github.com/Iquitim/lebre-lab).

## Where to start

| You want to… | Go to |
|---|---|
| Read what LEBRE v0.53 is and how it was evaluated | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_EN.pdf` (PT-BR: `…_v0.53_SPEC_r1_PTBR.pdf`) |
| Read the earlier, frozen v0.52 (the structural core) | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_EN.pdf` (PT-BR: `…_r1_PTBR.pdf`) |
| Read the paper (English, arXiv format; describes v0.52) | `paper/main.pdf` (source and build in `paper/`) |
| Know how each reported number was produced | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| Browse the experiment folders | [`experiments/INDEX.md`](experiments/INDEX.md) |
| See every random seed and data split used | [`docs/research/SEEDS.md`](docs/research/SEEDS.md) |
| Get the canonical model configuration | v0.53: [`configs/lebre_v053_canonical.json`](configs/lebre_v053_canonical.json); v0.52: [`configs/lebre_v052_canonical.json`](configs/lebre_v052_canonical.json) |
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
| `experiments/<STAGE-ID>/` | One folder per experiment or stage (86). Each has its scripts, pre-registration (when applicable), logs, result tables and a report. The v0.52 line is `LEBRE-V0.52-*` and `PRA-0[45]`; the v0.53 line is `LEBRE-V0.53-*` (prototype, design notes and literature audits PRA-06 to PRA-10, reserve, final evaluation). |
| `experiments/LEBRE-V0.53-PROTO-01/` | **Python implementation of v0.53**, promoted at commit `4a2620e` (`lebre053/`: the core files are byte-for-byte copies of `lebre==0.1.0`; M1 in `precisao.py`, M2 in `agregacao.py` and `model053.py`), with its tests. Frozen. |
| `experiments/LEBRE-V0.53-FINAL-01/` | Pre-registered final evaluation of v0.53 (pre-registration, scripts, run notes, results, per-series predictions). |
| `experiments/LEBRE-V0.52-PROTO-01/` | **Python reference implementation** of v0.52 (`lebre_v052h.py`, `change_engine.py`, `lebre_v052.py`), plus data loader, comparators and development log. Frozen. |
| `experiments/LEBRE-V0.52-EXT-01/lebre_c/` | **C99 port of the core** (float64/float32) and its host build. `mcu/` holds the Cortex-M4F firmware and the Renode simulation scripts. M1 and M2 have no C port. |
| `docs/research/` | Seed registry and the manifest of artifacts kept out of git. |
| `docs/architecture/` | Specifications (v0.1, v0.3.2, v0.51, v0.52 and its r1, v0.53 and its self-contained r1), freeze records, SHA-256 manifests, release notes, PDF builders (`pdf_source/`). |
| `configs/` | Canonical configurations of v0.52 and v0.53, machine-readable. |
| `paper/` | The preprint (LaTeX), with its asset generator and arXiv package. |
| `packages/lebre/` | Snapshot of the installable library `lebre` 0.1.0 (implements v0.52-r1; bit for bit in the reference environment). The library is developed at https://github.com/Iquitim/lebre, where 0.2.0 implements v0.53. |
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

Lima, S. (2026). *LEBRE research record — v0.53* [Software]. Zenodo. https://doi.org/10.5281/zenodo.23282527

- `10.5281/zenodo.23282527`: version v0.53 (promoted).
- `10.5281/zenodo.23049103`: version v0.52-r1.
- `10.5281/zenodo.23049102`: all versions; resolves to the latest.

Experiment artifacts (dataset): Lima, S. (2026). *LEBRE research record v0.52-r1: experiment artifacts* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23082357

See also `CITATION.cff`.

---

*Documentação em português: [`README.pt-BR.md`](README.pt-BR.md). Most internal experiment logs are written in Portuguese.*
