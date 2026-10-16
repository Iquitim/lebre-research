# 03 — F2: cascata memória–estrutura

**Questão.** É possível reduzir a redundância fazendo a estrutura aprender só a informação preditiva incremental não
explicada pela memória temporal?

**Resposta curta.**
- **[FATO]** Hoje, memória e estrutura são **paralelas**, e não em cascata. Três componentes modelam o passado do
  próprio alvo.
- **[RESULTADO]** Há um defeito documentado que a cascata ataca diretamente: entradas espúrias aceitas em séries
  integradas (M3, adiada para a v0.55).
- A redundância nunca foi medida. Remover a M1 não tem sustentação: o efeito isolado dela nunca foi medido, e ela faz
  parte do único ganho de precisão já confirmado.

Rótulos como em `01_ARCHITECTURE_BASELINE.md`.

## 1. Função real de cada componente

| Componente | Prevê | A partir de | Como usa o passado do alvo |
|---|---|---|---|
| **M**, memória (`_memory.py`) | yₜ | só o passado do alvo | parte de yₜ₋₁ (persistência) e soma ajustes: reversão à média, última diferença, sazonal ingênuo, incremento de um ciclo, perfil por fase |
| **S**, estrutura (`_core.py`) | yₜ | base [1, xₜ] (todas as entradas no atraso zero + passado do alvo padronizado) e blocos por banda de até 4 unidades aceitas | o passado do alvo é **uma entrada** padronizada por uma média lenta (taxa 10⁻⁴); pode virar unidade com bandas de atraso |
| Combinação M/S | L = m + wS·(s − m) | perda descontada de M e de S | — |
| **M1** (`_precision.py`) | yₜ, corrigindo L | yₜ₋₁, yₜ₋₂ e médias por banda das 5 entradas mais correlacionadas | regressão direta nas duas últimas observações |
| **M2** | saída final | referência trivial R e L' | R = 0, yₜ₋₁ ou yₜ₋ₛ |

**[DEDUÇÃO] Onde está a redundância potencial:**
1. **M, S e M1 modelam o passado do alvo**, cada um de um jeito: persistência mais ajustes; nível padronizado; regressão
   em yₜ₋₁ e yₜ₋₂.
2. **S e M1 modelam as entradas.** S usa todas no atraso zero e as aceitas por bandas; M1 usa as 5 mais correlacionadas
   por bandas, **sem teste**.
3. **M e M2 com referência de persistência partem do mesmo yₜ₋₁.**

**[FATO] Lacuna de medição:** nenhuma ablação registrada mede a contribuição marginal de cada componente dado os outros.
H2.1 não pode ser respondida com o que existe.

## 2. Por que a organização atual produz o defeito M3

**[RESULTADO]** (`LEBRE-V0.54-DESIGN-NOTE-01/M3_DIAGNOSTICO.md`, exploração com sementes 20261323–20261333). Em
passeios aleatórios independentes, entradas externas foram aceitas em 5 de 11 séries. Na família de níveis C03, 4 de 4
séries terminaram com uma entrada externa. A M4 não as remove, porque a contribuição delas não cai.

**[DEDUÇÃO] Mecanismo, pela identidade da F1** (`02`, §4):
- os testes comparam s com s + g;
- num alvo integrado, s não acompanha o nível, porque o passado do alvo entra padronizado por uma média lenta e sobra
  um componente que volta à média;
- logo ηₜ = f\*ₜ − sₜ é grande e previsível, e qualquer entrada que também passeia o projeta.

A memória **tem** raiz unitária (parte de yₜ₋₁), mas os testes não perguntam se a candidata melhora a memória. Eles
perguntam se ela melhora s.

## 3. A cascata, formalizada sem vazamento

Com mₜ a previsão da memória (função de y₍<t₎ apenas):

- **resíduo de inovação da memória:** rₜ = yₜ − mₜ, conhecido depois de yₜ;
- **estrutura incremental:** r̂ₜ = base·[1, xₜ] + Σᵤ wᵤ·bᵤ,ₜ, aprendida com o alvo rₜ (em vez de yₜ);
- **saída do núcleo:** Lₜ = mₜ + κₜ·r̂ₜ, com κₜ ∈ [0, 1] combinando "só memória" e "memória + estrutura" (substitui wS);
- **testes:** a referência passa a ser mₜ + r̂ₜ, e o desafiante mₜ + r̂ₜ + gₜ. A pergunta vira: "a candidata melhora a
  previsão **além do próprio passado do alvo**?" É a pergunta de Granger, feita sequencialmente.

