# 02 — F1: validade sequencial dos e-processes com NLMS adaptativo

**Questão.** A adaptação contínua de um NLMS de passo fixo compromete, em alguma condição, a validade dos e-processes da
LEBRE?

**Resposta curta.**
- **[DEDUÇÃO]** Não compromete a **validade** do e-process para a nula que ele de fato testa.
- **[RESULTADO]** Compromete a **interpretação estrutural** dessa nula. Isso já está demonstrado em condições
  identificadas.
- Não há falha de validade a corrigir. Há uma falha de interpretação, e ela já tem um caminho de correção na F2.

Rótulos como em `01_ARCHITECTURE_BASELINE.md`.

## 1. O que está implementado

**[FATO] NLMS** (`_core.py`, `observe`): com res = y − s, xb = [1, xₜ] e os blocos bᵤ das unidades ativas,

  base ← base + μ·res·xb / (‖xb‖² + Σᵤ‖bᵤ‖² + 10⁻⁶),  wᵤ ← wᵤ + μ·res·bᵤ / (mesmo denominador),  μ = 0,05.

A memória M usa a mesma forma, com pisos relativos no denominador (`_memory.py`).

**[FATO] Incremento do teste** de uma hipótese k, num passo testado:

  dₜ = min((yₜ − sₜ)²/Bₜ², 1) − min((yₜ − gₖ,ₜ)²/Bₜ², 1) − εₖ,

com sₜ a previsão estrutural vigente, gₖ,ₜ = sₜ + aₖ,ₜ − rₖ,ₜ a do desafiante, Bₜ = 2·max(σ̂ᵣ, 0,1·desvio do alvo) e
ε = 0,002 (adição, troca, divisão) ou −0,002 (remoção). Os passos testados excluem os 250 primeiros de cada desafiante de
adição e os passos fora do contrato de entrada ou em quarentena.

**[FATO] e-process** (`_engine.py`, `Hypothesis`): c = 1 + max(ε, 0); grade de 8 valores λ = 0,9·2⁻ʲ/c;
ψ(λ) = (−log(1 − cλ) − cλ)/c²; Sₙ = Σ dᵢ; Vₙ = Σ (dᵢ − γᵢ)², com γᵢ = max(−c, min(0, média dos d anteriores));
log e = log da média sobre λ de exp(λSₙ − ψ(λ)Vₙ). A hipótese é **persistente**: acumula todos os episódios de teste da
mesma mudança até ser aceita (exceto a remoção disparada da M4, que cria uma hipótese nova por episódio).

**[FATO] Previsibilidade.** sₜ, gₖ,ₜ e Bₜ são calculados em `predict`, antes de yₜ. O NLMS de S, o RLS do desafiante e
σ̂ᵣ só são atualizados depois de dₜ. A escolha dos passos testados (aquecimento, quarentena, abertura e fechamento de
episódios) depende só do passado.

## 2. Validade para a nula testada

**Nula testada (fraca, de comparação de métodos):** para todo n, Σᵢ≤ₙ μᵢ ≤ 0, em que μᵢ = E[dᵢ | ℱᵢ₋₁] e a soma corre
sobre os passos testados. É a nula fraca de Choe & Ramdas (*Comparing Sequential Forecasters*, Operations Research, 2024,
DOI 10.1287/opre.2021.0792).

**[DEDUÇÃO] Argumento.** Fixe λ ∈ [0, 1/c).

1. **Intervalo.** As perdas recortadas estão em [0, 1]. Então dᵢ ≥ −1 − max(ε, 0) = −c, e como γᵢ ≤ 0,
   yᵢ := dᵢ − γᵢ ≥ −c. O comentário do código registra exatamente essa condição.
2. **Lema de Fan** (forma de Howard, Ramdas, McAuliffe & Sekhon, 2021): para y ≥ −c,
   exp(λy − ψ(λ)y²) ≤ 1 + λy.
3. **Supermartingala sob qualquer distribuição.** Com a = λ(μᵢ − γᵢ),
   E[exp(λ(dᵢ − μᵢ) − ψ yᵢ²) | ℱᵢ₋₁] ≤ e^{λ(γᵢ − μᵢ)}·(1 + λ(μᵢ − γᵢ)) = e^{−a}(1 + a) ≤ 1.
   Logo Mₙ = exp(λ Σ(dᵢ − μᵢ) − ψVₙ) é supermartingala não negativa, **sob qualquer distribuição** dos dados, porque γᵢ
   é previsível.
4. **Nula fraca.** O processo do código é exp(λSₙ − ψVₙ) = exp(λ Σ μᵢ)·Mₙ ≤ Mₙ sempre que Σμᵢ ≤ 0. Portanto ele é um
   e-process (limitado por uma supermartingala de valor inicial 1) sob a nula fraca.
