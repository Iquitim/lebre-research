# Reproducibility map — LEBRE v0.52-r1

Every number in the v0.52 specification, revision 1 (`docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_{EN,PTBR}.pdf`), traces to a script, its inputs and its outputs listed here. All paths are relative to the repository root. The spec builder reads the numbers from the output files at build time (`docs/architecture/pdf_source/v052_data.py`); no number is typed by hand.

## 0. Before re-running anything

1. **Environment:**
   - Python 3.11 with `environment/requirements-research.txt`;
   - **pandas must be 2.2.3**: pandas ≥ 3 makes `to_numpy()` arrays read-only and breaks the frozen data loader;
   - toolchains as in `environment/TOOLCHAIN.md`.
2. **Restore the artifacts kept out of git** (`docs/research/ARTIFACTS_MANIFEST.tsv`: data, predictions, toolchain archives). Then run `python scripts/make_artifact_manifest.py --check`.
3. `python scripts/verify_integrity.py` checks all frozen SHA-256 manifests. It must report `PASS`.
4. `python scripts/reproduce_smoke.py` runs four checks:
   - configuration;
   - bit-exact re-run of the frozen model on reserve-3 series;
   - regeneration of the reserve-3 table;
   - C99 port versus Python.

   All four passed on 2026-09-29 (Windows 11, Python 3.11.9).

**Frozen code is never edited.** Later stages import the frozen modules. `configs/lebre_v052_canonical.json` is the canonical configuration; `experiments/LEBRE-V0.52-EXT-01/heldout2_cfg.py` asserts it equals the frozen definition.

**Held-out data (reserves).** The loader `experiments/LEBRE-V0.52-PROTO-01/data_v052.py` refuses reserve series unless called with `final=True`, which only pre-registered runs use. All three reserves are now consumed. Re-running them reproduces the published results, but it is not a new evaluation.

## 1. Data and splits

| What | Script | Output |
|---|---|---|
| Download of public datasets (ONS, CAMELS-BR, BDG2, Cascaded Tanks) with checksums | `experiments/LEBRE-V0.52-DATA-01/download_v052.py` | `data/external_v052/` (raw, out of git); `data/external_v052/MANIFEST.csv`, `SHA256SUMS.txt` |
| Development / held-out split by seeded permutations (seeds 5201–5203) | `experiments/LEBRE-V0.52-DATA-01/make_split_v052.py` | `SPLIT_V052.json` (+ SHA-256) |
| Reserve 2 and 3: next positions of the same permutations | `experiments/LEBRE-V0.52-HELDOUT-0{2,3}/select_reserve{2,3}.py` | `RESERVA2.json`, `RESERVA3.json` |

## 2. Development (spec §5–§12; not independent evidence)

| Result | Script (in `experiments/LEBRE-V0.52-PROTO-01/` unless noted) | Output |
|---|---|---|
| Measurements #3–#7 (synthetic, semi-synthetic, null batches, real development series) | `final3.py` … `final7.py`, `semi_synth*.py`, `null_batch.py` | `FINAL{3..7}_*.csv`, `DEV_LOG.md` |
| E-process simulation: type I and power, one-sided c | `sim_evidence.py` | reported in `DEV_LOG.md` (spec Fig. "Validity/Power") |
| Online oracle (information limit on smooth inputs) | `oracle_online.py` | `DEV_LOG.md` |
| Stress test of target gaps (hold + output contract) | `stress_gaps.py` | `STRESS_GAPS.csv` |
| Misadjustment note and verification | `experiments/LEBRE-V0.52-EXT-01/misadj_verify.py` | `MISADJ_VERIFY2.csv`, `MISADJUSTMENT_NOTE.md` |
| Development comparison incl. FITS, SparseTSF, TTM, Chronos-2 (1,000 points) | `comp_dev.py`, `chronos_dev.py`; `EXT-01/dev_comparators.py`, `ttm_tune_dev.py` | `COMP_DEV*.csv`, `EXT-01/DEV_COMP_*.csv`, `TTM_TUNE_DEV.csv` |
| Illustrative examples (evidence trace, recovered response, cost by component) | `experiments/LEBRE-V0.52-DOC-01/doc_examples.py` | `DOC_EXAMPLES.json`, `DOC_EXAMPLE_{A,B}.npz` |

## 3. Pre-registered evaluations on never-seen series (spec §13–§14)

Each folder contains the pre-registration (written and hashed before access), the run scripts, per-series predictions (`preds/`, out of git), logs, tables and a report.