**[DEDUÇÃO] Ausência de vazamento:** mₜ, r̂ₜ, gₜ e κₜ dependem só de y₍<t₎ e x₍≤t₎. O alvo rₜ é usado só no
aprendizado depois de yₜ, como o resíduo atual. A validade do e-process (F1, §2) continua valendo, porque a referência
segue previsível.

**[DEDUÇÃO] Ortogonalidade: três sentidos que não coincidem.**
- **Algébrica:** r̂ ajustado a r é ortogonal, na amostra, ao que a memória já usa, só se os atributos da memória
  estiverem entre os da estrutura. Não estão: a memória usa diferenças e perfis.
- **Estatística:** E[rₜ·(atributos da memória)] = 0 só quando a memória está bem ajustada. Ela é um NLMS com desajuste
  próprio, então sobra correlação.
- **Incrementalidade preditiva:** é a única que importa para a interpretação. É a propriedade testada pelo e-process
  da cascata.

**Riscos identificados antes de qualquer medição:**

| Risco | Por quê | Como detectar |
|---|---|---|
| **R1. O defeito da F1 muda de lugar** | o erro de estimação previsível passa a ser o da memória (NLMS μ = 0,05, 2 a 7 atributos); uma candidata que projete ηₘ ainda ganha | nulos com alvo AR forte e sazonal; oráculo de projeção sobre ηₘ |
| **R2. Perda onde a estrutura domina a memória** | se o alvo é quase todo explicado pelas entradas (bacias com chuva), r carrega o ruído da memória e a estrutura aprende mais devagar | ablação nas famílias de bacias; razão contra a v0.54 por família |
| **R3. Cointegração** | a informação incremental está no termo de correção de erro βxₜ − yₜ₋₁ | cenário cointegrado; conferir que a base, que tem xₜ e o passado do alvo padronizado, representa esse termo |
| **R4. Interação com a M1** | a M1 também regride em yₜ₋₁ e yₜ₋₂; com a cascata, o papel dela muda | ablações B × C |
| **R5. Custo** | a cascata tem o mesmo número de parâmetros; ela **não reduz custo** por si | contagem de operações e relógio |

## 4. Hipóteses e critérios (rascunho para o pré-registro; números a fixar antes de rodar)

| Hipótese | Resultado primário | Aceitação | Rejeição |
|---|---|---|---|
| **H2.5** a cascata reduz descobertas espúrias em séries integradas | fração de séries com entrada externa na estrutura final, em passeios aleatórios independentes (n ≥ 50) e em C03 | ≤ 1 de 4 em C03 (o critério da M3 da nota de desenho da v0.54) e limite superior do IC 95% ≤ 0,10 nos passeios | limite inferior do IC acima da fração da v0.54 |
| **H2.5-retenção** sem perder relações genuínas | fração de execuções que retêm a entrada verdadeira (cenários P1 a P3 do EXT-02 e cointegrado) | ≥ v0.54 − 5 p.p. | abaixo disso |
| **H2.5-precisão** sem piora preditiva | razão de erro cascata ÷ v0.54, bootstrap pareado por blocos, por família | limite superior ≤ 1,01 em toda família do banco de desenvolvimento | limite inferior > 1,01 em alguma família |
| **H2.1** há redundância mensurável | contribuição marginal de cada componente: aumento de erro ao retirá-lo, dados os demais (ablações D, E, F contra A) | um componente com contribuição marginal cujo IC contém 0 em ≥ 80% das famílias | todos com contribuição positiva |
| **H2.2** aprender sobre o resíduo melhora a eficiência | erro com o mesmo número de parâmetros (B contra A) | B ÷ A < 1 com IC abaixo de 1 em alguma família, sem piora em nenhuma | — |
| **H2.3** a cascata reduz custo | operações e tempo por passo | **não se espera** redução da cascata em si (R5); só a variante C pode reduzir | — |
| **H2.4** a M1 pode ser removida ou simplificada | razão C ÷ B por família | limite superior ≤ 1,01 em todas as famílias **e** custo menor | piora em alguma família (bacias é a candidata) |

