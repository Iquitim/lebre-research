# LEBRE v0.52 — Contrato de complexidade (rascunho para o pré-registro)

**Data:** 26/09/2026 · **Base:** medição em `COST_GRID.csv` (8 mil passos por célula; d = 1–6; sem período ou s = 24; m = 1–4 vagas).
**Princípio:** o compromisso é com **como o custo escala**, e não com um número fixo. O custo por passo **não cresce com o tempo** e cresce de forma **conhecida** com o tamanho do problema. É a métrica central da linha de pesquisa: desempenho por unidade de computação (ver memória do projeto sobre eficiência).

## 1. Lei de custo

\[
\text{FP/passo} \;\approx\; 63 \;+\; 17{,}5\,d \;+\; 26\,\mathbb 1[s=24] \;+\; 20\,m
\]

Ajuste por mínimos quadrados na grade medida; erro máximo de ~31 FP, porque as vagas nem sempre estão todas ocupadas e há interação fraca entre d e m.

| Componente | FP/passo (média da grade) | Escala com |
|---|---|---|
| Estrutura (base densa, átomos ativos, filtros de 2 polos) | ~62 | d (base e filtros), ≤ 4 átomos |
| Memória | ~36 com s = 24; menos sem período | s (features sazonais) |
| Experimentos (vagas) | ~27 (m = 1) → ~81 (m = 4) | m |
| Controle (combinador, intervalo, ranking amortizado) | ~18 | quase constante |
| Motor de evidência (log-e) | ~2–7 | m |
| Triagem | 8 | nº de sondas (2) |

**Memória de estado:** O(d·L + s + |dicionário|), sem crescimento com o tempo. A medição em bytes fica para a etapa de hardware.

## 2. Custo medido (FP/passo)

| d | s | m = 1 | m = 2 | m = 3 | m = 4 |
|---|---|---|---|---|---|
| 1 | — | 109 | 124 | 130 | 128 |
| 1 | 24 | 135 | 152 | 155 | 160 |
| 2 | — | 124 | 148 | 159 | 166 |
| 2 | 24 | 149 | 175 | 191 | 194 |
| 3 | — | 137 | 165 | 183 | 198 |
| 3 | 24 | 159 | 189 | 207 | 222 |
| 5 | — | 158 | 189 | 215 | 235 |
| 6 | 24 | 196 | 225 | 254 | 277 |

## 3. Perfis declarados

| Perfil | Configuração | Garantia de custo | Uso |
|---|---|---|---|
| **Embarcado** | m = 1; d ≤ 3 sem período, ou d ≤ 2 com s ≤ 24 | **≤ 150 FP/passo** | microcontrolador; será medido em hardware |
| **Padrão** | m = 2 | pela lei acima (~124–225 FP para d ≤ 6) | avaliação principal |
| **Fronteira** | m = 1…4 | pela lei acima | curva precisão × computação (resultado central) |

## 4. O que se reporta em toda avaliação

1. **Precisão × computação:** NMSE contra FP/passo para cada perfil e para cada comparador, no mesmo gráfico.
2. **Latência de descoberta × vagas:** a relação latência ∝ p/m, medida.
3. **Custo real por tarefa:** média e pico.

## 5. Observações honestas

- O perfil embarcado com m = 1 **descobre mais devagar** (fronteira no `DEV_LOG.md`: B2 com 2,2/3 atrasos, contra 3/3 com m = 2).
- O limite antigo de 150 FP com d = 5 da v0.51 não é compatível com esta arquitetura sem retirar capacidades. A escolha de trocar o teto fixo por uma lei de custo foi tomada com o responsável pelo projeto (26/09/2026).
