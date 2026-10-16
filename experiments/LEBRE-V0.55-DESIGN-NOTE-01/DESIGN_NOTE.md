# LEBRE v0.55 — Nota de desenho 01: núcleo ancorado (rascunho 0)

**Data:** 16/10/2026 · **Status:** rascunho de desenho. Nenhum código, nenhuma medição. A linha de base é a v0.54
congelada (`f9906c4`, `lebre==0.3.0`), que não é editada. Origem: programa `LEBRE-V0.55-FRONTIERS-01`, decisão do
responsável de "ir para a fronteira, olhando o núcleo".

## 1. Por que mexer no núcleo

Três defeitos medidos da v0.54 têm a **mesma raiz**: a referência contra a qual os testes medem a evidência.

| Defeito | Evidência | Raiz |
|---|---|---|
| Entradas espúrias em séries de níveis (M3) | 5/11 passeios aleatórios independentes; 4/4 séries de C03 | a referência s não tem raiz unitária; o seu erro é previsível e qualquer entrada que passeia o projeta |
| Substitutas aceitas antes da verdadeira | até 20% das execuções numa célula (FDR 0,090) | a referência não contém a verdadeira; a substituta projeta o erro |
| Garantia estrutural só "prática" | condição exata M ≲ 4ε exigiria μ ≲ 0,016; o núcleo usa 0,05 | a referência dos testes é a própria previsão viva, aprendida com passo rápido |

A Nota formal F1 (`NOTA_FORMAL_F1.md`) mostra que o e-process é válido para a sua nula **qualquer que seja o aprendiz**.
Portanto a correção não está no e-process. Está em **escolher a referência de modo que a nula testada implique a nula
estrutural**. A ablação "tudo ligado" mostrou que os testes não melhoram a precisão. O valor da arquitetura está na
estrutura com evidência, e é essa garantia que este desenho procura tornar real.

## 2. Alvo teórico

**Definições.**
- φₜ: vetor de atributos da referência (memória + base + unidades aceitas).
- f\*ₜ = E[yₜ | ℱₜ₋₁].
- Uma unidade u é **estruturalmente nula** se os seus atributos não mudam f\*: f\*ₜ é função de informação que não
  passa por zᵤ.
- ηₜ = f\*ₜ − Rₜ: o erro previsível da referência.

**Hipóteses do alvo.**
- **(H0)** previsibilidade: vale por construção (Nota F1).
- **(A2) boa especificação da referência sob a nula:** existe θ\* (possivelmente variando devagar) tal que
  f\*ₜ = mₜ + θ\*ᵀφₜ.
- **(A3) erro de estimação pequeno:** no evento Ω_ref, (1/n) Σᵢ≤ₙ ηᵢ²/Bᵢ² ≤ ε para todo n, sobre os passos testados.

**Alvo T.** Sob (H0), (A2) e (A3),

  FDR estrutural das mudanças aceitas ≤ 2α + P(Ω_refᶜ).

**Caminho de prova.**
1. No evento Ω_ref, e para u estruturalmente nula, a Proposição 1 da nota de desajuste dá
   E[Δₜ | ℱₜ₋₁] ≤ ηₜ²/Bₜ². Logo Σμᵢ ≤ 0, e a nula estrutural está contida na nula testada N_h (Corolário 1).
2. O Teorema 2 e o Corolário da Nota F1 fazem o resto.

**O que falta provar, declarado agora:**
1. **Recorte.** A Proposição 1 usa a perda sem recorte; o teste usa a recortada. É preciso um limite de
   E[Δᶜˡⁱᵖ] − E[Δ], ou uma versão da identidade para a perda recortada.
2. **P(Ω_refᶜ).** Um limite para o NLMS lento sob hipóteses declaradas (ruído sub-gaussiano, atributos limitados,
   mistura), incluindo o período logo depois de cada mudança aceita.
3. **Falhas de (A2):** substitutas (a verdadeira ainda fora da referência), não linearidade, ciclo não declarado.
   O alvo **não cobre** esses casos. Eles continuam a cargo dos testes de remoção e das medições.

