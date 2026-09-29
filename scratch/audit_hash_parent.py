#!/usr/bin/env python3
import hashlib
from pathlib import Path

parent_dir = Path("experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01")
audit_dir = Path("experiments/LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01")
audit_dir.mkdir(parents=True, exist_ok=True)
(audit_dir / "figures").mkdir(parents=True, exist_ok=True)

hash_lines = []
for p in sorted(parent_dir.rglob("*")):
    if p.is_file():
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        rel = p.relative_to(parent_dir).as_posix()
        hash_lines.append(f"{h}  {rel}")

out_path = audit_dir / "LEBRE_V0_2_PARENT_ARTIFACT_HASHES.txt"
out_path.write_text("\n".join(hash_lines) + "\n", encoding="utf-8")
print(f"Hashed {len(hash_lines)} parent files into {out_path}")
