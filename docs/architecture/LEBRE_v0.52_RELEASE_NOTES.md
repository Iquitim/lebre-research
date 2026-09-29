# LEBRE v0.52 — Notas de versão da documentação

**Data:** 27/09/2026 · **Versão documentada:** v0.52, congelada em `LEBRE-V0.52-FREEZE-01` (ver `LEBRE_v0.52_FREEZE_RECORD.md`) · **Status:** versão de pesquisa congelada, **não promovida**.

Esta nota **não altera** o congelamento: os 650 arquivos de `LEBRE_v0.52_SHA256SUMS.txt` e os da v0.51 foram reconferidos e estão intactos. Ela registra os documentos publicados e a evidência obtida **depois** do congelamento, com o mesmo código.

## 1. Documentos publicados

| Arquivo | Conteúdo |
|---|---|
| `pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_PTBR.pdf` | Especificação e relatório técnico em português, 25 páginas |
| `pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_EN.pdf` | A mesma especificação e relatório em inglês, 25 páginas |

**Princípios de redação:**
- documento autocontido, que não supõe leitura das versões anteriores; a LEBRE é tratada só como "LEBRE", e as versões anteriores aparecem apenas como evolução e ablação;
- nenhuma afirmação de "melhor" ou "mais econômico": todo resultado é qualificado pelo escopo testado;
- base teórica completa, com atribuição a cada fonte. O mecanismo central é declarado **não original**.

**Estrutura (22 seções):**
- sumário e escopo;
- princípios;
- arquitetura (D1–D4);
- base teórica: NLMS/RLS, memória, média dinâmica, faixas de oitava e Haar, triagem pré-branqueada, e-process com a constante c unilateral, níveis tipo e-LOND, intervalo adaptativo;
- ciclo de vida de uma mudança;
- condição de uso (desajuste da referência, Proposições 1–3);
- salvaguardas;
- custo analítico;
- observabilidade;
- metodologia;
- desenvolvimento;
- três reservas;
- ultraleves e modelos de fundação;
- microcontrolador simulado (D5 e 7 gráficos);
- ablações;
- literatura;
- evolução;
- limites;
- parâmetros;
- **pseudocódigo com condições de reprodutibilidade**;
- referências.

O documento tem 5 diagramas e 19 gráficos de dados.

## 2. Evidência pós-congelamento incluída nos documentos (mesmo código, sem alteração)

- **Nota formal do desajuste** (EXT-01):
  - identidade E[Δ | passado] = (2gη − g²)/B² ≤ η²/B²;
  - garantia exata se o desajuste normalizado for ≤ ε (NLMS: μ ≲ 0,016);
  - critério prático no horizonte.
  - A v0.52 (μ = 0,05) está no regime **prático**. Verificação: 10/40, 0/40 e 0/40 aceitações nulas para μ = 0,1, 0,05 e 0,03.
- **Reserva 3** (pré-registrada; 60 séries nunca vistas, 30 CAMELS-BR e 30 BDG2):
  - erro relativo ao NLinear **0,812** [0,752; 0,866], sem série catastrófica nem acima de 1,5;
  - empate com SARIMAX-X (1,002);
  - erro menor que o do TTM sem treino (0,747) e ajustado com entradas (0,771);
  - erro ~25% maior que o do Chronos-2 com covariáveis (1,250);
  - FITS 1,244 e SparseTSF 2,933 no protocolo online de um passo;
  - custo analítico 415 médio e 1.020 máximo (~4% e ~2% acima do contrato).
- **Porte C99 e microcontrolador simulado** (Renode 1.17, STM32F4/Cortex-M4F):
  - equivalência em float32: 28/29 séries de desenvolvimento e 54/60 da reserva;
  - custo: 3,2–6,0 mil instruções/passo, CPI estimado ~1,6, ~31–57 µs a 168 MHz;
  - memória: estado de 73 KB e 14,2 KB de código do modelo.
  - Não há medição em placa, e a energia não foi medida.

## 3. Material novo de apoio (só desenvolvimento)

`experiments/LEBRE-V0.52-DOC-01/` (ver o README da pasta):
- exemplos ilustrativos (uma série de desenvolvimento e um sintético declarado);
- decomposição dos rastreios de execução por função e por classe;
- firmware de perfil com saída por bloco (mesmo `lebre052.c`, mesmo simulador).

Nenhuma reserva foi acessada.

