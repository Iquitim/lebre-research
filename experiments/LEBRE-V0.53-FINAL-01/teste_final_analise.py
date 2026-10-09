"""teste_final_analise.py — roda final_run (mecanismo) e final_analise numa pasta temporária com 2 séries NÃO
reservadas (solar B01 usina 0 do Lab e uma bacia de desenvolvimento da v0.52), com um Chronos falso, para conferir que a
análise roda de ponta a ponta. Nenhum dado da reserva é lido.
Uso: LEBRE_LAB=... LEBRE053_PROTO=... python teste_final_analise.py <pasta temporária>"""
import glob
import json
import os
import sys

import numpy as np

import final_analise as FA
import final_dados as FD
import final_run as FR

LAB = os.environ["LEBRE_LAB"]
sys.path.insert(0, LAB)
from lab import fontes as F  # noqa: E402
from lab.run import load  # noqa: E402

base = sys.argv[1]
os.makedirs(os.path.join(base, "preds"), exist_ok=True)
os.makedirs(os.path.join(base, "chronos"), exist_ok=True)
mod = load(os.path.join(LAB, "scenarios", "B", "B01_solar.py"))
u = mod.escolher(mod.TIPO)[0]
fn = f"{u['lat']:.4f}_{u['lon']:.4f}_2024-01-01_2025-12-31_{'-'.join(FD.VARS_SOLAR)}_America-Sao_Paulo.json"
ons = sorted(glob.glob(os.path.join(LAB, "dados", "ons", "fator-capacidade-2", "*.csv")))
s1 = FD.usina("solar", u["nome"], ons, os.path.join(F.CACHE, "open_meteo", fn)); s1["zero_baseline"] = False
s2 = FD.v052("camels:17350000", final=False)
L53 = FR._proto()
sys.path.insert(0, os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.52-PROTO-01")); sys.path.insert(0, FD.RAIZ)
import comp_dev as C  # noqa: E402
lista = []
for fam, ident, s in (("solar", u["nome"], s1), ("camels", "17350000", s2)):
    s["X"], s["y"] = s["X"][:6000], s["y"][:6000]
    if s["quarantine"] is not None:
        s["quarantine"] = s["quarantine"][:6000]
    qu = s["quarantine"]
    f53, f52, fr, info = FR._modelos(L53, s, s["X"], s["y"], qu)
    n = 360
    c53, c52, cr, ci = FR._modelos(L53, s, s["X"][:n], s["y"][:n], qu[:n] if qu is not None else None)
    fs, ok, inf = C.run_airline_x(s["y"], C._scaled_inputs(s["X"]), s["season"])
    nome = os.path.join(base, "preds", f"{fam}__{FD._seguro(ident)}")
    np.savez_compressed(nome + ".npz", y=s["y"], v053=f53, v052=f52, ref=fr, sarimax=fs, curta_y=s["y"][:n],
                        curta_v053=c53, curta_v052=c52, curta_ref=cr)
    json.dump(dict(familia=fam, ident=ident, nome=s["nome"], T=len(s["y"]), d=int(s["X"].shape[1]), season=s["season"],
                   season2=s["season2"], referencia=FD.referencia(s), entradas=s["entradas"], info=info, info_curta=ci,
                   sarimax_ok=bool(ok), sarimax_info=str(inf)), open(nome + ".json", "w", encoding="utf-8"), default=str)
    idx = np.flatnonzero(np.isfinite(s["y"]))[-1000:]
    np.savez_compressed(os.path.join(base, "chronos", f"{fam}__{FD._seguro(ident)}.npz"), idx=idx,
                        CHRONOS2_COV=s["y"][idx] + 0.1)
    lista.append((fam, ident))
FA.main(base=base, lista=lista)
print("teste de ponta a ponta passou")
