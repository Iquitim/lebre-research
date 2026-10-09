# LEBRE v0.53 — Registro formal de congelamento

**Arquitetura:** LEBRE (Lifecycle-governed Evidence-Based Resource Evolution)
**Versão:** 0.53 (consolidação: M1 rascunho 5 + M2 candidata Q2 sobre a v0.52 inalterada)
**Status:** `PROMOTED_RESEARCH_VERSION_WITH_SCOPE_LIMITS`
**Etapa:** `LEBRE-V0.53-FREEZE-01`
**Data:** 9 de outubro de 2026
**Código promovido:** lebre-research, commit `4a2620e`, pasta `experiments/LEBRE-V0.53-PROTO-01` (inalterada desde então).
**Relação com as versões anteriores:** a v0.1 continua sendo a **referência canônica** do projeto; a v0.51 e a v0.52 continuam
**congeladas e inalteradas** (52/52 e 650/650 arquivos conferem com seus hashes em 09/10/2026; v0.1: 23/23). Diferentemente da
v0.52, a v0.53 foi **promovida por uma regra pré-registrada e vinculante**, numa avaliação única em dados reservados antes
de qualquer código da v0.53 (`experiments/LEBRE-V0.53-FINAL-01/PREREG_V053_FINAL.md`).

---

## 1. Princípio que orienta a versão

A LEBRE **não precisa ser o melhor previsor**: precisa **entregar bem com orçamento mínimo e sem falhas catastróficas**.
A v0.53 é uma versão de **consolidação** (nota de desenho 01): corrige dois modos de falha da v0.52 sem ampliar o espaço de
hipóteses: **F6**, a v0.52 abaixo da fronteira precisão × custo quando a série depende de defasagens conjuntas do alvo e
das entradas (marés, qualidade do ar); e **F8**, a v0.52 pior que uma referência trivial (câmbio, inflação).

## 2. O que está congelado

| Item | Conteúdo |
|---|---|
| **Código do modelo** | `experiments/LEBRE-V0.53-PROTO-01/lebre053/`: a v0.52 como cópia byte a byte de `lebre==0.1.0` (`_core.py`, `_engine.py`, `_memory.py`, `_model052.py`; hashes em `SHA256_COPIAS.txt`, conferidos) e as mudanças da v0.53 (`model053.py`, `precisao.py`, `agregacao.py`). Só dependem de numpy. Testes: 104, passando. |
| **Configuração canônica** | §3. Reproduz exatamente as previsões validadas: MSE idêntico em 813 de 813 séries (verificação E22) e na execução final. |
| **Configurações históricas** | Os demais valores de `saida` e `precisao` (rascunhos 0 a 6 da M2, candidatas D, S, M, P, Q; rascunhos 0 a 4 da M1) ficam no código apenas como ablações reproduzíveis; não fazem parte da v0.53. O `README.md` do protótipo é um diário de desenvolvimento e não lista as escolhas finais: vale este registro. |
| **Especificações e literatura** | `experiments/LEBRE-V0.53-DESIGN-NOTE-01/`: nota de desenho, especificações de cada rascunho da M1 e da M2 (com resultados e erratas), régua por decidibilidade e seus adendos 1 a 3 (`M2_CANDIDATA_D.md`), auditorias de literatura PRA-06 a PRA-10. |
| **Dados reservados** | `experiments/LEBRE-V0.53-DATA-01/`: regras e divisão da reserva (05/10/2026), travas, e os SHA-256 dos 55 arquivos brutos (`SNAPSHOT_SHA256SUMS.txt`, conferidos antes da execução). |
| **Avaliação final** | `experiments/LEBRE-V0.53-FINAL-01/`: pré-registro aprovado, leitores, scripts de execução e análise, testes feitos sem a reserva, ensaio geral, notas da execução, previsões por série (metadados), resultado e o adendo do SARIMAX no câmbio. |

Lista completa com SHA-256: `LEBRE_v0.53_SHA256SUMS.txt` (todos os arquivos rastreados dessas quatro pastas, verificados no
momento do congelamento).

## 3. Configuração canônica e constantes

