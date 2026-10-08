# LEBRE v0.53 — M1, rascunho 2: especialista de defasagens conjuntas com estrago limitado, especificação antes do código

**Data:** 08/10/2026. **Terceiro desenho da M1.** Critério de F6 inalterado (rascunho 1, seção 1: fronteira precisão ×
custo, teto de 2,5 vezes a v0.52 em B03). **Base:** E11 (LEBRE Lab, `M1_E11_RESULTADO.md`): o rascunho 1 melhora muito B03
(0,650 da v0.52; benzeno 0,233), mas (i) o custo total em B03 ficou ~3 vezes o da v0.52, acima do teto, por um erro de
conta da especificação do rascunho 1 (o teto vale para o custo total, não só para o especialista); (ii) o especialista,
liberado com o sistema recém-determinado e mal condicionado, produziu previsões enormes que o Prod (perda recortada) tolera
por alguns passos, com estrago ilimitado na saída em erro quadrático; (iii) isso gerou depois um valor não finito na M2.

## 1. Mudanças em relação ao rascunho 1

1. **Número de entradas derivado do teto (correção de conta):** orçamento do especialista em B03 = 2,5 × ~700 (v0.52) −
   ~700 (v0.52) − ~130 (M2) ≈ 920 FP por passo. Com custo (6k² + 4k)/8 + 2k + 10m e k = 3 + 5m, o maior m que cabe é
   **m = 5** (k = 28, ~690 FP). Regra: m = mín(d, 5).
2. **Estrago limitado:** a previsão do especialista usada na mistura é recortada para [L − B, L + B], com
   B = CLIP_K × máx(σ̂_L, piso), σ̂_L = raiz da média exponencial (LAM) dos erros quadráticos recentes da v0.52 (só passado):
   a mesma faixa em que a perda recortada da v0.52, usada pelo Prod, é informativa. Fora dela, o Prod não distingue
   graus de erro; dentro dela, um especialista errado custa no máximo o equivalente a um erro de B. É o análogo do que
   já valia na M2, cujas saídas combinadas ficam sempre entre a referência e a v0.52.
3. **Robustez numérica:** perdas não finitas passadas aos agregadores da M2 são tratadas como o maior valor finito (o
   passo conta como muito ruim para aquele previsor, sem propagar NaN); deve ser inócuo com a mudança 2.

O restante (variáveis, bandas, RLS a cada 8 passos, entrada no Prod depois de k atualizações, encaixe com a M2) fica como
no rascunho 1.

## 2. Critérios (os do rascunho 1, seção 3) e custo

Custo do especialista com m = 5: ~690 FP por passo, mais Prod (~31), recorte (~4) e triagem (~d).

## 3. Resultado no desenvolvimento (E12, 08/10/2026)

Atende aos três critérios (LEBRE Lab, `M1_E12_RESULTADO.md`): F6 em B03 1,392 do comparador completo, com custo de 1,95
vez a v0.52 (meta pela regra registrada: 1,653); B01 e B02 1,000; critérios da M2 nas 43 famílias, C05 incluída. Não é
evidência de seleção (três desenhos sobre os mesmos dados). Acréscimo de custo de M1 + M2: 156 a 878 FP por passo.
