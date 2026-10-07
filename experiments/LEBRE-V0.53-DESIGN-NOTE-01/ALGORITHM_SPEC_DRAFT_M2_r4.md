# LEBRE v0.53 — M2, rascunho 4: AdaHedge sobre a perda recortada da v0.52

**Data:** 08/10/2026 · **Status:** proposta, antes de qualquer código desta revisão. **Base:** resultados dos rascunhos 2
(AdaHedge resolve C05 e passa nas 22 famílias; falha nas séries curtas por B02) e 3 (Fixed Share não escolhido).

## 1. O problema que resta

Em B02 curto, os erros da LEBRE nos primeiros passos (antes de aprender o nível da carga) são ~10⁴ vezes maiores que os
da referência; com a perda quadrática bruta, esse déficit domina a soma por centenas de passos. Um passo isolado não
deveria pesar mais que um teto fixo.

## 2. Mudança em relação ao rascunho 2

Só a perda dada ao AdaHedge muda (algoritmo, pesos, saída, auditoria e estrutura como no rascunho 2):

- **Perda recortada, a mesma do motor de evidência da v0.52:** ℓ_k = min((y − f_k)² / B², 1), com
  B = CLIP_K × max(σ_min, piso), CLIP_K = 2 (constante da v0.52).
- **Escala σ_min:** o menor entre os desvios dos dois previsores, σ_k = raiz da média exponencial (LAM = 0,99, da v0.52)
  dos seus erros quadráticos, calculados **antes** do erro do passo (só passado). Escolha declarada: a escala do melhor
  previsor recente, de modo que erros grandes do pior previsor batam no teto. Piso: o da porta (SCALE_FLOOR × desvio do
  alvo, a partir do passo 200).
- **Primeira rodada:** só inicializa as escalas (como no rascunho 3).

Nenhuma constante nova: CLIP_K, LAM, SCALE_FLOOR e o teto 1 já existem na v0.52.

## 3. Garantia e limites

- O AdaHedge garante arrependimento (de Rooij et al., 2014, Teorema 8) sobre as perdas **recortadas**, que ficam em
  [0, 1]: o déficit de um passo é no máximo 1.
- A perda recortada não é convexa na previsão; a garantia não passa para a perda quadrática da média ponderada. A medição
  decide.
- Custo: o do rascunho 2 (48) mais o recorte (8, trabalhando com quadrados: B² = CLIP_K² × max(min(σ²_R, σ²_L), piso²),
  duas divisões e dois mínimos) e a auditoria (~18): ~74 FP por passo, **no limite** revisado de 75. Declarado antes de
  medir; o critério 5 é aplicado como está.

## 4. Medição

Mesmo plano do rascunho 2 (23 famílias, critérios 1, 2 com C05, 4, 5, 6, 7), uma configuração, sem parâmetros livres,
plano próprio commitado antes de rodar.

## 5. Resultado no banco de desenvolvimento (08/10/2026)

Medição completa no LEBRE Lab (`M2_DEV_R4_PLANO.md`, `M2_DEV_R4_RESULTADO.md`; protótipo `432ef71`). Reprodução da v0.52
e do rascunho 2 exatas. **Atende aos critérios 1, 4, 5 (acréscimo de 64 a 74 FP por passo), 6 e 7 (séries curtas: M2 ÷
melhor 1,013, limite superior 1,023), e C05 (1,0007, limite superior 1,003).** **Falha o critério 2 só em B01** (1,024,
limite superior 1,043), por uma única série (Arinos, 1,154): a usina começa a gerar no passo 720, a LEBRE leva milhares
de passos para aprendê-la, e com a perda recortada a vantagem por passo dela fica pequena; os pesos só passam para a
LEBRE por volta do passo 6.500. **Não escolhida.** A raiz comum às falhas dos rascunhos 2 e 4 é a memória total dos
pesos.
