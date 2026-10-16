# Nota formal F1 — Validade dos e-processes da LEBRE sob aprendizado adaptativo e controle de mudanças falsas com decisões assíncronas

**Data:** 16/10/2026 · **Objeto:** o código congelado da v0.54 (`experiments/LEBRE-V0.54-PROTO-01/lebre054`, commit
`f9906c4`; `lebre==0.3.0` tem a mesma árvore sintática). **Status:** prova escrita por quem fez a dedução. **Falta a
conferência por um leitor independente** antes de citar o resultado como garantia (Etapa 0.2 do roteiro em
`LEBRE-V0.55-FRONTIERS-01/08_PROPOSED_RESEARCH_ROADMAP.md`).

**Conferência numérica (não é prova):** `check_inequalities.py` verifica as duas desigualdades usadas, nas faixas
exatas do código, e as somas das sequências de níveis. Resultado: PASS.

## 1. Objeto

Considere uma hipótese de mudança estrutural h. Os passos em que h é testada formam um conjunto 𝒯 ⊂ ℕ, escolhido de
forma previsível. Os passos ficam fora de 𝒯 nas situações seguintes:
- fora dos episódios de teste;
- nos 250 primeiros passos de um desafiante de adição;
- em quarentena;
- fora do contrato de entrada.

Para t ∈ 𝒯, o incremento é

  dₜ = ℓ(yₜ, Rₜ) − ℓ(yₜ, Gₜ) − ε,  ℓ(y, f) = min{(y − f)²/Bₜ², 1},

com a referência Rₜ, o desafiante Gₜ e a escala Bₜ > 0. A filtração (ℱₜ) é a da informação disponível antes de yₜ₊₁.

**(H0) Hipótese de previsibilidade.** Rₜ, Gₜ, Bₜ e o indicador 1{t ∈ 𝒯} são ℱₜ₋₁-mensuráveis.

**[FATO]** No código, (H0) vale:
- Rₜ = sₜ, Gₜ e Bₜ são calculados em `predict`, antes de yₜ;
- os pesos do NLMS, os do RLS do desafiante e σ̂ᵣ só mudam em `observe`, depois de dₜ;
- a escolha de 𝒯 usa contadores e limiares do passado.

**Nenhuma hipótese sobre o modo de aprendizado entra além de (H0).** O passo do NLMS, o seu desajuste e qualquer
não estacionariedade dos dados ficam fora do argumento.

**O e-process do código.** Com c = 1 + max(ε, 0), a grade Λ = {0,9·2⁻ʲ/c : j = 0, …, 7} e
ψ(λ) = (−log(1 − cλ) − cλ)/c², para n testes realizados:

  eₙ = (1/|Λ|) Σ_{λ∈Λ} exp(λSₙ − ψ(λ)Vₙ),  Sₙ = Σᵢ dᵢ,  Vₙ = Σᵢ (dᵢ − γᵢ)²,

em que γᵢ = max(−c, min(0, média de d₁, …, dᵢ₋₁)), com γ₁ = 0, e as somas correm sobre os n primeiros passos de 𝒯.

**Nula fraca de h (N_h).** Com μᵢ = E[dᵢ | ℱ_{tᵢ−1}], vale Σ_{i≤n} μᵢ ≤ 0 para todo n até o instante considerado. É a
nula fraca de Choe & Ramdas (*Comparing Sequential Forecasters*, Operations Research, 2024). Por depender das médias
condicionais ao longo da trajetória realizada, N_h é um **evento** do espaço de probabilidade, e não uma propriedade
fixa da distribuição. Escrevemos N_h(n) para "a desigualdade vale para todo m ≤ n".

## 2. Lemas

**Lema 1 (desigualdade de Fan, escalada).** Para c > 0, 0 ≤ λ < 1/c e y ≥ −c,

  exp(λy − ψ(λ)y²) ≤ 1 + λy.

*Origem.* Para c = 1, é a desigualdade de Fan, Grama & Liu (2015), usada na forma de Howard, Ramdas, McAuliffe &
Sekhon (2021). O caso geral sai da substituição y ↦ y/c, λ ↦ cλ: ψ(λ) = ψ₁(cλ)/c², com ψ₁(u) = −log(1 − u) − u.
Conferência numérica: `check_inequalities.py` (L1). *Referências citadas de memória, a conferir no texto original.*

**Lema 2.** Para todo a real, e^{−a}(1 + a) ≤ 1.

*Prova.* 1 + a ≤ eᵃ. ∎

**Lema 3 (faixa).** No código, dᵢ − γᵢ ≥ −c.

*Prova.* As perdas recortadas estão em [0, 1]. Logo dᵢ ≥ −1 − ε, e para ε ≥ 0 isso dá dᵢ ≥ −c. Para ε < 0 (remoção:
ε = −0,002, c = 1), dᵢ ≥ −1 + |ε| > −c. Além disso γᵢ ≤ 0, então dᵢ − γᵢ ≥ dᵢ ≥ −c. ∎