**Tamanho de efeito relevante:** 1% no erro quadrático médio. É uma proposta deste programa, a justificar no
pré-registro: a auditoria da v0.54 usou 1,02 como sinal de alerta. A equivalência só é declarada quando o intervalo
inteiro fica dentro da margem, e nunca por ausência de significância.

## 5. Ablações obrigatórias, mapeadas no código

Todas são montadas **numa pasta de experimento**, por subclasses ou chaves locais. O núcleo canônico não é editado
(restrição 1). Antes de qualquer medida, cada variante passa por um teste de identidade: com a mudança desligada, ela é
idêntica à v0.54.

| Variante | Definição | Como construir |
|---|---|---|
| **A** | v0.54 canônica | `Lebre054(m5a, m5b, m4)`, sem mudança |
| **B** | cascata + M1 + M2 | subclasse do núcleo: S aprende rₜ = yₜ − mₜ; referência dos testes mₜ + r̂ₜ; κₜ por média dinâmica entre mₜ e mₜ + r̂ₜ |
| **C** | cascata, M1 desligada, M2 mantida | B com o especialista da M1 forçado a ω = 0 e sem cálculo (não é `core_only`, que desliga também a M2) |
| **D** | estrutura independente (sem resíduo), M1 desligada | A com a M1 desligada: isola o efeito da M1, que nunca foi medido sozinho |
| **E** | só memória | wS = 0 fixo, sem experimentos, com M2 |
| **F** | só estrutura | wS = 1 fixo, com experimentos, com M2 |

## 6. Cenários

- **Estacionários:** AR(1) e AR(2); ARMA(1,1).
- **Entradas:** exógena genuína com atraso 3; entrada redundante (cópia ruidosa da verdadeira); isca correlacionada
  (P2 do EXT-02).
- **Mudança de regime:** a relação muda de sinal na metade.
- **Integrados:**
  - I(1) com entrada genuína nas diferenças;
  - passeios aleatórios independentes (alvo e 5 entradas);
  - par cointegrado (y = βx + estacionário);
  - entrada que contém informação **não recuperável** pelo passado do alvo (choque exógeno conhecido só pela entrada).

Os cenários de desenvolvimento usam as sementes reservadas em `08`. A confirmação usa sementes novas e, para a
precisão, séries reais nunca usadas (CAMELS-BR posições 170+, BDG2 145+, 40 usinas eólicas; `docs/research/SEEDS.md`).

## 7. Métricas

Erro fora da amostra (MSE relativo a NLinear e à v0.54); incrementalidade (log-evidência do oráculo de projeção);
descobertas espúrias e retenção; operações por passo (contador analítico) **e** tempo de relógio; número de parâmetros
e de estados; erro nos 2.000 passos depois de cada mudança de regime. **Uma fração zero de falsas aceitações não é
garantia:** ela é reportada com o limite superior do IC.

## 8. Decisão

| Hipótese | Classe | Recomendação |
|---|---|---|
| H2.1 redundância mensurável | **INCONCLUSIVE** (plausível; nunca medida) | REQUIRE_ADDITIONAL_EXPERIMENTS (ablações D, E, F; baratas) |
| H2.2 eficiência representacional | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS (B × A) |
| H2.3 redução de custo pela cascata | **NOT_SUPPORTED** por dedução: mesma contagem de parâmetros | REJECT para a cascata em si; o custo só cai pela H2.4 |
| H2.4 remover ou simplificar a M1 | **NOT_SUPPORTED** com a evidência atual: efeito isolado nunca medido; M1 + M2 deram 0,879 em bacias | REQUIRE_ADDITIONAL_EXPERIMENTS (D antes, C depois). Não remover antes de medir (restrição 8). Motivo para medir: a M1 gasta 37% do custo na mediana |
| H2.5 menos descobertas espúrias em séries integradas | **PRELIMINARY_SUPPORT**: defeito real, mecanismo deduzido e coerente com a exploração; a correção não foi testada | **ADVANCE_TO_PROTOTYPE** (é a M3 da v0.55) |

**Desenho candidato:** variante B, com as ablações C a F como controles. A decisão sobre a M1 fica para depois de D e
de C. Antes disso, a M1 continua como está.
