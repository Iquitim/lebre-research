# Adendo 01 ao pré-registro da avaliação final da v0.56 (commitado antes da segunda validação e da execução)

**Data:** 25/10/2026.

**Motivo:** a candidata do pré-registro original (C5, commit `ef77728`) não passou na validação, e a avaliação final não
foi executada. A nova candidata é a **D4** (`experiments/LEBRE-V0.56-PROTO-02`, commit `c3074bd`; descrição em
`experiments/LEBRE-V0.56-VAL-02/PREREG_V056_VAL2.md`). A reserva final continua lacrada: nenhuma série dela foi carregada.

**O que muda:**
1. **Candidata:** variante "D4" de `Lebre056D` (protótipo 02, commit `c3074bd`); comparação: variante "A" do mesmo
   protótipo (a v0.55 canônica).
2. **Condição para rodar:** a **segunda** validação (`LEBRE-V0.56-VAL-02`) precisa passar.
3. **R5, memória:** a estimativa da v0.55 (86.180 B), mais a variação do estado da M1 com cinco entradas escolhidas, 8
   bytes por número. Na v0.55, k = 1 + 2 + 5·5 = 28, com P (k²), w (k) e 2 alvos. Na D4, k = 1 + 3 + 3·5 = 19, com P, w,
   3 alvos e 5 números do estudo sob demanda (σ̂²_E, q̂, alvos sem atualização e dois contadores).
4. Nos scripts, os nomes das variantes passam de C5 para D4; a lógica, a estatística e os critérios não mudam.

**O que não muda:** a reserva (`SPLIT_V056.json`), as execuções (principal e placebo, semente `[2026102900, família,
série]`), a estatística (`reps`, semente `[2026102901, família, série]`) e a regra de promoção R1 a R6, inclusive o
benefício demonstrado em `camels_cl` (R6: limite superior < 1,00).
