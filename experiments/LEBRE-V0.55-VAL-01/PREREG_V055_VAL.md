# Validação da v0.55 (núcleo ancorado, B10) em séries reais nunca usadas: pré-registro

**Data:** 17/10/2026, commitado **antes** de carregar qualquer valor destas séries.

**Candidata:** B10 do protótipo `experiments/LEBRE-V0.55-PROTO-01`, congelada no commit `b0522a0`. É a mesma que passou na
rodada D5 e na confirmação C1 do banco fixo do LEBRE Lab (`analises/BANCO_V055_*`). B10 tem:
- unidades externas testadas contra a previsão do núcleo e unidades internas contra a estrutura de nível;
- a estrutura de inovação como terceiro especialista aninhado;
- o portão suave pela triagem;
- os pesos de cada estrutura vindos do resíduo que o desafiante aprendeu;
- o piso de escala previsível, na escala de uma passada.

**Comparação:** A, a v0.54 canônica, do mesmo commit (cópia byte a byte de `f9906c4`).

## 1. Séries

Sorteadas só por metadados (`experiments/LEBRE-V0.55-DATA-01/make_split_v055val.py`; `SPLIT_V055_VAL.json`, SHA-256
`390f8c1d1fc24f974b1c30d40078ead622ef2e0c88a15547c9443b508ce7e34d`), nas posições seguintes às já consumidas das
permutações da v0.52:

| Família | Séries | Posições | Construção | Referência da M2 |
|---|---|---|---|---|
| camels | 20 bacias CAMELS-BR | 170–189 | a da v0.52 a v0.54: vazão diária; entradas precipitação, evapotranspiração e temperatura | persistência |
| bdg2 | 30 medidores BDG2 | 145–174 | a da v0.52 a v0.54: horária; ciclos 24 e 168 | sazonal |

Restam 47 bacias e 591 medidores nunca usados, para a avaliação final da v0.55.

**Limite declarado antes de rodar.** As duas famílias são, em geral, estacionárias ou sazonais. Esta validação testa se a
B10 **não piora** em dados reais. O ganho em séries integradas reais não é testado aqui: as séries de níveis já baixadas
foram todas consumidas, e a avaliação final precisará de séries de níveis novas.

## 2. Medidas

Por série:
- MSE de A e de B10 a partir de 20% da série (a janela do E20 e das avaliações anteriores);
- razão B10 ÷ A;
- custo por passo;
- entradas externas na estrutura final;
- peso final da estrutura de inovação;
- previsões não finitas.

**Bootstrap pareado por blocos móveis:**
- blocos de 20 passos em camels e de 168 em bdg2;
- 2.000 réplicas;
- semente `[2026102210, família, série]`, nunca usada.

Resumo por família: média geométrica das razões, com IC 95% pela média das réplicas em log das séries (a regra do teste
T10 da auditoria da v0.54).

## 3. Critérios

| Código | Critério | Passa se |
|---|---|---|
| V-a | sem piora | em cada família, limite superior do IC 95% ≤ 1,02 |
| V-b | sem falha numérica | nenhuma previsão não finita de B10 onde A é finita |
| V-c | custo | mediana por série da razão de custo ≤ 1,25 |

**Só descritivos:** entradas externas no fim (A e B10), as piores séries, o uso da estrutura de inovação.

**Decisão:**
- **passa:** B10 é a candidata da v0.55 para a avaliação final, que terá pré-registro próprio, reserva nova e regra de
  promoção vinculante;
- **falha:** o resultado é registrado, e B10 volta ao desenvolvimento.

Nada é ajustado depois de ver os resultados.

## 4. Execução

`python val_run.py` (gera `preds/`, fora do git), depois `python val_analise.py` (gera `VAL_RESULTADO.json`). Ambiente
de referência:
- CPython 3.11, NumPy 2.2.5, pandas 2.2.3;
- `LEBRE055_PROTO` no worktree do commit `b0522a0`.
