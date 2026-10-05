# Reserva da avaliação final da v0.53 (fixada em 05/10/2026, antes de qualquer código da v0.53)

**Arquivo da reserva:** `SPLIT_V053.json`, com o SHA-256 em `SPLIT_V053_SHA256.txt`.
**Gerado por:** `make_split_v053.py`. Usa só metadados, cobertura (fração de valores não faltantes) e sementes; os valores
das séries reservadas não são inspecionados.
**Cópia dos dados:** `snapshot_v053.py` grava os arquivos brutos em `data/external_v053/` (fora do git) e os SHA-256 em
`SNAPSHOT_SHA256SUMS.txt` (todos os 55 arquivos). A avaliação final usa exatamente esses arquivos. O sorteio foi feito
depois da fase base (35 arquivos), cujo hash está em `SPLIT_V053.json`; essa lista está em
`SNAPSHOT_BASE_SHA256SUMS.txt` e é idêntica às linhas correspondentes da lista completa.
**Sementes novas:** 5311 (solar) e 5312 (eólica), conferidas contra `docs/research/SEEDS.md` e contra as sementes do
LEBRE Lab.

## 1. Por que agora

A v0.53 vai ser desenvolvida com o LEBRE Lab e com os dados de desenvolvimento da v0.52 (nota de desenho 01, seção 4).
Os dados da avaliação final precisam estar separados antes da primeira linha de código, para que nenhuma decisão de
desenvolvimento seja influenciada por eles.

## 2. Famílias reservadas

| Família | Séries | Origem da escolha | Período |
|---|---|---|---|
| Hidrologia (CAMELS-BR) | 30 bacias | Posições 110 a 139 da permutação da v0.52 (semente 5202); as posições 0 a 109 foram usadas no desenvolvimento e nas reservas 1 a 3 | Como na v0.52 |
| Prédios (BDG2) | 30 medidores | Posições 85 a 114 da permutação da v0.52 (semente 5203); as posições 0 a 84 foram usadas | Como na v0.52 |
| Geração solar (ONS) | 8 usinas | Sorteio (semente 5311) entre as elegíveis, excluídas as 6 usadas no Lab | 2024-2025, horário |
| Geração eólica (ONS) | 8 usinas | Sorteio (semente 5312) entre as elegíveis, excluídas as 6 usadas no Lab | 2024-2025, horário |
| Carga elétrica (ONS) | 4 subsistemas | Todos; separação **no tempo**: o Lab usou 2022-2025 | 01/01/2026 a 30/09/2026, horário |
| Câmbio (Fed H.10, domínio público) | 8 pares | Todos os pares de domínio público não usados no Lab: libra, franco suíço, dólar canadense, dólar australiano, peso mexicano, won, coroa sueca, coroa norueguesa | 2010-2025, dias úteis |

**Elegibilidade das usinas (só metadados e cobertura):** tipo Solar ou Eólica no conjunto Fator de Capacidade do ONS,
coordenadas presentes, geração verificada em pelo menos 95% das horas de 2024-2025 e capacidade instalada de pelo menos
100 MW.

**Séries ausentes no arquivo de dados:** se uma bacia ou medidor reservado não tiver dados no arquivo baixado, ele é
substituído pela próxima posição da permutação, e a substituição fica registrada no JSON. Para as usinas, a cobertura
mínima já exclui esse caso.

**Verificação embutida:** o script recalcula as permutações da v0.52 e confere que as posições já consumidas são
exatamente as listas de `SPLIT_V052.json`, `RESERVA2.json` e `RESERVA3.json`. Se não forem, ele para.

## 3. Ressalvas declaradas

- **Carga elétrica é uma separação no tempo, não de séries:** os 4 subsistemas são os mesmos usados no Lab, em outro
  período. É a forma usual de avaliar previsão de carga, mas é mais fraca que séries inéditas.
- **Os arquivos brutos do ONS de 2024-2025 já foram baixados pelo Lab** (o conjunto vem em arquivos mensais com todas as
  usinas). Nenhuma execução usou as usinas reservadas. A cópia da reserva vem desses mesmos arquivos, com os SHA-256
  registrados.
- **Câmbio:** o Lab usou euro, iene e real; as entradas da avaliação final (juros americanos, por exemplo) podem coincidir
  com entradas usadas no Lab. O que é inédito são os alvos.
- **Prédios:** medidores do mesmo site compartilham o clima; na v0.52 isso foi reportado e aceito (sites compartilhados
  com o desenvolvimento). O script reporta quantos casos há.

## 4. Regras de uso

1. Os dados reservados só são carregados na execução final pré-registrada da v0.53. O código de desenvolvimento da v0.53
   chama `reserva_v053.recusar_se_reservado(...)` ao carregar qualquer série, e o LEBRE Lab tem a mesma trava.
2. O pré-registro fixa, antes da execução final, as tarefas exatas de cada família (alvo, entradas, tratamento de falhas),
   os modelos (v0.53, v0.52, SARIMAX com entradas, Chronos-2 com covariáveis) e os critérios.
3. Qualquer mudança nesta reserva depois deste ponto exige nova reserva, com novas sementes e registro do motivo.
