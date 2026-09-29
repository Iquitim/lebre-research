#!/usr/bin/env python3
"""make_artifact_manifest.py — lists every file kept OUT of git (per .gitignore) that belongs to the research record,
with size and SHA-256, into ARTIFACTS_MANIFEST.tsv. Caches (__pycache__, .pytest_cache) and QA renders are excluded.
These files must be restored from the artifact archive (e.g. a Zenodo deposit) for a full re-run; checkout + restore is
then verified with:  python scripts/make_artifact_manifest.py --check
The toolchain archives (tools/*.zip) are listed too, so their exact bytes can be checked after download."""
import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ARTIFACTS_MANIFEST.tsv"
SKIP = ("__pycache__", ".pytest_cache", "scratch/pdf_qa", ".png", ".pdb")   # .pdb debug symbols embed local paths
KEEP_TOOLS = ("tools/gcc.zip", "tools/renode.zip")


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def ignored():
    r = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "-z", "--others", "--ignored", "--exclude-standard"],
                       cwd=ROOT, capture_output=True, check=True)
    fs = [f for f in r.stdout.decode("utf-8").split("\0") if f]
    fs = [f for f in fs if not any(s in f for s in SKIP) and (not f.startswith("tools/") or f in KEEP_TOOLS)]
    return sorted(fs)


if __name__ == "__main__":
    if "--check" in sys.argv:
        bad = miss = 0
        for ln in OUT.read_text(encoding="utf-8").splitlines()[1:]:
            h, size, rel = ln.split("\t")
            p = ROOT / rel
            if not p.exists():
                miss += 1
            elif sha(p) != h:
                bad += 1; print("MISMATCH", rel)
        print(f"missing {miss}, mismatched {bad}"); sys.exit(1 if bad else 0)
    rows = [(sha(ROOT / f), (ROOT / f).stat().st_size, f) for f in ignored()]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("sha256\tbytes\tpath\n")
        for h, s, f in rows:
            fh.write(f"{h}\t{s}\t{f}\n")
    print(f"{len(rows)} files, {sum(r[1] for r in rows) / 1e9:.2f} GB -> {OUT.name}")
