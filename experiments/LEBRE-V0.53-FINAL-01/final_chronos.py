"""final_chronos.py — EXECUÇÃO ÚNICA PRÉ-REGISTRADA do Chronos-2 com covariáveis (teto de referência de precisão, fora
da classe de orçamento) na reserva, com o protocolo de LEBRE-V0.52-PROTO-01/chronos_dev.py, como na avaliação da v0.52:
zero-shot, contexto 512, previsão de um passo (mediana), 1.000 pontos observados espaçados no período de teste; entradas
como covariáveis passadas e seu valor atual como covariável futura conhecida. Saída: chronos/<tarefa>.npz.
"""
import os
import sys
import time

import numpy as np
import torch

import final_dados as FD

sys.path.insert(0, os.path.join(FD.RAIZ, "experiments", "LEBRE-V0.52-PROTO-01"))
import chronos_dev as CH  # noqa: E402

OUT = os.path.join(FD.AQUI, "chronos")

if __name__ == "__main__":
    torch.set_num_threads(16)
    from chronos import BaseChronosPipeline
    os.makedirs(OUT, exist_ok=True)
    pipe = BaseChronosPipeline.from_pretrained("amazon/chronos-2", device_map="cpu")
    for familia, ident in FD.tarefas():
        f = os.path.join(OUT, f"{familia}__{FD._seguro(str(ident))}.npz")
        if os.path.exists(f):
            continue
        t0 = time.time()
        d = FD.carregar(familia, ident)
        idx = CH.points(d["y"])
        inp = CH.contexts(d["y"], idx, d["X"])
        out = []
        for b in range(0, len(inp), 256):
            q, _ = pipe.predict_quantiles(inp[b:b + 256], prediction_length=1, quantile_levels=[0.5])
            q = torch.stack([qq.reshape(-1)[0] for qq in q]) if isinstance(q, list) else q.reshape(len(inp[b:b + 256]), -1)[:, 0]
            out.append(q.float().numpy())
        np.savez_compressed(f, idx=idx, CHRONOS2_COV=np.concatenate(out))
        print(f"CHRONOS2_COV {familia}:{ident} {time.time() - t0:5.0f}s", flush=True)
