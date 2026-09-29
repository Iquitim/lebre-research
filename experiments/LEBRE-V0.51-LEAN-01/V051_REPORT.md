# Relatório — LEBRE v0.51 (arquitetura mínima e barata)

Pré-registro: `PREREG_V051.md` (hash em `PREREG_V051_SHA256.txt`). Fundamentação: `ARQUITETURA_V051.md`.
Objeto: `lebre_v051.py` e `lebre_s051.py` (hashes congelados). **Decisão pré-registrada: `PROMOVIDA_v0.51`**; substitui a v0.5 como referência.
A LEBRE v0.1 continua canônica; M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## Arquitetura (4 peças, cada uma justificada)

| Peça | O que é | Respaldo | Custo (FP/passo) |
|---|---|---|---|
| S | LEBRE estrutural (v0.4.5, NLMS), com partida a frio dos estados de acionamento e dormência da evidência | martingales de mistura (validade para regressor previsível); optional skipping; sleeping experts (Freund et al. 1997); H∞ do LMS (Hassibi et al. 1996) | ~85–100 (d = 5) |
| M | memória: forma online do modelo airline / ETS, com 5 features relativas ao último valor, entre elas o **perfil sazonal de incrementos** | Box & Jenkins; Muth 1960; Hyndman et al. 2008; CycleNet (NeurIPS 2024); NLinear (AAAI 2023) | ~25–40 |
| Combinador | média dinâmica de modelos com esquecimento λ = 0,99 e η = 1/2 (da verossimilhança gaussiana) | Raftery, Kárný & Ettler 2010; Vovk 1990; Herbster & Warmuth 1998 | ~17 |
| Intervalo | rastreamento de quantil do erro combinado | Gibbs & Candès 2021; Angelopoulos et al. 2023 | ~2 |

## Resultados pré-registrados (todos os critérios vinculantes passaram)

| Critério | Limiar | Resultado |
|---|---|---|
| **B1** custo médio por tarefa (interno d = 5; held-out d ≤ 6) | ≤ 150 | ✅ máx. **147** (interno); **138** (held-out); média no held-out **121** |
| **B2** pico por passo | ≤ 500 | ✅ máx. **249** (interno); **196** (held-out, parte de teste) |
| I-1 interno: não degrada contra a v0.4.5 | < +0,010 | ✅ NMSE **0,2151 = v0.4.5** (limite superior +0,0018) |
| I-2 / I-3 cobertura / fidelidade | [0,88; 0,92] / ≤ 1e−9 | ✅ 0,902 / 1e−14 |
| **C1** held-out contra o NLinear calibrado | ≤ 1,10 | ✅ **0,84** (16% **melhor**) |
| **C2** contra o melhor de NLinear, DLinear e Holt-Winters | ≤ 1,15 | ✅ **0,84** |
| **C4** contra a v0.5 | ≤ 1,10 | ✅ **0,77** (23% melhor que a v0.5) |
| **S1** estabilidade (mediana / máximo) | ≤ 1,10 / ≤ 1,50 | ✅ **1,000 / 1,076** |
| S2 cobertura ∈ [0,85; 0,95] | ≥ 80% das tarefas | ✅ 90% (só Q1 fica fora: 0,965) |
| K-c divergências | 0 | ✅ |
| C3 (meta) contra o melhor Chronos | ≤ 1,50 | ✅ **1,37** |

- **Held-out novo** (10 séries, 15 modelos): **3º lugar**, empatada com o Chronos-Bolt small. Fica atrás só do Chronos-2 e do Chronos-2 com covariáveis.
- **Segunda leitura do held-out da v0.5:** 0,80× o NLinear; 0,75× a v0.5; 1,12× o melhor Chronos; 3º de 15.
- **BENCH-04** (semi-held-out): 0,85× o NLinear; 1,33× o melhor Chronos; **3º de 36**; estabilidade máxima de 1,16; 132 FP/passo.

## Custo comparado (held-out)

| Modelo | FP/passo (média; pico) | Memória |
|---|---|---|
| **LEBRE v0.51** | **121; 196** | **~1,4 KB** |
| LEBRE v0.4.5 | 98; 781 | 0,45 KB |
| LEBRE v0.5 | 1022; 2459 | 2,3 KB |
| NLinear online | 812; 2022 | 0,8 KB |
| DLinear online | 1849; 4614 | 1,2 KB |
| Chronos-Bolt tiny / Chronos-2 | ~10⁸–10¹⁰ (estimado); 0,8 / 15,6 ms por passo em CPU | ~36 MB / ~480 MB |

## Leitura honesta

- **O desempenho vem sobretudo da memória**, a forma online do modelo airline com perfil sazonal. Em séries reais, o peso da hipótese estrutural costuma ficar ~0.
  O papel da LEBRE estrutural é tornar o modelo **universal**: nos sistemas guiados por entradas (interno), ela assume e mantém o resultado da v0.4.5.
- **Por que a v0.51 supera a v0.5 e o NLinear sendo mais simples:** o perfil sazonal suavizado (Θ ≈ 0,9) resume muitos ciclos com baixa variância.
  A janela densa de 96–288 pesos, treinada online, tem mais desajuste. É coerente com o achado do M4: métodos estatísticos simples bem especificados são difíceis de bater.
- **Limites:**
  - o orçamento de 150 FP vale para d ≲ 6 entradas (+~8 FP por entrada adicional; com 25 entradas, ~260 de média e ~520 de pico);
  - o pico no held-out foi medido na parte de teste (70% final); no interno, no fluxo inteiro;
  - o Chronos-2 continua melhor (~1,37×);
  - N1 e N4 do held-out da v0.5, e o BENCH-04, já tinham sido vistos;
  - Chronos pode ter visto séries do Monash no pré-treino;
  - a troca de pesos do combinador é um sinal interpretável, não um alarme com erro controlado.
