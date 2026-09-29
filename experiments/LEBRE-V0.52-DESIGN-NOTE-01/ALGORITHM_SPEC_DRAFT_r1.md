# LEBRE v0.52 — Especificação do algoritmo integrado (rascunho 1)

**Data:** 27/09/2026 · **Status:** rascunho de desenvolvimento. Ainda não há pré-registro; os números abaixo vêm de dados de desenvolvimento e de conjuntos semi-sintéticos declarados antes de cada medição.
**Substitui:** o rascunho 0 (25/09/2026), que descrevia hipóteses por atraso individual. Essa forma continua existindo como ablação ("v0.52 atômica").

## 0. Ideia em uma frase

Um previsor online de custo fixo em que **toda mudança de estrutura é um experimento**. Um desafiante roda em sombra e é comparado com o modelo vigente por um e-process de melhora preditiva. A mudança só é aceita dentro de um controle de mudanças falsas válido para o fluxo inteiro. A **unidade de mudança é uma entrada inteira**, cuja resposta é depois refinada de forma hierárquica.

## 1. Componentes

| Componente | Função | Custo típico (FP/passo) |
|---|---|---|
| **M: memória** | Nível e ciclo do próprio alvo (reversão à média, diferença, sazonal, perfil), NLMS com pisos de escala | 23–49 |
| **S: especialista estrutural** | Base densa (viés + valor atual de cada entrada) + blocos de resposta das unidades aceitas | ~50 + ~40 por unidade ativa |
| **Combinação** | Média dinâmica de modelos entre M e S (w_S) | ~10 |
| **Vagas de experimento** (m = 2) | Cada vaga roda um desafiante e acumula evidência | 0–250 (depende de haver experimento ativo) |
| **Triagem** | Estatística de grupo por entrada, com pré-branqueamento, a cada 4 passos | 50–70 |
| **Controle** | Níveis de aceitação, escala, intervalo | ~25 |

**Custo medido:** 359 FP/passo em média nas séries reais de desenvolvimento (perfil padrão). O contrato de complexidade previa ≤ 250 (ver §8).

## 2. Unidades de mudança

- **Entrada i** (inclui o próprio passado do alvo como entrada padronizada): bloco de resposta com as médias do passado de x_i em faixas de oitava, [1], [2–3], [4–7], [8–15] e [16–31].
- **Estado latente do resíduo:** dois filtros do erro padronizado, com polos 0,8 e 0,95.
- **Divisão de faixa** (hierárquica): numa entrada já aceita, a faixa [lo, hi] pode ser substituída pelas médias das duas metades. Cada divisão é uma nova hipótese, testada só depois de o "pai" ter sido aceito (teste hierárquico; Meinshausen 2008; Yekutieli 2008).
- **Tipos de experimento:** acrescentar (margem ε = 0,002), remover (ε = −0,002, basta não piorar), trocar (quando há 4 unidades ativas) e dividir (ε = 0,002).

## 3. Desafiantes

- O desafiante de uma entrada ajusta, por **mínimos quadrados recursivos dentro do episódio**, o bloco de faixas mais o valor atual x_i(t). O bloco é assim julgado líquido do que x_i(t) já carrega (colinearidade).
- **Atraso de pico:** o desafiante carrega também o atraso isolado mais forte da entrada. Ele é escolhido pelo próprio desafiante, pela correlação pré-branqueada acumulada na primeira metade do aquecimento, e essa estatística é **persistente entre episódios** da mesma hipótese. Só usa o passado. Sem o pico, um atraso isolado fica diluído na média da faixa (1/largura do efeito); com ele, respostas estreitas e largas são representadas.
- **Aquecimento:** as primeiras 200 amostras de um episódio só treinam o desafiante e não geram evidência (subsequência previsível).
- Qualquer desafiante previsível mantém a validade do teste. A escolha do desafiante afeta só o poder.

## 4. Evidência

