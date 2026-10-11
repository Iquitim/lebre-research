# LEBRE v0.54 — Rascunho 0 da especificação da M5b

**Data:** 11/10/2026 · **Status:** critérios fixados antes de qualquer medição registrada; aprovado para medição (M5B_E1)
pelo responsável pelo projeto, que delegou a condução até o fim mantendo as regras do projeto. Sem resultado ainda.
**Protótipo:** `experiments/LEBRE-V0.54-PROTO-01`, commit `cfb0321` (`lebre054/screening.py`, parâmetro `m5b=True` de
`Lebre054`).

## O problema

Na v0.53, o custo do núcleo cresce com o número de entradas d. Em séries como as do cenário de custo (só 2 de d entradas
relevantes, 20 mil passos), o núcleo custa cerca de 500, 750, 1.250 e 3.150 operações por passo com d = 5, 10, 20 e 50.
Com d = 50, a triagem custa cerca de 1.870, dos quais cerca de 1.020 vêm de uma única peça: a matriz de covariâncias entre
todas as entradas, atualizada a cada 4 passos, com custo quadrático em d. Essa matriz serve **só ao relatório** de
entradas equivalentes (`equivalent_inputs`: entradas cuja correlação com uma unidade é ≥ 0,95, que a entrada aceita pode
estar representando). Ela não entra em nenhuma previsão nem em nenhuma decisão. O restante do custo vem da triagem das
entradas inativas (~800), das somas de faixas (~510) e do modelo base (~310).

## O que foi explorado e descartado antes de medir

Exploração (sementes 5605 a 5609, gerador do cenário de custo, nenhuma delas de medição registrada): **dormência das
entradas inativas na triagem**. A ideia era triar a cada 64 passos as entradas cuja estatística ficasse baixa por 2.000
passos e não manter suas somas de faixas.

- Com o limiar de sono na metade do limiar de candidatura, quase nenhuma entrada dormia: sob a hipótese nula, a
  estatística é aproximadamente χ² com 5 graus de liberdade e passa de 7,5 cerca de 19% do tempo.
- Com o limiar de sono igual ao de candidatura, o custo total com d = 50 caía para 1.500 a 2.100 por passo. Mas a entrada
  relevante de sinal mais fraco (atraso 10, coeficiente 0,5) dormia antes de ser descoberta. A detecção atrasava ou
  falhava em parte das séries, com MSE até 46% maior que o da v0.53. Isso aconteceu com triagem dormente a cada 64, 32 ou
  16 passos.

O motivo é estrutural: triar menos é detectar mais devagar. Nenhuma constante resolve isso sem perda de recall, que a
nota de desenho proíbe. **Decisão do responsável pelo projeto (11/10/2026):** a M5b fica só com a parte segura, sem
nenhuma mudança em previsões. A meta da nota de desenho (custo com 50 entradas ≤ 1,5 vez o custo com 5, depois revista
para ≤ 2,0 vezes) fica **não atingida e declarada**. A redução restante depende de retirar entradas do modelo base e da
triagem por evidência, o que é trabalho da M4 (remoções).

## O desenho

A matriz de covariâncias das entradas (média `g_m` e covariância `g_c`) passa a ser atualizada a cada **SE_EQ = 32**
passos em vez de 4, com peso **1e-3 × 32** em vez de 1e-3 × 4. A janela de tempo continua ~1.000 passos, com 8 vezes
menos amostras. Todo o resto do núcleo, da M1 (com a M5a) e da M2 é idêntico.

**Consequências exatas:**

- Previsões, estrutura e todas as decisões são idênticas, passo a passo, às da v0.54 sem a M5b, porque a matriz não entra
  em nenhuma delas.
- A economia é determinística: (3·d(d+1)/2 + 2d) × (1/4 − 1/32) operações por passo, com d contando as entradas do
  núcleo. São ~893 com d = 51 (50 entradas mais a entrada extra do núcleo), ~92 com d = 11 e ~10 com d = 3.
- O relatório de equivalentes fica mais ruidoso: o erro padrão da correlação perto de 0,95 sobe de ~0,006 para ~0,017.
  Longe do limiar nada muda. Na exploração com o gerador do cenário de substitutas, a concordância foi total com
  correlação verdadeira até 0,9. Com 0,95 o próprio relatório original oscila (diz "equivalente" em 29% das checagens) e a
  M5b discorda em 29%; com 0,97, em 6,6%.

Estimativa exploratória (semente 5606): custo do núcleo 525 → 509 (d = 5), 742 → 694 (10), 1.290 → 1.129 (20) e
3.158 → 2.265 (50, razão 0,717). Custo total 3.674 → 2.782 com d = 50.

## Critérios (fixados antes da medição M5B_E1)

Banco: as 64 famílias do E20 do LEBRE Lab, todas as séries. Comparação: protótipo no commit `cfb0321`, `Lebre054` com
`m5b=False` contra `m5b=True`, mesmos argumentos.

1. **Identidade:** em todas as séries, previsões idênticas passo a passo (NaN igual a NaN) e estrutura final idêntica.
2. **Custo:** custo do núcleo por passo menor com a M5b em todas as séries. Na média do grupo d = 50 de A01 e em A12,
   razão ≤ 0,80. O custo total é reportado.
3. **Relatório de equivalentes:** no fim de cada série, para cada entrada aceita u e cada outra entrada j cuja correlação
   estimada pelo original esteja fora da faixa 0,90 ≤ |r| ≤ 0,98, a pertinência de j aos equivalentes de u é a mesma nos
   dois. Dentro da faixa, a discordância é só reportada. A faixa vem do erro padrão acima: a 0,98 o limiar fica a mais de
   4 erros padrão; a 0,90, a cerca de 2.

**Regra:** a M5b (rascunho 0) é aceita se atender a 1, 2 e 3. Se não, as falhas são declaradas e nada é ajustado.

**Sem validação em dados novos, e por quê:** previsões e decisões são idênticas por construção, e o critério 1 confere isso
no banco inteiro. O custo segue uma fórmula. Só o relatório varia, e o critério 3 foi fixado antes de qualquer medição no
banco, que não foi usado para escolher nada da M5b. A evidência vinculante continua sendo a avaliação final
pré-registrada da v0.54.
