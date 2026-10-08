# M2 da v0.53: candidata S (switch distribution), especificação antes do código

**Data:** 08/10/2026. **Base:** a candidata D (`M2_CANDIDATA_D.md`) passou em 9 de 10 famílias da validação 2 e falhou
numa usina que começa a gerar no meio da série (Abaiara), em que a LEBRE leva ~800 passos para aprender e o déficit dessa
fase prende os pesos na referência (dificuldade D1 de `REFLEXAO_M2.md`). **Oitava configuração da M2.**

## 1. Literatura (lida no original)

van Erven, Grünwald e de Rooij (2012), *JRSS-B* 74(3):361–417 (versão do autor de 07/07/2011), seções 1–3: o
"catch-up phenomenon" é exatamente D1 (um modelo que aprende começa pior e fica melhor; médias bayesianas trocam tarde
porque o posterior depende da **altura** da diferença acumulada, não da inclinação). A **switch distribution** é uma
mistura bayesiana sobre sequências de previsores com trocas em instantes t₁ = 1 < t₂ < ...; prioridade (eq. 10–11):
número de trechos μ(m) = 2^{−m}, instantes de troca τ(t) = 1/(t(t − 1)), previsor de cada trecho uniforme; cálculo exato
em tempo linear como algoritmo forward de um modelo oculto de Markov (seção 2.3). Domina a média bayesiana por um fator
constante μ(1) = ½ (seção 2.4).

**Conta própria (a conferir nos testes):** com τ(t) = 1/(t(t − 1)), a chance de o trecho atual acabar e um novo começar
no passo t, dado que não acabou antes, é exatamente 1/t; com μ geométrico, cada trecho é o último com chance ½.

## 2. A candidata S

- **Previsores como densidades com variância comum:** N(f_k, σ̂²) para R e L, com σ̂² = máx(mín(σ²_R, σ²_L), piso²),
  σ²_k = média exponencial (LAM = 0,99, da v0.52) dos erros quadráticos passados de cada previsor (só passado), piso como
  na porta (SCALE_FLOOR, a partir do passo 200). Com variância comum, a diferença de log-verossimilhança entre R e L é
  (e²_R − e²_L)/(2σ̂²): o **erro quadrático**, a régua dos critérios (lição de E1 e E2).
- **Pesos:** posterior da switch distribution com a prioridade (11) do artigo, sem parâmetros livres e sem taxa de
  aprendizado a ajustar (mistura bayesiana; não há o ciclo entre "mixability gap" e η que derrubou o rascunho 6).
- **Saída:** média ponderada de R e L pelos pesos do posterior. **Comparação só com a referência definida** (como em D).
  Primeira rodada só inicializa as escalas.
- **Auditoria e estrutura:** como em D.

## 3. Garantias e limites

- Perda logarítmica (gaussiana de variância σ̂²): a switch distribution perde para qualquer sequência de previsores com
  m trechos no máximo −ln π(s) (domina cada q_s pelo fator π(s)); trocar no instante t custa ~2 ln t + ln 4 nats.
- A saída pontual é a média da mistura; para o erro quadrático não há garantia equivalente. A escolha de σ̂ é de
  modelagem (declarada).
- Custo estimado: ~45 FP por passo para os pesos, mais ~18 da auditoria.

## 4. Medição

1. **Desenvolvimento (E3):** banco de desenvolvimento, validação 1 e validação 2 (todas já gastas para seleção), com a
   régua por decidibilidade de `M2_CANDIDATA_D.md`. Plano commitado antes de rodar.
2. Se S atender a todos os critérios em todas as famílias: **validação 3** nova, regras antes do download, congelada,
   usada uma vez. Depois, a reserva (v0.53 completa).
