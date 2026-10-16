# 05 — F4: descoberta estrutural em alta dimensão

**Questão.** Em que condições a descoberta seletiva da LEBRE supera arquiteturas que usam todas as variáveis candidatas?

**Resposta curta.**
- **[RESULTADO]** Na única comparação registrada (v0.52, dimensões baixas, 100 séries reais, exploratória), os testes
  **não** melhoraram a precisão sobre "tudo ligado": 0,988 [0,970; 1,006].
- Acima de d ≈ 8 não há nenhuma evidência.
- **[DEDUÇÃO]** O código tem limites que tornam a pergunta mais estreita do que o enunciado supõe.

Este documento é um **protocolo**, não um resultado. Nenhuma medição foi feita.

Rótulos como em `01_ARCHITECTURE_BASELINE.md`.

## 1. O que a seleção da LEBRE de fato decide

- **[FATO]** O atraso zero de **todas** as entradas está sempre no modelo: base NLMS sobre [1, xₜ] (`_core.py`). A seleção
  decide os blocos de atraso por banda de oitava (1 a 31) e o atraso de pico de cada entrada. Em alta dimensão, "LEBRE sem
  descoberta" já é um NLMS sobre d + 2 coeficientes.
- **[FATO]** No máximo **4 unidades ativas** (`M_MAX = 4`) e **2 experimentos** simultâneos; um aquecimento de 250 passos
  por vez; recarga de 2.000 passos. Com mais de 4 relações com atraso, a seleção estrita **não consegue** representá-las
  todas. É um limite de capacidade do contrato de custo, não uma falha estatística.
- **[FATO]** A M1 escolhe as 5 entradas mais correlacionadas **sem teste**: é uma seleção por triagem, e não por evidência.

## 2. Consequências deduzidas para a escala em d

**[DEDUÇÃO] Limiar de evidência.** Os primeiros P = 2(d + 2) níveis valem α/(2P) (vezes R + 1). O limiar log(1/α)
cresce com log d:

| d | P | log(2P/α) | relativo a d = 4 |
|---|---|---|---|
| 4 | 12 | 6,17 | 1,00 |
| 8 | 20 | 6,68 | 1,08 |
| 16 | 36 | 7,27 | 1,18 |
| 32 | 68 | 7,91 | 1,28 |
| 64 | 132 | 8,57 | 1,39 |
| 128 | 260 | 9,25 | 1,50 |

Pela aproximação da nota formal (n\* ≈ 2σ²·log(1/α)/D²), o tempo até aceitar uma relação de efeito fixo cresce cerca de
50% de d = 4 para d = 128. É um custo de poder modesto: a correção por multiplicidade é logarítmica.

**[DEDUÇÃO] Custo por passo** (contagem analítica do código, termos dominantes, sem a M1):

| d | triagem espalhada | equivalentes (M5b, por passo) | base NLMS |
|---|---|---|---|
| 4 | ~82 | ~2 | ~24 |
| 16 | ~280 | ~16 | ~72 |
| 64 | ~1.072 | ~212 | ~264 |
| 128 | ~2.128 | ~820 | ~520 |

A triagem é linear em d; o relatório de equivalentes é quadrático, dividido por 31. **[RESULTADO]** A auditoria mediu
3.017 operações por passo com d = 50 em séries de 500 passos (`LEBRE-V0.54-AUDIT-01`, T2). Com d = 128, o custo passa
de ~3.500 operações por passo: fora da classe "algumas centenas a menos de dois mil" em que a LEBRE foi avaliada. A
F4 precisa declarar isso.

**[HIPÓTESE] Interação com a F1.** Com d candidatas, o máximo sobre unidades da projeção Dᵤ do erro de estimação da
referência cresce com d. A chance de alguma unidade ficar acima do limite detectável, D_crit, também cresce, mas ela é
compensada em parte pelo limiar maior. O saldo é desconhecido, e é a parte da F1 que só a F4 testa (F1-c).

## 3. Hipóteses (rascunho para o pré-registro)

