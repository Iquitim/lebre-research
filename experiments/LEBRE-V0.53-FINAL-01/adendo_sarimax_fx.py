"""adendo_sarimax_fx.py — SARIMAX com entradas no câmbio, com as entradas preenchidas (ADENDO_SARIMAX_FX_PLANO.md).
Só referência. Uso: python adendo_sarimax_fx.py"""
import json
import math
import os
import sys

import numpy as np

import final_dados as FD

sys.path.insert(0, os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, FD.RAIZ)
import comp_dev as C  # noqa: E402
import data_v052 as D  # noqa: E402

OUT = os.path.join(FD.AQUI, "adendo_sarimax_fx")


def main():
    os.makedirs(OUT, exist_ok=True)
    linhas = {}
    for familia, ident in FD.tarefas():
        if not familia.startswith("fx_"):
            continue
        base = f"{familia}__{FD._seguro(ident)}"
        s = FD.carregar(familia, ident)
        y = s["y"]
        Xf, _ = D._ffill_inputs(s["X"])
        fs, ok, info = C.run_airline_x(y, C._scaled_inputs(Xf), s["season"])
        np.savez_compressed(os.path.join(OUT, base + ".npz"), sarimax=fs)
        a = np.load(os.path.join(FD.AQUI, "preds", base + ".npz"))
        ini = int(0.2 * len(y))
        r = {}
        for nome in ("v053", "v052"):
            f = a[nome]
            m = np.isfinite(y) & np.isfinite(fs) & np.isfinite(f)
            m[:ini] = False
            r[nome] = float(np.sum((y[m] - fs[m]) ** 2) / np.sum((y[m] - f[m]) ** 2)) if ok and m.any() else None
        linhas.setdefault(familia, []).append(dict(serie=s["nome"], ok=bool(ok), info=str(info), **r))
        print(familia, s["nome"], ok, {k: (round(v, 4) if v else v) for k, v in r.items()}, flush=True)
    json.dump(linhas, open(os.path.join(FD.AQUI, "adendo_sarimax_fx.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    gm = lambda v: f"{math.exp(np.mean(np.log(v))):.3f}" if v else "-"
    L = ["# Adendo: SARIMAX com entradas no câmbio, entradas preenchidas (resultado)", "",
         "Plano `ADENDO_SARIMAX_FX_PLANO.md`. Só referência; a decisão da avaliação final não muda.", "",
         "| Família | séries ok | SARIMAX-X ÷ v0.53 (geo) | SARIMAX-X ÷ v0.52 (geo) |", "|---|---|---|---|"]
    for fam, ls in linhas.items():
        ok = [x for x in ls if x["ok"] and x["v053"]]
        L.append(f"| {fam} | {len(ok)} de {len(ls)} | {gm([x['v053'] for x in ok])} | {gm([x['v052'] for x in ok])} |")
    open(os.path.join(FD.AQUI, "ADENDO_SARIMAX_FX_RESULTADO.md"), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
