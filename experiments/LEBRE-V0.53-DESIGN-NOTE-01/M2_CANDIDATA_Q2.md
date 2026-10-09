# M2 da v0.53: candidata Q2 (a Q com o maior erro com esquecimento), especificação antes do código

**Data:** 09/10/2026. **14ª configuração da M2.** Base: o E17 (LEBRE Lab) mostrou, na M1, que normalizar as perdas do Prod
pelo maior erro já visto (candidata Q) congela o Prod depois de um erro recorde, risco já declarado na especificação da Q.
A Q da M2 usa a mesma normalização; o defeito não apareceu como falha no E16, mas o mecanismo é o mesmo e a validação 4
mostrou que uma aprovação no desenvolvimento pode não se repetir em dados novos.

## 1. A única mudança em relação à Q

N_t = máx((y_t − D_t)², (y_t − M_t)², LAM × N_{t−1}), LAM = 0,99 (constante da v0.52), em vez de N_t = máx de todo o
passado. Custo: +1 FP por passo.

## 2. Regra de escolha entre Q e Q2 (declarada antes de medir Q2)

Q2 e Q no mesmo desenvolvimento ampliado (E18 e releitura E16b), com a régua com os adendos 1 e 2. Se as duas atenderem,
**fica a Q2** (sem o mecanismo de congelamento conhecido). Se só uma atender, fica ela. Se nenhuma, as falhas são
declaradas.