## 3. Teorema 1 (validade sob a nula fraca, qualquer aprendiz previsível)

**Enunciado.** Sob (H0), o processo Mₙ := (1/|Λ|) Σ_λ exp(λ Σᵢ≤ₙ (dᵢ − μᵢ) − ψ(λ)Vₙ) é uma supermartingala não
negativa com M₀ = 1, sob **qualquer** distribuição dos dados. No evento N_h(n), eₙ ≤ Mₙ. Em consequência, para todo
tempo de parada τ e todo α ∈ (0, 1):

  (a) E[e_τ · 1{N_h(τ)}] ≤ 1 (para τ limitado; para τ qualquer, pelo lema de Fatou);
  (b) P(∃ n: eₙ ≥ 1/α e N_h(n)) ≤ α.

**Prova.** Fixe λ ∈ Λ e escreva Yᵢ = dᵢ − γᵢ. Pelo Lema 3, Yᵢ ≥ −c, e λ < 1/c pela construção da grade. Como γᵢ e μᵢ
são ℱ_{tᵢ−1}-mensuráveis, o Lema 1 dá

  exp(λ(dᵢ − μᵢ) − ψ Yᵢ²) = e^{λ(γᵢ − μᵢ)} exp(λYᵢ − ψYᵢ²) ≤ e^{λ(γᵢ − μᵢ)} (1 + λYᵢ).

Tomando a esperança condicional e com aᵢ = λ(μᵢ − γᵢ), vale E[1 + λYᵢ | ℱ] = 1 + aᵢ. Logo

  E[exp(λ(dᵢ − μᵢ) − ψYᵢ²) | ℱ_{tᵢ−1}] ≤ e^{−aᵢ}(1 + aᵢ) ≤ 1,

pelo Lema 2. Os passos fora de 𝒯 não alteram o processo, e a escolha deles é previsível por (H0). Então o produto dos
fatores é uma supermartingala na filtração dos tempos de teste. Uma média finita de supermartingalas com valor inicial 1
também é uma.

Agora, eₙ = (1/|Λ|) Σ_λ e^{λΣμᵢ}·exp(λΣ(dᵢ − μᵢ) − ψVₙ). No evento N_h(n), Σμᵢ ≤ 0 e λ ≥ 0, então cada termo fica
abaixo do correspondente de Mₙ, e eₙ ≤ Mₙ.

- **(a):** pela parada opcional, E[M_τ] ≤ 1 para τ limitado, e e_τ·1{N_h(τ)} ≤ M_τ.
- **(b):** seja σ o primeiro n com eₙ ≥ 1/α e N_h(n). Nesse instante, M_σ ≥ e_σ ≥ 1/α. Pela desigualdade de Ville,
  P(supₙ Mₙ ≥ 1/α) ≤ α. ∎

**Consequências diretas:**
1. **Adaptação.** O NLMS da referência (μ = 0,05), o RLS do desafiante, a M1 e a M2 entram só por (H0). Nenhuma taxa
   de aprendizado, desajuste, dependência temporal, heterocedasticidade ou quebra de regime invalida o teste para N_h.
2. **Persistência.** Uma hipótese persistente acumula episódios com desafiantes diferentes. Os episódios são escolhas
   previsíveis de 𝒯 e não exigem nada a mais.
3. **Duração mínima** (M4: aceitar só depois de 5.000 testes). Ela restringe o instante de aceitação a um tempo de
   parada, o que (a) e (b) permitem.
4. **O que o teorema não diz.** N_h é uma nula sobre a **diferença de perda contra a referência**, uma comparação de
   métodos. Ela não é a nula estrutural "os atributos da unidade não acrescentam informação". A distância entre as duas
   é o erro de estimação previsível da referência (nota `LEBRE-V0.52-EXT-01/MISADJUSTMENT_NOTE.md`, Proposição 1).

## 4. Teorema 2 (FDR de um motor com níveis fixados na criação e decisões assíncronas)

**Objeto [FATO].** Num motor, as hipóteses recebem índices j = 1, 2, … na ordem de criação, e o nível

  αⱼ = min{α·gⱼ·(Rⱼ + 1), 1/2}.

Aqui gⱼ ≥ 0 é função **só de j**, com Σⱼ gⱼ ≤ 1, e Rⱼ é o número de aceitações do motor antes da criação de j. A
hipótese j é aceita no primeiro instante de revisão em que log eⱼ ≥ log(1/αⱼ) e as condições de duração forem cumpridas.
Uma hipótese aceita é retirada e nunca mais aceita: um reteste da mesma mudança cria um índice novo. As decisões são
assíncronas: j pode ser aceita depois de j' > j ter sido criada, ou nunca.

**Sequências do código** (conferidas em `check_inequalities.py`):
- **motor principal:** P = 2(d + 2); gⱼ = 1/(2P) para j ≤ P e gⱼ = γ_{j−P}/2 depois, com γₖ = C/(k·log²(k + 1)) e C
  escolhido para Σγₖ ≤ 1. Logo Σgⱼ ≤ 1;
