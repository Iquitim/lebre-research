# Pré-registro — LEBRE v0.5 (três especialistas online com agregação exponencial)

**Escrito e com hash registrado antes de qualquer execução nos dados abaixo.** Objeto: `lebre_v05.py` (hash em `FREEZE_V05_SHA256.txt`),
que usa a cópia congelada `lebre_v045.py` (SHA-256 `97af0482…`). A v0.5 não é calibrada por tarefa. O único dado do ambiente é o período
de amostragem s, que define a janela Lw = max(96, 2s), como no DLinear, no NLinear e no Chronos.
LEBRE v0.1 continua canônica; M3 `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## 1. Objetivo declarado pelo responsável

Desempenho **competitivo** (não necessariamente superior) frente a modelos modernos, com **estabilidade**. A perda de parte da explicabilidade é aceita.

## 2. Evidência de DEV que motivou o desenho (só dados já usados; `dev_instab.py`, `dev_arch.py`, `dev_internal.py`)

- **O IPNLMS não causa a instabilidade.** Sem ele, a instabilidade entre pontos de partida é igual (pior caso 4,18 contra 3,18).
- **A causa é a representação em nível com hipótese estrutural esparsa.** Nas séries reais sazonais, o que decide o desempenho é a memória densa
  e longa do alvo, relativa ao último valor (NLinear). Nos sistemas guiados por entradas (I1–I14), essa memória é inútil ou prejudicial.
- **Resultados em DEV** (razão geométrica de NMSE contra o NLinear calibrado; variação entre pontos de partida):
  | Desenho | Séries reais | Variação máx. | Interno (I1–I14) |
  |---|---|---|---|
  | v0.4.5 | 2,07 | 3,33 | 0,221 |
  | cascata janela → LEBRE | 0,95 | — | 0,287 (piora o interno) |
  | janela pura | 0,91 | — | 0,97 (sem valor) |
  | **agregação de 3 especialistas (v0.5)** | **0,91** | **1,07** | **0,199** |
- **Descartados:** LEBRE sobre Δy (1,16); cascata com a LEBRE densa; aprendizado conjunto janela+LEBRE (divergiu); janela com covariáveis sem a guarda (X3: 0,37).

## 3. Arquitetura (resumo; detalhes no cabeçalho de `lebre_v05.py`)

- **Especialistas:**
  - **A:** a LEBRE estrutural v0.4.5;
  - **W:** memória do alvo (janela NLinear relativa a y₍t−1₎, NLMS com μ = 0,05);
  - **B:** W mais a LEBRE com base podada, sujeita a evidência, sobre o resíduo de W.
- **Agregação:** pesos exponenciais sobre a perda normalizada e descontada (η = 1, λ = 0,99), com garantia de arrependimento (Vovk 1990; Cesa-Bianchi & Lugosi 2006).
- **Saídas:** intervalo por rastreamento de quantil sobre o erro combinado; explicação aditiva exata ponderada pelos pesos.
- **Custo** (~900–2000 FP/passo): **abandona o orçamento de ≤ 100 FP da v0.4**, de forma declarada.

## 4. Partes e critérios

**Parte 1 — interno** (I1–I14, sementes **2501..2530**, verificadas livres; braços V032, V045 e V05). Vinculantes:
- I-1: NMSE V05 − V045 com limite superior de 95% < +0,010 (não degrada os sistemas guiados por entradas);
- I-2: cobertura média ∈ [0,88; 0,92];
- I-3: fidelidade da explicação, diferença relativa máxima ≤ 1e−9.
- **Reportado:** estrutura exata do especialista A e FP/passo.

**Parte 2 — HELD-OUT novo** (`data/external_v05/load05.py`; nenhuma dessas séries foi avaliada antes):
- 5 brasileiras:
  - N1 ONS carga SE/CO 2021–22;
  - N2 ONS hidráulica Norte 2021–22;
  - N3 ONS térmica SIN 2021–22;
  - N4 ONS eólica NE 2021–22;
  - N5 BCB euro/real.
- 5 internacionais: N6 ElecDemand Victoria; N7 AusElectricity série 3; N8 Pedestrian série 3; N9 Solar10min série 3; N10 KDDCup série 3.
- N1 e N4 são séries do BENCH-04 em outro período (**held-out temporal**, declarado).
- **Comparadores:**
  - calibrados como no BENCH-04: NLinear, DLinear e Holt-Winters online, IPNLMS;
  - sem calibração: ARX-NLMS, persistência, sazonal ingênuo, LEBRE v0.3.2 e v0.4.5;
  - Chronos (protocolo da emenda 01 do BENCH-04): Bolt-tiny no teste completo; Bolt-small e Chronos-2 em 1000 pontos; Chronos-2 com covariáveis em 500.
- Sementes 7611..7613. Métrica: NMSE mediano.
- **Vinculantes:**
  - **C1:** razão geométrica V05 / NLinear ≤ 1,10;
  - **C2:** razão geométrica V05 / melhor de {NLinear, DLinear, Holt-Winters} ≤ 1,15;
  - **S1 (estabilidade, 10 pontos de partida 0..450):** mediana entre tarefas de (máx/mín do NMSE) ≤ 1,10 e máximo ≤ 1,50;
  - **S2:** cobertura de 90% ∈ [0,85; 0,95] em ≥ 80% das tarefas;
  - **K-c:** zero divergências.
- **Meta declarada, não vinculante:**
  - **C3:** razão geométrica V05 / melhor Chronos ≤ 1,50.
  - Os modelos de fundação são outra classe: zero-shot, 9–120M de parâmetros, ~1000× o custo por passo. Há também risco de contaminação do pré-treino com dados públicos (Monash).

**Parte 3 — BENCH-04 (semi-held-out,** terceira vez que esses dados são vistos): a V05 contra os 35 modelos, com K-a a K-e, C1 a C3 e S1 reportados.

## 5. Regra de promoção

A LEBRE é promovida a **v0.5 (versão de pesquisa)**, que passa a ser a referência da linha de pesquisa, se passar em I-1 a I-3 e em C1, C2, S1, S2 e K-c.
C3 e a Parte 3 são reportados. Se falhar, a linha v0.4 (`lebre_v045.py`) permanece, e o resultado é reportado.

## 6. Limites declarados antes da execução

- A explicabilidade muda de natureza. A explicação continua **exata e aditiva**, mas a memória do alvo é **densa** (agregada em grupos de defasagens),
  e a estrutura esparsa nomeada vale só para o especialista A e para as covariáveis de B, ponderadas pelos pesos.
- O custo sobe cerca de 10×.
- Os alarmes de mudança vêm dos especialistas A e B, e a troca de pesos é um sinal adicional, não testado estatisticamente.
