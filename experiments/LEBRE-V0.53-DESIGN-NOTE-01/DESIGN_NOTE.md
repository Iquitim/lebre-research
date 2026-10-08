# LEBRE v0.53 — Nota de desenho 01: consolidar a base antes de expandir

**Data:** 05/10/2026 · **Status:** proposta, sem código e sem pré-registro. Nada aqui altera a v0.52 congelada.
**Base:** especificação v0.52-r1 e avaliação pré-registrada (reserva 3); testes exploratórios do LEBRE Lab (projeto
`lebre-lab`, ainda não publicado: 29 execuções registradas em 04/10/2026 sobre a biblioteca `lebre==0.1.0`, e depois
os protótipos D04 e D05 e a análise de incerteza, de 06 e 07/10). Revisão antes da especificação: `REVISAO_2026-10-07.md`.

## 0. Resumo

Na avaliação pré-registrada, a v0.52 teve o menor erro entre os comparadores leves e empatou com um SARIMAX por série,
a algumas centenas de operações por passo (o contrato de custo declarado foi perdido por pouco). Os testes
do LEBRE Lab mostraram **onde ela falha**, e várias falhas têm a mesma raiz: a parte que **se adapta continuamente**
(memória e modelo base) não tem o mesmo cuidado da parte que **muda de estrutura**, que só age com evidência. Esta
nota propõe que a v0.53 estenda o princípio central da LEBRE (mudar só com evidência de melhora preditiva, a custo
conhecido) a essa parte, antes de expandir o escopo para multissaída e previsão de vários passos.

## 1. De onde vem a proposta

Evidência exploratória do LEBRE Lab (versão congelada `lebre==0.1.0`, comparadores simples, critérios escritos antes de
rodar). Exploratória quer dizer: orienta o desenho, mas não prova nada sozinha.

| Falha | O que se viu | Execução | Gravidade |
|---|---|---|---|
| F6 | Relação quase exata com uma entrada no mesmo instante: erro 5,5 vezes o de uma regressão recursiva (benzeno; 2,1 vezes na média de 4 poluentes) | `20261004-183309_B03` | Alta |
| F9 | Níveis de preço (não estacionários): entradas aceitas em 4 de 4 séries, erro 7% acima do passeio aleatório | `20261004-184216_C03` | Alta |
| F8 | Séries sem nada a aprender: erro 5% a 7% acima de prever zero, nenhuma entrada espúria aceita | `20261004-184211_C01`, `20261004-184218_C04` | Média |
| F2 | Nenhuma remoção aceita, nem na pesquisa nem no Lab; após troca de regime a entrada antiga fica | `20261004-180630_A05` | Média |
| F1 | Custo cresce com o número de entradas, mesmo das que nunca são aceitas (~3.160 operações com 50 entradas) | `20261004-181040_A12` | Média |
| F7 | Maré meteorológica: pior que a persistência em 3 de 6 estações (no conjunto, melhor: 0,941; IC 0,929–0,953) | `20261004-183352_B07` | Média |
| F3–F5 | Atrasos acima de 31 passos, relações simétricas (x²), substituta redundante com correlação 0,8 | A03, A04, A10 | Baixa |

Dois resultados de ensemble indicam caminhos:
- **D03** (`20261004-191202_D03`): combinar a LEBRE com uma regressão recursiva e um ingênuo, por pesos online, reduziu o
  erro em 49% na qualidade do ar (cobre F6), ao preço de 4% a 9% onde a LEBRE já era a melhor.
- **D02** (`20261004-190435_D02`): combinar LEBREs com ciclos diferentes chegou a 3,8% de declarar o ciclo certo, contra
  um erro 1,9 vez maior ao não declarar ciclo.

**Diagnóstico comum (hipótese a confirmar):** F6, F8 e parte de F7 e F9 vêm de componentes que se ajustam sempre, sem
teste: o modelo base (NLMS, passo pequeno) e a memória. A mudança de estrutura, que só age com evidência, se comportou
bem em todos os testes nulos (0 entradas falsas em retornos, juros e no cenário sintético nulo).

## 2. Decisão de escopo (para o responsável pelo projeto)

O roteiro de 26/09/2026 previa para a v0.53 **multissaída e previsão de vários passos** (evidência sobre previsões
encadeadas). Esta nota propõe **inverter a ordem**:

