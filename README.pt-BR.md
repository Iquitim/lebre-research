# lebre-research — registro de pesquisa do previsor online LEBRE

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23049102.svg)](https://doi.org/10.5281/zenodo.23049102)

Este repositório responde a uma pergunta: **como os resultados da LEBRE foram obtidos?** Ele guarda o registro completo:
- implementações;
- scripts de experimento;
- pré-registros;
- resultados;
- versões congeladas com manifestos SHA-256;
- documentos;
- ferramentas para reexecutar tudo.

> **LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*) é um previsor online de um passo à frente para séries temporais com entradas, com custo fixo por passo. O núcleo estrutural aceita cada mudança de estrutura por um teste sequencial sempre válido (e-process) de melhora preditiva — inclusive remoções — contra a previsão que cada unidade pode melhorar (entradas externas contra a previsão do núcleo, que já contém o passado do próprio alvo); a camada M1 acrescenta um especialista de precisão que dorme enquanto não tem peso, e a camada M2 faz a previsão partir de uma referência trivial declarada.
>
> O estado atual é a **LEBRE v0.55**, **promovida** em 17/10/2026 por regra pré-registrada e vinculante, numa avaliação única em uma reserva nova de 84 séries (nenhuma família pior que a v0.54 além da margem, razões de 0,993 a 1,008; entradas placebo, passeios aleatórios, na estrutura final em 0 de 84 séries, contra 4 na v0.54; custo mediano por série de 0,989 vez o da v0.54). Tem limites de escopo declarados (piora pequena e significativa nas bacias, onde um ARX de mínimos quadrados recursivos da mesma classe de custo é melhor): ver `docs/architecture/LEBRE_v0.55_FREEZE_RECORD.md`. A especificação e relatório técnico autocontidos estão em `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_PTBR.pdf`. A versão anterior, v0.54 (promovida em 13/10/2026), continua congelada.

