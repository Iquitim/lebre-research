# LEBRE v0.52 — Nota de desenho 01: crescimento de modelo online com mudanças estruturais auditáveis

**Data:** 25/09/2026 · **Status:** rascunho de pesquisa. **Não há código, pré-registro nem resultados.**
**Base:** v0.51 congelada (`LEBRE-V0.51-FREEZE-01`), Errata 01, PRA-02 e PRA-03 (§5, leitura integral).
**Objetivo do projeto:** contribuição científica (ver memória do projeto).

---

## 1. Pergunta de pesquisa

> Um previsor online de custo constante por passo pode alterar a própria estrutura (acrescentar, remover ou trocar termos como atrasos e estados latentes) de modo que **(i)** toda mudança tenha evidência sempre válida, sem premissas distribucionais, de melhora preditiva, com a fração de mudanças sem essa evidência controlada ao longo do fluxo inteiro, e **(ii)** quando o modelo é bem especificado, a estrutura convirja para a verdadeira com latência limitada em função do orçamento de busca?

O item (i) é uma garantia de **segurança** que vale sempre. O item (ii) é uma garantia de **eficácia** que vale sob premissas. A contribuição pretendida está em ter as duas no mesmo procedimento, a custo de microcontrolador.

## 2. O que muda em relação à v0.51 (e por quê)

| v0.51 | Proposta | Motivo |
|---|---|---|
| Promoção por correlação resíduo × regressor (martingale de mistura) | Promoção por **comparação sequencial de previsores**: "modelo vigente" contra "modelo vigente + mudança" (Choe & Ramdas, 2024) | A garantia da v0.51 exige que o resto do modelo esteja correto (Errata E1); a comparação não exige |
| Limiar α/p por episódio | **Controle online de multiplicidade** sobre o fluxo de mudanças (tipo e-LOND, assíncrono) | O erro acumulado da v0.51 não é limitado (E5) |
| Remoção por CUSUM com aluguel (sem garantia) | Remoção como **mudança testada na mesma moeda** (o modelo sem o termo não é pior além de uma margem) | Unifica o critério; a remoção passa a ter garantia |
| Latente único; o polo errado trava (B3) | **Troca** (a → c) como mudança testável | O polo certo pode vencer o errado por comparação |
| Triagem + vagas com futilidade | Mantém-se; entra na teoria como **orçamento de busca** | A latência observada vem da busca (H7) |

**O que não muda:** a memória M, o combinador, o dicionário estrutural, os portões previsíveis e o orçamento de custo.

## 3. Formulação

**Filtração.** \(\mathcal G_{t-1}\) contém tudo o que se conhece antes de observar \(y_t\), inclusive \(x_t\). Um previsor é **previsível** se \(\hat y_t\) é \(\mathcal G_{t-1}\)-mensurável.

**Modelo vigente.** \(f_t\) é a previsão do sistema com a estrutura vigente \(A_t\). É previsível, e \(A_t\) resulta das decisões anteriores.

**Mudança proposta k.** Tem um tipo (acrescentar c, remover a, trocar a→c), começa num tempo de parada \(\sigma_k\) e define um **desafiante** previsível
\[
g^{(k)}_t = f_t + \Delta^{(k)}_t ,
\]
- acréscimo: \(\Delta = \theta_{k,t}\,\varphi_{c,t}\), com \(\theta_{k,t}\) aprendido online só sobre o resíduo de \(f\), a custo O(1);
- remoção: \(\Delta = -(\text{contribuição vigente de } a)\);
- troca: soma das duas.

O desafiante compara-se sempre com o **vigente**, mesmo quando o vigente muda durante o episódio.

**Perda limitada.** \(\ell_t(u) = \min\{(y_t-u)^2/B_t^2,\,1\}\), com \(B_t\) previsível (por exemplo, um múltiplo de \(\hat\sigma_{t-1}\)). Respaldo: Choe & Ramdas, §F.2 (limites previsíveis).

**Diferencial com margem.** \(d_{k,t} = \ell_t(f_t) - \ell_t(g^{(k)}_t) - \varepsilon_k\) e \(\delta_{k,t} = \mathbb E[d_{k,t}\mid\mathcal G_{t-1}]\). A margem \(\varepsilon_k \ge 0\) é o "preço" da mudança:
- positiva para acréscimos, exigindo melhora real;
- zero ou negativa para remoções, que só precisam mostrar que o termo não ajuda.

Pense nela como o aluguel da v0.51, agora dentro do teste.

**Passos de teste.** \(I_k\) é o conjunto de passos do episódio k em que os portões estão abertos. É previsível (respaldo: Choe & Ramdas, §F.1).

**Nula da mudança k (fraca, dependente do caminho):**
\[
H_k:\quad \textstyle\sum_{i\in I_k,\,i\le t}\delta_{k,i}\le 0\quad\text{para todo } t .
\]
Isto é: "durante o episódio, o desafiante não melhorou a perda média além da margem". H_k é um **evento aleatório**, porque depende do caminho, dos desafiantes e do vigente realizados.

