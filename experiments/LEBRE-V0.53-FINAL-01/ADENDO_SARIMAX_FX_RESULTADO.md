# Adendo: SARIMAX com entradas no câmbio, entradas preenchidas (resultado)

Plano `ADENDO_SARIMAX_FX_PLANO.md`. Só referência; a decisão da avaliação final não muda.

| Família | séries ok | SARIMAX-X ÷ v0.53 (geo) | SARIMAX-X ÷ v0.52 (geo) |
|---|---|---|---|
| fx_ret | 8 de 8 | 1.123 | 1.086 |
| fx_abs | 8 de 8 | 1.058 | 1.058 |
| fx_niv | 8 de 8 | 1.065 | 1.014 |

**Leitura:** com as entradas preenchidas, o SARIMAX com entradas roda nas 24 séries e fica **pior que a v0.53** nas três
famílias de câmbio (12% nos retornos, 6% na volatilidade, 7% nos níveis) e também pior que a v0.52 (1,4% a 8,6%). No
câmbio, a v0.53 fica, portanto, à frente das duas referências caras (SARIMAX-X e Chronos-2; `FINAL_RESULTADO.md`). Adendo
feito depois do resultado, só como referência; a decisão da avaliação final não muda.
