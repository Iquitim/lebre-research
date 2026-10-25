# Avaliação final da v0.56: pré-registro (commitado antes da validação e da execução; regra de promoção vinculante)

**Data:** 25/10/2026.

**Candidata e comparação:** as mesmas do pré-registro da validação (`experiments/LEBRE-V0.56-VAL-01/PREREG_V056_VAL.md`):
a variante "C5" do protótipo `experiments/LEBRE-V0.56-PROTO-01` (commit `ef77728`) contra a v0.55 canônica (variante
"A" do mesmo protótipo). A avaliação final só roda se a validação passar.

## 1. Reserva

`experiments/LEBRE-V0.56-DATA-01/SPLIT_V056.json` (SHA-256 `ec9bb01ea6dcb8bc177a55e7729081746b22fbcd86ca35297674e640d10604e3`).

| Família | Séries | Construção | Bloco |
|---|---|---|---|
| `camels_cl` | 30 bacias (posições 0–29 do sorteio) | a da validação | 30 |
| `bdg2` | 30 medidores (posições 235–264) | a das avaliações anteriores | 168 |
| `eolica` | 8 usinas (semente 5663) | a da v0.55: geração do ONS 2024–2025; tempo do Open-Meteo no local da usina (vento a 100 m: velocidade, u, v; vento a 10 m; temperatura); ciclo 24; referência sazonal | 168 |
| `solar` | 8 usinas (semente 5664), jan–set/2026 | a da v0.55: geração do ONS; radiação global e direta, nuvens, temperatura; ciclo 24; referência sazonal | 168 |
| `camels_br` | 17 bacias (posições 220–236) — família secundária | a do CAMELS-BR nas avaliações anteriores | 30 |

Sem família de níveis e sem rios do ONS (não restam séries inéditas; `SPLIT_RULES.md`, §2).

## 2. Execuções

Cada série roda **quatro vezes**, com a configuração canônica de cada modelo:
- A e C5 com as entradas reais (a **execução principal**);
- A e C5 com as entradas reais mais **duas entradas placebo** (passeios aleatórios gaussianos independentes), gerados com
  a semente `[2026102900, índice da família, índice da série]`.

Avaliação a partir de 20% da série; blocos da tabela; 2.000 réplicas, semente `[2026102901, família, série]`; a mesma
estatística da validação.

## 3. Regra de promoção (vinculante): a v0.56 é PROMOVIDA se, e só se, valerem todas

| Código | Critério |
|---|---|
| R1 sem piora | em **cada** família (inclusive `camels_br`), o limite superior do IC 95% da média geométrica das razões de MSE C5 ÷ A (execução principal) é ≤ 1,02 |
| R2 controle negativo | nas 93 séries, a fração com alguma entrada placebo na estrutura final da execução placebo: para C5, limite superior de Clopper–Pearson ≤ 0,10, **e** contagem de C5 ≤ a de A |
| R3 sem falha numérica | nenhuma previsão não finita de C5 onde a de A é finita, em nenhuma execução |
| R4 custo | mediana por série da razão de custo C5 ÷ A na execução principal ≤ 1,25 |
| R5 memória | estado estimado (a estimativa da v0.55, 86.180 B, mais a variação do estado da M1 com cinco entradas escolhidas, 8 bytes por número) ≤ 131.072 B |
| **R6 benefício** | em `camels_cl`, o limite superior do IC 95% de C5 ÷ A é **< 1,00** |

**Reportados sem decidir:**
- razões por família e por série, e as piores séries;
- janela curta (passos 200 a 2.000);
- custo por família;
- eventos do portão da M2;
- igualdade, série a série, da estrutura final entre A e C5 (esperada pela construção).

**Não feito, e declarado antes:** comparação com modelos externos. Ela pode ser feita depois, só como referência e com
plano próprio.

## 4. Execução e falhas

- Uma única execução: `final_run.py`, depois `final_analise.py`.
- Falha de infraestrutura pode ser repetida com o mesmo código e as mesmas sementes, registrada em `RUN_NOTAS.md`.
- Nenhuma mudança de modelo, de critério ou de análise depois de ver resultados, nem depois de ver a validação.
- Ambiente: o mesmo da validação; o protótipo num worktree limpo do commit `ef77728`.
