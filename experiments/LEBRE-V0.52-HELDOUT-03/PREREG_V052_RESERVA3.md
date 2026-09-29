# Pré-registro — LEBRE v0.52 na "reserva 3": comparadores ultraleves e TTM, porte em C e custo em microcontrolador simulado

**Data:** 27/09/2026 · **Status:** registrado **antes** de qualquer acesso aos valores das séries da reserva 3. A seleção (`select_reserve3.py`) leu só atributos de elegibilidade, cobertura, fração de zeros e nomes de arquivos, e verificou que não há sobreposição com o desenvolvimento nem com as reservas 1 e 2.

## 1. Objetivo

Com a v0.52 **congelada** (configuração canônica, sem nenhuma alteração), medir em 60 séries nunca vistas:
- (a) a posição na classe de orçamento, agora com os modelos ultraleves FITS e SparseTSF;
- (b) a distância a tetos pequenos e grandes: TTM, sem treino e ajustado com as entradas, e Chronos-2 com covariáveis;
- (c) a fidelidade do porte em C float32;
- (d) o custo real num Cortex-M4F simulado.

Avaliação **descritiva**, sem decisão de promoção. Princípio: entregar bem com orçamento mínimo e sem falhas catastróficas.

## 2. Dados — reserva 3 (`RESERVA3.json`)

- Regra fixada antes: as próximas posições das mesmas permutações com semente (CAMELS-BR, semente 5202: posições 80–109; BDG2, semente 5203: posições 55–84).
- **30 bacias do CAMELS-BR + 30 medidores do BDG2.**
- **Limitações:** sem ONS (rios esgotados); 3 locais do BDG2 (Bull, Eagle, Hog) compartilham o clima com o desenvolvimento.

## 3. Modelos (congelados; configurações fixadas só com dados de desenvolvimento)

- **V052_PY:** LEBRE v0.52, configuração canônica (congelamento LEBRE-V0.52-FREEZE-01).
- **V052_C32:** o porte C99 da mesma configuração, em precisão simples (build do PC do mesmo código do microcontrolador). No desenvolvimento: sequências de mudanças idênticas em 28/29 séries e diferença relativa mediana do NMSE de 8·10⁻⁷.
- **Classe de orçamento:**
  - V051, NLinear, DLinear, Holt-Winters, ARX denso NLMS, LASSO online (calibrados nos primeiros 15%);
  - **FITS** (~1.200 parâmetros, ~9,8 mil FLOPs/previsão) e **SparseTSF** (< 100 parâmetros, ~2–3 mil FLOPs), ajustados só nos primeiros 15%, com pesos fixos depois, univariados.
- **Referências:**
  - SARIMAX com entradas;
  - ARX por mínimos quadrados com ordem online (~4–6·10⁴ FLOPs);
  - **TTM** zero-shot univariado (15,6 M FLOPs);
  - **TTM ajustado** nos primeiros 15% com as entradas como canais exógenos e o valor atual como covariável futura (lr 10⁻³, 5 épocas; a melhor das duas configurações tentadas no desenvolvimento; 30–64 M FLOPs);
  - **Chronos-2 com covariáveis** (~10⁹–10¹⁰ FLOPs).
  - TTM e Chronos seguem o protocolo dos 1.000 pontos.
- **Microcontrolador:** firmware float32 no Renode 1.17 (STM32F4 Cortex-M4F + DWT, contagem de instruções) nas **2 primeiras bacias e nos 2 primeiros medidores** da lista.

## 4. Análise (`heldout3_analysis.py`)

- MSE relativo ao NLinear, máscara comum (últimos 70%); médias geométricas; IC 95% por bootstrap estratificado (semente 8003).
- **Série catastrófica:** erro relativo > 10; ou desvio > 10× a amplitude observada; ou previsão não finita num passo observado.
- **Q1:** séries catastróficas da V052_PY (esperado: 0).
- **Q2:** posição da V052_PY na classe de orçamento.
- **Q3:** fração dos tetos (V052_PY / Chronos-2 com covariáveis, / TTM sem treino, / TTM ajustado, nos 1.000 pontos; / SARIMAX-X, / ARX por mínimos quadrados, na máscara completa).
- **Q4:** robustez (pior grupo; fração > 1,5; catastróficas).
- **Q5:** porte em C float32 em dados novos. **Critério:** sequências de mudanças aceitas idênticas às do Python em **≥ 90%** das séries, e mediana de |diferença relativa do NMSE| **< 10⁻⁴**.
- **Q6:** custo (FP analítico: média ≤ 400 e máximo por passo ≤ 1.000, o contrato; microcontrolador: instruções por passo — média, mediana, p99,9, pico — e RAM do estado). Ciclos estimados com o CPI medido no desenvolvimento (~1,6).

## 5. Expectativas registradas antes

