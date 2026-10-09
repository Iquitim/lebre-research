# LEBRE v0.53 — Notas de versão da documentação

**Data:** 09/10/2026 · **Versão documentada:** v0.53, congelada em `LEBRE-V0.53-FREEZE-01` (`LEBRE_v0.53_FREEZE_RECORD.md`,
adendo 01) · **Status:** versão de pesquisa **promovida** por regra pré-registrada, com limites de escopo declarados.

Esta nota **não altera** o congelamento: os 177 arquivos de `LEBRE_v0.53_SHA256SUMS.txt` e os das versões anteriores conferem
(verificador do repositório: aprovado). Ela registra os documentos publicados depois do congelamento.

## 1. Documentos publicados

| Arquivo | Conteúdo |
|---|---|
| `pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_PTBR.pdf` | **Revisão 1 (vigente).** Especificação e relatório técnico autocontidos, em português, 33 páginas |
| `pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_r1_EN.pdf` | **Revisão 1 (vigente).** O mesmo documento em inglês, 32 páginas |
| `pdf/LEBRE_ARCHITECTURE_v0.53_SPEC_PTBR.pdf`, `..._EN.pdf` | Revisão 0 (17 páginas cada), mantida e verificada; substituída pela revisão 1 |

**Revisão 1 — documento autocontido.** A revisão 0 descrevia só os componentes novos e remetia à especificação da
v0.52 para a base. A revisão 1 descreve a LEBRE inteira sem supor a leitura de nenhum outro documento: o núcleo
estrutural (memória, especialista estrutural, combinação, plano de mudanças testadas por e-process, níveis tipo e-LOND,
salvaguardas), a M1 e a M2 (com a teoria de agregação usada: AdaHedge, switch distribution, (A,B)-Prod e o limite das
perdas sem limite), o ciclo de vida das mudanças, a condição de uso, o custo e a memória, a observabilidade, as duas
metodologias de avaliação, a evidência do núcleo (desenvolvimento, simulação de mudanças falsas, reservas 1 a 3,
microcontrolador simulado), o desenvolvimento e as validações de M1 e M2, a avaliação final, a evolução e as ablações,
a literatura, os limites, todos os parâmetros e o pseudocódigo do passo inteiro. As versões anteriores aparecem só como
evolução e ablações. Nenhum resultado foi alterado. Os caminhos de M2 passaram a se chamar H (AdaHedge) e W (troca única),
para não colidir com a memória M do núcleo; no código continuam `_subD` e `_subM`.

**Princípios de redação (os mesmos da v0.52):** nenhum número digitado à mão (o gerador lê todos dos arquivos de resultado:
a avaliação final da v0.53, as pastas congeladas de resultado da v0.52 para a evidência do núcleo e o LEBRE Lab público);
nenhum caminho local; toda afirmação qualificada pelo escopo testado; nenhum componente declarado original. O gerador
recusa o documento se encontrar caminhos locais ou remissões à especificação da v0.52.

**Estrutura (26 seções):** sumário executivo; problema, premissa e escopo; princípios; arquitetura (D1 a D3); base teórica
do núcleo; base teórica de M1 e M2; ciclo de vida; condição de uso; M1; M2; salvaguardas e intervalo; custo e memória;
observabilidade; metodologia; evidência do núcleo; núcleo em microcontrolador simulado; desenvolvimento de M1 e M2;
validações; avaliação final; evolução e ablações; literatura; limites; parâmetros; pseudocódigo e reprodutibilidade;
referências; histórico de revisões.

## 2. Outros arquivos desta etapa

- `configs/lebre_v053_canonical.json`: configuração canônica da v0.53.
- `REPRODUCIBILITY.md`, seção 8; `experiments/INDEX.md`; `docs/research/SEEDS.md`; `README.md`; `docs/README.md`.
- `LEBRE_v0.53_SPEC_r1_SHA256SUMS.txt`: hashes dos PDFs, HTMLs e do gerador da revisão 1. `LEBRE_v0.53_SPEC_SHA256SUMS.txt`
  (revisão 0): os PDFs e HTMLs conferem; as fontes do gerador foram atualizadas no lugar para gerar a revisão 1 e o
  verificador as reporta como SUPERSEDED (mesmo procedimento da v0.52).
- O LEBRE Lab foi publicado (https://github.com/Iquitim/lebre-lab); o documento registra o commit do Lab que leu.

## 3. Reprodução dos PDFs

`python docs/architecture/pdf_source/build_v053_spec.py` (gera a revisão 1; Microsoft Edge para a impressão, internet para o KaTeX, e uma
cópia do LEBRE Lab, indicada por `LEBRE_LAB` ou como pasta irmã `lebre-lab`). Como na v0.52, os bytes dos PDFs não são
reprodutíveis (os gráficos guardam a data de geração); o conteúdo e os números são.
