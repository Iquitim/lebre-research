# Pré-registro — avaliação final da LEBRE v0.53 na reserva

**Data:** 09/10/2026. **Status:** escrito **antes** de qualquer acesso aos valores das séries reservadas. A reserva foi
fixada em 05/10/2026, antes de qualquer código da v0.53 (`experiments/LEBRE-V0.53-DATA-01/`, `SPLIT_V053.json`,
SHA-256 `c2e983c6…aaff0d2d` no arquivo `SPLIT_V053_SHA256.txt`); a cópia dos 55 arquivos brutos confere com
`SNAPSHOT_SHA256SUMS.txt` (verificado em 09/10, só os hashes). O código foi testado apenas com séries **não reservadas** no
mesmo formato (seção 7). **A execução só começa depois da aprovação deste documento pelo responsável pelo projeto.** **Aprovado pelo responsável pelo projeto em 09/10/2026, depois das verificações de `ENSAIO_RESULTADO.md`.**

## 1. Pergunta

A v0.53 (v0.52 + M1 rascunho 5 + M2 candidata Q2) melhora a v0.52 em domínios nunca vistos, sem piorar nenhuma família e
dentro do custo declarado? Princípio do projeto: a LEBRE não precisa ser a melhor; precisa entregar bem com orçamento
mínimo e sem falhas catastróficas. SARIMAX com entradas e Chronos-2 com covariáveis são tetos de referência, reportados.

## 2. O que é a v0.53 avaliada

- Código: lebre-research, commit `4a2620e`, pasta `experiments/LEBRE-V0.53-PROTO-01`, rodado numa cópia fixa (git
  worktree) desse commit; o script recusa rodar se a cópia não estiver nesse commit ou tiver alterações.
- Configuração: `Lebre053(d, season, season2, referencia, porta=True, eps_porta=0.002, recriar=True, alpha_porta=0.01,
  observar_quarentena_entradas=True, saida="prod_q2", precisao="r5")`.
  - M1 rascunho 5 (`ALGORITHM_SPEC_DRAFT_M1_r5.md`): especialista AR2 + bandas de defasagem de até 5 entradas (RLS a cada 8
    passos), combinado com a v0.52 por AdaHedge no erro quadrático, com entrada em sombra.
  - M2 candidata Q2 (`M2_CANDIDATA_Q2.md`): (A,B)-Prod anytime entre D (AdaHedge) e M (troca num só sentido) com perdas
    normalizadas pelo maior erro com esquecimento; referência trivial R = zero (retornos), sazonal ingênuo (com ciclo) ou
    persistência.
- v0.52 de comparação: a mesma base com a porta desligada (`porta=False`), idêntica a `lebre==0.1.0`.
- Ambiente: Python 3.11.9, numpy 2.2.5, pandas 2.2.3, statsmodels 0.15.0 (o mesmo nos dois ambientes usados); v0.53, v0.52,
  referência e SARIMAX no ambiente do LEBRE Lab; Chronos-2 (pacote `chronos` 2.3.2, torch 2.11.0, modelo
  `amazon/chronos-2` em cache) no Python do sistema, como na avaliação da v0.52.

## 3. Dados e tarefas (`final_dados.py`)

104 séries em 8 famílias, todas da reserva:

| Família | Séries | Construção (a mesma do desenvolvimento) | season / season2 | d | Referência | Bloco do bootstrap |
|---|---|---|---|---|---|---|
| camels | 30 bacias (CAMELS-BR, posições 110-139, semente 5202) | `data_v052.load_camels` (vazão diária; precipitação, evapotranspiração, temperatura; quarentena das entradas preenchidas) | – / – | 3 | persistência | 30 |
| bdg2 | 30 medidores (BDG2, posições 85-114, semente 5203) | `data_v052.load_bdg2` (consumo horário; temperatura do ar e de orvalho) | 24 / 168 | 2 | sazonal | 168 |
| solar | 8 usinas (ONS, semente 5311) | como B01 do Lab: geração verificada 2024-2025; ERA5 (radiação global e direta, nuvens, temperatura) no local | 24 / – | 4 | sazonal | 168 |
| eolica | 8 usinas (ONS, semente 5312) | como B06: vento a 100 m (velocidade, u, v), vento a 10 m, temperatura | 24 / – | 5 | sazonal | 168 |
| carga | 4 subsistemas, 01/01 a 30/09/2026 | como B02: carga horária; ERA5 na capital (5 variáveis) | 24 / 168 | 5 | sazonal | 168 |
| fx_ret | 8 pares do H.10, 2010-2025 | como C01: retorno log diário (%); entradas com 1 dia útil de atraso: os outros 3 pares do grupo (grupos de 4 na ordem do `SPLIT_V053.json`) e variações dos juros de 2 e 10 anos | – / – | 5 | zero | 20 |
| fx_abs | os mesmos | como C02: valor absoluto dos retornos | – / – | 5 | persistência | 20 |
| fx_niv | os mesmos | como C03: níveis; entradas: níveis dos outros 3 e juros | – / – | 5 | persistência | 20 |

