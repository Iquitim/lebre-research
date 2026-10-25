# Notas de execução — DEV-02

## 1. Defeito corrigido durante a execução (25/10/2026)

Na primeira execução de `dev2_run.py resto`, 3 séries de prédios (Fox_education_Shaun, Peacock_lodging_Matthew,
Hog_office_Roger) falharam com divisão por zero na regra D2. Em alvos constantes, o erro a priori da M1 fica exatamente
zero, σ̂²_E = 0, e a regra divide por zero; D3 e D4 têm a mesma divisão. **Correção** (commitada antes de refazer as
séries com falha): quando σ̂²_E = 0, qualquer erro diferente de zero conta como surpresa. A correção só muda o
comportamento no caso σ̂²_E = 0, que antes interrompia a execução; as séries que terminaram sem erro não passaram por esse
caso e não precisam ser refeitas. As séries com falha são refeitas com o código corrigido (o script pula as que já têm
resultado).

Refeitas com o código corrigido (`e0196d0`), sem erro e com a conferência bit a bit verdadeira: os 3 prédios e o rio
Apolônio Sales (reserva 1 do ONS), que tinha falhado pelo mesmo defeito antes de a correção entrar em vigor. A parte
"resto" ficou completa (166 de 166 séries).

## 2. Execução completa e análise (25/10/2026)

E20: 728 de 728 séries sem erro (ambiente do Lab, código corrigido). Análise `dev2_analise.py` sem desvio do plano.
Escolhida pela regra: **D4**. Resultado: `DEV2_RESULTADO.md`.
