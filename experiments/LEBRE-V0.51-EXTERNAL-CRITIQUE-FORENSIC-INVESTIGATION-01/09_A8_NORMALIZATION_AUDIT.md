# 09 — A8 e a normalização

1. **Normalização autoritativa da v0.51.**
   - Nos benchmarks externos, o ambiente usa `CausalStandardScaler`: EMA com α = 10⁻⁴ (constante de tempo ~10.000 passos), início em média 0 e variância 1, piso de variância 10⁻⁴.
   - Na suíte interna (onde se mediram os ~91% de estrutura), as entradas entram **sem** normalização (já são ~N(0,1)).
   - A réplica usou o normalizador da sua própria v0.1 (EMA de ~100 passos), que **não** é o da v0.51.
2. **Tarefa A8.** É uma tarefa da v0.1 do replicador; o gerador não está disponível (`ARTIFACT_MISSING`), então o A8 não pôde ser executado.
3. **Diagnóstico possível sem o A8.** B1–B3 com entrada bruta, com o escalonador do projeto e com um EMA de 100 passos no estilo da réplica (tabela de `RUN_NORM_SUMMARY.csv`):

| task   | norm   |   exact |   nmse |
|:-------|:-------|--------:|-------:|
| B1     | causal |   0.926 |  0.697 |
| B1     | ema100 |   0.932 |  0.696 |
| B1     | raw    |   0.926 |  0.697 |
| B2     | causal |   0.595 |  0.608 |
| B2     | ema100 |   0.594 |  0.613 |
| B2     | raw    |   0.574 |  0.611 |
| B3     | causal |   0     |  0.398 |
| B3     | ema100 |   0     |  0.4   |
| B3     | raw    |   0     |  0.398 |

   Com entradas estacionárias, o normalizador não altera a estrutura recuperada. O efeito descrito pela crítica depende de entradas não estacionárias, como os regimes do A8.
4. **Classificação** (três afirmações separadas):
   - `A8_REPRODUCTION_STATUS = NOT_EXECUTABLE`: faltam o gerador e os resultados brutos da réplica.
   - `A8_NORMALIZATION_IMPLEMENTATION_DIFF = CONFIRMED`: pela descrição da própria réplica, ela usou um EMA de ~100 passos, e não o escalonador da v0.51 (EMA com α = 10⁻⁴).
   - `A8_NORMALIZATION_CAUSAL_ROOT_CAUSE = INSUFFICIENT_EVIDENCE`: a diferença existe, mas não há como demonstrar que ela explica o resultado do A8. Nas tarefas estacionárias B1–B3 o normalizador não tem efeito, e isso não diz nada sobre entradas não estacionárias.
   - O efeito do escalonador autoritativo em entradas não estacionárias continua **sem teste**. Não se generaliza do A8 para as demais tarefas.