**Se a prova de 2 não sair, o alvo cai para um resultado de condição suficiente:** "se (A3) vale, então…". As
medições passam a estimar P(Ω_refᶜ) pelo oráculo de projeção. Isso já seria mais do que a v0.54 tem.

## 3. O que a âncora na memória compra, em teoria

- **Passeio aleatório sem estrutura:** f\*ₜ = yₜ₋₁. A memória parte de yₜ₋₁, então (A2) vale com θ\* = 0. Na v0.54, (A2)
  falha para s, e esse é o mecanismo da M3.
- **AR estacionário:** a memória tem reversão à média e a última diferença; com o passado do alvo também na base, (A2)
  vale para AR(1) e AR(2).
- **Cointegração:** o termo de correção βxₜ − yₜ₋₁ é linear na base, que contém xₜ e o passado do alvo padronizado.
  (A2) vale **aproximadamente**: a entrada está na base no atraso zero, mas a padronização causal tem média móvel lenta,
  e o termo só é linear a menos dessa deriva. É um caso a medir, não um caso coberto.
- **Bacias com chuva forte:** (A2) depende da estrutura aceita, como hoje.

## 4. Especificação (rascunho 0)

Tudo que não está listado aqui permanece **como na v0.54**: e-process, motores e níveis, M1, M2, M4, M5a, M5b, memória,
triagem, envelope, intervalo.

| Elemento | v0.54 | v0.55 (rascunho 0) |
|---|---|---|
| Alvo da estrutura | yₜ | rₜ = yₜ − mₜ (inovação da memória, conhecida depois de yₜ) |
| Estrutura de previsão | s, NLMS μ = 0,05 | ŝᶠ, NLMS μ = 0,05 sobre os mesmos atributos, com alvo rₜ |
| Combinação do núcleo | L = m + wS(s − m), wS por média dinâmica de M e S | L = m + κ·ŝᶠ, κ pela mesma média dinâmica entre "m" e "m + ŝᶠ" (mesmas constantes) |
| **Referência dos testes** | s (a previsão viva) | **Rₜ = mₜ + ŝˢₜ**, com ŝˢ uma cópia **lenta**: NLMS μ_ref = 0,01 sobre os mesmos atributos, alvo rₜ |
| Desafiante | g = s + a − r | g = R + a − r; RLS do desafiante sobre (y − R) + parte devolvida |
| Escala B | 2·max(σ̂ de y − s, piso) | 2·max(σ̂ de y − R, piso) |
| Remoção | g = s − contribuição da unidade em s | g = R − contribuição da unidade em ŝˢ |
| Mudança aceita | a unidade entra com os pesos do desafiante | entra em ŝᶠ e em ŝˢ com os pesos do desafiante (cópia previsível) |
| Assentamento | — | depois de cada mudança aceita, novos testes começam só após N_settle passos (inicial: 500; calibrar no desenvolvimento) |
| Triagem | resíduo y − s | resíduo y − R |

**Escolha de μ_ref = 0,01.** O Corolário 1 exige M ≲ 4ε = 0,008, e o NLMS tem M ≈ μ/(2 − μ). O desajuste medido no
EXT-01 ficou cerca de 1,5× acima do teórico (entradas coloridas). Com μ = 0,01: M_teórico = 0,005 e
M_esperado ≈ 0,0075 ≤ 0,008. Fica perto do limite e sem folga. Por isso o oráculo de projeção é medida obrigatória.

**Custo [DEDUÇÃO].** A cópia lenta acrescenta ~4p operações por passo, com p o número de atributos da referência
(d + 2 + blocos ativos; p ≈ 40 com d = 8). São ~160 operações, cerca de +18% sobre a mediana de 870 da v0.54. Uma
variante mais barata, a estudar só se o custo for decisivo: atualizar ŝˢ a cada 2 passos com μ_ref dobrado.

**Preço esperado [HIPÓTESE].**
- A referência lenta acompanha mal mudanças de regime. Logo depois de uma quebra, η cresce por atraso de
  acompanhamento, e não por desajuste, e (A3) pode falhar. A garantia exige estacionaridade local.
