# LEBRE v0.54 — Notas de versão da documentação

**Data:** 14/10/2026 · **Versão documentada:** v0.54, congelada em `LEBRE-V0.54-FREEZE-01` (`LEBRE_v0.54_FREEZE_RECORD.md`,
adendo 01), com a errata 01 · **Status:** versão de pesquisa **promovida** por regra pré-registrada, com limites de escopo
declarados.

Esta nota **não altera** o congelamento: os 148 arquivos de `LEBRE_v0.54_SHA256SUMS.txt` e os das versões anteriores
conferem (verificador do repositório: aprovado). Ela registra os documentos publicados depois do congelamento.

## 1. Documentos publicados

| Arquivo | Conteúdo |
|---|---|
| `pdf/LEBRE_ARCHITECTURE_v0.54_SPEC_PTBR.pdf` | **Revisão 0 (vigente).** Especificação e relatório técnico autocontidos, em português, 40 páginas |
| `pdf/LEBRE_ARCHITECTURE_v0.54_SPEC_EN.pdf` | **Revisão 0 (vigente).** O mesmo documento em inglês, 38 páginas |

**Documento autocontido desde a primeira edição.** Ele descreve a LEBRE inteira sem supor a leitura de nenhum outro
documento:

- o núcleo estrutural, agora com a remoção disparada (evidência por episódio, orçamento próprio, duração mínima) e o
  relatório de equivalentes barato;
- a M1, com a dormência;
- a M2;
- a teoria, o ciclo de vida, a condição de uso, o custo médio e de pico, a memória e a observabilidade;
- as três metodologias de avaliação: o núcleo na classe de orçamento, M1 e M2 sobre o núcleo, e a v0.54 sobre a versão
  anterior;
- a evidência do núcleo, o desenvolvimento das camadas e da v0.54, as validações 1 a 7, as duas avaliações finais, a
  auditoria de estresse e a errata 01, a evolução e as ablações, a literatura, os limites, todos os parâmetros e o
  pseudocódigo do passo inteiro.

As versões anteriores aparecem só como evolução e ablações. A estrutura de 26 seções é a mesma da especificação anterior;
o conteúdo novo entra nas seções existentes (§3, §4, §5.9, §7, §9, §12, §13, §14, §15, §17 a §20, §22 a §24, §26).

**Princípios de redação (os mesmos de antes):** nenhum número digitado à mão (o gerador lê todos dos arquivos de
resultado: as avaliações finais da v0.54 e da v0.53, a auditoria, as pastas congeladas de resultado da v0.52 para a
evidência do núcleo e o LEBRE Lab público); nenhum caminho local; toda afirmação qualificada pelo escopo testado; nenhum
componente declarado original. O gerador recusa o documento se encontrar caminhos locais ou remissões a outras
especificações.

## 2. Outros arquivos desta etapa

| Arquivo | Conteúdo |
|---|---|
| `LEBRE_v0.54_FREEZE_RECORD.md`, `..._FREEZE_MANIFEST.yaml`, `..._SHA256SUMS.txt` | Registro de congelamento (código no commit `f9906c4`) |
| `LEBRE_v0.54_FREEZE_ADDENDUM_01.md` | Correção de texto: a validação 6 usou 20 séries reais, não 24 |
| `LEBRE_v0.54_SPEC_SHA256SUMS.txt` | Hashes dos PDFs, HTMLs e do gerador desta especificação |
| `configs/lebre_v054_canonical.json` | Configuração canônica, legível por máquina |

O gerador (`pdf_source/build_v054_spec.py`, `v054_text.py`, `v054_data.py`, `v054_diagrams.py`) importa sem alterar o
modelo visual e os módulos da especificação anterior. Ele precisa de Python com `pypdfium2` e do Microsoft Edge, e lê o
LEBRE Lab pela variável `LEBRE_LAB` (por padrão, uma pasta irmã `lebre-lab`).
