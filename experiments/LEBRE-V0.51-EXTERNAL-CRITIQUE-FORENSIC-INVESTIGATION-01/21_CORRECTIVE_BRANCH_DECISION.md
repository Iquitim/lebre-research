# 21 — Decisão sobre ramos corretivos

| Ramo | Condição de autorização | Evidência | Decisão |
|---|---|---|---|
| A — normalização | S canônico sofre o problema do normalizador | a réplica usou outro normalizador; em B1–B3 nenhum efeito; A8 indisponível | **não autorizado** (evidência insuficiente; exige um teste não estacionário pré-registrado antes) |
| B — troca no conjunto ativo | falha do B3 causada por vagas cheias | orçamento cheio em 3,5% do tempo, 0 bloqueios; a causa é o latente único e a escolha de polo | **não autorizado** na forma proposta; o mecanismo real sugere um ramo diferente (seleção/revisão do polo latente), que não está na lista |
| C — vazão de teste | H7 limitado pela vazão, e não pelo poder | proposta tardia (~1.500–2.900 passos) com teste rápido (~200–300 passos); mecanismo observado, não isolado | **candidato mais forte**, mas o mecanismo é de *busca/triagem* e não de vagas de teste |
| D — poder do martingale | testes observados, com evidência lenta | as amostras até o cruzamento (90–150) são adequadas; só o átomo fraco do B2 sofre futilidade | não autorizado |
| E — atualização do quantil em lote | aliasing de fase reproduzido | **reproduzido** em dado sintético e real (0,85–0,97 → 0,900–0,906) | **autorizável** isoladamente |
| F — contrato numérico do NLMS | ambiguidade do ε afeta resultados ou estabilidade | divergência reproduzida no degrau; nenhum efeito no held-out | **autorizável** isoladamente (baixo risco) |

**Recomendação para revisão humana:**
- Os ramos **E** e **F** atendem às condições e são isoláveis.
- O problema estrutural principal (B3 e H7) aponta para dois mecanismos que não estavam na lista pré-definida: a *seleção do polo com latente único* e a *vazão da triagem*. Eles precisam de um desenho novo antes de qualquer experimento.
- Pelas regras desta etapa, **nenhum reparo foi executado**, e a decisão final cabe à revisão humana (`AUTHORIZED_CORRECTIVE_BRANCH = HUMAN_REVIEW`).
