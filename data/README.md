# data/ (raw data not in git)

Only loaders, checksum lists and manifests are tracked. The raw public datasets are listed with SHA-256 in `docs/research/ARTIFACTS_MANIFEST.tsv` and must be downloaded (or restored from the artifact archive) before re-running.

| Folder | Content | How to obtain | Licence |
|---|---|---|---|
| `external_v052/` | ONS hourly/daily hydro data, CAMELS-BR v1.2, Building Data Genome 2 v1.0, Cascaded Tanks | `python experiments/LEBRE-V0.52-DATA-01/download_v052.py`; file list, URLs, licences and SHA-256 in `external_v052/MANIFEST.csv` and `SHA256SUMS.txt` | ONS CC-BY; CAMELS-BR CC-BY-4.0; BDG2 CC-BY-4.0; Cascaded Tanks CC-BY-SA-4.0 (see `experiments/LEBRE-V0.52-DATA-01/LICENSES_AND_CITATIONS.md`) |
| `external_v051/`, `external_v05/`, `external_bench04/` | ONS load/generation, BCB exchange rates, UCI and other sets used by v0.4–v0.51 | loaders `load051.py`, `load05.py`, `load04.py` document the sources | per source |
| `external_bench02/`, `external_bench03/`, `external_v03/` | ETT, electricity, traffic, exchange-rate; Monash archive (`.tsf`); UCI sets | `SHA256SUMS.txt` in each folder | per source (Monash CC-BY-4.0) |
| `external/` | Early benchmark series (Silverbox, Elec2, Jena climate, …) | — | per source |

**Redistribution.** Before depositing raw data in a public archive, confirm that each licence allows redistribution. Datasets without an explicit licence (e.g. Wiener-Hammerstein, not used in published results) must not be redistributed. Where redistribution is not allowed, the checksums plus the download script are the reproducibility path.
