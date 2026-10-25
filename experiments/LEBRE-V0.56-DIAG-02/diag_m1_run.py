#!/usr/bin/env python3
"""diag_m1_run.py — execuções do diagnóstico da M1 (PLANO_DIAG_M1.md, §3). Grava preds/<conjunto>__<id>.npz e .json
(fora do git). Em cada bacia, confere que M0 reproduz bit a bit a previsão L0 gravada pelo DIAG-01.
Uso: LEBRE055_PROTO=<worktree b0522a0>/experiments/LEBRE-V0.55-PROTO-01 python diag_m1_run.py {A|B} [variantes...]
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
D1 = AQUI.parent / "LEBRE-V0.56-DIAG-01"
OUT = AQUI / "preds"
COMMIT = "b0522a0"
TODAS = ("M0", "M1", "M2", "M3", "M4", "M5")
GRAVAR = ("M0", "M5")


def proto():
    p = os.environ["LEBRE055_PROTO"]
    head = subprocess.run(["git", "-C", p, "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    sujo = subprocess.run(["git", "-C", p, "status", "--porcelain", "--", "."], capture_output=True, text=True).stdout.strip()
    if head != COMMIT or sujo:
        raise SystemExit(f"protótipo errado ou alterado: {head} {sujo}")


def job(arg):
    conj, gid, variantes = arg
    base = OUT / f"{conj}__{gid}"
    try:
        t0 = time.time(); proto()
        for p in (str(D1), str(AQUI)):
            if p not in sys.path:
                sys.path.insert(0, p)
        import diag_dados as DD
        import diag_m1 as M
        s = DD.carregar(gid)
        novo, _ = M.classes()
        old = dict(np.load(base.with_suffix(".npz"))) if base.with_suffix(".npz").exists() else {}
        info = json.loads(base.with_suffix(".json").read_text(encoding="utf-8")) if base.with_suffix(".json").exists() else {}
        prev = {k: v for k, v in old.items() if k != "y"}
        for v in variantes:
            m = novo(v)
            f, G = M.rodar(m, s, gravar=v in GRAVAR)
            prev[v] = f
            if G is not None:
                for k, a in G.items():
                    prev[f"{v}_{k}"] = a
            info[v] = dict(custo=m.cost_per_step, estrutura=m.structure, m1_entradas=m.layer_weights["m1_inputs"],
                           dormencia=getattr(m._m1, "sleeps", None))
            if v == "M0":
                L0 = np.load(D1 / "preds" / f"{conj}__{gid}.npz")["L0"]
                info["M0_igual_L0_diag01"] = bool(np.array_equal(f, L0, equal_nan=True))
                assert info["M0_igual_L0_diag01"], "M0 difere de L0 do DIAG-01"
        np.savez_compressed(base.with_suffix(".npz"), y=s["y"], **prev)
        info["_"] = dict(conjunto=conj, pos=s["pos"], T=len(s["y"]))
        base.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, default=str) + "\n", encoding="utf-8",
                                             newline="\n")
        return arg[:2], f"ok {round(time.time() - t0)}s"
    except Exception:
        return arg[:2], "ERRO " + traceback.format_exc()[-900:]


if __name__ == "__main__":
    conj = sys.argv[1]
    assert conj in ("A", "B")
    variantes = tuple(sys.argv[2:]) or TODAS
    assert set(variantes) <= set(TODAS) and "M0" in variantes, variantes
    sys.path.insert(0, str(D1))
    import diag_dados as DD
    C, _ = DD.conjuntos()
    OUT.mkdir(exist_ok=True)
    tarefas = [(conj, g, variantes) for g in C[conj]]
    print(len(tarefas), "bacias", variantes, flush=True)
    with ProcessPoolExecutor(14) as ex:
        for t, st in ex.map(job, tarefas, chunksize=1):
            print(t, st, flush=True)
