# Avaliação final da v0.53 na reserva: resultado

Pré-registro `PREREG_V053_FINAL.md`.

Séries: 104 de 104; faltam: nenhuma.

**Melhora geral (v0.53 ÷ v0.52, todas as séries): 0.955 (0.951–0.960; n = 104) → atende (limite superior < 1).**

| Critério | Falhas |
|---|---|
| 1 | - |
| 2 | - |
| 4 | - |
| 6 | - |
| 7 | - |
| NaN | - |
| custo | - |

Critério 7 (curtas, contra o melhor): 1.007 (0.995–1.017; n = 101). Empates exatos fora do agregado (alvo e as três previsões iguais no trecho; RUN_NOTAS.md, item 2): bdg2:chilledwater:Hog_education_Mathilda.
Memória estimada (não medida): 85,092 B de 131,072 B (cabe).

**Decisão: v0.53 PROMOVIDA** (sem piora: True; melhora clara: True; memória: True).

| Família | séries (v0.52 melhor / ref. melhor / indecidível / choque) | 1 | 2 | v0.53 ÷ v0.52 (todas) | +custo máx | externas v0.53 (v0.52) |
|---|---|---|---|---|---|---|
| camels | 15 / 2 / 7 / 6 | 0.845 (0.814–0.878; n = 2) | 0.911 (0.899–0.924; n = 15) | 0.879 | 495 | 9 (9) |
| bdg2 | 30 / 0 / 0 / 0 | - | 0.993 (0.988–1.000; n = 30) | 0.993 | 385 | 16 (16) |
| solar | 8 / 0 / 0 / 0 | - | 1.000 (1.000–1.000; n = 8) | 1.000 | 696 | 1 (1) |
| eolica | 8 / 0 / 0 / 0 | - | 1.000 (1.000–1.000; n = 8) | 1.000 | 918 | 3 (3) |
| carga | 4 / 0 / 0 / 0 | - | 1.000 (1.000–1.000; n = 4) | 1.000 | 831 | 4 (4) |
| fx_ret | 0 / 5 / 1 / 2 | 1.000 (1.000–1.000; n = 5) | - | 0.966 | 894 | 0 (0) |
| fx_abs | 6 / 0 / 0 / 2 | - | 1.000 (1.000–1.000; n = 6) | 1.000 | 894 | 0 (0) |
| fx_niv | 0 / 6 / 0 / 2 | 1.001 (1.000–1.002; n = 6) | - | 0.952 | 894 | 7 (7) |

## Referências fora da classe de orçamento (só reportadas)

| Família | SARIMAX-X ÷ v0.53 (geo) | v0.53 ÷ Chronos-2 nos 1.000 pontos (geo) | v0.52 ÷ Chronos-2 (geo) |
|---|---|---|---|
| camels | 1.134 | 0.885 | 1.008 |
| bdg2 | 1.034 | 1.248 | 1.241 |
| solar | 1.096 | 1.237 | 1.237 |
| eolica | 1.049 | 1.051 | 1.051 |
| carga | 0.968 | 1.433 | 1.433 |
| fx_ret | - | 0.954 | 0.979 |
| fx_abs | - | 0.983 | 0.983 |
| fx_niv | - | 0.881 | 0.921 |

## Leitura (escrita depois do resultado)

- **Decisão pela regra pré-registrada: v0.53 promovida.** Sem piora em nenhuma família (critérios 1, 2, 4, 6, 7, NaN e
  custo), melhora clara no conjunto (0,955; IC 95% 0,951 a 0,960) e memória estimada de 85 KB (de 128 KB).
- **De onde vem o ganho:** bacias (0,879; a v0.53 também fica abaixo do Chronos-2 nos 1.000 pontos, 0,885), níveis de
  câmbio (0,952), retornos (0,966) e prédios (0,993). Em **solar, eólica e carga a v0.53 é idêntica à v0.52** (razão 1,000;
  peso final da M1 = 0 nas 20 séries; a M2 fica na v0.52), com acréscimo de custo de até 696, 918 e 831 FP por passo:
  nessas famílias a v0.53 paga mais sem ganho.
- **Duas correções durante a execução**, documentadas em `RUN_NOTAS.md`, nenhuma em modelo ou critério: leitura da carga
  de 2026 pelo código do subsistema (o ONS renomeou o Sudeste) e o tratamento de um caso degenerado nas séries curtas
  (empate exato com erro zero, excluído do agregado; uma piora nesse caso contaria como falha).
- **Referências:** o SARIMAX com entradas não rodou nas 24 séries de câmbio (entradas com feriados faltantes; o método não
  aceita valores faltantes nas entradas); é só referência, sem efeito na decisão. O Chronos-2 é melhor que a v0.53 em
  prédios, solar e carga (1,24 a 1,43) e pior nas bacias e no câmbio.
- **Limites:** a memória é estimativa, não medição; o IC do conjunto trata as séries como independentes; os adendos da
  régua (choque) foram decididos no desenvolvimento, antes desta execução.

**Adendo (09/10/2026, só referência):** o SARIMAX com entradas foi rodado de novo no câmbio com as entradas preenchidas pela
regra da v0.52 (`ADENDO_SARIMAX_FX_RESULTADO.md`): SARIMAX-X ÷ v0.53 = 1,123 (fx_ret), 1,058 (fx_abs), 1,065 (fx_niv).
