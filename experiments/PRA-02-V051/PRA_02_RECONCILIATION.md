# PRA-02 — Reconciliação com a auditoria independente

**Data:** 25/09/2026
**Entradas:**
- PRA-02 interna (`PRA_02_REPORT.md`);
- auditoria independente feita por outro modelo com o prompt cego `PROMPT_PRIOR_ART_INDEPENDENTE.md`, que não recebeu as referências nem as conclusões da PRA-02.

**Verificação:** as citações novas mais críticas foram conferidas por busca (§4). O comportamento de código citado foi conferido em `lebre_s051.py`.

## 1. Onde as duas concordam

- Nenhum componente isolado é novo. A integração é, no máximo, `POSSIBLY_DISTINCT`, de forma estreita.
- O controle de erro "por episódio" é insuficiente; a literatura de testes múltiplos online com e-valores está à frente (A9 = `KNOWN`).
- Precedentes comuns: alpha-investing (Zhou et al. 2005), AMRules, Lindon et al. (JASA 2026), de Heide (2026), DMA (Raftery et al. 2010), ARX-Laguerre, CUSUM (Page 1954), TinyML.
- `NOVELTY_CLAIM_READY = NO`.

## 2. Onde a auditoria independente foi mais severa (e tem razão)

| Ponto | PRA-02 | Independente | Posição reconciliada |
|---|---|---|---|
| Zhou et al. 2005 e AMRules | ALTA | **CRÍTICA** | Aceito: qualquer frase do tipo "seleção estrutural online com controle estatístico" é antecipada. |
| Ciclo sombra → promoção → remoção | "distinção real, mas estreita" | **KNOWN** (CVFDT 2001, AMRules, M-RAN) | Aceito: o padrão arquitetural é antigo; só o critério (teste sempre válido) muda. |
| Aluguel de parcimônia | variante de CUSUM | Ungar et al. 2005 (IIC, penalidade adaptativa por codificação); Yamanishi & Miyaguchi 2016 (MDL + mudança) | Aceito: o princípio é conhecido; a fórmula exata não foi encontrada. |
| Banco de polos | Laguerre/Kautz | Também estimação adaptativa por múltiplos modelos (Magill 1965) e patentes de bancos de Kalman | Aceito: o banco de polos não é onde está a novidade. |

## 3. Pontos novos levantados pela auditoria independente

| # | Ponto | Verificação | Avaliação |
|---|---|---|---|
| N1 | **Validade do martingale de promoção.** A forma auto-normalizada só é supermartingale sob condições (por exemplo, incrementos e_t·φ_t condicionalmente simétricos). Citar Ville não basta. | A especificação já condiciona a garantia a "incrementos condicionalmente simétricos". **Mas** sob a nula "o átomo não acrescenta nada ao modelo atual", o resíduo e_t tem média condicional ≠ 0 sempre que o resto de S está mal ajustado (átomos faltando, atraso do NLMS). Aí e_t·φ_t não tem média zero se φ_t estiver correlacionado com a estrutura que falta. | **Procede e é o ponto mais importante.** A garantia só vale para a nula "pura" (φ independente de tudo), que é exatamente a única testada empiricamente (N1/N2: 0/17 686). Sob estrutura mal especificada, o teste mede **relevância preditiva dado o modelo atual**, não "estrutura verdadeira". Isso é coerente com o que o diagnóstico mostrou: polo errado promovido no B3 e atrasos aproximados. |
| N2 | Viés de seleção pela triagem | `_fresh()` zera S, Q e n na proposta; a triagem é zerada (`screen[c] = 0`). O início do teste é um tempo de parada previsível. | **Já tratado no código**, mas falta o argumento formal escrito. |
| N3 | "Equivalente à função de previsão airline / Holt-Winters" é uma afirmação larga demais | Holt-Winters aditivo corresponde a um ARIMA restrito do tipo (0,1,s+1)(0,1,0)_s, e não genericamente ao airline. | **Procede.** A especificação diz que G com a = 0,1 "é exatamente isso com Θ = 0,9" e "coincide" com o estado do Holt-Winters. Deve ser rebaixado para "inspirado em / análogo a", salvo prova para essas features. |
| N4 | FLOPs contados à mão não são resultado de hardware | A especificação já declara "execução em microcontroladores não verificada". | Coberto; reforça que a afirmação embarcada exige medição real. |
| N5 | A decomposição aditiva exata é álgebra, não método de XAI | A especificação já diz isso (§8, §14). | Coberto. |
| N6 | Não chamar o intervalo de "conformal" | A especificação usa "rastreamento de quantil"/"intervalo adaptativo". | Coberto. |

