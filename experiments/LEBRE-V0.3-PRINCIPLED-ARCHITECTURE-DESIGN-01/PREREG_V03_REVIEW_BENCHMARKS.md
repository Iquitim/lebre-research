# Pré-registro — Revisão da LEBRE v0.3 / v0.3.1: benchmarks interno e externo

**Escrito e com hash registrado ANTES de qualquer execução destes benchmarks.** Status: exploratório-confirmatório (a arquitetura
não é canônica; M3 continua `UNOPENED`).

## Objetos avaliados (congelados)

| Id | Arquivo | SHA-256 |
|---|---|---|
| V03 (iter4) | `lebre_v03.py` | ver `FREEZE_ITER4_SHA256.txt` |
| V031 (correção de bugs: F1–F5) | `lebre_v031.py` | `381731ba…53cb9` (`FREEZE_V031_SHA256.txt`) |

A V031 foi motivada **apenas** pelos testes de propriedades (`verify_properties.py`, sementes 5031..5230), não por resultados de benchmark.
A checagem de não-regressão nas sementes de DEV 3301..3310 não alterou nenhum parâmetro.

## Parte I — Benchmark interno I1–I14 (confirmatório)

- **Sementes:** 2116..2145 (N = 30). A varredura do repositório as mostrou livres. O bloco 2056..2085 está reservado para o ARB10.
- **Braços:** V02_A0 (K1, K_arb=5), V02_B1 (K2, K_arb=5), V03, V031, CTRL_ARX (NLMS μ=0,1 sobre `[x_t, 1, y_{t-1}]`).
- **Métricas:** definições idênticas às do estudo pai (NMSE da execução inteira, latência de chaveamento, reativação da I7),
  FP/passo e recuperação estrutural exata nos checkpoints de fim de regime (I10 excluída; x0@1 aceito em regimes latentes).
- **Unidade inferencial:** semente. Primeiro faz-se a média sobre as 14 tarefas dentro de cada semente; depois, testes pareados.

| Hipótese | Contraste | Regra |
|---|---|---|
| H1 superioridade | V031 − V02_A0 (NMSE) | limite superior unilateral de 95% < 0 |
| H2 recurso (gate) | média de FP da V031 | ≤ 100,000000 |
| H3 valor além da autorregressão | V031 − CTRL_ARX (NMSE) | limite superior unilateral de 95% < 0 |
| H4 explicabilidade | fração de estrutura exata por semente, V031 − V02_A0 | limite inferior unilateral de 95% > 0 |

H1, H3 e H4 recebem correção de Holm (α familiar = 0,05, testes t pareados unilaterais). H2 é um gate.
**Salvaguardas** (V031 − V02_A0, reportadas): por tarefa, ΔNMSE ≤ +0,010; latência de chaveamento I11–I14 ≤ +50 passos; reativação da I7.
**Secundário:** os mesmos contrastes para V03; e V031 − V03.

## Parte II — Externo A: BENCH-01 sintético com sementes novas

- **Tarefas:** A1–A8, H1, H2. **Sementes:** 131..160 (N = 30, livres; o BENCH-01B usou 101..130).
- **Modelos:** os 15 do BENCH-01B com as **configurações calibradas originais** (melhor configuração por tarefa em
  `BENCH_01B_CALIBRATION_LOG.csv`), mais V03, V031, CTRL_ARX e CTRL_PERSIST, os quatro sem calibração.
- **Harness:** `experiments/bench01/runner.py::run_full_stream`, sem alteração (escalador causal, teste a partir de 0,30T).

## Parte III — Externo B: três datasets reais nunca usados no projeto (UCI)

Arquivos em `data/external_v03/` (SHA-256 em `SHA256SUMS.txt`). Pré-processamento fixado aqui, a partir apenas dos nomes das colunas:

| Id | Dataset | Alvo | Features | Linhas |
|---|---|---|---|---|
| X1 | Appliances Energy Prediction | `Appliances` | lights, T1..T9, RH_1..RH_9, T_out, Press_mm_hg, RH_out, Windspeed, Visibility, Tdewpoint (26); excluídos date, rv1, rv2 (ruído aleatório por construção) | todas, em ordem |
| X2 | Beijing PM2.5 | `pm2.5` | DEWP, TEMP, PRES, Iws, Is, Ir, hour (7); excluídos cbwd (categórica) e índices de calendário | linhas com alvo ausente removidas; ordem mantida |
| X3 | Metro Interstate Traffic | `traffic_volume` | temp, rain_1h, snow_1h, clouds_all, hora extraída de date_time (5); texto e holiday excluídos | todas, em ordem |

- **Protocolo do BENCH-01B:** os baselines são calibrados pelo seu próprio grid nos primeiros 15% do fluxo (sementes de calibração 42..44,
  escolha pelo MSE médio). V03, V031 e os controles não são calibrados. Avaliação com teste a partir de 0,30T e sementes 101..105
  (os dados são determinísticos; as sementes só afetam modelos estocásticos).

## Desfechos externos (Partes II e III)

Por tarefa: NMSE mediano, rank entre todos os modelos, pertinência à fronteira de Pareto (NMSE mediano × FLOPs médios),
Wilcoxon pareado por semente da V031 contra o Track B, contra o CTRL_ARX e contra o melhor modelo calibrado da tarefa.
Agregados: NMSE médio, rank médio e número de tarefas na fronteira de Pareto. Tetos do BENCH-01 (≤ 100 FLOPs, ≤ 1024 bytes)
reportados por tarefa. **Nenhum parâmetro será alterado depois de ver estes resultados.**
