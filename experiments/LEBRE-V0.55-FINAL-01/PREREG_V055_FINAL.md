# Avaliação final da v0.55: pré-registro (commitado antes da execução; regra de promoção vinculante)

**Data:** 17/10/2026.

**Candidata:** B10 do protótipo `experiments/LEBRE-V0.55-PROTO-01`, congelada no commit `b0522a0`. É o núcleo
ancorado:
- unidades externas testadas contra a previsão do núcleo e unidades internas contra a estrutura de nível;
- a estrutura de inovação como terceiro especialista aninhado;
- o portão suave pela triagem;
- os pesos de cada estrutura vindos do resíduo que o desafiante aprendeu;
- o piso de escala previsível, na escala de uma passada.

Tudo o mais é a v0.54: M1 com dormência, M2, M4 e M5b.

**Comparação:** A, a v0.54 canônica, do mesmo commit. É cópia byte a byte de `f9906c4`, conferida em
`SHA256_COPIAS.txt`.

**História da candidata:**
- desenvolvimento D1 a D5 no LEBRE Lab, com todas as rodadas registradas, inclusive as negativas;
- confirmação C1 com sementes nunca usadas;
- validação em 50 séries reais nunca usadas (`experiments/LEBRE-V0.55-VAL-01`).

## 1. Reserva

`experiments/LEBRE-V0.55-DATA-02`:
- regras em `SPLIT_RULES.md`, commitadas antes de baixar ou sortear;
- `SPLIT_V055.json`, SHA-256 `70876130250c32823b86e16eac0915a241102722b392a553daef6b47cd40c5e4`;
- dados brutos com SHA-256 em `SNAPSHOT_SHA256SUMS.txt`.

| Família | Séries | Construção (a das avaliações anteriores, sem mudança) | Bloco do bootstrap |
|---|---|---|---|
| camels | 30 bacias (posições 190–219) | vazão diária; entradas precipitação, evapotranspiração, temperatura; referência persistência | 30 |
| bdg2 | 30 medidores (posições 175–204) | horária; ciclos 24 e 168; referência sazonal | 168 |
| eolica | 8 usinas (semente 5521) | geração do ONS 2024–2025; ERA5: vento a 100 m (velocidade, u, v), vento a 10 m, temperatura; ciclo 24 | 168 |
| solar | 8 usinas (semente 5522), jan–set/2026 | geração do ONS; ERA5: radiação global e direta, nuvens, temperatura; ciclo 24 | 168 |
| niveis_ecb | 8 taxas do euro do BCE (PLN, CZK, HUF, RON, TRY, IDR, PHP, ILS), dias úteis 2010–2025 | entradas EUR/USD, EUR/GBP, EUR/JPY e EUR/CHF com um dia útil de atraso; referência persistência | 20 |

**Ficaram de fora pela regra de cobertura**, aplicada sem mudança:
- as 6 taxas de commercial paper (cobertura de 60% a 87%, contra o mínimo de 90%);
- o ISK (49%).

## 2. Execuções

Cada série roda **quatro vezes**, todas com a mesma configuração canônica de cada modelo:
- A e B10 com as entradas reais (a **execução principal**);
- A e B10 com as entradas reais mais **duas entradas placebo**: passeios aleatórios gaussianos independentes, gerados
  com a semente `[2026102500, índice da família, índice da série]`.

A avaliação usa as previsões a partir de 20% da série. Os blocos do bootstrap são os da tabela, os mesmos da avaliação
final da v0.54. Há 2.000 réplicas, com semente `[2026102600, família, série]`.

## 3. Regra de promoção (vinculante): a v0.55 é PROMOVIDA se, e só se, valerem todas

| Código | Critério |
|---|---|
| R1 sem piora | em **cada** família, o limite superior do IC 95% da média geométrica das razões de MSE B10 ÷ A (execução principal) é ≤ 1,02 |
| R2 controle negativo | nas 84 séries, a fração com **alguma entrada placebo na estrutura final** da execução placebo: para B10, limite superior de Clopper–Pearson ≤ 0,10, **e** contagem de B10 ≤ a de A |
| R3 sem falha numérica | nenhuma previsão não finita de B10 onde a de A é finita, em nenhuma execução |
| R4 custo | mediana por série da razão de custo B10 ÷ A na execução principal ≤ 1,25 |
| R5 memória | estado estimado (a estimativa da v0.54, mais os números novos do núcleo ancorado, 8 bytes cada) ≤ 131.072 B |

**Reportados sem decidir:**
- razões por família e por série, e o ganho em `niveis_ecb`;
- entradas externas aceitas (A e B10);
- placebo por família;
- peso final da estrutura de inovação;
- janela curta (passos 200 a 2.000 de cada série: as previsões online do início coincidem com as de uma série curta);
- as piores séries.

**Não feito, e declarado antes:** comparações com SARIMAX-X e Chronos-2. A pergunta aqui é a v0.55 contra a v0.54.

## 4. Execução e falhas

- Uma única execução: `final_run.py`, depois `final_analise.py`.
- Uma falha de infraestrutura (erro de leitura, processo interrompido) pode ser repetida com o mesmo código e as mesmas
  sementes. Ela é registrada em `RUN_NOTAS.md`.
- Nenhuma mudança de modelo, de critério ou de análise depois de ver resultados.
- Ambiente de referência: CPython 3.11, NumPy 2.2.5, pandas 2.2.3; `LEBRE055_PROTO` no worktree do commit `b0522a0`.
