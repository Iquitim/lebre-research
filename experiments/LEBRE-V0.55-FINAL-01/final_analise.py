#!/usr/bin/env python3
"""final_analise.py — regra de promoção da v0.55 (PREREG_V055_FINAL.md, §3) a partir de preds/. Grava
FINAL_RESULTADO.json e FINAL_RESULTADO.md."""
import importlib.util
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
FAMILIAS = ["camels", "bdg2", "eolica", "solar", "niveis_ecb"]
BLOCO = {"camels": 30, "bdg2": 168, "eolica": 168, "solar": 168, "niveis_ecb": 20}
B_REP, SEMENTE = 2000, 2026102600
RAM_LIMITE = 128 * 1024


def par_bootstrap(y, a, b, ini, L, rng, fim=None):
    """razão MSE(a) ÷ MSE(b) e réplicas em log por blocos móveis pareados (a regra do E20, do T10 e da validação)"""
    fim = len(y) if fim is None else min(fim, len(y))
    y, a, b = y[:fim], a[:fim], b[:fim]
    ok = np.isfinite(y) & np.isfinite(a) & np.isfinite(b); ok[:ini] = False
    la, lb = np.where(ok, (y - a) ** 2, 0.0), np.where(ok, (y - b) ** 2, 0.0)
    ponto = la[ok].sum() / lb[ok].sum()
    ca, cb = np.r_[0, np.cumsum(la[ini:])], np.r_[0, np.cumsum(lb[ini:])]
    n = len(la) - ini; m = max(n // L, 1)
    st = rng.integers(0, n - L + 1, size=(B_REP, m))
    with np.errstate(divide="ignore", invalid="ignore"):
        rep = np.log((ca[st + L] - ca[st]).sum(1) / (cb[st + L] - cb[st]).sum(1))
    return float(ponto), rep


def cp_sup(x, n, a=0.05):
    if x >= n:
        return 1.0
    lo, hi = x / n, 1.0
    for _ in range(80):
        p = (lo + hi) / 2
        cdf = sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x + 1))
        lo, hi = (p, hi) if cdf > a / 2 else (lo, p)
    return (lo + hi) / 2


def ram(d_max):
    """estimativa da v0.54 (LEBRE-V0.54-FINAL-01/final_analise.ram_estimada, sem alteração) mais o estado novo do núcleo
    ancorado, 8 bytes por número: base_s e base_i (2·(d+2)); pesos da estrutura de inovação (até 4 unidades × 6);
    atributos da memória na estrutura (3 vetores de até 7); escalares (Di, wI, d_sm, d_sv, n_d, res_prev_int,
    last_change: 7)"""
    sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.54-FINAL-01"))
    sp = importlib.util.spec_from_file_location("final_analise_v054", RAIZ / "experiments" / "LEBRE-V0.54-FINAL-01" / "final_analise.py")
    A54 = importlib.util.module_from_spec(sp)
    cwd = os.getcwd(); os.chdir(RAIZ / "experiments" / "LEBRE-V0.54-FINAL-01")
    try:
        sp.loader.exec_module(A54)
        r54, info = A54.ram_estimada(d_max)
    finally:
        os.chdir(cwd)
    novos = 2 * (d_max + 2) + 4 * 6 + 3 * 7 + 7
    return r54 + 8 * novos, dict(info, numeros_v055=novos)


def main():
    res = {"familias": {}, "series": []}
    nan, custos, pl = 0, [], {"A": 0, "B10": 0}
    d_max = 0
    for fi, fam in enumerate(FAMILIAS):
        arqs = sorted((AQUI / "preds").glob(f"{fam}__*.json"))
        reps, logs, reps_c, logs_c = [], [], [], []
        for k, arq in enumerate(arqs):
            meta = json.loads(arq.read_text(encoding="utf-8")); Z = np.load(arq.with_suffix(".npz"))
            y = Z["y"]; ini = int(0.2 * len(y)); d_max = max(d_max, meta["d"] + 2)
            for a_, b_ in (("A", "B10"), ("A_pl", "B10_pl")):
                nan += int((np.isfinite(y) & np.isfinite(Z[a_]) & ~np.isfinite(Z[b_]))[ini:].sum())
            rng = np.random.default_rng([SEMENTE, fi, k])
            p, rep = par_bootstrap(y, Z["B10"], Z["A"], ini, BLOCO[fam], rng)
            pc, repc = par_bootstrap(y, Z["B10"], Z["A"], 200, 24 if BLOCO[fam] == 168 else 20, rng, fim=2000)
            reps.append(rep); logs.append(math.log(p)); reps_c.append(repc); logs_c.append(math.log(pc))
            I = meta["info"]; cr = I["B10"]["custo"] / I["A"]["custo"]; custos.append(cr)
            plv = {v: any(u in meta["placebo"] for u in I[v + "_pl"]["externas_final"]) for v in ("A", "B10")}
            for v in pl:
                pl[v] += plv[v]
            res["series"].append(dict(familia=fam, ident=meta["ident"], razao=p, razao_curta=pc, custo_razao=cr,
                                      externas_A=I["A"]["externas_final"], externas_B10=I["B10"]["externas_final"],
                                      placebo_A=plv["A"], placebo_B10=plv["B10"], wI=I["B10"]["wI"]))
        rr = np.vstack(reps).mean(0); rr = rr[np.isfinite(rr)]
        rc = np.vstack(reps_c).mean(0); rc = rc[np.isfinite(rc)]
        ss = [s for s in res["series"] if s["familia"] == fam]
        res["familias"][fam] = dict(n=len(arqs), geo=float(np.exp(np.mean(logs))),
                                    ic95=[float(np.exp(np.quantile(rr, 0.025))), float(np.exp(np.quantile(rr, 0.975)))],
                                    curta_geo=float(np.exp(np.mean(logs_c))),
                                    curta_ic95=[float(np.exp(np.quantile(rc, 0.025))), float(np.exp(np.quantile(rc, 0.975)))],
                                    externas_A=sum(bool(s["externas_A"]) for s in ss), externas_B10=sum(bool(s["externas_B10"]) for s in ss),
                                    placebo_A=sum(s["placebo_A"] for s in ss), placebo_B10=sum(s["placebo_B10"] for s in ss),
                                    inovacao_ativa=sum(s["wI"] > 0.5 for s in ss))
    n_tot = len(res["series"])
    ram_b, ram_info = ram(d_max)
    cr = {"R1": all(f["ic95"][1] <= 1.02 for f in res["familias"].values()),
          "R2": cp_sup(pl["B10"], n_tot) <= 0.10 and pl["B10"] <= pl["A"],
          "R2_placebo": dict(A=pl["A"], B10=pl["B10"], n=n_tot, B10_sup=cp_sup(pl["B10"], n_tot), A_sup=cp_sup(pl["A"], n_tot)),
          "R3": nan == 0, "R3_nan": nan,
          "R4": float(np.median(custos)) <= 1.25, "R4_mediana": float(np.median(custos)),
          "R5": ram_b <= RAM_LIMITE, "R5_bytes": ram_b, "R5_info": ram_info}
    cr["PROMOVIDA"] = all(cr[k] for k in ("R1", "R2", "R3", "R4", "R5"))
    res["criterios"] = cr
    (AQUI / "FINAL_RESULTADO.json").write_text(json.dumps(res, indent=1, ensure_ascii=False, default=str) + "\n",
                                               encoding="utf-8", newline="\n")
    print(json.dumps(dict(familias=res["familias"], criterios=cr), indent=1, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()
