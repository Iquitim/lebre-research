# LEBRE v0.56 — Diagnóstico das bacias: plano (commitado antes de qualquer medição)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DIAG-01` · **Natureza:** diagnóstico **exploratório**, em reservas já
consumidas. Nenhuma mudança de desenho é feita nesta etapa. Uma candidata da v0.56, se houver, terá plano próprio.

## 1. Pergunta

Na comparação externa da v0.55 (só referência, 30 bacias da reserva final), um ARX com mínimos quadrados recursivos
(ARX-RLS, ~1.700 operações por passo) errou cerca de 11% a 13% menos que a v0.55 nas bacias, com significância depois
da correção de Holm. Nas outras famílias, a v0.55 foi melhor ou empatou. Na avaliação final, a v0.55 também ficou 0,8%
pior que a v0.54 nas bacias, mais no início das séries.

- **Q1 (principal).** Que ingrediente do ARX-RLS explica a vantagem dele sobre a LEBRE nas bacias?
- **Q2 (secundária).** Onde, no tempo e no regime de vazão, se concentra a perda da v0.55 contra a v0.54 nas bacias?

## 2. Dados

Bacias do CAMELS-BR, mesma regra de elegibilidade e mesma permutação (semente 5202) da v0.52. Alvo: vazão diária (mm).
Entradas: precipitação (MSWEP), evapotranspiração real (GLEAM), temperatura média (ERA5-Land). Sem ciclo declarado,
referência "persistence", como nas avaliações.

| Conjunto | Posições | Séries | Uso |
|---|---|---|---|
| **D-A (descoberta)** | 140–169 (reserva final da v0.54, consumida em 13/10/2026) | 30 | todas as medições das §3 e §4 |
| **D-B (replicação)** | 110–139 (reserva final da v0.53, consumida em 09/10/2026) | 30 | só a replicação da §5, depois do resultado de D-A |
| Fumaça | 0–9 (desenvolvimento da v0.52) | 10 | só testes de funcionamento dos scripts, sem valor de evidência |
| **Fora** | 170–219 (validação e reserva final da v0.55) | 50 | **não usadas**: foi nelas que a pergunta surgiu; procurar a explicação ali seria circular |
| **Lacradas** | 220–236 (nunca usadas) | 17 | **não tocadas** |

O carregador recebe uma lista explícita de IDs, confere que cada ID está na posição declarada da permutação e recusa
qualquer posição ≥ 170.

**Restrição registrada:** 17 bacias inéditas não bastam para uma família da avaliação final de uma futura v0.56. Se o
diagnóstico levar a uma candidata, a fonte de bacias novas (outro conjunto CAMELS ou Caravan) será decidida e registrada
antes de qualquer download.

## 3. Medições em D-A (execução única)

Todas as séries rodam do primeiro ao último passo. Janela de avaliação principal: a mesma da comparação externa (de 30% da série até o fim;
alvo observado e previsão finita em todos os modelos comparados). Janela curta: passos 200 a 2.000.

### 3.1 Escada do lado do ARX-RLS (cada degrau tira um ingrediente)

O código do ARX-RLS é a classe `ArxRls` de `LEBRE-V0.55-COMP-01/comp_run.py`, importada sem alteração. Entradas
padronizadas causalmente como na comparação. λ calibrado, como na comparação, nos primeiros 15% dos passos observados (no máximo 5.000), em {0,99; 0,999; 0,9999},
salvo onde dito.

| Código | Modelo | Ingrediente testado |
|---|---|---|
| R0 | ARX-RLS da comparação | — (reprodução) |
| R1 | só a vazão: constante + y(t−1..t−3), RLS | as entradas |
| R2 | só a precipitação como entrada (t..t−3) | evapotranspiração e temperatura |
| R3 | entradas só em t (sem defasagens) | as defasagens das entradas |
| R4 | só y(t−1) como passado do alvo | a ordem autorregressiva |
| R5 | λ = 1 (sem esquecimento) | o rastreamento de mudanças |
| R6 | mesmos atributos de R0, NLMS em vez de RLS (μ calibrado na mesma janela de calibração, em {0,01; 0,05; 0,2}) | o algoritmo de adaptação (segunda ordem contra gradiente) |

### 3.2 Lado da LEBRE

Código congelado da v0.55 (`LEBRE-V0.55-PROTO-01`, commit `b0522a0`), conferido como na avaliação final.