- **Perda limitada:** ℓ_t(u) = min{(y_t − u)²/B_t², 1}, com B_t = 2·max(σ̂_t, 0,1·s_t). σ̂_t é a escala recente do erro do especialista estrutural. s_t é a **escala lenta** de y (EMA 10⁻⁴, média simples no início). Sem esse piso, trechos de alvo constante tornam qualquer ganho absoluto minúsculo em evidência grande (caso observado: estruturas aceitas com o aquecimento de um prédio desligado).
- **Diferencial:** d_t = ℓ_t(S_t) − ℓ_t(g_t) − ε. As mudanças são julgadas na previsão do especialista estrutural (opção IIb).
- **E-process unilateral:** mistura uniforme sobre 8 valores de λ, exp{λ Σd − ψ_{E,c}(λ) V}, com V = Σ(d_i − γ_i)², γ_i = min(média passada, 0) e ψ_{E,c}(λ) = (−log(1 − cλ) − cλ)/c².

### 4.1 Validade com c = 1 + max(ε, 0)

A forma de Choe & Ramdas (2024) supõe |d_i − γ_i| ≤ c, com c igual à amplitude total. A demonstração de base (Howard, Ramdas, McAuliffe & Sekhon 2021, §A.8) usa só o lema de Fan, Grama & Liu (2015): exp{λξ − ψ_E(λ)ξ²} ≤ 1 + λξ para ξ ≥ −1 e λ ∈ [0, 1).

Para o teste unilateral (λ ≥ 0), sob a nula fraca E_{i−1}[d_i] = μ_i ≤ 0, basta d_i − γ_i ≥ −c:
- E_{i−1}[exp{λ(d_i − γ_i) − ψ_{E,c}(λ)(d_i − γ_i)²}·e^{λ(γ_i − μ_i)}] ≤ (1 + λ(μ_i − γ_i))·e^{λ(γ_i − μ_i)} ≤ 1;
- como λ Σd ≤ λ Σ(d − μ), o processo é limitado por uma supermartingala não negativa.

Como d_i ≥ −(1 + ε) e γ_i ≤ 0, vale c = 1 + max(ε, 0). A mistura de e-processes é um e-process, e as pausas entre episódios são uma subsequência previsível. Na simulação (400 trajetórias × 5.000 passos, nula no limite), o erro tipo I ficou ≤ 0,025 contra α = 0,05. O poder subiu de 0,66 para 0,77 em relação a c = 2.

### 4.2 Alternativa estudada e não adotada

Apostas com λ previsível (aGRAPA; Waudby-Smith & Ramdas 2023): válidas e ~2,4× mais rápidas em simulação. Com entradas quase idênticas (correlação 0,98), porém, aceitam a substituta da entrada verdadeira. Não é erro do controle de melhora preditiva; é um limite de identificabilidade. Ficam para um critério de descoberta que trate entradas quase colineares como grupo.

## 5. Aceitação e controle de mudanças falsas

- Hipóteses persistentes: um e-process por mudança candidata, acumulado entre episódios.
- Nível tipo e-LOND fixado na criação: γ = 1/(2P) para as primeiras P = 2 × (número de unidades) hipóteses, depois 0,5·γ_k com γ_k ∝ 1/(k log² k); nível = α·γ·(R + 1), com R = mudanças já aceitas.
- Encerramento de episódio: aceitação; regra de varredura (evidência do episódio ≤ 0 após 100 amostras); ou 5.000 amostras.

## 6. Triagem e escalonamento

- **Triagem por entrada:** correlações EMA (peso 0,02, a cada 4 passos) entre o resíduo pré-branqueado e as médias de faixa pré-branqueadas. O pré-branqueamento é AR(1) por entrada, com coeficiente causal (Box–Jenkins). A estatística de grupo é a soma dos quadrados em unidades da escala nula, e a unidade é aberta se a estatística passar do quantil 99% de χ²₅.
- **Triagem de divisões:** correlação do resíduo com o detalhe de Haar (média da metade esquerda − direita), aberta acima do quantil 99% de χ²₁.
- **Prioridade:** remoção periódica das unidades ativas; depois, o melhor candidato (unidade ou divisão) acima do limiar; espera de 2.000 passos entre episódios da mesma hipótese.

