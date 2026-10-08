# M2 da v0.53: candidata P ((A,B)-Prod com D como referência de confiança e M como oportunista), especificação antes do código

**Data:** 08/10/2026. **12ª configuração da M2.** Base: as falhas de D e de M são complementares nas 43 famílias de
desenvolvimento (régua por decidibilidade):

| | D (AdaHedge acumulado, sem troca) | M (troca num só sentido, escala recente) |
|---|---|---|
| Falha | só a fase de aprendizado longa (Abaiara, W-B01) | critério 1 em C01, C03, VB07, CURTAS, W-CURTAS (distorção de escala no início) |
| Onde a outra falha | boa | boa (Abaiara: 1,000) |

**Decisão do responsável pelo projeto (antes de medir):** limite de custo da M2 = **150 FP por passo** (com auditoria).

## 1. Literatura (lida no original)

Sani, Neu e Lazaric (2014), *NeurIPS* 27, e o material suplementar oficial (apêndice B): **(A,B)-Prod "anytime"**
(Algoritmo 1, Teorema 6). Mistura um algoritmo A com um previsor de confiança B; garante arrependimento contra B no máximo
2 ln 2 + 2K_T, K_T = O(log log T), e contra A da ordem de √(C log log C), para perdas em [0, 1] e qualquer sequência.
Peso de B fixo (½); peso de A w_A (início ½), atualizado por w_A ← w_A (1 + η_{t−1} δ_t)^{η_t/η_{t−1}}, δ_t = f(b_t) −
f(a_t); taxa η_t = √(1 / (1 + Σ_{s<t} δ_s²)), com η_1 = ½; s_t = η_t w_A / (η_t w_A + w_B/2). Para perdas convexas, a
saída pode ser a mistura s_t a_t + (1 − s_t) b_t (nota de rodapé 1 do artigo).

**Leitura declarada:** a análise do Prod exige η ≤ ½ com |δ| <= 1; o algoritmo fixa η_1 = ½ e, a partir daí, uso
η_t = mín(½, √(1/(1 + Σ δ²))), como em Gaillard, Stoltz e van Erven (2014), de onde o artigo diz adaptar a versão.

## 2. A candidata P

- **B = D** (candidata D, congelada: AdaHedge sobre o erro quadrático, só com a referência definida).
- **A = M** (candidata M do E4, barata: troca num só sentido, escala recente).
- **Perdas do Prod em [0, 1]:** a perda recortada da v0.52 das duas saídas, f(x) = mín((y − x)²/B², 1), B² = CLIP_K² ×
  máx(mín(σ²_R, σ²_L), piso²) (a mesma do rascunho 4; só passado).
- **Saída:** s_t × saída de M + (1 − s_t) × saída de D. Enquanto a referência não está definida, a saída é L.
- **Auditoria e estrutura:** como em D.
- **Efeito esperado:** onde D é boa e M erra (as cinco famílias de E4), a saída fica a uma constante de D; onde M é muito
  melhor por muito tempo (fase de aprendizado longa), a saída migra para M.

## 3. Garantias e limites

- Teorema 6 (perdas recortadas, jogada aleatorizada): arrependimento contra D <= 2 ln 2 + O(log log T); contra M,
  O(√(C log log C)). A saída usa a mistura determinística (rodapé 1), e a perda recortada não é convexa: a garantia vale
  para a versão aleatorizada; a medição decide.
- Custo estimado: D (48) + M (37) + Prod (~31: taxa, pesos, perdas recortadas das duas saídas, atualização) + auditoria
  (~18) = ~134 FP por passo, abaixo de 150.

## 4. Medição

E7 (desenvolvimento) nas 43 famílias, régua por decidibilidade, plano commitado antes; se atender a todos os critérios
(5 com 150 FP), **validação 3** nova, congelada, usada uma vez; depois a reserva (v0.53 completa).
