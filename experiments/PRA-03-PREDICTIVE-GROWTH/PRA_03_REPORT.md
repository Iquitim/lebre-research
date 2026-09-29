# PRA-03 — Prior art da reformulação "crescimento de modelo com garantia de melhora preditiva"

**Data:** 25/09/2026 · **Objetivo do projeto:** contribuição de pesquisa.
**Reformulação avaliada:**
- a promoção de um átomo estrutural passa a ser um teste sempre válido de que "modelo atual + átomo" prevê melhor que "modelo atual", válido sob má especificação;
- as promoções ficam sob controle de erro ao longo de todo o fluxo (testes múltiplos online com e-valores);
- tudo dentro de um orçamento fixo de custo.

**Limite:** leitura de resumos; 8 buscas; um mecanismo de busca.

## 1. O que já existe (a reformulação não é nova nas partes)

| Peça | Precedente | Situação |
|---|---|---|
| Teste sempre válido de "um previsor é melhor que outro, em média", sem supor distribuição, para previsores sequenciais quaisquer | Choe & Ramdas, *Comparing sequential forecasters*, Operations Research (2024), arXiv 2110.00115; pacote R `seqcomp` | **Existe.** Vale para previsores previsíveis quaisquer, inclusive os aprendidos online |
| E-valores para diferenças de score entre previsões, com parada opcional | Henzi & Ziegel, Biometrika 109 (2022) | **Existe** |
| Evidência sempre válida de que uma correção pré-especificada melhora o score logarítmico, válida para parte das distribuições mal especificadas | Choi, arXiv 2608.08174 (ago/2026) | **Existe** para correções fixas e pré-especificadas |
| Eliminação sequencial de modelos com cobertura uniforme no tempo | Arnold, Gavrilopoulos, Schulz & Ziegel, *Sequential model confidence sets*, arXiv 2404.18678 (2024) | **Existe** para um conjunto dado de modelos |
| Seleção de modelos de previsão em tempo real por e-valores | Backhaus et al., arXiv 2410.17800 (2024), demanda elétrica | **Existe** (aplicado) |
| FDR online com e-valores sob dependência arbitrária | e-LOND (Xu & Ramdas, AISTATS 2024); e-GAI (ICML 2025); SAVA (2025); *carefree* (Tavyrikov et al., EJS 2026); *dynamic e-closure* (de Heide, 2026) | **Existe** |
| Combinar e-processes de filtrações diferentes | Choe & Ramdas, *Combining evidence across filtrations*, JRSS-B (2026) | **Existe** |
| Seleção sequencial offline com validade (caminho de modelos) | Taylor et al. 2014 (forward stepwise); Fithian et al. 2015 (selective sequential model selection) | **Existe**, offline |

## 2. Lacuna que não encontramos preenchida

Nenhum trabalho encontrado reúne:
1. **candidatos gerados de forma adaptativa** a partir de um dicionário estrutural (atrasos, estados latentes), cada um com um previsor-sombra **aprendido online**;
2. uma **referência que evolui**: cada promoção redefine o modelo contra o qual os testes seguintes são feitos (sequência aninhada de nulas que dependem do caminho);
3. **controle ao longo da vida** da taxa de "mudanças estruturais que não melhoram a previsão", num fluxo de candidatos que podem ser retestados;
4. **remoção e substituição na mesma moeda** (evidência de piora preditiva);
5. **orçamento fixo de custo** por passo, com a vazão da busca como parte do problema.

## 3. Avaliação honesta

- **Risco principal:** um revisor pode ler a proposta como composição direta de resultados conhecidos (Choe & Ramdas + e-LOND). Para ser contribuição, a proposta precisa de pelo menos um resultado **não trivial**. Candidatos:
  - (a) a **definição e o controle de uma taxa de erro para crescimento com referência que evolui**. Não é imediato: a nula de cada candidato depende de promoções anteriores, que são aleatórias;
  - (b) uma **ligação entre as mudanças aceitas e uma garantia de desempenho** (por exemplo, cada mudança aceita reduz o score esperado, com implicação sobre o arrependimento acumulado);
  - (c) uma análise de **poder e latência sob orçamento** (vazão da busca × vagas de teste), que é justamente o gargalo observado na v0.51;
  - (d) **evidência empírica em dados reais guiados por entradas**, contra comparadores fortes.
