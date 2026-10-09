# LEBRE v0.53 — M1, rascunho 5: especialista do rascunho 2 combinado por AdaHedge no erro quadrático, especificação antes do código

**Data:** 09/10/2026. **Sexto desenho da M1.** Base (LEBRE Lab):
- **E18b:** o rascunho 4 atende a F6 em B03 e B07 e não causa piora em nenhuma família, mas falha em VB07 e XB07.
- **E19:** nas marés, o especialista sozinho é melhor que a v0.52 em 15 de 18 séries, mas o Prod lhe dá peso ~0. As três
  formas de pôr o erro quadrático em [0, 1] para o Prod falharam por razões diferentes: recorte em 2σ (cego aos erros
  grandes: validação 4), maior erro de todos (congela: E17), maior erro com esquecimento (pesa contra os passos de erro
  grande: E19). O problema é a exigência de perdas limitadas do Prod (PRA-10), não o ajuste da normalização.

## 1. O rascunho 5

- **Especialista:** o do rascunho 2 (e 4), sem mudança.
- **Combinação com a v0.52:** **AdaHedge** (de Rooij, van Erven, Grünwald e Koolen, 2014; a classe `Agregador` já usada na
  candidata D da M2) com dois especialistas (v0.52 e E) e perda = **erro quadrático sem recorte nem normalização**. O
  AdaHedge não precisa conhecer a escala das perdas (a taxa de aprendizado se ajusta à soma das diferenças de mistura); o
  peso segue o erro quadrático acumulado, que é o que o MSE mede.
- **Entrada em sombra:** como no rascunho 4: o AdaHedge é atualizado desde que o especialista tem previsão, mas L' = L até
  N_MIN = 100 atualizações. Depois, L' = w_L L + w_E E.
- **Proteção contra piora (declarada, sem garantia constante):** o AdaHedge garante arrependimento contra o melhor dos dois
  da ordem de √(L* × faixa × ln 2) + faixa × ln 2 em unidades de erro quadrático (L* = perda acumulada do melhor), que
  relativamente ao MSE total some com o tamanho da série; não há a garantia de arrependimento constante contra a v0.52 que
  o Prod daria em perdas limitadas, que na prática não se materializou (validação 4, E17, E19). Séries curtas ficam
  protegidas pela sombra.
- **Custo:** o do rascunho 2 com o AdaHedge no lugar do Prod: ~690 + 48 FP por passo com m = 5; ~320 + 48 com d = 3.

## 2. Critérios (E20, desenvolvimento ampliado)

1. F6 em B03, B07, VB07 e XB07 (fronteira do E14, teto 2,5 vezes), com a M2 escolhida na releitura E16c.
2. Critérios da M2 (régua por decidibilidade com o adendo 3) com M1 + M2 em todas as famílias, C05 incluída; NaN = falha.
3. Custo reportado.
