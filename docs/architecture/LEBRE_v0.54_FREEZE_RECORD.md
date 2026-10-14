# LEBRE v0.54 — Registro formal de congelamento

**Arquitetura:** LEBRE (Lifecycle-governed Evidence-Based Resource Evolution)
**Versão:** 0.54 (consolidação: M5a + M5b + M4 sobre a v0.53 inalterada)
**Status:** `PROMOTED_RESEARCH_VERSION_WITH_SCOPE_LIMITS`
**Etapa:** `LEBRE-V0.54-FREEZE-01`
**Data:** 14 de outubro de 2026
**Código congelado:** lebre-research, commit `f9906c4`, pasta `experiments/LEBRE-V0.54-PROTO-01` (inalterada desde então).
Esse é o código promovido (commit `cfe72ce`) com a **errata 01** (§5), que muda só a distribuição do custo entre os passos:
previsões, decisões e relatório são idênticos.
**Relação com as versões anteriores:** a v0.1 continua sendo a **referência canônica** do projeto; a v0.51, a v0.52 e a
v0.53 continuam **congeladas e inalteradas** (o verificador `scripts/verify_integrity.py` passa em todos os manifestos em
14/10/2026). Como a v0.53, a v0.54 foi **promovida por uma regra pré-registrada e vinculante**, numa avaliação única em
dados reservados antes de qualquer código da v0.54 (`experiments/LEBRE-V0.54-FINAL-01/PREREG_V054_FINAL.md`).

---

## 1. Princípio que orienta a versão

A LEBRE **não precisa ser o melhor previsor**: precisa **entregar bem com orçamento mínimo e sem falhas catastróficas**.
A v0.54 estende esse princípio ao **custo** (gastar só onde há uso) e à **saída** de estrutura (remover quando a evidência
deixa de sustentar), sem mudar o que a v0.53 prevê onde a v0.53 já era útil.

## 2. O que está congelado

| Item | Conteúdo |
|---|---|
| **Código do modelo** | `experiments/LEBRE-V0.54-PROTO-01/lebre054/`: a v0.53 como cópia byte a byte de `lebre==0.2.0` (hashes em `SHA256_COPIAS.txt`, conferidos pelos testes) e as mudanças da v0.54 em arquivos novos: `dormancy.py` (M5a), `screening.py` (M5b), `removal.py` (M4), `model054.py` (montagem). `cycle.py` (M6) está no código, **desligado** e fora da v0.54. Só dependem de numpy. Testes: 23, passando. |
| **Configuração canônica** | §3. |
| **Especificações** | `experiments/LEBRE-V0.54-DESIGN-NOTE-01/`: nota de desenho, especificações de cada rascunho da M5a, M5b, M4 e M6 (com resultados e decisões), diagnóstico da M3, protocolo e relatório da busca de literatura PRA-11. |
| **Dados reservados** | `experiments/LEBRE-V0.54-DATA-01/`: regras e divisão da reserva (10/10/2026), travas, SHA-256 dos arquivos brutos. A reserva foi consumida pela avaliação final. |
| **Avaliação final** | `experiments/LEBRE-V0.54-FINAL-01/`: pré-registro, leitores, scripts de execução e análise, ensaio em séries já gastas, notas da execução, previsões por série (metadados), resultado e a errata 01. |
| **Auditoria de estresse** | `experiments/LEBRE-V0.54-AUDIT-01/`: plano, scripts, resumo numérico e relatório da auditoria feita depois da promoção. |

Lista completa com SHA-256: `LEBRE_v0.54_SHA256SUMS.txt` (todos os arquivos rastreados dessas cinco pastas, 148,
verificados no momento do congelamento). O desenvolvimento e as validações estão no LEBRE Lab (repositório
`Iquitim/lebre-lab`, pasta `analises/`), com plano e resultado de cada medição.

## 3. Configuração canônica e constantes

```python
Lebre054(d, season=s, season2=s2, reference=R, m5a=True, m5b=True, m4=True)   # m6=False (padrão)
```

R = `"zero"` (retornos financeiros), `"seasonal"` (com ciclo declarado) ou `"persistence"` (sem ciclo), como na v0.53.

| Parte | Constantes |
|---|---|
| **Base (v0.53)** | `lebre==0.2.0` inalterada: núcleo estrutural da v0.52-r1, M1 (especialista de precisão com AdaHedge) e M2 (referência trivial com (A,B)-Prod). |
| **M5a: M1 dormente** (`ALGORITHM_SPEC_DRAFT_M5a_r2.md`) | Depois da sombra, a M1 dorme se o seu peso ω < 10⁻³ por 2.000 alvos aprendidos. Dormindo: estatística de ganho amostrada a cada 8 alvos, regressão a cada 64, AdaHedge congelado, saída igual à do núcleo + M2. Desperta se a média exponencial (taxa 0,01) do ganho relativo passar de 0,05 depois de pelo menos 100 amostras; o AdaHedge recomeça com sombra de 100 atualizações. Se a seleção de entradas muda durante o sono, a M1 desperta em teste e volta a dormir depois de 500 alvos com ω < 10⁻³, a menos que ω chegue a 10⁻³. |
| **M5b: relatório de equivalentes barato** (`ALGORITHM_SPEC_DRAFT_M5b.md`, rascunho 2) | A matriz de covariâncias das entradas (só relatório) usa uma amostra a cada 31 passos (primo, sem aliasing com ciclos de 7, 12, 24 e 168), com peso 1e-3 × 31, aplicada uma linha por vez nos passos seguintes (até ⌈d/30⌉ linhas por passo). |
| **M4: remoção disparada** (`ALGORITHM_SPEC_DRAFT_M4.md`, rascunho 1) | Acrescentada ao calendário original de remoções (que continua igual). Um teste de remoção abre quando a contribuição média da unidade cai abaixo de 0,5 × a referência (pico desde a aceitação, que volta ao valor atual a cada teste), com pelo menos 2.000 passos entre testes da mesma unidade. Hipótese nova por episódio, e-process do zero, nível e-LOND próprio α × γ_k × (remoções aceitas + 1) com α = 0,05, margem 0,002, duração de até 10.000 passos e aceitação só depois de 5.000 passos de evidência; o disparado tem prioridade sobre um teste periódico de remoção da mesma unidade. |
| **Custo (contagem auditada)** | regra da v0.52 (1 FP por operação elementar), com as contagens acrescentadas de cada mudança nos seus arquivos. |

