"""reserva_v053.py — trava contra o uso acidental da reserva da avaliação final da v0.53 (SPLIT_RULES.md, regra 4.1).

Todo carregador de dados do desenvolvimento da v0.53 chama recusar_se_reservado(...) antes de ler uma série. Só a
execução final pré-registrada passa final=True.
"""
import json
from pathlib import Path

import pandas as pd

_SPLIT = json.loads((Path(__file__).resolve().parent / "SPLIT_V053.json").read_text(encoding="utf-8"))
INICIO_CARGA = pd.Timestamp(_SPLIT["carga"]["periodo"][0])

RESERVADAS = {
    "camels_br": {int(g) for g in _SPLIT["camels_br"]["reservadas"]},
    "bdg2": set(_SPLIT["bdg2"]["reservadas"]),
    "solar": {u["nome"] for u in _SPLIT["solar"]["reservadas"]},
    "eolica": {u["nome"] for u in _SPLIT["eolica"]["reservadas"]},
    "cambio": set(_SPLIT["cambio"]["pares"]),
}


class SerieReservada(RuntimeError):
    pass


def recusar_se_reservado(familia, ident=None, ate=None, final=False):
    """Levanta SerieReservada se (familia, ident) pertence à reserva, ou se a carga pede dados a partir de 2026.

    familia: camels_br | bdg2 | solar | eolica | cambio | carga; ident: id da série; ate: última data pedida (carga).
    """
    if final:
        return
    if familia == "carga":
        if ate is not None and pd.Timestamp(ate) >= INICIO_CARGA:
            raise SerieReservada(f"carga a partir de {INICIO_CARGA.date()} é reservada para a avaliação final")
        return
    if ident is not None and (int(ident) if familia == "camels_br" else ident) in RESERVADAS[familia]:
        raise SerieReservada(f"{familia}:{ident} é reservada para a avaliação final da v0.53")