**E-process.** \(E_{k,t}\) é o e-process sub-exponencial de mistura de Choe & Ramdas (Teorema 3) aplicado a \((d_{k,i})_{i\in I_k}\).

**Decisão.** Aceitar a mudança k quando \(E_{k,t}\ge 1/\alpha_k\). O episódio também termina por futilidade ou por orçamento.

**Níveis.** \(\alpha_k = \alpha\,\gamma_k\,(|R^{\text{dec}}_{<k}|+1)\), com \(\sum_k \gamma_k \le 1\), em que \(R^{\text{dec}}_{<k}\) conta só as mudanças **já decididas** antes de \(\tau_k\). É a versão assíncrona e conservadora do e-LOND; ver §7.

## 4. Garantias pretendidas

### G1 — Segurança (sem premissas distribucionais)

Seja a taxa de mudanças falsas \(\mathrm{FCR}_t = \mathbb E\big[V_t/\max(R_t,1)\big]\), com \(R_t\) = número de mudanças aceitas até t e \(V_t\) = número das aceitas cuja \(H_k\) é verdadeira. **Conjectura G1:** \(\mathrm{FCR}_t\le\alpha\) para todo t.

**Esboço da prova.**
1. No Teorema 3 de Choe & Ramdas, o e-process é dominado, caminho a caminho e no evento em que a nula vale, por uma supermartingale \(L_{k,t}\) que tem essa propriedade sob **qualquer** distribuição. Logo \(\mathbb E[E_{k,\tau}\,\mathbf 1\{H_k\}]\le 1\) para qualquer tempo de parada τ, mesmo com \(H_k\) aleatória.
2. A prova do e-LOND só usa \(\mathbb E[E_k\mathbf 1\{k\text{ nula}\}]\le 1\) e \(\alpha_k\le\alpha\gamma_k(|R_k|)\) quando k é aceita. Com níveis assíncronos conservadores, a desigualdade se mantém.
3. Portanto \(\mathrm{FCR}\le\alpha\sum\gamma_k\le\alpha\).

**Pontos a verificar:**
- o passo 1 com a margem \(\varepsilon_k\) e com os portões;
- o passo 2 com decisões assíncronas e revogáveis. A revogação não é problema: cada remoção é uma nova hipótese, e nenhuma decisão antiga é desfeita estatisticamente.

### G2 — Eficácia sob boa especificação (a parte difícil)

**Premissas:**
- **(A1)** \(y_t=\sum_{a\in A^*}\beta_a\varphi_{a,t}+\eta_t\), com \(A^*\subseteq\mathcal D\), \(|A^*|\le M_{\max}\) e ruído sub-gaussiano independente;
- **(A2)** regressores estacionários, ergódicos e com excitação persistente restrita (autovalor mínimo limitado em subconjuntos de tamanho ≤ \(2M_{\max}\));
- **(A3)** passo de aprendizado adequado para os coeficientes-sombra;
- **(A4)** a busca revisita todo candidato com frequência positiva;
- **(A5)** margens menores que os ganhos verdadeiros: \(\varepsilon<\min_{a\in A^*}\) ganho de perda de \(a\).

**Conjecturas G2:**
- **(G2a)** a fração do tempo em que \(A_t=A^*\) tende a 1 − O(α);
- **(G2b)** o tempo até \(A^*\subseteq A_t\) é limitado em expectativa por um termo de busca, O(\(|\mathcal D|\)/taxa de triagem × vagas), mais um termo de teste, O(\(\log(1/\alpha)/\text{gap}^2\));
- **(G2c)** com a troca como mudança, o sistema sai de polos errados e de atrasos aproximados: depois que o termo verdadeiro entra, o aproximado passa a ter ganho ≤ 0 e é removido.

Isso responde diretamente às três falhas diagnosticadas na v0.51: latente (B3), vários atrasos e latência (H7).

### G3 — Custo

Por passo: O(d + número de vagas + sondas de triagem), sem dependência do comprimento do fluxo. Cada desafiante custa O(1), porque só acrescenta ou subtrai um termo ao vigente.

## 5. Busca por contraexemplos (a combinação ingênua basta?)

