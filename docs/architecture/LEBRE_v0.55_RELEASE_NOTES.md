# LEBRE v0.55 — Notas de versão da documentação

**Data:** 17/10/2026 · **Versão documentada:** v0.55, congelada em `LEBRE-V0.55-FREEZE-01` (`LEBRE_v0.55_FREEZE_RECORD.md`)
· **Status:** versão de pesquisa **promovida** por regra pré-registrada e vinculante, com limites de escopo declarados.

Esta nota **não altera** o congelamento: os 64 arquivos de `LEBRE_v0.55_SHA256SUMS.txt` e os das versões anteriores
conferem (verificador do repositório: aprovado). Ela registra os documentos publicados depois do congelamento.

## 1. Documentos publicados

| Arquivo | Conteúdo |
|---|---|
| `pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_PTBR.pdf` | **Revisão 0 (vigente).** Especificação e relatório técnico autocontidos, em português, 47 páginas |
| `pdf/LEBRE_ARCHITECTURE_v0.55_SPEC_EN.pdf` | **Revisão 0 (vigente).** O mesmo documento em inglês, 41 páginas |

**Documento autocontido desde a primeira edição.** Ele descreve a LEBRE inteira sem supor a leitura de nenhum outro
documento:

- o núcleo estrutural ancorado: unidades externas testadas contra a previsão do núcleo e internas contra a estrutura de
  nível, a estrutura de inovação com a combinação aninhada, o portão suave pela triagem, os pesos de quem aprendeu e a
  escala de uma passada calculada antes de ver o alvo (nova §5.10, com diagrama e pseudocódigo);
- a remoção disparada, o relatório de equivalentes barato, a M1 com dormência e a M2;
- a validade dos e-processes com qualquer aprendiz previsível (nota formal F1, ainda sem conferência independente), a
  errata 01 da nota e o limite conjunto 2α dos dois motores de mudança (§5.6, §5.7);
- a metodologia da v0.55: banco sintético fixo com critérios fixos, confirmação com sementes nunca usadas, validação
  real, avaliação final com entradas placebo como controle negativo e regra vinculante R1–R5, e a comparação externa
  (§14 d);
- o desenvolvimento D1 a D5 e a confirmação C1, com os resultados negativos (§17); a validação da v0.55 (§18); a
  avaliação final da v0.55 (§19.1) e a comparação com 12 modelos externos com correção de Holm (§19.2);
- toda a evidência das versões anteriores (§19.3 a §19.7), a evolução e as ablações, a literatura, os limites, os
  parâmetros e o pseudocódigo.

As versões anteriores aparecem só como evolução e ablações. A estrutura de 26 seções é a mesma da especificação anterior;
o conteúdo novo entra nas seções existentes (§1, §3, §4, §5.6, §5.7, §7, §12, §14, §17 a §24, §26), mais a §5.10 e as
§19.1 e §19.2 (as antigas §19.1 a §19.5 passam a §19.3 a §19.7).

**Princípios de redação (os mesmos de antes):** nenhum número digitado à mão nos resultados da v0.55 (o gerador lê todos
dos arquivos de resultado: avaliação final, validação e comparação da v0.55 neste repositório; rodadas D1 a D4, D5 e C1
no LEBRE Lab público; as evidências anteriores pelos geradores das especificações anteriores); nenhum caminho local; toda
afirmação qualificada pelo escopo testado; nenhum componente declarado original. O gerador recusa o documento se
encontrar caminhos locais ou remissões a outras especificações. Na revisão visual, os números das rodadas D1 a D4 citados
no texto foram conferidos com os resultados do Lab.

## 2. Outros arquivos desta etapa

| Arquivo | Conteúdo |
|---|---|
| `LEBRE_v0.55_FREEZE_RECORD.md`, `..._FREEZE_MANIFEST.yaml`, `..._SHA256SUMS.txt` | Registro de congelamento (código no commit `b0522a0`, variante `B10`) |
| `LEBRE_v0.55_SPEC_SHA256SUMS.txt` | Hashes dos PDFs, HTMLs e do gerador desta especificação |
| `configs/lebre_v055_canonical.json` | Configuração canônica, legível por máquina |

O gerador (`pdf_source/build_v055_spec.py`, `v055_text.py`, `v055_data.py`, `v055_diagrams.py`) importa sem alterar o
modelo visual e os módulos da especificação anterior; `v055_text.py` foi gerado a partir de `v054_text.py` por edições
explícitas. Ele precisa de Python com `pypdfium2` e do Microsoft Edge, e lê o LEBRE Lab pela variável `LEBRE_LAB` (por
padrão, uma pasta irmã `lebre-lab`).
