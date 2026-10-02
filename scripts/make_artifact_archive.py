#!/usr/bin/env python3
"""make_artifact_archive.py — builds the public archive of the experiment artifacts kept out of git.

Selection (from docs/research/ARTIFACTS_MANIFEST.tsv, experiments/ only; raw third-party data under data/ and
toolchains under tools/ are never included):
- included unchanged: per-series prediction arrays, foundation-model outputs, documentation examples, event logs and
  the generated firmware header;
- included FILTERED: aggregated development-phase prediction files that also hold series from datasets whose licence
  does not allow redistribution under CC-BY-4.0 (Silverbox: no explicit licence; Cascaded Tanks: CC-BY-SA-4.0). The
  entries of those datasets are removed; every other array is kept bit for bit;
- excluded: firmware build outputs (.elf, .o, .dll, .lib, .map). They link third-party runtime code and the linker
  maps hold local paths; they are rebuilt from the sources in git with the pinned toolchain (environment/TOOLCHAIN.md).

Writes to <out> eight zip parts of at most ~200 MB each (so that each can be uploaded on its own), plus ARCHIVE_README.md,
ARCHIVE_CONTENTS.tsv and ARCHIVE_SHA256SUMS.txt as separate files; every part unzips at the repository root. Also
writes docs/research/ARCHIVE_CONTENTS.tsv (path, original SHA-256, archived SHA-256, status).
scripts/verify_integrity.py accepts a FILTERED file whose hashes match that record.
Usage: python scripts/make_artifact_archive.py <out_dir>"""
import csv
import hashlib
import io
import sys
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAME = "lebre-research-v0.52-r1-artifacts"
EXCLUDE_EXT = {".elf", ".o", ".dll", ".lib", ".map"}
NOT_REDISTRIBUTABLE = {"silverbox", "tanks"}        # see experiments/LEBRE-V0.52-DATA-01/LICENSES_AND_CITATIONS.md


PARTS = ["part1-reserve3", "part2-reserve2-and-early-logs", "part3-reserve1-ons", "part4a-reserve1-camels",
         "part4b-reserve1-bdg2", "part5-development-a", "part6a-development-tuning-1-4", "part6b-development-tuning-5-14"]


def part_of(path):
    e = path.split("/")
    if e[1] in ("LEBRE-V0.52-HELDOUT-03", "LEBRE-V0.52-DOC-01", "LEBRE-V0.52-EXT-01"):
        return "part1-reserve3"
    if e[1] == "LEBRE-V0.52-HELDOUT-01":
        if e[2] == "preds" and e[3].startswith("ons__"):
            return "part3-reserve1-ons"
        return "part4a-reserve1-camels" if e[2] == "preds" and e[3].startswith("camels__") else "part4b-reserve1-bdg2"
    if e[1] == "LEBRE-V0.52-PROTO-01":
        if e[2].startswith("TUNE_DEV"):
            rnd = int(e[2][len("TUNE_DEV"):].split("_")[0])
            return "part6a-development-tuning-1-4" if rnd <= 4 else "part6b-development-tuning-5-14"
        return "part5-development-a"
    return "part2-reserve2-and-early-logs"           # reserve 2 and the event logs of earlier phases


def sha(b):
    return hashlib.sha256(b).hexdigest()


def source_of(key):
    return key.split(":")[0].split("|")[0]


def filtered_npz(path):
    """Copy of an .npz without the entries of non-redistributable datasets, or None if it holds none."""
    z = np.load(path, allow_pickle=False)
    if not any(source_of(k) in NOT_REDISTRIBUTABLE for k in z.files):
        return None
    keep = {k: z[k] for k in z.files if source_of(k) not in NOT_REDISTRIBUTABLE}
    buf = io.BytesIO(); np.savez_compressed(buf, **keep)
    return buf.getvalue()


