# Validação da v0.56: pré-registro (commitado antes da execução)

**Data:** 25/10/2026.

**Candidata:** variante "C5" do protótipo `experiments/LEBRE-V0.56-PROTO-01`, congelada no commit `ef77728`. É a v0.55
com a M1 mudada em quatro parâmetros:
- regressão atualizada a cada 4 alvos aprendidos (em vez de 8);
- bandas de defasagem das entradas [0], [1], [2–3] (em vez de cinco bandas, até 15 passos);
- três defasagens do alvo (em vez de duas);
- sem o recorte da previsão da M1 em torno da previsão do núcleo.

O núcleo e a M2 não mudam; os eventos de estrutura do núcleo são idênticos aos da v0.55 (verificado nos testes do
protótipo e em `LEBRE-V0.56-DEV-01/verif_estrutura.py`).

**Comparação:** A, a v0.55 canônica, variante "A" do mesmo protótipo (cópia byte a byte de `b0522a0`, conferida em
`SHA256_COPIAS.txt`).

**História da candidata** (todas as etapas com plano commitado antes):
1. diagnósticos `LEBRE-V0.56-DIAG-01` e `-02`, em reservas consumidas do CAMELS-BR;
2. escolha da versão barata em `LEBRE-V0.56-DEV-01`, num banco de todas as famílias com dados usados. Nenhuma variante
   foi admissível; a C5 seguiu por **desvio declarado** (preserva 69,4% do ganho da correção completa nas bacias, contra
   o mínimo de 70%). Ela passou nos demais critérios, foi replicada e passou numa checagem de segurança nos rios do ONS.
   Limites registrados: a replicação nas bacias usou dados já olhados; há pioras isoladas de até ~17% numa série.

## 1. Dados

`experiments/LEBRE-V0.56-DATA-01`: regras em `SPLIT_RULES.md` e `SPLIT_RULES_CORRECAO_01.md`; `SPLIT_V056.json`, SHA-256
`ec9bb01ea6dcb8bc177a55e7729081746b22fbcd86ca35297674e640d10604e3`; dados brutos com SHA-256 em
`SNAPSHOT_SHA256SUMS.txt` e `SNAPSHOT_BASE_SHA256SUMS.txt`.

| Família | Séries | Construção | Bloco do bootstrap |
|---|---|---|---|
| `camels_cl` | 20 bacias (posições 30–49 da permutação do sorteio) | vazão diária (mm), 1990–2014; entradas do mesmo dia: precipitação MSWEP, evapotranspiração potencial (Hargreaves), temperatura média (CR2MET); vazão negativa ou ausente = alvo ausente; entradas ausentes mantidas no último valor, com o passo marcado em quarentena (a regra do CAMELS-BR); sem ciclo; referência persistência | 30 |
| `bdg2` | 30 medidores (posições 205–234) | horária; ciclos 24 e 168; referência sazonal (a construção das avaliações anteriores) | 168 |

## 2. Execuções e medidas

Cada série roda **duas vezes**, com A e C5 e as entradas reais. A avaliação usa as previsões a partir de 20% da série,
como na avaliação final da v0.55. Razão de MSE C5 ÷ A por série; resumo por família pela média geométrica, com IC 95%
pelo bootstrap pareado de blocos móveis da avaliação final da v0.55 (`reps`, média das réplicas em log), 2.000 réplicas,
semente `[2026102902, família, série]`.

## 3. Critério para seguir à avaliação final

A validação **passa** se valerem as duas:
- **V1 benefício nas bacias novas:** em `camels_cl`, o limite superior do IC 95% de C5 ÷ A é < 1,00;
- **V2 sem piora nos prédios:** em `bdg2`, o limite superior do IC 95% de C5 ÷ A é ≤ 1,02.

Também são exigidos: nenhuma previsão não finita de C5 onde a de A é finita; custo mediano C5 ÷ A ≤ 1,25.

**Se a validação falhar:** o resultado é registrado, a avaliação final **não** é executada e a decisão volta ao
responsável pelo projeto.

**Reportados sem decidir:** razões por série, piores séries, janela curta (passos 200 a 2.000), custo por família.

## 4. Execução e falhas

- Uma única execução: `val_run.py`, depois `val_analise.py`.
- Falha de infraestrutura pode ser repetida com o mesmo código e as mesmas sementes, registrada em `RUN_NOTAS.md`.
- Nenhuma mudança de modelo, de critério ou de análise depois de ver resultados.
- O pré-registro da avaliação final (`experiments/LEBRE-V0.56-FINAL-01/PREREG_V056_FINAL.md`) é commitado junto com este,
  antes da validação.
