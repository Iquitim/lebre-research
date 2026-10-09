"""ensaio_v052.py — ensaio geral da v0.53 em bacias e prédios já gastos pela v0.52 (ENSAIO_PLANO.md, item 2).
Uso: LEBRE053_PROTO=<worktree>/experiments/LEBRE-V0.53-PROTO-01 python ensaio_v052.py"""
import json
import os
import sys
import traceback
from concurrent.futures import ProcessPoolExecutor

import numpy as np

import final_dados as FD
import final_run as FR

sys.path.insert(0, os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.53-DATA-01"))
from reserva_v053 import recusar_se_reservado  # noqa: E402


def tarefas():
    import data_v052 as D
    r2 = json.load(open(os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.52-HELDOUT-02", "RESERVA2.json"), encoding="utf-8"))
    dev = [t for t in D.dev_tasks() if t.startswith(("camels:", "bdg2:"))]
    return [("dev", t) for t in dev] + [("reserva2_v052", f"camels:{g}") for g in r2["camels_br"]] + \
           [("reserva2_v052", f"bdg2:{m}") for m in r2["bdg2"]]


def job(item):
    origem, t = item
    try:
        fam = "camels" if t.startswith("camels:") else "bdg2"
        recusar_se_reservado("camels_br" if fam == "camels" else "bdg2", t.split(":", 1)[1])
        s = FD.v052(t, final=True)
        FD.conferir(s, fam)
        f53, f52, fr, info = FR._modelos(FR._proto(), s, s["X"], s["y"], s["quarantine"])
        y = s["y"]
        ini = int(0.2 * len(y))
        nan = int((np.isfinite(y) & ~np.isfinite(f53))[ini:].sum())
        ok = np.isfinite(y) & np.isfinite(f53) & np.isfinite(f52)
        ok[:ini] = False
        razao = float(np.sum((y[ok] - f53[ok]) ** 2) / np.sum((y[ok] - f52[ok]) ** 2))
        return dict(origem=origem, tarefa=t, T=len(y), nan=nan, razao=razao,
                    acrescimo=info["custo_v053"] - info["custo_v052"], estrutura=info["estrutura_identica"], erro=None)
    except Exception:
        return dict(origem=origem, tarefa=t, erro=traceback.format_exc()[-600:])


if __name__ == "__main__":
    FR._proto()
    ts = tarefas()
    with ProcessPoolExecutor(14) as ex:
        R = list(ex.map(job, ts, chunksize=1))
    json.dump(R, open(os.path.join(FD.AQUI, "ensaio_v052.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    erros = [r for r in R if r["erro"]]
    ok = [r for r in R if not r["erro"]]
    print(f"séries: {len(R)}; erros: {len(erros)}; com NaN: {sum(r['nan'] > 0 for r in ok)}; "
          f"acréscimo > 1100: {sum(r['acrescimo'] > 1100 for r in ok)}; estrutura diferente: {sum(not r['estrutura'] for r in ok)}")
    for r in erros:
        print("ERRO", r["tarefa"], r["erro"][-300:])
    for fam in ("camels", "bdg2"):
        v = [r["razao"] for r in ok if r["tarefa"].startswith(fam)]
        a = [r["acrescimo"] for r in ok if r["tarefa"].startswith(fam)]
        if v:
            print(f"{fam}: v0.53 ÷ v0.52 geo {np.exp(np.mean(np.log(v))):.3f} (mín {min(v):.3f}, máx {max(v):.3f}); "
                  f"acréscimo de custo mediana {np.median(a):.0f}, máx {max(a):.0f}")