- **motor das remoções disparadas (M4):** gⱼ = γⱼ.

**Enunciado.** Para todo instante T (ou tempo de parada limitado), sejam R_T o total de aceitações do motor até T e
V_T o número de hipóteses j aceitas até T no evento N_j(τⱼ), em que τⱼ é o instante da aceitação. Sob (H0) para cada
hipótese:

  FDR_T := E[V_T / max(R_T, 1)] ≤ α,

sob **dependência arbitrária** entre as hipóteses.

**Prova.** Para cada j, seja τⱼ o instante de aceitação, ou T se j não for aceita até T, e Eⱼ = eⱼ(τⱼ ∧ T).

1. **Desigualdade de Markov, ponto a ponto:** 1{j aceita até T} ≤ αⱼ·Eⱼ, porque a aceitação exige Eⱼ ≥ 1/αⱼ.
2. **Monotonia:** se j é aceita até T, então R_T ≥ Rⱼ + 1. As aceitações não diminuem, e as Rⱼ anteriores à criação
   de j não incluem j.
3. **Combinando,** no evento em que j é aceita até T sob N_j(τⱼ):

   1{j conta em V_T}/max(R_T, 1) ≤ αⱼEⱼ·1{N_j(τⱼ)}/(Rⱼ + 1) ≤ α·gⱼ·Eⱼ·1{N_j(τⱼ)},

   usando αⱼ ≤ α·gⱼ·(Rⱼ + 1).
4. **Esperança:** gⱼ é determinístico, e o Teorema 1(a) dá E[Eⱼ·1{N_j(τⱼ ∧ T)}] ≤ 1. Somando em j:
   FDR_T ≤ α Σⱼ gⱼ ≤ α. ∎

O argumento é o do e-LOND (Xu & Ramdas, AISTATS 2024). As decisões assíncronas e o teto de 1/2 não exigem nada a mais:
o teto só diminui os níveis, e a assincronia entra apenas pela monotonia do passo 2.

**Observação (nula dependente da trajetória).** Tratar "j é nula" como o evento N_j(τⱼ), e não como um rótulo fixo, é
o que permite aplicar o Teorema 1 a hipóteses cujas médias condicionais dependem do próprio caminho: episódios,
desafiantes e referência. Isso define o FDR em relação à nula fraca de comparação de métodos. É uma definição mais
fraca do que um FDR "estrutural".

## 5. Corolário (os motores juntos)

As mudanças de estrutura da v0.54 são decididas por dois motores com α = 0,05 cada: o principal e o das remoções
disparadas. A auditoria da porta da M2 tem um terceiro motor (α = 0,01), que não muda a estrutura nem a saída. Com R o
total de aceitações estruturais e Rₘ as de cada motor, R ≥ Rₘ. Então

  E[(V¹ + V²)/max(R, 1)] ≤ E[V¹/max(R¹, 1)] + E[V²/max(R², 1)] ≤ 2α = 0,10.

**[DEDUÇÃO]** O limite conjunto das mudanças estruturais é 2α. A especificação v0.54 diz que as garantias são
separadas e não afirma um limite conjunto. A próxima revisão do texto deve dizer "≤ 2α no conjunto".

## 6. Observação sobre a hipótese persistente de remoção periódica

**[FATO]** No motor principal, a hipótese de remoção periódica de uma unidade, ("out", u), é persistente e só é
retirada quando é aceita (`consume` remove apenas a hipótese do experimento aceito). Uma remoção **disparada** aceita
retira a hipótese disparada, e não a periódica. Se a unidade for readicionada depois, o próximo teste periódico de
remoção reabre a **mesma** hipótese ("out", u), com a evidência acumulada na vida anterior da unidade.

**[DEDUÇÃO]** Isso não fere os Teoremas 1 e 2: a hipótese continua uma só, com o seu índice e o seu nível, e a nula
fraca dela é a média sobre todos os seus passos testados. Mas a pergunta que ela responde mistura as duas vidas da
unidade. É o mesmo mecanismo do "a evidência de antes pesa para sempre" que motivou a M4, agora entre vidas. O efeito
prático não foi medido. Registrado para a F3.

## 7. O que esta nota não estabelece

- **Nenhuma garantia sobre a nula estrutural.** A ponte é o erro de estimação da referência: Corolário 1 da nota de
  desajuste, condição M ≲ 4ε.
- **Nenhuma afirmação sobre poder.**
- **Nada sobre a M1 nem sobre a saída:** a M1 seleciona entradas sem teste.
- A prova tem um único autor; falta a conferência independente.

**Referências:**
- Choe & Ramdas (2024), Operations Research, DOI 10.1287/opre.2021.0792;
- Xu & Ramdas (2024), PMLR 238;
- Javanmard & Montanari (2018), Annals of Statistics;
- Howard, Ramdas, McAuliffe & Sekhon (2021), Annals of Statistics, e Fan, Grama & Liu (2015), Electronic Journal of
  Probability — citadas de memória, a conferir;
- Ville (1939).
