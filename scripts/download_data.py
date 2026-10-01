#!/usr/bin/env python3
"""download_data.py — downloads the raw public data of v0.52 and checks them against the frozen checksums.

Runs the frozen download script (experiments/LEBRE-V0.52-DATA-01/download_v052.py) unchanged. That script rewrites
data/external_v052/MANIFEST.csv and SHA256SUMS.txt with the hashes of the day; both are frozen records, so they are
kept aside and restored here, and the hashes of the day go to data/external_v052/DOWNLOADED_SHA256SUMS.txt.

Every file listed in the frozen SHA256SUMS.txt is then reported as identical, changed or missing. The publishers keep
updating some files (ONS adds the current month and completes the current year). The check fails only when a file
read by the loaders differs: ONS hourly files of 2015-2025, CAMELS-BR and BDG2 (experiments/LEBRE-V0.52-PROTO-01/
data_v052.py). Cascaded Tanks and the ONS daily files are not read in the published results.
Usage: python scripts/download_data.py"""
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "data" / "external_v052"
RECORDS = ("MANIFEST.csv", "SHA256SUMS.txt")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def used(rel):
    m = re.search(r"ons_hourly/DADOS_HIDROLOGICOS_HO_(\d{4})_\d{2}\.parquet$", rel)
    return bool(m and 2015 <= int(m.group(1)) <= 2025) or "/camels_br/" in rel or "/bdg2/" in rel


def main():
    D.mkdir(parents=True, exist_ok=True)
    saved = {n: (D / n).read_bytes() for n in RECORDS}
    try:
        r = subprocess.run([sys.executable, str(ROOT / "experiments/LEBRE-V0.52-DATA-01/download_v052.py")])
    finally:
        if (D / "SHA256SUMS.txt").read_bytes() != saved["SHA256SUMS.txt"]:
            shutil.copyfile(D / "SHA256SUMS.txt", D / "DOWNLOADED_SHA256SUMS.txt")
        for n, b in saved.items():
            (D / n).write_bytes(b)
    if r.returncode:
        print("download failed"); return 1
    same, changed, missing = 0, [], []
    for ln in saved["SHA256SUMS.txt"].decode("utf-8").splitlines():
        if not ln.strip():
            continue
        h, rel = ln.split(maxsplit=1); rel = rel.lstrip("*")
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
        elif sha(p) == h:
            same += 1
        else:
            changed.append(rel)
    bad = [x for x in changed + missing if used(x)]
    print(f"frozen data files: {same} identical, {len(changed)} changed, {len(missing)} missing")
    for x in changed + missing:
        print(f"  {'CHANGED' if x in changed else 'MISSING'} {x}  ({'READ BY THE LOADERS' if used(x) else 'not used in the published results'})")
    print("RESULT:", "FAIL (a file used in the results differs from the frozen data)" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
