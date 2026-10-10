"""reserva_v054.py — trava contra o uso acidental da reserva da avaliação final da v0.54 (SPLIT_RULES.md, regra 4.1).

Todo carregador de dados do desenvolvimento da v0.54 chama recusar_se_reservado(...) antes de ler uma série. Só a
execução final pré-registrada passa final=True.
"""
import json
from pathlib import Path

import pandas as pd

_SPLIT = json.loads((Path(__file__).resolve().parent / "SPLIT_V054.json").read_text(encoding="utf-8"))
INICIO_SOLAR = pd.Timestamp(_SPLIT["solar"]["periodo"][0])

RESERVADAS = {
    "camels_br": {int(g) for g in _SPLIT["camels_br"]["reservadas"]},
    "bdg2": set(_SPLIT["bdg2"]["reservadas"]),
    "eolica": {u["nome"] for u in _SPLIT["eolica"]["reservadas"]},
    "niveis": set(_SPLIT["niveis"]["reservadas"]),
}


class SerieReservada(RuntimeError):
    pass


def recusar_se_reservado(familia, ident=None, ate=None, final=False):
    """Levanta SerieReservada se (familia, ident) pertence à reserva, ou se a solar pede dados a partir de 2026.

    familia: camels_br | bdg2 | eolica | solar | niveis; ident: id da série; ate: última data pedida (solar: qualquer
    usina, porque a reserva solar é uma separação no tempo).
    """
    if final:
        return
    if familia == "solar":
        if ate is not None and pd.Timestamp(ate) >= INICIO_SOLAR:
            raise SerieReservada(f"solar a partir de {INICIO_SOLAR.date()} é reservada para a avaliação final da v0.54")
        return
    if ident is not None and (int(ident) if familia == "camels_br" else ident) in RESERVADAS[familia]:
        raise SerieReservada(f"{familia}:{ident} é reservada para a avaliação final da v0.54")
