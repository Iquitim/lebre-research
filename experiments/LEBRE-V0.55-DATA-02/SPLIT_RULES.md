# Reserva da avaliação final da v0.55: regras (commitadas antes de baixar ou sortear qualquer coisa)

**Data:** 17/10/2026. **Pedido do responsável:** "máximo de cautela; pode pegar qualquer dado global público disponível
que faça sentido para validar".

**O que é avaliado:** a candidata B10, congelada em `b0522a0` (`experiments/LEBRE-V0.55-PROTO-01`). Ela passou na rodada
D5 e na confirmação C1 do banco fixo do LEBRE Lab, e na validação em séries reais (`experiments/LEBRE-V0.55-VAL-01`).

**Princípios:**
- **Só metadados, cobertura e sementes.** Os valores das séries não são inspecionados antes da execução final. Cobertura
  é a fração de valores não faltantes.
- **Cópia dos dados com SHA-256 antes do sorteio.** Os arquivos brutos ficam em `data/external_v055/`, fora do git.
- **Nenhuma série ou período já usado** por qualquer avaliação, validação ou desenvolvimento como alvo.

## 1. Famílias

| Família | Séries | Origem | Período |
|---|---|---|---|
| camels | 30 bacias CAMELS-BR | posições 190 a 219 da permutação da v0.52 (semente 5202). As posições 0 a 189 foram usadas (a última, 170–189, na validação da v0.55) | como na v0.52 |
| bdg2 | 30 medidores BDG2 | posições 175 a 204 da permutação da v0.52 (semente 5203). As posições 0 a 174 foram usadas | como na v0.52 |
| eolica | 8 usinas eólicas do ONS | sorteio, semente **5521**, entre as elegíveis inéditas: as da v0.54 (sem as 36 do Lab e as 8 da reserva da v0.53), menos as 8 da reserva da v0.54 | 2024–2025, horário |
| solar | 8 usinas solares do ONS | sorteio, semente **5522**, entre as elegíveis de 2026 da v0.54, menos as 8 da reserva da v0.54. **Separação no tempo** (os dados de 2026 dessas usinas nunca foram carregados) | 01/01/2026 a 30/09/2026, horário |
| niveis_cp | 6 taxas de commercial paper do Fed (H.15), via FRED, nunca usadas | todas as elegíveis com cobertura ≥ 90% dos dias úteis: DCPN30, DCPN2M, DCPN3M (AA não financeiras), DCPF1M, DCPF2M, DCPF3M (AA financeiras) | 2010–2025, dias úteis |
| niveis_ecb | taxas de referência do euro (BCE) para moedas fora do H.10 do Fed, nunca usadas | todas as elegíveis com cobertura ≥ 90%: PLN, CZK, HUF, RON, ISK, TRY, IDR, PHP, ILS | 2010–2025, dias úteis |

**Entradas das famílias de níveis** (todas com um dia útil de atraso, só passado):
- **niveis_cp:** taxa efetiva de fed funds (DFF) e letra do Tesouro de 3 meses (DTB3), via FRED, ambas de domínio público;
- **niveis_ecb:** EUR/USD, EUR/GBP, EUR/JPY e EUR/CHF do BCE.

Algumas entradas coincidem com séries vistas antes. O que é inédito são os alvos.

**Elegibilidade das usinas:** a mesma regra da v0.54 (`LEBRE-V0.54-DATA-01/make_split_v054.py`, `usinas()`): tipo no
conjunto Fator de Capacidade do ONS, coordenadas, geração verificada em ≥ 95% das horas, capacidade ≥ 100 MW; na solar,
também ≥ 95% de jan–set/2026. A lista do Lab é reconstruída pela mesma regra.

## 2. Controle negativo (placebo) em todas as séries

Cada série é rodada duas vezes:
1. **Execução principal:** as entradas reais. É a base dos critérios de precisão.
2. **Execução placebo:** as entradas reais mais **duas entradas placebo**. São passeios aleatórios gaussianos
   independentes, gerados com a semente `[2026102500, índice da família, índice da série]`, nunca usada, e sem nenhuma
   relação com a série. Uma placebo na estrutura final é, por construção, uma descoberta falsa medida em dados reais.

## 3. Licenças

- CAMELS-BR: CC BY 4.0;
- BDG2: CC BY 4.0;
- ONS: CC BY;
- Open-Meteo (ERA5): CC BY 4.0;
- FRED, séries do Board of Governors: "Public Domain: Citation Requested", conferido na página da série;
- BCE: reuso livre com citação da fonte ("Source: ECB statistics") e sem modificar as estatísticas, conforme a "Policy
  regarding the reuse of ESCB statistics", conferida na página do BCE em 17/10/2026.

Os dados brutos não são redistribuídos.

## 4. Ressalvas declaradas antes

- **Solar:** separação no tempo, como na v0.54. As usinas podem ter aparecido no Lab com dados de 2024–2025.
- **Prédios:** sites que compartilham o clima com medidores já usados são aceitos, como antes.
- **Níveis:** não há verdade conhecida sobre a relação real entre as entradas e os alvos. O ganho em séries integradas é
  reportado, e o controle placebo é o teste de interpretação.
- **Ficam de fora:** câmbio do H.10 (esgotado) e carga (usada na v0.53).

## 5. Ordem

1. Estas regras: commit.
2. `snapshot_v055.py base`: FRED, BCE e conferência dos arquivos do ONS já registrados. SHA-256.
3. `make_split_v055.py`: sorteio e cobertura. `SPLIT_V055.json` e SHA-256.
4. `snapshot_v055.py tempo`: Open-Meteo nos locais das usinas sorteadas. SHA-256.
5. Pré-registro da avaliação final, com a regra de promoção vinculante, e os scripts: commit.
6. Uma única execução.