| Hipótese | Resultado primário | Aceitação |
|---|---|---|
| **H4.1** a seleção supera "tudo ligado" quando d é grande e as relações são esparsas | razão de erro A ÷ B por célula (d, esparsidade), bootstrap pareado | limite superior < 0,99 em células com d ≥ 32 e esparsidade ≤ 4 |
| **H4.2** o controle de falsas aceitações não se degrada com d | fração de execuções nulas com ≥ 1 entrada externa aceita | limite superior do IC 95% ≤ 0,05 em todo d |
| **H4.3** o atraso de detecção cresce como log d | passos até aceitar a verdadeira | inclinação contra log(2P/α) compatível com a dedução do §2 (IC contém a previsão) |
| **H4.4** o custo segue a contagem | operações e relógio por passo | dentro de ±10% da contagem; relógio reportado |
| **H4.5** substitutas correlacionadas crescem com d | fração de aceitações estruturalmente falsas com grupos correlacionados | só descritiva; sem critério de aceitação |

**Onde a seleção pode ser neutra ou prejudicial** (registrar sem forçar resultado positivo):
- d pequeno: a evidência anterior já indica neutralidade;
- mais de 4 relações verdadeiras: há limite de capacidade;
- relações intermitentes: a remoção da M4 é cara (F3);
- séries integradas: há aceitações espúrias (F2).

## 4. Desenho experimental

**Grade:** d ∈ {4, 8, 16, 32, 64, 128} × relações verdadeiras k ∈ {1, 2, 4, 8} × correlação entre entradas
{independentes; AR(0,9) independentes; grupos de 4 com correlação 0,9} × sinal {fraco 0,1; médio 0,3 desvio}. Cenários
adicionais, com d ∈ {16, 64}: atraso de 3 a 20 passos, relação intermitente, quebra estrutural, alvo integrado e
"causalidade aparente" (entrada que repete o passado do alvo e não traz informação incremental).

**Plano em duas fases:**
1. **Exploratória:** 10 sementes por célula, delineamento fracionado (cerca de 100 células). Serve para formular as
   células da confirmação; não conta como evidência.
2. **Confirmatória:** 50 sementes novas nas células escolhidas, com critérios fixados antes.

**Modelos, com o mesmo conjunto de informação** (mesmas entradas, mesmas bandas de atraso de 1 a 31, mesma memória
como deslocamento ou nenhuma, declarado no pré-registro):
- **A.** LEBRE v0.54 (seleção estrita).
- **B.** LEBRE com todas as unidades ativas desde o início, sem experimentos. O protótipo v0.52 tinha `all_on`; para a
  v0.54, é uma subclasse na pasta do experimento. O teto M_MAX não se aplica a unidades iniciais.
- **C.** LEBRE sem descoberta: experimentos desligados (base NLMS + memória).
- **D.** Regressão online regularizada: RLS com esquecimento e regularização sobre todos os atributos de banda (custo
  quadrático em 5d; reportar como fora da classe de custo), e uma variante de custo linear (NLMS ou gradiente com
  truncamento para B atributos, no espírito de Wang et al. 2014).
- **E.** Seleção estatística compatível com fluxo: α-investing por fluxo (Zhou, Foster, Stine & Ungar, JMLR 2006),
  adaptado a janelas, com o mesmo α.

**Métricas:** MSE e MAE relativos; FDR e proporção de falsas descobertas (estrutural, pela verdade do gerador); poder,
precisão e recall da seleção; atraso de detecção; unidades ativas; operações e relógio por passo; inclinações em d.

**Restrições:**
- execução pura em Python é lenta com d = 128: medir o tempo numa célula antes de fixar o tamanho da grade;
- nenhuma célula é interpretada sem o IC;
- menor erro médio em algumas células não prova superioridade.

## 5. Decisão

| Hipótese | Classe | Recomendação |
|---|---|---|
| H4.1 seleção supera tudo ligado em alta dimensão | **INCONCLUSIVE** (sem dados acima de d ≈ 8; neutra abaixo) | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.2 FDR estável em d | **INCONCLUSIVE** (0/400 nulos com d = 4; 0/100 na auditoria) | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.3 atraso ~ log d | **PRELIMINARY_SUPPORT** por dedução (§2) | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.4 custo segue a contagem | **PRELIMINARY_SUPPORT** (d = 50 medido; contagem conhecida) | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.5 substitutas crescem com d | **INCONCLUSIVE** | descritiva |

**A F4 é uma linha de pesquisa independente.** Ela produz um mapa de onde a seleção ajuda, é neutra ou atrapalha, e não
justifica, por si, mudar a arquitetura. Em d alto, ela também sai da classe de custo declarada.
