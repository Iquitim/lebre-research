# 04 — F3: FDR com estado e memória de regimes intermitentes

**Questão.** A LEBRE pode preservar conhecimento sobre relações que somem e voltam, e acelerar a sua recuperação, sem
comprometer o controle de mudanças falsas?

**Resposta curta.**
- **[RESULTADO]** O problema é real e está medido: +4,6% a +10% de erro quando uma relação some por mais de ~5.200
  passos e volta. É o limite declarado na errata 01 da v0.54.
- **[DEDUÇÃO]** Reaproveitar *parâmetros* (warm start) não ameaça a validade, porque o desafiante só precisa ser
  previsível.
- **[DEDUÇÃO]** Reaproveitar *evidência* muda a pergunta testada. Uma reativação sem novo teste viola o princípio da
  arquitetura.

Rótulos como em `01_ARCHITECTURE_BASELINE.md`.

## 1. O ciclo de vida atual de uma relação intermitente

| Fase | O que o código faz | Fonte |
|---|---|---|
| 1. Surge | a triagem (correlações pré-branqueadas, média exponencial w = 0,02 a cada 4 passos) passa do limiar; um desafiante RLS começa de pesos zero e P = 10·I; 250 passos de aquecimento sem evidência; depois, e-process até log(1/αⱼ) | `_core.py` (`_fill`, `_open`, `observe`) |
| 2. Ativa | pesos por banda aprendidos por NLMS; contribuição média (EMA 0,01) | `_core.py` |
| 3. Enfraquece | o pico de contribuição desde a aceitação é guardado | `removal.py` (`_fill`) |
| 4. Some | contribuição < 0,5 × pico → teste de remoção **disparado**, com hipótese nova e orçamento próprio; aceita só depois de 5.000 passos de evidência | `removal.py` |
| 5. Ausente | **os pesos são apagados** (`del self.active[...]`, `contrib_ema.pop`); a hipótese de adição tinha sido consumida na aceitação | `_core.py` (`_accept`, `consume`) |
| 6. Volta igual | redescoberta do zero: triagem, desafiante novo de pesos zero, 250 de aquecimento, **hipótese nova** com índice maior (nível menor), e-process do zero | `_core.py` |
| 7. Volta diferente | idem; nada do antigo é usado | — |

**[RESULTADO]** (`LEBRE-V0.54-AUDIT-01/RELATORIO_AUDITORIA.md`, T5):
- as remoções caem, em mediana, entre 5.155 e 5.205 passos depois do início do bloco desligado;
- a readição leva em mediana 675 a 920 passos, e até 2.250;
- blocos de até 5.000 passos não disparam remoção;
- efeito no erro: +10,0% (blocos de 7.500), +5,5% (10.000), +4,6% (15.000), contra a v0.53, que não remove.

## 2. Cinco memórias que não podem ser confundidas

| Memória | Hoje | Reaproveitar afeta a validade? |
|---|---|---|
| **a. Parâmetros** (pesos por banda, atraso de pico) | apagados na remoção | **[DEDUÇÃO] Não.** Qualquer inicialização ℱₜ₋₁-mensurável do desafiante mantém o e-process válido (`02`, §2): o argumento só pede que gₜ seja previsível |
| **b. Estados internos** (P do RLS, somas por banda) | apagados; somas por banda recalculadas | **Não**, pela mesma razão |
| **c. Direção e intensidade** | apagadas | **Não**, se usadas só para iniciar o desafiante ou priorizar a triagem |
| **d. Evidência acumulada** | adição: hipótese consumida na aceitação; remoção periódica: **persistente** (acumula todos os episódios desde a aceitação); remoção disparada: nova por episódio | **Sim.** Ver §3 |
| **e. Riqueza estatística** | e-LOND: o nível de uma hipótese nova cresce com o número de aceitações anteriores, (R + 1) | só se a regra mudar. Ver §4 |

**Reutilização computacional ≠ reutilização de evidência.** As memórias a, b e c mudam *o que o desafiante sabe no
início*. A memória d muda *o que conta como prova*.

## 3. Por que reaproveitar evidência muda a pergunta

**[DEDUÇÃO]** Uma hipótese persistente é válida para a sua nula fraca: "em média, *sobre todos os passos testados de
todos os episódios*, a mudança não melhora". Reabrir a hipótese antiga de adição, sem consumi-la, seria válido para essa
média. Mas a média mistura o regime de agora com os anteriores. É exatamente o defeito que motivou a M4: na remoção
periódica, a evidência de antes da troca de regime "pesa para sempre" (docstring de `removal.py`).

Portanto:
- **reativação completa sem teste (opção E):** viola o princípio "mudar só com evidência". Não há justificativa
  matemática para a sua validade como decisão sobre o regime atual. **Recomendação: REJECT**, salvo prova nova;
- **reaproveitar evidência antiga como valor inicial do e-process:** válido só para a nula da média sobre regimes, que
  não é a pergunta. Não recomendado;
- **evidência nova com prior informativo** (por exemplo, um nível maior para hipóteses de readição): mexe no orçamento.
  Ver §4.

## 4. Riqueza e orçamento: o que exigiria prova nova

