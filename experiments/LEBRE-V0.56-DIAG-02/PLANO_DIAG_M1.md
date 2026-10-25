# LEBRE v0.56 — Diagnóstico da M1 nas bacias: plano (commitado antes de qualquer medição)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DIAG-02` · **Natureza:** diagnóstico **exploratório**, complemento de
`LEBRE-V0.56-DIAG-01`, nas mesmas reservas já consumidas. Nenhuma mudança de desenho é feita aqui.

## 1. Pergunta

O `DIAG-01` mostrou que a vantagem do ARX-RLS sobre a v0.55 nas bacias (1,124 em D-A, 1,053 em D-B) vem da adaptação
de segunda ordem e de uma dinâmica autorregressiva forte. Mas a camada M1 da LEBRE **já é** um ARX ajustado por RLS:
constante, y(t−1) e y(t−2) e médias das bandas de defasagem [0], [1], [2–3], [4–7] e [8–15] das até cinco entradas mais
correlacionadas com o alvo, combinada com a previsão do núcleo por AdaHedge.

**Pergunta:** que limitação da M1, ou da forma como ela entra na saída, impede a LEBRE de chegar perto do ARX-RLS?

Limitações identificadas no código congelado, antes de medir:
1. **Frequência do RLS:** a regressão é atualizada só a cada 8 alvos aprendidos (EVERY = 8); a M1 aprende com 1/8 dos
   dias. Isso combina com a diferença ser maior no início das séries.
2. **Recorte:** a previsão E é limitada a L ± 2·max(σ̂_L, piso), em torno da previsão do núcleo, o que pode cortar
   respostas à chuva (onde está mais da metade da diferença).
3. **Ordem autorregressiva:** duas defasagens do alvo (o ARX usa três).
4. **Dormência** (v0.54): a M1 pode dormir enquanto o seu peso é desprezível.
5. **Combinações:** a mistura com o núcleo (AdaHedge, sombra de 100 atualizações, reinício a cada troca de entradas) e
   a M2, que parte da persistência.

## 2. Dados

Os mesmos conjuntos do `DIAG-01`, com o mesmo carregador e as mesmas travas: **D-A** (posições 140–169) para as medições,
**D-B** (110–139) só para a replicação; posições ≥ 170 recusadas. R0 (ARX-RLS) vem das previsões já gravadas pelo
`DIAG-01`, sem rodar de novo.

## 3. Medições em D-A (execução única)

As variantes trocam só a M1 da v0.55 por uma subclasse de diagnóstico (`diag_m1.py`) com quatro chaves; o resto é o
código congelado (commit `b0522a0`). A subclasse grava, a cada passo: a previsão do núcleo L, E antes e depois do
recorte, o peso ω da M1, a combinação L' e a saída.

| Código | Variante | Limitação removida |
|---|---|---|
| M0 | v0.55 canônica (subclasse com as chaves no padrão) | — |
| M1 | RLS da M1 a cada alvo aprendido (em vez de a cada 8) | 1 |
| M2 | sem o recorte de E | 2 |
| M3 | três defasagens do alvo em z | 3 |
| M4 | sem dormência (a M1 da v0.53) | 4 |
| M5 | M1 + M2 + M3 juntas | 1 a 3 |

A triagem e a escolha das entradas da M1 continuam a cada 8 alvos em todas as variantes (só a regressão muda em M1).

**Teste de fumaça, antes da execução:** M0 tem de dar previsões idênticas, bit a bit, às da v0.55 numa bacia de fumaça;
na execução, M0 tem de reproduzir bit a bit as previsões L0 gravadas pelo `DIAG-01` em cada bacia de D-A.

**Previsões internas** (gravadas dentro das execuções, sem rodar nada a mais):
- E livre: E antes do recorte, onde existe, em M0 e em M5;
- L' (núcleo + M1) e a saída (depois da M2), em M0.

## 4. Estatística

A mesma do `DIAG-01` (`reps` de `comp_analise.py`, blocos de 30 dias, 2.000 réplicas, média do log da razão por série,
janela de 30% da série até o fim, máscara comum aos modelos comparados). Sementes 2026102802 (D-A) e 2026102803 (D-B),
conferidas como não usadas em 25/10/2026. Holm sobre a família de contrastes M0 ÷ Mk, k = 1 a 5.

## 5. Regras de leitura (fixadas antes)

G = log(MSE M0 ÷ MSE R0), em média geométrica sobre as séries.

1. **Limitação que explica.** A limitação k explica parte substancial se log(MSE M0 ÷ MSE Mk) ≥ 0,5·G, o contraste for
   significativo por Holm e o sinal for de melhora.
2. **Descritivos, fora de Holm:**
   - E livre (M0 e M5) ÷ R0: o quanto o especialista, sozinho, fica perto do ARX-RLS;
   - L' ÷ núcleo (o ganho da M1) e saída ÷ L' (o efeito da M2);
   - fração dos passos em que E é recortado, no total e nos dias de chuva (mesma definição de regime do `DIAG-01`);
   - fração dos passos com a M1 dormente;
   - custo por passo de cada variante (M1 aumenta o custo; isso é registrado, não decide).
3. **Replicação em D-B:** só as variantes classificadas pela regra 1 e M5, mais M0. A classificação se mantém se o efeito
   tiver o mesmo sinal, IC acima de zero e pelo menos metade da magnitude de D-A.
4. **Saída:** um relatório que diga quais limitações explicam e quanto da diferença para o ARX-RLS sobra com todas
   removidas (M5 ÷ R0).

## 6. O que esta etapa não faz

Não muda a LEBRE nem a biblioteca; não usa dados novos; não faz afirmação confirmatória. Uma variante que ajude aqui
ainda precisa passar no banco de todas as famílias (as bacias não são as únicas) e numa avaliação final em dados novos.

## 7. Arquivos

Este plano, `diag_m1.py` (subclasse, variantes e teste de fumaça), `diag_m1_run.py`, `diag_m1_analise.py`,
`RUN_NOTAS.md`, `DIAG_M1_RESULTADO.md` e `.json`. Previsões em `preds/` (fora do git).
