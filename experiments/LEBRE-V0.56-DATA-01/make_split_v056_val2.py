#!/usr/bin/env python3
"""make_split_v056_val2.py — séries da segunda validação da v0.56 (SPLIT_RULES_ADENDO_01.md): as posições seguintes das
permutações já registradas. Usa só o sorteio registrado e metadados; nenhum valor de série."""
import hashlib
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
import make_split_v056 as M  # noqa: E402


def main():
    s = json.loads((HERE / "SPLIT_V056.json").read_text(encoding="utf-8"))
    assert hashlib.sha256((HERE / "SPLIT_V056.json").read_bytes()).hexdigest() == "ec9bb01ea6dcb8bc177a55e7729081746b22fbcd86ca35297674e640d10604e3"
    perm = s["camels_cl"]["permutacao"]
    assert perm[:30] == s["camels_cl"]["final"] and perm[30:50] == s["camels_cl"]["validacao"]
    cl = perm[50:70]
    b = M.bdg2()                                                     # reconstrói a permutação do BDG2 e confere a v0.55
    assert b["final"] == s["bdg2"]["final"] and b["validacao"] == s["bdg2"]["validacao"]
    import io
    import zipfile

    import numpy as np
    z = zipfile.ZipFile(M.D52 / "bdg2" / "building-data-genome-project-2-v1.0.zip")
    base = "buds-lab-building-data-genome-project-2-3d0cbaf/data/"
    meters = []
    for kind in ("chilledwater", "hotwater", "steam"):
        m = pd.read_csv(io.BytesIO(z.read(base + f"meters/cleaned/{kind}_cleaned.csv")), index_col=0)
        cov, nz = m.notna().mean(), (m.fillna(0) != 0).mean()
        meters += [f"{kind}:{x}" for x in cov[(cov >= M.MIN_COV) & (nz >= 0.5)].index]
    pick = [str(x) for x in np.random.default_rng(M.SEED_BDG2).permutation(sorted(meters))]
    assert sorted(pick[235:265]) == s["bdg2"]["final"]
    bd = sorted(pick[265:295])
    usados = set(s["camels_cl"]["final"]) | set(s["camels_cl"]["validacao"])
    assert not set(cl) & usados and not set(bd) & (set(s["bdg2"]["final"]) | set(s["bdg2"]["validacao"]))
    out = dict(criado=pd.Timestamp.now().isoformat(timespec="seconds"),
               split_v056_sha256="ec9bb01ea6dcb8bc177a55e7729081746b22fbcd86ca35297674e640d10604e3",
               camels_cl=dict(posicoes="50-69", validacao2=cl), bdg2=dict(posicoes="265-294", validacao2=bd))
    p = HERE / "SPLIT_V056_VAL2.json"
    p.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    h = hashlib.sha256(p.read_bytes()).hexdigest()
    (HERE / "SPLIT_V056_VAL2_SHA256.txt").write_text(f"{h} *SPLIT_V056_VAL2.json\n", encoding="utf-8", newline="\n")
    print("CAMELS-CL", len(cl), "| BDG2", len(bd), "| SHA-256", h)


if __name__ == "__main__":
    main()
