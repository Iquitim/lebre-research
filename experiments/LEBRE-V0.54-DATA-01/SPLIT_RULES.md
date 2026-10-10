# Reserva da avaliação final da v0.54 (fixada em 10/10/2026, antes de qualquer código da v0.54)

**Arquivo da reserva:** `SPLIT_V054.json`, com o SHA-256 em `SPLIT_V054_SHA256.txt`.
**Gerado por:** `make_split_v054.py`. Usa só metadados, cobertura (fração de valores não faltantes) e sementes; os valores
das séries reservadas não são inspecionados.
**Cópia dos dados:** `snapshot_v054.py` grava os arquivos brutos em `data/external_v054/` (fora do git) e os SHA-256 em
`SNAPSHOT_SHA256SUMS.txt` (69 arquivos). O sorteio foi feito depois da fase base (53 arquivos), cujo hash está em
`SPLIT_V054.json`; essa lista está em `SNAPSHOT_BASE_SHA256SUMS.txt` e é idêntica às linhas correspondentes da lista
completa. Os arquivos do ONS de 2024-2025 (eólica) são os já registrados na reserva da v0.53
(`data/external_v053/ons_fator`, SHA-256 em `LEBRE-V0.53-DATA-01/SNAPSHOT_SHA256SUMS.txt`).
**Sementes novas:** 5421 (eólica) e 5422 (solar), conferidas contra `docs/research/SEEDS.md` e contra os dois repositórios.
**Decisões do responsável pelo projeto (10/10/2026):** níveis não estacionários da EIA e do Tesouro dos EUA; carga fora
da reserva; evidência de remoções (M4) do desenvolvimento e das validações; solar por separação no tempo.

## 1. Por que agora

A v0.54 vai ser desenvolvida com o LEBRE Lab (nota de desenho 01, seção 3). Os dados da avaliação final precisam estar
separados antes da primeira linha de código, para que nenhuma decisão de desenvolvimento seja influenciada por eles.

## 2. Famílias reservadas

| Família | Séries | Origem da escolha | Período |
|---|---|---|---|
| Hidrologia (CAMELS-BR) | 30 bacias | Posições 140 a 169 da permutação da v0.52 (semente 5202); as posições 0 a 139 foram usadas (v0.52, reservas 2 e 3, v0.53) | Como na v0.52 |
| Prédios (BDG2) | 30 medidores | Posições 115 a 144 da permutação da v0.52 (semente 5203); as posições 0 a 114 foram usadas | Como na v0.52 |
| Geração eólica (ONS) | 8 usinas | Sorteio (semente 5421) entre as 48 elegíveis inéditas: excluídas as 36 usadas no Lab e as 8 da reserva da v0.53 | 2024-2025, horário |
| Geração solar (ONS) | 8 usinas | Sorteio (semente 5422) entre as 27 elegíveis; **separação no tempo** | 01/01/2026 a 30/09/2026, horário |
| Níveis não estacionários | 17 séries | Todas as elegíveis: 10 preços à vista diários da EIA (gás natural, gasolinas, diesel, óleo de aquecimento, querosene de aviação, propano) e 7 taxas do Tesouro dos EUA (nominais de 1 e 6 meses; reais de 5, 7, 10, 20 e 30 anos) com cobertura >= 90% dos dias úteis | 2010-2025, dias úteis |

**Elegibilidade das usinas (só metadados e cobertura):** tipo no conjunto Fator de Capacidade do ONS, coordenadas
presentes, geração verificada em pelo menos 95% das horas de 2024-2025 (e, na solar, também de jan-set/2026) e capacidade
instalada de pelo menos 100 MW. A lista das usinas do Lab é a de `lab/usinas.escolher(tipo, n=36)`; o script a reconstrói
e a conferência contra o Lab deu idêntica (36 de 36).

**Níveis excluídos:** WTI (alvo no desenvolvimento do Lab), Brent (quase idêntico ao WTI; os dois ficam disponíveis como
entradas), taxas nominais do Tesouro de 3 meses e de 1 a 30 anos (usadas no Lab).

## 3. Ressalvas declaradas

- **Solar é uma separação no tempo, não de séries:** as usinas solares elegíveis de 2024-2025 foram todas usadas (36 no
  Lab, 8 na reserva da v0.53). Das 8 sorteadas, 2 apareceram no Lab e 4 na reserva da v0.53, sempre com dados de
  2024-2025; os dados de 2026 nunca foram carregados por nenhuma execução (o Lab é travado contra 2026).
- **Níveis:** as entradas (por exemplo, WTI e Brent) podem coincidir com séries vistas no Lab; o que é inédito são os
  alvos. Ao conferir o cabeçalho de um arquivo do Tesouro, uma linha de valores de 2015 (taxas reais) apareceu na tela;
  ela não serve para nenhuma decisão.
- **Prédios:** 8 sites dos medidores reservados compartilham o clima com medidores já usados (Bull, Cockatoo, Eagle, Fox,
  Hog, Moose, Panther, Peacock), como já aceito na v0.52 e na v0.53.
- **Carga e câmbio fora:** a carga de 2026 até setembro foi usada na v0.53, e as moedas flutuantes do H.10 estão
  praticamente esgotadas. A ausência fica como limite declarado.
- **Remoções (M4):** não há verdade conhecida sobre trocas de regime em séries reais; a avaliação final verifica só que
  remover não piora.

## 4. Regras de uso

1. Os dados reservados só são carregados na execução final pré-registrada da v0.54. O código de desenvolvimento da v0.54
   chama `reserva_v054.recusar_se_reservado(...)` ao carregar qualquer série, e o LEBRE Lab tem a mesma trava
   (`lab/reserva_v054.json`).
2. O pré-registro fixa, antes da execução final, as tarefas exatas de cada família (alvo, entradas, tratamento de falhas),
   os modelos (v0.54, v0.53, SARIMAX com entradas, Chronos-2 com covariáveis) e os critérios, inclusive a execução sem
   ciclo declarado para a M6.
3. Qualquer mudança nesta reserva depois deste ponto exige nova reserva, com novas sementes e registro do motivo.
