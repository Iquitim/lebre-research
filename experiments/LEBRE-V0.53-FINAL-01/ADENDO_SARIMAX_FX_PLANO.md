# Adendo (09/10/2026, depois do resultado): SARIMAX com entradas no câmbio, com as entradas preenchidas

**Só referência; não muda a decisão** (o SARIMAX não entra em nenhum critério do `PREREG_V053_FINAL.md`). Na execução
final, o SARIMAX com entradas não rodou nas 24 séries de câmbio: as entradas têm feriados faltantes e o método não aceita
valores faltantes nas entradas (`MissingDataError`; `FINAL_RESULTADO.md`). Pedido do responsável pelo projeto.

**O quê (`adendo_sarimax_fx.py`):** nas 24 séries de câmbio (fx_ret, fx_abs, fx_niv), o mesmo SARIMAX da execução final
(`comp_dev.run_airline_x`, ajuste nos primeiros 15%, season nenhuma), com as entradas **preenchidas pela regra da
avaliação da v0.52** (`data_v052._ffill_inputs`: último valor visto, sem olhar o futuro; 0 antes do primeiro valor), que é
também a convenção da LEBRE para entradas faltantes. O alvo continua com os faltantes (o SARIMAX aceita alvo faltante).

**Saída:** `adendo_sarimax_fx/<série>.npz` e `ADENDO_SARIMAX_FX_RESULTADO.md`, com SARIMAX-X ÷ v0.53 e SARIMAX-X ÷ v0.52
(MSE a partir de 20% de T, nos passos com alvo e as duas previsões finitos), média geométrica por família. Os arquivos da
execução final (`preds/`) não são alterados.
