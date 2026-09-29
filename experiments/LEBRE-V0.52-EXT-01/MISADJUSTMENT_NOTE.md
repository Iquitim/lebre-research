# Nota formal — Desajuste da referência e o significado estrutural de um teste de melhora preditiva

**Data:** 27/09/2026 · **Contexto:** LEBRE v0.52 (congelada). Cada mudança estrutural é aceita por um e-process sobre a diferença de perda entre a referência S (o especialista estrutural vigente, aprendido online) e um desafiante G = S + g. Pergunta: quando uma aceitação significa "existe estrutura", e não apenas "o desafiante corrige o erro de estimação de S"?

## 1. Definições

- Filtração (ℱₜ): informação disponível antes de yₜ. A referência Sₜ, o desafiante Gₜ = Sₜ + gₜ e a escala Bₜ > 0 são ℱₜ₋₁-mensuráveis (previsíveis).
- **Previsão ótima:** f\*ₜ = E[yₜ | ℱₜ₋₁]. **Ruído:** εₜ = yₜ − f\*ₜ, com E[εₜ | ℱₜ₋₁] = 0.
- **Erro de estimação da referência:** ηₜ = f\*ₜ − Sₜ. **É ℱₜ₋₁-mensurável**: depende só dos pesos atuais e das entradas já observadas.
- **Diferença de perda** (quadrática, normalizada, sem recorte): Δₜ = [(yₜ − Sₜ)² − (yₜ − Gₜ)²] / Bₜ². O teste usa dₜ = Δₜ^clip − ε com a perda recortada min{·, 1} e a margem ε > 0.
- **Nula do teste** (fraca, Choe & Ramdas): para todo n, (1/n) Σᵢ≤ₙ E[dᵢ | ℱᵢ₋₁] ≤ 0.
- **Nula estrutural** para a unidade u: os atributos zᵤ da unidade não acrescentam informação sobre yₜ, isto é, f\*ₜ é a mesma com ou sem eles. Num alvo sem nenhuma estrutura, f\*ₜ = 0.

## 2. Resultados

**Proposição 1 (identidade).** Para qualquer desafiante previsível,

  E[Δₜ | ℱₜ₋₁] = (2 gₜ ηₜ − gₜ²) / Bₜ²  ≤  ηₜ² / Bₜ²,

com igualdade quando gₜ = ηₜ.

*Demonstração.* yₜ − Sₜ = εₜ + ηₜ e yₜ − Gₜ = εₜ + ηₜ − gₜ. Expandindo, (εₜ+ηₜ)² − (εₜ+ηₜ−gₜ)² = 2gₜ(εₜ+ηₜ) − gₜ². Como gₜ, ηₜ e Bₜ são ℱₜ₋₁-mensuráveis e E[εₜ | ℱₜ₋₁] = 0, a esperança condicional é (2gₜηₜ − gₜ²)/Bₜ². O máximo em gₜ de 2gη − g² é η², atingido em g = η. ∎

**Consequência:** a nula do teste compara **métodos** (modelo + estimação), como em Giacomini & White (2006). Se a referência erra (ηₜ ≠ 0), existem desafiantes com melhora esperada positiva **mesmo sob a nula estrutural**: basta que g se correlacione com o erro de estimação de S, que é previsível.

**Corolário 1 (garantia exata; condição universal).** Se, para todo n,

  (1/n) Σᵢ≤ₙ ηᵢ² / Bᵢ² ≤ ε,

então, sob a nula estrutural, **nenhum** desafiante previsível tem melhora média positiva na perda sem recorte, e a nula do teste vale. Nesse caso, o controle de mudanças falsas do e-process (e do procedimento tipo e-LOND sobre ele) **transfere-se para a nula estrutural**.

*Demonstração.* Pela Proposição 1, E[Δᵢ | ℱᵢ₋₁] ≤ ηᵢ²/Bᵢ²; logo (1/n)Σ E[Δᵢ − ε | ℱᵢ₋₁] ≤ (1/n)Σ ηᵢ²/Bᵢ² − ε ≤ 0. ∎

**Proposição 2 (desafiantes de coeficiente fixo).** Se gᵢ = θᵀzᵤ,ᵢ com θ constante numa janela W, então a melhora média na janela é no máximo

  Dᵤ(W) + ε,  com Dᵤ(W) = (1/|W|) Σᵢ∈W (Pᵤηᵢ)² / Bᵢ² − ε,

em que Pᵤ é a projeção de mínimos quadrados, ponderada por 1/Bᵢ², de η sobre zᵤ em W.

*Demonstração.* A soma de (2θᵀzη − (θᵀz)²)/B² sobre W é uma função quadrática côncava em θ, e o seu máximo é a norma ponderada da projeção. ∎

Os desafiantes da LEBRE usam mínimos quadrados recursivos dentro de um episódio, com coeficiente aproximadamente constante. Por isso **Dᵤ é a quantidade relevante na prática**, e ela é bem menor que o limite universal quando só uma fração ρᵤ² do erro de estimação é projetável nos atributos da unidade.

