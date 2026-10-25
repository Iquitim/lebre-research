# Notas de execução — diagnóstico da M1

## 1. D-A (25/10/2026)

Execução única de `diag_m1_run.py A` (scripts e análise no commit `f27b43b`, antes de qualquer leitura): 30 de 30 bacias
sem erro, 6 variantes cada. Em todas as bacias, M0 reproduziu bit a bit a previsão L0 gravada pelo DIAG-01. Nenhum
desvio do plano.

Pela regra 1, só M5 (as três limitações removidas juntas) é classificada; M1 (RLS a cada passo) fica logo abaixo do
limiar (log 0,052 contra 0,5·G = 0,058).

## 2. D-B (replicação)

Pela regra 3: só M5, mais M0.

Execução (25/10/2026): M0 e M5 em D-B, 30 de 30 bacias sem erro; M0 de novo idêntica, bit a bit, à L0 do DIAG-01. M5
replicada pela regra 3. Resultado: `DIAG_M1_RESULTADO.md`.
