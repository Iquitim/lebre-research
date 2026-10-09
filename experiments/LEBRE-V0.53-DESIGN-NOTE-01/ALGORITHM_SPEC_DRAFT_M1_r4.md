# LEBRE v0.53 — M1, rascunho 4: especialista do rascunho 2 com o Prod corrigido, especificação antes do código

**Data:** 09/10/2026. **Quinto desenho da M1.** Base (LEBRE Lab):
- **E14 (tabela por família):** a regressão AR2 + bandas de defasagem de 3 entradas, atualizada a cada 8 passos (318 FP),
  atende à meta de F6 nas **quatro** famílias abaixo da fronteira (B03 1,574; B07 1,035; VB07 1,039; XB07 1,032; metas
  ~1,65 e ~1,05). Esse é, em essência, o especialista do rascunho 2 (que em B03 deu 1,392 com m = 5).
- **Validação 4 e E13:** o rascunho 2 falhou pelo **Prod com perda recortada em 2σ**, não pelo especialista.
- **E16 e E17:** o rascunho 3 trocou o especialista (perdeu B03) e normalizou as perdas pelo maior erro já visto, o que
  **congela** o Prod depois de um recorde (peso ~1 num especialista pior em Arinos e San Francisco; ~0 num muito melhor em
  St. Petersburg); e o Prod começa com pesos iguais, o que custa 1-3% na entrada tardia (inflação mensal).

## 1. O rascunho 4

- **Especialista:** o do rascunho 2, sem mudança (z = [1, y_{t−1}, y_{t−2}, bandas t; 1; 2-3; 4-7; 8-15 das m = mín(d, 5)
  entradas de maior correlação], RLS a cada 8 passos, previsão recortada em L ± CLIP_K × máx(σ̂_L, piso)).
- **Prod, perdas:** f_t(x) = (y_t − x)² / N_t, com o **maior erro com esquecimento**
  N_t = máx((y_t − L_t)², (y_t − E_t)², LAM × N_{t−1}), LAM = 0,99 (a constante de esquecimento que a v0.52 já usa; nenhum
  parâmetro novo). As perdas ficam em [0, 1]; depois de um recorde, a escala volta ao nível típico em algumas centenas de
  passos, em vez de ficar presa.
- **Entrada em sombra:** o Prod é atualizado desde que o especialista tem previsão, mas a saída só usa s depois de
  **N_MIN = 100** atualizações do Prod (constante já existente); antes disso L' = L. O especialista só pesa depois de mostrar
  desempenho.
- **Custo:** o do rascunho 2 com o Prod contado: ~690 + 31 + 7 FP com m = 5; ~320 + 38 com d = 3.

## 2. Critérios (E18, desenvolvimento ampliado; os do rascunho 3, seção 2)

1. F6 em B03, B07, VB07 e XB07 (fronteira do E14, teto 2,5 vezes).
2. Critérios da M2 (régua por decidibilidade com os adendos 1 e 2) com M1 + M2 em todas as famílias, C05 incluída.
3. Custo reportado.

## 3. Resultado (E18b, 09/10/2026): não atende

LEBRE Lab, `analises/E18B_RESULTADO.md` e `E18B_ALVO_RESULTADO.md`. F6: B03 1,404 (meta 1,652) e B07 1,040 (meta 1,054)
atendem; VB07 1,120 (meta 1,056) e XB07 1,087 (meta 1,061) não. Custo 2,0-2,2 vezes a v0.52. Critérios da M2 com a M1:
nenhuma falha causada pela M1 (as pioras do rascunho 3 em Arinos e na inflação mensal e a de Horizonte do rascunho 2 não
aparecem). Nada ajustado.
