# Relatório de promoção — LEBRE v0.4 (implementada por `lebre_v042.py`)

**Decisão pré-registrada:** `PROMOVIDA` a **LEBRE v0.4 — versão de pesquisa, não canônica**.
A LEBRE v0.1 continua sendo a referência canônica congelada. M3 continua `UNOPENED`. `NOVELTY_CLAIM_READY = NO`.
Implementação: `lebre_v042.py`, SHA-256 `5c9ac0f7952dd42c593ad117a712d3ae4f44356fb56bfc36fa08a2de94986506`.

## 1. Objetivo

Melhorar o desempenho preditivo **sem degradar** o que a v0.3.2 havia conquistado (precisão interna, custo ≤ 100 FP, explicabilidade estrutural,
validade estatística e agilidade de adaptação) e **sem inflar a arquitetura**.

## 2. O que mudou da v0.3.2 para a v0.4

| Mudança | Fundamento | Efeito principal |
|---|---|---|
| **Aprendizado IPNLMS** (ganho proporcional, α = 0) | Duttweiler 2000; Benesty & Gay 2002 | é o principal ganho externo; explora esparsidade dentro da base densa |
| **Potência analítica** das features no IPNLMS | P6: toda feature tem potência de projeto conhecida (entradas e atrasos 1; latente e acionamento (1−p)/(1+p)) | elimina ruído de estimação, custo e exposição ao silêncio |
| **σ̂² congelado sem excitação** | P4: "silêncio não é evidência", aplicado a toda estatística de escala | retenção após quiescência (I7 melhora) |
| **Recorte de entradas padronizadas em ±8** | robustez a outliers (caso X3) | proteção contra registros errados |
| **Intervalos de predição calibrados online** (rastreamento de quantil) | Angelopoulos, Candès & Tibshirani 2023; Gibbs & Candès 2021 | benefício de transparência operacional |
| **Explicação exata por previsão** (contribuições fixadas no instante da previsão) | modelo intrinsecamente interpretável | fidelidade exata |
| Precheck exato do teste (`S² < 2·thr·Q` ⇒ não cruza) | condição necessária exata | economia de custo |

**Testado e descartado** (não pagou aluguel ou violava princípio): âncora de persistência (C1, redundante com o IPNLMS e prejudica a explicação);
base no ciclo de vida (C3, custo e perda de atributos fracos); estado MATURE com evidência subamostrada (C4, violava P2 e atrasava a detecção);
CUSUM em blocos (perde retenção em estrutura intermitente); reinício de ganhos após eventos (sem efeito); estimação empírica de potência (ruidosa).
**Resultado: a v0.4 tem menos mecanismos ativos do que os considerados, e nenhum mecanismo novo de decisão.**

## 3. Trajetória (todas as avaliações pré-registradas com hash)

| Versão | Interna G1–G6 | Salvaguardas | Externa | Decisão |
|---|---|---|---|---|
| v0.4 (C1…C6) | ✅ (sementes 2176..2205) | ❌ I11 +86; detecção 2,0× (reportadas) | BENCH-03: 5/5, 2ª de 25 | não adotada (degradação) |
| v0.4.1 | ✅ (2206..2235) | ❌ I14 +101; I4 +0,019; detecção 1,39× (vinculantes) | BENCH-03: 5/5, 1ª de 25 | **não promovida** |
| **v0.4.2** | ✅ (**2236..2265**) | ✅ **todas** | **BENCH-03b (held-out): 5/5, 1ª de 24** | **PROMOVIDA** |

O diagnóstico entre a v0.4.1 e a v0.4.2 usou as sementes 2176..2235, já consumidas e declaradas DEV. A v0.4.2 foi julgada apenas em sementes e dados novos.

## 4. Confirmação interna (I1–I14, N = 30, sementes 2236..2265)

