# LEBRE v0.55 — Registro formal de congelamento

**Arquitetura:** LEBRE (Lifecycle-governed Evidence-Based Resource Evolution)
**Versão:** 0.55 (núcleo ancorado: testes de estrutura contra a previsão do núcleo, estrutura de inovação, portão suave
pela triagem e piso de escala previsível, sobre a v0.54)
**Status:** `PROMOTED_RESEARCH_VERSION_WITH_SCOPE_LIMITS`
**Etapa:** `LEBRE-V0.55-FREEZE-01`
**Data:** 17 de outubro de 2026

**Código congelado:** lebre-research, commit `b0522a0`, pasta `experiments/LEBRE-V0.55-PROTO-01`, variante `B10`. A
pasta está inalterada desde esse commit.

**Relação com as versões anteriores:**
- a v0.1 continua sendo a **referência canônica** do projeto;
- a v0.51 a v0.54 continuam **congeladas e inalteradas** (o verificador `scripts/verify_integrity.py` passa em todos os
  manifestos em 17/10/2026);
- dentro do protótipo, a v0.54 está como cópia byte a byte de `f9906c4` (`SHA256_COPIAS.txt`).

A v0.55 foi **promovida por uma regra pré-registrada e vinculante**, numa execução única em reserva nova
(`experiments/LEBRE-V0.55-FINAL-01/PREREG_V055_FINAL.md`).

---

## 1. Princípio que orienta a versão

A LEBRE aceita estrutura só com evidência sempre válida. A v0.55 muda **a pergunta** que essa evidência responde.
- Uma entrada externa passa a ser aceita só se melhorar **a previsão do núcleo**, que já contém a memória do próprio
  alvo, e não apenas a estrutura de nível.
- O que a evidência aceita passa a chegar à previsão também em séries integradas, por uma estrutura de inovação.

## 2. O que está congelado

| Item | Conteúdo |
|---|---|
| **Código** | `experiments/LEBRE-V0.55-PROTO-01/lebre055/`: a v0.54 como cópia byte a byte de `f9906c4`; `anchored.py` (todas as alavancas, rascunhos 0 a 7); `model055.py` (variantes; a **v0.55 é `B10`**). 41 testes, entre eles a identidade bit a bit da reescrita (variante A0) com a v0.54. |
| **Programa de pesquisa** | `experiments/LEBRE-V0.55-FRONTIERS-01/`: auditoria da v0.54, as quatro fronteiras, literatura, matriz de decisão, roteiro. |
| **Desenho e teoria** | `experiments/LEBRE-V0.55-DESIGN-NOTE-01/`: nota de desenho com os adendos 01 a 07, Nota formal F1 (validade dos e-processes com qualquer aprendiz previsível; e-LOND assíncrono; 2α conjunto), a **errata 01** da nota e a conferência numérica das desigualdades. |
| **Validação real** | `experiments/LEBRE-V0.55-DATA-01/` (sorteio) e `experiments/LEBRE-V0.55-VAL-01/` (pré-registro e resultado). |
| **Reserva final** | `experiments/LEBRE-V0.55-DATA-02/`: regras (commitadas antes de qualquer download), scripts de cópia e sorteio, SHA-256 dos 37 arquivos brutos, `SPLIT_V055.json`. A reserva foi consumida. |
| **Avaliação final** | `experiments/LEBRE-V0.55-FINAL-01/`: pré-registro, scripts, notas, resultado. |
| **Comparação externa** | `experiments/LEBRE-V0.55-COMP-01/`: plano, scripts, notas (incluindo a troca para GPU), resultado. É só referência. |

Lista completa com SHA-256: `LEBRE_v0.55_SHA256SUMS.txt` (todos os arquivos rastreados dessas oito pastas, 64).

O desenvolvimento está no LEBRE Lab (`Iquitim/lebre-lab`, `analises/`), com plano e resultado de cada rodada:
- D1 a D4, negativas;
- o banco fixo `BANCO_V055_*`, com a rodada D5;
- a confirmação C1.

## 3. Configuração canônica

```python
Lebre055(d, season=s, season2=s2, reference=R, variant="B10")
# B10 = a v0.54 canônica (M5a, M5b, M4) com REF_SPLIT, INNOV, SCREEN_CORE_INT, INN_FROM_OWN_RESIDUAL,
#       PRED_FLOOR e DIFF_FLOOR ligadas (ANCHOR, SLOW, REF_CORE e GATE_INTERNAL desligadas)
```