## 4. Evidência que acompanha o congelamento

**Avaliação final pré-registrada e vinculante** (`FINAL_RESULTADO.md`, 93 séries reservadas desde 10/10: 30 bacias
CAMELS-BR, 30 medidores BDG2, 8 usinas eólicas e 8 solares do ONS, 17 séries de níveis da EIA e do Tesouro dos EUA):

- **sem piora em nenhuma família** (régua por decidibilidade com a v0.53 como base; v0.54 ÷ v0.53 de 0,989 a 1,000 por
  família; séries curtas 1,007; nenhuma previsão não finita);
- **custo:** razão mediana v0.54 ÷ v0.53 por série de **0,905** (IC 95% 0,857 a 0,932); eólica 0,753, prédios 0,847,
  níveis 0,879, solar 0,917, bacias 1,006 (onde a M1 é útil, a v0.54 gasta o mesmo que a v0.53);
- **memória estimada** de 85.268 B (não medida), dentro de 128 KB;
- **referências fora da classe de orçamento** (só reportadas): Chronos-2 com covariáveis foi melhor nos prédios (v0.54 ÷
  Chronos-2 1,338), na solar (1,319) e na eólica (1,060), e pior nas bacias (0,943) e nos níveis (0,835); SARIMAX com
  entradas ficou pior que a v0.54 onde rodou (1,04 a 1,11) e falhou nos níveis.

**Desenvolvimento e validações (LEBRE Lab):** cada mudança foi medida no banco de 64 famílias contra a configuração
anterior, revista quando falhou e, depois de revista, validada em dados nunca vistos, usados uma única vez (validações 6 e
7 e a segunda medição da errata 01). A combinação inteira foi medida no banco na auditoria (teste T10): nenhuma família com
limite superior acima de 1,02.

**Auditoria de estresse** (`experiments/LEBRE-V0.54-AUDIT-01/RELATORIO_AUDITORIA.md`): nenhum defeito de correção e
nenhuma falha catastrófica em 10 testes (identidade e determinismo, 12 tipos de estresse, nulos, entradas fracas,
despertar da M1, crescimento do estado, combinação no banco). Dois defeitos encontrados, tratados em §5.

## 5. Errata 01 e limites declarados

**Errata 01** (`experiments/LEBRE-V0.54-FINAL-01/ERRATA_01.md`):

1. **Pico de custo da M5b, corrigido.** A atualização inteira da matriz coincidia periodicamente com a regressão da M1 e
   elevava o pico por passo (+11% com 20 entradas, +50% com 50). A M5b rascunho 2 espalha a atualização; previsões,
   decisões, relatório e custo total são os mesmos, e o pico ficou em no máximo 1,054 vez o da v0.53 (aceita na segunda
   medição, em 60 séries novas).
2. **Relações que somem e voltam (M4), declarado.** Uma relação ausente por mais de ~5.200 passos é removida e precisa ser
   redetectada quando volta (mediana de 675 a 920 passos); com blocos ligado/desligado de 7.500 a 15.000 passos, o erro
   fica 5% a 10% acima do da v0.53. Sem correção na v0.54.

**Outros limites:**

- **Fora da v0.54:** a M3 (interpretação em níveis; `M3_DIAGNOSTICO.md`): entradas externas espúrias continuam aceitas
  em séries de níveis (3 de 17 na reserva, como na v0.53). A M6 (ciclo como hipótese): dois desenhos medidos, nenhum
  atendeu na solar sem ciclo declarado; o ciclo continua precisando ser declarado.
- **Metas não atingidas:** custo com 50 entradas ≤ 2 vezes o custo com 5 (a M5b corta só a parte quadrática do
  relatório); o "30% a menos" citado como exemplo na nota de desenho (a meta pré-registrada foi um IC abaixo de 1).
- **Avaliação final:** uma falha de infraestrutura na primeira passada (os processos filhos importaram o leitor da v0.53
  de mesmo nome) foi corrigida e documentada (`RUN_NOTAS.md`); 4 resultados inválidos foram retirados antes de qualquer
  análise.
- **Anterior à v0.54:** a lista de eventos do modelo cresce sem limite (v0.53 e v0.54); num dispositivo embarcado,
  precisa ser limitada.
- **Remoções em dados reais:** não há verdade conhecida sobre trocas de regime nas séries reais; a evidência da M4 vem do
  desenvolvimento e das validações.

## 6. Reprodução

```bash
git checkout f9906c4
cd experiments/LEBRE-V0.54-PROTO-01 && python -m pytest -q tests      # 23 testes; precisa de lebre==0.2.0
python scripts/verify_integrity.py                                    # todos os manifestos, inclusive este
```

A avaliação final foi executada com o código do commit `cfe72ce` (antes da errata 01). Os scripts e os hashes estão em
`experiments/LEBRE-V0.54-FINAL-01/`.
