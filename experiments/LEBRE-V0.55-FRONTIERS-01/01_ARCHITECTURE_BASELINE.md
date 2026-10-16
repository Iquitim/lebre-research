# 01 — Arquitetura atual da LEBRE (v0.54): auditoria de base

**Data:** 16/10/2026 · **Escopo:** Fase 0 do programa de investigação das quatro fronteiras (F1 a F4). Nenhuma medição
nova foi feita; todo número abaixo vem de um arquivo de resultado já registrado, indicado ao lado.
**Código auditado:** `experiments/LEBRE-V0.54-PROTO-01/lebre054/`, commit congelado `f9906c4` (idêntico a `lebre==0.3.0`,
cujos módulos têm a mesma árvore sintática). A pasta foi conferida contra o commit congelado antes da leitura (diferença
vazia).

**Rótulos usados em todos os documentos deste diretório:**
- **[FATO]** verificado no código ou num arquivo de resultado, com a referência;
- **[DEDUÇÃO]** consequência lógica ou matemática do código, sem medição;
- **[HIPÓTESE]** afirmação ainda não testada;
- **[RESULTADO]** medição já registrada (pré-registrada ou exploratória, como indicado).

## 1. Correções de premissa do enunciado

Três premissas do enunciado das fronteiras não conferem com o código. Elas mudam o desenho das investigações.

1. **[FATO] A M1 não é uma camada de memória.** A memória temporal é o especialista M (`_memory.py`), que fica *dentro*
   do núcleo e é combinado com o especialista estrutural S por média dinâmica de modelos (`_core.py`, `wS`). A M1
   (`_precision.py`) é um *especialista de precisão*: mínimos quadrados recursivos sobre as duas últimas observações do
   alvo e médias por banda de atraso das cinco entradas mais correlacionadas, combinado com a saída do núcleo por AdaHedge.
2. **[FATO] O núcleo usa NLMS de passo fixo μ = 0,05 em dois lugares:** na regressão estrutural S (`_core.py`,
   `g_ = MU * res / den`) e na memória M (`_memory.py`, `self.mu = 0.05`). Os desafiantes dos experimentos usam mínimos
   quadrados recursivos (RLS) sem esquecimento; a M1 usa RLS com esquecimento λ = 0,999.
3. **[FATO] A seleção estrutural não decide se uma entrada entra no modelo; decide se os seus atrasos entram.** O vetor
   base de S contém sempre o valor *atual* de todas as entradas e o passado padronizado do alvo
   (`xb = [1, x_t]`, `self.base`). Uma unidade aceita acrescenta blocos de médias por bandas de oitava de atraso
   (1, 2–3, 4–7, 8–15, 16–31) e, opcionalmente, um atraso de pico. Na F4, "LEBRE sem descoberta" ainda usa todas as
   entradas no atraso zero.

## 2. Mapa do fluxo causal de um passo

A ordem abaixo é a do código. Tudo o que é calculado em `predict` usa só informação anterior a yₜ.

```
predict(xₜ)                                           [antes de ver yₜ]
 ├─ padronização causal das entradas (média e variância exponenciais, taxa 1e-4)
 ├─ passado do alvo padronizado vira a entrada d+1; recorte |x| ≤ 8 (quarentena de L passos se recortar)
 ├─ histórico H (32 atrasos) e somas por banda atualizados
 ├─ memória:   m = y_{t−1} + w_M · φ            φ = [reversão à média, última diferença,
 │                                                  sazonal ingênuo, incremento de um ciclo, perfil por fase, (2º ciclo)]
 ├─ estrutura: s = base · [1, xₜ] + Σ_unidades ativas w_u · blocos_u
 ├─ núcleo:    L = m + wS · (s − m)              wS = logística(−0,5·D), D = soma descontada de (eₛ² − eₘ²)/σ²
 ├─ envelope:  L recortado a [mín − 0,5·amplitude, máx + 0,5·amplitude] dos valores observados (depois de 50)
 ├─ desafiantes em sombra (até 2): gₖ = s + aₖ − rₖ (adição, troca, divisão ou remoção)
 ├─ M1:        E = recorte(w_E · z, L ± 2·max(σ_L, piso));  L' = (1 − ω)·L + ω·E   (ω por AdaHedge; sombra de 100)
 │             com dormência (M5a): enquanto dorme, L' = L e E só é calculado a cada 8 alvos
 └─ M2:        R = referência trivial (zero, persistência ou sazonal ingênuo);
               H = AdaHedge(R, L'), W = troca única R → L', saída = s_P·W + (1 − s_P)·H  ((A,B)-Prod)

observe(yₜ)                                           [depois de ver yₜ]
 ├─ escala B = 2·max(σ̂_r, 0,1·desvio do alvo)        (σ̂_r: erro de s, só do passado)
 ├─ para cada desafiante: dₖ = min((y−s)²/B², 1) − min((y−gₖ)²/B², 1) − εₖ → e-process da hipótese
 │   (depois de 250 passos de aquecimento nas adições); o desafiante aprende por RLS o resíduo que explicaria
 ├─ NLMS de S sobre [xb, blocos ativos] com o resíduo y − s; contribuição média de cada unidade (EMA 0,01)
 ├─ triagem espalhada (cada entrada a cada 4 passos): correlações pré-branqueadas por banda; grupos de equivalentes
 │   (M5b: uma amostra a cada 31 passos, aplicada por linhas)
 ├─ D, wS, intervalo adaptativo de 90%, memória M (NLMS), envelope, estado residual (polos 0,8 e 0,95)
 ├─ a cada 10 passos: revisão dos experimentos (aceitar se log e ≥ log(1/αₖ); fechar se n ≥ 5.000 ou n ≥ 100 com soma ≤ 0),
 │   abertura de novos (remoção periódica a cada 2.000 passos por unidade; remoção disparada, M4; candidata da triagem)
 ├─ M1: AdaHedge, RLS a cada 8 alvos, nova seleção das entradas a cada 5.000; dormência e despertar (M5a)
 └─ M2: AdaHedge H, troca W, (A,B)-Prod; auditoria da porta (e-process com orçamento α = 0,01; só registra eventos)
```

