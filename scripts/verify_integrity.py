#!/usr/bin/env python3
"""verify_integrity.py — checks every SHA-256 manifest of the project (frozen versions and published documents).

Each line is reported as OK, MISMATCH (file present, different bytes) or MISSING (not present in this checkout; files
kept out of git are listed in docs/research/ARTIFACTS_MANIFEST.tsv and must be restored from the artifact archive). Known, documented
supersessions are reported separately. Exit code 1 only on MISMATCH that is not a documented supersession.
Usage: python scripts/verify_integrity.py [--quiet]"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = sorted((ROOT / "docs" / "architecture").glob("*SHA256SUMS*.txt"))
# Build sources of the v0.52 spec revision 0 were updated in place to build revision 1 (LEBRE_v0.52_RELEASE_NOTES.md);
# the revision-0 PDFs/HTML themselves are unchanged and verified.
SUPERSEDED = {("LEBRE_v0.52_SPEC_SHA256SUMS.txt", p) for p in (
    "docs/architecture/pdf_source/build_v052_spec.py", "docs/architecture/pdf_source/v052_text.py",
    "docs/architecture/pdf_source/v052_charts.py", "docs/architecture/pdf_source/v052_data.py")}


# Files whose local absolute paths were removed before publication (scripts/sanitize_local_paths.py): the manifest keeps
# the original hash; the record maps it to the sanitized one.
SANITIZED = {}
_rec = ROOT / "docs" / "architecture" / "SANITIZATION_RECORD.tsv"
if _rec.exists():
    for _ln in _rec.read_text(encoding="utf-8").splitlines()[1:]:
        _p, _before, _after, _m = _ln.split("	")
        SANITIZED[(_p, _before)] = _after


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    quiet = "--quiet" in sys.argv
    bad = 0
    for m in MANIFESTS:
        c = {"OK": 0, "MISSING": 0, "MISMATCH": 0, "SUPERSEDED": 0, "SANITIZED": 0}
        for ln in m.read_text(encoding="utf-8", errors="replace").splitlines():
            ln = ln.strip()
            if not ln or ln.startswith("#"):
                continue
            h, rel = ln.split(maxsplit=1); rel = rel.lstrip("*").strip()
            p = ROOT / rel
            if not p.exists() and (m.parent / rel).exists():      # some manifests use paths relative to themselves
                p = m.parent / rel
            if not p.exists():
                st = "MISSING"
            elif (hp := sha(p)) == h.lower():
                st = "OK"
            elif SANITIZED.get((rel, h.lower())) == hp:
                st = "SANITIZED"
            elif (m.name, rel) in SUPERSEDED:
                st = "SUPERSEDED"
            else:
                st = "MISMATCH"; bad += 1
            c[st] += 1
            if st not in ("OK", "SANITIZED") and not quiet:
                print(f"  {st:10s} {rel}")
        print(f"{m.name}: " + ", ".join(f"{k} {v}" for k, v in c.items() if v))
    print("RESULT:", "FAIL" if bad else "PASS (no unexpected mismatch)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