```python
Lebre053(d, season=s, season2=s2, referencia=R, porta=True, eps_porta=0.002, recriar=True, alpha_porta=0.01,
          observar_quarentena_entradas=True, saida="prod_q2", precisao="r5")
```

R = `"zero"` (retornos financeiros), `"sazonal"` (com ciclo declarado) ou `"persistencia"` (sem ciclo).

| Parte | Constantes |
|---|---|
| **Base (v0.52)** | `lebre==0.1.0` inalterada (configuração canônica da v0.52; registro `LEBRE_v0.52_FREEZE_RECORD.md`, §3). |
| **M1: especialista de precisão** (`ALGORITHM_SPEC_DRAFT_M1_r5.md`) | z = [1, y_{t−1}, y_{t−2}, médias das bandas de defasagem [0], [1], [2–3], [4–7], [8–15] das m = mín(d, 5) entradas de maior correlação absoluta com o alvo, padronizadas]; k = 3 + 5m; RLS com λ = 0,999 e δ = 100, atualizada a cada 8 alvos observados; triagem a cada 8 passos, seleção depois de 100 alvos e refeita a cada 5.000; previsão recortada em L ± 2·máx(σ̂_L, piso); entra depois de k atualizações. |
| **M1: combinação com a v0.52** | AdaHedge (de Rooij et al., 2014) com dois especialistas (v0.52 e M1) sobre o **erro quadrático sem recorte**; entrada em sombra: a saída só usa a mistura depois de 100 atualizações do AdaHedge. |
| **M2: referência trivial** (`M2_CANDIDATA_Q2.md`) | D: AdaHedge sobre o erro quadrático de R e L (só com a referência definida); M: troca num só sentido R → L (switch distribution, risco 1/t) sobre perdas gaussianas na escala recente; combinação de D e M pelo (A,B)-Prod anytime (Sani, Neu e Lazaric, 2014) com perdas normalizadas pelo maior erro com esquecimento (N_t = máx(perdas, 0,99·N_{t−1})); caminho de reserva em escala logarítmica no M contra 0/0. |
| **Porta e auditoria** | e-process da porta com ε = 0,002, α = 0,01, recriado depois de cada decisão; a v0.52 dentro da v0.53 mantém a mesma estrutura de quando roda sozinha (critério 6, verificado em todas as séries). |
| **Custo (contagem auditada)** | regra da v0.52 (1 FP por operação elementar); RLS 6k² + 5k por atualização; previsão 2k + 18m + 4; AdaHedge 48; M2 ~132-137 FP por passo. |

## 4. Evidência que acompanha o congelamento

**Avaliação final pré-registrada e vinculante** (`FINAL_RESULTADO.md`; 104 séries reservadas desde 05/10: 30 bacias
CAMELS-BR, 30 medidores BDG2, 8 usinas solares e 8 eólicas do ONS, carga de 2026 dos 4 subsistemas, 8 pares de câmbio em 3
tarefas):
- **sem piora em nenhuma família** (régua por decidibilidade com os adendos 1 a 3; entradas falsas no câmbio iguais às da
  v0.52; estrutura preservada; séries curtas 1,007 [0,995; 1,017] do melhor de v0.52 e referência; nenhuma previsão não
  finita; acréscimo de custo máximo de 918 FP, abaixo do limite de 1.100);
- **melhora clara:** v0.53 ÷ v0.52 = **0,955** [IC 95%: 0,951; 0,960] nas 104 séries;
- por família: bacias **0,879**, níveis de câmbio **0,952**, retornos **0,966**, prédios **0,993**; volatilidade do câmbio,
  solar, eólica e carga **1,000**;
- tetos de referência (só reportados): o Chronos-2 com covariáveis é melhor nos prédios, solar, eólica e carga (v0.53 ÷
  Chronos-2 de 1,05 a 1,43) e pior nas bacias (0,885) e no câmbio (0,88 a 0,98); o SARIMAX com entradas é pior que a v0.53 em todas as
  famílias exceto a carga (0,968), inclusive no câmbio com as entradas preenchidas (adendo: 1,06 a 1,12);