| | v0.2 A0 | v0.3.2 | **v0.4** |
|---|---|---|---|
| NMSE | 0,3159 | 0,2151 | **0,2131** |
| FP/passo | 111,1 | 97,2 | **99,9** |
| Estrutura exata | 72,0% | 89,6% | **91,7%** (NI e melhor: limite inferior +0,0075) |
| Cobertura (90%) | — | — | **0,900** |
| Fidelidade da explicação | — | — | **exata (diferença 0)** |
| Atraso de detecção (média; mediana) | — | 226; 40 | **228; 40** |
| Latência I11 / I12 / I13 / I14 | — | 244 / 1465 / 154 / 1273 | **265 / 1467 / 140 / 1221** |
| Reativação I7 | — | 54,4 | **50,1** |
| Pior ΔNMSE por tarefa | — | — | +0,004 (I4) |

## 5. Externo held-out — BENCH-03b (15 tarefas, 24 modelos, dados e sementes nunca usados)

| Critério | Limiar | v0.4 |
|---|---|---|
| K-a: vence a persistência | ≥ 70% | **93%** |
| K-b: ≤ 1,25× o melhor clássico | ≥ 60% | **93%** |
| K-c: zero divergências | 100% | **✅** |
| K-d: ≤ 1,25× a v0.3.2 | ≥ 90% | **93%** |
| K-e: cobertura ∈ [0,85; 0,95] | ≥ 80% | **93%** |

Rank médio 3,60, **1º de 24** (IPNLMS 5,40; v0.3.2 5,73; CCN 7,20; River HATR 8,67).
Razão média geométrica de NMSE: **0,98× o melhor clássico** e **0,935× a v0.3.2**. Vence o melhor clássico em 9 de 15 tarefas.
Semi-held-out (BENCH-03, já visto): também 5/5, 1º de 24.

## 6. Regressões e limites conhecidos (declarados)

- **KDDCup2018 S2:** NMSE 0,179 contra 0,122 da v0.3.2 (1,46×). É o único caso fora de K-d.
- **Cobertura fora da faixa** em AusElectricity S2 (0,811): o rastreador (a cada 8 passos) atrasa em séries fortemente não estacionárias.
- **T5 (pior caso do latente contra o Kalman):** 2,13× (v0.3.2: 1,64×); a mediana é 1,19×.
- **Custo externo** cresce com d: média de 177 FP no BENCH-03b (d até 32). O ≤ 100 FP vale para d = 5 (99,9 no interno, com folga mínima).
- Trilha B (não linear): as árvores do River continuam melhores em Friedman, Mv e Planes2D. A classe continua linear nos parâmetros.
- Os limiares K-a e K-b foram escolhidos perto do desempenho de DEV. O BENCH-03b é um teste de **replicação** em dados novos.

## 7. Artefatos

`lebre_v042.py` e `FREEZE_V042_SHA256.txt`; pré-registros `PREREG_BENCH03.md`, `PREREG_ADDENDUM_V041.md` e `PREREG_ADDENDUM_V042.md` (com hashes);
`INTERNAL_V042_*.csv`; `BENCH03B_RESULTS.csv`, `BENCH03B_DECISION.json` e `BENCH03B_BY_TASK.csv`; `DEV_*.csv` e `dev_detect.py` (DEV);
`OBSERVABILITY_TESTS_v042.csv`; `../LEBRE-V0.3-PRINCIPLED-ARCHITECTURE-DESIGN-01/PROPERTY_TESTS_v042.csv`.

## 8. Atualização posterior (2026-09-23)

- **BENCH-04** (dados reais novos, incluindo os brasileiros): a v0.4.2 ficou em `PARTIALLY_COMPETITIVE` (3/5), com erro 1,18× o da v0.3.2.
  A causa foi o recorte C5 durante o aquecimento do escalonador (`LEBRE-V0.4-EXTERNAL-BENCH-04/BENCH04_REPORT.md` §7).
- **Sementes novas** (2401..2430): a v0.4.2 falha a salvaguarda de detecção (1,30×) e a de ΔNMSE por tarefa (I5 +0,018).
- **A linha v0.4 passa a ser implementada por `lebre_v045.py`** (C5′, guarda de contrato de entrada), com ressalvas.
  Ver `../LEBRE-V0.45-ROBUST-GUARD-01/DECISAO_V045_SUBSTITUI_V042.md`.