- **[FATO]** Cada aceitação, inclusive de remoção disparada e de readição, aumenta R e, com ele, o nível das hipóteses
  criadas depois.
- **[DEDUÇÃO]** Isso não quebra o FDR: remoções corretas e readições corretas são descobertas verdadeiras, e o argumento
  de `02`, §3, vale para qualquer R.
- **[HIPÓTESE]** Uma relação que oscila gera muitas aceitações verdadeiras e eleva os níveis das hipóteses futuras de
  *todas* as unidades. É um efeito de "riqueza acumulada" a medir (falsas aceitações em outras unidades depois de muitas
  oscilações).
- **[DEDUÇÃO] Qualquer regra nova de riqueza exige prova própria:** níveis diferentes para readições, reciclagem de
  α, e-closure online, ou hipóteses "setwise persistent" com FDR (de Heide 2026, arXiv 2608.09927; arXiv 2603.24792;
  alpha-investing sempre válido de Yao, Gang & Sun, arXiv 2512.12244). As garantias desses trabalhos valem para os
  procedimentos deles, não para uma adaptação da LEBRE.

## 5. Hipóteses e protocolo

| Hipótese | Resultado primário | Aceitação (rascunho) |
|---|---|---|
| **H3.1** warm start reduz o tempo de redescoberta | mediana de passos entre a volta da relação e a readição | redução ≥ 30% contra A, com IC pareado |
| **H3.2** hibernação preserva conhecimento a custo controlado | erro nos blocos ligados depois da volta; bytes guardados por unidade removida | erro B ou C ÷ A < 1 nos blocos de 7.500–15.000; custo de memória ≤ 1% do estado (85 KB) |
| **H3.3** warm start direcional sem aumentar falsas descobertas | readições falsas (unidade readicionada enquanto a relação continua ausente) e falsas aceitações em nulos e iscas | readições falsas: limite superior do IC ≤ o de A; nulos: 0 aceitações com limite superior do IC ≤ 0,05 |
| **H3.4** riqueza com estado melhora o poder | poder de detecção sob FDR ≤ α | só depois de uma prova escrita (REQUIRE_FORMAL_PROOF) |

**Variantes** (montadas na pasta do experimento, sem editar o núcleo):
- **A.** Descarte integral e reaprendizagem (v0.54).
- **B.** Hibernação só dos pesos: ao remover, guardar (unidade, bandas, pesos, atraso de pico); ao reabrir o desafiante
  da mesma unidade, iniciar w com eles.
- **C.** Hibernação de pesos e de P do RLS.
- **D.** Warm start direcional com revalidação independente: B, mais prioridade na triagem para a unidade hibernada.
  Sempre com hipótese nova e e-process do zero.
- **E.** Reativação completa: não executada (§3).
- **A′. Simplificação a testar primeiro:** duração mínima de remoção ligada ao histórico da unidade (por exemplo, a
  duração mínima dobra a cada remoção da mesma unidade). Nenhum estado novo além de um contador. Pela diretriz, uma
  simplificação é investigada antes de um mecanismo novo.

**Variações** (grade fatorial reduzida):
- duração da ausência: 2.500, 5.000, 7.500, 10.000 e 15.000 passos;
- recorrências: 1, 3 e 6;
- intensidade: 0,1, 0,2 e 0,4 desvio;
- hipóteses concorrentes: 0, 2 e 6 entradas com relação própria;
- semelhança da volta: mesma direção e intensidade; mesma direção com a metade da intensidade; direção oposta.

**Diagnóstico prévio, barato (sem mudar nada):** decompor os 675 a 920 passos da readição em triagem, espera por vaga,
aquecimento (250) e acumulação de evidência, instrumentando a v0.54 nos cenários do T5. Se a acumulação de evidência
dominar, o warm start ajuda pouco: ele encurta o aprendizado, não o limiar.

**Métricas:** tempo de redescoberta, erro acumulado na recuperação, retenção, readições falsas, FDR empírico (com IC),
poder, bytes guardados, estabilidade dos níveis (R ao longo do tempo).

## 6. Decisão

| Hipótese | Classe | Recomendação |
|---|---|---|
| H3.1 warm start acelera a redescoberta | **PRELIMINARY_SUPPORT**: o atraso existe e tem uma parte de aprendizado (aquecimento de 250 e pesos do zero); o tamanho dessa parte não foi medido | REQUIRE_ADDITIONAL_EXPERIMENTS (diagnóstico prévio), depois ADVANCE_TO_PROTOTYPE |
| H3.2 hibernação com custo controlado | **INCONCLUSIVE**; custo de memória deduzido como pequeno (até 4 unidades × ≤ 7 pesos, mais P se C) | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H3.3 direcional sem mais falsas descobertas | **INCONCLUSIVE**; validade preservada por dedução se a evidência for nova | REQUIRE_ADDITIONAL_EXPERIMENTS |
| H3.4 riqueza com estado | **INCONCLUSIVE**; base teórica existe em 2025–2026, mas não para este procedimento | REQUIRE_FORMAL_PROOF; DEFER (linha teórica independente) |
| Opção E, reativação sem teste | **THEORETICAL_BLOCKER** para a interpretação no regime atual | REJECT |
