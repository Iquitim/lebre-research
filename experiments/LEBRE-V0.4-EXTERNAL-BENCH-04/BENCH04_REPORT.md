# Relatório — BENCH-04: LEBRE v0.4 em dados reais variados, modelos novos e dados brasileiros

Pré-registro: `PREREG_BENCH04.md` (SHA-256 `34e04349…`). Emenda 01 (orçamento de tempo do Chronos, antes dos resultados afetados).
Objeto: `lebre_v042.py`, congelada e sem calibração. Este estágio não altera a arquitetura. M3 continua `UNOPENED`; `NOVELTY_CLAIM_READY = NO`.

## 1. Escopo

- **10 tarefas reais, nunca usadas antes:**
  - 5 brasileiras: ONS (carga SE/CO e Norte; geração eólica e solar do NE) e BCB (dólar/real);
  - 5 internacionais: UCI Air Quality, Tetouan, Bike Sharing, OikoLab temperatura e vento.
- **35 modelos no ranking:**
  - filtros clássicos, BENCH-01B e River (5 modelos);
  - **novos:** DLinear e NLinear online, QKLMS, RFF-NLMS, Holt-Winters, River AMRules e PA;
  - **modelos de fundação:** Chronos-Bolt tiny e small, Chronos-2 e Chronos-2 com covariáveis.
- Sementes 7611..7613. Foram 972 execuções online, mais 36 do Chronos.

## 2. Critérios primários

| | Limiar | Todas (10) | Só BR (5) |
|---|---|---|---|
| K-a vence persistência | ≥ 70% | **60% ❌** | 40% ❌ |
| K-b ≤ 1,25× melhor clássico | ≥ 60% | **70% ✅** | 60% ✅ |
| K-c zero divergências | 100% | **✅** | ✅ |
| K-d ≤ 1,25× v0.3.2 | ≥ 90% | **60% ❌** | 40% ❌ |
| K-e cobertura 90% ∈ [0,85; 0,95] | ≥ 80% | **80% ✅** | 60% ❌ |
| **Rótulo** | | **`PARTIALLY_COMPETITIVE` (3/5)** | `NOT_COMPETITIVE` (2/5) |

**É a primeira vez que a v0.4 não replica o resultado do BENCH-03b (5/5).** Nesse conjunto, a v0.4 fica atrás da v0.3.2:
razão geométrica de 1,18×, com perdas grandes em BR2 (0,170 contra 0,086) e em Tetouan (0,038 contra 0,022).

## 3. Ranking (rank médio, 35 modelos)

1. Chronos-2: 1,8
2. Chronos-2 com covariáveis: 2,0
3. **NLinear online: 3,8**
4. Chronos-Bolt small: 4,7
5. Chronos-Bolt tiny: 5,2
6. DLinear online: 6,3
7. Holt-Winters e LEBRE v0.3.2: 9,3
8. **LEBRE v0.4: 9,9 (9ª posição)**
9. Persistência: 11,2
10. ARX-NLMS: 12,2
11. IPNLMS: 13,1

A LEBRE v0.4 fica à frente de todos os filtros adaptativos, redes online, árvores do River e modelos de kernel. Mas fica **muito atrás** dos modelos com janela longa:
- **Contra o melhor Chronos:** o NMSE da LEBRE é 4,2× maior (média geométrica). Ela fica dentro de 1,25× dele em só 2 de 10 tarefas.
- **Contra o melhor entre DLinear, NLinear e Holt-Winters:** o NMSE é 2,7× maior. Também dentro de 1,25× em só 2 de 10 tarefas.
- **K-b ampliado** (incluindo Holt-Winters, DLinear e NLinear entre os clássicos): 20%.
- **Câmbio (BR5):** ninguém supera a persistência; a LEBRE fica empatada com ela, com NMSE de 0,0009 contra 0,0008.

## 4. Intervalos e custo

- **Cobertura de 90% da LEBRE:** fica na faixa em 8 de 10 tarefas. Fica abaixo em BR4 (solar, 0,83) e ficaria acima em BR5 (0,985).
  A largura relativa é 2 a 4× maior que a do Chronos-2, que também cobre bem (0,88–0,94). **Os intervalos da LEBRE são calibrados, mas largos.**
- **Custo:** a LEBRE gasta ~110 FP/passo, ~1,4 kB e ~0,05 ms/passo.
  - NLinear: ~810 FP e 0,026 ms.
  - Chronos-Bolt tiny: 0,8 ms/passo, com 9M parâmetros.
  - Chronos-2: 28 ms/passo, ou 104 ms com covariáveis. **São 500 a 2000× mais lentos que a LEBRE na CPU.**
  - Os tempos do Chronos amostrado ficaram parcialmente inflados, porque um processo antigo disputou a CPU por alguns minutos.