R = `"zero"`, `"seasonal"` ou `"persistence"`, como na v0.54.

| Mudança (chave) | O que faz |
|---|---|
| REF_SPLIT | Unidades **externas** (entradas e as suas divisões) são testadas contra a previsão do núcleo, R = m + wS·(s − m); a remoção desconta a contribuição da unidade na previsão do núcleo. Unidades **internas** (passado do alvo, estado residual e as suas divisões) são testadas contra a estrutura de nível s, como na v0.54. |
| INNOV | Estrutura de inovação ŝ_Δ: prevê r = y − m com as mesmas unidades aceitas e os mesmos atributos, pesos próprios, NLMS μ = 0,05. Combinação aninhada: L₁ = m + wS·(s − m) e L = L₁ + wI·((m + ŝ_Δ) − L₁), com wI pela mesma média dinâmica (λ = 0,99, η = 0,5, a cada 8 passos). A contribuição descontada de uma unidade externa é (1 − wI)·wS·c_s + wI·c_Δ. |
| SCREEN_CORE_INT | **Portão suave pela triagem:** a triagem das unidades internas usa o resíduo da previsão do núcleo, y − L. Uma unidade interna só ganha vaga se explica o que o núcleo ainda erra. Não há limiar novo. |
| INN_FROM_OWN_RESIDUAL | Cada estrutura recebe pesos do desafiante só se ele aprendeu o resíduo dela. As internas entram na inovação com peso zero (divisões: as duas metades com o peso da mãe). |
| PRED_FLOOR, DIFF_FLOOR | Piso da escala dos testes calculado **antes** de ver yₜ, igual a 0,1·√(min(variância do nível, variância de Δy)). |

## 4. Evidência que acompanha o congelamento

**Avaliação final pré-registrada e vinculante** (`FINAL_RESULTADO.md`; 84 séries reservadas: 30 bacias CAMELS-BR, 30
medidores BDG2, 8 usinas eólicas e 8 solares do ONS, 8 taxas do euro do BCE):

| Critério | Resultado |
|---|---|
| R1 sem piora por família (limite superior ≤ 1,02 contra a v0.54) | bacias 1,008 (até 1,014); prédios 0,998; eólica 0,994; solar 0,993; níveis 1,000 |
| R2 controle negativo: placebos (passeios aleatórios) na estrutura final | **0/84** na v0.55, contra 4/84 na v0.54 |
| R3 falha numérica | nenhuma |
| R4 custo | mediana 0,989 da v0.54 |
| R5 memória estimada | 86.180 B, contra o limite de 131.072 B |

**Desenvolvimento e confirmação** (LEBRE Lab, banco fixo de 23 células com critérios fixos):
- a rodada D5 e a confirmação **C1**, com sementes nunca usadas, passaram;
- espúrias em séries integradas: 0 (v0.54: 22/60 e 22/40);
- integradas com entrada verdadeira: 0,913 (0,907–0,918).

**Validação real** (`VAL_RESULTADO.md`): bacias 1,003; prédios 0,993.

**Comparação externa, só referência** (`COMP_RESULTADO.md`, correção de Holm):
- a v0.55 é melhor que o SARIMAX-X em todas as famílias;
- o Chronos-2 com covariáveis, ~10⁶ vezes mais caro, é melhor em prédios, solar e eólica;
- **um ARX com RLS da mesma classe de custo é melhor nas bacias** (11 a 13%);
- nos níveis, a v0.55 empata com a persistência, e todos os outros modelos perdem para ela.

## 5. Limites declarados

1. **Bacias:** piora pequena e significativa contra a v0.54 (0,8%, maior no início das séries), e um ARX com RLS do
   mesmo custo é melhor.
2. **Séries integradas reais:** o ganho demonstrado em sintéticos não apareceu nos níveis do BCE (1,000).
3. **Relações reais fracas** são registradas como estrutura mais devagar.
4. **Nota formal F1:** prova com autor único, ainda sem conferência independente. A errata 01 registra que, no núcleo
   congelado da v0.54, a escala dos testes não é estritamente previsível; a v0.55 corrige isso.
5. **FDR estrutural:** controle empírico. O limite conjunto teórico é 2α para os dois motores de mudança estrutural.
6. **Memória e custo:** estimados pelo modelo analítico, não medidos em microcontrolador. Só previsão de um passo.
7. **Nenhum componente é original;** a contribuição é de integração e empírica.
