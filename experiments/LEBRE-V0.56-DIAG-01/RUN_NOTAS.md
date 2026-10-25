# Notas de execução — diagnóstico das bacias

## 1. D-A (25/10/2026)

Execução única de `diag_run.py A` (scripts no commit `1ded72b`, análise no commit `f997e47`, ambos antes de qualquer
leitura): 30 de 30 bacias sem erro, 11 modelos cada. Protótipo num worktree limpo no commit `b0522a0`. Nenhum desvio do
plano na execução nem na análise.

## 2. Observação depois do resultado de D-A: borda da grade do NLMS

O μ do degrau R6 (NLMS com os atributos do ARX) foi escolhido no maior valor da grade pré-registrada (0,2) em 25 de 30
bacias. Logo, o efeito medido de "RLS em vez de NLMS" (R6) é um **limite superior** do efeito do algoritmo de
adaptação: um NLMS com passo maior poderia ficar mais perto do RLS.

**Checagem suplementar, post hoc e declarada antes de rodar:** degrau R6x = R6 com μ calibrado da mesma forma em
{0,5; 1,0} (o NLMS normalizado é estável para μ < 2), em D-A e em D-B. Ela **não entra** na classificação da §5 do
plano (que continua usando R6, como pré-registrado); serve só para dizer quanto do efeito de R6 sobrevive a uma grade
maior. Sementes de bootstrap: as mesmas do conjunto (o contraste recebe um índice próprio).

## 3. D-B (replicação)

Pela regra 4 do plano, rodam em D-B só os modelos dos ingredientes classificados como "parte substancial" em D-A (R1,
R3, R4, R6 e a memória fraca, que vem de L2), mais R0 e L0; e a checagem suplementar R6x.
