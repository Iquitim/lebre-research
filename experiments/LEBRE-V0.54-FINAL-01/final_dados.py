"""final_dados.py — tarefas da avaliação final da v0.54 na reserva (PREREG_V054_FINAL.md, seção 3).

Reserva: experiments/LEBRE-V0.54-DATA-01 (SPLIT_V054.json; arquivos brutos em data/external_v054, fora do git; a eólica
usa os arquivos do ONS de 2024-2025 já registrados em data/external_v053/ons_fator). Cada família reproduz a construção
do desenvolvimento:
  camels, bdg2   como na avaliação da v0.52/v0.53 (LEBRE-V0.52-PROTO-01/data_v052.py, quarentena das entradas
                 preenchidas); bdg2 com season 24 e season2 168
  eolica         como B06 do LEBRE Lab: geração verificada do ONS 2024-2025; ERA5 (Open-Meteo) no local: vento a 100 m
                 (velocidade, u, v), vento a 10 m, temperatura; season 24
  solar          como B01: geração verificada do ONS, 01/01 a 30/09/2026 (separação no tempo); ERA5: radiação global e
                 direta, nuvens, temperatura; season 24
  niveis         nível diário (dias úteis 2010-2025) dos 17 alvos da EIA e do Tesouro dos EUA; entradas com 1 dia útil
                 de atraso: WTI e Brent (EIA) e as taxas nominais de 2 e 10 anos do Tesouro; referência persistência
Funções auxiliares (serie, tempo, vento_uv, v052) vêm de LEBRE-V0.53-FINAL-01/final_dados.py, sem alteração. Os leitores
recebem caminhos, para serem testados em arquivos não reservados do mesmo formato (teste_final_dados.py).
"""
import importlib.util
import json
import os

import numpy as np
import pandas as pd

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
_spec = importlib.util.spec_from_file_location(                    # o módulo da v0.53 tem o mesmo nome deste
    "final_dados_v053", os.path.join(RAIZ, "experiments", "LEBRE-V0.53-FINAL-01", "final_dados.py"))
F53 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(F53)

SNAP = os.path.join(RAIZ, "data", "external_v054")
SNAP53 = os.path.join(RAIZ, "data", "external_v053")
SPLIT = json.load(open(os.path.join(RAIZ, "experiments", "LEBRE-V0.54-DATA-01", "SPLIT_V054.json"), encoding="utf-8"))

HORAS_EOLICA = pd.date_range("2024-01-01 00:00", "2025-12-31 23:00", freq="h")
HORAS_SOLAR = pd.date_range("2026-01-01 00:00", "2026-09-30 23:00", freq="h")
DIAS_NIV = pd.bdate_range("2010-01-01", "2025-12-31")
FAMILIAS = ["camels", "bdg2", "eolica", "solar", "niveis"]
ENTRADAS_NIV = ["eia:RWTC", "eia:RBRTE", "tesouro:nominal:2 Yr", "tesouro:nominal:10 Yr"]
serie, tempo, vento_uv = F53.serie, F53.tempo, F53.vento_uv


# ------------------------------------------------------------------ ONS: usinas
_GER = {}


def geracao_ons(arquivos, horas):
    """Como lab.usinas._tabela: geração verificada horária por usina/conjunto, na grade dada."""
    chave = (tuple(arquivos), str(horas[0]), str(horas[-1]))
    if chave not in _GER:
        df = pd.concat([pd.read_csv(a, sep=";", decimal=".") for a in arquivos], ignore_index=True)
        df["din_instante"] = pd.to_datetime(df["din_instante"])
        df = df[(df["din_instante"] >= horas[0]) & (df["din_instante"] <= horas[-1])]
        _GER[chave] = df.pivot_table(index="din_instante", columns="nom_usina_conjunto",
                                     values="val_geracaoverificada").reindex(horas)
    return _GER[chave]


def usina(tipo, nome, arquivos_ons, arq_tempo, horas):
    ger = geracao_ons(arquivos_ons, horas)[nome]
    if tipo == "solar":
        t = tempo(arq_tempo, F53.VARS_SOLAR)
    else:
        t = tempo(arq_tempo, F53.VARS_EOLICA)
        uu, vv = vento_uv(t["wind_speed_100m"], t["wind_direction_100m"])
        t = t.assign(vento100_u=uu, vento100_v=vv).drop(columns=["wind_direction_100m"])
    t = t[(t.index >= horas[0]) & (t.index <= horas[-1])]
    return serie(nome, ger, t, season=24)


