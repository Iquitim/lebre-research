# 06 — Literatura e originalidade

**Método.** Este documento parte de três revisões anteriores do projeto: PRA-04 (`experiments/PRA-04-V052`), PRA-05
(`LEBRE-V0.52-EXT-02/PRA_05_REPORT.md`, 47 consultas) e PRA-11 (`LEBRE-V0.54-DESIGN-NOTE-01/PRA_11_RELATORIO.md`). A
elas somou, em 16/10/2026, 6 buscas novas para as lacunas de F3 e F4.

**Limitações:**
- um mecanismo de busca geral, consultas em inglês;
- leitura por título, resumo e páginas de registro, sem texto integral;
- sem dupla triagem; trabalhos de 2026 podem não estar indexados.

**Não é uma revisão sistemática.** Nenhuma afirmação de diferença deve ir para um artigo sem a leitura do texto integral
dos trabalhos marcados como próximos.

**Coluna "conferido":**
- **S:** registro encontrado nesta sessão;
- **R:** conferido numa revisão anterior do projeto;
- **C:** citado de conhecimento prévio, não conferido aqui. Confira antes de usar.

## 1. Referências por tema

| Tema | Referência | Status | Conferido |
|---|---|---|---|
| Comparação sequencial de previsores, nula fraca | Choe & Ramdas, *Comparing Sequential Forecasters*, Operations Research 72(4), 2024, DOI 10.1287/opre.2021.0792 | revisado por pares | S |
| e-LOND, FDR online com e-valores | Xu & Ramdas, *Online multiple testing with e-values*, PMLR 238 (AISTATS 2024) | revisado por pares | S |
| LOND | Javanmard & Montanari, Annals of Statistics, 2018 | revisado por pares | R (citado na especificação) |
| Teste fechado online com e-valores | Fischer & Ramdas, arXiv 2407.15733 | preprint | R (autores), S (registro) |
| Causalidade de Granger | Granger, Econometrica, 1969 | revisado por pares | C |
| e-closure online, mais poder que e-LOND | arXiv 2603.24792 | preprint | S |
| e-BH online | arXiv 2407.20683 | preprint | S |
| Hipóteses persistentes com FDR | de Heide, arXiv 2608.09927 | preprint | R |
| α-investing sempre válido, duplamente sequencial | Yao, Gang & Sun, arXiv 2512.12244 | preprint | R |
| Sequências de confiança, lema de Fan | Howard, Ramdas, McAuliffe & Sekhon, Annals of Statistics, 2021 | revisado por pares | C |
| Comparar métodos, não modelos | Giacomini & White, Econometrica, 2006 | revisado por pares | R |
| Comparação aninhada com estimação | Clark & West, Journal of Econometrics, 2007 | revisado por pares | R |
| Monitores sempre válidos que disparam por falha de premissa | Han & Qu, arXiv 2608.30502 | preprint | R |
| Viés do incumbente na promoção de desafiantes | Fernández-Barrios et al., arXiv 2609.04388 | preprint | R |
| e-process de melhora em árvores online | Amoukou, Mishra & Veloso, arXiv 2605.31239 | preprint | R |
| Correção preditiva pré-especificada, evidência sempre válida | Choi, arXiv 2608.08174 | preprint | R |
| Granger distribucional com teste sequencial | Jha, arXiv 2606.22230 | preprint | R, S |
| Granger por teste sequencial (sem validade a qualquer tempo) | arXiv 2303.17916 | preprint | S |
| Modelos lineares sempre válidos (t e F sequenciais) | arXiv 2210.08589 | preprint | S |
| Desajuste do NLMS/LMS | literatura clássica de filtragem adaptativa (por exemplo, Haykin, *Adaptive Filter Theory*; Sayed, *Fundamentals of Adaptive Filtering*) | livros | C |
| Combinação convexa de filtros adaptativos | Arenas-García et al., IEEE Trans. Signal Processing, 2006 | revisado por pares | R |
| Deriva recorrente de conceito, reúso de modelos | Suárez-Cetrulo, Quintana & Cervantes, Expert Systems with Applications 213:118934, 2023 | revisado por pares | S |
| Deriva recorrente (revisão) | IJCAI 2024, trilha de revisões | revisado por pares | S |
| Seleção por fluxo com α-investing | Zhou, Foster, Stine & Ungar, JMLR 7:1861–1885, 2006 | revisado por pares | S |
| Seleção online de atributos | Wang, Zhao, Hoi & Jin, IEEE TKDE 26(3):698–710, 2014 | revisado por pares | S |
| Seleção com atributos em fluxo (OSFS, SAOLA) | Wu et al., 2013; Yu et al., ACM TKDD | revisados por pares | S (registros) |
| Identificação esparsa recursiva de ARMAX | arXiv 2505.00323 | preprint | R |
| Regressão espúria; monitoramento de cointegração | Granger & Newbold, 1974; Trapani & Whitehouse, 2020 | revisados por pares | C; R |