**Proposição 3 (critério prático no horizonte; aproximação).** Quando Dᵤ > 0 é pequeno, a log-evidência cresce em média como n·Dᵤ²/(2σ_d²), em que σ_d é o desvio-padrão de dₜ. O tempo típico até o limiar log(1/αₖ) é

  n\* ≈ 2 σ_d² log(1/αₖ) / Dᵤ².

Numa série de comprimento T, aceitações falsas são **improváveis** se

  Dᵤ < D_crit(T) = σ_d · √(2 log(1/αₖ) / T).

**Isto não é uma garantia:** é o regime em que a violação da nula do teste é pequena demais para ser detectada no horizonte disponível.

**Ligação com o aprendiz NLMS.** Para um NLMS normalizado com passo μ, o erro de estimação em regime estacionário é E[η²] ≈ M·σ², com desajuste M ≈ μ/(2 − μ). Com Bₜ = 2σ̂ e σ̂² ≈ σ²(1 + M), o Corolário 1 exige M/(4(1+M)) ≤ ε, isto é, **M ≲ 4ε**. Com ε = 0,002, isso dá M ≲ 0,008 e μ ≲ 0,016.

## 3. Verificação empírica (desenvolvimento; 120 execuções nulas, sementes 7201–7240)

Alvos sem estrutura nenhuma (ruído gaussiano e t de Student com 3 graus de liberdade), com as entradas reais do rio de desenvolvimento e a v0.52 congelada variando só μ. Aqui f\* = 0, então η = −S.

| μ | M medido (teórico μ/(2−μ)) | D máximo por série, média | Oráculo: log-evidência máxima do melhor desafiante (mediana / máx.) | Aceitações reais |
|---|---|---|---|---|
| 0,10 | 0,082 (0,053) | **+0,0044** | **18,2 / 33,4** (limiar 5,63) | **10/40** |
| 0,05 | 0,037 (0,026) | +0,0013 | 0,7 / 5,2 | 0/40 |
| 0,03 | 0,021 (0,015) | −0,0004 | 0,01 / 0,2 | 0/40 |

- **Oráculo:** o mesmo e-process unilateral aplicado à melhora **realizada**, com perda recortada, do melhor desafiante de coeficiente fixo possível (a projeção de η nos atributos da unidade, calculada sobre a série inteira). Por construção, é um **limite superior** do que um desafiante real consegue.
- **O que confere com a teoria:**
  - o desajuste medido cresce com μ, cerca de 1,5× acima do valor teórico (o NLMS normaliza pela potência de todos os atributos, e as entradas são coloridas);
  - as aceitações ocorrem **só** onde o oráculo cruza o limiar (μ = 0,1), e sempre na unidade de maior projeção (o próprio passado do alvo);
  - com μ = 0,05 a nula do teste **não** vale estritamente (D > 0), mas o desvio (~0,0013) fica abaixo de D_crit ≈ 0,1·√(2·5,63/32.000) ≈ 0,0019, e nem o oráculo cruza o limiar;
  - com μ = 0,1, D ≈ 0,0044 > D_crit.
- **Limitações:**
  - o Corolário 1 (garantia exata) exigiria μ ≲ 0,016, e a v0.52 usa 0,05, que está no **regime prático** da Proposição 3, não no da garantia;
  - as proposições tratam a perda sem recorte. O recorte coincide com ela quando os dois erros ficam dentro de B (a maioria dos passos com B = 2σ̂); o oráculo usa a perda recortada;
  - nas execuções com μ = 0,1 que aceitaram, o oráculo foi medido depois da aceitação, quando S já incluía a unidade. Isso só pode **reduzir** o valor medido ali e não altera a separação entre os valores de μ.

## 4. Implicações de desenho

1. **Condição de uso explícita:** num sistema que aceita estrutura por melhora preditiva sobre uma referência aprendida, a referência precisa ter desajuste pequeno em relação à margem, **M ≲ 4ε** para a garantia exata. Na prática, D < D_crit no horizonte de interesse.
2. **Três alavancas:**
   - reduzir o desajuste: passo menor ou mínimos quadrados de memória longa na referência;
   - aumentar a margem ε, o que custa poder;
   - usar os testes de estrutura contra uma referência "lenta" separada da previsão viva.
3. **Diagnóstico recomendado:** lotes nulos (alvos sem estrutura) e o oráculo de projeção, como controles de calibração sob a nula (no mesmo espírito de Han & Qu, 2026).

## 5. Relação com a literatura

- **Giacomini & White (2006):** testes de capacidade preditiva comparam métodos. A Proposição 1 é a forma explícita dessa distinção para um e-process que decide **estrutura**.
- **Clark & West (2007):** em comparações aninhadas com estimação em lote, o erro de estimação **penaliza** o modelo maior. Aqui o efeito vai no sentido oposto, porque o erro de estimação é o da **referência adaptativa**, e ele é previsível pelo passado.
- **Amoukou, Mishra & Veloso (2026):** mesma comparação incumbente × desafiante em árvores online, sem discutir o erro de estimação do incumbente. Numa folha estimada por média corrente, o desajuste é pequeno, o que pode explicar por que o efeito não aparece lá.
- **Han & Qu (2026):** monitores sempre válidos disparam em séries reais por falha de premissa (permutabilidade). O nosso caso é diferente: o teste é válido para a sua nula, e a falha está na **interpretação estrutural**.
