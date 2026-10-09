# Verificações antes da aprovação do pré-registro: resultado (09/10/2026)

Plano `ENSAIO_PLANO.md` (commit `d8eaad8`). Nenhum valor da reserva foi lido.

1. **Presença dos arquivos (só nomes):** 221 itens conferidos, nenhum faltando (tempo das 16 usinas e dos 4 subsistemas,
   carga de 2026, 24 arquivos mensais do ONS, 10 do FRED, os nomes das 16 usinas nos arquivos do ONS, as 30 bacias nos 4
   zips do CAMELS-BR, os 30 medidores no cabeçalho do BDG2).
2. **Ensaio geral** (55 séries já gastas pela v0.52: 10 bacias e 5 medidores do desenvolvimento, 20 e 20 da reserva 2 da
   v0.52; v0.53 no commit `4a2620e`): **0 erros, 0 passos com previsão não finita, 0 séries com acréscimo > 1.100 FP,
   estrutura idêntica em todas.** Pela regra do plano, o pré-registro segue para aprovação sem mudanças de código.

Só informação (dados já usados, não é evidência): v0.53 ÷ v0.52, média geométrica, **0,847 nas bacias** (0,645 a 1,017; a
pior, 61267000, 1,017) e 0,997 nos prédios (0,939 a 1,002); acréscimo de custo mediano de 463 FP nas bacias e 378 nos
prédios (máximo 490). Dados: `ensaio_v052.json`.