## 4. Referências novas (verificadas nesta sessão)

- Ungar, Zhou, Foster & Stine — Streaming Feature Selection using IIC, AISTATS 2005 — [PMLR](https://proceedings.mlr.press/r5/ungar05a.html)
- Tavyrikov, Goeman & de Heide — Carefree multiple testing with e-processes — [arXiv 2501.19360](https://arxiv.org/abs/2501.19360) (Electronic Journal of Statistics, ago/2026)
- Pérez-Ortiz, Lardy, de Heide & Grünwald — E-statistics, group invariance and anytime-valid testing — [Annals of Statistics 52(4), 2024](https://projecteuclid.org/journals/annals-of-statistics/volume-52/issue-4/E-statistics-group-invariance-and-anytime-valid-testing/10.1214/24-AOS2394.short)
- Xu & Ramdas — Online multiple testing with e-values (e-LOND) — [AISTATS 2024](https://proceedings.mlr.press/v238/xu24a.html)
- Não verificados por mim, citados pela auditoria independente: CVFDT (Hulten, Spencer & Domingos, KDD 2001); Magill (IEEE TAC 1965); Yamanishi & Miyaguchi (IEEE BigData 2016); Ben Abdelwahed et al. (ISA Transactions 2017); Shekhar & Williams (TRR 2007); patentes US6845938B2, US6643554B2, US10826932B2 e CN102997923B.

## 5. Encontrados só pela PRA-02

SAVA (Yao, Gang & Sun, 2025); R-SINDy (2024); Ren et al. 2026 (identificação esparsa bayesiana online); Fu & Zhao 2025; Leung, Hota & Paré 2024; Koop & Korobilis 2012; ARIMA online (Liu et al., 2016); TinyCast (2026).

## 6. Consequências

1. **Governança:** `NOVELTY_CLAIM_READY = NO` (mantido). A formulação mais estreita defensável exige, antes de qualquer afirmação:
   - (a) formalizar H₀ e a filtração e **provar** que a estatística de promoção é um e-process sob essa H₀, ou substituí-la por uma construção com hipóteses verificáveis (Lindon et al.; Pérez-Ortiz et al.);
   - (b) substituir o controle por episódio por uma política de testes múltiplos online (e-LOND / e-closure / orçamento Σα ≤ α por hipótese).
2. **Interpretação da evidência atual:** "0 promoções falsas" vale para a nula pura. Sob má especificação, promoções de átomos correlacionados com a estrutura que falta são esperadas, porque o teste mede relevância preditiva.
3. **Documentação congelada:** N1 (escopo da garantia) e N3 (equivalência airline/Holt-Winters) são imprecisões da especificação v0.51. Como os arquivos estão congelados por hash, a correção deve ir numa **errata separada**, não na edição dos arquivos congelados.
4. **v0.52:** a ordem de prioridade passa a ser:
   - (i) formalização e prova, ou troca do teste de promoção;
   - (ii) controle global de erro;
   - (iii) latente;
   - (iv) higiene.

   Os itens (i) e (ii) são pré-requisitos de qualquer afirmação científica sobre a parte estrutural.
