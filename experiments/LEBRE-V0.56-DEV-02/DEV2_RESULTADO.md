# LEBRE v0.56 — M1 com estudo sob demanda e triagem do que é fixo: resultado

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DEV-02` · **Plano:** `PLANO_DEV_DINAMICO.md` (commit `10735f6`); código e
análise commitados antes da execução (`a0e5026`); defeito corrigido durante a execução em `RUN_NOTAS.md` · **Números:**
`DEV2_RESULTADO.json` · **Natureza:** desenvolvimento, só com dados já usados (894 séries).

## 1. Parte A — conclusão pela regra fixada: escolhida a **D4**

Estudar sob demanda **vence** os períodos fixos. A D4 atualiza a regressão da M1 só quando o erro surpreende, com um
orçamento médio de 1/4 dos alvos (na prática ~30%, contando o aquecimento e o limite de 8 alvos sem atualização). Ela
alcança quase todo o ganho da atualização a cada passo, a ~5% a mais de custo que a v0.55.

| Variante | Atualiza | Bacias BR D-A | Bacias BR D-B | Bacias do Chile CL-V | Rios ONS (reserva 1) | Prédios | Custo (mediana; p95) | Critérios |
|---|---|---|---|---|---|---|---|---|
| C3 (a cada passo, referência) | 100% | 0,907 | 0,918 | 0,907 | 0,954 | 0,990 | — | referência do ganho |
| C4 (a cada 2, fixo) | 50% | 0,914 | 0,934 | 0,934 | 0,969 | 0,995 | 1,16; 1,54 | falha K1 (YC01 1,022) e K2 (Chile: 71% do ganho) |
| D1 (faixa de erro) | ~26% | 0,914 | 0,932 | 0,926 | 0,970 | 0,997 | 1,05 | falha K2 (Chile: 78%) |
| D2 (censura) | ~26% | 0,916 | 0,933 | 0,934 | 0,970 | 0,999 | 1,26 | falha K2 e K3 |
| D3 (orçamento 1/2) | ~51% | 0,904 | 0,918 | 0,912 | 0,962 | 0,992 | 1,21; 1,66 | **admissível** |
| **D4 (orçamento 1/4)** | **~30%** | **0,907** [0,891; 0,924] | **0,926** [0,915; 0,937] | **0,909** [0,891; 0,925] | **0,970** [0,957; 0,984] | 0,997 [0,994; 1,004] | **1,055; 1,54** | **admissível, a mais barata** |

(razões de MSE variante ÷ v0.55; < 1 é melhor)

- **D4 preserva** 100% (D-A), 90% (D-B) e 98% (Chile) do ganho da atualização a cada passo. O critério pedia 80% em cada
  conjunto.
- **Sem piora:** a pior família do E20 fica em 1,019 (YC01). A D4 melhora significativamente 21 das 64 famílias do E20.
  As seis pioras significativas são todas ≤ 0,7% (cenários sintéticos A01, A03, A08, A09, A10, A11).
- **Rios do ONS:** melhora de 1,7% a 3%. **Prédios:** neutro.
- **Por série:** 1,2% das 894 séries pioram mais de 5% (a pior, a série "C. BRANCO 2" dos rios do ONS, 1,155); 9,3% melhoram mais
  de 5%.
- **A frequência fixa erra dos dois lados:** a C4 atualiza 50% dos alvos e entrega menos que a D4 com 30%. O que importa é
  **quando** atualizar, não quantas vezes.

## 2. Parte B — triagem de sensibilidade (descritiva)

Razão variante ÷ v0.55 por parte (a mudança é de um único número, para outro valor fixo):

| Número (v0.55) | Valor testado | Prédios | D-A | D-B | Chile | ONS dev. | ONS res. | Marca |
|---|---|---|---|---|---|---|---|---|
| passo da estrutura (0,05) | 0,02 | 1,010 | 1,008 | 1,016 | 1,014 | 1,026 | 1,019 | — (0,05 já é bom) |
| | 0,2 | 1,010 | 1,011 | 1,000 | 0,992 | 1,028 | 1,035 | — |
| **passo da memória (0,05)** | **0,02** | **0,993** | **0,981** | **0,989** | **0,963** | **0,988** | **0,993** | **mal calibrado: melhora em todas as seis partes** |
| | 0,2 | 1,091 | 1,013 | 1,028 | 1,037 | 1,010 | 1,026 | — |
| defasagens do alvo na M1 (2) | 1 / 5 | ~1,00–1,01 / ~0,99–1,01 | | | | | | — |
| cadência dos pesos do núcleo (8) | 4 / 16 | ~0,99–1,01 | | | | | | — (não rouba) |
| esquecimento do núcleo (0,99) | 0,98 | 0,997 | 1,038 | 1,044 | 1,057 | 1,000 | 1,007 | — |
| | 0,995 | 1,005 | 0,980 | 0,990 | 0,986 | 1,006 | 1,008 | indício de dependência do contexto (melhora nas bacias, piora levemente prédios e rios), abaixo dos limiares da marca |

- **O passo da memória rouba resultado em todo lugar.** Com 0,02 em vez de 0,05, todas as partes melhoram, de 0,7% (prédios,
  rios) a 3,7% (Chile), com IC abaixo de 1 em todas. É a peça P2 da nota de desenho, e a próxima a tratar: primeiro saber se
  basta outro valor fixo ou se um passo variável vai mais longe.
- **O esquecimento do núcleo** mostra o padrão que um valor dinâmico resolveria: mais memória ajuda as bacias e atrapalha um
  pouco os prédios e os rios. É fraco (≤ 2%), mas consistente.
- **Não roubam resultado** (dentro da faixa testada): o passo da estrutura, a ordem autorregressiva da M1 e a cadência dos
  pesos do núcleo.

## 3. Limites

- Desenvolvimento: tudo em dados já usados. Parte das bacias (D-A, D-B, Chile) já tinha informado as etapas anteriores.
- O custo da D4 varia com os dados: a mediana é 1,055, o percentil 95 é 1,54 e o pior caso declarado é o da atualização
  a cada passo.
- A triagem testou só dois valores por número e não testa combinações.

## 4. O que vem a seguir

1. **Congelar a D4** como nova candidata da v0.56 (a M1 com estudo sob demanda, orçamento 1/4, 3 defasagens do alvo, 3
   bandas, sem recorte).
2. **Validação nova** em dados nunca tocados (bacias chilenas das posições 50–69 do sorteio da v0.56; prédios BDG2 das
   posições 265–294), com regras e pré-registro commitados antes. Depois, a avaliação final com a reserva lacrada e o
   pré-registro mantido.
3. Em paralelo, como desenvolvimento: a **peça P2** (passo da memória), com plano próprio.
