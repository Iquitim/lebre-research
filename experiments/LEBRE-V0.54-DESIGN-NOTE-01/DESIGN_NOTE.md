# LEBRE v0.54 — Nota de desenho 01: custo proporcional ao uso e estrutura que também sai

**Data:** 10/10/2026 · **Status:** proposta, sem código e sem pré-registro. Nada aqui altera a v0.53 promovida e
congelada (`docs/architecture/LEBRE_v0.53_FREEZE_RECORD.md`).
**Base:** especificação v0.53-r1; avaliação final da v0.53 (`experiments/LEBRE-V0.53-FINAL-01/`); linha de base E23 no
LEBRE Lab (`diagnosticos/E23_RESULTADO.md`, commits `c8275a9` e `8c81617`, com a `lebre==0.2.0` publicada).
**Escopo decidido pelo responsável pelo projeto (10/10/2026):** a v0.54 termina a consolidação, com as prioridades 1
(custo proporcional ao uso), 2 (remoções que acontecem e interpretação em séries não estacionárias) e 3 (ciclo como
hipótese). A expansão para várias saídas e vários passos passa para a v0.55. Princípio: rigor antes de pressa.

## 0. Resumo

A v0.53 ganhou da v0.52 sem piorar nenhuma família, mas paga por isso em todas: custo mediano de 919 operações por
passo, cerca do dobro do núcleo. A linha de base E23 mostra de onde vem esse custo: na maior parte das séries, a M1
trabalha com **peso zero**. Mostra também três falhas que continuam como na v0.52: a estrutura só cresce (nenhuma
remoção), entradas espúrias em níveis de preço ficam registradas como relevantes, e sem declarar o ciclo o erro chega a
quase três vezes o normal. Esta nota propõe que a v0.54 estenda o princípio da LEBRE (mudar só com evidência, a custo
conhecido) ao **custo** (gastar só onde há uso) e à **saída** de estrutura (remover quando a evidência deixa de
sustentar), e trate o ciclo como hipótese do próprio mecanismo.

## 1. De onde vem a proposta: linha de base medida (E23)

Biblioteca publicada (`lebre==0.2.0`, v0.53) ao lado do núcleo sozinho, só em dados de desenvolvimento. Descritivo.

| Falha | O que se mediu na v0.53 | Fonte |
|---|---|---|
| **F10 (nova): camada paga sem uso** | A M1 custa ~400 a ~840 FP por passo (cresce com m = mín(d, 5)). Peso final zero em 95 de 95 séries do E23 (sintéticas, nulas e de níveis) e em **70 de 104** séries da avaliação final (todas as de solar, eólica, carga e câmbio; 25 de 30 prédios), com acréscimo mediano de 800 FP e custo 2,25 vezes o do núcleo nessas séries; nelas, a v0.53 é idêntica ao núcleo, exceto no câmbio, onde o ganho é da M2 | E23 §1; `final_resultado.json` |
| **F1: custo cresce com entradas nunca aceitas** | Núcleo: 760 FP com 10 entradas, 1.253 com 20, 3.161 com 50 (só 2 relevantes; recall 1,00, nenhuma falsa) | E23 §1 (A01, A12) |
| **F2: remoções nunca acontecem** | Após a troca de regime, a entrada antiga foi removida em 0 de 20 séries e ficou na estrutura final em 20 de 20; erro 7,7% acima do linear online | E23 §2 (A05) |
| **F9 restante: interpretação em níveis** | A M2 corrigiu a precisão (0% a 0,9% contra o passeio aleatório, antes 3% a 15%), mas 4 de 4 séries de níveis ainda aceitam e mantêm uma entrada externa espúria | E23 §3 (C03) |
| **D02: ciclo precisa ser declarado** | Sem declarar o ciclo, erro 2,87 vezes o da v0.53 com o ciclo certo na carga e 1,44 vez na solar; a M2 com persistência não compensa | E23 §5 |
| Controle | 0 de 40 séries nulas com entrada falsa | E23 §4 (A02) |

**Ressalva sobre F10.** "Peso final zero" descreve o fim da série; o peso pode ter sido positivo antes, e a M1 pode voltar
a ser útil depois de uma mudança. Qualquer regra de economia precisa preservar a capacidade de reativação, e isso faz
parte do critério.

## 2. Mudanças propostas

Cada mudança é uma hipótese, com a falha que a motiva e um critério no banco de desenvolvimento. Os componentes não são
novos isoladamente (seção 5); o que se propõe é governá-los pelo mesmo regime de evidência e de custo declarado.

### M5. Custo proporcional ao uso (F10 e F1) — prioridade 1

Duas partes, medidas separadamente (ablação):

