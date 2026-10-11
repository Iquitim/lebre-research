# Pré-registro — avaliação final da LEBRE v0.54 na reserva

**Data:** 11/10/2026. **Status:** escrito **antes** de qualquer acesso aos valores das séries reservadas. A reserva foi
fixada em 10/10/2026, antes de qualquer código da v0.54 (`experiments/LEBRE-V0.54-DATA-01/`, `SPLIT_V054.json`, SHA-256
`cda12ec2…b214bece8` no arquivo `SPLIT_V054_SHA256.txt`; seção 8). O código foi testado apenas com séries **não reservadas** no mesmo formato (seção 7).
**Aprovação:** o responsável pelo projeto delegou a condução da v0.54 até o fim ("pode seguir até o fim sem me pedir mais
autorização", 11/10/2026). A execução só começa depois do ensaio e do commit deste documento com os hashes dos scripts.

## 1. Pergunta

A v0.54 (v0.53 + M5a + M5b + M4) mantém a precisão da v0.53 em domínios nunca vistos e custa menos? Princípio do
projeto: a LEBRE não precisa ser a melhor; precisa entregar bem com orçamento mínimo e sem falhas catastróficas. SARIMAX
com entradas e Chronos-2 com covariáveis são tetos de referência, só reportados.

## 2. O que é a v0.54 avaliada

- **Código:** lebre-research, commit `cfe72ce`, pasta `experiments/LEBRE-V0.54-PROTO-01`, rodado numa cópia fixa (git
  worktree) desse commit; o script recusa rodar se a cópia não estiver nesse commit ou tiver alterações.
- **Configuração:** `Lebre054(d, season, season2, reference, m5a=True, m5b=True, m4=True)`, com `reference` = zero,
  persistência ou sazonal, como na v0.53.
  - **M5a rascunho 2** (`ALGORITHM_SPEC_DRAFT_M5a_r2.md`; aceita na validação 6): a camada de precisão M1 dorme enquanto
    seu peso fica abaixo de 10⁻³ por 2.000 alvos, com teste curto quando a seleção de entradas muda.
  - **M5b rascunho 1** (`ALGORITHM_SPEC_DRAFT_M5b.md`; aceita na validação 7): a matriz de covariâncias das entradas (só
    relatório) é atualizada a cada 31 passos.
  - **M4 rascunho 1** (`ALGORITHM_SPEC_DRAFT_M4.md`; aceita na validação 7): teste de remoção disparado pela queda da
    contribuição, acrescentado ao calendário original, com evidência por episódio, orçamento próprio e duração mínima de
    5.000 passos.
  - **Fora da v0.54, e declarado:** M3 (interpretação em níveis; `M3_DIAGNOSTICO.md`) e M6 (ciclo como hipótese; dois
    desenhos medidos, nenhum atendeu na solar). O código da M6 rascunho 0 está no commit, desligado (`m6=False`).
- **v0.53 de comparação:** a biblioteca publicada `lebre==0.2.0` (`lebre.Lebre`, mesmos argumentos).
- **Ambiente:** Python 3.11.9, numpy 2.2.5, pandas 2.2.3, statsmodels 0.15.0 e lebre 0.2.0 no ambiente do LEBRE Lab
  (v0.54, v0.53, referência e SARIMAX); Chronos-2 (pacote `chronos` 2.3.2, torch 2.11.0, modelo `amazon/chronos-2` em
  cache) no Python do sistema, como nas avaliações anteriores.

## 3. Dados e tarefas (`final_dados.py`)

93 séries em 5 famílias, todas da reserva:

| Família | Séries | Construção (a mesma do desenvolvimento) | season / season2 | d | Referência | Bloco do bootstrap |
|---|---|---|---|---|---|---|
| camels | 30 bacias (CAMELS-BR, posições 140-169, semente 5202) | `data_v052.load_camels` (vazão diária; precipitação, evapotranspiração, temperatura; quarentena das entradas preenchidas) | – / – | 3 | persistência | 30 |
| bdg2 | 30 medidores (BDG2, posições 115-144, semente 5203) | `data_v052.load_bdg2` (consumo horário; temperatura do ar e de orvalho) | 24 / 168 | 2 | sazonal | 168 |
| eolica | 8 usinas (ONS, semente 5421) | como B06: geração verificada 2024-2025; vento a 100 m (velocidade, u, v), vento a 10 m, temperatura | 24 / – | 5 | sazonal | 168 |
| solar | 8 usinas (ONS, semente 5422), 01/01 a 30/09/2026 | como B01: geração verificada; radiação global e direta, nuvens, temperatura | 24 / – | 4 | sazonal | 168 |
| niveis | 17 séries: 10 preços à vista diários da EIA e 7 taxas do Tesouro dos EUA (nominais de 1 e 6 meses; reais de 5, 7, 10, 20 e 30 anos) | nível em dias úteis 2010-2025; entradas com 1 dia útil de atraso: WTI e Brent (EIA) e taxas nominais de 2 e 10 anos | – / – | 4 | persistência | 20 |

**Conferência automática** (`final_dados.conferir`): season, season2, número de entradas, número de passos esperado
(eólica 17.544; solar 6.552; níveis 4.174), referência e alvo majoritariamente observado; a execução para se algo não
conferir. **Séries curtas** (critério A4): os primeiros 360 passos de cada série, com a exclusão por falta de alvo de
antes (menos da metade observada depois dos 20%).

Ressalvas da reserva (declaradas em 10/10, `SPLIT_RULES.md`): a solar é separação no tempo (2 das 8 usinas apareceram no
Lab e 4 na reserva da v0.53, sempre com dados de 2024-2025); as entradas dos níveis (WTI, Brent, taxas nominais) podem
coincidir com séries vistas no Lab; 8 sites de prédios compartilham o clima com medidores já usados; carga e câmbio fora.
A tarefa dos níveis (as 4 entradas) é fixada aqui; a reserva fixou só os alvos e as entradas disponíveis.

## 4. Execução (`final_run.py`, `final_chronos.py`)

Uma única execução. Por série: v0.54, v0.53 e a referência (série completa e versão curta), e SARIMAX com entradas
(`comp_dev.run_airline_x`, ajuste nos primeiros 15%, como antes). Chronos-2 com covariáveis nos 1.000 pontos do protocolo
da v0.52. Repetição só por falha de infraestrutura, documentada; nenhuma alteração de código depois do acesso.

## 5. Critérios (fixados agora)

Período de avaliação: t ≥ 20% de T. Régua por decidibilidade como na avaliação da v0.53 (`M2_CANDIDATA_D.md` com os
adendos 1 a 3), agora com a v0.53 no papel antes ocupado pela v0.52: cada série é classificada pelo IC 95% de v0.53 ÷
referência (bootstrap de blocos pareado, B = 2.000, semente 2026101291) em "v0.53 melhor", "referência melhor" ou
"indecidível"; com o maior passo isolado acima de máx(5%, 5 × 2 ln(n)/n) do erro da referência, "indecidível (choque)".
Medição com a semente 2026101292.

**A. Sem piora (todos obrigatórios):**
1. Em cada família, v0.54 ÷ referência nas séries "referência melhor": limite superior do IC 95% ≤ 1,01.
2. Em cada família, v0.54 ÷ v0.53 nas séries "v0.53 melhor": limite superior ≤ 1,02.
3. niveis (teste negativo): número de séries com entrada externa aceita pela v0.54 ≤ o da v0.53.
4. Séries curtas (todas as famílias juntas): v0.54 ÷ o melhor de v0.53 e referência, limite superior ≤ 1,05.
5. Nenhum passo de avaliação com previsão não finita (séries completas e curtas).

**B. Redução de custo:** a mediana, entre as 93 séries, da razão de custo por passo v0.54 ÷ v0.53 (contagem auditada de
operações), com IC 95% por bootstrap das séries (B = 2.000, semente 2026101293): **limite superior < 1**. A nota de
desenho citava "por exemplo 30% a menos" como meta a fixar aqui; o desenvolvimento não sustenta esse número (validação 6,
séries reais: razão mediana de custo total 0,84), e a meta numérica não é adotada.

**C. Perfil embarcado (estimativa declarada, não medição):** a estimativa da v0.53 (74.988 B medidos da v0.52 no
STM32F407 mais o estado da v0.53, `LEBRE-V0.53-FINAL-01/final_analise.ram_estimada`) mais o estado acrescentado pela
v0.54 (22 números de 8 bytes) ≤ 128 KB.

**Promoção da v0.54:** A e B e C. Reportados, sem critério: razões por família (todas as séries), custo por família,
remoções aceitas (não há verdade conhecida sobre trocas de regime em séries reais), estado da M1, entradas externas por
família, SARIMAX-X ÷ v0.54, v0.54 ÷ Chronos-2 e v0.53 ÷ Chronos-2 nos 1.000 pontos.

**Critérios de sucesso da nota de desenho que não se aplicam, e por quê:** "ciclo" (a M6 não entrou na v0.54);
"estrutura" (nenhuma família reservada tem troca de regime conhecida; a evidência da M4 fica declarada como do
desenvolvimento e das validações 7, como decidido em 10/10/2026).

## 6. Expectativas registradas antes

- **Precisão:** v0.54 ÷ v0.53 perto de 1,00 em todas as famílias. Onde a M1 dorme, a saída fica igual à do núcleo e
  da M2; onde a M1 pesa, a v0.54 é idêntica à v0.53. A M5b não muda previsões. A M4 só age quando uma contribuição cai
  à metade.
- **Custo:** razão mediana ~0,85 (validação 6, séries reais: 0,84). A M5a precisa de ~2.100 passos para agir; a solar
  (6.552 passos) e os níveis (4.174) devem economizar menos que a eólica e os prédios.
- **Níveis:** a M4 não resolve a interpretação (M3); espera-se o mesmo número de séries com entrada externa.
- **B é provável, mas não garantido:** em séries curtas ou onde a M1 pesa, a razão fica perto de 1.
- **Adendo, depois do ensaio em séries já gastas (`ENSAIO_RESULTADO.md`), antes de qualquer acesso à reserva:** nas
  bacias e nos prédios, a M1 manteve peso na maior parte das séries e o custo ficou ~1,00; a razão mediana nas 11 séries
  do ensaio foi 0,935 (IC 0,857 a 1,006). Como bacias e prédios são 60 das 93 séries da reserva, **B passa a ser
  incerto, com falha provável**. Nas séries em que a M1 dormiu, o erro caiu (até −9% em prédios). Os critérios não
  mudam.

## 7. Testes feitos antes, sem a reserva

- **Leitores:** `eia_xls` e `tesouro_csv` testados em cópias baixadas à parte de séries não reservadas no mesmo formato
  (WTI, curva nominal de 2015 e curva real de 2005, fora do período reservado).
- **Ensaio** (`ensaio_v054.py`; resultado em `ENSAIO_RESULTADO.md`): execução e análise de ponta a ponta com o mesmo
  código, em 11 séries já gastas (3 bacias e 3 medidores da reserva da v0.53, 2 eólicas e 2 solares da reserva da v0.53
  em 2024-2025, e a taxa nominal de 1 ano do Tesouro, usada no Lab).

## 8. Integridade

| Arquivo | SHA-256 |
|---|---|
| PROTO `lebre054/model054.py` (commit `cfe72ce`) | `248914dfa9e43463a8b5694281eaa1c1599f7f7cf71dda4f2591d4ae5b485c7c` |
| PROTO `lebre054/dormancy.py` | `c206505fa80f0cd795caad042f5f0e152e525ae53a745333a6cbd1183bb09bb7` |
| PROTO `lebre054/screening.py` | `608e64387e859640797407c9fd4f42755ac078f6e5a336460f7bf692034c35b0` |
| PROTO `lebre054/removal.py` | `c69dcfb529074153b270a868c4dee3d8ac4f6555f2e3ae4a244e2cecd6d4d3be` |
| PROTO `lebre054/cycle.py` (desligado) | `ab76c591104dabd677bae756cc84d500025ff627b7f4a38cf4f7262d4db43fdd` |
| PROTO `lebre054/_core.py` (cópia da lib 0.2.0) | `382995e2ebed1b4efabaea36fc63eb2342cd61a9dbc65007a18f3e941203adfe` |
| PROTO `lebre054/_engine.py` | `2585eef978230b854f4b83c61e74e1949a690b099ddb11478016507645c87cab` |
| PROTO `lebre054/_memory.py` | `ead0675e3b30d839df12a819e07fbacc23039a54d561ba0f04fdc230a75ff277` |
| PROTO `lebre054/full.py` | `f8b3edc24ba9e02c6faf65d98302cde4a1909be53bde7fe7b418139141e1aa94` |
| `LEBRE-V0.54-DATA-01/SPLIT_V054.json` | `cda12ec248a455f0596ddb86de524980bebb51a21d68fbab141dad5b214bece8` |
| `LEBRE-V0.54-DATA-01/SNAPSHOT_SHA256SUMS.txt` | `bc5f6dc10fc0c5300c4fbd42724549ecc2dac980f0ef52a138ee807535a6dc11` |
| `LEBRE-V0.53-DATA-01/SNAPSHOT_SHA256SUMS.txt` (ONS 2024-2025 da eólica) | `2faafbb6a1b4fa995f7069d97caba30c02e4da9b25eb8aa08893feb8d4d6b6b8` |

Os SHA-256 dos scripts desta pasta (`final_*.py`, `ensaio_v054.py`) estão em `SHA256SUMS.txt`, gerado no mesmo commit
deste documento. Os scripts de LEBRE-V0.53-FINAL-01 usados sem alteração (`final_dados.py`, `final_regua.py`,
`final_analise.py`) têm os hashes registrados em `LEBRE-V0.53-FINAL-01/SHA256SUMS.txt`.
