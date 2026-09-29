# Pré-registro — LEBRE v0.51 (arquitetura mínima e barata)

**Escrito e com hash registrado antes de qualquer execução nos dados abaixo.**
- Objeto: `lebre_v051.py` e `lebre_s051.py` (hashes em `FREEZE_V051_SHA256.txt` e `FREEZE_S051_SHA256.txt`).
- Fundamentação: `ARQUITETURA_V051.md`.
- Sem calibração por tarefa. O período s é declarado pelo ambiente.
- LEBRE v0.1 continua canônica; M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## Partes

**Parte 1 — interno** (I1–I14; sementes **2561..2590**, verificadas livres; braços V045, V05 e V051).

**Parte 2 — HELD-OUT novo** (`data/external_v051/load051.py`; séries nunca avaliadas por nenhuma etapa):
- 5 brasileiras:
  - Q1 ONS carga do SIN (balanço) 2019–20;
  - Q2 ONS hidráulica SE 2019–20;
  - Q3 ONS hidráulica S 2019–20;
  - Q4 ONS eólica do SIN 2019–20;
  - Q5 BCB libra/real.
- 5 internacionais: Q6 AusElectricity série 4; Q7 Pedestrian série 4; Q8 Solar10min série 4; Q9 KDDCup série 4; Q10 AusElectricity série 5.
- **Comparadores e protocolo idênticos aos do `PREREG_V05.md`** (NLinear, DLinear, Holt-Winters e IPNLMS calibrados; ARX, persistência, sazonal ingênuo;
  LEBRE v0.5, v0.4.5 e v0.3.2; Chronos-Bolt tiny no teste completo; Bolt-small e Chronos-2 em 1000 pontos; Chronos-2 com covariáveis em 500).
- Sementes 7611..7613; 10 pontos de partida (0..450) para V051, V05 e NLinear.

**Parte 3 (reportada):** V051 no held-out da v0.5 (`external_v05`, segunda vez que é visto) e no BENCH-04 (semi-held-out).

## Critérios vinculantes

| Código | Critério | Limiar |
|---|---|---|
| **B1** | custo médio de FP/passo em **cada** tarefa interna (d = 5) e em **cada** tarefa do held-out (d ≤ 6) | ≤ 150 |
| **B2** | pico de FP/passo nessas mesmas tarefas | ≤ 500 |
| I-1 | interno: NMSE V051 − V045, limite superior de 95% | < +0,010 |
| I-2 | cobertura interna média | ∈ [0,88; 0,92] |
| I-3 | fidelidade da explicação (diferença relativa máxima) | ≤ 1e−9 |
| C1 | held-out: razão geométrica V051 / NLinear | ≤ 1,10 |
| C2 | held-out: razão geométrica V051 / melhor de {NLinear, DLinear, Holt-Winters} | ≤ 1,15 |
| C4 | held-out: razão geométrica V051 / V05 (não perde a competitividade da v0.5) | ≤ 1,10 |
| S1 | estabilidade: mediana entre tarefas de (máx/mín do NMSE entre partidas) / máximo | ≤ 1,10 / ≤ 1,50 |
| S2 | cobertura de 90% ∈ [0,85; 0,95] | ≥ 80% das tarefas |
| K-c | divergências | 0 |

**Reportados:**
- C3: V051 / melhor Chronos (meta ≤ 1,50);
- ranking;
- custo por componente e por d;
- Parte 3.

## Regra de promoção

A LEBRE é promovida a **v0.51 (versão de pesquisa)**, que substitui a v0.5 como referência, se passar em **todos** os critérios vinculantes.
Caso contrário, a v0.5 permanece, e a fronteira encontrada é reportada.

## Limites declarados antes

- O orçamento vale para d ≲ 6 entradas; o custo cresce ~8 FP por entrada adicional.
- Em DEV, a v0.51 fica ~7% atrás da v0.5 nas séries reais (0,976 contra 0,91) e ~10% atrás no interno (0,220 contra 0,199), custando ~6× menos.
