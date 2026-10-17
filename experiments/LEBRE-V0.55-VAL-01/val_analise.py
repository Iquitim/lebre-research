#!/usr/bin/env python3
"""val_analise.py — critérios V-a, V-b e V-c do PREREG_V055_VAL.md a partir de preds/. Grava VAL_RESULTADO.json."""
import json
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
B_REP, SEMENTE = 2000, 2026102210
BLOCO = {"camels": 20, "bdg2": 168}
FAM = ("camels", "bdg2")


def par_bootstrap(y, a, b, ini, L, rng):
    """razão MSE(a) ÷ MSE(b) e réplicas em log por blocos móveis pareados (a regra do E20 / T10)"""
    ok = np.isfinite(y) & np.isfinite(a) & np.isfinite(b); ok[:ini] = False
    la, lb = np.where(ok, (y - a) ** 2, 0.0), np.where(ok, (y - b) ** 2, 0.0)
    ponto = la[ok].sum() / lb[ok].sum()
    ca, cb = np.r_[0, np.cumsum(la[ini:])], np.r_[0, np.cumsum(lb[ini:])]
    n = len(la) - ini; m = n // L
    st = rng.integers(0, n - L + 1, size=(B_REP, m))
    with np.errstate(divide="ignore", invalid="ignore"):
        rep = np.log((ca[st + L] - ca[st]).sum(1) / (cb[st + L] - cb[st]).sum(1))
    return float(ponto), rep


def main():
    res = {"familias": {}, "series": []}
    nan_total, custos = 0, []
    for fi, fam in enumerate(FAM):
        arqs = sorted((AQUI / "preds").glob(f"{fam}__*.json"))
        reps, logs = [], []
        for k, arq in enumerate(arqs):
            meta = json.loads(arq.read_text(encoding="utf-8")); Z = np.load(arq.with_suffix(".npz"))
            y, a, b = Z["y"], Z["A"], Z["B10"]; ini = int(0.2 * len(y))
            nan = int((np.isfinite(y) & np.isfinite(a) & ~np.isfinite(b))[ini:].sum()); nan_total += nan
            p, rep = par_bootstrap(y, b, a, ini, BLOCO[fam], np.random.default_rng([SEMENTE, fi, k]))
            reps.append(rep); logs.append(math.log(p))
            cr = meta["info"]["B10"]["custo"] / meta["info"]["A"]["custo"]; custos.append(cr)
            res["series"].append(dict(familia=fam, ident=meta["ident"], razao=p, custo_razao=cr, nan=nan,
                                      externas_A=meta["info"]["A"]["externas_final"],
                                      externas_B10=meta["info"]["B10"]["externas_final"], wI=meta["info"]["B10"]["wI"],
                                      wS_A=meta["info"]["A"]["wS"]))
        rr = np.vstack(reps).mean(0); rr = rr[np.isfinite(rr)]
        res["familias"][fam] = dict(n=len(arqs), geo=float(np.exp(np.mean(logs))),
                                    ic95=[float(np.exp(np.quantile(rr, 0.025))), float(np.exp(np.quantile(rr, 0.975)))])
    res["criterios"] = {"V-a": all(f["ic95"][1] <= 1.02 for f in res["familias"].values()),
                        "V-b": nan_total == 0, "V-c": float(np.median(custos)) <= 1.25,
                        "custo_mediana": float(np.median(custos)), "nan": nan_total}
    res["criterios"]["PASSA"] = all(res["criterios"][k] for k in ("V-a", "V-b", "V-c"))
    (AQUI / "VAL_RESULTADO.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                             newline="\n")
    print(json.dumps(dict(familias=res["familias"], criterios=res["criterios"]), indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