- **v0.53 = consolidação:** mesma tarefa (um alvo, um passo), corrigindo F6, F8, F9, F2 e F1 dentro do contrato de
  complexidade, com cálculo proporcional à surpresa (já previsto para a v0.53) como forma de atacar F1.
- **v0.54 = expansão:** multissaída e vários passos, sobre uma base que não perde para comparadores simples nos casos
  conhecidos.

**Por quê:** expandir sobre uma base com F6 e F9 levaria as mesmas falhas para um problema maior, onde seriam mais
difíceis de isolar. **Contra:** atrasa a parte mais próxima da ambição de modelo de mundo. A decisão é do responsável
pelo projeto; o restante desta nota supõe a consolidação.

## 3. Mudanças propostas

Cada mudança é uma hipótese, com a falha que a motiva e um critério no banco de desenvolvimento. Os componentes não são
novos isoladamente (ver seção 6); o que se propõe é integrá-los ao mesmo regime de evidência e de custo da v0.52.

### M1. Especialista de precisão (F6) — prioridade 1

> **Atualização 08/10/2026 (validação 4, LEBRE Lab `analises/M1_VAL4_RESULTADO.md`):** o rascunho 2
> (`ALGORITHM_SPEC_DRAFT_M1_r2.md`), aprovado no desenvolvimento (E12), **não é confirmado**. Em Y-B03 (qualidade do ar de
> Pequim, dados novos) a meta de fronteira é atendida pela regra, mas sem contribuição da M1 (1,221 contra 1,225 da v0.52
> sozinha, que já atenderia), com custo de 1,94 vez a v0.52. Em Y-B01 a M1 piora uma série solar em 19,5% (família 1,030;
> limite 1,02). Evidência atual: o ganho da M1 em B03 não se reproduziu em dados novos.

> **Atualização 08/10/2026:** custo recontado (~160-190 FP por passo na versão completa, não 30-40). Decisão do responsável
> pelo projeto: **M1 enxuta**, com atualizações a cada 8 passos (~70 + d FP); entra pelo (A,B)-Prod, como a M2, em vez de
> um teste. Especificação: `ALGORITHM_SPEC_DRAFT_M1.md`.

- **Ideia:** um terceiro especialista na combinação que a LEBRE já faz (hoje memória e modelo estrutural): uma regressão
  recursiva (RLS) **só nas k entradas de maior correlação** atual, com k pequeno e fixo (custo O(k²)).
- **Regime de evidência:** o especialista entra em sombra e só passa a pesar na previsão quando o e-process mostrar melhora
  sobre a combinação vigente, como qualquer mudança estrutural.
- **Custo:** com k = 3, cerca de 30 a 40 operações por passo a mais (a confirmar na lei de custo).
- **Critério no banco de desenvolvimento:** B03 com erro no máximo 1,05 vez o do linear online, sem piorar mais de 2% em
  B01 e B02.

### M2. Referência trivial como ponto de partida (F8) — prioridade 2

> **Atualização 08/10/2026 (validação 4: deixa de estar resolvida):** sem a M1, a candidata P falha no critério 1 em
> Y-C01 (câmbio 1990-1999: 1,007, limite superior 1,016 > 1,01; baht 1,024) e em Y-B07 (uma série, Portland: limite
> superior 1,020). A aprovação na validação 3 não se generalizou (LEBRE Lab,
> `diagnosticos/M1_VAL4_ATRIBUICAO_RESULTADO.md`). A atualização abaixo fica como registro histórico.

> **Atualização 08/10/2026 (resolvida no desenvolvimento e na validação 3):** depois de 11 desenhos (18 configurações), a
> candidata P (`M2_CANDIDATA_P.md`: (A,B)-Prod anytime com AdaHedge sobre o erro quadrático como referência de confiança e
> switch distribution num só sentido como oportunista) passou em todos os critérios nas 43 famílias de desenvolvimento e na
> validação 3, com a régua por decidibilidade e custo de 129-134 FP por passo (limite de 150 decidido pelo responsável pelo
> projeto). **Tensão declarada:** a seção 5 pede custo médio da v0.53 <= 1,25 vez o da v0.52; só a M2 já pode levar séries
> baratas a ~1,7 vez. A M5 (redução de custo) passa a ser necessária, e o limite final será decidido no pré-registro.

