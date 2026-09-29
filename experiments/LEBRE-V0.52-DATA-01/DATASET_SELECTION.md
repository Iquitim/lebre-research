# LEBRE v0.52 — Seleção de dados reais guiados por entradas (DATA-01)

**Data:** 25/09/2026 · **Status:** proposta para decisão; nada foi baixado.
**Por que primeiro:** é o maior risco da contribuição. Sem sistemas reais em que as entradas **causam** o alvo, com atrasos e estados de armazenamento, a parte estrutural da nova arquitetura não pode ser avaliada. Nas 20 séries reais da v0.51, 15 não tiveram nenhuma promoção estrutural.

## 1. Critérios (a fixar antes de olhar resultados)

| # | Critério | Por quê |
|---|---|---|
| C1 | Entradas exógenas com **caminho causal físico** até o alvo (não só co-movimento) | É o domínio para o qual o especialista estrutural existe |
| C2 | Estrutura esperada conhecida ao menos qualitativamente (tempo de viagem, armazenamento, dinâmica de processo) | Permite verdade de referência parcial para as afirmações estruturais |
| C3 | Pelo menos ~20 mil passos por série, ou muitas séries | A latência de descoberta medida foi de 1,5–3 mil passos |
| C4 | Atrasos compatíveis com o dicionário (L ≤ 32 passos), ou possibilidade de reamostrar | Senão a estrutura verdadeira fica fora do dicionário |
| C5 | Público, com licença que permita uso e publicação; download reprodutível com hash | Reprodutibilidade |
| C6 | Nunca usado no desenvolvimento da LEBRE (para o held-out) | Evita viés de seleção |
| C7 | Diversidade de mecanismos: dominado por **atraso**, por **armazenamento** (latente) e **processo industrial** | Cobre os três tipos de átomo |
| C8 | Dados faltantes em quantidade tratável e documentada | Evita artefatos de preenchimento |

## 2. Candidatos

| Candidato | Mecanismo | C1 | C2 | C3 | C4 | C5 | C6 | Observações |
|---|---|---|---|---|---|---|---|---|
| **ONS — dados hidráulicos por reservatório (cascatas)** | Atraso (tempo de viagem entre usinas) + armazenamento | ✔ defluência de montante → afluência de jusante | ✔ tempo de viagem físico | ✔ horário, vários anos | ⚠ viagem de horas a dias: com dados horários pode passar de 32; talvez agregar em 3–6 h | ✔ dados abertos ONS | ✔ nunca usado | **Brasileiro, novo, com atraso físico conhecido.** Vários pares de cascata (São Francisco, Grande, Paranaíba, Paraná, Tietê) dão várias séries independentes |
| **CAMELS-BR** (897 bacias brasileiras, diário) | Armazenamento (resposta chuva–vazão) + atraso curto | ✔ chuva e evapotranspiração → vazão | ✔ recessão e armazenamento | ⚠ diário: ~10–40 anos = 4–15 mil passos por bacia; compensado pelo número de bacias | ✔ | ✔ Zenodo, artigo ESSD | ✔ | Bom teste para **latente acionado por entrada** (o caso em que a v0.51 falhou) |
| **Nonlinear Benchmark: Cascaded Tanks, Wiener-Hammerstein, EMPS** | Dinâmica de processo com entrada controlada | ✔ entrada de excitação conhecida | ✔ física documentada | ⚠ séries relativamente curtas (Cascaded Tanks ~1 mil pontos) | ✔ | ✔ | ✔ (o Silverbox foi usado na v0.1) | Padrão da área de identificação de sistemas; sinais de excitação ricos. Útil como **desenvolvimento** |
| **Silverbox** (já no repositório) | Oscilador de Duffing | ✔ | ✔ | ✔ | ✔ | ✔ | ✗ usado na v0.1 | Só para **desenvolvimento** |
| **Debutanizadora / unidade de recuperação de enxofre** (Fortuna et al.) | Processo industrial com atrasos de medição (~45 min) | ✔ | ✔ | ⚠ debutanizadora: 2.394 pontos | ✔ | ⚠ disponibilidade e licença a verificar | ✔ | Clássico de soft sensors com atraso; conferir onde baixar |
| **Building Data Genome 2** (1.636 edifícios, horário, 2 anos) | Clima → aquecimento/resfriamento (inércia térmica = latente) | ✔ temperatura externa → energia | ⚠ ocupação e agenda dominam | ✔ 17.544 passos por medidor | ✔ | ✔ | ✔ | Escolher medidores de aquecimento/resfriamento, onde o clima causa a carga |