| Código | Modelo | O que mede |
|---|---|---|
| L0 | v0.55 (B10), configuração canônica | — |
| L1 | v0.54 (variante A do mesmo protótipo) | Q2 |
| L2 | v0.55, só o núcleo estrutural (sem M1 e M2) | o papel de M1 e M2 nas bacias |
| L3 | v0.55 com todas as unidades ativas desde o início e sem experimentos ("tudo ligado") | o atraso de aceitação |
| L4 | a memória do núcleo sozinha (a previsão m, gravada dentro da execução de L2) | a dinâmica autorregressiva da LEBRE, comparada com R1 |

L3 é uma subclasse de diagnóstico, nova, escrita nesta etapa: no início, todas as entradas e o passado do alvo ficam
ativos com as bandas de oitava e pesos zero (e o mesmo na estrutura de inovação), o estado residual ativo com pesos zero,
e nenhum experimento abre. Antes da execução, um teste de fumaça confere que, com a subclasse desligada, as previsões são
idênticas, bit a bit, às de L0 numa bacia de fumaça.

### 3.3 Estatística

- Por série: MSE na janela; razões entre modelos; média geométrica das razões por conjunto.
- IC 95%: bootstrap pareado por blocos móveis, com a mesma função da comparação externa (`reps` de `comp_analise.py`),
  blocos de 30 dias, 2.000 réplicas; estatística do conjunto = média, sobre as séries, do log da razão por série, e IC
  pelos percentis da média das réplicas, como na comparação. Sementes: 2026102800 (D-A) e 2026102801 (D-B), conferidas como não usadas em 25/10/2026.
- Correção de Holm sobre os contrastes da escada (R1 a R6 contra R0; L2, L3 e L4 contra o par correspondente), por
  conjunto.

## 4. Localização (D-A; descritiva)

Para L0 contra R0 (Q1) e L0 contra L1 (Q2): a fração da diferença de erro quadrático acumulado e a razão de MSE dentro
de cada regime, com os regimes definidos pela série observada:
- **chuva:** precipitação em t ou t−1 acima do percentil 90 dos dias com chuva da própria bacia;
- **subida:** y(t) > y(t−1), fora de chuva;
- **recessão:** os demais passos;
- e por tempo: passos 200–2.000, 2.000–5.000 e o restante.

Também por série (descritivo): a correlação da razão L0/R0 com a fração de dias de chuva, o desvio-padrão relativo da
vazão e o instante de aceitação da precipitação na v0.55.

## 5. Regras de leitura (fixadas antes)

Seja G = log(MSE de L0 / MSE de R0), em média geométrica sobre as séries (a vantagem do ARX-RLS).

1. **Reprodução.** Se o IC 95% de G em D-A contém zero, a vantagem não se reproduz nas reservas consumidas: isso é
   registrado como o resultado principal e a §5.2 não é aplicada.
2. **Ingrediente do ARX.** Para cada degrau k, Δk = log(MSE de Rk / MSE de R0). O ingrediente explica **parte
   substancial** da vantagem se Δk ≥ 0,5·G e o limite inferior do IC de Δk (com Holm) for maior que zero.
3. **Lado da LEBRE.** O atraso de aceitação explica parte substancial se log(MSE de L0 / MSE de L3) ≥ 0,5·G com IC acima
   de zero. A memória é a parte fraca se log(MSE de L4 / MSE de R1) > 0 com IC acima de zero.
4. **Replicação em D-B.** Só os ingredientes classificados como "parte substancial" em D-A rodam em D-B (os modelos
   necessários, mais R0 e L0). A classificação se mantém se o efeito tiver o mesmo sinal, IC acima de zero e pelo menos
   metade da magnitude de D-A. O que não replicar é registrado como não replicado.
5. **Saída.** Um relatório com uma de cinco conclusões, ou mais de uma se várias passarem: (a) algoritmo de adaptação;
   (b) dinâmica autorregressiva da memória; (c) atraso de aceitação; (d) rastreamento de mudanças; (e) nenhum ingrediente
   isolado explica.

## 6. O que esta etapa não faz

- Não muda a LEBRE nem a biblioteca; não toca os dados lacrados nem os da v0.55.
- Não faz afirmação confirmatória: as reservas usadas já foram consumidas; a replicação em D-B reduz, mas não elimina, o
  risco de uma explicação ajustada aos próprios dados.
- Não compara com os modelos de fundação.

## 7. Custo e arquivos

Estimativa: ~60 séries × 7 modelos ARX e 4 execuções da LEBRE, alguns minutos por série em paralelo. Previsões em
`preds/` (fora do git). Arquivos: este plano, `diag_dados.py` (carregador com as travas da §2), `diag_run.py`,
`diag_allon.py` (subclasse L3 e o teste de fumaça), `diag_analise.py`, `DIAG_RESULTADO.md` e `.json`, `RUN_NOTAS.md`.
Qualquer desvio deste plano é registrado em `RUN_NOTAS.md` antes da análise.