| Evaluation | Folder | Run | Analysis → tables | Report |
|---|---|---|---|---|
| Reserve 1 (125 series; version without output safeguards) | `LEBRE-V0.52-HELDOUT-01` | `heldout_run.py`, `heldout_chronos.py` | `heldout_analysis.py` → `HELDOUT_TABLE_*.csv` | `HELDOUT_REPORT.md` |
| Reserve 2 (40 series; final version) | `LEBRE-V0.52-HELDOUT-02` | `heldout2_run.py`, `heldout2_chronos.py` | `heldout2_analysis.py` → `RESERVA2_*.csv` | `RESERVA2_REPORT.md` |
| Reserve 3 (60 series; ultralight, TTM, C port, MCU) | `LEBRE-V0.52-HELDOUT-03` | `heldout3_run.py`, `heldout3_ttm_chronos.py`, `heldout3_mcu.sh` | `heldout3_analysis.py` → `RESERVA3_*.csv` | `RESERVA3_REPORT.md` |

## 4. C99 port and simulated microcontroller (spec §15)

| Result | Script | Output |
|---|---|---|
| Host build of the port (float64, float32) | `experiments/LEBRE-V0.52-EXT-01/lebre_c/build_host.sh` (zig cc 0.16.0) | `lebre052_f{64,32}.dll` (out of git) |
| Equivalence on 29 development series | `EXT-01/equiv_test.py` | `EQUIV_TEST.csv` |
| Cortex-M4F firmware + Renode run (development series) | `EXT-01/mcu/build_run.sh <task> <tag>` | `EXT-01/mcu/uart_*.txt`, `size_*.txt` |
| Same on reserve 3 (pre-registered) | `HELDOUT-03/heldout3_mcu.sh` | `HELDOUT-03/mcu/r3_*.txt` |
| Cycle estimate from execution traces | `EXT-01/mcu/cycles_estimate.py`; `DOC-01/trace_breakdown.py` | `DOC-01/TRACE_BREAKDOWN.csv` |
| Per-block profile (documentation only) | `DOC-01/mcu_profile/build_profile.sh` | `DOC-01/mcu_profile/profile_*.txt` |

The Renode run scripts use a workdir without spaces (`/tmp/claude/lebre_mcu` in Git Bash, i.e. `%TEMP%\claude\lebre_mcu`). Renode fails on paths containing spaces.

## 5. Post-freeze checks included in r1 (spec §12, §16, §17)

| Result | Script (`experiments/LEBRE-V0.52-EXT-02/`) | Output / report |
|---|---|---|
| False-change control simulation (700 runs, seeds 8201…) | `fdr_sim.py` | `FDR_SIM_*.csv`, `FDR_SIM_REPORT.md` |
| Exploratory "all on" ablation on reserves 2 and 3 | `ablation_allon.py` | `ABL_ALLON_*.csv`, `ABL_ALLON_REPORT.md` |
| Literature audit, second round | protocol + log (no code) | `LIT_REVIEW_*.md`, `PRA_05_REPORT.md` |

The plan and script hashes were recorded before these runs (`HASHES_BEFORE_RUN.txt`).

## 6. Documents

| Document | Builder | Notes |
|---|---|---|
| v0.52 spec r1 (EN, PT-BR) | `docs/architecture/pdf_source/build_v052_spec.py` (+ `v052_text.py`, `v052_charts.py`, `v052_diagrams.py`, `v052_data.py`) | Needs Microsoft Edge (headless print) and internet access for KaTeX. **Byte-level** output is not reproducible, because the charts embed their generation timestamp; content and numbers are. Revision 0 is kept only as PDF/HTML with hashes (its builder was updated in place). |
| Paper (English, arXiv) | `paper/build.sh` (runs `paper/build_assets.py`, `pdflatex`, `bibtex`) | Every number, table and data figure is generated from the result files; `paper/arxiv_source.tar.gz` is the arXiv upload. |
| Earlier specs (v0.1, v0.3.2, v0.51, v0.51-r1) | `docs/architecture/pdf_source/build_*.py` | Frozen with their manifests. |

## 7. Known reproducibility caveats

- The C float32 build reproduces the Python decision sequence on 90–97% of the series; elsewhere a decision near the threshold shifts by a few steps (rounding). The float64 build is exact.
- Foundation models (Chronos-2, TTM) were run on CPU with the package versions in `environment/requirements-research.txt`. Other versions or hardware may change their numbers slightly.
- Before publication, absolute paths of the original workstation were removed from 34 tracked files (`scripts/sanitize_local_paths.py`). Hard-coded directories in scripts became portable (`os.path.expanduser("~")`, the system temp dir, `/tmp` in Git Bash); logs show `<HOME>`. Ten of these files are listed in hash manifests; `docs/architecture/SANITIZATION_RECORD.tsv` maps their original to their sanitized SHA-256, and `scripts/verify_integrity.py` reports them as SANITIZED. No frozen model, analysis or result file was affected.
