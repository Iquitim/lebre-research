# Protótipo v0.55 — teste de fumaça (desenvolvimento, antes de qualquer medição registrada)

**Data:** 16/10/2026 · **Cenários:** os de `tests/test_anchored.py` (sementes 5471–5475) e 8 passeios aleatórios com 5
entradas que também passeiam (sementes 5477–5478, 4 séries cada, 4.000 passos, referência de persistência).
**Uso:** só para achar defeito grosseiro e escolher as variantes da medição D1. **Não é evidência.** Essas sementes não
entram na D1.

**Registro completo de variantes tentadas** (nada omitido):
- **rascunho 0:** B, B1, B2;
- **rascunho 1:** B, B1 com os atributos da memória na estrutura;
- **rascunho 2:** B4, B5 (referência = previsão do núcleo).

## MSE no último 2/3 da série e estruturas aceitas

| Cenário | A (v0.54) | B (r1) | B1 (r1) | B2 | B4 | B5 |
|---|---|---|---|---|---|---|
| band_season_gaps | 0,1405 | 0,1460 | 0,1460 | 0,1316 | 0,1363 | 0,1499 |
| correlated_12 | 0,1158 | 0,1442 | 0,1446 | 0,1237 | 0,1233 | 0,1237 |
| opposite_lags_split | 0,1734 | 0,4021 | 0,3461 | 0,2440 | 0,2038 | 0,2451 |
| random_walk_level | 0,2440 | 0,2440 | 0,2440 | 0,2440 | 0,2440 | 0,2440 (aceitou x2) |
| relation_vanishes | 0,1045 | 0,1858 | 0,1369 | 0,1081 | 0,1046 | 0,1081 |

**Rascunho 0** (sem os atributos da memória): B1 tinha 0,4305 em opposite_lags_split.

## Passeios aleatórios: séries (de 8) com entrada externa na estrutura final

| A | B2 | B4 | B5 |
|---|---|---|---|
| 2 | **8** | **0** | **0** |

## Diagnóstico

1. **Âncora na previsão viva (B, B1): resultado negativo.** Em opposite_lags_split, B1 aceita a mesma estrutura de A,
   com peso da estrutura 1, mas o erro fica alto até o fim: 0,31 contra 0,09 no último terço.
   - Os atributos da memória na estrutura (rascunho 1, motivado por Frisch–Waugh–Lovell) quase não ajudaram.
   - Com a memória congelada em persistência pura, a perda continuou: 0,20 contra 0,09.
   - **Causa:** aprender a estrutura sobre a inovação r = y − m. O NLMS precisa cancelar yₜ₋₁ com coeficiente −1 sobre
     uma entrada padronizada e faz isso mal. A cascata na previsão viva tem custo de precisão real.
2. **Referência lenta sem âncora (B2): resultado negativo nos níveis.** 8 de 8 passeios terminam com entrada espúria.
   Uma referência lenta e sem raiz unitária erra o nível ainda mais, e qualquer entrada que passeia projeta esse erro.
   Isso é coerente com a Proposição 1 da nota de desajuste.
3. **Referência = previsão combinada do núcleo (B4): candidata principal.**
   - 0 de 8 passeios com entrada espúria (A: 2 de 8);
   - precisão perto de A em 4 dos 5 cenários;
   - em opposite_lags_split, aceita own_past em vez das divisões, com MSE 0,204 contra 0,173.
   - É a menor mudança: a previsão viva é a da v0.54, e só a pergunta dos testes muda.
4. **B5 (B4 + referência lenta): candidata secundária.** O custo é maior e o atraso das descobertas é o de B2; houve
   uma aceitação espúria no passeio de nível dos testes.

**Variantes da D1:** A (controle), **B4 (principal)** e B5 (secundária). B, B1 e B2 ficam registradas como resultados
negativos de desenvolvimento.

## Rascunho 3 (B6), depois da D1 — mesma fumaça

B6: unidades externas testadas contra a previsão do núcleo; internas (passado do alvo, estado residual) contra s.

| Cenário | A | B4 | B6 |
|---|---|---|---|
| band_season_gaps | 0,1405 | 0,1363 | 0,1510 |
| correlated_12 | 0,1158 | 0,1233 | 0,1233 |
| opposite_lags_split | 0,1734 | 0,2038 | **0,1515** (divisões recuperadas) |
| random_walk_level | 0,2440 | 0,2440 | 0,2440 |
| relation_vanishes | 0,1045 | 0,1046 | 0,1046 |
| Passeios: séries com entrada externa no fim (de 8) | 2 | 0 | 0 |