## 4. Como reconstruir

```
cd docs/architecture/pdf_source
python build_v052_spec.py            # ou: python build_v052_spec.py pt | en
```

- **Requisitos:** Python 3.11, numpy, pandas 2.2.3, matplotlib, pypdfium2, Microsoft Edge (impressão em PDF sem cabeçalho) e acesso à internet para o KaTeX.
- **Fonte dos números:** todos são lidos dos arquivos de resultado em tempo de construção (`v052_data.py`).
- **Verificação automática:** o construtor recusa o HTML se o texto contiver caminhos locais ou nomes de arquivos de resultado.
- **Revisão visual:** as páginas renderizadas ficam em `scratch/pdf_qa_v052/`.

## 5. Integridade

`LEBRE_v0.52_SPEC_SHA256SUMS.txt` registra os SHA-256 de 21 arquivos:
- os PDFs e os HTML;
- os módulos de construção (`build_v052_spec.py`, `v052_text.py`, `v052_charts.py`, `v052_diagrams.py`, `v052_data.py`);
- o material de apoio da DOC-01.

## 6. Pendências não iniciadas (propostas, sem execução)

- Medição em placa física e de energia.
- Redução da tabela de hipóteses (RAM) e otimizações (divisões, emulação de precisão dupla).
- Nova avaliação em séries nunca vistas (CAMELS-BR 110+, BDG2 85+) e em outro domínio.


---

## Revisão 1 dos documentos (27/09/2026)

**Arquivos:**
- `pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_PTBR.pdf` (28 páginas);
- `pdf/LEBRE_ARCHITECTURE_v0.52_SPEC_r1_EN.pdf` (27 páginas);
- hashes em `LEBRE_v0.52_SPEC_r1_SHA256SUMS.txt`.

A revisão 0 continua disponível, com os hashes conferidos.

**Correções de linguagem** (resposta a revisões externas):
1. **Validade estatística:** os e-values são válidos sob as hipóteses especificadas; com a referência adaptativa, essas hipóteses valem só aproximadamente, e o controle de mudanças falsas é verificado empiricamente.
2. **Contrato de custo:** declarado como **não cumprido** (+3,7% na média, +2,0% no pico). O contrato não foi revisado depois do resultado.
3. **Microcontrolador:** a compatibilidade fica restrita ao porte testado em simulador (Cortex-M4F, dezenas de KB de RAM).
4. **Capa:** três avaliações pré-registradas sequenciais; versão final confirmada em 40 + 60 séries.
5. **Disponibilidade:** o código e os pré-registros estão arquivados com hashes, mas **não publicados** em repositório público.

**Acréscimos posteriores ao congelamento** (`experiments/LEBRE-V0.52-EXT-02/`, com plano e hashes registrados antes; mesmo código congelado):
- **Simulação do controle de mudanças falsas** (700 execuções):
  - nulos: 0 de 400 execuções com qualquer mudança aceita;
  - com uma entrada verdadeira: dentro de α = 0,05 pelo critério declarado, mas duas células (persistência 0,5) ficaram acima (FDR 0,090 e 0,077);
  - causa: **substitutas correlacionadas** aceitas antes da entrada verdadeira; a remoção corrigiu 10 de 17 casos.
  - A estrutura aceita é relevância preditiva, não causa.
- **Ablação exploratória "tudo ligado"** nas reservas 2 e 3 (100 séries):
  - razão 0,988 [0,970; 1,006];
  - custo 395 contra 415;
  - o mecanismo de testes não melhora a precisão de forma distinguível, e a sua utilidade prática não foi demonstrada.
- **Segunda rodada da auditoria de literatura (PRA-05):**
  - 22 consultas com protocolo fixado antes (47 no total);
  - novos vizinhos: Choi 2026, Jha 2026, de Heide 2026, Yao–Gang–Sun 2025, Lara Pinal et al. 2026, Fernández-Barrios et al. 2026;
  - a conclusão de não originalidade do núcleo se mantém;
  - nova limitação: falta de comparadores ARMAX/Kalman e SARIMAX online.

**Nota de reprodutibilidade:** os módulos de construção (`build_v052_spec.py`, `v052_*.py`) foram atualizados in loco para a r1. Eles reconstroem a r1; a r0 fica preservada só como PDF/HTML com hash. Em revisões futuras, copiar os fontes antes de editar.