A biblioteca instalável [`lebre`](https://github.com/Iquitim/lebre) (a 0.3.0 implementa a v0.54; a 0.2.0, a v0.53; a 0.1.0, a v0.52-r1) e o artigo (`paper/`, que descreve a v0.52) remetem a este repositório. O desenvolvimento e as validações da v0.53, da v0.54 e da v0.55 foram feitos no [LEBRE Lab](https://github.com/Iquitim/lebre-lab), público.

## Por onde começar

| Objetivo | Onde |
|---|---|
| Entender a LEBRE v0.55 e como foi avaliada | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_PTBR.pdf` (inglês: `…_v0.55_SPEC_EN.pdf`) |
| Entender a v0.52, anterior e congelada (o núcleo estrutural) | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_PTBR.pdf` |
| Ler o artigo (em inglês; descreve a v0.52) | `paper/main.pdf` |
| Saber como cada número foi produzido | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) (em inglês) |
| Navegar pelas pastas de experimentos | [`experiments/INDEX.md`](experiments/INDEX.md) |
| Sementes e divisões de dados | [`docs/research/SEEDS.md`](docs/research/SEEDS.md) |
| Configuração canônica | v0.55: [`configs/lebre_v055_canonical.json`](configs/lebre_v055_canonical.json); v0.54: [`configs/lebre_v054_canonical.json`](configs/lebre_v054_canonical.json); v0.53: [`configs/lebre_v053_canonical.json`](configs/lebre_v053_canonical.json); v0.52: [`configs/lebre_v052_canonical.json`](configs/lebre_v052_canonical.json) |
| Ambiente, ferramentas e dados | [`environment/`](environment/), [`tools/README.md`](tools/README.md), [`data/README.md`](data/README.md) |
| Conferir a integridade dos congelamentos | `python scripts/verify_integrity.py` |
| Conferir que os resultados ainda se regeneram | `python scripts/reproduce_smoke.py` |
| Usar a biblioteca instalável | `pip install lebre` (0.2.0 = v0.53; [repositório](https://github.com/Iquitim/lebre), [doi:10.5281/zenodo.23073983](https://doi.org/10.5281/zenodo.23073983)) |

## Pastas principais

| Pasta | Conteúdo |
|---|---|
| `experiments/LEBRE-V0.55-PROTO-01/` | Implementação em Python da v0.55, congelada no commit `b0522a0`, variante `B10` (a v0.54 copiada byte a byte de `f9906c4`; o núcleo ancorado em `anchored.py`). Congelada. |
| `experiments/LEBRE-V0.55-FINAL-01/` | Avaliação final pré-registrada da v0.55, com entradas placebo como controle negativo. |
| `experiments/LEBRE-V0.55-COMP-01/` | Comparação com 12 modelos externos (só referência). |
| `experiments/LEBRE-V0.54-PROTO-01/` | Implementação em Python da v0.54, congelada no commit `f9906c4` (código promovido `cfe72ce` + errata 01; os arquivos da v0.53 são cópias byte a byte da `lebre==0.2.0`). Congelada. |
| `experiments/LEBRE-V0.54-FINAL-01/` | Avaliação final pré-registrada da v0.54 e errata 01. |
| `experiments/LEBRE-V0.54-AUDIT-01/` | Auditoria de estresse da v0.54, depois da promoção. |
| `experiments/LEBRE-V0.53-PROTO-01/` | Implementação em Python da v0.53, promovida no commit `4a2620e` (os arquivos do núcleo são cópias byte a byte da `lebre==0.1.0`). Congelada. |
| `experiments/LEBRE-V0.53-FINAL-01/` | Avaliação final pré-registrada da v0.53. |
| `experiments/LEBRE-V0.52-PROTO-01/` | Implementação de referência da v0.52 (o núcleo). Congelada. |
| `experiments/LEBRE-V0.52-EXT-01/lebre_c/` | Porte em C99 do núcleo e o firmware do Cortex-M4F simulado (Renode). A M1 e a M2 não têm porte em C. |
| `docs/architecture/` | Especificações, registros de congelamento, manifestos SHA-256, notas de versão e os geradores dos PDFs. |
| `packages/lebre/` | Retrato da biblioteca `lebre` 0.1.0; a biblioteca é desenvolvida em https://github.com/Iquitim/lebre. |

## Por que os arquivos não foram movidos

Os congelamentos são conferidos por manifestos SHA-256 com caminhos relativos, e os scripts se importam entre pastas por caminhos relativos. Mover arquivos quebraria as duas coisas. Por isso a organização é feita por índices, não por realocação.

## O que fica fora do git

Os arquivos abaixo estão listados com tamanho e SHA-256 em `docs/research/ARTIFACTS_MANIFEST.tsv` (802 arquivos, cerca de 3 GB):
- dados brutos;
- previsões por série (`*.npz`);
- pacotes de ferramentas;
- binários de firmware e de compilação;
- quatro registros de eventos muito grandes.

As saídas dos experimentos são publicadas num arquivo separado, [doi:10.5281/zenodo.23082357](https://doi.org/10.5281/zenodo.23082357) (oito partes `lebre-research-v0.52-r1-artifacts-part*.zip`, geradas por `scripts/make_artifact_archive.py`; conteúdo em `docs/research/ARCHIVE_CONTENTS.tsv`). Os dados brutos são baixados das fontes originais e as ferramentas são instaladas conforme `environment/TOOLCHAIN.md`. Passo a passo em `REPRODUCIBILITY.md`, seção 0 (em inglês).

## Status e limites

**v0.55** (registro de congelamento, §5; especificação, §22):
- Previsão de um passo. Nas bacias, piora pequena e significativa contra a v0.54 (1,008, IC 95% 1,003–1,014, dentro da margem de 1,02), e um ARX com mínimos quadrados recursivos da mesma classe de custo erra 11% a 13% menos (comparação externa, só referência).
- O ganho de levar a informação de uma entrada verdadeira à previsão em séries integradas foi mostrado só em sintéticos; nas séries de níveis reais do BCE, não apareceu (1,000).
- Relações reais fracas são registradas como estrutura mais devagar (menos séries terminam com entrada externa).
- A nota formal F1 (validade com qualquer aprendiz previsível) tem autor único e ainda não teve conferência independente; a errata 01 dela registra que a escala dos testes da v0.54 não era estritamente previsível. O limite conjunto das mudanças de estrutura é 2α (dois motores); o controle de mudanças falsas estruturais continua empírico.
- Memória e custo são estimados pelo modelo analítico, não medidos em microcontrolador. Nenhum componente é original.

**v0.54** (registro de congelamento, §5; especificação, §22):
- Previsão de um passo. A v0.54 mantém a precisão da v0.53 (0,989 a 1,000 por família) e custa menos onde a M1 não tem peso; onde a M1 ajuda (bacias), o custo é o mesmo. O corte de 30% citado como exemplo na nota de desenho não foi atingido.
- Uma relação que some por mais de ~5.200 passos e volta é removida e precisa ser redetectada: +5% a +10% de erro em séries com esse padrão (declarado na errata 01, sem correção).
- Entradas espúrias em séries de níveis continuam aceitas (M3 fica para a v0.55); o ciclo continua precisando ser declarado (M6 ficou fora).
- O relatório de equivalentes barato elevava o pico de custo por passo com muitas entradas no código promovido; a errata 01 corrigiu, com previsões idênticas.
- A lista de eventos cresce sem limite (já na v0.53). Nenhum componente é original.

**v0.53** (registro de congelamento, §5; especificação, §22):
- Previsão de um passo. O ganho veio de bacias e câmbio; em solar, eólica e carga a v0.53 é idêntica à v0.52.
- Custa mais que a v0.52 em todas as séries: na avaliação final, +476 operações por passo na mediana (máximo +918, dentro do teto pré-registrado de 1.100), total mediano de 919, cerca do dobro da v0.52.
- A evidência da fronteira precisão × custo (F6) em dados novos vem de uma validação; a memória (~83 KB) é estimada.
- Sem garantia formal de erro na escala original para a M1 e a M2; os adendos do choque na régua de avaliação foram decididos durante o desenvolvimento.
- Nenhum componente é original.

**v0.52-r1** (o núcleo estrutural):
- Resultados em dois domínios (hidrologia e prédios), com 1 a 5 entradas, previsão de um passo.
- O contrato de custo declarado **não foi cumprido** (+3,7% na média, +2,0% no pico).
- Os resultados de microcontrolador vêm de um **simulador**.
- O mecanismo de testes **não** melhorou a precisão em relação a ligar todas as entradas.
- O núcleo do mecanismo **não é original**.

## Licença

- **Código:** Apache-2.0.
- **Documentos, relatórios, figuras e tabelas de resultados:** CC-BY-4.0.
- **Exceções:** dados de terceiros mantêm as licenças originais; o logo fica fora das duas licenças.

Detalhes em `NOTICE`.

## Citação

Lima, S. (2026). *LEBRE research record — v0.54* [Software]. Zenodo. https://doi.org/10.5281/zenodo.23376152

DOIs por versão: v0.54 (promovida, com a errata 01) `10.5281/zenodo.23376152`; v0.53 (promovida) `10.5281/zenodo.23282527`; v0.52-r1 `10.5281/zenodo.23049103`.

O DOI `10.5281/zenodo.23049102` reúne todas as versões e aponta sempre para a mais recente.

Artefatos dos experimentos (conjunto de dados): Lima, S. (2026). *LEBRE research record v0.52-r1: experiment artifacts* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23082357
