# Notas de execução — DEV-02

## 1. Defeito corrigido durante a execução (25/10/2026)

Na primeira execução de `dev2_run.py resto`, 3 séries de prédios (Fox_education_Shaun, Peacock_lodging_Matthew,
Hog_office_Roger) falharam com divisão por zero na regra D2. Em alvos constantes, o erro a priori da M1 fica exatamente
zero, σ̂²_E = 0, e a regra divide por zero; D3 e D4 têm a mesma divisão. **Correção** (commitada antes de refazer as
séries com falha): quando σ̂²_E = 0, qualquer erro diferente de zero conta como surpresa. A correção só muda o
comportamento no caso σ̂²_E = 0, que antes interrompia a execução; as séries que terminaram sem erro não passaram por esse
caso e não precisam ser refeitas. As séries com falha são refeitas com o código corrigido (o script pula as que já têm
resultado).