## 2. As cinco perguntas, por fronteira

### F1 — validade com NLMS adaptativo

1. **Já existe?** Sim, a base. A validade de e-processes com previsores aprendidos online é exatamente o cenário de Choe &
   Ramdas (previsores arbitrários, previsíveis). O lema de centragem previsível é o de Howard et al. A forma explícita
   para um e-process que decide *estrutura* contra uma referência NLMS (Proposição 1 da nota formal) não foi encontrada.
   O tema geral (Giacomini & White; viés do incumbente) é conhecido.
2. **Diferença na LEBRE:** a ligação quantitativa entre o desajuste do NLMS e a margem (M ≲ 4ε), e o diagnóstico de que
   a falha é de interpretação, e não de validade.
3. **Tipo de contribuição:** observação teórica modesta, mais verificação empírica.
4. **Baseline científico:** um e-process com referência fixa (sem adaptação) ou com referência RLS de memória longa.
5. **Falsificação:** encontrar a Proposição 1, ou o critério M ≲ 4ε, publicados. Ou mostrar uma série nula em que um
   desafiante previsível viole a validade (o que contradiria o §2 de `02`).

### F2 — cascata memória–estrutura

1. **Já existe?** A ideia de modelar só a informação incremental além do próprio passado é Granger (1969). A
   aprendizagem sobre resíduos é clássica: boosting, modelos em cascata, ARIMAX com regressão sobre inovações. Testes
   sequenciais de Granger existem (Jha 2026; arXiv 2303.17916), mas sem a integração com seleção por unidade e custo fixo.
2. **Diferença:** fazer o teste sempre válido de cada unidade perguntar "além da memória", num previsor online de custo
   fixo, e mostrar que isso elimina a aceitação espúria em séries integradas.
3. **Tipo:** integração, mais um resultado empírico sobre aceitações espúrias.
4. **Baseline:** v0.54 (teste contra s); teste de Granger em janela com correção de multiplicidade; diferenciar o alvo
   antes de modelar.
5. **Falsificação:** um método online publicado que já teste inclusão de variáveis contra a inovação de um modelo do
   próprio passado com garantia a qualquer tempo. Ou a cascata não reduzir as aceitações espúrias.

### F3 — memória de regimes e FDR com estado

1. **Já existe?** O reúso de modelos em deriva recorrente é uma linha estabelecida (Suárez-Cetrulo et al. 2023; IJCAI
   2024). A reutilização de evidência com controle de FDR em hipóteses persistentes é teoria ativa (de Heide 2026; Yao,
   Gang & Sun 2025; e-closure online 2026). As buscas desta sessão **não** encontraram nada sobre warm start de
   hipóteses ou reciclagem de evidência entre hipóteses recorrentes.
2. **Diferença:** separar formalmente o reúso computacional (parâmetros iniciais do desafiante, livre para a validade) do
   reúso de evidência (muda a nula), num previsor com remoção testada.
3. **Tipo:** algorítmica e de integração. Uma regra de riqueza nova seria teórica e exigiria prova própria.
4. **Baseline:** v0.54 (descarte); reúso de modelos de deriva recorrente sem teste (o que a literatura de fluxo faz).
5. **Falsificação:** o warm start não reduzir a redescoberta (se a evidência dominar o atraso). Ou um trabalho de deriva
   recorrente que já use evidência sempre válida para revalidar o modelo reaproveitado.

### F4 — descoberta em alta dimensão

1. **Já existe?** Seleção online com controle tipo FDR existe desde Zhou et al. (2006, α-investing por fluxo). Seleção
   online com orçamento de atributos existe (Wang et al. 2014; OSFS; SAOLA). Identificação esparsa recursiva com garantia
   assintótica também (arXiv 2505.00323).
2. **Diferença:** garantia a qualquer tempo por unidade (bloco de atrasos), com remoção testada, sob custo por passo
   declarado.
3. **Tipo:** empírica (mapa de desempenho), mais integração.
4. **Baseline:** α-investing por fluxo e seleção online com truncamento (§4 de `05`).
5. **Falsificação:** α-investing ou "tudo ligado" igualar ou superar a LEBRE em todas as células com IC. Isso já
   aconteceu na dimensão baixa contra "tudo ligado".

## 3. Originalidade, em resumo

Nenhuma das quatro fronteiras tem um componente que possa ser declarado original com a evidência atual. A contribuição
possível de cada uma é de **integração**, mais uma **observação teórica modesta** (F1) e **resultados empíricos**:

- F2: aceitações espúrias em séries integradas, com e sem âncora na memória;
- F3: o custo da falta de memória de regimes;
- F4: o mapa por dimensão.

Isso é coerente com as revisões anteriores do projeto.