- **Explicação:** a LEBRE termina com 0 a 4 átomos estruturais por tarefa e de 1 a 74 eventos de ciclo de vida.

## 5. Por que a LEBRE perdeu (diagnóstico pós-hoc, fora do pré-registro, sem efeito na decisão)

`posthoc_diag.py`: mesma v0.4 congelada. O que muda é só a **representação do alvo**, feita pelo ambiente.

| Tarefa | RAW (BENCH-04) | Δy (diferenças) | Δy + y[t−s] | NLinear | melhor Chronos |
|---|---|---|---|---|---|
| BR1 carga SE/CO | 0,078 | 0,027 | 0,029 | 0,015 | 0,004 |
| BR2 carga N | 0,170 | 0,066 | 0,059 | 0,041 | 0,023 |
| BR4 solar NE | 0,074 | 0,059 | **0,019** | 0,012 | 0,007 |
| R2 Tetouan | 0,038 | **0,006** | **0,005** | 0,0035 | 0,0047 |
| R3 Bike | 0,259 | 0,273 | **0,175** | 0,128 | 0,035 |

1. **Nível alto com deriva lenta** (carga em dezenas de milhares de MW) prejudica a LEBRE, que aprende o viés e o nível devagar.
   Trocar o alvo por diferenças corta o erro pela metade ou mais. Em Tetouan, ela passa de pior que a persistência para melhor que ela.
2. **Falta memória sazonal longa.** Com y[t−s] como entrada e o alvo em diferenças, o solar cai de 0,074 para 0,019.
   Porém, com o alvo em nível bruto, acrescentar y[t−s] **piora** as cargas (0,24 em BR1). O efeito depende da representação.
3. Mesmo com as duas correções, continua uma lacuna de ~1,5 a 2× para o NLinear e maior para o Chronos. Ela vem da janela longa (96 a 288 passos) desses modelos.

## 6. Conclusão honesta

- Em dados reais sazonais de alta frequência, a LEBRE v0.4 **não é competitiva** com modelos modernos de janela (NLinear, DLinear) nem com modelos de fundação (Chronos).
- Ela continua **à frente da família de filtros adaptativos e redes online** contra a qual foi projetada.
- Ela mantém as vantagens de **custo** (centenas a milhares de vezes mais barata que o Chronos), **zero divergências**, **intervalos calibrados** e **explicação exata**.
- A declaração de benefícios da v0.4 deve ser lida com esse limite. A frase "competitiva (1ª de 24 no BENCH-03b)" vale para aquele conjunto e **não se generaliza** para séries sazonais reais com nível alto.
- **Direções para a v0.5 (a pré-registrar):** representação do alvo por diferenças ou nível adaptativo, e um átomo sazonal (y[t−s]) com o mesmo teste de evidência.

## 7. Adendo pós-hoc — de onde vem a regressão da v0.4 contra a v0.3.2 (`posthoc_ablation.py`, `posthoc_offsets.py`)

Fora do pré-registro. A v0.4 congelada foi usada sem alteração; só mudam as opções do construtor e o ponto de partida do fluxo.

- **Ablação** (razão geométrica de NMSE contra a v0.3.2):
  - completa: 1,175;
  - sem IPNLMS: 1,168;
  - IPNLMS com α = 0,5: 1,192;
  - ganhos a cada 10 passos: 1,154;
  - sem congelar σ²: 1,179;
  - **sem o recorte de ±8: 0,993**.
  **O IPNLMS não é a causa. O recorte das entradas padronizadas é.**
- **Robustez a 10 pontos de partida** (0 a 450 passos descartados, com a mesma janela de teste):
  - v0.4 contra v0.3.2: **1,21×** (1,25× pareado), ou seja, a regressão é real;
  - v0.4 sem o recorte: **1,04×**, quase empate;
  - a v0.4 com recorte é também **muito mais instável**, por exemplo p10–p90 de 0,124–0,314 no BR2, contra 0,086–0,092 da v0.3.2.
- **Mecanismo:** no teste, o recorte age em 0% dos passos. Ele age só no aquecimento do escalonador causal, onde |z| chega a 3·10⁴,
  e deixa um estado inicial ruim que persiste. Qual estatística carrega esse dano (pesos, decisões estruturais ou σ̂²) ainda não foi isolado.
- **Implicação:** o recorte (motivado pelo caso X3 de outliers) viola na prática o espírito do P6, porque depende de um escalonamento que, no aquecimento, não é confiável.
  Candidato para a v0.5: recortar só depois do aquecimento do escalonador, ou recortar em relação a uma escala robusta própria.
  Isso exigiria pré-registro e reavaliação interna (caso X3) e externa.