## 3. Componentes, estados e regras de atualização

| Componente | Arquivo | Estado | Regra | Implementado / experimental |
|---|---|---|---|---|
| Memória M | `_memory.py` | pesos (2 a 7), buffer de 2·ciclo+2, perfil por fase | NLMS μ = 0,05 com pisos relativos | implementado |
| Estrutura S | `_core.py` | base (d+2), até 4 unidades ativas com pesos por banda | NLMS μ = 0,05 sobre base e blocos | implementado |
| Combinação M/S | `_core.py` | D, wS | média dinâmica, λ = 0,99, η = 0,5 | implementado |
| Experimentos | `_core.py`, `_engine.py` | até 2 em sombra; pesos e P do RLS | RLS sem esquecimento; aquecimento de 250 | implementado |
| e-process | `_engine.py` (`Hypothesis`) | S, V, n, média | mistura sub-exponencial unilateral com centragem previsível γ = min(média passada, 0) | implementado |
| Níveis | `_engine.py` (`ChangeEngine`) | n_hyp, n_accepted | α = 0,05; primeiros P = 2·(d+2) recebem α/(2P), depois 0,5·α·γₖ; vezes (aceitas + 1); teto 0,5 | implementado |
| Remoção disparada (M4) | `removal.py` | pico de contribuição por unidade | abre se contribuição < 0,5 × pico; hipótese nova; orçamento próprio | implementado (v0.54) |
| Equivalentes (M5b) | `screening.py` | matriz de covariância, vetor do ciclo | amostra a cada 31, por linhas | implementado (v0.54), só relatório |
| M1 | `_precision.py`, `dormancy.py` | RLS (k = 3 + 5·m), AdaHedge | λ = 0,999; dormência ω < 1e-3 por 2.000 alvos | implementado |
| M2 | `full.py`, `_aggregation.py` | AdaHedge, troca, Prod | sem horizonte | implementado |
| Ciclo como hipótese (M6) | `cycle.py` | — | — | **presente e desligado**; não faz parte da v0.54 |

**[FATO] Limites estruturais declarados no código:** no máximo 4 unidades ativas (`M_MAX = 4`); no máximo 2 experimentos
simultâneos (`M_SLOTS = 2`); um aquecimento de desafiante por vez; recarga de 2.000 passos antes de retestar uma unidade.

## 4. Governança estatística: o que o código garante e o que não garante

- **[FATO]** O incremento dₖ é previsível em tudo menos yₜ: s, gₖ e B são calculados antes de yₜ (`predict`), e o
  desafiante só aprende depois de dₖ ser registrado. O NLMS de S também só muda depois.