- **M5a — camadas.** Quando o peso de uma camada fica abaixo de um limiar por um período declarado, ela passa a ser
  atualizada com frequência reduzida (por exemplo, a regressão da M1 a cada 64 alvos em vez de 8), continuando a
  prever e a ser avaliada pela combinação; volta à frequência normal quando o peso sobe. A regra usa só o passado.
  Alternativas a comparar no desenho: frequência reduzida contínua; pausa com sondagens periódicas; custo da M1 em
  sombra só a cada k passos.
- **M5b — núcleo (F1).** Entradas nunca aceitas deixam de entrar no modelo base e passam a ser triadas com frequência
  reduzida; aprendizado e evidência podem pausar por uma regra que só usa o passado (pausar assim equivale a apostar zero
  nesses passos e preserva a validade do e-process; PRA-06).
- **Critérios no desenvolvimento:**
  - M5a: onde a M1 fica com peso zero (A01, A05, C03 e as famílias de desenvolvimento correspondentes), custo da M1
    reduzido em pelo menos 75%; onde a M1 ajuda (famílias abaixo da fronteira e bacias), razão de MSE v0.54 ÷ v0.53 com
    limite superior do IC 95% ≤ 1,01; num cenário sintético em que a relação útil para a M1 só aparece depois de um
    período sem ela, a M1 volta a pesar (critério numérico a fixar no rascunho da especificação, antes de medir).
  - M5b: em A01 e A12, custo com 50 entradas no máximo 1,5 vez o custo com 5, sem perda de recall e sem entradas falsas.
- **Encaixe:** muda a lei de custo de "cresce com d e paga todas as camadas" para "cresce com o que está em uso".

### M4 + M3. Remoções que acontecem e interpretação em séries não estacionárias (F2, F9) — prioridade 2

- **M4 — ideia:** redesenhar o teste de remoção. Hoje ele exige evidência de que remover **melhora** com margem fixa,
  o que é lento demais. Alternativas a comparar: remover quando a contribuição fica abaixo de um limiar declarado por um
  período, com erro controlado; testar a remoção como troca da unidade por sua referência trivial; testar a
  **persistência** da melhora (uma unidade aceita precisa continuar sustentada pela evidência).
- **M3 — ideia:** com remoções que funcionam, a melhora passageira que levou a uma aceitação espúria em níveis deixa de
  sustentá-la. Caminhos complementares, a escolher depois do primeiro desenho da M4: testar as hipóteses sobre as
  variações do alvo; tratar "diferenciar o alvo" como uma hipótese do próprio mecanismo.
- **Critérios no desenvolvimento:**
  - A05: a entrada antiga removida em pelo menos 14 de 20 séries depois da troca de regime (prazo a fixar no rascunho,
    antes de medir);
  - C03: entrada externa na estrutura final em no máximo 1 de 4 séries (também se reporta quantas foram aceitas em algum
    momento);
  - sem remoções falsas: em A01, nenhuma entrada verdadeira removida; A02 continua sem entradas falsas;
  - precisão: em todas as famílias de desenvolvimento, razão v0.54 ÷ v0.53 com limite superior ≤ 1,02.

### M6. Ciclo como hipótese (D02) — prioridade 3

- **Ideia:** em vez de o usuário declarar o ciclo, memórias sazonais candidatas (por exemplo 24 e 168 para dados
  horários; 7 para diários) viram hipóteses do mecanismo de experimentos, com a mesma evidência sempre válida. Primeiro
  uso do mecanismo para hipóteses sobre a **memória**, não sobre entradas; prepara a v0.55.
- **Critérios no desenvolvimento:** nas séries de D02 (B01, B02), sem declarar ciclo, erro no máximo 1,05 vez o da v0.53
  com o ciclo certo; com o ciclo declarado, nenhuma piora (limite superior ≤ 1,01); custo declarado; nenhuma memória
  sazonal aceita em séries sem ciclo (A02 e equivalentes).

**Fora da v0.54** (para a v0.55 ou depois): várias saídas e vários passos (expansão), atrasos acima de 31 passos (F3),
transformações não lineares como candidatas (F4), bloqueio de substitutas redundantes (F5), restos de maré com período
não inteiro (F7).

## 3. Processo e rigor

1. **Reservar os dados da avaliação final antes de qualquer código** (seção 6; decisão pendente).
2. **O LEBRE Lab continua como banco de desenvolvimento.** Cada mudança é medida em todos os cenários, com a v0.53
   (`lebre==0.2.0`) como referência. Plano commitado antes de cada medição.
3. **Uma mudança por vez, com ablação**, na ordem das prioridades. Cada M só fica se atender ao seu critério sem piorar
   as demais acima do declarado.
4. **Validações em dados novos**, cada conjunto escolhido só por metadados, congelado com SHA-256 e usado uma vez.
5. **Uma avaliação final pré-registrada** nos dados reservados, com a v0.54, a v0.53, SARIMAX com entradas e Chronos-2.
6. **Toda avaliação reporta a fronteira precisão × custo** e o perfil embarcado.

