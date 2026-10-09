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

## 3. Resultado (E18b, 09/10/2026)

LEBRE Lab, `analises/E18B_RESULTADO.md`. Q2 falha no critério 1 em CURTAS (limite superior 1,0107 > 1,01; Boston curta
1,021). A Q atende a tudo no E16b (mesma régua). **Pela regra da seção 2, fica a candidata Q.** (Correção de registro: o
commit `fc71880` diz "104 tests"; são 103.)

## 4. Releitura com o adendo 3 da régua (E16c, 09/10/2026)

LEBRE Lab, `analises/E16C_RESULTADO.md`. Com o limite do choque dependente do tamanho do trecho (adendo 3), **Q e Q2 atendem
a todos os critérios nas 64 famílias**. Pela regra da seção 2, **a candidata da M2 passa a ser a Q2**. Vai para a validação
5 junto com a M1 que ficar.

## 5. Validação 5 (09/10/2026): confirmada com a M1 rascunho 5

LEBRE Lab, `analises/M1_VAL5_RESULTADO.md`: todos os critérios da M2 (régua com o adendo 3) em todas as famílias Z, Z-C05
incluída, sem NaN.