## 7. Resultados de desenvolvimento (medição #3, conjunto declarado antes)

- **Semi-sintéticos com entradas reais** (5 tarefas × 3 sementes novas): a entrada verdadeira foi encontrada em 3/3 sementes em duas das três tarefas estruturadas. Nenhuma entrada exógena fora da verdade foi aceita. Latência de 4 mil a 17 mil passos.
- **Sintéticos puros:** estruturas recuperadas até o atraso exato (por exemplo, atraso 12 com peso 0,84 contra 0,8 verdadeiro), em 500–2.200 passos.
- **Séries reais de desenvolvimento** (29 tarefas: vazões do ONS, CAMELS-BR, BDG2, Silverbox, Cascaded Tanks), média geométrica do NMSE relativo ao NLinear online, nos mesmos 1.000 pontos para todos:

| Grupo | v0.52 (esta) | Chronos-2 com covariáveis | v0.52 atômica | ARX denso online | SARIMAX-X |
|---|---|---|---|---|---|
| ONS | **0,472** | 0,500 | 0,535 | 0,529 | 0,847 |
| CAMELS | 0,870 | 0,838 | 0,951 | 1,208 | **0,825** |
| BDG2 | 0,916 | **0,718** | 0,920 | 2,008 | 0,970 |
| Todas | **0,645** | 0,701 | 0,757 | 1,109 | 0,988 |

Todos os comparadores recebem as mesmas entradas. O Chronos-2 recebe as covariáveis passadas e o valor atual das entradas como covariável futura conhecida. Custo: ~360 FP/passo contra ~10⁹–10¹⁰ estimados para o Chronos-2.

## 8. Limitações e questões abertas

1. **Custo × descoberta.** O perfil que cumpre o contrato (≤ 250 FP; 1 vaga, mínimos quadrados a cada 4 passos) mantém a precisão (todas: 0,666 nos 1.000 pontos), mas perde quase toda a descoberta em entradas suaves. O custo fixo é dominado pela memória, pelos pesos dos blocos ativos e pela triagem.
2. **Entradas quase idênticas** não são distinguíveis por melhora preditiva. A descoberta deveria reportar grupos de entradas equivalentes.
3. **Estrutura com memória longa em entrada suave** (armazenamento com polo 0,85) não foi descoberta: o valor atual e o próprio passado do alvo já carregam essa informação.
4. **Prédios (BDG2):** longe do Chronos-2. Provavelmente faltam ciclos semanais e padrões de ocupação, que a memória não representa.
5. **Falso positivo no próprio passado do alvo** em 1 de 3 sementes de um alvo ruído branco: compatível com o controle em α, mas registrado.
6. Tudo acima vem de dados de desenvolvimento. A avaliação confirmatória exige pré-registro e dados reservados.

## 9. Adendo (27/09/2026, medição #4)

- **Grupos de entradas equivalentes:** o modelo mantém uma correlação causal (EMA) entre as entradas e, junto de cada entrada aceita, reporta as quase idênticas (|corr| ≥ 0,95). Exemplo: aceita x1 e reporta o grupo {x0, x1} (duas usinas vizinhas, correlação 0,98). A decisão não muda; muda o que se afirma: "esta entrada ou uma equivalente".
- **Segundo ciclo declarado na memória:** em séries horárias de prédios, a semana (168 h) entra como metadado, igual ao dia (24 h), com dois termos a mais na memória (ingênuo semanal e seu incremento). BDG2: 0,927 → 0,910 no conjunto completo; 0,916 → 0,887 nos 1.000 pontos.
- **Triagem** restrita às entradas ainda não ativas.
- **Cortes de custo avaliados e rejeitados:** pesos vivos atualizados em passos alternados (Silverbox 0,095 → 0,198) e mínimos quadrados do desafiante em passos alternados (Silverbox → 0,143). A estrutura aceita e o desafiante precisam ser atualizados a cada passo.
- **Medição #4** (conjunto declarado antes, sementes novas): entradas verdadeiras (ou do grupo) descobertas nas três tarefas estruturadas; zero aceitações fora da verdade, inclusive num nulo em que a entrada muda só a variância do alvo; séries reais 0,641 nos 1.000 pontos (Chronos-2 com covariáveis 0,701); custo 353 FP/passo. **Falha no contrato de 250 FP.**