## 3. Proposta de partição (a confirmar)

- **Desenvolvimento:** Silverbox, Cascaded Tanks e Wiener-Hammerstein, **uma** cascata do ONS e **algumas** bacias do CAMELS-BR.
- **Held-out pré-registrado:** as demais cascatas do ONS, uma amostra aleatória de bacias do CAMELS-BR com semente declarada, um subconjunto de medidores de aquecimento/resfriamento do BDG2 e, se estiver disponível, a debutanizadora.
- **Verdade de referência parcial:** tempos de viagem publicados entre usinas (ONS) e tempos de resposta das bacias (atributos do CAMELS-BR) como **plausibilidade** das estruturas descobertas. Não são estruturas exatas, e isso deve estar dito no pré-registro.

## 4. Decisões pendentes (suas)

1. Você tem acesso a **dados privados** de processo industrial ou de hidrologia com vazão a montante? Eles valeriam mais que qualquer público.
2. Aprova a lista e a partição acima? Ou prefere priorizar o ONS (brasileiro, com atraso físico) e o CAMELS-BR?
3. Antes do download: conferir licenças (ONS, CAMELS-BR, BDG2, Nonlinear Benchmark, Fortuna) e registrar hashes.

## Fontes

- ONS Dados Abertos — [Dados hidráulicos por reservatório (base diária)](https://dados.ons.org.br/dataset/dados-hidrologicos-res) · [ENA diário por reservatório](https://dados.ons.org.br/dataset/ena-diario-por-reservatorio)
- CAMELS-BR — [ESSD 2020](https://essd.copernicus.org/articles/12/2075/2020/) · [Zenodo](https://zenodo.org/records/15025488)
- [Nonlinear Benchmark](https://www.nonlinearbenchmark.org/)
- Building Data Genome 2 — [Scientific Data 2020](https://www.nature.com/articles/s41597-020-00712-x) · [Zenodo](https://zenodo.org/records/3887306)
- Debutanizadora / SRU — [Fortuna et al., Soft analyzers for a sulfur recovery unit](https://www.sciencedirect.com/science/article/abs/pii/S0967066103000790)

## 5. Estado do download (25/09/2026)

- **Baixado com** `download_v052.py` em `data/external_v052/`: 237 arquivos, 1,46 GB, exatamente como publicados.
- **Integridade:** manifesto com URL, licença, tamanho e SHA-256 de cada arquivo em `data/external_v052/MANIFEST.csv`. Os hashes estão em `data/external_v052/SHA256SUMS.txt` (SHA-256 do arquivo: `e10c663063f445cc8bd585597b4894c9357ead4156786839f2751ab4dc3f34b0`), e os **237/237** conferem.
- **ONS horário:** cobre **2010–2026**, e não só 2019+ (≈ 16 anos horários).
- **ONS diário:** 2000–2026.
- **CAMELS-BR v1.2:** atributos, vazão das 897 bacias, precipitação, evapotranspiração real e temperatura.
- **BDG2 v1.0:** arquivo completo (zip).
- **Cascaded Tanks:** dados e documento.
- **Retirado:** Wiener-Hammerstein. O certificado do servidor não pôde ser verificado, e não há licença explícita. Não foi baixado; o desenvolvimento usa Silverbox e Cascaded Tanks.
- **Congelamento:** estes hashes passam a ser a referência. O pré-registro da v0.52 deve citá-los, e a partição desenvolvimento/held-out deve ser fixada **antes** de qualquer análise dos dados de held-out.
