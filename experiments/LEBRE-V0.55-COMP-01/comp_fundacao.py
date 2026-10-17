#!/usr/bin/env python3
"""comp_fundacao.py — modelos de fundação (COMP_PLANO.md, §2) nos 1.000 pontos de chronos_dev.points:
CHRONOS2_COV, CHRONOS2, CHRONOS_BOLT_SMALL (zero-shot, contexto 512, mediana; chronos_dev.contexts sem alteração),
TTM_ZS e TTM_FT_EXOG (ttm_run.run com lr 1e-4, 30 épocas, parada antecipada; ajuste só na janela de calibração).
Grava fundacao/<família>__<id>.npz (fora do git). Uso: python comp_fundacao.py

Dispositivo: GPU (CUDA) se disponível, a pedido do responsável (17/10/2026). O TTM usa ttm_gpu.py, cópia de
ttm_run.py que só move modelos e tensores para a GPU. A execução parcial anterior em CPU (14 séries) foi descartada,
e todas as séries rodam no mesmo dispositivo (RUN_NOTAS.md).
"""
import importlib.util
import sys
import time
from pathlib import Path

import numpy as np
import torch

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
OUT = AQUI / "fundacao"
sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.52-PROTO-01"))
sys.path.insert(0, str(RAIZ / "experiments" / "LEBRE-V0.52-EXT-01"))
import chronos_dev as CH  # noqa: E402
sys.path.insert(0, str(AQUI))
import ttm_gpu as TTM  # noqa: E402
DEV = "cuda" if torch.cuda.is_available() else "cpu"


def _fr():
    sp = importlib.util.spec_from_file_location("final_run_v055", RAIZ / "experiments" / "LEBRE-V0.55-FINAL-01" / "final_run.py")
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m


def prever(pipe, inp):
    out = []
    for b in range(0, len(inp), 256):
        q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[0.5])
        q = torch.stack([qq.reshape(-1)[0] for qq in q]) if isinstance(q, list) else q.reshape(len(inp[b:b + 256]), -1)[:, 0]
        out.append(q.float().cpu().numpy())
    return np.concatenate(out)


if __name__ == "__main__":
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    OUT.mkdir(exist_ok=True)
    FR = _fr()
    print("dispositivo:", DEV, torch.__version__, torch.cuda.get_device_name(0) if DEV == "cuda" else "", flush=True)
    pipes = {"CHRONOS2": BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map=DEV),
             "CHRONOS_BOLT_SMALL": BaseChronosPipeline.from_pretrained("amazon/chronos-bolt-small", device_map=DEV)}
    for familia, ident in FR.tarefas():
        f = OUT / f"{familia}__{''.join(c if c.isalnum() else '_' for c in str(ident))}.npz"
        if f.exists():
            continue
        t0 = time.time()
        s, ref = FR.carregar(familia, ident)
        y, X = s["y"], s["X"]
        idx = CH.points(y)
        res = {"idx": idx}
        res["CHRONOS2_COV"] = prever(pipes["CHRONOS2"], CH.contexts(y, idx, X))
        uni = CH.contexts(y, idx)
        res["CHRONOS2"] = prever(pipes["CHRONOS2"], uni)
        res["CHRONOS_BOLT_SMALL"] = prever(pipes["CHRONOS_BOLT_SMALL"], uni)
        calib = np.flatnonzero(np.isfinite(y))[:min(int(0.15 * len(y)), 5000)]
        t = TTM.run(X, y, calib, idx, seed=0, lr=1e-4, epochs=30, early_stop=True)
        for k, (p, fl) in t.items():
            res[k] = p; res[k + "_flops"] = fl
        np.savez_compressed(f, **res)
        print(f"{familia}:{ident} {time.time() - t0:5.0f}s", flush=True)