## 10. Adendo (27/09/2026, contrato revisado e medição #5)

- **Contrato de custo do perfil padrão:** média ≤ 400 FP/passo nas séries reais (revisado depois da medição #4). A âncora externa é o ARX denso online com as mesmas entradas, que custa 144 + 132·d FP/passo. A v0.52 custa menos que ele **na média** (353 contra 390), mas não série a série: com uma só entrada, o ARX custa 276 e a v0.52 261–450, porque o custo dela é quase fixo. Picos: p99,9 até 1.304 FP e máximo 1.414 FP, quando duas vagas aquecem ao mesmo tempo. Ainda não há limite de pico.
- **Medição #5** (replicação com sementes e estruturas novas, código inalterado): passa nos seis critérios. Descobre a entrada verdadeira em duas de três tarefas estruturadas, sem aceitar entradas externas falsas.
- **Limitação identificada:** em alvos sem estrutura, o próprio passado do alvo foi aceito em 2 de 15 execuções. A causa provável é que o desafiante também re-ajusta o coeficiente do valor atual da entrada, e esse re-ajuste melhora a previsão frente à base em NLMS sem que exista estrutura. A correção proposta é um controle pareado (mesmo re-ajuste, sem o bloco).

## 11. Adendo (27/09/2026, medição #6): condição de uso — referência com desajuste pequeno

- **Achado:** com a base S aprendendo por NLMS com passo 0,1, alvos sem nenhuma estrutura tinham a unidade do próprio passado aceita em ~20% das execuções (desenvolvimento, 8 de 40). O desajuste do NLMS (~μ/2 do ruído) cria um erro de S **previsível pelo passado**, porque a oscilação dos pesos depende dos dados recentes. Um bloco do próprio passado cancela parte desse ruído: há melhora real sobre S, mas ela vem da imperfeição do aprendiz, não de estrutura.
- **Condição de uso do método:** para que "melhora preditiva sobre a referência" signifique "estrutura", a referência precisa ter desajuste pequeno. Um controle pareado (re-ajuste do valor atual sem o bloco) foi testado e não resolve.
- **Correção adotada:** passo da base μ = 0,05. Resultado: zero aceitações em 40 execuções nulas de desenvolvimento e em 30 da medição #6 (critério ≤ 3 de 30).
- **Medição #6** (conjunto declarado antes): passa nos sete critérios. Séries reais nos 1.000 pontos: 0,653 (Chronos-2 com covariáveis 0,701); custo médio 360 FP/passo.

## 12. Adendo (27/09/2026, medição #7): picos de custo e limite de informação

- **Controle de pico sem mudar a estatística:**
  1. no máximo um desafiante em aquecimento por vez;
  2. cada parte da triagem (cada entrada, o estado latente, os grupos, cada divisão) é atualizada na sua própria fase, com a mesma frequência de antes;
  3. a estatística do atraso de pico processa metade dos atrasos por passo, alternando (aquecimento 250, escolha em 200; o mesmo número de amostras por atraso).

  Pico máximo nas séries reais de desenvolvimento: 1.409 → **904** FP/passo; média 380. O escalonamento custa ~2% de precisão, porque adia aberturas.
- **Limite de informação em entradas muito suaves:** um oráculo online (desafiante que conhece o atraso verdadeiro, testa desde o início e nunca é encerrado) julgado pelo mesmo e-process precisa de 9 a 27 mil passos, ou não chega em 32 mil, para descobrir y = 0,6·x(t−k) quando x tem autocorrelação ~0,99. A informação nova de um atraso de entrada suave, além do valor atual, é pequena. **Escopo declarado:** a descoberta com garantia só é esperada quando a entrada carrega informação suficiente no horizonte disponível. Nesses casos a previsão continua boa, porque a base usa o valor atual das entradas.
- **Opções avaliadas e desligadas:** triagem com média de faixa bruta e desafiante persistente sem esquecimento com episódios longos. Ganho pequeno (dentro do ruído) e uma aceitação falsa fora de grupo no desenvolvimento.
- **Medição #7** (declarada antes, focada em entradas suaves): passa em sete de oito critérios (segurança, precisão, custo médio, pico, nulos 0/30). Falha na descoberta das entradas mais suaves, como esperado. Séries reais nos 1.000 pontos: 0,669 (Chronos-2 com covariáveis 0,701).

## 13. Adendo final (27/09/2026): lacunas do alvo, avaliação em dados reservados e posição na literatura

**Princípio de avaliação:** a LEBRE não precisa ser a melhor; precisa **entregar bem com orçamento mínimo e sem falhas catastróficas**. Os modelos caros (SARIMAX ajustado série a série, ARX por mínimos quadrados, Chronos-2) são **tetos de referência**, não adversários.

**Falha encontrada em dados reservados (125 séries nunca vistas):** quando o alvo falta por vários passos, a memória preenchia o próprio histórico com as próprias previsões (malha aberta). Com certos pesos aprendidos, a recursão é instável: 6 de 125 séries explodiram (até 10⁷⁹). Fora dessas séries, o erro relativo ao NLinear foi 0,706, igual ao do desenvolvimento.

**Correção (duas peças, ~15 FP/passo):**
1. durante a lacuna, a memória recebe o **último valor observado** (retenção), nunca a própria previsão;
2. **contrato de saída:** a previsão é limitada ao envelope dos alvos observados (máximo e mínimo correntes que relaxam devagar para a média, taxa 10⁻³), alargado em 0,5× a sua largura; uma previsão não finita vira o último valor observado.

No teste de estresse do desenvolvimento, as explosões foram de 10 para 0, e o erro caiu ~2% mesmo sem lacunas injetadas.

**Avaliação pré-registrada em 40 séries nunca vistas** (20 bacias do CAMELS-BR, 20 medidores do BDG2):

| Modelo | Erro relativo ao NLinear (IC 95%) | Séries > 1,5 | Catastróficas | FP/passo |
|---|---|---|---|---|
| **LEBRE v0.52 corrigida** | **0,767** [0,657; 0,858] | 0% | 0 | 407 |
| LEBRE v0.52 sem a correção | 1,107 | 7,5% | 2 | 392 |
| DLinear online (melhor comparador na classe) | 0,957 | 5% | 0 | 1.533 |
| SARIMAX com entradas (teto clássico) | 0,767 | 0% | 0 | ajuste por máxima verossimilhança |
| Chronos-2 com covariáveis (teto grande, 1.000 pontos) | 0,662 (v0.52: 0,769) | — | — | ~10⁹–10¹⁰ |

A v0.52 corrigida foi a **mais precisa e a mais robusta da classe de orçamento**, empatou com o SARIMAX com entradas e ficou com erro 16% acima do Chronos-2 com covariáveis. **O custo médio (407) e o pico (1.015) passaram ~2% dos limites declarados** (400 e 1.000).

**Posição na literatura (auditoria PRA-04):**
- o mecanismo central, aceitar mudanças estruturais por e-process de melhora preditiva com controle de erro no fluxo, **já existe** em árvores de decisão online (Amoukou, Mishra & Veloso, 2026), sobre Choe & Ramdas (2024) e e-LOND;
- a v0.52 contribui com a **extensão e a integração**: séries com entradas, unidades por entrada, refinamento hierárquico, testes de remoção e troca, controle de FDR e orçamento fixo;
- contribui também com o **achado da condição de uso** (a referência precisa ter desajuste pequeno; relacionado a Giacomini & White, 2006, e a Han & Qu, 2026) e com a **evidência empírica sob orçamento**.
