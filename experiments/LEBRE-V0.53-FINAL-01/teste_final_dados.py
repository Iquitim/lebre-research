"""teste_final_dados.py — confere os leitores de final_dados.py contra a construção do LEBRE Lab, só com séries NÃO
reservadas no mesmo formato (nenhum dado da reserva é lido):
  solar e eólica: as usinas 0 de B01 e B06 do Lab, com os arquivos do ONS e do Open-Meteo do próprio Lab;
  carga: Sudeste em 2025 (B02 do Lab usa 2022-2025), arquivos do Lab;
  câmbio: o grupo de W-C01 a W-C03 do Lab (DEXINUS, DEXSIUS, DEXTHUS, DEXDNUS, 2010-2025), arquivos do Lab;
  camels e bdg2: uma tarefa de desenvolvimento da v0.52 (só forma e conferência).
Uso: LEBRE_LAB=<pasta do LEBRE Lab> python teste_final_dados.py
"""
import glob
import os
import sys

import numpy as np

import final_dados as FD

LAB = os.environ["LEBRE_LAB"]
sys.path.insert(0, LAB)
from lab import fontes as F  # noqa: E402
from lab.run import load  # noqa: E402


def igual(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return a.shape == b.shape and np.array_equal(a, b, equal_nan=True)


def lab_gerar(arq, i):
    return load(os.path.join(LAB, "scenarios", arq)).gerar(i)


def teste_usinas():
    ons = sorted(glob.glob(os.path.join(LAB, "dados", "ons", "fator-capacidade-2", "*.csv")))
    for tipo, arq, vars_ in (("solar", "B/B01_solar.py", FD.VARS_SOLAR), ("eolica", "B/B06_eolica.py", FD.VARS_EOLICA)):
        ref = lab_gerar(arq, 0)
        mod = load(os.path.join(LAB, "scenarios", arq))
        u = mod.escolher(mod.TIPO)[0]
        fn = f"{u['lat']:.4f}_{u['lon']:.4f}_2024-01-01_2025-12-31_{'-'.join(vars_)}_America-Sao_Paulo.json"
        s = FD.usina(tipo, u["nome"], ons, os.path.join(F.CACHE, "open_meteo", fn))
        FD.conferir(s, tipo)
        assert igual(s["y"], ref["y"]) and igual(s["X"], ref["X"]) and s["entradas"] == ref["entradas"], tipo
        print("ok", tipo, u["nome"], s["X"].shape)


def teste_carga():
    ref = lab_gerar("B/B02_carga_eletrica.py", 0)
    import pandas as pd
    horas = pd.date_range("2025-01-01 00:00", "2025-12-31 23:00", freq="h")
    arq_c = next(f for f in glob.glob(os.path.join(LAB, "dados", "ons", "curva-carga", "*.csv")) if "2025" in f)
    fn = next(f for f in glob.glob(os.path.join(LAB, "dados", "open_meteo", "-23.5500_-46.6300_2022-01-01_2025-12-31_*")))
    s = FD.carga("SUDESTE", arq_c, fn, horas=horas)
    FD.conferir(s, "carga", passos=False)
    i0 = int(np.searchsorted(pd.to_datetime(pd.date_range(ref["inicio"], ref["fim"], freq="h")), horas[0]))
    assert igual(s["y"], ref["y"][i0:i0 + len(horas)]) and igual(s["X"], ref["X"][i0:i0 + len(horas)]), "carga"
    print("ok carga SUDESTE 2025", s["X"].shape)


def teste_cambio():
    grupo = ["DEXINUS", "DEXSIUS", "DEXTHUS", "DEXDNUS"]
    arqs = {x: os.path.join(LAB, "dados", "fred", f"{x}.csv") for x in grupo + ["DGS2", "DGS10"]}
    for tipo, arq in (("fx_ret", "W/WC01_retornos.py"), ("fx_abs", "W/WC02_volatilidade.py"), ("fx_niv", "W/WC03_niveis.py")):
        for i, alvo in enumerate(grupo):
            ref = lab_gerar(arq, i)
            s = FD.cambio(tipo, alvo, grupo, arqs)
            FD.conferir(s, tipo)
            assert igual(s["y"], ref["y"]) and igual(s["X"], ref["X"]), (tipo, alvo)
            assert bool(s["zero_baseline"]) == bool(ref.get("zero_baseline")), (tipo, "referência")
        print("ok", tipo, s["X"].shape)


def teste_v052():
    import data_v052 as D
    for fam, tarefa in (("camels", next(t for t in D.dev_tasks() if t.startswith("camels:"))),
                        ("bdg2", next(t for t in D.dev_tasks() if t.startswith("bdg2:")))):
        s = FD.v052(tarefa, final=False)
        FD.conferir(s, fam)
        print("ok", fam, tarefa, s["X"].shape)


if __name__ == "__main__":
    teste_usinas()
    teste_carga()
    teste_cambio()
    teste_v052()
    print("todos os testes passaram")
