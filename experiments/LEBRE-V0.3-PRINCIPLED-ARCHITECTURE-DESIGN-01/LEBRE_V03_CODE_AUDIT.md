# Auditoria de código — `lebre_v03.py` (iter4, congelado) → `lebre_v031.py`

Cada achado foi verificado por leitura linha a linha e, quando indicado, por teste empírico em `verify_properties.py`
(sementes 5031..5230; resultados em `PROPERTY_TESTS.csv` e `PROPERTY_TESTS_v031.csv`).

## Achados

| ID | Severidade | Achado | Evidência | Status na v0.3.1 |
|---|---|---|---|---|
| A1 | **Alta (validade)** | O teste de promoção normaliza S e V acumulados no passado pelo σ̂² **do momento da decisão**. Quando σ² muda (silêncio, heterocedasticidade), a estatística se infla e há promoções espúrias. | T6: átomos promovidos com entradas exatamente zero (ex.: "x1 atrasado 26" em t=2300 na I7). T3 heterocedástico: 0,21 falsas promoções por fluxo, contra limite de 0,052 | **Corrigido (F1):** estatística auto-normalizada `Q = Σ(eφ)²`, mistura τ fixada na abertura → 0,00 |
| A2 | **Alta (validade)** | A garantia de Ville supunha ruído gaussiano com σ conhecido. | T3 com t₃: 0,26 falsas promoções por fluxo (5× o limite) | **Corrigido (F1):** válido para ruído condicionalmente simétrico (de la Peña 1999; Howard et al. 2020, Lema 3(d)) → 0,00 |
| A3 | **Média (equivariância)** | O modelo não é invariante à escala do alvo: ρ = 0,25 em unidades de y, σ² inicial = 1, e estados latentes em unidades de y misturados a entradas adimensionais na norma do NLMS. | T7: NMSE 0,186 (×1) contra 0,396 (×1000) | **Corrigido (F2):** prior de informação unitária relativa a σ̂ e inovação normalizada `u/σ̂` → 0,191 nas três escalas |
| A4 | Média (numérica) | σ² decai geometricamente sem piso em fluxos constantes; subfluxo possível em silêncios muito longos. | T7, fluxo nulo: σ² = 2,9e-7 após 3000 passos | **Corrigido (F3):** piso relativo de 1e-10 × pico, inicialização preguiçosa |
| A5 | Baixa (explicabilidade) | Rótulo "polo nan" quando o acionamento é removido junto com o latente. | eventos das execuções de DEV | **Corrigido (F4)** |
| A6 | Baixa (contabilidade) | A pré-checagem conta 6 FP onde há 7; o ramo do log conta 3 onde há 4. Comparações de ponto flutuante (ordenação do dicionário, min/max) e o `log` não entram no FP. | leitura; T8: ~7,5 comparações/passo com ordenação completa, 0,001 log/passo | **Parcial (F5):** seleção top-k (≈ n comparações por reposição, seleção idêntica, contagem exposta em `n_rank_compares`). O subconteio de ~1 FP por avaliação de teste permanece documentado (< 0,5 FP/passo) |
| A7 | Baixa | O aluguel usa `min(1, φ²/v_ref)`, cuja média é < 1 (≈ 0,68 para φ gaussiano). O T_idle efetivo é ≈ 1,5× o nominal. | analítico | documentado |
| A8 | Baixa | O `T_max` de futilidade conta *testes*, não passos (com test_every = 2 ⇒ 400 passos). O comentário dizia "passos". | leitura | documentado |
| A9 | Baixa | O acionamento com polo 0 duplica exatamente o átomo de atraso x_i@1 (redundância inofensiva). | leitura | documentado |
| A10 | Informativa | A garantia por episódio não é garantia por fluxo: E[falsas por fluxo] ≤ (nº de episódios)·α/p ≈ 0,05. | T3 | documentado |
| A11 | Informativa | Memória contabilizada por convenção (float32/fp16), mas a simulação roda em float64. O comportamento numérico em fp16 **não foi validado**. | leitura | lacuna aberta |

## Propriedades verificadas (iguais nas duas versões, salvo indicação)

| Teste | v0.3 | v0.3.1 |
|---|---|---|
| T1 causalidade (perturbar y_t e o futuro não altera ŷ_{≤t}) | ✅ diferença 0,0 | ✅ 0,0 |
| T2 alinhamento de atrasos k ∈ {1, 7, 32} | ✅ 30/30 | ✅ 30/30 |
| T3 promoções falsas por fluxo (gauss / t₃ / hetero), limite 0,052 | 0,005 / **0,26** / **0,21** | **0,000 / 0,000 / 0,000** |
| T4 remoções falsas do átomo verdadeiro | 4 em 1,14M passos | 4 em 1,14M passos |
| T5 MSE do latente / ótimo de Kalman (mediana; máximo) | 1,18; 1,97 | 1,18; 1,91 |
| T6 latente retido no silêncio; eventos durante o silêncio | 30/30; **1,67** | 30/30; **0,00** |
| T7 NMSE com y ×10⁻³ / ×1 / ×10³ | 0,247 / 0,186 / **0,396** | **0,191 / 0,191 / 0,191** |
| T8 FP/passo na I4 (tarefa mais cara) | 107,9 | 108,8 |

## Não alterado de propósito

Os parâmetros de projeto (μ, α, ARL, T_idle, polos, M_max, cadências) **não** mudaram entre a v0.3 e a v0.3.1. As correções tratam apenas de
validade, equivariância, robustez numérica e contabilidade. A troca `ρ = 0,25 → ρ_rel = 1` é uma reparametrização para a forma relativa (F2),
não um ajuste: com σ ≈ 0,5, ρ_rel = 1 corresponde a ρ ≈ 0,25 em unidades absolutas.
