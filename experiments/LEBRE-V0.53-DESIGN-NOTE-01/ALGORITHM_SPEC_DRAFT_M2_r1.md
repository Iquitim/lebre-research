# LEBRE v0.53 — Rascunho da especificação, parte 1: M2, rascunho 1

**Data:** 08/10/2026 · **Status:** rascunho 1, antes de qualquer código desta revisão. **Substitui** o rascunho 0
(`ALGORITHM_SPEC_DRAFT_M2.md`) nos três pontos abaixo; o restante do rascunho 0 continua valendo.
**Motivo:** a medição do rascunho 0 no LEBRE Lab (`M2_DEV_RESULTADO.md`) não escolheu nenhuma configuração; as falhas
foram C05 (critério 2) e B06 (critério 5).

## 1. Mudança A: orçamento de erro próprio para a porta

**Problema (B06):** compartilhar a sequência e-LOND da estrutura faz cada hipótese e cada troca da porta deslocarem os
níveis das hipóteses estruturais seguintes. A porta passa a mudar quais entradas a LEBRE aceita, e com isso o custo.

**Mudança:** a porta usa um **motor de evidência próprio** (mesma classe da v0.52, `ChangeEngine`), com orçamento
α_porta, família de tamanho 2 (promover e rebaixar) e sua própria sequência de níveis. A estrutura fica com o motor e o
α = 0,05 da v0.52, **intocados**: o caminho estrutural da v0.53 é idêntico ao da v0.52.

**Garantia (atualizada):** cada fluxo controla a sua taxa de descobertas falsas (estrutura em α = 0,05; porta em
α_porta), nas mesmas condições da v0.52. Para a união dos dois fluxos, com V decisões falsas e R decisões:
(V₁ + V₂) / max(R₁ + R₂, 1) <= V₁ / max(R₁, 1) + V₂ / max(R₂, 1), porque se R_i = 0 então V_i = 0 e, se ambos forem
positivos, cada fração cresce ao trocar o denominador conjunto pelo próprio. Tomando a esperança, a taxa de descobertas
falsas da união é no máximo **0,05 + α_porta**. A garantia global declarada passa a ser essa soma.

**α_porta:** a escolher no desenvolvimento entre {0,01; 0,05} (seção 4). Um valor menor dá menos trocas falsas e
promoções mais lentas.

## 2. Mudança B: a porta observa mesmo quando só as entradas estão fora do contrato

**Problema (C05):** na v0.52, quando uma entrada sai da faixa do contrato, os passos seguintes entram em quarentena
(nenhum aprendizado estrutural nem evidência). Numa série curta isso se repete e a porta viu só 147 de 359 passos.

**Mudança:** a porta observa todo passo com alvo observado, **exceto** quando o próprio alvo vem marcado em quarentena
pela fonte (`quarantine=True` em `observe`). A quarentena por entradas fora do contrato continua valendo para a
estrutura, como na v0.52.

**Por que é válido:** a escolha dos passos observados depende só das entradas, que são conhecidas antes do alvo; pular ou
não um passo por uma regra previsível equivale a apostar zero nele e não afeta a validade do e-process (PRA-06). A
hipótese passa a ser sobre todos os passos com alvo observado não marcado, inclusive os de entradas fora do contrato,
que é exatamente quando importa saber se a LEBRE ainda é melhor que a referência.

**Por que a quarentena da estrutura não muda:** ela protege o aprendizado de pesos com entradas suspeitas; a porta não
aprende pesos, só compara duas previsões já feitas.

## 3. Mudança C: margem, recriação e séries curtas

- **ε_porta = 0,002 e hipóteses recriadas** fixados: no rascunho 0 as 6 combinações deram resultados quase iguais. É uma
  decisão de simplicidade, não um resultado.
- **Séries curtas:** nenhuma regra nova. Se, com as mudanças A e B, C05 continuar falhando, a limitação é declarada ("em
  séries de poucas centenas de passos a porta pode não chegar a promover a LEBRE; desligue-a com `porta=False`") em vez
  de acrescentar outro parâmetro. Não se ajusta nada para fazer C05 passar.

## 4. Medição (plano próprio no LEBRE Lab, escrito antes de rodar)

- **Configurações:** α_porta ∈ {0,01; 0,05}; as demais escolhas fixas como acima.
- **Critérios:** os 5 do rascunho 0 (seção 7), mais um de implementação:
  6. **Caminho estrutural idêntico:** em todas as séries, os eventos estruturais (exceto os da porta) e o custo da parte
     v0.52 são iguais aos da v0.52 sem porta.
- **Regra de escolha:** entre as configurações que atendem aos 6 critérios, a de menor média geométrica de M2 ÷
  referência nas famílias negativas; empate (< 0,001) decide pelo menor α_porta. Se nenhuma atender, nenhuma é
  escolhida e as falhas são declaradas.
- **Reprodutibilidade do rascunho 0:** o protótipo mantém as opções do rascunho 0 (motor compartilhado e sem observar na
  quarentena por entradas) para que os resultados de `M2_DEV_RESULTADO.md` possam ser reproduzidos.

## 5. Resultado no banco de desenvolvimento (08/10/2026)

Medição no LEBRE Lab (`M2_DEV_R1_PLANO.md`, `M2_DEV_R1_RESULTADO.md`; protótipo `9bfdd0d`):

- **Nas 21 famílias que não são C05, as duas configurações atendem aos 6 critérios:** nas negativas a saída fica na
  referência (razão 1,000); onde a v0.52 vence, o pior limite superior de M2 ÷ v0.52 é 1,001; no máximo 0,48 troca por
  2.000 passos; acréscimo de custo de no máximo 18,4 FP por passo; caminho estrutural idêntico ao da v0.52 em todas as
  séries.
- **C05 falha nas duas** (critérios 2 e 3). Pela regra do plano, **nenhuma configuração é escolhida**, e C05 vira
  limitação declarada: em séries de poucas centenas de passos a porta pode promover a LEBRE tarde demais (ali, entre os
  passos 200 e 260 de 360); recomendação: `porta=False` nesses casos.
- **α_porta = 0,01 e 0,05** diferem só na velocidade da primeira promoção e na garantia global (0,06 contra 0,10).

## 6. Decisão de projeto (não é resultado de medição)

Como a medição não distingue as duas configurações fora de C05, a escolha de α_porta é uma decisão de projeto:
**proposta α_porta = 0,01**, pela garantia global mais forte (taxa de descobertas falsas da união <= 0,06), aceitando
promoções um pouco mais lentas. A decisão é do responsável pelo projeto e será testada, como tudo, na avaliação final
pré-registrada na reserva.
