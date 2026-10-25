# Notas de execução — versão barata da correção da M1

## 1. Escolha (25/10/2026)

Execução única de `dev_run.py escolha` no ambiente do LEBRE Lab, com o protótipo num worktree limpo no commit `b0522a0`
(código e análise no commit `f1dea28`, antes da execução): 788 de 788 tarefas sem erro. Os avisos de log de valor
inválido no registro vêm do pandas, dentro do carregador do E20 (os mesmos das execuções anteriores do E20), e não
afetam as previsões. Análise sem desvio do plano.

Resultado: nenhuma variante admissível (`DEV_M1_RESULTADO.md`); a decisão volta ao responsável pelo projeto, como manda
a §5 do plano.

## 2. Desvio declarado (25/10/2026, antes da replicação)

**Decisão do responsável pelo projeto:** seguir com a **C5** (RLS da M1 a cada 4 alvos aprendidos, 3 bandas de
defasagem, 3 defasagens do alvo, sem recorte), embora ela não seja admissível pela regra da §5 do plano.

- **Critério desviado:** só o K2 (ganho nas bacias). A C5 preserva 69,4% do ganho da correção completa em D-A, contra o
  mínimo de 70%.
- **Critérios mantidos, todos aprovados pela C5:** K1 (nenhuma família do E20 nem os prédios com limite superior acima de
  1,02; a pior foi 1,010), K3 (custo mediano 0,985) e K4 (nenhuma previsão não finita a mais).
- **Motivo:** o K2 mede quanto do ganho possível se preserva, não segurança nem custo. A alternativa mais próxima (C4)
  exigiria afrouxar o critério de não piora.
- **Replicação, sem mudança:** a regra de replicação da §5 continua valendo integralmente para a C5 (ganho em D-B com IC
  acima de zero e pelo menos metade do de D-A; prédios R com limite superior ≤ 1,02).
- **Código:** `dev_analise.py replica C5 --desvio` aceita a C5 apesar de `escolhida = None`. É a única mudança, e ela não
  altera nenhum cálculo.

## 3. Replicação da C5 (25/10/2026)

`dev_run.py replica C5`: 60 de 60 tarefas sem erro (bacias D-B e prédios R, A e C5). `dev_analise.py replica C5
--desvio`: **replicada**. Bacias D-B: v0.55 ÷ C5 = 1,053 [1,041; 1,067] (log 0,052 contra o mínimo de 0,035, metade do de
D-A); prédios R: C5 ÷ v0.55 = 0,995 [0,989; 1,000]; custo mediano 0,96. Números: `DEV_M1_RESULTADO_replica.json`.

## 4. Verificação pós-escolha, a pedido do responsável pelo projeto (25/10/2026)

Achados da revisão, antes de seguir para a avaliação final:

1. **Nenhuma família descartada:** as 64 famílias do E20 entraram com todas as séries (728) em todas as variantes; o
   critério K1 não passou "por vazio".
2. **Consistência entre etapas, códigos e ambientes:** a variante A desta etapa (ambiente do LEBRE Lab) é idêntica, bit a
   bit, à L0 do DIAG-01 nas 60 bacias, e a C0 é idêntica, bit a bit, à M5 do DIAG-02 nas 30 bacias de D-A.
3. **A M1 não muda a estrutura:** `verif_estrutura.py`, em 11 séries com muitas mudanças de estrutura (E20 A01, A04, A05
   ×2, A07, B03, C03; 2 prédios; 2 bacias): eventos do núcleo, estrutura final e previsão do núcleo idênticos, passo a
   passo, entre A e C5. Os eventos do portão da M2 podem mudar (0 contra 2 numa bacia), porque o portão compara a
   referência com a saída da M1. Consequência: o controle placebo de uma avaliação final dará o mesmo resultado da v0.55.
4. **Independência limitada da replicação:** as bacias D-B já tinham sido usadas no DIAG-01 e no DIAG-02 (onde a correção
   completa foi replicada nelas). A replicação nas bacias D-B não é, portanto, um teste novo da direção da correção; só
   os prédios R são novos para esta linha de trabalho. A avaliação em bacias nunca usadas (CAMELS-CL) é o teste que
   decide.
5. **Lacuna no banco: vazões afluentes dos rios do ONS.** Na v0.52, o grupo em que o RLS piorou ("ONS", 0,595 contra
   0,508) eram as vazões afluentes em cascatas de reservatórios (dados de 3 horas, ciclo de 8 passos). Elas **não estavam**
   no banco desta etapa (o E20 tem carga, solar e eólica do ONS, não os rios).

**Checagem adicional, declarada antes de rodar (só segurança):** A contra C5 nas séries de rios do ONS do SPLIT_V052, as
45 da reserva 1 (consumida pela avaliação de 2026-09) e as 11 de desenvolvimento. Mesma função `reps`, janela de 30% até o
fim, blocos de 56 passos (uma semana), semente 2026102806 (conferida como não usada). **Critério:** limite superior do IC
95% da razão C5 ÷ A ≤ 1,02 em cada um dos dois grupos. Se falhar, isso é registrado como falha de segurança da C5 e a
decisão volta ao responsável pelo projeto.

Execução da checagem dos rios: a primeira tentativa, no ambiente do Lab, falhou nas 56 séries antes de qualquer previsão
(o ambiente não tem leitor de parquet, o formato dos dados do ONS). Repetida com o Python do sistema (a parte dos rios não
usa o E20), sem nenhuma outra mudança.

**Resultado da checagem dos rios (56 de 56 séries sem erro):** passa. Desenvolvimento (11): C5 ÷ A = 0,994 [0,981;
1,005]; reserva 1 (45): 0,968 [0,955; 0,981]; custo 1,02. A C5 **melhora** os rios. Piores séries: Itaúba 1,092, Rosana
1,066, Jupiá 1,035; melhor: Machadinho 0,540. Números: `DEV_M1_RESULTADO_ons.json`.

**Achados descritivos da revisão (sem critério):**
- **Cauda por série** (848 séries do banco e das replicações, sem os rios): 0,2% das séries pioram mais de 5% com a C5,
  1,2% pioram mais de 2% e 10,4% melhoram mais de 2%. As duas piores são bacias de D-B (84095000: 1,167; 70300000:
  1,073). Nos rios, as três piores ficam entre 1,035 e 1,092. **A média por família esconde pioras isoladas de até ~17%**;
  isso precisa estar nos limites da candidata.
- **Diferença restante para o ARX-RLS** (média geométrica por série, sem IC): C5 ÷ ARX-RLS = 1,048 em D-A (era 1,124 na
  v0.55) e 1,000 em D-B (era 1,053).
