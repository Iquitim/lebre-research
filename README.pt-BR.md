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

O estado documentado atual é a **LEBRE v0.52, especificação revisão 1 ("v0.52-r1")**: versão de pesquisa congelada, **não promovida**, com limites de escopo declarados.

## Por onde começar

| Objetivo | Onde |
|---|---|
| Entender a LEBRE v0.52 e o que foi medido | `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_PTBR.pdf` |
| Saber como cada número foi produzido | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) (em inglês) |
| Navegar pelas pastas de experimentos | [`experiments/INDEX.md`](experiments/INDEX.md) |
| Sementes e divisões de dados | [`docs/research/SEEDS.md`](docs/research/SEEDS.md) |
| Configuração canônica | [`configs/lebre_v052_canonical.json`](configs/lebre_v052_canonical.json) |
| Ambiente, ferramentas e dados | [`environment/`](environment/), [`tools/README.md`](tools/README.md), [`data/README.md`](data/README.md) |
| Conferir a integridade dos congelamentos | `python scripts/verify_integrity.py` |
| Conferir que os resultados ainda se regeneram | `python scripts/reproduce_smoke.py` |

## Por que os arquivos não foram movidos

Os congelamentos são conferidos por manifestos SHA-256 com caminhos relativos, e os scripts se importam entre pastas por caminhos relativos. Mover arquivos quebraria as duas coisas. Por isso a organização é feita por índices, não por realocação.

## O que fica fora do git

Os arquivos abaixo estão listados com tamanho e SHA-256 em `docs/research/ARTIFACTS_MANIFEST.tsv` (802 arquivos, cerca de 3 GB):
- dados brutos;
- previsões por série (`*.npz`);
- pacotes de ferramentas;
- binários de firmware e de compilação;
- quatro registros de eventos muito grandes.

Eles devem ir para um arquivo permanente (por exemplo, Zenodo). A cópia restaurada é conferida com `python scripts/make_artifact_manifest.py --check`.

## Licença

- **Código:** Apache-2.0.
- **Documentos, relatórios, figuras e tabelas de resultados:** CC-BY-4.0.
- **Exceções:** dados de terceiros mantêm as licenças originais; o logo fica fora das duas licenças.

Detalhes em `NOTICE`.

## Citação

Lima, S. (2026). *LEBRE research record — v0.52-r1* [Software]. Zenodo. https://doi.org/10.5281/zenodo.23049103

O DOI `10.5281/zenodo.23049102` reúne todas as versões e aponta sempre para a mais recente.
