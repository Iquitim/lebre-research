# 11 — Sensibilidade ao τ do martingale (ANÁLISE DE SENSIBILIDADE, não otimização)

**Derivação no código:** τ = ρ / (σ̂² · m_φ), com ρ = 1. É um prior de informação unitária: a mistura gaussiana sobre λ tem variância igual à de uma observação, e m_φ é a potência de projeto do regressor. A especificação mostra τ só dentro da fórmula, sem valor nem unidade.

**Correspondência com a réplica:** a réplica usa m ∈ {50, 200, 1000}, no estilo de Howard et al. (fronteira ajustada para um tempo intrínseco m). Isso corresponde aproximadamente a ρ = 1/m. A grade pré-definida usou exatamente esses valores; nenhum outro foi testado.

| task   |   rho |   exact |   promotions |   nmse |
|:-------|------:|--------:|-------------:|-------:|
| B2     | 0.001 |   0     |            0 |  1.071 |
| B2     | 0.005 |   0.279 |           27 |  0.719 |
| B2     | 0.02  |   0.585 |           34 |  0.612 |
| B2     | 1     |   0.574 |           33 |  0.611 |
| B3     | 0.001 |   0     |           10 |  0.657 |
| B3     | 0.005 |   0     |           27 |  0.514 |
| B3     | 0.02  |   0     |           44 |  0.416 |
| B3     | 1     |   0     |           40 |  0.398 |
| N1     | 0.001 | nan     |            0 |  1.069 |
| N1     | 0.005 | nan     |            0 |  1.069 |
| N1     | 0.02  | nan     |            0 |  1.069 |
| N1     | 1     | nan     |            0 |  1.069 |

- **N1:** nenhuma promoção falsa para nenhum τ.
- **B2:** limítrofe. ρ = 1 e 1/50 dão ~0,58, abaixo do alvo de 0,80 da réplica. Com ρ mais conservador a estrutura some (1/200 → 0,28; 1/1000 → 0,00). A crítica relatou o efeito oposto (m = 1000 elevaria o B2 para 0,841); com o código original isso **não** se reproduz.
- **B3:** exato = 0 em toda a grade.

**Classificação:** `TAU_SENSITIVITY = SPEC_UNDERSPECIFIED`. O parâmetro não está na especificação, e o resultado de múltiplos atrasos depende dele (**BOUNDARY_SENSITIVE** para o B2). A falha do B3 é **ROBUST** a τ.