**Conferência automática** (`final_dados.conferir`, motivada pela errata do ciclo nas validações 4 e 5 do LEBRE Lab):
season, season2, número de entradas, número de passos esperado (solar e eólica 17.544; carga 6.552; câmbio 4.174),
referência e alvo majoritariamente observado; a execução para se algo não conferir. **Séries curtas** (critério 7): os
primeiros 360 passos de cada série, com a exclusão por falta de alvo de antes (menos da metade observada depois dos 20%).

Ressalvas da reserva (declaradas em 05/10, `SPLIT_RULES.md`): a carga é separação no tempo (os mesmos 4 subsistemas do
desenvolvimento, em 2026); os arquivos mensais do ONS de 2024-2025 contêm usinas usadas no Lab (nenhuma reservada); entradas
de câmbio (juros) coincidem com entradas do desenvolvimento; 7 medidores do BDG2 compartilham site com séries já usadas.

## 4. Execução (`final_run.py`, `final_chronos.py`)

Uma única execução. Por série: v0.53, v0.52 e a referência (série completa e versão curta), e SARIMAX com entradas
(`comp_dev.run_airline_x`, ajuste nos primeiros 15%, como na v0.52). Chronos-2 com covariáveis nos 1.000 pontos do
protocolo da v0.52. Repetição só por falha de infraestrutura, documentada; nenhuma alteração de código depois do acesso.

## 5. Critérios (fixados agora; decisões do responsável pelo projeto em 09/10/2026)

Período de avaliação: t >= 20% de T. Régua por decidibilidade (`M2_CANDIDATA_D.md`, com os adendos 1 a 3): cada série é
classificada pelo IC 95% de v0.52 ÷ referência (bootstrap de blocos pareado, B = 2.000, semente 20261053) em "v0.52
melhor", "referência melhor" ou "indecidível"; com o maior passo isolado > máx(5%, 5 × 2 ln(n)/n) do erro da referência,
"indecidível (choque)". Medição com a semente 20261054.

**A. Sem piora (todos obrigatórios):**
1. Em cada família, M2 ÷ referência nas séries "referência melhor": limite superior do IC 95% <= 1,01.
2. Em cada família, v0.53 ÷ v0.52 nas séries "v0.52 melhor": limite superior <= 1,02.
3. fx_ret (teste negativo): número de séries com entrada externa aceita pela v0.53 <= o da v0.52.
4. Em todas as séries, a estrutura da v0.52 dentro da v0.53 é idêntica à da v0.52 sozinha.
5. Séries curtas (todas as famílias juntas): v0.53 ÷ o melhor de v0.52 e referência, limite superior <= 1,05.
6. Nenhum passo de avaliação com previsão não finita (séries completas e curtas).
7. Custo: em cada série, acréscimo médio por passo da v0.53 sobre a v0.52 <= **1.100 FP** (contagem auditada, commit
   `4a2620e`). Substitui o "<= 1,25 vez" preliminar da nota de desenho (decisão de 09/10: o acréscimo da v0.53 é quase
   fixo, ~540 a 970 FP; uma razão pune as séries em que a v0.52 é barata; 1,25 vez é incompatível com M1 + M2, E21).

**B. Melhora clara:** v0.53 ÷ v0.52 em todas as 104 séries (média geométrica; IC 95% pela média, entre as séries, das
réplicas de log da razão de cada série): **limite superior < 1**.

**C. Perfil embarcado (estimativa declarada, não medição):** 74.988 B medidos da v0.52 no STM32F407 (LEBRE-V0.52-EXT-01)
mais a contagem analítica do estado acrescentado pela v0.53 (8 bytes por número; `final_analise.ram_estimada`) <= 128 KB.

**Promoção da v0.53:** A e B e C. Reportados, sem critério: as razões por família, SARIMAX-X ÷ v0.53, v0.53 ÷ Chronos-2 e
v0.52 ÷ Chronos-2 nos 1.000 pontos, custo por série, peso final da M1.

