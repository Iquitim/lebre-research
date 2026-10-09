# LEBRE v0.53 — Notas de versão da documentação

**Data:** 09/10/2026 · **Versão documentada:** v0.53, congelada em `LEBRE-V0.53-FREEZE-01` (`LEBRE_v0.53_FREEZE_RECORD.md`,
adendo 01) · **Status:** versão de pesquisa **promovida** por regra pré-registrada, com limites de escopo declarados.

Esta nota **não altera** o congelamento: os 177 arquivos de `LEBRE_v0.53_SHA256SUMS.txt` e os das versões anteriores conferem
(verificador do repositório: aprovado). Ela registra os documentos publicados depois do congelamento.

## 1. Documentos publicados

| Arquivo | Conteúdo |
|---|---|
| `pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_PTBR.pdf` | Especificação e relatório técnico em português, 17 páginas |
| `pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_EN.pdf` | A mesma especificação e relatório em inglês, 17 páginas |

**Princípios de redação (os mesmos da v0.52):** nenhum número digitado à mão (o gerador lê todos dos arquivos de resultado,
deste repositório e do LEBRE Lab público); nenhum caminho local; toda afirmação qualificada pelo escopo testado; nenhum
componente declarado original. A v0.52 aparece resumida e é descrita por inteiro na sua especificação, revisão 1.

**Estrutura (16 seções):** sumário executivo; ponto de partida (F6 e F8); arquitetura (D1); M1; M2 e o limite dos choques;
custo auditado; metodologia (régua por decidibilidade, adendos, F6, promoção); desenvolvimento (D2: desenhos e falhas);
validações (com a errata do ciclo); avaliação final (resultados por família, tetos de referência); limites; literatura;
parâmetros; pseudocódigo e reprodutibilidade; referências; histórico de revisões.

## 2. Outros arquivos desta etapa

- `configs/lebre_v053_canonical.json`: configuração canônica da v0.53.
- `REPRODUCIBILITY.md`, seção 8; `experiments/INDEX.md`; `docs/research/SEEDS.md`; `README.md`; `docs/README.md`.
- `LEBRE_v0.53_SPEC_SHA256SUMS.txt`: hashes dos PDFs, HTMLs e do gerador.
- O LEBRE Lab foi publicado (https://github.com/Iquitim/lebre-lab); o documento registra o commit do Lab que leu.

## 3. Reprodução dos PDFs

`python docs/architecture/pdf_source/build_v053_spec.py` (Microsoft Edge para a impressão, internet para o KaTeX, e uma
cópia do LEBRE Lab, indicada por `LEBRE_LAB` ou como pasta irmã `lebre-lab`). Como na v0.52, os bytes dos PDFs não são
reprodutíveis (os gráficos guardam a data de geração); o conteúdo e os números são.
