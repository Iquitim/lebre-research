#!/usr/bin/env python3
"""dev2_run.py — execuções da etapa LEBRE-V0.56-DEV-02 (PLANO_DEV_DINAMICO.md, §3). Grava preds/<parte>__<id>.npz e
.json (fora do git). O protótipo congelado (commit ef77728) num worktree limpo, em LEBRE056_PROTO.

  <python do Lab> dev2_run.py e20     E20: D1 a D4 (A, C3, C4 e C5 vêm de LEBRE-V0.56-DEV-01/preds)
  python dev2_run.py resto            prédios P, bacias D-A, D-B e CL-V, rios do ONS: A, C3, C4, C5, D1 a D4, S1 a S10

Conferência: nas partes recalculadas, as previsões de A, C3, C4 e C5 são comparadas bit a bit com as já gravadas
(DEV-01 para P e D-A; DIAG-01 para A em D-B; DIAG-03 para CL-V; DEV-01 para A e C5 nos rios e C5 em D-B). No E20, as
referências são reaproveitadas, não recalculadas, e não há conferência.
"""
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
E = AQUI.parent
OUT = AQUI / "preds"
COMMIT = "ef77728"
REF = ("A", "C3", "C4", "C5")
DIN = ("D1", "D2", "D3", "D4")
SENS = tuple(f"S{i}" for i in range(1, 11))
for p in (AQUI, E / "LEBRE-V0.56-DEV-01", E / "LEBRE-V0.56-DIAG-01", E / "LEBRE-V0.56-DATA-01"):
    sys.path.insert(0, str(p))


def proto():
    p = os.environ["LEBRE056_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")


def _serie(parte, ident):
    if parte == "e20":
        import dev_run as R1
        return R1._serie("e20", tuple(ident))
    if parte == "P":
        import dev_dados as DD
        s = DD.carregar_predio(ident); s["ref"] = "seasonal"
        return s
    if parte in ("ONSD", "ONSR"):
        import dev_dados as DD
        return DD.carregar_rio(ident)
    if parte in ("DA", "DB"):
        import diag_dados as DG
        s = DG.carregar(ident)
        return dict(y=s["y"], X=s["X"], q=s["q"], season=None, season2=None, ref="persistence")
    import dados_v056 as D
    s, ref = D.carregar("camels_cl", ident); s["ref"] = ref
    return s


def _gravadas(parte, ident):
    """previsões já gravadas por etapas anteriores, para a conferência bit a bit"""
    nome = lambda pasta, n: E / pasta / "preds" / n                            # noqa: E731
    seguro = "".join(c if c.isalnum() else "_" for c in str(ident))
    if parte == "e20":
        f = nome("LEBRE-V0.56-DEV-01", f"e20__{ident[0]}__{ident[1]}.npz")
        return {k: v for k, v in np.load(f).items() if k in REF}
    if parte in ("P", "DA"):
        Z = np.load(nome("LEBRE-V0.56-DEV-01", f"{parte}__{seguro}.npz"))
        return {k: Z[k] for k in REF if k in Z}
    if parte == "DB":
        out = {"A": np.load(nome("LEBRE-V0.56-DIAG-01", f"B__{ident}.npz"))["L0"]}
        Z = np.load(nome("LEBRE-V0.56-DEV-01", f"DB__{ident}.npz")); out["C5"] = Z["C5"]
        return out
    if parte in ("ONSD", "ONSR"):
        Z = np.load(nome("LEBRE-V0.56-DEV-01", f"{parte}__{seguro}.npz"))
        return {k: Z[k] for k in ("A", "C5")}
    Z = np.load(nome("LEBRE-V0.56-DIAG-03", f"CLV__{ident}.npz"))
    return {k: Z[k] for k in REF if k in Z}


def job(arg):
    parte, ident, variantes = arg
    nome = f"e20__{ident[0]}__{ident[1]}" if parte == "e20" else f"{parte}__{''.join(c if c.isalnum() else '_' for c in str(ident))}"
    base = OUT / nome
    if base.with_suffix(".json").exists():
        return nome, "já feito"
    try:
        t0 = time.time(); proto()
        import dev2_modelos as M
        s = _serie(parte, ident)
        prev, info = {}, {}
        for v in variantes:
            prev[v], info[v] = M.rodar(v, s, s["ref"])
        grav = _gravadas(parte, ident)
        conf = {k: bool(np.array_equal(prev[k], grav[k], equal_nan=True)) for k in grav if k in prev}
        if parte == "e20":
            prev.update(grav)
        info["_"] = dict(parte=parte, ident=list(ident) if parte == "e20" else str(ident), T=len(s["y"]), conferencia=conf,
                         origem=s.get("origem"))
        np.savez_compressed(base.with_suffix(".npz"), y=s["y"], **prev)
        base.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, default=str) + "\n", encoding="utf-8", newline="\n")
        return nome, f"ok {round(time.time() - t0)}s conferência {conf}"
    except Exception:
        return nome, "ERRO " + traceback.format_exc()[-900:]


def tarefas(modo):
    if modo == "e20":
        import dev_dados as DD
        E20, _ = DD.e20()
        return [("e20", (fam, k), DIN) for fam in E20.TODAS for k in range(len(list(E20._series(fam))))]
    import dados_v056 as D
    import dev_dados as DD
    import diag_dados as DG
    P = DD.predios(); C, _ = DG.conjuntos(); O = DD.rios_ons()
    todas = REF + DIN + SENS
    t = [("P", m, todas) for m in P["P"]] + [("DA", g, todas) for g in C["A"]] + [("DB", g, todas) for g in C["B"]]
    t += [("CLV", g, todas) for f, g in D.series("validacao") if f == "camels_cl"]
    t += [(k, r, todas) for k in ("ONSD", "ONSR") for r in O[k]]
    return t


if __name__ == "__main__":
    modo = sys.argv[1]
    assert modo in ("e20", "resto")
    OUT.mkdir(exist_ok=True)
    ts = tarefas(modo)
    print(len(ts), "tarefas", flush=True)
    with ProcessPoolExecutor(int(os.environ.get("PROCS", "14"))) as ex:
        for nome, st in ex.map(job, ts, chunksize=1):
            print(nome, st, flush=True)
