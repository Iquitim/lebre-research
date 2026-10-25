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