5. **Mistura em λ.** Uma média de processos, cada um limitado pela sua supermartingala, é limitada pela média dessas
   supermartingalas, que é supermartingala. A desigualdade de Ville dá P(supₙ eₙ ≥ 1/α) ≤ α.
6. **Persistência e passos pulados.** Os passos não testados são escolhidos de forma previsível e não entram no produto.
   Isso equivale a um fator 1 nesses passos e não altera a supermartingala. A revisão a cada 10 passos só observa o
   processo num subconjunto dos tempos.

**Consequência:** o NLMS pode ter qualquer passo, qualquer desajuste e qualquer dependência temporal. Nada disso entra
no argumento, porque tudo o que ele produz é ℱᵢ₋₁-mensurável. Ruído autocorrelacionado, heterocedástico ou com mudança
de regime também não entra: o argumento não supõe estacionariedade nem permutabilidade. **Não é preciso Monte Carlo para
a validade.** Simulação nenhuma a provaria, e esta dedução a estabelece (sujeita à verificação do §5).

**Hipótese H1.1 — SUPPORTED (dedução),** com a ressalva de que a prova acima precisa ser escrita por extenso e conferida
por um leitor independente. Uma prova curta exige isso antes de ser citada como garantia.

## 3. Controle de mudanças falsas sobre o fluxo

**[FATO]** O nível da hipótese de índice j (ordem de criação) é αⱼ = min(α·gⱼ·(Rⱼ + 1), 0,5). Aqui gⱼ é função só de j,
com Σgⱼ ≤ 1 (primeiros P = 2(d+2): 1/(2P); depois 0,5·γ₍ⱼ₋P₎), e Rⱼ é o número de mudanças aceitas *quando j foi
criada*. As decisões são assíncronas: j pode ser aceita depois de hipóteses criadas mais tarde.

**[DEDUÇÃO] Argumento (FDR ≤ α por motor, dependência arbitrária).** Seja τⱼ o primeiro cruzamento do limiar, ou o fim.
O valor parado Eⱼ = eⱼ,τⱼ satisfaz E[Eⱼ·1{nula j vale até τⱼ}] ≤ 1, pelo §2 com parada opcional, e vale
1{j aceita} ≤ αⱼ·Eⱼ.

Se j é aceita, o total final de aceitações do motor satisfaz R ≥ Rⱼ + 1, porque as aceitações só aumentam e j é uma
delas. Então

  E[Σⱼ nulas 1{j aceita}/max(R, 1)] ≤ Σⱼ E[αⱼEⱼ/(Rⱼ + 1)] ≤ α Σⱼ gⱼ E[Eⱼ·1{nula}] ≤ α.

O argumento segue o de e-LOND (Xu & Ramdas, AISTATS 2024) e não usa independência. O teto 0,5 só reduz os níveis.

**[DEDUÇÃO] Conjunto dos motores.** A remoção disparada (M4) tem motor e orçamento próprios (α = 0,05). Repetindo o
argumento com o R de cada motor e usando R_total ≥ R_motor, o FDR conjunto das mudanças de estrutura é ≤ 2α = 0,10. A
especificação v0.54 diz que as garantias são separadas, sem afirmar um limite conjunto. Uma frase explícita com 2α
evitaria uma leitura otimista.

**Observação sobre a nula aleatória.** A condição "a hipótese j é nula" depende da trajetória: ela é definida pelas
médias condicionais ao longo dos episódios realizados. O argumento acima a trata como o evento em que a nula fraca vale
até τⱼ, e o limite do §2 vale nesse evento. Esse ponto precisa constar da prova escrita.

## 4. Onde a garantia não diz o que se quer: a nula estrutural

**Nula estrutural:** "os atributos da unidade não acrescentam informação sobre yₜ". **[RESULTADO]** A nota formal
`experiments/LEBRE-V0.52-EXT-01/MISADJUSTMENT_NOTE.md` mostra:

- **Identidade:** com ηₜ = f\*ₜ − sₜ o erro de estimação previsível da referência,
  E[Δₜ | ℱₜ₋₁] = (2gₜηₜ − gₜ²)/Bₜ².
- **Consequência:** um desafiante que se correlacione com ηₜ tem melhora esperada positiva **mesmo sob a nula
  estrutural**.
- **Garantia exata para a nula estrutural:** exige (1/n)Σηᵢ²/Bᵢ² ≤ ε, o que para o NLMS dá desajuste M ≲ 4ε, ou
  seja, μ ≲ 0,016. Com μ = 0,05, a LEBRE está no **regime prático**: o desvio fica abaixo do detectável no horizonte, e
  isso não é garantia.

**Condições em que a interpretação estrutural já falhou (H1.2 — SUPPORTED, já demonstrada):**