- O assentamento e a referência lenta atrasam descobertas.
- As duas coisas precisam ser medidas: atraso de detecção e aceitações nos 2.000 passos depois de quebras.

## 5. Medição de desenvolvimento D1 (a pré-registrar antes de qualquer execução)

**Variantes:**
- **A:** v0.54.
- **B:** núcleo ancorado completo.
- **B1:** só a âncora (referência = m + ŝᶠ, sem cópia lenta).
- **B2:** só a referência lenta, sem âncora (referência = cópia lenta de s).

As variantes B1 e B2 separam as duas alavancas. Elas ficam numa pasta de experimento, por subclasse. Antes de qualquer
medida, cada uma passa pelo teste de identidade (com tudo desligado, igual à v0.54) e pelo teste de não vazamento
(alterar o futuro não muda nenhuma previsão passada).

**Desfecho primário: FDR estrutural** (pela verdade do gerador). Os nulos e as alternativas seguem.

| Cenário | Para quê |
|---|---|
| Passeios aleatórios independentes (alvo + 5 entradas), n ≥ 50 | M3 |
| C03 (níveis) do banco | critério da nota v0.54: ≤ 1 de 4 |
| AR(1) e AR(2) com entradas independentes; alvo sazonal | (A2) e risco do erro da memória |
| Nulos com quebra de variância e de coeficiente | atraso de acompanhamento |
| P1–P3 do EXT-02 (verdadeira + isca, ruído AR, cauda pesada) | substitutas: fora do alvo, só medido |
| Cointegrado; I(1) com entrada nas diferenças; choque exógeno só visível na entrada | retenção do que é genuíno |

**Critérios (rascunho; fixar no pré-registro):**

| Hipótese | Aceitação | Rejeição (abandona o desenho) |
|---|---|---|
| D1-a: B reduz espúrias em séries integradas | passeios: limite superior do IC 95% ≤ 0,10; C03: ≤ 1/4 | passeios: limite inferior ≥ o da v0.54 |
| D1-b: nulos estacionários sem piora | 0 aceitações com limite superior do IC ≤ 0,05 em cada célula | alguma célula com limite inferior > 0,05 |
| D1-c: o oráculo confirma (A3) | D máximo por unidade < 0 (média), em ≥ 90% das execuções nulas | D > D_crit em > 10% |
| D1-d: retenção do genuíno | ≥ v0.54 − 5 p.p. em cada cenário de alternativa | abaixo |
| D1-e: atraso de detecção | mediana ≤ 1,5 × v0.54 | > 2 × |
| D1-f: precisão no banco do LEBRE Lab | razão B ÷ A com limite superior ≤ 1,01 por família | limite inferior > 1,01 em alguma família |
| D1-g: custo | média ≤ 1,25 × v0.54; pico registrado | > 1,5 × |

**Decisões possíveis depois da D1:**
- B passa: rascunho 1 e validação em dados nunca vistos (CAMELS-BR 170+, BDG2 145+, eólicas);
- só B1 passa: a âncora basta, e a referência lenta sai (mais simples);
- só B2 passa: a garantia vem da referência lenta, e a M3 continua aberta;
- nenhuma passa: registrar o resultado negativo e voltar ao diagnóstico.

**Sementes:** da faixa reservada 2026101500–2026102999, a dividir no pré-registro e registrar em
`docs/research/SEEDS.md`.

## 6. Etapas até uma v0.55

1. **Agora:** esta nota + Nota formal F1. Conferência independente da F1. Formulação do item "recorte" (§2, item 1).
2. Protótipo em `experiments/LEBRE-V0.55-PROTO-01` (cópia da v0.54 mais um arquivo novo; nada da v0.54 editado).
   Testes de identidade e de não vazamento.
3. Pré-registro e execução da D1.
4. Se passar: validação em dados novos; em paralelo, a correção da M4 (F3, variante A′), sobre o núcleo novo.
5. Avaliação final pré-registrada da v0.55, com regra de promoção vinculante e reserva nova.
