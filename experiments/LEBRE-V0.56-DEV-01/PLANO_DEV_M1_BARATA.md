# LEBRE v0.56 — Versão barata da correção da M1: plano (commitado antes de qualquer medição)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DEV-01` · **Natureza:** desenvolvimento, só com dados já usados. Nenhum
dado novo é tocado; a avaliação final da v0.56, se houver, terá plano e dados próprios.

## 1. Ponto de partida

O `LEBRE-V0.56-DIAG-02` mostrou que três mudanças na M1, **juntas**, fecham quase toda a diferença da v0.55 para um ARX
com RLS nas bacias, e o efeito replicou: RLS a cada alvo aprendido (em vez de a cada 8), sem o recorte de E em torno da
previsão do núcleo e três defasagens do alvo (em vez de duas). Mas o custo por passo subiu ~2,7 vezes, acima do limite de
1,25 vez a versão anterior usado na promoção da v0.55. Decisão do responsável pelo projeto (25/10/2026): procurar primeiro
uma versão barata, em todas as famílias, só com dados já usados.

O custo da M1 é dominado pela atualização do RLS, cerca de 6k² + 5k operações, com k = 1 + (defasagens do alvo) +
(bandas) × m e m = mín(entradas, 5). Duas alavancas baixam o custo: a frequência da atualização e o número de bandas de
defasagem das entradas. Com três bandas ([0], [1], [2–3]), a M1 cobre as defasagens 0 a 3, as mesmas do ARX-RLS da
comparação.

## 2. Variantes

Todas com as três defasagens do alvo e **sem** o recorte (as duas mudanças que, no diagnóstico, só pesam junto com a
atualização mais frequente). A dormência, a triagem e a escolha das entradas da M1 ficam como na v0.55. O núcleo e a M2
não mudam.

| Código | Atualização do RLS | Bandas | RLS por passo (m = 3 / m = 5) |
|---|---|---|---|
| A | v0.55 (a cada 8; 5 bandas; 2 defasagens; com recorte) | 5 | 254 / 606 |
| C0 | a cada 1 (= M5 do diagnóstico, referência de ganho) | 5 | 2.261 / 5.191 |
| C1 | a cada 2 | 5 | 1.130 / 2.596 |
| C2 | a cada 4 | 5 | 565 / 1.298 |
| C3 | a cada 1 | 3 | 1.079 / 2.261 |
| C4 | a cada 2 | 3 | 540 / 1.130 |
| C5 | a cada 4 | 3 | 270 / 565 |
| C6 | a cada 8 | 3 | 135 / 283 |

O custo vale nos modos ativos; no modo dormente a M1 segue a v0.55. O código é a subclasse de diagnóstico do `DIAG-02`
(`diag_m1.py`), estendida com o número de bandas. Teste de fumaça antes de rodar: com as chaves no padrão, previsões
idênticas, bit a bit, às da v0.55.

## 3. Banco (todas as famílias, só dados já usados)

| Parte | Conteúdo | Uso |
|---|---|---|
| **E20 do LEBRE Lab** | 64 famílias, 728 séries: 12 cenários sintéticos (A01–A12), carga, solar, eólica, qualidade do ar e maré (B, V, W, X, Y) e finanças, inclusive níveis (C) | escolha |
| **Prédios** | BDG2, posições 115–144 da permutação da v0.52 (reserva final da v0.54, consumida) | escolha |
| **Bacias D-A** | CAMELS-BR, posições 140–169 (reserva final da v0.54, consumida) | escolha |
| **Bacias D-B** | CAMELS-BR, posições 110–139 (reserva final da v0.53, consumida) | só replicação da escolhida |
| **Prédios R** | BDG2, posições 85–114 (reserva final da v0.53, consumida) | só replicação da escolhida |

Travas: os carregadores recusam bacias de posição ≥ 170 e medidores de posição ≥ 145 (as reservas da v0.55 e o que nunca
foi usado).

## 4. Medidas

- **Precisão:** razão de MSE de cada variante contra A, por série.
  - No E20: a função, os blocos e a janela do E20 (`m2_dev.par_bootstrap`, a partir de 20% da série), como no critério
    de precisão das rodadas da v0.55.
  - Nos prédios e nas bacias: a função da comparação externa (`reps`), janela de 30% da série até o fim, blocos de 168
    horas (prédios) e 30 dias (bacias).
  - Resumo por família: média geométrica e IC 95% pela média das réplicas em log.
- **Custo:** razão do custo por passo (variante ÷ A) por série; mediana no banco inteiro (E20 + prédios + D-A) e máximo
  por família.
- **Falhas:** previsões não finitas.
- Sementes do bootstrap: 2026102804 (escolha) e 2026102805 (replicação), conferidas como não usadas em 25/10/2026.

## 5. Regra de escolha (fixada antes)

Uma variante C1 a C6 é **admissível** se:
- **K1, nenhuma piora:** em nenhuma família do E20 e nos prédios o limite superior do IC 95% da razão contra A passa de
  1,02;
- **K2, ganho nas bacias:** em D-A, log(MSE A ÷ MSE Cx) ≥ 0,7 · log(MSE A ÷ MSE C0), com limite inferior do IC acima de
  zero (preserva pelo menos 70% do ganho da correção completa);
- **K3, custo:** mediana da razão de custo no banco ≤ 1,25;
- **K4:** nenhuma previsão não finita a mais que A.

**Escolha:** entre as admissíveis, a de menor custo mediano; empate (diferença < 0,02), a de maior ganho em D-A.

**Replicação da escolhida** em D-B e nos prédios R: ganho em D-B com IC acima de zero e pelo menos metade do de D-A;
prédios R com limite superior ≤ 1,02.

**Se nenhuma for admissível:** o resultado é registrado com o critério que falhou em cada variante e volta ao
responsável pelo projeto (a decisão sobre o teto de custo é dele). Nenhuma variante nova é criada depois de ver os
resultados.

## 6. O que esta etapa não faz

Não muda o núcleo nem a M2; não toca dados novos; não promove nada. A escolhida, se houver, vira a candidata da v0.56,
que ainda precisa de validação e avaliação final pré-registradas em dados nunca usados (as bacias novas do CAMELS-CL e as
demais famílias).

## 7. Arquivos

Este plano, `dev_m1.py` (variantes e fumaça), `dev_dados.py` (carregadores com travas), `dev_run.py`, `dev_analise.py`,
`RUN_NOTAS.md`, `DEV_M1_RESULTADO.md` e `.json`. Previsões em `preds/` (fora do git).