README = """# LEBRE research record v0.52-r1: experiment artifacts

Companion archive of the research record https://github.com/Iquitim/lebre-research
(doi:10.5281/zenodo.23049103). It holds the experiment outputs that are too large for git: per-series prediction
arrays of the pre-registered evaluations, foundation-model comparator outputs, development-phase prediction files,
documentation examples and event logs of earlier phases.

## How to use

1. Clone the research repository (main branch) and unzip every part of this archive at its root; files land at the paths listed
   in docs/research/ARTIFACTS_MANIFEST.tsv. Use a checkout that contains docs/research/ARCHIVE_CONTENTS.tsv: support
   for this archive was added after tag v0.52-r1; the model, results and frozen manifests are unchanged.
2. Download the raw public data with `python scripts/download_data.py` (not redistributed here; sources, licences
   and SHA-256 in data/README.md). It checks every file against the frozen hashes.
3. Run `python scripts/verify_integrity.py` and `python scripts/reproduce_smoke.py` (REPRODUCIBILITY.md).

## What is not here, and why

- Raw third-party data: obtained from the original publishers with the download script.
- Firmware build outputs (.elf, .o, .dll, .lib, .map): rebuilt from the sources in git with the pinned toolchain;
  they link third-party runtime code and the linker maps contain local build paths.
- Entries of two datasets inside the aggregated development-phase files (status FILTERED in ARCHIVE_CONTENTS.tsv):
  Silverbox (no explicit licence) and Cascaded Tanks (CC-BY-SA-4.0). All other arrays in those files are unchanged.
  Development tables that involve these two datasets cannot be regenerated from this archive alone.

## Licences

Model outputs, logs and other files produced in this project: CC-BY-4.0, (c) 2026 Silvano Lima.
Some arrays (the target `y` in the per-series files and the documentation examples, and the generated firmware
header) are copies of third-party series, which remain under their original licences and require attribution:
- ONS, Operador Nacional do Sistema Eletrico. Dados Abertos: Dados Hidraulicos por Reservatorio (CC-BY).
  https://dados.ons.org.br/dataset/dados_hidrologicos_ho
- Chagas, V. B. P. et al. (2020). CAMELS-BR: hydrometeorological time series and landscape attributes for 897
  catchments in Brazil. Earth System Science Data 12, 2075-2096. doi:10.5281/zenodo.15025488 (CC-BY-4.0).
- Miller, C. et al. (2020). The Building Data Genome Project 2, energy meter data from the ASHRAE Great Energy
  Predictor III competition. Scientific Data 7, 368. doi:10.5281/zenodo.3887306 (CC-BY-4.0).
Foundation-model outputs were produced with Chronos-2 / Chronos-Bolt (Amazon, Apache-2.0) and Tiny Time Mixers
(IBM, Apache-2.0).

Parts (all unzip at the repository root):
- part1-reserve3: reserve 3 (the evaluation reported in the paper), documentation examples, development comparators;
- part2-reserve2-and-early-logs: reserve 2 and event logs of earlier phases;
- part3-reserve1-ons, part4a-reserve1-camels, part4b-reserve1-bdg2: reserve 1 (part4b also holds the
  Chronos outputs of reserve 1);
- part5-development-a, part6a-development-tuning-1-4, part6b-development-tuning-5-14: development-phase prediction
  files.
The smoke reproduction of the paper results needs part1 only.

Integrity: ARCHIVE_SHA256SUMS.txt lists every file in the archive and every zip part.
"""


def main():
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(open(ROOT / "docs/research/ARTIFACTS_MANIFEST.tsv", encoding="utf-8"), delimiter="\t"))
    rows = [r for r in rows if r["path"].startswith("experiments/")]
    for old in out.glob(f"{NAME}*"):
        old.unlink()
    record, sums = [], []
    zfs = {k: zipfile.ZipFile(out / f"{NAME}-{k}.zip", "w", zipfile.ZIP_DEFLATED, compresslevel=6) for k in PARTS}
    for r in sorted(rows, key=lambda r: r["path"]):
        p = r["path"]
        if Path(p).suffix.lower() in EXCLUDE_EXT:
            record.append((p, r["sha256"], "", "EXCLUDED")); continue
        b = (ROOT / p).read_bytes()
        assert sha(b) == r["sha256"], f"local file differs from the manifest: {p}"
        f = filtered_npz(ROOT / p) if p.endswith(".npz") else None
        if f is not None:
            b, status = f, "FILTERED"
        else:
            status = "IDENTICAL"
        info = zipfile.ZipInfo(p, date_time=(2026, 9, 30, 0, 0, 0))
        info.compress_type = zipfile.ZIP_STORED if p.endswith(".npz") else zipfile.ZIP_DEFLATED
        zfs[part_of(p)].writestr(info, b)
        record.append((p, r["sha256"], sha(b), status)); sums.append(f"{sha(b)} *{p}")
    for z in zfs.values():
        z.close()
    rec_txt = "path\tsha256_original\tsha256_archived\tstatus\n" + "".join("\t".join(x) + "\n" for x in record)
    parts = [out / f"{NAME}-{k}.zip" for k in PARTS]
    part_sums = [f"{sha(z.read_bytes())} *{z.name}" for z in parts]
    (out / "ARCHIVE_README.md").write_text(README, encoding="utf-8", newline="\n")
    (out / "ARCHIVE_CONTENTS.tsv").write_text(rec_txt, encoding="utf-8", newline="\n")
    (out / "ARCHIVE_SHA256SUMS.txt").write_text("# zip parts\n" + "\n".join(part_sums) + "\n# files inside the parts\n"
                                                + "\n".join(sums) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "docs/research/ARCHIVE_CONTENTS.tsv").write_text(rec_txt, encoding="utf-8", newline="\n")
    n = {st: sum(1 for x in record if x[3] == st) for st in ("IDENTICAL", "FILTERED", "EXCLUDED")}
    print(n)
    for z in parts:
        print(f"{z.stat().st_size / 1e6:7.1f} MB  {z.name}")


if __name__ == "__main__":
    main()
