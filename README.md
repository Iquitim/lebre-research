# lebre-research — research record of the LEBRE online forecaster

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23049102.svg)](https://doi.org/10.5281/zenodo.23049102)

This repository answers one question: **how were the LEBRE results obtained?** It holds the complete research record: implementations, experiment scripts, pre-registrations, results, frozen versions with SHA-256 manifests, documents and the tools needed to re-run them.

> **LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*) is an online, one-step-ahead forecaster for time series with inputs. It runs within a budget of a few hundred floating-point operations per step. Each structural change is accepted by an anytime-valid sequential test (e-process) of predictive improvement.
>
> The current documented state is **LEBRE v0.52, specification revision 1 ("v0.52-r1")**. It is a frozen research version, **not promoted**, with declared scope limits.

A reusable library (`lebre`) and a paper are separate, later deliverables. They will point back to this repository.

## Where to start

| You want to… | Go to |
|---|---|
| Read what LEBRE v0.52 is and what was measured | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_EN.pdf` (PT-BR: `…_r1_PTBR.pdf`) |
| Know how each reported number was produced | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) |
| Browse the experiment folders | [`experiments/INDEX.md`](experiments/INDEX.md) |
| See every random seed and data split used | [`docs/research/SEEDS.md`](docs/research/SEEDS.md) |
| Get the canonical model configuration | [`configs/lebre_v052_canonical.json`](configs/lebre_v052_canonical.json) |
| Set up the environment and toolchains | [`environment/`](environment/), [`tools/README.md`](tools/README.md), [`data/README.md`](data/README.md) |
| Check integrity of the frozen versions | `python scripts/verify_integrity.py` |
| Check that results still regenerate | `python scripts/reproduce_smoke.py` |
| Check the library against published predictions | `python scripts/check_lebre_package.py` |

## Repository layout

The physical layout is **historical and intentionally preserved**:
- frozen versions are verified by SHA-256 manifests that record relative paths;
- experiment scripts import each other through relative paths.

Moving files would break both. Organisation is therefore provided by the indexes above rather than by relocation.

| Path | Content |
|---|---|
| `experiments/<STAGE-ID>/` | One folder per experiment or stage (86). Each has its scripts, pre-registration (when applicable), logs, result tables and a report. The v0.52 line is `LEBRE-V0.52-*` and `PRA-0[45]`. |
| `experiments/LEBRE-V0.52-PROTO-01/` | **Python reference implementation** of v0.52 (`lebre_v052h.py`, `change_engine.py`, `lebre_v052.py`), plus data loader, comparators and development log. Frozen. |
| `experiments/LEBRE-V0.52-EXT-01/lebre_c/` | **C99 port** (float64/float32) and its host build. `mcu/` holds the Cortex-M4F firmware and the Renode simulation scripts. |
| `docs/research/` | Seed registry and the manifest of artifacts kept out of git. |
| `docs/architecture/` | Specifications (v0.1, v0.3.2, v0.51, v0.52 and its r1), freeze records, SHA-256 manifests, PDF builders (`pdf_source/`). |
| `configs/` | Canonical configuration(s), machine-readable. |
| `packages/lebre/` | The installable library `lebre` 0.1.0 (implements v0.52-r1 bit for bit); prepared to become its own repository. |
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

In total, 802 files and about 3 GB. They are meant to be deposited in an archival service (e.g. Zenodo) and restored before a full re-run; `python scripts/make_artifact_manifest.py --check` verifies a restored copy.

## Status and honesty notes

- Results cover two domains (hydrology, buildings) with 1–5 inputs and one-step forecasting.
- The declared cost contract was **not met** (+3.7% mean, +2.0% peak).
- The microcontroller results come from a **simulator**.
- The testing mechanism did **not** improve accuracy over an "all inputs on" ablation.
- The core mechanism is **not original**.

See §19 of the specification for the full list.

## Licence

- **Code:** Apache-2.0 (`LICENSE`).
- **Documents, reports, figures and result tables:** CC-BY-4.0 (`LICENSE-CC-BY-4.0.txt`).
- **Exclusions:** third-party data keep their own licences; the logo is excluded from both licences.

Details are in `NOTICE`.

## Citation

Lima, S. (2026). *LEBRE research record — v0.52-r1* [Software]. Zenodo. https://doi.org/10.5281/zenodo.23049103

- `10.5281/zenodo.23049103`: this version (v0.52-r1).
- `10.5281/zenodo.23049102`: all versions; resolves to the latest.

See also `CITATION.cff`.

---

*Documentação em português: [`README.pt-BR.md`](README.pt-BR.md). Most internal experiment logs are written in Portuguese.*