- **C1: G1 não implica benefício.** Considere mudança de regime. Um termo útil no regime A é aceito com evidência válida (a mudança é "verdadeira") e passa a prejudicar no regime B. G1 se mantém, mas a previsão piora até que uma remoção seja aceita. **Lição:** G1 é uma garantia sobre a *evidência* das mudanças, que é descritiva, não sobre a utilidade futura. A utilidade exige premissas (G2) ou uma garantia de **reversão**: um termo que passa a prejudicar é removido com latência limitada, sob poder suficiente. A reversão deve fazer parte de G2.
- **C2: comparar com uma referência congelada.** Se o desafiante fosse comparado com o modelo do início do episódio, e não com o vigente, o e-process continuaria válido, mas responderia outra pergunta: aceitaria mudanças redundantes com promoções feitas no meio do episódio. Não é falha de validade; é uma escolha de desenho obrigatória (comparar sempre com o vigente).
- **C3: o teste da v0.51.** A estatística de correlação com o resíduo não é e-process fora de H₀ = "S correto" (E1). A proposta a substitui.
- **C4: níveis LOND síncronos com episódios sobrepostos.** Usar \(|R_{<k}|\) contando decisões ainda não tomadas quebraria a prova. Por isso a versão assíncrona conservadora (§7).

**Conclusão honesta.** Para a **segurança** (G1), a combinação de Choe & Ramdas com e-LOND assíncrono parece bastar, com cuidados técnicos (nulas aleatórias, margens, portões, assincronia). Em forma de resultado, G1 fica provavelmente no nível de um lema, não de uma contribuição central. **A contribuição, se existir, está em G2** (convergência, latência sob orçamento e reversão) **combinada com G1**, no mesmo procedimento de custo constante, e na demonstração empírica. Isso desloca o risco: é G2 que precisa ser nova e provável.

## 6. Afirmação-alvo (se tudo der certo)

> "Um previsor online de custo constante por passo cuja estrutura evolui por mudanças testadas. Toda mudança tem evidência sempre válida de melhora preditiva, e a fração de mudanças sem essa evidência é controlada ao longo de todo o fluxo, sem premissas distribucionais. Sob boa especificação, a estrutura converge para a verdadeira, sai de estruturas erradas por troca e desfaz mudanças que deixam de ajudar, com latência limitada em função do orçamento de busca."

**O que não se afirma:** descoberta de estrutura verdadeira sem premissas; garantia de benefício futuro sem premissas; novidade estatística das peças.

## 7. Pendências de prior art (antes de qualquer implementação)

1. **G2 é o ponto crítico.** Buscar recuperação de suporte online com garantia de consistência: Fu & Zhao (2025) têm "convergência de conjunto"; recuperação esparsa sequencial ou adaptativa; seleção de ordem recursiva consistente. Verificar se alguém já combinou consistência com controle distribution-free de inclusões falsas.
2. **Testes online assíncronos:** Zrnic, Ramdas & Jordan, *Asynchronous online testing of multiple hypotheses* (JMLR, 2021). Confirmar a forma exata dos níveis para episódios sobrepostos.
3. **Alocação de vagas de teste:** *multi-armed sequential testing by betting* (arXiv 2603.17925) e testes adaptativos com orçamento. Relevante para G2b.
4. **Nulas aleatórias com e-valores:** confirmar que \(\mathbb E[E\,\mathbf 1\{H\}]\le 1\) é a condição usada nas provas de FDR com e-valores. Relacionado: Wang & Ramdas (e-BH), *dynamic e-closure* (de Heide, 2026).

## 8. Plano de avaliação (esboço, a pré-registrar)

- **Sintético:** os processos do diagnóstico da v0.51 (um atraso, três atrasos, latente acionado, caudas pesadas, nulos) e mudança de regime (C1), com as métricas FCR empírico, fração do tempo com estrutura exata, latência e custo.
- **Real guiado por entradas:** pelo menos dois conjuntos, a definir antes de implementar (candidatos: hidrologia com vazão a montante, energia de edificações com clima, Silverbox, processos industriais).
- **Comparadores:** v0.51 congelada; só M; alpha-investing; AMRules/FIMT-DD (River); RLS/LMS esparso; a mesma arquitetura com o teste de Lindon et al. no lugar da comparação.
- **Hardware:** medição em microcontrolador após a estabilização.

## 9. Riscos

- **Poder:** testes de diferença de perda costumam ter menos poder local que testes de score/correlação. A latência pode piorar, e ela já é o gargalo.
- **Perda recortada:** o recorte em \(B_t\) reduz a sensibilidade a erros grandes. A escolha de \(B_t\) afeta o poder, não a validade.
- **G2 pode não ser demonstrável** com NLMS e premissas realistas. Pode ser necessário RLS nos coeficientes-sombra ou passos decrescentes, o que muda o custo.
- **Novidade de G2:** se já existir consistência com controle distribution-free de inclusões falsas online, a contribuição encolhe para a integração e a avaliação.

## 10. Próximos passos propostos

1. Resolver as pendências de prior art do §7, com prioridade para o item 1 (G2).
2. Se G2 sobreviver: escrever a prova de G1 por completo (curta) e tentar G2a e G2c no caso linear-gaussiano com RLS nos coeficientes-sombra.
3. Em paralelo: escolher e obter os conjuntos de dados reais guiados por entradas.
4. Só então implementar a v0.52, com pré-registro e uma mudança isolada por experimento.