- **Desenvolvimento** (29 séries): V052 0,697 (máscara completa); FITS 1,44; SparseTSF 3,5; TTM sem treino 1,38 e ajustado 2,14 (1.000 pontos); Chronos-2 com covariáveis 0,701.
- **Reserva 2:** V052 0,767, empate com o SARIMAX-X; Chronos-2 com covariáveis 16% melhor; custo médio 407 e máximo 1.015 FP.
- **Microcontrolador (desenvolvimento):** 3,7–6,0 mil instruções por passo em média, picos de 42–48 mil em passos de decisão, 75 KB de estado.
- **Espera-se de novo:** custo ~2% acima do contrato nos prédios; o Chronos-2 com covariáveis mais preciso que a v0.52.

## 6. Integridade

- Execução única; repetição só por falha de infraestrutura, documentada; nenhuma mudança de modelo depois do acesso.
- **Ferramentas:** pandas 2.2.3; numpy 2.2.5; torch 2.11.0+cpu; granite-tsfm 0.3.9; arm-none-eabi-gcc 15.2.1 (xPack 15.2.1-1.1); Renode 1.17.0; zig cc (host) 0.16.0.

| Arquivo | SHA-256 |
|---|---|
| lebre_v052h.py | `edbaf21dfc19729ce08f114f707f8f1ff900fd55cc6a9011114fc1b48b4e9fd7` |
| change_engine.py | `11bb13022e408776b2c0a222852e22d00e4c443b7a9f78471a9ce7a1b4c96e9d` |
| lebre_v052.py | `212872117d795203ae4bf46382af9b95b13eb05cb6cca507fa7e4546ef530b27` |
| data_v052.py | `88a77ae64b92e414aa55af070a5b142a88ddd20652e0b5d6c8cf841c4f8970fa` |
| comp_dev.py | `0bc9d773364ac130acfec1e1f688d2eb14b8a2eecc0a90569de51b7a6c9af40f` |
| strong_baselines.py | `323a9803abee2149ec880f02988a51ff87861b6bcaf36ab2e05f975a3561d258` |
| chronos_dev.py | `33deb6e80521b6941e47934ad8f738fc88b42070aa441590fa03549a307122b0` |
| heldout2_cfg.py | `2d913648e0a3b1878e3110c0e1ff21ac4e060ea715f8d2943fb0e4eecf366384` |
| equiv_test.py | `7d4b705923e7a81dc94423a1c862cd89f8643ed91f26a832ef587317fadc2d3a` |
| ultralight.py | `6b9b5f497048af2f4bfd4517c0dd8aeb7e6334b8e6ece7099e176f198c06446f` |
| ttm_run.py | `6510bba906792deaa6f37e04ab94e5b4f95cf92ffb3531306dda34b147226d47` |
| lebre_c/lebre052.h | `ec2d00eb5bfcd9ebb874ed58795b67ffc1ba809be2fcd60b5f73fe836c81f4f7` |
| lebre_c/lebre052.c | `9684b71287f55d12ceffab5cd85c79638a2830b50843730d8fd75481e4515b53` |
| lebre_c/api.c | `d653f7665298b9f7dae1ed3874597df71a2233ccb52b972136a7884cc92bd8c3` |
| lebre_c/lebre052_f32.dll | `75896d3ff18631af7ee9103ac8cbb2e9d5284dac7c58ae4ba367859e012ab492` |
| mcu/main.c | `10a13e22d5e959ae08c08cf1700652c941e43e1b60840a1bf5168c7868b62d2e` |
| mcu/startup.c | `f9fe0af1b909e51476d2e1209f100b6edb747a520a789a1993aa0b78ef4cf3fa` |
| mcu/link.ld | `7c39be506e82a91b1484551f37c7fa71642849457527ec216356ce94be58d4c6` |
| mcu/platform.repl | `1d7640a770a3903db83d88a3d76c2e011142deca16c1112ff26d4a5fad1c64d1` |
| mcu/gen_data.py | `b41dcbcd69cb630aedd85b3b76101fa4ef33d668428f0d70079ae90a975702af` |
| mcu/build_run.sh | `f2f6f8e96b78deb2c3e05df4be33e2cc554fd933605ff6707a4912b7865361aa` |
| mcu/cycles_estimate.py | `0e2b0bc47d7b0adb6f53aa92e3491decf843e84b3b9b6267e3969d03cede48eb` |
| select_reserve3.py | `503833104e4cf80d40a8f78d3d5e9fb6161b8c6b19d6c1802e925ccb03698d7f` |
| RESERVA3.json | `1b2d1268b02794717fbaa1ea91855e9caa34580ea3a88c1cb704b69330f69051` |
| heldout3_run.py | `3f9ba7a5844e6ddd915dc25d731b800652c8d2556da20c90f0798762291534de` |
| heldout3_ttm_chronos.py | `13517c9f3dc26cf995cab2e92420d0af9d1a657e40efb871afde0c201bdd1964` |
| heldout3_mcu.sh | `cae3750cfd0db547f678244f05e839c20c9f808075544f5e6a2187c9c8d0118c` |
| heldout3_analysis.py | `56d31bb081b278146ff8c2dc047955a05d7496efb05c88bbe852f6824c46323f` |