| Condição | Mecanismo (η previsível e projetável) | Evidência |
|---|---|---|
| Passo grande (μ = 0,1) | desajuste maior que a margem | 10/40 séries nulas com aceitação falsa; 0/40 com μ = 0,05 (EXT-01) |
| Alvo integrado (nível) | s não tem raiz unitária; o componente que ela não acompanha é previsível e qualquer entrada que passeia o projeta | entradas externas aceitas em 5 de 11 passeios aleatórios independentes (exploração) e em 4 de 4 séries de C03 (`LEBRE-V0.54-DESIGN-NOTE-01/M3_DIAGNOSTICO.md`) |
| Substituta correlacionada antes da verdadeira | enquanto a verdadeira falta, a substituta projeta η | até 20% das execuções numa célula, FDR 0,090 (`LEBRE-V0.52-EXT-02/FDR_SIM_REPORT.md`) |

**Condições testadas sem falha** com μ = 0,05: nulos globais, nulo exógeno com alvo AR, nulo heterocedástico e nulo com
quebra de variância (0 de 400 execuções, EXT-02); 100 nulos da auditoria v0.54 (0 aceitações, `LEBRE-V0.54-AUDIT-01`).
Isso **não é garantia universal**: com 400 execuções, o IC 95% da fração vai até 0,009.

**Leitura unificada.** O problema M3, adiado para a v0.55, é um caso desta fronteira: a interpretação estrutural falha
porque a referência dos testes (s) tem erro previsível em séries integradas. A correção proposta para a M3, ancorar a
estrutura na memória (F2), é a terceira alavanca da nota formal: testar contra uma referência com η menor.

## 5. Hipótese H1.3 e o que falta

**H1.3 (uma construção alternativa preserva a validade e melhora o poder): INCONCLUSIVE.** Candidatas, nenhuma
testada:

1. **Referência ancorada na memória** (F2). Reduz η em séries integradas. É a mais bem motivada, mas muda o núcleo.
2. **Referência lenta separada** só para os testes: RLS de memória longa ou μ pequeno, mantendo μ = 0,05 na previsão
   viva. Isso preserva a precisão e aproxima M ≲ 4ε. Custa um segundo conjunto de pesos.
3. **Margem ε maior.** É a segunda alavanca da nota formal e custa poder. Não foi medida.
4. **Procedimentos de FDR mais poderosos** (e-closure online, arXiv 2603.24792; de Heide 2026). Mexem no orçamento,
   não no e-process. Pertencem à F3 (H3.4).

**Trabalho que falta para fechar a F1 (nenhum muda a arquitetura):**

| Item | Tipo | Critério de conclusão |
|---|---|---|
| F1-a: prova escrita do §2 (centragem γ, nula fraca, passos pulados, mistura) | formal | conferida por um leitor independente; condições do lema citadas da fonte original |
| F1-b: prova escrita do §3 (e-LOND assíncrono, nula aleatória, dois motores → 2α) | formal | idem; frase de 2α acrescentada na próxima revisão da especificação |
| F1-c: calibração da nula estrutural sob condições ainda não cobertas: alta dimensão (F4) e mudança gradual de regime | experimental, compartilhado com F2/F4 | ver o protocolo do §6 |

## 6. Protocolo experimental mínimo (F1-c), a pré-registrar antes de rodar

- **Nulos estruturais:** alvo AR(1) ou passeio aleatório, ruído gaussiano, t₃ ou GARCH(1,1); entradas independentes
  AR(ρ), ρ ∈ {0,5; 0,95}; d ∈ {4, 16, 64}; mudança gradual da variância ou do coeficiente AR do alvo no meio da série.
- **Alternativas:** uma entrada verdadeira com atraso 3, efeito de 0,1 a 0,4 desvio.
- **Medidas:**
  - fração de execuções com ≥ 1 entrada externa aceita (IC de Clopper-Pearson);
  - D máximo por unidade, pelo oráculo de projeção da nota formal;
  - poder e atraso de detecção nas alternativas.
- **Sementes pareadas** entre a v0.54 e qualquer variante, faixa reservada no roteiro (`08`).
- **Decisão:**
  - a F1 só gera mudança de arquitetura se alguma célula nula tiver limite inferior do IC acima de 0,05 com μ = 0,05;
  - um resultado nulo (nenhuma falha) é registrado como resultado, não como prova.

## 7. Decisão

| Hipótese | Classe | Recomendação |
|---|---|---|
| H1.1 validade para a nula testada | **SUPPORTED** (dedução) | REQUIRE_FORMAL_PROOF (escrever e conferir; não muda código) |
| H1.2 condições de falha (interpretação estrutural) | **SUPPORTED** (já demonstrada) | REJECT como fronteira nova: já está documentada; a correção vai pela F2 |
| H1.3 construção alternativa com mais poder | **INCONCLUSIVE** | DEFER; a candidata 1 entra na F2 e a 4 na F3 |

**Uma correção da validade do e-process não se justifica:** não há falha demonstrável, e o argumento do §2 cobre o NLMS
adaptativo. O que se justifica é a correção de texto (2α) e a prova escrita.
