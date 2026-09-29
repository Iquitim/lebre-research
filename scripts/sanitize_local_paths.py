#!/usr/bin/env python3
"""sanitize_local_paths.py — removes absolute paths of the original workstation (which contain the local user name)
from tracked text files, before the repository is made public.

The user name is read from the environment at run time (USERNAME / USER); it is never written in this file.
Rules (applied in order):
  code (.py)  a hard-coded artifact/download/temp directory literal becomes a portable expression
              (os.path.expanduser("~") / tempfile.gettempdir());
  code (.sh)  the Renode workdir "/c/Users/<user>/AppData/Local/Temp/..." becomes "/tmp/..." (Git Bash maps /tmp to %TEMP%);
  text        the site-packages path of the local Python becomes <site-packages>; any remaining "<drive>:/Users/<user>"
              (either slash style, also inside file:/// links) becomes <HOME>.
For each changed file the SHA-256 before and after is appended to docs/architecture/SANITIZATION_RECORD.tsv, together
with the manifests that list it, so scripts/verify_integrity.py can still verify frozen entries.
Usage: python scripts/sanitize_local_paths.py [--dry-run]"""
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REC = ROOT / "docs" / "architecture" / "SANITIZATION_RECORD.tsv"
USER = os.environ.get("USERNAME") or os.environ.get("USER")
U = re.escape(USER)
HOME = rf"(?:[A-Za-z]:|/[a-zA-Z])[\\/]+Users[\\/]+{U}"
SITE = rf"{HOME}[\\/]+AppData[\\/]+Local[\\/]+Packages[\\/]+PythonSoftwareFoundation\.Python\.[0-9._a-z]+[\\/]+LocalCache[\\/]+local-packages[\\/]+Python3\d+[\\/]+site-packages"
WS = rf"{HOME}[\\/]+\.gemini[\\/]+antigravity-ide[\\/]+brain[\\/]+[0-9a-f-]{{36}}"


def py_rules(s):
    # r"<WS>" or "<WS>/file.png"  ->  os.path.join(os.path.expanduser("~"), "lebre_artifacts"[, "file.png"])
    def ws_lit(m):
        tail = m.group("tail")
        args = ['os.path.expanduser("~")', '"lebre_artifacts"'] + ([f'"{tail}"'] if tail else [])
        return f'os.path.join({", ".join(args)})'
    s = re.sub(rf'r?"{WS}(?:[\\/]+(?P<tail>[^"\\/]+))?"', ws_lit, s)
    s = re.sub(rf'r?"{HOME}[\\/]+Downloads[\\/]+(?P<f>[^"]+)"', lambda m: f'os.path.join(os.path.expanduser("~"), "Downloads", "{m.group("f")}")', s)
    s = re.sub(rf'r?"{HOME}[\\/]+AppData[\\/]+Local[\\/]+Temp[\\/]+(?P<a>[^"\\/]+)[\\/]+(?P<b>[^"\\/]+)"',
               lambda m: f'os.path.join(__import__("tempfile").gettempdir(), "{m.group("a")}", "{m.group("b")}")', s)
    return s


def sh_rules(s):
    return re.sub(rf'{HOME}/AppData/Local/Temp/', '/tmp/', s)


def text_rules(s):
    s = re.sub(SITE, "<site-packages>", s)
    s = re.sub(WS, "<assistant-workspace>", s)
    s = re.sub(HOME, "<HOME>", s)
    return s


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    dry = "--dry-run" in sys.argv
    files = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout.decode().split("\0")
    pat = re.compile(HOME.encode(), re.I)
    manifests = sorted((ROOT / "docs" / "architecture").glob("*SHA256SUMS*.txt"))
    rows = []
    for f in [x for x in files if x]:
        p = ROOT / f
        if not p.is_file():
            continue
        b = p.read_bytes()
        if not pat.search(b):
            continue
        s = b.decode("utf-8", errors="surrogateescape")
        if f.endswith(".py"):
            s = py_rules(s)
        elif f.endswith(".sh"):
            s = sh_rules(s)
        s = text_rules(s)
        nb = s.encode("utf-8", errors="surrogateescape")
        listed = [m.name for m in manifests if f in m.read_text(encoding="utf-8", errors="replace")]
        rows.append((f, sha(b), sha(nb), ";".join(listed)))
        print(f"{'(dry) ' if dry else ''}{f}  listed in: {', '.join(listed) or '-'}")
        if not dry:
            p.write_bytes(nb)
    if not dry and rows:
        new = not REC.exists()
        with open(REC, "a", encoding="utf-8", newline="\n") as fh:
            if new:
                fh.write("path\tsha256_before\tsha256_after\tmanifests\n")
            for r in rows:
                fh.write("\t".join(r) + "\n")
    print(f"{len(rows)} files {'would change' if dry else 'sanitized'}")


if __name__ == "__main__":
    main()