- **O que muda na semântica:** abandona-se "descobrir a estrutura verdadeira" em favor de "toda mudança estrutural tem evidência sempre válida de melhora preditiva". É mais estreito, mas verificável e honesto (resolve os problemas E1 e E5 da errata).

## 4. Próximos passos recomendados

1. **Ler na íntegra** Choe & Ramdas (2024), Choi (2026), Arnold et al. (2024) e e-LOND. Confirmar que a lacuna do §2 é real e ver o que cada um já garante.
2. **Escrever uma nota de desenho** (sem código): pergunta de pesquisa, afirmação-alvo, definições formais (nula por candidato relativa ao modelo no início do teste, taxa de erro ao longo da vida, filtração) e esboço do procedimento e da prova.
3. **Obter os dados reais guiados por entradas** antes de implementar.

## 5. Leitura integral dos quatro trabalhos centrais (25/09/2026)

Textos completos do arXiv, com o texto extraído dos PDFs; lidas as seções de formulação, hipóteses, teoremas principais e discussão.

| Trabalho | O que garante, exatamente | Premissas-chave | Limites relevantes para nós |
|---|---|---|---|
| **Choe & Ramdas** (OR 2024; arXiv v6, 61 p.) | CS e e-process (Teor. 2–3) para a **nula fraca** H₀ʷ(p,q): Δₜ = (1/t)Σ E₍ᵢ₋₁₎[S(pᵢ,yᵢ) − S(qᵢ,yᵢ)] ≤ 0 para todo t, isto é, "p não é melhor que q, **em média**, até t" | Previsores **arbitrários e previsíveis** em relação à filtração do jogo (podem ser aprendidos online); nenhuma premissa de estacionariedade; **scores limitados** nos teoremas principais (sem limite: CS assintótica, §C) | Só **dois** previsores (comparações par a par, sem correção de multiplicidade); conclusões **descritivas** ("foi melhor até τ", §6), não preditivas; nenhum crescimento de modelo. **Útil:** a §F.1 valida a comparação em **subsequências previsíveis**, o que dá respaldo direto aos portões (silêncio, quarentena, dormência). |
| **Choi** (arXiv 2608.08174, 49 p.) | Teorema 1: o produto das razões de verossimilhança preditiva "corrigida/fonte" é e-process sob **H₀ᵖʳᵉᵈ: a fonte é a distribuição preditiva correta**; §3.4: a validade estende-se a um **semiespaço direcional** de alvos mal especificados | Correção fixa antes dos dados; a Prop. 5 permite **correções previsíveis** (aprendidas); preditivas probabilísticas | A nula é "fonte correta", **a mesma fragilidade do nosso E1**, só parcialmente mitigada pelo semiespaço. Vários candidatos: só **mistura ou painel fixo e finito** (Prop. 6), sem candidatos chegando nem atualização da fonte após confirmação. |
| **Arnold, Gavrilopoulos, Schulz & Ziegel** (SMCS, arXiv 2404.18678v, jan/2026) | Conjuntos sequenciais que contêm os modelos (uniforme ou fracamente) superiores, com cobertura uniforme no tempo; e-processes par a par + ajuste de testes múltiplos (fechamento) | Conjunto **fixo** M₀ de m modelos; diferenças de perda limitadas (nula fraca) ou sub-exponenciais (forte) | Nenhum modelo **entra** depois; eliminação, não crescimento; custo alto do fechamento completo (os autores evitam a versão cara). |
| **Xu & Ramdas** (e-LOND, AISTATS 2024) | FDR ≤ α em todo t para um **fluxo de hipóteses**, cada uma decidida uma vez com um e-valor (por exemplo, um e-process parado no seu próprio τ), níveis αₜ = α·γₜ·(\|Rₜ₋₁\|+1), sob **dependência arbitrária** (Teor. 1) | Cada Eₜ deve ser e-valor para sua Hₜ | As hipóteses são fixas quanto ao conteúdo. Não trata **nulas definidas a partir das descobertas anteriores** (no nosso caso, "o candidato não melhora o modelo **atual**", e o modelo atual é resultado das rejeições passadas). Decisões irrevogáveis: não prevê remover uma descoberta. |

