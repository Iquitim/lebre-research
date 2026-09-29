# Emenda 01 ao PREREG_BENCH04 — orçamento de tempo dos modelos Chronos

**Motivo:** limite de ~10 min de CPU para esta etapa, definido pelo usuário. Na CPU, o Chronos-2 no teste completo levaria cerca de 3 h.
**Escrita depois** de ver os resultados dos modelos online e do Chronos-Bolt-tiny (teste completo), e **antes** de qualquer resultado do
Bolt-small e do Chronos-2. A emenda muda só o número de pontos avaliados, não os modelos nem os critérios.

- CHRONOS_BOLT_TINY: teste completo (já executado, sem mudança).
- CHRONOS_BOLT_SMALL e CHRONOS2 (contexto 512): N = 1000 pontos do teste igualmente espaçados (linspace).
- CHRONOS2_COV (contexto 256): N = 500 pontos igualmente espaçados.
- O NMSE é o MSE nesses pontos dividido pela variância do teste completo. É uma estimativa sem viés do MSE do teste
  (amostragem sistemática), mas com variância maior. Esses modelos entram no ranking **com rótulo de amostra**.
- K-a a K-e não dependem do Chronos e ficam inalterados.
