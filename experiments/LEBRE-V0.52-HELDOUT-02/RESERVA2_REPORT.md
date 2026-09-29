# LEBRE v0.52 corrigida — Avaliação na reserva 2: relatório

**Data:** 27/09/2026 · **Pré-registro:** `PREREG_V052_RESERVA2.md` (antes de qualquer acesso) · **Execução:** única; 40/40 séries, sem erros.

## 1. O que foi avaliado

40 séries reais nunca usadas por nenhum modelo: 20 bacias do CAMELS-BR e 20 medidores de prédios do BDG2. Elas foram tiradas das próximas posições das mesmas permutações com semente da divisão original.

- **Candidata:** LEBRE v0.52 com a correção das lacunas do alvo (retenção do último valor observado + contrato de saída).
- **Congelada:** a v0.52 sem a correção, como foi avaliada na reserva anterior.
- **Classe de orçamento** (≤ 2.000 FP/passo): v0.51, NLinear, DLinear, Holt-Winters, ARX denso, LASSO online.
- **Referências** (tetos, fora da classe): SARIMAX com entradas, ARX por mínimos quadrados (~49 mil FP) e Chronos-2 com covariáveis (~10⁹–10¹⁰ FP).

Métrica: MSE relativo ao NLinear online (menor é melhor).

## 2. Resultado pré-registrado

| Modelo | Classe | CAMELS | BDG2 | Todas [IC 95%] | Pior grupo | Séries > 1,5 | Catastróficas | FP/passo |
|---|---|---|---|---|---|---|---|---|
| **LEBRE v0.52 corrigida** | orçamento | **0,703** | 0,836 | **0,767** [0,657; 0,858] | **0,836** | **0%** | **0** | 407 |
| LEBRE v0.52 congelada | orçamento | 1,468 | 0,834 | 1,107 [0,746; 1,826] | 1,468 | 7,5% | 2 | 392 |
| DLinear | orçamento | 0,948 | 0,965 | 0,957 | 0,965 | 5% | 0 | 1.533 |
| NLinear | orçamento | 1,000 | 1,000 | 1,000 | 1,000 | 0% | 0 | 674 |
| Holt-Winters | orçamento | 1,087 | 1,139 | 1,112 | 1,139 | 17,5% | 0 | 20 |
| ARX denso NLMS | orçamento | 0,916 | 4,345 | 1,995 | 4,345 | 40% | 4 | 474 |
| LASSO online | orçamento | 0,888 | 4,576 | 2,016 | 4,576 | 42,5% | 3 | 705 |
| LEBRE v0.51 | orçamento | 1,258 | 5,645 | 2,665 | 5,645 | 32,5% | 3 | 110 |
| SARIMAX com entradas | referência | 0,703 | 0,837 | 0,767 [0,646; 0,870] | 0,837 | 0% | 0 | ajuste por máx. verossimilhança |
| ARX por mínimos quadrados | referência | 0,595 | 3,387 | 1,419 | 3,387 | 22,5% | 3 | 48.944 |

**1.000 pontos com o modelo de fundação:** v0.52 corrigida **0,769**; SARIMAX-X 0,784; **Chronos-2 com covariáveis 0,662**; v0.52 congelada 1,043; DLinear 0,949.

## 3. Respostas às perguntas pré-registradas

- **Q1 — A correção elimina as falhas catastróficas?** **Sim:** 0 séries catastróficas, contra 2 da versão congelada (as duas no CAMELS). A correção foi acionada de fato: o contrato de saída cortou 67 passos em 19 séries; a fração média de alvo ausente foi 3%, com máximo de 20%.
- **Q2 — Corrigida contra congelada?** **0,693** [0,425; 0,989]: melhor, com IC abaixo de 1.
- **Q3 — Posição na classe de orçamento?** **1º lugar** (0,767). Depois vêm DLinear (0,957, com ~4× o custo), NLinear (1,000), congelada, Holt-Winters, ARX denso, LASSO e v0.51. Nas razões pareadas, a corrigida é melhor que todos os modelos da classe, com IC abaixo de 1.
- **Q4 — Fração do teto?** Contra o **Chronos-2 com covariáveis**, o erro da v0.52 é **16% maior** (razão 1,161; ela vence 12 de 40 séries). Em redução de erro sobre o NLinear, alcança ~68% do ganho do teto (23% contra 34%), com cerca de 10⁷ vezes menos computação. Contra o **SARIMAX com entradas**, **empata** (0,999 [0,965; 1,038]; 0,981 nos 1.000 pontos). Contra o **ARX por mínimos quadrados**, é **melhor** (0,540), porque ele falha nos prédios.
- **Q5 — Robustez?** Pior grupo 0,836, **nenhuma série acima de 1,5** e nenhuma catastrófica. É a mais robusta da classe de orçamento, empatada com o SARIMAX-X entre as referências.
- **Q6 — Custo?** Média de **407 FP/passo** (CAMELS 391; BDG2 422) e máximo por passo de **1.015**. **Ambos passam levemente dos limites declarados** (400 e 1.000); a expectativa registrada antes já previa isso para os prédios, com os ciclos diário e semanal.

**Estrutura:** 23 de 40 séries aceitaram ao menos uma entrada. Cobertura do intervalo de 90%: 0,905.

## 4. Leitura

1. **A correção funciona em dados novos:** as falhas catastróficas desapareceram e a precisão melhorou 31% em relação à versão congelada.
2. **Dentro do orçamento, a v0.52 é a melhor com folga** e a única sem nenhuma série ruim. Ela empata com o SARIMAX com entradas, um modelo clássico ajustado por máxima verossimilhança série a série.
3. **Contra o teto** (Chronos-2 com covariáveis), fica 16% atrás em erro, a um custo cerca de 10⁷ vezes menor. É exatamente o posicionamento declarado: entregar bem com orçamento mínimo, sem precisar ser o melhor.
4. **O custo ficou ~2% acima do contrato** (média e pico). É uma falha pequena, mas real, e fica registrada.

**Limitações:** 40 séries (intervalos largos); sem ONS; 4 locais do BDG2 compartilham o clima com o desenvolvimento; a correção foi desenhada depois de ver a falha na reserva 1 (e verificada só em desenvolvimento antes desta avaliação).
