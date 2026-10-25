# Adendo 01 das regras dos dados da v0.56: a segunda validação (commitado antes de calcular)

**Data:** 25/10/2026.

**Motivo:** a primeira candidata (C5) não passou na validação (`LEBRE-V0.56-VAL-01`). As 20 bacias chilenas daquela
validação e os 30 prédios dela foram depois usados no desenvolvimento da nova candidata (D4, `LEBRE-V0.56-DEV-02`) e não
servem mais como validação. A nova candidata precisa de uma validação em séries nunca tocadas.

**Regra:** as séries seguintes das mesmas permutações já registradas, com as mesmas regras de elegibilidade, a mesma
construção e a mesma trava.

| Família | Séries | Origem |
|---|---|---|
| `camels_cl` | 20 | posições **50–69** da permutação das 103 bacias elegíveis registrada em `SPLIT_V056.json` (campo `permutacao`, semente 5662) |
| `bdg2` | 30 | posições **265–294** da permutação da v0.52 (semente 5203) |

- Nenhuma dessas séries está na reserva final (posições 0–29 do CAMELS-CL; 235–264 do BDG2), nem foi usada antes.
- Ficam nunca usadas, depois deste adendo, as posições 70–102 do CAMELS-CL e 295 em diante do BDG2.
- O resultado vai em `SPLIT_V056_VAL2.json`, com SHA-256, gerado por `make_split_v056_val2.py`. O carregador
  (`dados_v056.py`) passa a aceitar também essas séries, só para o uso "validacao2".
- A reserva final e o seu sorteio (`SPLIT_V056.json`) não mudam.
