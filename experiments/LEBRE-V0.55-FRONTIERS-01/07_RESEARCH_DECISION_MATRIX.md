# 07 — Matriz de decisão

Síntese dos documentos 01 a 06. Nenhuma classificação abaixo se apoia em medição nova. As que dependem de dedução estão
marcadas assim e exigem prova escrita ou medição antes de virar mudança no núcleo.

## 1. Por hipótese

| Hipótese | Evidência existente | Classe | Recomendação |
|---|---|---|---|
| H1.1 o e-process é válido sob NLMS adaptativo (nula testada) | dedução completa no `02`, §2 a §3, mais o comentário do código | **SUPPORTED** (dedução) | REQUIRE_FORMAL_PROOF |
| H1.2 a interpretação estrutural falha em condições específicas | nota formal EXT-01 (μ = 0,1: 10/40); M3 (5/11); iscas EXT-02 (até 20%) | **SUPPORTED** (resultados registrados) | REJECT como fronteira nova (já documentada); a correção vai pela F2 |
| H1.3 construção alternativa com validade e mais poder | nenhuma | **INCONCLUSIVE** | DEFER |
| H2.1 redundância mensurável entre componentes | nenhuma ablação marginal | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H2.2 aprender sobre o resíduo é mais eficiente | nenhuma | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H2.3 a cascata reduz custo | dedução: mesmo número de parâmetros | **NOT_SUPPORTED** (dedução) | REJECT (para a cascata em si) |
| H2.4 a M1 pode ser removida ou simplificada | efeito isolado nunca medido; M1 + M2 = 0,879 em bacias; M1 = 37% do custo | **NOT_SUPPORTED** com a evidência atual | REQUIRE_ADDITIONAL_EXPERIMENTS (ablações D e C) |
| H2.5 a cascata reduz descobertas espúrias em séries integradas | defeito medido; mecanismo deduzido; correção não testada | **PRELIMINARY_SUPPORT** | **ADVANCE_TO_PROTOTYPE** |
| H3.1 warm start acelera a redescoberta | atraso medido (675–920 passos); parte de aprendizado não separada | **PRELIMINARY_SUPPORT** | REQUIRE_ADDITIONAL_EXPERIMENTS (diagnóstico), depois ADVANCE_TO_PROTOTYPE |
| H3.2 hibernação a custo controlado | custo deduzido pequeno | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H3.3 warm start direcional sem mais falsas | validade preservada por dedução se a evidência for nova | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H3.4 riqueza estatística com estado | teoria ativa, nenhuma para este procedimento | **INCONCLUSIVE** | REQUIRE_FORMAL_PROOF; DEFER |
| F3-E reativação completa sem teste | muda a nula; viola o princípio | **THEORETICAL_BLOCKER** | REJECT |
| H4.1 seleção supera tudo ligado em alta dimensão | neutra em dimensão baixa; nada acima de d ≈ 8 | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.2 FDR estável em d | 0/400 (d = 4); 0/100 (auditoria) | **INCONCLUSIVE** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.3 atraso de detecção ~ log d | dedução | **PRELIMINARY_SUPPORT** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.4 custo segue a contagem | d = 50 medido | **PRELIMINARY_SUPPORT** | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H4.5 substitutas crescem com d | nenhuma | **INCONCLUSIVE** | descritiva |

## 2. Por fronteira

Escala: 1 = baixo, 3 = alto. "Risco de regressão" alto é ruim.

| Critério | F1 | F2 | F3 | F4 |
|---|---|---|---|---|
| Relevância científica | 2 | 3 | 2 | 2 |
| Evidência de necessidade real | 1 (validade); 3 (interpretação, já coberta) | **3** (M3 medido) | **3** (T5 medido) | 1 |
| Potencial de originalidade | 1 | 1–2 | 1–2 | 1 |
| Potencial de melhoria preditiva | 0 | 2 (níveis; risco em bacias) | 2 (só em séries intermitentes) | ? |
| Potencial de redução de custo | 0 | 0 (cascata); 2 (se a M1 sair) | 0 | 0 (o custo cresce com d) |
| Dificuldade matemática | 2 (prova curta) | 1 | 1 (warm start); 3 (riqueza) | 1 |
| Complexidade de implementação | 0 | 3 (muda o núcleo) | 1 (A′, B); 2 (C, D) | 2 (harness, baselines) |
| Risco de regressão | 0 | **3** (todas as famílias) | 1 | 0 (não muda o núcleo) |
| Qualidade da evidência atual | alta (dedução + resultados) | média (exploração + mecanismo) | alta (auditoria pré-planejada) | baixa |

## 3. Observações que não são hipóteses do enunciado, mas saíram da auditoria

1. **FDR conjunto = 2α.** As mudanças de estrutura têm dois orçamentos de α = 0,05 (principal e remoção disparada).
   A especificação diz que as garantias são separadas. Falta a frase de que o limite conjunto é 2α. Correção de texto na
   próxima revisão; nenhum código muda.
2. **A M1 seleciona entradas sem teste.** A seleção da M1 é por correlação (top 5), fora do regime de evidência. Não é
   um defeito declarado. É uma assimetria a registrar, e conversa com H2.4.
3. **Lista de eventos sem limite** (já registrada na auditoria, T9), relevante para F3 se a hibernação guardar
   histórico.
