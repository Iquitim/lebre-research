"""ensaio_v054.py — ensaio da avaliação final da v0.54 em séries JÁ GASTAS, no formato de cada família, antes de qualquer
acesso à reserva da v0.54 (PREREG_V054_FINAL.md, seção 7). Usa exatamente final_run.processar e final_analise.main.

Séries (todas já usadas na avaliação final da v0.53 ou no LEBRE Lab):
  camels, bdg2   as 3 primeiras bacias e os 3 primeiros medidores da reserva da v0.53
  eolica         2 usinas da reserva da v0.53 (ONS 2024-2025; tempo em data/external_v053)
  solar          2 usinas da reserva da v0.53, 2024-2025 (a reserva da v0.54 é 2026)
  niveis         taxa nominal de 1 ano do Tesouro (usada no Lab, C04), com as entradas da família, a partir de cópias
                 baixadas à parte (pasta dada no argumento), nunca dos arquivos da reserva
Uso: LEBRE054_PROTO=... python ensaio_v054.py <pasta_niveis> <pasta_saida>
"""
import json
import os
import sys

import final_dados as FD
import final_run as FR

SPLIT53 = json.load(open(os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.53-DATA-01", "SPLIT_V053.json"), encoding="utf-8"))
SNAP53 = FD.SNAP53


def series_ensaio(pasta_niveis):
    out = []
    for g in SPLIT53["camels_br"]["reservadas"][:3]:
        out.append(("camels", str(g), lambda g=g: FD.F53.v052(f"camels:{g}", final=True)))
    for m in SPLIT53["bdg2"]["reservadas"][:3]:
        out.append(("bdg2", m, lambda m=m: FD.F53.v052(f"bdg2:{m}", final=True)))
    ons = sorted(os.path.join(SNAP53, "ons_fator", f) for f in os.listdir(os.path.join(SNAP53, "ons_fator")))
    for tipo in ("eolica", "solar"):
        for u in SPLIT53[tipo]["reservadas"][:2]:
            arq = os.path.join(SNAP53, "open_meteo", f"{tipo}_{FD._seguro(u['nome'])}.json")
            out.append((tipo, u["nome"], lambda t=tipo, n=u["nome"], a=arq: FD.usina(t, n, ons, a, FD.HORAS_EOLICA)))

    def ler(chave):
        return FD.ler_nivel(chave, snap=pasta_niveis)
    out.append(("niveis", "tesouro:nominal:1 Yr", lambda: FD.nivel("tesouro:nominal:1 Yr", ler=ler)))
    return out


if __name__ == "__main__":
    pasta_niveis, saida = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(saida, "preds"), exist_ok=True)
    lista = []
    for fam, ident, carregar in series_ensaio(pasta_niveis):
        s = carregar()
        s["zero_baseline"] = False
        FD.conferir(s, fam, passos=fam != "solar")
        base = os.path.join(saida, "preds", f"{fam}__{FD._seguro(str(ident))}")
        print(fam, ident, FR.processar(s, fam, ident, base), flush=True)
        lista.append((fam, ident))
    json.dump(lista, open(os.path.join(saida, "lista.json"), "w", encoding="utf-8"), ensure_ascii=False)