- **[DEDUÇÃO]** Por isso, a validade do e-process para a sua nula (a nula fraca de comparação de *métodos*: "em média
  sobre os passos testados, o desafiante não melhora a perda recortada de s em mais de ε") **não depende** de o NLMS
  estar adaptando. Ver `02_F1_SEQUENTIAL_VALIDITY.md`, §2.
- **[RESULTADO]** A interpretação estrutural dessa nula ("a entrada não acrescenta informação") falha quando o erro de
  estimação de s é previsível: nota formal `experiments/LEBRE-V0.52-EXT-01/MISADJUSTMENT_NOTE.md` (com μ = 0,1, 10 de 40
  séries nulas aceitaram estrutura falsa; com μ = 0,05, 0 de 40).
- **[RESULTADO]** Com substitutas correlacionadas, mudanças estruturalmente falsas ocorreram em até 20% das execuções de
  uma célula (FDR estimado 0,090 numa célula; `experiments/LEBRE-V0.52-EXT-02/FDR_SIM_REPORT.md`).
- **[FATO]** Há **três orçamentos de erro separados:** o principal (adições, trocas, divisões e remoções periódicas,
  α = 0,05), o das remoções disparadas (α = 0,05) e o da auditoria da porta da M2 (α = 0,01, que não decide a saída).
  A especificação v0.54 diz corretamente que as garantias são separadas. Ela não afirma um limite conjunto.
  **[DEDUÇÃO]** Pela soma dos orçamentos, o FDR conjunto das mudanças de estrutura fica limitado por 2α = 0,10, e não
  por α. Isso merece uma frase explícita na próxima revisão do texto (ver `07`).

## 5. Divergências entre especificação e implementação

| Item conferido | Especificação v0.54 | Código | Situação |
|---|---|---|---|
| μ do NLMS | 0,05 em S e na memória, "regime prático" | 0,05 | confere |
| Níveis tipo LOND fixados na criação | sim, decisões assíncronas | sim | confere; prova do caso assíncrono não está escrita (ver `02`, §3) |
| Orçamento próprio da remoção disparada | sim, garantia separada | sim | confere; FDR conjunto não declarado (§4) |
| M1: M_MAX = 5, bandas 0, 1, 2–3, 4–7, 8–15, λ = 0,999 | sim | sim | confere |
| Até dois experimentos em sombra | sim | `M_SLOTS = 2` | confere |
| Auditoria da porta não decide a saída | sim | `_mode` só escolhe qual hipótese é testada | confere |

Nenhuma divergência de comportamento foi encontrada nos itens conferidos. A conferência não foi exaustiva: cobriu os
parâmetros que as quatro fronteiras usam.

## 6. Linha de base registrada (sem medição nova)

| Medida | Valor | Fonte |
|---|---|---|
| v0.54 ÷ v0.53, erro, por família (93 séries reservadas) | 0,989 a 1,000; nenhuma piora | `LEBRE-V0.54-FINAL-01/FINAL_RESULTADO.md` |
| Custo v0.54 ÷ v0.53, mediana por série | 0,905 (IC 95% 0,857–0,932) | idem |
| Custo por passo v0.54 (média por série) | mediana 870, mín. 556, máx. 1.245 operações | `final_resultado.json` |
| Fração do custo gasta pela M1, mediana por série | **0,371** (mín. 0,09, máx. 0,45); bacias 0,40, prédios 0,17 | calculado de `final_resultado.json` em 16/10/2026 |
| v0.53 ÷ v0.52 (efeito conjunto de M1 + M2) | bacias 0,879; câmbio em nível 0,952; retornos 0,966; prédios 0,993; solar, eólica, carga 1,000 | `LEBRE-V0.53-FINAL-01/FINAL_RESULTADO.md` |
| Memória do estado estimada | 85.268 B | `LEBRE-V0.54-FINAL-01` |
| Pico por passo com 50 entradas | ≤ 1,054 × v0.53 (depois da errata 01) | `ERRATA_01.md` |
| Nulos (100 séries) | 0 entradas externas aceitas | `LEBRE-V0.54-AUDIT-01/RELATORIO_AUDITORIA.md`, T3 |
| Relação intermitente (blocos 7.500 / 10.000 / 15.000) | +10,0% / +5,5% / +4,6% de erro contra a v0.53 | idem, T5 |
| Testes de estrutura × tudo ligado (v0.52, exploratório) | 0,988 [0,970; 1,006] | `LEBRE-V0.52-EXT-02/ABL_ALLON_REPORT.md` |

**[FATO] Lacuna:** o efeito *isolado* da M1 (sem a M2) não foi medido em nenhuma avaliação final. As avaliações dão o
efeito conjunto de M1 + M2.

**Reprodução:** `python scripts/verify_integrity.py` (integridade de todos os arquivos congelados); a avaliação final da
v0.54 é reproduzida por `experiments/LEBRE-V0.54-FINAL-01/final_run.py` com os dados listados em
`docs/research/ARTIFACTS_MANIFEST.tsv`. Ambiente de referência: Windows, CPython 3.11, NumPy 2.2.5, pandas 2.2.3.

## 7. Gate 0

Toda afirmação sobre o funcionamento da LEBRE nos documentos 02 a 08 remete a um item deste documento ou a um arquivo
de código ou de resultado. As três correções de premissa do §1 mudam o desenho de F2 e F4.