- memória estimada (não medida): 85.092 B, dentro de 128 KB.

**Validação 5** (43 séries novas, medição única; `M1_VAL5_RESULTADO.md` no LEBRE Lab): F6 atendida em qualidade do ar de
Pequim (1,118 contra meta 1,410; v0.52 1,169) e em 6 estações de maré novas (0,925 contra 1,068; v0.52 1,017); critérios da
M2 em todas as famílias. **Errata:** solar, eólica e carga dessa validação foram montadas com ciclo de 30 h (§5).

**Desenvolvimento (não vinculante):** as 64 famílias do desenvolvimento ampliado (E16c, E20); 6 desenhos da M1 e 14
configurações da M2; auditoria de NaN (E18: nenhum em medições registradas); verificação de identidade depois da redução de
custo sem mudança de previsões (E22: 813/813); ensaio geral em 55 séries de bacias e prédios já gastas (0 erros, 0 NaN).

## 5. Condição de uso e limitações congeladas junto

1. **Custo sem ganho em parte dos domínios:** a v0.53 custa mais que a v0.52 em todas as séries (acréscimo mediano de ~540
   FP por passo; razão mediana de ~2,3 vezes; até ~3,9 vezes onde a v0.52 é barata). Em solar, eólica e carga, a M1 terminou
   com peso zero e a v0.53 é **idêntica** à v0.52, pagando de 700 a 900 FP a mais por passo. A meta preliminar de 1,25 vez
   da nota de desenho mostrou-se incompatível com M1 + M2 e foi substituída, antes da avaliação, por um teto absoluto de
   1.100 FP de acréscimo (decisão do responsável pelo projeto).
2. **F6 na reserva final:** a reserva não tem famílias do tipo F6 (marés, qualidade do ar); a evidência de F6 em dados novos
   vem só da validação 5, com margem pequena em uma família do desenvolvimento (VB07: 1,053 contra 1,056).
3. **Régua decidida durante o desenvolvimento:** os adendos 1 a 3 (séries dominadas por um choque ficam indecidíveis nos
   critérios 1 e 2, com limite dependente do tamanho) foram decididos depois de ver dados de desenvolvimento, antes da
   validação 5 e da avaliação final.
4. **Erratas e correções declaradas:** ciclo de 30 h em solar, eólica e carga das validações 4 e 5 (o alcance da validação
   5 foi restringido); na execução final, duas correções de leitura e análise sem efeito em modelo ou critério (`RUN_NOTAS.md`).
5. **Perfil embarcado:** a memória é estimativa analítica; a v0.53 não foi portada para C nem medida no microcontrolador.
6. **Incerteza:** o IC do conjunto trata as séries como independentes; famílias com poucas séries (carga: 4) dão intervalos
   largos.
7. **Originalidade:** nenhum componente é novo (AdaHedge, (A,B)-Prod, switch distribution, RLS com bandas de defasagem; PRA-06
   a PRA-10). A contribuição é de **integração** sob orçamento declarado e da evidência empírica pré-registrada.
8. **Rastreabilidade:** o desenvolvimento, as validações 1 a 5 e os diagnósticos foram feitos no LEBRE Lab, repositório
   **local, não publicado**; este registro cita os commits do Lab, mas a cadeia completa só pode ser auditada quando ele for
   publicado.

## 6. O que fica fora deste congelamento

- **M4** (remoções que acontecem), **M5 original** (custo proporcional ao uso e à surpresa) e **M6** (ciclo como hipótese)
  foram adiadas para a v0.54 (decisão do responsável pelo projeto). A M5 da v0.53 ficou restrita a mudanças que preservam as
  previsões.
- Qualquer nova avaliação exige **dados nunca vistos**. A reserva da v0.53 está consumida. Continuam disponíveis, entre
  outros: posições 140+ da permutação do CAMELS-BR e 115+ da do BDG2; usinas elegíveis do ONS não usadas; estações da NOAA e
  de Pequim não usadas; a carga do ONS a partir de outubro de 2026. Moedas flutuantes do H.10 fora da reserva estão
  praticamente esgotadas.
