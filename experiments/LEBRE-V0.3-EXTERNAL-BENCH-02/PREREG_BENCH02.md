# Pré-registro — BENCH-02: benchmark externo extenso da LEBRE v0.3.2

**Escrito e com hash registrado ANTES de qualquer execução.** Objeto: `lebre_v032.py` (congelado,
SHA-256 `ef0d9634…32efe8`), **sem calibração**. Nenhum parâmetro será alterado depois dos resultados.

## 1. Fundamentação na literatura (por que estas trilhas)

| Trilha | Linha de pesquisa | Referências que usam estes dados/protocolos |
|---|---|---|
| A. Previsão online de séries temporais (h = 1) | aprendizado online sob deriva de conceito | FSNet (Pham et al., ICLR 2023); OneNet (Wen et al., NeurIPS 2023); LSTD (arXiv 2502.12603); datasets ETT (Zhou et al., Informer, AAAI 2021), ECL/Traffic/Exchange (Lai et al., LSTNet, SIGIR 2018) |
| B. Regressão em fluxo com deriva | mineração de fluxos de dados | Friedman com deriva (Ikonomovska et al. 2011); ARF-Reg (Gomes et al., ESANN 2018); River (Montiel et al., JMLR 2021) |
| C. Identificação de sistemas não lineares | benchmarks da comunidade de identificação | Wiener–Hammerstein (Schoukens et al. 2009), Cascaded Tanks e EMPS (nonlinearbenchmark.org; Schoukens & Noël 2017) |
| D. Identificação de sistemas esparsos | filtragem adaptativa esparsa | ZA/RZA-LMS (Chen, Gu & Hero, ICASSP 2009); IPNLMS (Benesty & Gay, ICASSP 2002) |

## 2. Tarefas

**Trilha A (previsão de 1 passo; informação: todas as variáveis em t−1).**
ETTh1, ETTh2, ETTm1, ETTm2 (alvo OT, D = 7); Exchange (alvo = última coluna, D = 8); Jena Weather 2014–2016 (alvo T (degC), D = 14);
ECL (alvo = última coluna, univariado, D = 1); Traffic (alvo = última coluna, univariado, D = 1).
Arquivos em `data/external_bench02` e `data/external` (SHA-256 em `SHA256SUMS.txt`).

**Trilha B (regressão em fluxo).** Sintéticas do River 0.26.1, T = 20 000, sementes **7051..7060**:
FriedmanDrift `lea` (posições 5000/10000/15000), `gra` (7000/14000), `gsg` (7000/14000, janela 1000), Planes2D e Mv.
Reais do River: Bikes (features numéricas + hora; estação e descrição descartadas), WaterFlow (X = [y_{t−1}, hora]) e TrumpApproval (6 features).

**Trilha C (identificação, predição de 1 passo, informação X_t = [u_t, y_{t−1}]).** Wiener–Hammerstein, Cascaded Tanks e EMPS, do pacote
`nonlinear-benchmarks`. O fluxo é a partição de treino oficial seguida da partição de teste oficial, e o **teste é avaliado na partição de teste oficial**.
(Os resultados publicados nesses benchmarks são de erro de simulação livre, não de predição de 1 passo, e portanto **não são comparáveis**.)

**Trilha D (sistema FIR esparso).** Comprimento 32 (taps 0..31); K ∈ {1, 4, 8} coeficientes N(0,1) em posições aleatórias; o sistema é trocado
por outro sistema esparso aleatório em T/2; entrada branca N(0,1) ou AR(1) com ρ = 0,8; SNR de 20 dB; T = 10 000; sementes **7101..7110**
(60 fluxos). Representação padrão: linha de atrasos, X_t = [x_t, …, x_{t−31}] (D = 32), para todos os modelos. Braço adicional
`LEBRE_V032_NATIVE`: X_t = [x_t] (D = 1), usando o dicionário de atrasos da própria LEBRE (mesma informação, outra representação).

## 3. Modelos

- **LEBRE_V032** (congelada, sem calibração).
- **Controles:** CTRL_PERSISTENCE (`ŷ = y_{t−1}`); CTRL_SEASONAL_NAIVE (`ŷ = y_{t−s}`; s = 24 para ETTh/ECL/Traffic, 96 para ETTm e 144 para Jena);
  CTRL_ARX_NLMS (μ = 0,1 sobre [x, 1, y_{t−1}]).
- **Filtros adaptativos clássicos:** IPNLMS (α = 0; μ calibrado em {0,1; 0,5}), mais C2_NLMS, C3_RLS e B1_RZA_LMS do BENCH-01B.
- **Os 15 modelos do BENCH-01B** (incluindo o Track_B, antecessor da LEBRE), calibrados pelo próprio grid na janela de calibração
  = primeiros min(15% T, 5000) passos, com sementes 42..44.
- **Aprendizado em fluxo (River 0.26.1, hiperparâmetros padrão da biblioteca):** RIVER_SGD_LINREG (StandardScaler + LinearRegression),
  RIVER_HATR (HoeffdingAdaptiveTreeRegressor) e RIVER_ARF (ARFRegressor, n_models = 10).
- **Sementes dos modelos estocásticos nos dados reais:** 7201..7203.

## 4. Protocolo e métricas

Harness `experiments/bench01/runner.py::run_full_stream`, sem alteração: escalador causal nas entradas, predição antes de revelar y,
teste a partir de 0,30T (Trilhas A, B e D) ou na partição de teste oficial (Trilha C). Divergência = falha.
Métricas por execução: NMSE e MAE no teste, e **skill contra a persistência**, `1 − MSE/MSE_persistência`, na mesma janela.
FLOPs e memória são reportados só para modelos instrumentados (os do River não são).

## 5. Desfechos primários

- **E1:** rank médio (pelo NMSE mediano por tarefa) da LEBRE_V032 entre todos os modelos, em todas as tarefas e por trilha.
- **E2:** por tarefa, Wilcoxon pareado por semente (tarefas sintéticas) contra o melhor outro modelo, contra o Track_B e contra o CTRL_ARX_NLMS,
  com contagem de vitórias e derrotas.
- **E3 (teste de existência):** fração das tarefas em que a LEBRE_V032 tem skill > 0 contra a persistência **e** está entre os 3 primeiros no rank.
- **E4:** pertinência à fronteira de Pareto (NMSE × FLOPs) entre modelos instrumentados.
- **E5:** tetos de recurso (≤ 100 FLOPs, ≤ 1 KB) por tarefa.

## 6. Critério de decisão pré-declarado (para a seção "existência justificada")

`JUSTIFIED_EXTERNALLY` se E1 colocar a LEBRE_V032 entre os 3 primeiros no rank médio global **e** E3 ≥ 50% das tarefas.
`PARTIALLY_JUSTIFIED` se ela for top-3 em pelo menos duas trilhas. Caso contrário, `NOT_JUSTIFIED_EXTERNALLY`.
