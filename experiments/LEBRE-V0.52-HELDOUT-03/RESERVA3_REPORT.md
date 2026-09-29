# LEBRE v0.52 — Avaliação na reserva 3: comparadores ultraleves e TTM, porte em C e custo em microcontrolador simulado

**Data:** 27/09/2026 · **Pré-registro:** `PREREG_V052_RESERVA3.md` (antes de qualquer acesso aos valores das séries) · **Execução:** 60/60 séries sem erro de modelo.
**Incidentes de infraestrutura**, todos na etapa do microcontrolador e registrados no diário da extensão:
1. caminho em formato do shell;
2. consumo da entrada padrão;
3. duas séries do BDG2 sem relatório no laço, rodadas manualmente com o mesmo script.

Nenhum modelo foi alterado.

## 1. O que foi avaliado

60 séries nunca vistas (30 bacias do CAMELS-BR e 30 medidores do BDG2), tiradas das próximas posições das mesmas permutações com semente.

- **LEBRE v0.52 congelada** (configuração canônica), em Python e no **porte C99 em precisão simples**, que é o código do microcontrolador.
- **Classe de orçamento** (até ~10⁴ FLOPs por previsão): v0.51, NLinear, DLinear, Holt-Winters, ARX denso, LASSO online, **FITS** e **SparseTSF**.
- **Tetos de referência:**
  - SARIMAX com entradas;
  - ARX por mínimos quadrados com ordem online;
  - **TTM** (Tiny Time Mixers), sem treino e ajustado com as entradas;
  - Chronos-2 com covariáveis.

Métrica: MSE relativo ao NLinear online (menor é melhor).

## 2. Resultado pré-registrado

| Modelo | Classe | CAMELS | BDG2 | Todas [IC 95%] | Pior grupo | Séries > 1,5 | Catastróficas | FLOPs/previsão |
|---|---|---|---|---|---|---|---|---|
| **LEBRE v0.52 (Python)** | orçamento | 0,858 | 0,768 | **0,812** [0,752; 0,866] | **0,858** | **0%** | **0** | 415 |
| LEBRE v0.52 (C float32) | orçamento | 0,858 | 0,768 | 0,812 | 0,858 | 0% | 0 | = |
| NLinear | orçamento | 1,000 | 1,000 | 1,000 | 1,000 | 0% | 0 | 674 |
| DLinear | orçamento | 1,076 | 0,947 | 1,009 | 1,076 | 3,3% | 0 | 1.533 |
| Holt-Winters | orçamento | 1,213 | 1,244 | 1,229 | 1,244 | 25% | 0 | 20 |
| FITS | orçamento | 1,362 | 1,137 | 1,244 | 1,362 | 18% | 0 | 9.757 |
| ARX denso NLMS | orçamento | 1,008 | 2,711 | 1,653 | 2,711 | 38% | 2 | 474 |
| LASSO online | orçamento | 1,015 | 3,048 | 1,759 | 3,048 | 38% | 4 | 705 |
| LEBRE v0.51 | orçamento | 2,180 | 2,140 | 2,160 | 2,180 | 48% | 4 | 108 |
| SparseTSF | orçamento | 2,980 | 2,886 | 2,933 | 2,980 | 87% | 3 | 4.016 |
| SARIMAX com entradas | referência | 0,817 | 0,803 | 0,810 [0,763; 0,851] | 0,817 | 0% | 0 | ajuste por máx. verossimilhança |
| ARX por mínimos quadrados | referência | 0,677 | 2,867 | 1,394 | 2,867 | 20% | 4 | 48.944 |

**1.000 pontos** (com os modelos de fundação):

| Modelo | CAMELS | BDG2 | Todas | FLOPs/previsão |
|---|---|---|---|---|
| **LEBRE v0.52** | 0,836 | 0,787 | **0,811** | ~415 |
| SARIMAX com entradas | 0,798 | 0,818 | 0,808 | — |
| TTM sem treino | 1,204 | 0,978 | 1,085 | 15,6·10⁶ |
| TTM ajustado com entradas | 1,049 | 1,054 | 1,052 | 55,6·10⁶ |
| **Chronos-2 com covariáveis** | 0,782 | **0,539** | **0,649** | ~10⁹–10¹⁰ |

## 3. Respostas às perguntas pré-registradas

