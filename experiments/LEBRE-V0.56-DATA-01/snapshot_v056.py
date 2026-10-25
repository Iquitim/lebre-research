#!/usr/bin/env python3
"""snapshot_v056.py — cópia dos dados brutos novos da v0.56 em data/external_v056/ (fora do git), com SHA-256
(regras em SPLIT_RULES.md, §4).

Duas fases, nesta ordem:
  python snapshot_v056.py base    os cinco arquivos do CAMELS-CL (PANGAEA, CC-BY-4.0) e a conferência dos arquivos
                                  brutos já registrados (CAMELS-BR e BDG2 da v0.52; ONS de 2024-2025 e de 2026)
  python snapshot_v056.py tempo   Open-Meteo nos locais das usinas sorteadas (depende de SPLIT_V056.json)
Os arquivos são gravados como baixados, sem abrir os valores. As funções de download são as de
LEBRE-V0.54-DATA-01/snapshot_v054.py, importadas sem alteração.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data" / "external_v056"
_s = importlib.util.spec_from_file_location("snapshot_v054", ROOT / "experiments" / "LEBRE-V0.54-DATA-01" / "snapshot_v054.py")
S54 = importlib.util.module_from_spec(_s); _s.loader.exec_module(S54)

PANGAEA = "https://store.pangaea.de/Publications/Alvarez-Garreton-etal_2018/"
CL = ["1_CAMELScl_attributes.zip", "3_CAMELScl_streamflow_mm.zip", "6_CAMELScl_precip_mswep.zip",
      "10_CAMELScl_tmean_cr2met.zip", "12_CAMELScl_pet_hargreaves.zip"]


def _conferir(pasta, sums):
    reg = {ln.split(" *")[1]: ln.split(" *")[0] for ln in sums.read_text().splitlines() if pasta in ln}
    assert reg, pasta
    for rel, h in reg.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h, f"arquivo alterado: {rel}"
    print("conferido:", pasta, len(reg), "arquivos")


def fase_base():
    for f in CL:
        S54.baixar(PANGAEA + f, OUT / "camels_cl" / f)
    E = ROOT / "experiments"
    _conferir("data/external_v053/ons_fator", E / "LEBRE-V0.53-DATA-01" / "SNAPSHOT_SHA256SUMS.txt")
    _conferir("data/external_v054/ons_fator_2026", E / "LEBRE-V0.54-DATA-01" / "SNAPSHOT_SHA256SUMS.txt")
    sums52 = ROOT / "data" / "external_v052" / "SHA256SUMS.txt"
    reg = [ln.split() for ln in sums52.read_text().splitlines() if ln.strip() and ("camels_br" in ln or "bdg2" in ln)]
    assert reg
    for h, rel in reg:
        p = ROOT / rel.lstrip("*")
        assert hashlib.sha256(p.read_bytes()).hexdigest() == h, f"arquivo alterado: {rel}"
    print("conferido: CAMELS-BR e BDG2 da v0.52,", len(reg), "arquivos")


def fase_tempo():
    split = json.loads((HERE / "SPLIT_V056.json").read_text(encoding="utf-8"))
    for tipo, vars_, (ini, fim) in (("solar", S54.VARS_SOLAR, ("2026-01-01", "2026-09-30")),
                                    ("eolica", S54.VARS_EOLICA, ("2024-01-01", "2025-12-31"))):
        for u in split[tipo]["reservadas"]:
            safe = "".join(c if c.isalnum() else "_" for c in u["nome"])
            S54.open_meteo(u["lat"], u["lon"], ini, fim, vars_, OUT / "open_meteo" / f"{tipo}_{safe}.json")


def gravar_somas(nome):
    linhas = [f"{hashlib.sha256(p.read_bytes()).hexdigest()} *{p.relative_to(ROOT).as_posix()}"
              for p in sorted(OUT.rglob("*")) if p.is_file()]
    (HERE / nome).write_text("\n".join(linhas) + "\n", encoding="utf-8", newline="\n")
    print(len(linhas), "arquivos em", nome)


if __name__ == "__main__":
    fase = sys.argv[1]
    {"base": fase_base, "tempo": fase_tempo}[fase]()
    gravar_somas("SNAPSHOT_BASE_SHA256SUMS.txt" if fase == "base" else "SNAPSHOT_SHA256SUMS.txt")
