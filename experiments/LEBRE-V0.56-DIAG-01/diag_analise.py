#!/usr/bin/env python3
"""diag_analise.py — análise do diagnóstico das bacias (PLANO_DIAG_BACIAS.md, §3.3, §4 e §5). Escrito e commitado antes
de qualquer leitura dos resultados de D-A.

Estatística (a da comparação externa): por série, razão de MSE na janela e réplicas em log por blocos móveis pareados de
30 dias (`reps` de LEBRE-V0.55-COMP-01/comp_analise.py, importada sem alteração); no conjunto, a média do log da razão
sobre as séries, IC 95% pelos percentis da média das réplicas e p-valor bilateral pelas réplicas. "Com Holm" (regra 2):
o contraste é significativo pela correção de Holm (alfa 0,05) sobre a família de contrastes da escada, e o efeito tem o
sinal exigido. Sementes: 2026102800 (D-A), 2026102801 (D-B).
Uso: python diag_analise.py {A|B}   ->  DIAG_RESULTADO_<conjunto>.json
"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
E = AQUI.parents[0]
SEMENTE = {"A": 2026102800, "B": 2026102801}
BLOCO, TEST_FRAC = 30, 0.30
# (rótulo, modelo a, modelo b): estatística = log(MSE a / MSE b)
ESCADA = [(f"D_{k}", k, "R0") for k in ("R1", "R2", "R3", "R4", "R5", "R6")]
LADO_LEBRE = [("L2_vs_L0", "L2", "L0"), ("L0_vs_L3", "L0", "L3"), ("L4_vs_R1", "L4", "R1")]
FORA_HOLM = [("G", "L0", "R0"), ("Q2", "L0", "L1")]


def _cmp():
    sp = importlib.util.spec_from_file_location("comp_analise_v055", E / "LEBRE-V0.55-COMP-01" / "comp_analise.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def carregar(conj):
    import diag_dados as DD
    C, pos = DD.conjuntos()
    S = []
    for gid in C[conj]:
        Z = dict(np.load(AQUI / "preds" / f"{conj}__{gid}.npz"))
        info = json.loads((AQUI / "preds" / f"{conj}__{gid}.json").read_text(encoding="utf-8"))
        s = DD.carregar(gid, C, pos)
        assert np.array_equal(Z["y"], s["y"], equal_nan=True)
        S.append(dict(gid=gid, y=Z["y"], P={k: v for k, v in Z.items() if k != "y"}, info=info, chuva=s["X"][:, 0]))
    return S


def mascara(s, modelos):
    y = s["y"]; ok = np.isfinite(y); ok[: int(TEST_FRAC * len(y))] = False
    for k in modelos:
        ok &= np.isfinite(s["P"][k])
    return ok


def contraste(S, a, b, modelos, conj, ci, R_, janela=None):
    logs, rr = [], []
    for si, s in enumerate(S):
        ok = mascara(s, modelos) if janela is None else janela(s, a, b)
        y = s["y"][ok]
        if len(y) < 50:
            continue
        rng = np.random.default_rng([SEMENTE[conj], ci, si])
        p, r = R_.reps((y - s["P"][a][ok]) ** 2, (y - s["P"][b][ok]) ** 2, BLOCO, rng)
        logs.append(math.log(p)); rr.append(r)
    R = np.vstack(rr).mean(0); R = R[np.isfinite(R)]
    return dict(n=len(logs), log=float(np.mean(logs)), razao=float(np.exp(np.mean(logs))),
                ic95_log=[float(np.quantile(R, 0.025)), float(np.quantile(R, 0.975))],
                p=float(min(1.0, 2 * min((R <= 0).mean(), (R >= 0).mean()))), por_serie=[float(math.exp(v)) for v in logs])


def janela_tempo(lo, hi):
    def f(s, a, b):
        ok = np.isfinite(s["y"]) & np.isfinite(s["P"][a]) & np.isfinite(s["P"][b])
        t = np.arange(len(ok)); return ok & (t >= lo) & (t < hi)
    return f


def regimes(s, ok):
    p, y = s["chuva"], s["y"]
    molhado = p[np.isfinite(p) & (p > 0)]
    lim = np.quantile(molhado, 0.9) if len(molhado) else np.inf
    ch = np.zeros(len(y), bool); ch[0] = p[0] > lim; ch[1:] = (p[1:] > lim) | (p[:-1] > lim)
    sobe = np.zeros(len(y), bool); sobe[1:] = y[1:] > y[:-1]
    return {"chuva": ok & ch, "subida": ok & ~ch & sobe, "recessao": ok & ~ch & ~sobe}


def localizar(S, a, b, modelos):
    out = {}
    for nome in ("chuva", "subida", "recessao"):
        frac, razoes, peso = [], [], []
        for s in S:
            ok = mascara(s, modelos); rg = regimes(s, ok)[nome]
            ea, eb = (s["y"] - s["P"][a]) ** 2, (s["y"] - s["P"][b]) ** 2
            tot = float((ea[ok] - eb[ok]).sum())
            if rg.sum() >= 20:
                razoes.append(float(ea[rg].sum() / eb[rg].sum()))
                frac.append(float((ea[rg] - eb[rg]).sum() / tot) if tot != 0 else float("nan"))
                peso.append(float(rg.sum() / ok.sum()))
        out[nome] = dict(n=len(razoes), razao_geo=float(np.exp(np.mean(np.log(razoes)))),
                         fracao_da_diferenca_mediana=float(np.nanmedian(frac)), fracao_dos_passos_mediana=float(np.median(peso)))
    return out


def descritivo(S, a, b, modelos):
    from scipy.stats import spearmanr
    lr, molhado, cv, acc = [], [], [], []
    for s in S:
        ok = mascara(s, modelos); y = s["y"][ok]
        lr.append(math.log(((y - s["P"][a][ok]) ** 2).sum() / ((y - s["P"][b][ok]) ** 2).sum()))
        p = s["chuva"]; molhado.append(float(np.mean(p[np.isfinite(p)] > 0)))
        yy = s["y"][np.isfinite(s["y"])]; cv.append(float(yy.std() / max(yy.mean(), 1e-9)))
        t0 = [t for t, u in s["info"]["L0"]["aceitas"] if u == "x0"]
        acc.append(t0[0] if t0 else len(s["y"]))
    rho = lambda v: dict(zip(("rho", "p"), map(float, spearmanr(lr, v))))  # noqa: E731
    return dict(fracao_dias_chuva=rho(molhado), cv_vazao=rho(cv), instante_aceitacao_precipitacao=rho(acc),
                precipitacao_aceita_em=int(sum(a_ < len(s["y"]) for a_, s in zip(acc, S))), n=len(S))


def main(conj):
    R_ = _cmp(); S = carregar(conj)
    modelos = sorted(set.intersection(*[set(s["P"]) for s in S]))
    res = {"conjunto": conj, "modelos": modelos, "n_series": len(S)}
    fam = [c for c in ESCADA + LADO_LEBRE if c[1] in modelos and c[2] in modelos]
    con = {}
    for ci, (rot, a, b) in enumerate(FORA_HOLM + fam):
        if a in modelos and b in modelos:
            con[rot] = contraste(S, a, b, modelos, conj, ci, R_)
    sig = R_.holm([con[c[0]]["p"] for c in fam])
    for c, sg in zip(fam, sig):
        con[c[0]]["holm"] = bool(sg)
    res["contrastes"] = con
    if "G" in con:
        G = con["G"]; res["reproduz"] = bool(G["ic95_log"][0] > 0)
        regras = {}
        for rot in [c[0] for c in ESCADA if c[0] in con]:
            c = con[rot]; regras[rot] = bool(res["reproduz"] and c["log"] >= 0.5 * G["log"] and c["holm"] and c["log"] > 0)
        if "L0_vs_L3" in con:
            c = con["L0_vs_L3"]; regras["atraso_aceitacao"] = bool(res["reproduz"] and c["log"] >= 0.5 * G["log"] and c["holm"] and c["log"] > 0)
        if "L4_vs_R1" in con:
            c = con["L4_vs_R1"]; regras["memoria_fraca"] = bool(c["holm"] and c["log"] > 0)
        res["regras_secao5"] = regras
        res["janelas_tempo_G"] = {f"{lo}-{hi}": contraste(S, "L0", "R0", modelos, conj, 90 + i, R_, janela_tempo(lo, hi))
                                  for i, (lo, hi) in enumerate(((200, 2000), (2000, 5000), (5000, 10 ** 9)))}
        res["regimes_G"] = localizar(S, "L0", "R0", modelos)
        res["descritivo_G"] = descritivo(S, "L0", "R0", modelos)
    if "Q2" in con:
        res["janelas_tempo_Q2"] = {f"{lo}-{hi}": contraste(S, "L0", "L1", modelos, conj, 95 + i, R_, janela_tempo(lo, hi))
                                   for i, (lo, hi) in enumerate(((200, 2000), (2000, 5000), (5000, 10 ** 9)))}
        res["regimes_Q2"] = localizar(S, "L0", "L1", modelos)
    res["parametros"] = {k: [s["info"][k].get("par") for s in S] for k in modelos if k.startswith("R")}
    (AQUI / f"DIAG_RESULTADO_{conj}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8",
                                                     newline="\n")
    for rot, c in con.items():
        print(f"{rot:10s} razão {c['razao']:.3f}  IC log [{c['ic95_log'][0]:+.3f}; {c['ic95_log'][1]:+.3f}]  p {c['p']:.4f}"
              f"  holm {c.get('holm', '-')}")
    print("regras:", res.get("regras_secao5"))


if __name__ == "__main__":
    main(sys.argv[1])
