# LEBRE v0.56 — Versão barata da correção da M1: resultado da escolha

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DEV-01` · **Plano:** `PLANO_DEV_M1_BARATA.md` (commit `417c3b5`); código e
análise no commit `f1dea28`, antes da execução · **Números:** `DEV_M1_RESULTADO_escolha.json`.

## 1. Conclusão pela regra fixada

**Nenhuma variante é admissível.** Pela regra (§5 do plano), o resultado é registrado e a decisão volta ao responsável
pelo projeto. Nenhuma variante nova foi criada depois de ver os resultados.

Duas variantes falham por margens muito pequenas:
- **C5** (RLS a cada 4 alvos, 3 bandas): passa em não piora, custo e falhas, e preserva **69,4%** do ganho da correção
  completa nas bacias, contra o mínimo de 70%.
- **C4** (RLS a cada 2 alvos, 3 bandas): passa em ganho (89%), custo (1,15) e falhas, mas uma família do E20 (YC01,
  retornos diários, 4 séries) tem limite superior de **1,0209**, contra o máximo de 1,02. A estimativa pontual é 1,006
  e o IC (0,985–1,021) contém 1, então não é piora demonstrada.

## 2. Números

Execução única: 788 séries (728 do E20, 30 prédios, 30 bacias D-A), 8 modelos cada, nenhum erro, nenhuma previsão não
finita a mais que a v0.55.

| Variante | Bacias D-A: v0.55 ÷ variante [IC 95%] | Fração do ganho de C0 | Pior família do E20 (limite superior) | Prédios: variante ÷ v0.55 (sup.) | Custo (mediana) | Família mais cara | Critério que falha |
|---|---|---|---|---|---|---|---|
| C0 (referência) | 1,106 [1,088; 1,126] | 100% | — | 0,990 (0,996) | 2,28 | 5,10 (B06) | — |
| C1: a cada 2, 5 bandas | 1,096 | 91% | 1,020 (YC01) | 0,996 (1,001) | 1,55 | 2,80 | K3 custo |
| C2: a cada 4, 5 bandas | 1,055 | 53% | 1,010 | 0,996 (1,001) | 1,18 | 1,59 | K2 ganho |
| C3: a cada 1, 3 bandas | 1,102 | 97% | 1,019 (YC02) | 0,990 (0,997) | 1,51 | 2,62 | K3 custo |
| **C4: a cada 2, 3 bandas** | 1,094 [1,074; 1,115] | 89% | **1,021 (YC01)** | 0,995 (1,000) | 1,15 | 1,67 | **K1 por 0,0009** |
| **C5: a cada 4, 3 bandas** | 1,072 [1,054; 1,091] | **69,4%** | 1,010 | 0,996 (1,002) | **0,985** | 1,10 | **K2 por 0,6 ponto** |
| C6: a cada 8, 3 bandas | 1,041 | 40% | 1,037 (YB03) | 0,999 (1,001) | 0,90 | 1,00 | K1 e K2 |

**Fora das bacias** (descritivo): C4 melhora significativamente 19 famílias do E20 e C5, 18. Entre elas estão a
qualidade do ar (B03: 0,85 e 0,87), a maré (B07, VB07, WB07), a eólica (B06, VB06, WB06), a volatilidade (C02, VC02) e
cenários sintéticos (A02, A04, A10). As pioras significativas são todas menores que 0,7% (C4: seis famílias, a maior
1,006; C5: quatro, a maior 1,004).

## 3. Leitura

- A correção funciona em quase todo o banco, não só nas bacias. Os ganhos fora das bacias são de 1% a 15% e as pioras,
  quando existem, são pequenas.
- Baratear pela **frequência** da atualização custa mais ganho que baratear pelas **bandas**. Com três bandas (as
  defasagens 0 a 3, as mesmas do ARX), atualizar a cada 1, 2 ou 4 alvos preserva 97%, 89% e 69% do ganho.
- **C5 é mais barata que a v0.55** (0,985), porque o RLS de três bandas a cada 4 passos custa o mesmo que o de cinco
  bandas a cada 8, e o z menor barateia a previsão.

## 4. Decisão pendente (do responsável pelo projeto)

A regra não admite nenhuma variante. Seguir com qualquer uma delas é um **desvio declarado** da regra de escolha, a
registrar antes da replicação. A replicação (bacias D-B e prédios R) e, depois, a validação e a avaliação final em dados
nunca usados continuam sendo os testes que decidem.

## 5. Decisão e replicação (25/10/2026)

O responsável pelo projeto decidiu seguir com a **C5**, com desvio declarado só no critério K2 (`RUN_NOTAS.md`, §2,
registrado antes da replicação). A replicação, pela regra da §5 sem mudança, **passou**:

| | Resultado | Exigência |
|---|---|---|
| Bacias D-B (posições 110–139): v0.55 ÷ C5 | 1,053 [1,041; 1,067] | IC acima de 1 e ≥ metade do ganho de D-A |
| Prédios R (posições 85–114): C5 ÷ v0.55 | 0,995 [0,989; 1,000] | limite superior ≤ 1,02 |
| Custo mediano | 0,96 | — |

**A C5 é a candidata da v0.56:** a M1 com o RLS atualizado a cada 4 alvos aprendidos, 3 bandas de defasagem das entradas
([0], [1], [2–3]), 3 defasagens do alvo e sem o recorte de E; o resto da v0.55 sem mudança. Ela ainda precisa da
validação e da avaliação final pré-registradas em dados nunca usados.

## 6. Verificação pós-escolha (pedido do responsável pelo projeto)

Detalhes em `RUN_NOTAS.md`, §4.

| Verificação | Resultado |
|---|---|
| Famílias descartadas no critério de não piora | nenhuma (64 famílias, 728 séries em todas as variantes) |
| Consistência entre etapas e ambientes | A = L0 do DIAG-01 (60 bacias) e C0 = M5 do DIAG-02 (30 bacias), bit a bit |
| A mudança da M1 altera a estrutura? | não: eventos do núcleo, estrutura e previsão do núcleo idênticos em 11 séries; o controle placebo não muda |
| **Lacuna corrigida: rios do ONS** (onde o RLS piorou na v0.52; ausentes do banco) | checagem declarada antes de rodar: **passa e melhora** (reserva 1: 0,968 [0,955; 0,981]; desenvolvimento: 0,994) |
| Independência da replicação nas bacias | limitada: D-B já tinha sido usada nos diagnósticos; só os prédios R e os rios eram novos para esta linha |
| Pioras isoladas por série | raras (0,2% acima de 5%), mas até 1,167 numa bacia e 1,092 num rio |
| Diferença restante para o ARX-RLS | 1,048 (D-A) e 1,000 (D-B) |

**Limites da candidata que a avaliação final precisa observar:**
- a escolha usou o desvio declarado no K2;
- a direção da correção foi achada e replicada em bacias já olhadas;
- há pioras isoladas de até ~17% numa série;
- os eventos do portão da M2 podem mudar.