- **Q1 — Falhas catastróficas?** **Nenhuma** em 60 séries. Na classe de orçamento, ARX denso, LASSO, v0.51 e SparseTSF têm de 2 a 4 cada.
- **Q2 — Posição na classe de orçamento?** **1º lugar com folga** (0,812), à frente de NLinear (1,000), DLinear (1,009), Holt-Winters (1,229), FITS (1,244), ARX denso (1,653), LASSO (1,759), v0.51 (2,160) e SparseTSF (2,933). Nas comparações pareadas, a v0.52 vence de 45 a 60 das 60 séries contra cada um, com IC abaixo de 1 em todos.
- **Q3 — Fração dos tetos?**
  - **TTM:** a v0.52 é **melhor** que as duas configurações. Razões pareadas de 0,747 (sem treino; vence 57/60) e 0,771 (ajustado; vence 50/60), com ~4·10⁴ a 10⁵ vezes menos FLOPs.
  - **SARIMAX com entradas:** **empate** (1,002 [0,966; 1,041]).
  - **ARX por mínimos quadrados:** a v0.52 é **melhor no total** (0,582). O ARX é melhor nas bacias (0,677) e falha nos prédios (2,867).
  - **Chronos-2 com covariáveis:** **melhor que a v0.52.** A razão pareada é 1,250, ou seja, a v0.52 erra ~25% mais, e vence só 9/60 séries. Nos prédios a diferença é grande (0,787 contra 0,539).
- **Q4 — Robustez?** Pior grupo 0,858, nenhuma série acima de 1,5 e nenhuma catastrófica. É a mais robusta da classe de orçamento, empatada com o SARIMAX-X entre as referências.
- **Q5 — Porte em C em dados novos?**
  - sequências de mudanças aceitas idênticas às do Python em **54/60 séries (90%)**, exatamente o critério (≥ 90%);
  - mediana de |diferença relativa do NMSE| de **1,1·10⁻⁶** (critério < 10⁻⁴); máximo 1,0·10⁻²;
  - nenhum estouro de capacidade.

  **Passou**, no limite do primeiro critério.
- **Q6 — Custo?**
  - FP analítico médio de **415** e máximo por passo de **1.020**: **~4% e ~2% acima do contrato** (400 e 1.000), como previsto.
  - **Microcontrolador simulado** (Cortex-M4F, float32; 4 séries da reserva):

| Série | Instruções/passo: média | mediana | p99,9 | pico | Padronizador | Ciclos/passo (×1,6) | Tempo a 168 MHz | Confere com o Python |
|---|---|---|---|---|---|---|---|---|
| CAMELS 51795000 | 3.203 | 3.003 | 12.223 | 36.771 | 110 | ~5.100 | ~31 µs | NMSE e decisões iguais |
| CAMELS 64625000 | 3.521 | 3.215 | 12.267 | 36.708 | 110 | ~5.600 | ~34 µs | idem |
| BDG2 Fox_education_Ollie | 5.806 | 5.587 | 15.375 | 45.402 | 34 | ~9.300 | ~55 µs | idem (3 mudanças) |
| BDG2 Panther_education_Vincent | 5.528 | 5.463 | 16.971 | 45.696 | 33 | ~8.800 | ~53 µs | idem (3 mudanças) |

Estado do modelo: **75 KB de RAM**. Código do modelo: ~15 KB de flash (+ ~10 KB de libm). Os picos ocorrem só em passos de decisão.

## 4. Leitura

1. **O posicionamento se confirma em dados novos.** Dentro de algumas centenas de FLOPs por passo (poucos milhares de instruções num Cortex-M4), a LEBRE v0.52 é a **mais precisa e a única sem nenhuma série ruim** entre os modelos baratos. Isso inclui modelos ultraleves publicados (FITS, SparseTSF), que no protocolo online de um passo ficam atrás do próprio NLinear.
2. **Contra modelos de fundação pequenos, ela vence.** O TTM (~0,8 M parâmetros), sem treino ou ajustado com as entradas, fica ~25% atrás, com ~4·10⁴ a 10⁵ vezes mais FLOPs.
3. **Contra o Chronos-2 com covariáveis, perde:** ~25% mais erro, sobretudo nos prédios. É o teto de referência, a ~10⁷ vezes o custo.
4. **O porte em C é fiel em dados novos**, e o custo medido no simulador (~3,2–5,8 mil instruções, ~31–55 µs a 168 MHz) é compatível com um microcontrolador comum.
5. **O contrato de custo analítico fica ~2–4% estourado.** É uma falha pequena e reportada; o custo real no dispositivo é o do simulador.

**Limitações:**
- 60 séries de dois domínios (sem ONS);
- a comparação com FITS e SparseTSF usa o nosso protocolo (ajuste nos primeiros 15%, pesos fixos, um passo), que não é o regime para o qual foram desenhados;
- o TTM foi testado em duas configurações de ajuste, escolhidas no desenvolvimento;
- os ciclos são estimados de rastreios com os tempos do manual do Cortex-M4 (sem esperas de flash), não medidos em placa;
- a energia não foi medida.