> **Atualização 06/10/2026 (protótipo no LEBRE Lab, D04, `20261006-063405_D04`):** uma porta simples (média exponencial da diferença de perda, alfa = 0,01) reduziu a perda contra a referência de 6,9% para 1,5% (retornos), de 6,8% para 3,8% (níveis) e de 5,2% para 0,3% (juros), sem perda na carga e na solar (1,000 contra a LEBRE). Não atingiu a margem declarada de 1% em retornos e níveis. Direção para a especificação: trocar a média exponencial por uma decisão governada pelo mesmo e-process das mudanças estruturais.

> **Atualização 07/10/2026 (teste amplo D05 e incerteza, LEBRE Lab `analises/INCERTEZA_RESULTADO.md`):** em 19 famílias onde a LEBRE vence a referência (corrigido de "20" na revisão de 07/10), a porta não piorou mais que 0,7% (limite superior do intervalo de 95% de no máximo 1,015 nas famílias reais). Nos testes negativos, a porta ainda é pior que a referência em retornos (1,015; IC 1,004–1,031) e níveis (1,038; IC 1,009–1,057); em juros, inconclusivo (1,003; IC 0,991–1,016). O MSE recalculado reproduziu exatamente as execuções originais. Requisito da literatura (PRA-06): a comparação por e-process exige perda limitada (o recorte da v0.52) ou os métodos para escores não limitados.

- **Ideia:** a previsão começa na referência mais simples declarada (zero para variações; persistência ou sazonal ingênuo
  para níveis) e a parte adaptativa só ganha peso com evidência de melhora sobre ela.
- **Encaixe:** é o mesmo princípio das mudanças estruturais aplicado à própria previsão: a LEBRE como um todo vira um
  desafiante da referência trivial.
- **Critério (revisado em 07/10, com a regra de incerteza do Lab):** em C01, C03 e C04, limite superior do intervalo de
  95% da razão contra a referência (zero ou passeio aleatório) <= 1,01; em todas as famílias em que a v0.52 vence a
  referência, limite superior da razão contra a v0.52 <= 1,02. C03 passou de M3 para cá depois do diagnóstico F9.

### M3. Não estacionariedade (F9) — prioridade 3, começa por diagnóstico

> **Atualização 06/10/2026 (diagnóstico, `experiments/LEBRE-V0.53-DIAG-F9-01/RESUMO.md`):** as entradas espúrias mudaram o erro em menos de 1%, e a LEBRE sem entradas perde para o passeio aleatório na mesma medida. Em precisão, F9 é o mesmo problema de F8 e fica com M2; M3 cai de prioridade e trata só da interpretação das entradas aceitas.

- **Primeiro, entender:** nos níveis de preço, a melhora que levou às aceitações foi real e passageira (tendências comuns
  por um tempo) ou um artefato? O e-process mede melhora preditiva no fluxo; ele pode estar certo sobre o que mede e a
  melhora não durar.
- **Caminhos possíveis, a escolher depois do diagnóstico:** testar as hipóteses sobre as variações do alvo; tratar
  "diferenciar o alvo" como uma hipótese do próprio motor; ou exigir que a melhora persista (remoção que funcione, M4).
- **Critério (revisado em 07/10):** C03 com entrada externa aceita em no máximo 1 de 4 séries. A parte de precisão foi
  para M2.

### M4. Remoções que acontecem (F2) — prioridade 4

- **Ideia:** redesenhar o teste de remoção. Hoje ele exige evidência de que remover **melhora** com margem fixa, o que é
  lento demais. Alternativas: remover quando a contribuição fica abaixo de um limiar declarado por um período (com custo
  de erro controlado), ou testar a remoção como troca pela referência trivial da unidade.
- **Critério:** em A05, a entrada antiga removida em pelo menos 14 de 20 séries depois da troca de regime, sem remoções
  falsas em A01 e A02.

### M5. Custo proporcional ao uso e à surpresa (F1) — prioridade 5

- **Ideia:** entradas nunca aceitas deixam de entrar no modelo base e passam a ser triadas com frequência reduzida;
  aprendizado e evidência podem pausar em trechos sem surpresa, por uma regra previsível (pausar por uma regra que só
  usa o passado equivale a apostar zero e preserva a validade do e-process; ver PRA-06, que substitui a indicação
  anterior, não verificada, a um apêndice de Choe e Ramdas).
