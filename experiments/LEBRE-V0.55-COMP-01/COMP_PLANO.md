# Comparação da v0.55 com modelos externos: plano (commitado antes de rodar qualquer modelo externo)

**Data:** 17/10/2026. **Pedido do responsável:** comparação criteriosa com SARIMAX-X, Chronos-2 e outros modelos fortes.

**Status:** referência, **fora** da decisão de promoção. A v0.55 já foi promovida pela regra dela
(`LEBRE-V0.55-FINAL-01`), e nada aqui a altera.

**Séries:** as 84 da reserva final da v0.55 (`LEBRE-V0.55-DATA-02`). Nenhum modelo externo é ajustado nelas fora da
própria janela de calibração causal descrita abaixo.

**Previsões da LEBRE:** as da execução final já feita (`LEBRE-V0.55-FINAL-01/preds`), da v0.55 (B10) e da v0.54 (A),
sem rodar de novo.

## 1. Informação igual para todos

Previsão de **um passo**. No instante t, todo modelo conhece:
- o passado do alvo, y₁ … y_{t−1};
- as entradas até o instante atual, x₁ … xₜ.

É exatamente a informação da LEBRE. Nenhum modelo vê yₜ antes de prever.

Os modelos com calibração usam só a **janela de calibração**: as primeiras min(15% da série, 5.000) observações, a regra
de `comp_dev.py` (v0.52 a v0.54). Nada depois dela entra na escolha de configuração.

## 2. Modelos

Agrupados por classe de custo por previsão (ordem de grandeza declarada no relatório).

| Classe | Modelo | Protocolo |
|---|---|---|
| referência | REF: a referência trivial da M2 da família (persistência em camels e níveis; sazonal ingênuo 24 em bdg2, eólica e solar) | a regra da LEBRE |
| online, linear | ARX_NLMS: NLMS denso em [1, xₜ … xₜ₋₃₂, yₜ₋₁ … yₜ₋₃₂] | μ ∈ {0,01; 0,05; 0,2} calibrado (comp_dev.py) |
| online, linear | NLINEAR_ONLINE e DLINEAR_ONLINE | grade de `newmodels.py` calibrada (comp_dev.py) |
| online, linear | ARX_RLS: mínimos quadrados recursivos com esquecimento em [1, xₜ … xₜ₋₃, yₜ₋₁ … yₜ₋₃, yₜ₋ₛ se houver ciclo], alvo e entradas padronizados causalmente | λ ∈ {0,99; 0,999; 0,9999} calibrado; P simetrizada e reiniciada se perder a positividade |
| estatístico | SARIMAX_X: SARIMA aéreo (0,1,1)(0,1,1)ₛ com regressores xₜ … xₜ₋₄ (sem ciclo: ARIMA(0,1,1)) | máxima verossimilhança na janela de calibração; filtro de Kalman na série inteira (comp_dev.run_airline_x, sem alteração) |
| aprendizado de máquina | GBM: `HistGradientBoostingRegressor` do scikit-learn, alvo yₜ − yₜ₋₁; atributos Δy nos atrasos 1 a 3, yₜ₋₁ − yₜ₋ₛ (se houver ciclo), xₜ, xₜ₋₁ a xₜ₋₃ e as médias de x nos atrasos 4–7 e 8–15 | hiperparâmetros fixos (200 iterações, taxa 0,05, 31 folhas, sem parada antecipada); 10 reajustes em janela crescente, igualmente espaçados a partir do fim da calibração, cada um só com o passado |
| fundação | CHRONOS2_COV: Chronos-2 com as entradas como covariáveis passadas e xₜ como covariável futura conhecida | zero-shot, contexto 512, mediana, 1.000 pontos (chronos_dev.py, sem alteração) |
| fundação | CHRONOS2: univariado | idem |
| fundação | CHRONOS_BOLT_SMALL: univariado | idem |
| fundação | TTM_ZS: Tiny Time Mixers r2, univariado, zero-shot | ttm_run.py, 1.000 pontos |
| fundação | TTM_FT_EXOG: TTM r2 com as entradas como canais, ajustado só na janela de calibração | ttm_run.run(lr = 10⁻⁴, 30 épocas, parada antecipada), 1.000 pontos |

