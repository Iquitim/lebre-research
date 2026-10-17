#!/usr/bin/env python3
"""comp_analise.py — estatística da comparação (COMP_PLANO.md, §3-4): razões MSE e MAE v0.55 ÷ modelo por família, IC
por bootstrap pareado de blocos móveis (média das réplicas em log das séries), p-valor bilateral pelas réplicas, Holm
por janela. Grava COMP_RESULTADO.json."""
import json
import math
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
FAM = ["camels", "bdg2", "eolica", "solar", "niveis_ecb"]
BLOCO = {"camels": 30, "bdg2": 168, "eolica": 168, "solar": 168, "niveis_ecb": 20}
COMPLETOS = ["V054", "REF", "ARX_NLMS", "NLINEAR_ONLINE", "DLINEAR_ONLINE", "ARX_RLS", "SARIMAX_X", "GBM"]
FUNDACAO = ["CHRONOS2_COV", "CHRONOS2", "CHRONOS_BOLT_SMALL", "TTM_ZS", "TTM_FT_EXOG"]
B_REP, SEMENTE, TEST_FRAC = 2000, 2026102700, 0.30


def reps(e_a, e_b, L, rng):
    """razão sum(e_a)/sum(e_b) e réplicas em log por blocos móveis pareados sobre as perdas já mascaradas"""
    n = len(e_a); L = max(1, min(L, n)); m = max(n // L, 1)
    ca, cb = np.r_[0, np.cumsum(e_a)], np.r_[0, np.cumsum(e_b)]
    st = rng.integers(0, n - L + 1, size=(B_REP, m))
    with np.errstate(divide="ignore", invalid="ignore"):
        r = np.log((ca[st + L] - ca[st]).sum(1) / (cb[st + L] - cb[st]).sum(1))
    return float(e_a.sum() / e_b.sum()), r


def holm(ps):
    ordem = sorted(range(len(ps)), key=lambda i: ps[i]); m = len(ps); sig = [False] * m
    for k, i in enumerate(ordem):
        if ps[i] <= 0.05 / (m - k):
            sig[i] = True
        else:
            break
    return sig


def carregar():
    S = []
    for fam in FAM:
        for arq in sorted((RAIZ / "experiments" / "LEBRE-V0.55-FINAL-01" / "preds").glob(f"{fam}__*.npz")):
            L = np.load(arq); C = np.load(AQUI / "preds" / arq.name); Fz = np.load(AQUI / "fundacao" / arq.name)
            meta = json.loads((AQUI / "preds" / arq.with_suffix(".json").name).read_text(encoding="utf-8"))
            y = L["y"]; prev = {"V055": L["B10"], "V054": L["A"]}
            prev.update({k: C[k] for k in COMPLETOS if k != "V054"})
            S.append(dict(familia=fam, nome=arq.stem, y=y, prev=prev, idx=Fz["idx"],
                          fund={k: Fz[k] for k in FUNDACAO}, falhas=[k for k, v in meta["info"].items() if not v.get("ok", True)]))
    return S


def comparar(S, janela):
    res, ps, chaves = {}, [], []
    modelos = COMPLETOS if janela == "completa" else COMPLETOS + FUNDACAO
    for fi, fam in enumerate(FAM):
        ss = [s for s in S if s["familia"] == fam]
        for mi, mod in enumerate(modelos):
            logs, rr, logs_mae, rr_mae, vit, n_ok = [], [], [], [], 0, 0
            for si, s in enumerate(ss):
                y = s["y"]
                if janela == "completa":
                    ok = np.isfinite(y); ok[: int(TEST_FRAC * len(y))] = False
                    for k in ["V055"] + COMPLETOS:
                        ok &= np.isfinite(s["prev"][k])
                    a, b = s["prev"]["V055"][ok], s["prev"][mod][ok]; yy = y[ok]; L = BLOCO[fam]
                else:
                    idx = s["idx"]; yy = y[idx]; a = s["prev"]["V055"][idx]
                    b = s["fund"][mod] if mod in FUNDACAO else s["prev"][mod][idx]
                    ok = np.isfinite(yy) & np.isfinite(a) & np.isfinite(b); yy, a, b = yy[ok], a[ok], b[ok]; L = 10
                if len(yy) < 50:
                    continue
                n_ok += 1
                rng = np.random.default_rng([SEMENTE, 0 if janela == "completa" else 1, fi, mi, si])
                p, r = reps((yy - a) ** 2, (yy - b) ** 2, L, rng); logs.append(math.log(p)); rr.append(r)
                pm, rm = reps(np.abs(yy - a), np.abs(yy - b), L, rng); logs_mae.append(math.log(pm)); rr_mae.append(rm)
                vit += p < 1
            if not logs:
                continue
            R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]; Rm = np.vstack(rr_mae).mean(0); Rm = Rm[np.isfinite(Rm)]
            pval = float(min(1.0, 2 * min((R <= 0).mean(), (R >= 0).mean())))
            res[f"{fam}|{mod}"] = dict(familia=fam, modelo=mod, n=n_ok, mse_geo=float(np.exp(np.mean(logs))),
                                       mse_ic95=[float(np.exp(np.quantile(R, 0.025))), float(np.exp(np.quantile(R, 0.975)))],
                                       mae_geo=float(np.exp(np.mean(logs_mae))),
                                       mae_ic95=[float(np.exp(np.quantile(Rm, 0.025))), float(np.exp(np.quantile(Rm, 0.975)))],
                                       p=pval, v055_melhor_em=vit)
            ps.append(pval); chaves.append(f"{fam}|{mod}")
    for k, sg in zip(chaves, holm(ps)):
        res[k]["significativo_holm"] = sg
        r = res[k]
        r["leitura"] = ("v0.55 melhor" if r["mse_geo"] < 1 else "v0.55 pior") if sg else "sem diferença demonstrada"
    return res


def main():
    S = carregar()
    out = {"completa": comparar(S, "completa"), "pontos1000": comparar(S, "pontos1000"),
           "falhas": {s["nome"]: s["falhas"] for s in S if s["falhas"]}}
    (AQUI / "COMP_RESULTADO.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for jan in ("completa", "pontos1000"):
        print("==", jan)
        for k, r in out[jan].items():
            print(f"{k:32s} n={r['n']:2d} MSE {r['mse_geo']:.3f} ({r['mse_ic95'][0]:.3f}-{r['mse_ic95'][1]:.3f}) "
                  f"MAE {r['mae_geo']:.3f} {r['leitura']}")
    print("falhas:", out["falhas"])


if __name__ == "__main__":
    main()