# ------------------------------------------------------------------ níveis: EIA e Tesouro
def eia_xls(arq):
    """Planilha diária da EIA (hist_xls): aba 'Data 1', duas linhas de cabeçalho; data e valor."""
    df = pd.read_excel(arq, sheet_name="Data 1", skiprows=2)
    return pd.Series(pd.to_numeric(df.iloc[:, 1], errors="coerce").to_numpy(),
                     index=pd.to_datetime(df.iloc[:, 0])).sort_index()


def tesouro_csv(arquivos, coluna):
    """Curvas diárias do Tesouro dos EUA (um CSV por ano): a coluna pedida ('2 Yr', '5 YR', ...)."""
    partes = []
    for a in arquivos:
        df = pd.read_csv(a)
        if coluna in df.columns:
            partes.append(pd.Series(pd.to_numeric(df[coluna], errors="coerce").to_numpy(),
                                    index=pd.to_datetime(df["Date"], format="%m/%d/%Y")))
    s = pd.concat(partes).sort_index()
    return s[~s.index.duplicated()]


def ler_nivel(chave, snap=SNAP):
    fonte = chave.split(":")
    if fonte[0] == "eia":
        return eia_xls(os.path.join(snap, "eia", f"{fonte[1]}d.xls"))
    tipo, col = fonte[1], fonte[2]
    arqs = sorted(os.path.join(snap, "tesouro", f) for f in os.listdir(os.path.join(snap, "tesouro"))
                  if f.startswith(f"{tipo}_"))
    return tesouro_csv(arqs, col)


def nivel(alvo, ler=ler_nivel, dias=DIAS_NIV):
    cal = lambda s: s[~s.index.duplicated()].reindex(dias)            # noqa: E731
    ent = pd.DataFrame({k: cal(ler(k)) for k in ENTRADAS_NIV}).shift(1)
    s = serie(f"nivel_{alvo}", cal(ler(alvo)), ent, freq=None)
    s["zero_baseline"] = False
    return s


# ------------------------------------------------------------------ tarefas da reserva
def tarefas():
    t = [("camels", str(g)) for g in SPLIT["camels_br"]["reservadas"]]
    t += [("bdg2", m) for m in SPLIT["bdg2"]["reservadas"]]
    t += [("eolica", u["nome"]) for u in SPLIT["eolica"]["reservadas"]]
    t += [("solar", u["nome"]) for u in SPLIT["solar"]["reservadas"]]
    t += [("niveis", k) for k in SPLIT["niveis"]["reservadas"]]
    return t


def _seguro(nome):
    return "".join(c if c.isalnum() else "_" for c in nome)


def carregar(familia, ident):
    """Só na execução final pré-registrada."""
    if familia == "camels":
        s = F53.v052(f"camels:{ident}", final=True)
    elif familia == "bdg2":
        s = F53.v052(f"bdg2:{ident}", final=True)
    elif familia in ("solar", "eolica"):
        u = next(x for x in SPLIT[familia]["reservadas"] if x["nome"] == ident)
        pasta = os.path.join(SNAP, "ons_fator_2026") if familia == "solar" else os.path.join(SNAP53, "ons_fator")
        ons = sorted(os.path.join(pasta, f) for f in os.listdir(pasta))
        horas = HORAS_SOLAR if familia == "solar" else HORAS_EOLICA
        s = usina(familia, u["nome"], ons, os.path.join(SNAP, "open_meteo", f"{familia}_{_seguro(u['nome'])}.json"), horas)
        s["zero_baseline"] = False
    else:
        s = nivel(ident)
    s["familia"] = familia
    conferir(s, familia)
    return s


ESPERADO = {  # season, season2, d, passos (None = não fixo), referência
    "camels": (None, None, 3, None, "persistencia"),
    "bdg2": (24, 168, 2, None, "sazonal"),
    "eolica": (24, None, 5, len(HORAS_EOLICA), "sazonal"),
    "solar": (24, None, 4, len(HORAS_SOLAR), "sazonal"),
    "niveis": (None, None, 4, len(DIAS_NIV), "persistencia"),
}


def referencia(s):
    return "zero" if s.get("zero_baseline") else ("sazonal" if s.get("season") else "persistencia")


def conferir(s, familia, passos=True):
    season, season2, d, T, ref = ESPERADO[familia]
    assert s["season"] == season, (familia, "season", s["season"])
    assert s["season2"] == season2, (familia, "season2", s["season2"])
    assert s["X"].shape[1] == d, (familia, "d", s["X"].shape)
    assert len(s["y"]) == s["X"].shape[0], (familia, "tamanhos")
    if passos and T is not None:
        assert len(s["y"]) == T, (familia, "passos", len(s["y"]), T)
    assert referencia(s) == ref, (familia, "referência", referencia(s))
    assert np.isfinite(s["y"]).mean() > 0.5, (familia, "alvo quase todo faltante")