## 4. Critérios de sucesso da v0.54 (preliminares; fixados no pré-registro)

- **Sem piora** em relação à v0.53 em nenhuma família (régua por decidibilidade da v0.53, com os mesmos adendos).
- **Redução clara de custo:** custo mediano da v0.54 com intervalo de 95% abaixo do da v0.53 (a meta numérica, por
  exemplo 30% a menos, fica para o pré-registro, depois do desenvolvimento).
- **Estrutura:** pelo menos uma família reservada em que a remoção seja verificável, ou, se não houver, a evidência de M4
  fica declarada como só de desenvolvimento e validação.
- **Ciclo:** nas famílias reservadas com ciclo conhecido, a v0.54 sem ciclo declarado dentro de 1,05 vez a v0.54 com o
  ciclo certo.
- Nenhum aumento de entradas falsas nos testes negativos; memória estimada ≤ 128 KB.

## 5. Literatura e originalidade

> **Atualização 10/10/2026 (PRA-11 feita, `PRA_11_RELATORIO.md`):** nenhum trabalho encontrado antecipa as seis afirmações; há parciais próximos para M5a (M-LCB, Latypov et al. 2025), M5b e integração (ADOWIP, Wang 2026) e M4 (seleção online de variáveis com RLS, Souza e Araújo 2012). A contribuição continua sendo de integração.

Nenhum componente deve ser presumido novo. Busca rápida (10/10/2026, não sistemática): seleção de variáveis online
existe com penalização ou métodos bayesianos, sem remoção com teste sempre válido; há monitoramento sequencial de raiz
unitária (Steland; Wang), mas não o tratamento de regressão espúria no fluxo; detecção de período é em geral em lote ou
com período fixo (OneShotSTL); atualização seletiva e filtragem seletiva de dados reduzem custo em filtros adaptativos
(Gollamudi et al. 1998; Diniz 2008; PRA-06), mas não encontramos o desligamento do componente de peso nulo numa
combinação convexa. Não achar não prova originalidade: antes do rascunho da especificação, fazer uma busca formal
(**PRA-11**), com afirmações e consultas fixadas antes, como a PRA-05 da v0.52.

## 6. Reserva dos dados finais

> **Atualização 10/10/2026 (feita, antes de qualquer código):** `experiments/LEBRE-V0.54-DATA-01/` (`SPLIT_RULES.md`). Decisões do responsável pelo projeto: níveis da EIA e do Tesouro dos EUA; carga fora; evidência da M4 do desenvolvimento e das validações; solar por separação no tempo (as usinas solares elegíveis de 2024-2025 estavam esgotadas). Reservadas: 30 bacias, 30 prédios, 8 eólicas, 8 solares (jan-set/2026) e 17 séries de níveis (10 da EIA, 7 do Tesouro: as nominais de 1 a 30 anos já tinham sido usadas no Lab). Travas nos dois repositórios. A proposta original fica abaixo como registro.


Fazer antes de qualquer código, com hashes e travas nos dois repositórios, como em `LEBRE-V0.53-DATA-01`.

- **Mesmos domínios da v0.53 (para verificar "sem piora" e o custo):** CAMELS-BR nas posições 140+ da permutação; BDG2
  nas posições 115+; usinas solares e eólicas do ONS ainda não usadas.
- **Ciclo (M6):** as séries com ciclo conhecido acima (prédios 24 + 168; solar e eólica 24) servem para comparar a v0.54
  sem ciclo declarado com a v0.54 com o ciclo certo, na mesma execução.
- **Pontos que precisam de decisão:**
  1. **Níveis não estacionários (M3):** as moedas flutuantes do H.10 estão praticamente esgotadas. Alternativas de
     domínio público dos EUA: preços diários de energia da EIA; taxas do Tesouro americano em nível. É preciso escolher a
     fonte e conferir licença e disponibilidade antes de reservar.
  2. **Carga elétrica:** a carga de 2026 do ONS foi usada até setembro; a de outubro em diante ainda não tem extensão
     suficiente. Alternativas: deixar a carga fora da reserva da v0.54 ou esperar acumular dados.
  3. **Remoção (M4) em dados reais:** não há verdade conhecida sobre trocas de regime em séries reais; a proposta é que
     a evidência de M4 venha do desenvolvimento e das validações (sintéticas e semissintéticas), e a avaliação final
     verifique só que remover não piora.
  4. **Tamanho:** a v0.53 usou 104 séries; manter ordem de grandeza semelhante.

## 7. Próximos passos

1. ~~Decisão sobre a reserva e reserva dos dados finais~~: feitas em 10/10/2026 (`LEBRE-V0.54-DATA-01`).
2. ~~PRA-11~~: feita em 10/10/2026 (`PRA_11_RELATORIO.md`).
3. Rascunho da especificação, começando pela M5a, com os critérios numéricos que faltam fixados antes de medir.
