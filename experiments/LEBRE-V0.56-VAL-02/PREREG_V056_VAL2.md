# Segunda validação da v0.56 (candidata D4): pré-registro (commitado antes da execução)

**Data:** 25/10/2026.

**Candidata:** variante "D4" do protótipo `experiments/LEBRE-V0.56-PROTO-02`, congelada no commit `c3074bd`. É a v0.55
com a M1 mudada:
- **estudo sob demanda:** a regressão da M1 é atualizada quando o alvo surpreende, com orçamento médio de 1/4 dos alvos,
  aquecimento obrigatório e nunca mais de 8 alvos sem atualização;
- três defasagens do alvo, bandas de defasagem das entradas [0], [1], [2–3], sem o recorte da previsão da M1.

O núcleo e a M2 não mudam (eventos de estrutura idênticos aos da v0.55, conferido nos testes do protótipo).

**Comparação:** A, a v0.55 canônica, variante "A" do mesmo protótipo (cópias byte a byte conferidas).

**História** (todas as etapas com plano commitado antes):
1. a primeira candidata (C5, M1 com período fixo de 4 alvos) **não passou** na primeira validação
   (`LEBRE-V0.56-VAL-01`);
2. o diagnóstico (`LEBRE-V0.56-DIAG-03`) mostrou que o período fixo de 4 alvos tirava o ganho nas bacias do Chile;
3. por decisão do responsável pelo projeto, períodos fixos deram lugar ao estudo sob demanda (`LEBRE-V0.56-DESIGN-NOTE-01`);
4. a D4 foi escolhida por regra fixada antes, em 894 séries já usadas (`LEBRE-V0.56-DEV-02`). Esse banco inclui as 20
   bacias chilenas e os 30 prédios da primeira validação.

## 1. Dados

`experiments/LEBRE-V0.56-DATA-01/SPLIT_RULES_ADENDO_01.md`; `SPLIT_V056_VAL2.json`, SHA-256
`7a80c2911cff967e1422cb2ad37b587967b818921f8102c00559b97555557d76`. Séries nunca usadas, fora da reserva final:

| Família | Séries | Construção | Bloco |
|---|---|---|---|
| `camels_cl` | 20 bacias (posições 50–69 do sorteio da v0.56) | a da primeira validação (1990–2014; MSWEP, evapotranspiração potencial de Hargreaves, temperatura média; referência persistência) | 30 |
| `bdg2` | 30 medidores (posições 265–294) | a das avaliações anteriores | 168 |

## 2. Execuções e medidas

A e D4, entradas reais. Avaliação a partir de 20% da série; razão de MSE D4 ÷ A por série; por família, média
geométrica com IC 95% pelo bootstrap pareado de blocos móveis `reps` (`LEBRE-V0.55-COMP-01/comp_analise.py`, média das
réplicas em log), 2.000 réplicas, semente `[2026102906, família, série]`, conferida como não usada.

## 3. Critério para seguir à avaliação final (o mesmo da primeira validação)

- **V1:** em `camels_cl`, limite superior do IC 95% de D4 ÷ A < 1,00;
- **V2:** em `bdg2`, limite superior ≤ 1,02;
- nenhuma previsão não finita de D4 onde a de A é finita;
- custo mediano D4 ÷ A ≤ 1,25.

**Se falhar:** registro; a avaliação final **não** roda; a decisão volta ao responsável pelo projeto.
**Reportados sem decidir:** razões por série, piores séries, janela curta, custo (mediana e percentil 95), fração de
atualizações da M1.

## 4. Execução

Uma única execução (`val2_run.py`, depois `val2_analise.py`). Falha de infraestrutura pode ser repetida com o mesmo código
e as mesmas sementes, registrada em `RUN_NOTAS.md`. Nenhuma mudança depois de ver resultados. O adendo do pré-registro da
avaliação final (`experiments/LEBRE-V0.56-FINAL-01/PREREG_V056_FINAL_ADENDO_01.md`) é commitado junto com este.
