# 22 — Relatório forense final

## 1. Escopo e proveniência
- **Código autoritativo:** `lebre_v051.py` / `lebre_s051.py` da etapa LEBRE-V0.51-LEAN-01. Os hashes congelados foram verificados em cada processo; ver `02_PROVENANCE_HASHES.txt`.
- **Ordem temporal original:** código às 03:56–03:57, pré-registro às 04:01, resultados às 04:02–04:03. A ordem é válida localmente, mas o pré-registro não foi publicado com o documento: **verificável só internamente**.
- **Réplica:** só o relatório PDF. O código e os resultados brutos estão `ARTIFACT_MISSING`.
- **Divulgação:** a rodada principal desta investigação precedeu a redação do plano. Todos os resultados abaixo são diagnósticos pós-hoc (rótulo `POST_HOC_DIAGNOSTIC`), exceto a execução do código congelado em si.

## 2. Completude da especificação (03)
Faltam no PDF, mas existem no código:
- τ (ρ = 1, com normalização pela potência);
- T_max = 200;
- B_probe = 2 e w = 0,2;
- M_max = 4;
- troca com R ≥ h/2;
- **limite de um latente**;
- H_hot = 4;
- ε = 10⁻⁶ no S e nenhum ε na M;
- cadência do quantil e forma da atualização.

A padronização causal está **descrita de forma errada**: o código usa uma EMA com α = 10⁻⁴, não médias acumuladas. → `SPECIFICATION_REPRODUCIBILITY = INSUFFICIENT`.

## 3. Reprodução de H4–H9 (05)
Das 70 células comparadas: 4 exatas, 16 com arredondamento, 43 com diferença material e 7 não reprodutíveis. As diferenças materiais vêm de três fontes:
- comprimento do fluxo e checagens diferentes;
- contabilidade de FP diferente (réplica ~350, original ~120–150 por passo);
- M diferente em N1: 1,447 no original contra 1,048 na réplica, ou seja, a réplica não usa o mesmo especialista de memória.

As **conclusões qualitativas** H4, H5, H6 (padrão de falhas) e H8 (falha localizada no B3) coincidem. H9 diverge.

## 4. Hipóteses
| Hipótese | Resultado | Rótulo |
|---|---|---|
| H4 | 0/17.686, CP95 1,7·10⁻⁴ < 2,96·10⁻⁴ | CONFIRMED_ARCHITECTURAL_RESULT |
| H5 | 3 remoções / 974.840 passos ativos (T1), 100% redescobertas | CONFIRMED_ARCHITECTURAL_RESULT |
| H6 | B1 0,93, T1 0,98; B2 0,57; B3 0,00; B4 0,27 | CONFIRMED_ARCHITECTURAL_FAILURE (múltiplos atrasos / latente) |
| H7 | B1 4/10 ≤ 2000; o gate é viável; o atraso está na proposta | CONFIRMED_ARCHITECTURAL_FAILURE + mecanismo de vazão da busca |
| H8 | B3 = 1,020 > 1,01 (critério vinculante global); demais ≤ 1,001 (descritivo) | NOT_SUPPORTED (dano concentrado no B3) |
| H9 | razões de FP de 0,148 / 0,167 / 0,202 e NMSE ≤ 1,081 contra a variante densa | CONFIRMED (a divergência da réplica é REPLICA_MISMATCH) |
| A8 | não executável | NOT_EXECUTABLE; diferença de normalização CONFIRMED; causa INSUFFICIENT_EVIDENCE |

## 5. Mecanismos (07, 08, 10, 11)
- **B3:** `WRONG_ATOM_PROMOTION + ELIGIBILITY_DEPENDENCY`. A hipótese da saturação do conjunto ativo é refutada no código original: o conjunto fica cheio em 3,5% do tempo, com 0 bloqueios.
- **H7:** limitado pela vazão da proposta. As 4 vagas ficam presas em testes fúteis de 400 passos, e a triagem ruidosa sonda cada candidato a cada 80 passos. O poder do martingale é adequado: 90–150 amostras.
- **τ:** o B2 é limítrofe (0,57 → 0,00 com ρ = 1/1000); o B3 é robusto à falha. A tendência relatada pela réplica (m = 1000 melhora o B2) não se reproduz.

## 6. Aspectos numéricos (12, 13, 14)
- **NLMS:** CODE_ONLY no S; sem ε na M, o que é invariante à escala mas diverge em "plano seguido de degrau" (NMSE 8·10²⁰).
- **Memória:** ≈ 196d + 12s + ~190 B (float32). O limite de ~1,3 KB exige s ≤ 78 com d = 1, s ≤ 46 com d = 3, s ≤ 13 com d = 5, e nunca é atingido com d = 6. Com s = 1440, são ~18 KB.
- **Quantil:** o aliasing de fase é real. A cobertura real vai de 0,851 a 0,971 com o operador do código; com o operador acumulado fica em 0,900–0,906.

## 7. Previsão e evidência real (15, 16, 17)
- **Frase defensável:** melhor entre os comparadores online pré-registrados (0,84× o NLinear, 8/10 séries). O airline por MLE pós-hoc é ~5% melhor e o Chronos-2 é 1,36× melhor.
- **"Estabilidade":** mede sensibilidade ao burn-in.
- **Held-out:** o segundo conjunto é semi-held-out.
- **Contribuição de S:** 16/20 séries são dominadas pela memória (w_S ≈ 0); 15/20 não têm nenhuma promoção estrutural. Só a Q9 (KDD S4) tem contribuição estrutural relevante, de 21%. O ganho vem principalmente de M.

## 8. Recursos (18)
- A crítica procede quanto ao custo do escalonador fora da contagem (~12d FP por passo).
- A afirmação H9 é robusta às três convenções de contagem **quando a comparação é com a variante densa do projeto**.
- A reconciliação com a contagem da réplica é impossível (ARTIFACT_MISSING). Por isso, `RESOURCE_CLAIM_ROBUST = PARTIAL`.

## 9. Veredictos por afirmação (20)
- **SUPPORTED:** C2, C6.
- **SUPPORTED_WITH_SCOPE_LIMITS:** C1, C3, C7, C9, C10.
- **NOT_SUPPORTED:** C4, C8, C11–C14, C16, C17.
- **REFUTED:** C5.
- **INSUFFICIENT_EVIDENCE:** C15.

## 10. Decisão (21)
- **Nenhum experimento corretivo foi executado.**
- **Ramos isoláveis e autorizáveis:** E (atualização do quantil em lote) e F (contrato numérico do NLMS).
- **Ramo de maior impacto:** revisão da regra de latente único / seleção de polo e da vazão da triagem. Está fora da lista pré-definida e exige desenho pré-registrado.
- **Decisão:** HUMAN_REVIEW.

**Status da v0.51 após a auditoria:** as garantias estatísticas se mantêm; a afirmação estrutural precisa ser restrita a atrasos únicos sintéticos; a especificação exige correção documental (parâmetros, normalização, memória, quantil, terminologia de held-out e estabilidade).
