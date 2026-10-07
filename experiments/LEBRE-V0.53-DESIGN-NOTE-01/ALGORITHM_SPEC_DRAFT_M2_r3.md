# LEBRE v0.53 — M2, rascunho 3: Fixed Share sobre previsões probabilísticas

**Data:** 08/10/2026 · **Status:** proposta, antes de qualquer código desta revisão. **Base:** PRA-08 e a medição do
rascunho 2 (`M2_DEV_R2_RESULTADO.md`). **Condição do responsável pelo projeto:** nenhuma versão é promovida sem
resolver C05; o rascunho 2 resolveu C05 mas falhou nas séries curtas (B02).

## 1. Mudança em relação ao rascunho 2

Só o algoritmo dos pesos muda; o resto do rascunho 2 continua (saída = média ponderada de R e L; porta como auditoria;
estrutura idêntica à v0.52; mesmos passos observados).

- **Previsores como densidades:** em cada passo, R e L viram N(f_k, σ_k²), com σ_k² = média exponencial (fator LAM =
  0,99 da v0.52) dos erros quadráticos passados do próprio previsor, com piso igual ao da porta (SCALE_FLOOR × desvio do
  alvo, a partir do passo 200). Perda: ℓ_k = (y − f_k)²/(2σ_k²) + ln σ_k.
- **Pesos:** Fixed Share com taxa de troca α_t = 1/t (Adamskiy et al., 2016, Corolário 6), início uniforme, atualização
  da equação (5) do artigo. Para N = 2: u_{t+1} = α_{t+1} + (1 − 2α_{t+1}) × (posterior da rodada t).
- **Início:** a primeira rodada só inicializa as escalas (não há σ antes do primeiro erro); os pesos começam na segunda.

## 2. Garantia e limites

- Para qualquer sequência de dados e qualquer intervalo [t₁, t₂] de rodadas, a perda logarítmica da mistura excede a do
  melhor previsor do intervalo em no máximo ln t₂ (Corolário 6, N = 2). O déficit do início é esquecido ao custo de ln t.
- A saída pontual é a média da mistura; não há garantia equivalente para a perda quadrática (PRA-08, seção 3).
- **Custo estimado:** ~40 FP por passo para os pesos, mais ~18 da auditoria.

## 3. Medição

Mesmo plano do rascunho 2 (23 famílias, mesmos critérios 1, 2, 4, 5, 6 e 7, mesmo bootstrap), com plano próprio
commitado antes de rodar. Uma única configuração, sem parâmetros livres. Se falhar, as falhas são declaradas e nada é
ajustado.

## 4. Resultado no banco de desenvolvimento (08/10/2026)

Medição no LEBRE Lab (`M2_DEV_R3_PLANO.md`, `M2_DEV_R3_RESULTADO.md`; protótipo `bda07f4`), interrompida depois que a
regra já estava decidida (8 das 23 famílias medidas). **Não escolhida:** falha o critério 2 em C05 (1,108, IC 95%
1,02–1,21), B01, B02 e C02; o critério 1 em C01, C03 e C04; e o critério 7 nas séries curtas (1,115). Diagnóstico: com
a perda logarítmica da gaussiana de escala própria, a vantagem por passo do melhor previsor é só ~½ ln(razão dos erros
quadráticos médios); o Fixed Share, pronto para trocar, segue sequências de sorte (em C05 o peso da LEBRE oscila entre
0,03 e 0,93). O rascunho 2 (AdaHedge) continua sendo o único que resolve C05; o problema em aberto é só o déficit inicial
em séries curtas (B02).