## 6. Expectativas registradas antes

- câmbio: a v0.52 tende a perder para a referência (retornos e níveis); a M2 deve levar a v0.53 para perto dela, com
  ganho sobre a v0.52 (no desenvolvimento, C01 0,94-0,97 e C03 ~0,95);
- bacias, prédios, solar, eólica e carga: a v0.52 é boa; espera-se v0.53 ~1,00 (M1 com peso pequeno, M2 perto da
  v0.52);
- **B é incerto:** o ganho deve vir sobretudo do câmbio (24 das 104 séries); um IC inteiro abaixo de 1 no conjunto não está
  garantido mesmo com a v0.53 funcionando como desenhada;
- custo: acréscimo de ~400 a 970 FP por passo; memória estimada ~83-85 KB.
- **Adendo, depois do ensaio em dados já gastos (`ENSAIO_RESULTADO.md`), antes de qualquer acesso à reserva:** nas 30
  bacias e 25 medidores já usados pela v0.52, a v0.53 ficou em 0,847 da v0.52 nas bacias (não ~1,00, como esperado
  acima) e 0,997 nos prédios, sem erro, NaN ou custo acima do limite. A expectativa para as bacias passa a ser de ganho; os
  critérios não mudam.

## 7. Testes feitos antes, sem a reserva

- `teste_final_dados.py`: os leitores reproduzem **valor a valor** as séries do LEBRE Lab (B01 e B06 usina 0; carga do
  Sudeste em 2025; os 3 tipos de câmbio no grupo de W-C01 a W-C03) e passam na conferência para CAMELS-BR e BDG2 de
  desenvolvimento.
- `teste_final_run.py`: o mecanismo de execução reproduz **exatamente** o MSE da v0.53 e o custo da v0.52 registrados no
  E20 do Lab (B01, usina Janaúba).
- `teste_final_analise.py`: execução e análise de ponta a ponta em 2 séries não reservadas, com um Chronos falso.

## 8. Integridade

| Arquivo | SHA-256 |
|---|---|
| PROTO `lebre053/model053.py` (commit `4a2620e`) | `509eae52c663bd2316d5c0a807a4c5b89399845a5c860b476d4edc773951464d` |
| PROTO `lebre053/precisao.py` | `6106a03d75e8d15ecf464819507f8095cd3823c1f40fe6e655161c031156ffe1` |
| PROTO `lebre053/agregacao.py` | `532cbdfb6307e5d444a44846c50e679a28651c6c71a60d17e4e781a0478b06bd` |
| PROTO `lebre053/_core.py` | `382995e2ebed1b4efabaea36fc63eb2342cd61a9dbc65007a18f3e941203adfe` |
| PROTO `lebre053/_engine.py` | `2585eef978230b854f4b83c61e74e1949a690b099ddb11478016507645c87cab` |
| PROTO `lebre053/_memory.py` | `ead0675e3b30d839df12a819e07fbacc23039a54d561ba0f04fdc230a75ff277` |
| PROTO `lebre053/_model052.py` | `e1e361d648bdbce7110bbf41a00835e62281c1dce8e56db2b85b2258aaff0d2d` |
| PROTO `lebre053/__init__.py` | `f0358581a51db6628354a5f5e6f65ecbeae38ff3c84cd189e0771f587a249674` |
| `LEBRE-V0.53-DATA-01/SPLIT_V053.json` | `c2e983c6c1628764ffcd76592c88ce52fbc2ae9788442445f9f3eaf546012935` |
| `LEBRE-V0.53-DATA-01/SNAPSHOT_SHA256SUMS.txt` | `2faafbb6a1b4fa995f7069d97caba30c02e4da9b25eb8aa08893feb8d4d6b6b8` |
| `LEBRE-V0.52-PROTO-01/data_v052.py` | `88a77ae64b92e414aa55af070a5b142a88ddd20652e0b5d6c8cf841c4f8970fa` |
| `LEBRE-V0.52-PROTO-01/comp_dev.py` | `0bc9d773364ac130acfec1e1f688d2eb14b8a2eecc0a90569de51b7a6c9af40f` |
| `LEBRE-V0.52-PROTO-01/chronos_dev.py` | `33deb6e80521b6941e47934ad8f738fc88b42070aa441590fa03549a307122b0` |

Os SHA-256 dos scripts desta pasta (`final_*.py`, `teste_*.py`, `ensaio_*.py`) estão em `SHA256SUMS.txt`, gerado no mesmo
commit deste documento.
