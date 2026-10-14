# Errata 01 da LEBRE v0.54

**Data:** 14/10/2026. **Origem:** auditoria de estresse feita depois da promoção, a pedido do responsável pelo projeto
(`experiments/LEBRE-V0.54-AUDIT-01/RELATORIO_AUDITORIA.md`, commit `b342171`). A avaliação final pré-registrada
(`FINAL_RESULTADO.md`, commit `c0effa2`) não é refeita nem alterada por esta errata.

## 1. Correção: pico de custo da M5b

**Defeito.** Na M5b rascunho 1 (código promovido, commit `cfe72ce`), a matriz de covariâncias das entradas, que serve só
ao relatório de entradas equivalentes, era atualizada de uma vez a cada 31 passos. Essa atualização coincidia
periodicamente com a regressão da camada M1, que roda a cada 8 alvos, e quebrava o escalonamento de custo do núcleo. O
custo médio caía, mas o pico por passo subia:

| Entradas | pico v0.53 | pico v0.54 promovida |
|---|---|---|
| 10 | 6.265 | 6.485 (+3,5%) |
| 20 | 6.583 | 7.333 (+11%) |
| 50 | 7.837 | 11.724 (+50%) |

**Correção (M5b rascunho 2, protótipo commit `f9906c4`).** No passo de fase do ciclo, a média é atualizada e o vetor
centrado é guardado, como antes. A matriz é então atualizada com esse mesmo vetor uma linha por vez nos passos seguintes,
no máximo ⌈d/30⌉ linhas por passo. A consulta ao relatório aplica antes as linhas pendentes.

**O que muda e o que não muda:**

- **Previsões, estrutura e decisões:** idênticas às da v0.54 promovida, passo a passo. A matriz não entra em nenhuma
  delas.
- **Relatório de equivalentes:** idêntico em qualquer momento. Ao fim de cada ciclo, a matriz é bit a bit a do rascunho 1:
  mesma amostra e mesma aritmética por elemento, conferido em séries com d de 3 a 50 e com faltas.
- **Custo total:** o mesmo por ciclo (3d(d+1)/2 + 2d operações). No fim de uma série, as linhas do último ciclo que ainda
  não foram aplicadas não são contadas. A diferença é no máximo o custo de um ciclo, por exemplo 9 operações em 20.000
  passos com d = 2.
- **Pico por passo:** volta para perto do da v0.53, no máximo 1,054 vez (50 entradas) nas medições abaixo.
- **Estado novo:** o vetor centrado do ciclo, d números.

**Medições (LEBRE Lab):**

1. **Primeira medição no banco** (`analises/ERRATA01_V054_RESULTADO.md`, commit `6b826cd`; 64 famílias, 728 séries):
   - identidade atendida em todas as séries;
   - pico atendido (pior caso A12: 1,054 vez a v0.53, contra 1,522 da promovida);
   - **não aceita** pela redação do critério 2, "custo médio igual". Em 70 séries, a diferença era exatamente o custo
     das linhas pendentes no fim, verificado em 728 de 728.
2. **Segunda medição, em 60 séries sintéticas novas**, com o critério 2 reescrito depois da primeira e declarado
   (`analises/ERRATA01_V054_E2_RESULTADO.md`): **aceita**. Identidade em todas as séries, custo total igual contando as
   linhas pendentes, pico no máximo 1,054 vez o da v0.53.

**Consequência para a avaliação final.** A v0.54 com a errata 01 faz as mesmas previsões e as mesmas decisões que a v0.54
avaliada na reserva, e tem o mesmo custo médio, salvo a contagem das linhas pendentes no fim de cada série (no máximo um
ciclo). Os critérios A e C da avaliação final valem sem mudança. No critério B, a razão de custo de cada série pode cair
em no máximo 3d(d+1)/2 / T. **O código da v0.54 passa a ser o do commit `f9906c4`** (a M6, presente no commit, continua
desligada).

## 2. Limitação declarada: relações que somem e voltam (M4)

A auditoria (teste T5) mostrou que a M4 remove uma relação ausente por mais de ~5.200 passos, o que é válido para o
episódio testado. Quando a relação volta, ela precisa ser redetectada: a readição leva em mediana 675 a 920 passos, e até
2.250. Com blocos ligado/desligado de 7.500, 10.000 e 15.000 passos, o erro ficou 10%, 5,5% e 4,6% acima do da v0.53, e os
eventos por série subiram de 1,0 para 3,4. Com blocos de até 5.000 passos, a remoção não acontece. Relações sazonais em
dados horários podem ter esse formato. **Sem correção na v0.54**; os caminhos para a v0.55 estão em
`ALGORITHM_SPEC_DRAFT_M4.md`.

## 3. Observação anterior à v0.54

A lista de eventos do modelo cresce sem limite na v0.53 e na v0.54 (por exemplo, de 176 para 713 eventos entre 50.000 e
200.000 passos com 50 entradas). Num dispositivo embarcado, ela precisa ser limitada ou descartável. Não é introduzida pela
v0.54.