### Conclusão da leitura integral

1. **O teste de promoção certo existe:** a e-process de Choe & Ramdas para a nula fraca de diferença média de score entre "modelo atual" e "modelo atual + átomo", ambos aprendidos online, é válida **sem** exigir que o modelo atual esteja correto. Isso resolve E1 de forma mais limpa que Choi, cuja nula é "fonte correta". **Custo a pagar:** score limitado (erro quadrático recortado ou score normalizado) e uma conclusão **descritiva** ("melhorou até agora").
2. **O controle ao longo do fluxo existe para hipóteses fixas:** e-LOND e o arcabouço duplamente sequencial (Robertson et al., 2023; de Heide, 2026).
3. **Lacuna confirmada, agora mais precisa:**
   - (a) nulas **dependentes do caminho**: cada hipótese é definida em relação a um modelo de referência que é função das decisões anteriores;
   - (b) **decisões revogáveis**: remoção e substituição de descobertas, com a taxa de erro das remoções também controlada;
   - (c) a tensão entre a garantia **descritiva** (melhorou no passado) e o uso **preditivo** da decisão (manter o termo no futuro);
   - (d) tudo sob **custo fixo por passo**.

   Nenhum dos quatro trabalhos trata (a)–(d), e nenhum trata crescimento de modelo.
4. **Implicação para a contribuição:** o núcleo teórico candidato é **definir uma taxa de erro para crescimento/poda online com referência que muda e provar que um procedimento de custo constante a controla**, reaproveitando Choe & Ramdas (teste) e e-LOND/e-closure (multiplicidade). Um resultado desse tipo não é aplicação direta dos quatro trabalhos. Isso ainda precisa ser confirmado na nota de desenho, inclusive tentando encontrar um contraexemplo em que a composição ingênua falha.

## Referências

- Choe & Ramdas — [arXiv 2110.00115](https://arxiv.org/abs/2110.00115) · [Operations Research](https://doi.org/10.1287/opre.2021.0792) · [seqcomp](https://rdrr.io/cran/seqcomp/f/README.md)
- Henzi & Ziegel — [arXiv 2103.08402](https://arxiv.org/abs/2103.08402) · [Biometrika](https://academic.oup.com/biomet/article/109/3/647/6375942)
- Choi — [arXiv 2608.08174](https://arxiv.org/abs/2608.08174)
- Arnold et al. — [arXiv 2404.18678](https://arxiv.org/abs/2404.18678)
- Backhaus et al. — [arXiv 2410.17800](https://arxiv.org/abs/2410.17800)
- Xu & Ramdas (e-LOND) — [AISTATS 2024](https://proceedings.mlr.press/v238/xu24a.html) · e-GAI — [arXiv 2506.01452](https://arxiv.org/pdf/2506.01452)
- Choe & Ramdas — Combining evidence across filtrations — [arXiv 2402.09698](https://arxiv.org/abs/2402.09698) · [JRSS-B](https://academic.oup.com/jrsssb/advance-article-abstract/doi/10.1093/jrsssb/qkag058/8627076)
- Taylor et al. — [arXiv 1405.3920](https://arxiv.org/pdf/1405.3920) · Fithian et al. — [arXiv 1512.02565](https://arxiv.org/pdf/1512.02565)
