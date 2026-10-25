# Segunda validação da v0.56 (candidata D4): resultado

**Data:** 25/10/2026 · **Pré-registro:** `PREREG_V056_VAL2.md` (commit `678820d`, antes da execução) · **Números:**
`VAL2_RESULTADO.json`.

## Resultado: **não passou**

| Família | Séries | D4 ÷ v0.55 [IC 95%] | Janela curta | Custo | Critério | |
|---|---|---|---|---|---|---|
| `camels_cl` (bacias do Chile, nunca usadas) | 20 | **0,900 [0,882; 0,915]** | 0,986 | 1,045 | V1: limite superior < 1,00 | **passa** |
| `bdg2` (prédios, nunca usados) | 30 | **1,200 [1,009; 1,250]** | — | 1,030 | V2: limite superior ≤ 1,02 | **falha** |

- Nenhuma previsão não finita a mais; custo mediano 1,044 (p95 1,22); a M1 atualizou 31% dos alvos (mediana); estrutura
  idêntica à da v0.55 nas 50 séries.
- A falha nos prédios vem de **uma série catastrófica**: no medidor `chilledwater:Hog_office_Shawna`, a D4 erra **255
  vezes** mais que a v0.55. A previsão chegou a 107.147, com o alvo no máximo em 732. Os 10 piores passos somam 99,4% do
  erro da D4 nessa série; sem eles, a razão ainda é 1,64. As demais piores séries: bacias 4533002 (1,187), 4522002
  (1,057), 7350003 (1,055); o prédio Cockatoo_education_Christi (1,034).

**Consequência, pelo pré-registro:** a avaliação final **não é executada**, a reserva continua lacrada, e a decisão volta
ao responsável pelo projeto.

## Diagnóstico da série catastrófica (exploratório, só nesta série já gasta)

1. **Defeito latente da M1, presente também na v0.55.** Na escolha das entradas, a M1 padroniza o passado do alvo pela
   variância daquele momento. Nesse medidor, o alvo estava **parado em zero** na hora da escolha (aparelho desligado). A
   variância ficou praticamente nula (o piso é 1e-24), e quando o consumo voltou, os valores padronizados ficaram
   gigantescos. A previsão da M1 saltou para −2.224 (passo 2.722) e −103.695 (passo 2.723). Em seguida, a matriz do RLS
   perdeu a positividade e foi reiniciada, com ganho alto, o que repetiu a explosão mais tarde (passo 3.537: −23.380).
2. **A D4 tirou a proteção que escondia o defeito.** Na v0.55, o recorte da previsão da M1 em torno da previsão do
   núcleo (L ± 2·max(σ̂_L, piso)) contém esse tipo de explosão. Sem o recorte, ela chega à saída. O recorte é uma
   **segurança**, e foi removido por evidência de precisão (nas bacias) sem um teste de segurança equivalente nos prédios.

## Leitura

- **O ganho nas bacias novas é real e grande:** 10% nas bacias chilenas nunca usadas, com IC bem abaixo de 1. O estudo sob
  demanda funcionou onde se esperava.
- **A segurança falhou:** um defeito antigo, que o recorte escondia, apareceu num prédio com alvo parado em zero.
- Uma candidata corrigida precisa: (a) corrigir a padronização da M1 (um piso de variância relativo à escala do alvo, não
  absoluto); (b) manter uma segurança na saída da M1 (o recorte, possivelmente mais largo); (c) ser testada contra alvos
  que param e voltam, nos prédios e nos sintéticos de dados faltantes e sensor travado.
