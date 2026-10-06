# LEBRE v0.53 — Nota de desenho 01: consolidar a base antes de expandir

**Data:** 05/10/2026 · **Status:** proposta, sem código e sem pré-registro. Nada aqui altera a v0.52 congelada.
**Base:** especificação v0.52-r1 e avaliação pré-registrada (reserva 3); testes exploratórios do LEBRE Lab (projeto
`lebre-lab`, ainda não publicado: 29 execuções registradas em 04/10/2026 sobre a biblioteca `lebre==0.1.0`).

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
| F7 | Maré meteorológica: pior que a persistência em 3 de 6 estações | `20261004-183352_B07` | Média |
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

- **Ideia:** um terceiro especialista na combinação que a LEBRE já faz (hoje memória e modelo estrutural): uma regressão
  recursiva (RLS) **só nas k entradas de maior correlação** atual, com k pequeno e fixo (custo O(k²)).
- **Regime de evidência:** o especialista entra em sombra e só passa a pesar na previsão quando o e-process mostrar melhora
  sobre a combinação vigente, como qualquer mudança estrutural.
- **Custo:** com k = 3, cerca de 30 a 40 operações por passo a mais (a confirmar na lei de custo).
- **Critério no banco de desenvolvimento:** B03 com erro no máximo 1,05 vez o do linear online, sem piorar mais de 2% em
  B01 e B02.

### M2. Referência trivial como ponto de partida (F8) — prioridade 2

- **Ideia:** a previsão começa na referência mais simples declarada (zero para variações; persistência ou sazonal ingênuo
  para níveis) e a parte adaptativa só ganha peso com evidência de melhora sobre ela.
- **Encaixe:** é o mesmo princípio das mudanças estruturais aplicado à própria previsão: a LEBRE como um todo vira um
  desafiante da referência trivial.
- **Critério:** C01 e C04 com erro no máximo 1,01 vez o de prever zero; nenhuma piora acima de 2% nos cenários em que a
  v0.52 venceu a referência.

### M3. Não estacionariedade (F9) — prioridade 3, começa por diagnóstico

> **Atualização 06/10/2026 (diagnóstico, `experiments/LEBRE-V0.53-DIAG-F9-01/RESUMO.md`):** as entradas espúrias mudaram o erro em menos de 1%, e a LEBRE sem entradas perde para o passeio aleatório na mesma medida. Em precisão, F9 é o mesmo problema de F8 e fica com M2; M3 cai de prioridade e trata só da interpretação das entradas aceitas.

- **Primeiro, entender:** nos níveis de preço, a melhora que levou às aceitações foi real e passageira (tendências comuns
  por um tempo) ou um artefato? O e-process mede melhora preditiva no fluxo; ele pode estar certo sobre o que mede e a
  melhora não durar.
- **Caminhos possíveis, a escolher depois do diagnóstico:** testar as hipóteses sobre as variações do alvo; tratar
  "diferenciar o alvo" como uma hipótese do próprio motor; ou exigir que a melhora persista (remoção que funcione, M4).
- **Critério:** C03 sem entradas aceitas em pelo menos 3 de 4 séries e erro no máximo 1,02 vez o do passeio aleatório.

### M4. Remoções que acontecem (F2) — prioridade 4

- **Ideia:** redesenhar o teste de remoção. Hoje ele exige evidência de que remover **melhora** com margem fixa, o que é
  lento demais. Alternativas: remover quando a contribuição fica abaixo de um limiar declarado por um período (com custo
  de erro controlado), ou testar a remoção como troca pela referência trivial da unidade.
- **Critério:** em A05, a entrada antiga removida em pelo menos 14 de 20 séries depois da troca de regime, sem remoções
  falsas em A01 e A02.

### M5. Custo proporcional ao uso e à surpresa (F1) — prioridade 5

- **Ideia:** entradas nunca aceitas deixam de entrar no modelo base e passam a ser triadas com frequência reduzida;
  aprendizado e evidência podem pausar em trechos sem surpresa, por uma regra previsível (pausas por regra previsível
  preservam a validade do e-process; a referência a conferir é Choe e Ramdas, apêndice F.1).
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

1. **Reservar os dados da avaliação final antes de qualquer código** (`experiments/LEBRE-V0.53-DATA-01/`): séries e
   períodos que nem a pesquisa da v0.52 nem o LEBRE Lab tocaram, com regras de separação e hashes commitados. Candidatos
   naturais: usinas e subsistemas do ONS não usados no Lab e o ano de 2026; hidrologia e prédios fora das reservas 1 a 3.
2. **O LEBRE Lab vira banco de desenvolvimento.** Cada mudança é medida em todos os cenários A a D, com os números da
   v0.52 como referência. Ao ser usado para desenvolver, o Lab deixa de ser evidência independente sobre a v0.53.
3. **Uma mudança por vez, com ablação.** Cada M entra sozinha, é medida e só fica se atender ao seu critério sem piorar
   os demais acima do declarado.
4. **Uma avaliação final pré-registrada** nos dados reservados, com quatro modelos: v0.53, v0.52, SARIMAX com entradas e
   Chronos-2 com covariáveis. Ela responde de uma vez se a v0.52 é útil nos domínios reservados (reforça o artigo) e se
   a v0.53 melhora sobre ela.
5. **Toda avaliação reporta a fronteira precisão × computação** e o perfil embarcado, como no contrato de complexidade.

## 5. Critérios de sucesso da v0.53 (preliminares; fixados no pré-registro)

- Nos dados reservados, erro menor que o da v0.52 (média geométrica), com custo médio no máximo 1,25 vez o dela.
- Nenhuma família de séries com piora acima de 5% em relação à v0.52.
- Nos cenários nulos do Lab e nos testes negativos financeiros, nenhum aumento de entradas falsas.
- Perfil embarcado mantido (cabe no mesmo microcontrolador simulado).

## 6. Literatura e originalidade

Nenhum componente é novo: especialistas RLS e combinação dinâmica de modelos, encolhimento para uma previsão de
referência, diferenciação de séries não estacionárias, triagem com frequência reduzida e cálculo adaptativo existem
separadamente. A contribuição continua sendo de **integração**: o mesmo regime de evidência sempre válida e de custo
declarado governando também a parte adaptativa. Antes de afirmar qualquer ineditismo, repetir a busca de trabalhos
anteriores feita para a v0.52 (`experiments/LEBRE-V0.52-DESIGN-NOTE-01/DESIGN_NOTE_02_COMPUTE_BOUNDED.md`).

## 7. Próximos passos

1. Decisão de escopo (seção 2).
2. Reserva dos dados finais (`LEBRE-V0.53-DATA-01`), antes de qualquer código.
3. Diagnóstico de F9 (M3) e busca de trabalhos anteriores para M1, M2 e M5.
4. Rascunho da especificação do algoritmo, mudança por mudança, a partir das prioridades acima.
