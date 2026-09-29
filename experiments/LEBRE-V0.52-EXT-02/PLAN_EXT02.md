# LEBRE v0.52 — EXT-02: verificações adicionais antes da redação final (plano declarado antes de rodar)

**Data:** 27/09/2026. **Regras:**
- a v0.52 está congelada; os módulos são só **importados**, na configuração canônica (`EXT-01/heldout2_cfg.CANONICAL`);
- nada é ajustado; nenhum resultado desta pasta muda o modelo;
- o documento só pode afirmar o que for medido aqui, com o rótulo correto (simulação, exploratório etc.).

## 1. Simulação do controle de mudanças falsas (sintética, sem dados reais)

**Pergunta.** Na configuração congelada, o fluxo de decisões controla na prática a fração de mudanças falsas?

O fluxo tem estas características:
- hipóteses persistentes;
- decisões assíncronas a cada 10 passos;
- níveis tipo e-LOND;
- referência aprendida online, com desajuste.

A simulação mede o controle em cenários com dependência temporal, correlação entre entradas, heterocedasticidade, caudas pesadas e quebra de variância. A garantia teórica **não** é afirmada, porque a nula do teste depende do desajuste (§7 do documento). Esta é uma verificação empírica.

**Entradas sintéticas.** d = 4 entradas exógenas, T = 30.000 passos.
- Cada entrada é x_i = 0,7·f_i + 0,71·u_i (correlação ~0,5 entre entradas):
  - f é um fator comum AR(1) com coeficiente ρ;
  - u_i são AR(1) independentes com o mesmo ρ;
  - variância unitária.
- Dois níveis de persistência: ρ ∈ {0,5; 0,95}.
- As entradas passam pelo mesmo padronizador causal usado nas avaliações.

**Cenários** (ruído e ~ N(0,1), salvo indicação):

| Cenário | Alvo | Verdade (unidades exógenas) |
|---|---|---|
| N1 nulo global | y = e | nenhuma; **qualquer** mudança aceita é falsa (inclui próprio passado e estado latente) |
| N2 nulo exógeno, alvo autocorrelacionado | y = v, v = 0,9·v(t−1) + √0,19·e | nenhuma exógena (próprio passado e estado latente são estrutura real) |
| N3 nulo heterocedástico | y = σ_t·e, σ_t = exp(0,5·x1(t))/c (média condicional 0) | nenhuma |
| N4 nulo com quebra de variância | y = e, com desvio-padrão 1 até T/2 e 2 depois | nenhuma; qualquer mudança é falsa |
| P1 parcial | y = 0,5·x0(t−6) + e | {x0} |
| P2 parcial com isca correlacionada | y = 0,5·x0(t−6) + e, com x1 substituída por 0,7·x0 + 0,71·u (correlação ~0,7, abaixo do limiar de grupo 0,95) | {x0} |
| P3 parcial, ruído dependente e de cauda pesada | y = 0,5·x0(t−6) + v, v = 0,8·v(t−1) + 0,6·t₃/√3 | {x0} |

**Contagem.** A contagem é feita sobre mudanças aceitas do tipo acrescentar ou trocar (a unidade que entra) e do tipo remover (a unidade que sai). As divisões hierárquicas são refinamentos de uma unidade já aceita e são contadas à parte.
- **Mudança exógena falsa:**
  - acrescentar ou trocar para uma entrada exógena fora da verdade;
  - remover uma entrada verdadeira.
- **Nos nulos N1 e N4:** qualquer mudança aceita é falsa.
- **Por execução:**
  - V = número de mudanças falsas;
  - R = número total de mudanças aceitas (sem divisões);
  - FDP = V / max(R, 1).
- **Por cenário:**
  - fração de execuções com V ≥ 1, com IC de Clopper-Pearson a 95%;
  - FDR estimado = média do FDP, com IC por bootstrap;
  - taxa de descoberta da verdade nos cenários P.

**Tamanho e sementes.**
- 2 níveis de ρ × 50 sementes por cenário = 100 execuções por cenário, 700 no total.
- Sementes: 8201 + 1000·(índice do cenário) + 100·(índice de ρ) + k, com k = 0…49 (faixa nunca usada).

**Critério declarado (descritivo, sem efeito sobre o modelo).** O controle empírico é considerado **consistente com α = 0,05** num cenário se o FDR estimado for ≤ 0,05 e o limite superior do IC for ≤ 0,10. Qualquer cenário fora disso é reportado como falha do controle empírico nesse cenário.

## 2. Ablação "tudo ligado, sem testes" nas reservas 2 e 3 (EXPLORATÓRIA)

**Pergunta.** A conclusão "o mecanismo de testes não melhora a precisão", obtida na reserva 1 (versão sem salvaguardas), se repete nas reservas 2 e 3 com a versão final?

**Rótulo.** Exploratório. As reservas já foram consumidas pelas avaliações pré-registradas. O resultado não é confirmatório e não altera nenhuma afirmação pré-registrada.

**Método.**
- Mesma configuração canônica com `all_on=True`: todas as unidades ativas desde o início, sem experimentos.
- Mesmas séries, mesmas entradas padronizadas e mesma máscara.
- A métrica, relativa ao NLinear, usa as previsões já salvas das avaliações.

**Relatório:**
- razão pareada LEBRE / tudo ligado (média geométrica, IC 95% por bootstrap estratificado, semente 8003), com as vitórias por série;
- custo analítico das duas versões;
- número de unidades ativas no fim.

Não haverá seleção posterior de subconjuntos.

## 3. Revisão bibliográfica sistemática

Protocolo em `LIT_REVIEW_PROTOCOL.md`: consultas fixadas antes, critérios de inclusão e registro de cada consulta.

## 4. Revisão r1 do documento

Correções de linguagem apontadas na revisão (validade dos e-values sob hipóteses versus controle empírico; contrato de custo não cumprido, +3,7% e +2,0%; microcontrolador com a especificação testada; capa com as avaliações sequenciais; disponibilidade de código). Entram também os resultados dos itens 1–3, com os seus rótulos.
