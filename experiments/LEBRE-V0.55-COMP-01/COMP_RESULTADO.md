# Comparação da v0.55 com modelos externos: resultado

**Plano:** `COMP_PLANO.md` (commit `cee2604`, antes de rodar). Mudança de dispositivo dos modelos de fundação para GPU
no commit `e25e77d`, declarada em `RUN_NOTAS.md`.
**Séries:** as 84 da reserva final da v0.55. **Status:** referência; não altera a promoção.

Números completos em `COMP_RESULTADO.json`. A visão robusta (mediana das razões por série nos 1.000 pontos) está em
`COMP_MEDIANAS_1000PTS.json`. Essa visão foi **acrescentada depois** de ver que um comparador diverge em algumas séries
(§3).

Todas as razões são **MSE da v0.55 ÷ MSE do modelo**: abaixo de 1, a v0.55 erra menos. "Significativo" quer dizer
depois da correção de Holm sobre todos os pares de cada janela (5%).

## 1. Custo por previsão (ordem de grandeza)

| Classe | Modelos | Operações por previsão |
|---|---|---|
| LEBRE v0.55 | — | ~860 (mediana) |
| Online, mesma classe | ARX_NLMS 410–800; NLINEAR ~670; DLINEAR ~1.500; ARX_RLS 1.100–3.950 | 10²–10³ |
| Estatístico | SARIMAX_X | 10²–10³ por passo do filtro, mais o ajuste por verossimilhança |
| Aprendizado de máquina | GBM | ~10³ por previsão, mais 10 reajustes em lote em toda a história |
| Fundação | TTM_ZS 1,6·10⁷ (medido); TTM_FT_EXOG 6,4·10⁷ (medido) mais o ajuste fino; Chronos-2 e Chronos-Bolt ~10⁹–10¹⁰ (estimativa: 2 × parâmetros × tokens de contexto) | 10⁷–10¹⁰ |

## 2. Quem é significativamente melhor que a v0.55

| Família | Janela completa (a partir de 30%) | 1.000 pontos (inclui os modelos de fundação) |
|---|---|---|
| **camels** (30) | **ARX_RLS** (v0.55 ÷ RLS 1,125); **GBM** (1,152); v0.54 (1,010) | **ARX_RLS** (1,155); **GBM** (1,105) |
| **bdg2** (30) | nenhum | **Chronos-2 com covariáveis** (1,227); Chronos-2 (1,165); Chronos-Bolt (1,084) |
| **eólica** (8) | nenhum | **Chronos-2 com covariáveis** (1,055); Chronos-2 (1,052) |
| **solar** (8) | **GBM** (1,099) | **Chronos-2 com covariáveis** (1,363); Chronos-2 (1,316); Chronos-Bolt (1,237); GBM (1,115) |
| **níveis do BCE** (8) | nenhum | nenhum |

**Onde a v0.55 é significativamente melhor:**
- **SARIMAX-X:** em todas as famílias, de 0,91 a 0,97.
- **NLinear e DLinear online:** em quase todas, de 0,54 a 0,96.
- **TTM:** zero-shot em todas, de 0,61 a 0,89; ajustado com entradas em todas, de 0,08 a 0,72.
- **Chronos:** nas bacias (Chronos-2 univariado 0,831; Chronos-Bolt 0,767) e nos níveis (0,78 a 0,91).
- **GBM:** em prédios, eólica e níveis.
- **ARX_RLS:** em prédios, solar e níveis.
- **Referência trivial:** em todas as famílias, menos os níveis, onde a v0.55 empata com a persistência (1,003, sem
  diferença).

## 3. Cuidados na leitura

1. **O ARX_NLMS diverge em algumas séries.** O erro chega a 31.732 vezes o da v0.55 num medidor e a 121.083 vezes num
   nível. A média geométrica da família fica dominada por isso (por exemplo, 0,047 nos prédios). Pela mediana por série,
   ele fica mais perto, mas ainda pior que a v0.55: 0,92 nas bacias, 0,23 nos prédios, 0,81 na eólica, 0,67 na solar e
   0,15 nos níveis. É o protocolo auditado das versões anteriores, sem mudança. O resultado fica registrado como
   **comparador instável**.
2. **O TTM ajustado falha nos níveis** (0,078). A padronização na janela de calibração, que é do protocolo, não serve
   para séries integradas, cujo nível sai da faixa calibrada. Isso já tinha aparecido num teste sintético antes da
   execução.
3. **O GBM** tem custo de previsão parecido com o da v0.55, mas faz 10 reajustes em lote na história inteira. Não é um
   modelo online de custo fixo.
4. **Eólica, solar e níveis têm só 8 séries cada.** Os IC são por bootstrap dentro das séries, e a generalização para
   outras usinas ou moedas é mais fraca.
5. **Os níveis do BCE** parecem um passeio aleatório para todos os modelos: o melhor é empatar com a persistência. A
   v0.55 empata, e todos os outros perdem para ela.

## 4. Leitura

- **A v0.55 não é o modelo mais preciso, e nunca se propôs a ser.** O Chronos-2 com covariáveis, com cerca de 10⁶ vezes
  mais operações por previsão, é melhor em prédios (18%), solar (27%) e eólica (5%). Nas bacias e nos níveis, a v0.55 é
  melhor ou igual a ele.
- **Na mesma classe de custo, há um concorrente que a supera numa família.** Nas bacias, o **ARX_RLS** (um ARX simples
  com mínimos quadrados recursivos, ~1.700 operações por passo) erra cerca de 11% a 13% menos que a v0.55, e o GBM cerca
  de 10% a 13% menos. Nas outras quatro famílias, a v0.55 é melhor que o ARX_RLS ou empata com ele: na eólica, 1,009,
  sem diferença; nos prédios e na solar, a v0.55 é melhor.
- **Contra o SARIMAX-X,** a referência estatística clássica com entradas, a v0.55 é melhor em todas as famílias.
- **O que isso diz sobre a LEBRE.** Ela fica entre os melhores da sua classe de custo em 4 de 5 famílias, mas não em
  todas. As bacias, onde um ARX com RLS denso ganha, são justamente a família em que a v0.55 já piorava 0,8% contra a
  v0.54.

**Pergunta aberta para a próxima versão:** o que o ARX_RLS capta nas bacias que a v0.55 não capta? Por exemplo, a
resposta exata nos atrasos curtos da precipitação, ou uma adaptação mais rápida.
