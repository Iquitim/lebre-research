# Validação da v0.56: resultado

**Data:** 25/10/2026 · **Pré-registro:** `PREREG_V056_VAL.md` (commit `bd8694c`); scripts no commit `6c32263`; errata
do texto em `RUN_NOTAS.md`, §1, registrada antes da leitura · **Números:** `VAL_RESULTADO.json`.

## Resultado: a validação **não passou**

| Família | Séries | C5 ÷ v0.55 [IC 95%] | Janela curta | Custo | Critério | |
|---|---|---|---|---|---|---|
| `camels_cl` (bacias do Chile, nunca usadas) | 20 | **0,988 [0,969; 1,005]** | 0,994 | 0,957 | V1: limite superior < 1,00 | **falha** |
| `bdg2` (prédios, nunca usados) | 30 | 0,989 [0,983; 0,995] | — | 0,983 | V2: limite superior ≤ 1,02 | passa |

- Nenhuma previsão não finita a mais; custo mediano 0,963.
- A estrutura final é idêntica entre a v0.55 e a C5 nas 50 séries, como esperado pela construção.
- Piores séries (todas bacias do Chile): 4503001 1,135; 8351001 1,047; 8317001 1,044; 10364001 1,041; 4703002 1,039.
- A janela curta de um medidor (Hog_education_Casandra) não é finita (erro zero nas duas versões entre os passos 200 e
  2.000). É descritivo e não entra em critério.

**Consequência, pelo pré-registro:** a avaliação final **não é executada**, a reserva final continua lacrada, e a decisão
volta ao responsável pelo projeto.

## Leitura

- Nas bacias brasileiras usadas no desenvolvimento, a C5 melhorava de 5% a 7%. Nas bacias chilenas novas, a melhora
  estimada é de 1,2%, e o IC inclui 1. O ganho nas bacias **não se generalizou com a força esperada**. Este era o risco
  registrado na verificação (`LEBRE-V0.56-DEV-01/RUN_NOTAS.md`, §4): a direção da correção foi achada e replicada em
  bacias já olhadas.
- As bacias chilenas diferem das brasileiras em pontos conhecidos antes da execução, não investigados: entram com
  evapotranspiração potencial em vez da real, têm outro regime climático (neve no centro e no sul) e outro clima de
  precipitação. Não se sabe qual desses pontos, se algum, explica a diferença.
- Nos prédios novos, a C5 melhora 1,1% com IC abaixo de 1, o que é consistente com o banco de desenvolvimento.