LightGBM e XGBoost não estão no ambiente de referência, e o responsável decidiu não instalar pacotes no Python do sistema.
O gradient boosting do scikit-learn é o substituto declarado.

## 3. Janelas de avaliação

- **Janela completa:** a partir de 30% da série (a regra de `comp_dev.py`), na **máscara comum**: alvo observado e
  previsão finita de todos os modelos de série completa (REF, LEBRE v0.55 e v0.54, ARX_NLMS, NLINEAR, DLINEAR, ARX_RLS,
  SARIMAX_X, GBM). Um modelo que falhar numa série fica fora da máscara só nela, e a falha é reportada.
- **1.000 pontos:** os pontos de `chronos_dev.points`, igualmente espaçados, com alvo observado, a partir de 30%. Ali
  são comparados **todos** os modelos, inclusive os de fundação.

## 4. Estatística

- **Primária:** razão de MSE v0.55 ÷ modelo, por série. Por família, a média geométrica das séries, com IC 95% por
  bootstrap pareado de blocos móveis, pela média das réplicas em log das séries (a regra do T10 e da avaliação final).
  - Blocos da janela completa: camels 30, bdg2 168, eólica 168, solar 168, níveis 20.
  - Blocos nos 1.000 pontos: 10 pontos.
  - 2.000 réplicas, semente `[2026102700, janela, família, modelo, série]`.
- **Comparações múltiplas:** p-valor bilateral pela fração das réplicas de cada lado de 1. Correção de Holm sobre todos
  os pares (família, modelo) de cada janela, a 5%. Uma diferença só é chamada de "significativa" depois da correção.
- **Secundárias:**
  - razão de MAE, pelo mesmo método;
  - número de séries em que a v0.55 é melhor;
  - posição da v0.55 entre os modelos, por família.
- **Custo:** operações por previsão em ordem de grandeza.
  - LEBRE, ARX e (N/D)Linear: o contador dos próprios modelos;
  - SARIMAX: a dimensão do estado ao quadrado por passo;
  - GBM: número de árvores × profundidade;
  - TTM: o contador do PyTorch;
  - Chronos: estimativa declarada (2 × parâmetros × comprimento do contexto em tokens).

## 5. O que se pode concluir

**Pode-se concluir:**
- onde a v0.55 é significativamente melhor ou pior que cada modelo, depois da correção, por família e por janela, com
  as classes de custo lado a lado;
- quantas famílias têm algum modelo significativamente melhor que a v0.55.

**Não se pode concluir:**
- que um modelo é "o melhor" em geral (são 5 famílias);
- nada sobre horizontes maiores que um passo.

Os resultados são reportados como saem. Nenhum modelo é reconfigurado depois de ver resultados.

## 6. Execução

1. `comp_run.py`: modelos de série completa.
2. `comp_fundacao.py`: Chronos e TTM, nos 1.000 pontos.
3. `comp_analise.py`: estatística.

Uma falha de infraestrutura pode ser repetida com o mesmo código e é registrada em `RUN_NOTAS.md`.

## 7. Notas antes da execução

- **Correção do ARX_RLS**, feita num teste **sintético**, antes de qualquer execução na reserva. A primeira versão
  padronizava o alvo com média e desvio lentos, e numa série integrada sintética ficou pior que a persistência (0,56
  contra 0,42), porque os coeficientes derivavam com a escala. A versão registrada usa o alvo na escala original e chega
  ao piso teórico (0,250).
- **Teste de API dos modelos de fundação** num sintético pequeno: rodam. Os números desse teste não são usados.
