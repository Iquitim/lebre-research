# LEBRE v0.56 — Regras dos dados de validação e da avaliação final (commitadas antes de qualquer download)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DATA-01` · Fonte das bacias novas: `FONTE_BACIAS_NOVAS.md`.

## 1. Princípios (os mesmos das versões anteriores)

- **Só metadados, cobertura e sementes.** Nenhum valor de série é inspecionado antes da execução pré-registrada.
  Cobertura (fração de valores não faltantes) é calculada sem olhar os valores.
- **Ordem:** (1) estas regras, commitadas; (2) download e SHA-256 dos arquivos brutos; (3) sorteio pelos scripts, com o
  resultado e o seu SHA-256 commitados; (4) pré-registro da validação e da avaliação final, commitado; (5) validação;
  (6) avaliação final.
- **Trava:** o carregador recusa qualquer série fora do sorteio registrado.
- **Nada de ajuste depois:** se uma regra não puder ser aplicada como escrita, a falha é registrada e a correção, se
  houver, é declarada e commitada antes de qualquer previsão.

## 2. Famílias

| Família | Uso | Séries | Origem e sorteio | Período |
|---|---|---|---|---|
| `camels_cl` | validação e final | até 20 + 30 | CAMELS-CL 2018 (PANGAEA, CC-BY-4.0). Elegíveis pela §3; permutação dos IDs elegíveis ordenados, semente **5662**. **Final: posições 0–29; validação: posições 30–49.** Com menos de 50 elegíveis, a final tem prioridade e a validação fica com o que sobrar; com menos de 30, todas vão para a final e não há validação de bacias. | 01/01/1990 a 31/12/2015, diário |
| `bdg2` | validação e final | 30 + 30 | BDG2, mesma regra de elegibilidade e permutação da v0.52 (semente 5203). **Validação: posições 205–234; final: 235–264.** As posições 0–204 foram usadas. | como na v0.52 |
| `eolica` | final | 8 | usinas eólicas do ONS, mesma regra de elegibilidade da v0.54 e da v0.55, entre as 32 elegíveis ainda não usadas (as 40 da v0.55 menos as 8 da reserva da v0.55); semente **5663** | 2024–2025, horário |
| `solar` | final | 8 | usinas solares do ONS, mesma regra da v0.55, entre as elegíveis de 2026 ainda não usadas (as 19 da v0.55 menos as 8 da reserva da v0.55); semente **5664**; separação no tempo (os dados de 2026 dessas usinas nunca foram carregados como série) | 01/01/2026 a 30/09/2026, horário |
| `camels_br` | final (família secundária) | 17 | CAMELS-BR, posições 220–236 da permutação da v0.52 (semente 5202), as últimas nunca usadas | como na v0.52 |

**Sem família de níveis:** pelas regras existentes, não restam séries de níveis inéditas com cobertura (a coroa
islandesa do BCE e as taxas de commercial paper do Fed falharam na cobertura da v0.55). Isso é um limite declarado da
avaliação. A mudança da v0.56 não altera nenhuma decisão de estrutura (verificado em `LEBRE-V0.56-DEV-01`), e foram
as decisões de estrutura que motivaram as famílias de níveis.

**Sem rios do ONS:** as séries elegíveis já foram todas usadas.

## 3. Elegibilidade das bacias do CAMELS-CL

Os critérios de bacia "quase natural" do artigo de referência (Alvarez-Garreton et al., 2018, §3.2.5), todos lidos do
arquivo de atributos:
- nenhuma grande barragem (indicador = 0);
- grau de intervenção (vazão anual alocada a direitos consuntivos superficiais ÷ vazão média anual) < 0,10;
- fração impermeável < 0,05;
- fração de cultivo < 0,20;
- fração de plantação florestal exótica < 0,20;
- fração glaciar < 0,05.

Cobertura, calculada nos arquivos de séries sem inspecionar valores:
- **vazão (mm/dia)** válida em ≥ 85% dos dias de 1990 a 2015 (o artigo usa 85% de 1990–2010 para o subconjunto quase
  natural);
- **precipitação MSWEP, evapotranspiração potencial (Hargreaves) e temperatura média (CR2MET)** válidas em ≥ 99% dos dias
  de 1990 a 2015.

Os nomes exatos das colunas serão lidos do cabeçalho do arquivo de atributos. O mapeamento de cada critério acima para
uma coluna será registrado no script do sorteio, antes de calcular a elegibilidade. Se algum critério não tiver coluna
correspondente, isso será registrado e o critério ficará de fora, sem substituto.

**Entradas** (todas do mesmo dia, como no CAMELS-BR): precipitação MSWEP, evapotranspiração potencial (Hargreaves) e
temperatura média (CR2MET). Diferença declarada: o CAMELS-BR usa evapotranspiração **real** (GLEAM). Sem ciclo
declarado, referência "persistence", como nas bacias brasileiras.

## 4. Arquivos a baixar

Do depósito https://doi.pangaea.de/10.1594/PANGAEA.894885, só:
- `1_CAMELScl_attributes.zip`;
- `3_CAMELScl_streamflow_mm.zip`;
- `6_CAMELScl_precip_mswep.zip`;
- `10_CAMELScl_tmean_cr2met.zip`;
- `12_CAMELScl_pet_hargreaves.zip`.

Eles ficam em `data/external_v056/camels_cl/`, fora do git, com SHA-256 em `SNAPSHOT_SHA256SUMS.txt`. Atribuição em
NOTICE: "Source: CAMELS-CL (Alvarez-Garreton et al., 2018), CC-BY-4.0". As demais famílias usam os arquivos brutos já
registrados (BDG2, ONS e CAMELS-BR), com o SHA-256 conferido antes do sorteio.

## 5. Controle negativo

As duas entradas placebo da v0.55 (passeios aleatórios gaussianos independentes) em todas as séries da avaliação final,
com semente nova a declarar no pré-registro.
