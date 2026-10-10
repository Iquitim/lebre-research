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

> **LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*) é um previsor online de um passo à frente para séries temporais com entradas, com custo fixo por passo. O núcleo estrutural aceita cada mudança de estrutura por um teste sequencial sempre válido (e-process) de melhora preditiva; a camada M1 acrescenta um especialista de precisão, e a camada M2 faz a previsão partir de uma referência trivial declarada.
>
> O estado atual é a **LEBRE v0.53**, **promovida** em 09/10/2026 por regra pré-registrada, numa avaliação única em dados reservados antes de qualquer código da v0.53 (nenhuma piora por família; v0.53/v0.52 = 0,955, IC 95% 0,951–0,960, em 104 séries reservadas). Tem limites de escopo declarados: ver `docs/architecture/LEBRE_v0.53_FREEZE_RECORD.md`. A especificação e relatório técnico autocontidos (núcleo + M1 + M2) estão em `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_PTBR.pdf`.

A biblioteca instalável [`lebre`](https://github.com/Iquitim/lebre) (a 0.2.0 implementa a v0.53; a 0.1.0, a v0.52-r1) e o artigo (`paper/`, que descreve a v0.52) remetem a este repositório. O desenvolvimento e as validações da M1 e da M2 foram feitos no [LEBRE Lab](https://github.com/Iquitim/lebre-lab), público.

## Por onde começar

| Objetivo | Onde |
|---|---|
| Entender a LEBRE v0.53 e como foi avaliada | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_PTBR.pdf` (inglês: `…_r1_EN.pdf`) |
| Entender a v0.52, anterior e congelada (o núcleo estrutural) | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_PTBR.pdf` |
| Ler o artigo (em inglês; descreve a v0.52) | `paper/main.pdf` |
| Saber como cada número foi produzido | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) (em inglês) |
| Navegar pelas pastas de experimentos | [`experiments/INDEX.md`](experiments/INDEX.md) |
| Sementes e divisões de dados | [`docs/research/SEEDS.md`](docs/research/SEEDS.md) |
| Configuração canônica | v0.53: [`configs/lebre_v053_canonical.json`](configs/lebre_v053_canonical.json); v0.52: [`configs/lebre_v052_canonical.json`](configs/lebre_v052_canonical.json) |
| Ambiente, ferramentas e dados | [`environment/`](environment/), [`tools/README.md`](tools/README.md), [`data/README.md`](data/README.md) |
| Conferir a integridade dos congelamentos | `python scripts/verify_integrity.py` |
| Conferir que os resultados ainda se regeneram | `python scripts/reproduce_smoke.py` |
| Usar a biblioteca instalável | `pip install lebre` (0.2.0 = v0.53; [repositório](https://github.com/Iquitim/lebre), [doi:10.5281/zenodo.23073983](https://doi.org/10.5281/zenodo.23073983)) |

## Pastas principais

| Pasta | Conteúdo |
|---|---|
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

Lima, S. (2026). *LEBRE research record — v0.53* [Software]. Zenodo. https://doi.org/10.5281/zenodo.23282527

DOIs por versão: v0.53 (promovida) `10.5281/zenodo.23282527`; v0.52-r1 `10.5281/zenodo.23049103`.

O DOI `10.5281/zenodo.23049102` reúne todas as versões e aponta sempre para a mais recente.

Artefatos dos experimentos (conjunto de dados): Lima, S. (2026). *LEBRE research record v0.52-r1: experiment artifacts* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.23082357