- **Encaixe:** muda a lei de custo de "cresce com d" para "cresce com o que está em uso", e mantém o perfil embarcado.
- **Critério:** em A01 e A12, custo com 50 entradas no máximo 1,5 vez o custo com 5, sem perda de recall.

### M6. Ciclo como hipótese (D02) — prioridade 6, opcional

- **Ideia:** em vez de o usuário declarar o ciclo, memórias sazonais candidatas viram hipóteses do motor de experimentos.
- **Valor:** primeiro uso do motor para hipóteses sobre a **memória**, não sobre entradas; prepara a generalização.
- **Critério:** em B01 e B02, sem declarar ciclo, erro no máximo 1,05 vez o da v0.52 com o ciclo certo.

**Fora da v0.53** (para a v0.54 ou depois): atrasos acima de 31 passos (F3), transformações não lineares como candidatas
(F4), bloqueio de substitutas redundantes (F5), restos de maré com período não inteiro (F7). Cada uma amplia o espaço de
hipóteses, e com isso o custo; ficam melhor junto com a expansão.

## 4. Processo e rigor

1. **Reservar os dados da avaliação final antes de qualquer código** (`experiments/LEBRE-V0.53-DATA-01/`, feito em
   05/10/2026: CAMELS-BR e BDG2 nas posições seguintes da v0.52, 16 usinas do ONS, carga de 2026 e 8 pares de câmbio,
   com hashes e travas nos dois repositórios).
2. **O LEBRE Lab vira banco de desenvolvimento.** Cada mudança é medida em todos os cenários A a D, com os números da
   v0.52 como referência. Ao ser usado para desenvolver, o Lab deixa de ser evidência independente sobre a v0.53.
3. **Uma mudança por vez, com ablação.** Cada M entra sozinha, é medida e só fica se atender ao seu critério sem piorar
   os demais acima do declarado.
4. **Uma avaliação final pré-registrada** nos dados reservados, com quatro modelos: v0.53, v0.52, SARIMAX com entradas e
   Chronos-2 com covariáveis. Ela responde de uma vez se a v0.52 é útil nos domínios reservados (reforça o artigo) e se
   a v0.53 melhora sobre ela.
5. **Toda avaliação reporta a fronteira precisão × computação** e o perfil embarcado, como no contrato de complexidade.

## 5. Critérios de sucesso da v0.53 (preliminares; fixados no pré-registro)

- Nos dados reservados, erro menor que o da v0.52 (média geométrica, com intervalo de 95% todo abaixo de 1), com custo
  médio no máximo 1,25 vez o dela.
- Nenhuma família de séries com piora acima de 5% em relação à v0.52.
- Nos cenários nulos do Lab e nos testes negativos financeiros, nenhum aumento de entradas falsas.
- Perfil embarcado mantido (cabe no mesmo microcontrolador simulado).

## 6. Literatura e originalidade

Nenhum componente é novo: especialistas RLS e combinação dinâmica de modelos, encolhimento para uma previsão de
referência, diferenciação de séries não estacionárias, triagem com frequência reduzida e cálculo adaptativo existem
separadamente. A contribuição continua sendo de **integração**: o mesmo regime de evidência sempre válida e de custo
declarado governando também a parte adaptativa. Antes de afirmar qualquer ineditismo, repetir a busca de trabalhos
anteriores feita para a v0.52 (`experiments/LEBRE-V0.52-DESIGN-NOTE-01/DESIGN_NOTE_02_COMPUTE_BOUNDED.md`). Uma busca
rápida e dirigida para M1, M2 e M5 está em `PRA_06_V053.md` (06/10/2026): as três têm antecedentes diretos.

## 7. Próximos passos

1. ~~Decisão de escopo (seção 2)~~: consolidação aceita em 05/10/2026.
2. ~~Reserva dos dados finais~~: feita em 05/10/2026.
3. ~~Diagnóstico de F9 e busca de trabalhos anteriores~~: feitos em 06 e 07/10/2026 (`LEBRE-V0.53-DIAG-F9-01`,
   `PRA_06_V053.md`); protótipo de M2 testado no Lab (D04, D05) com incerteza medida.
4. Rascunho da especificação do algoritmo, mudança por mudança, começando por M2 (rascunho 0 de M2 em
   `ALGORITHM_SPEC_DRAFT_M2.md`, 07/10/2026). Limites a levar em conta:
   `REVISAO_2026-10-07.md`, seções 4 e 5.
