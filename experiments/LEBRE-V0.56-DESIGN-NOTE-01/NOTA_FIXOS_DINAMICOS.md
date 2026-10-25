# LEBRE v0.56 — O que é fixo e poderia ser dinâmico: nota de desenho 01

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DESIGN-NOTE-01` · **Natureza:** inventário e programa; nenhuma medição.

## 1. Princípio (decisão do responsável pelo projeto, 25/10/2026)

> "A LEBRE deve ser econômica, mas quando isso fizer sentido. O fixo meio que rouba resultado."

O diagnóstico do Chile (`LEBRE-V0.56-DIAG-03`) mostrou isso na prática. A frequência fixa da regressão da M1 (a cada 8
passos na v0.55, a cada 4 na C5) custou o ganho nas bacias chilenas, e o melhor período mudava de uma bacia para outra,
do começo para o fim da série e dos dias de chuva para os secos. Um número fixo gasta demais onde não precisa e de menos
onde precisa. A LEBRE já tem um mecanismo desse tipo, a dormência da M1 (v0.54); a proposta é levar o mesmo princípio
ao resto do modelo.

## 2. Regra de classificação

Nem todo número fixo deve virar dinâmico. Cada constante cai numa de quatro classes:

| Classe | O que é | Regra |
|---|---|---|
| **G, garantia** | define a hipótese testada ou o controle de erro (nível α, margens ε, orçamento do e-LOND) | **fica fixa.** Torná-la função dos dados mudaria o que está sendo garantido. |
| **S, segurança** | protege a saída contra falhas (recorte de entradas fora do contrato, envelope da saída) | fica fixa, salvo evidência forte de que rouba resultado |
| **A, aprendizado** | velocidade, frequência ou memória de adaptação (passos, esquecimento, cadências) | **candidata principal** a dinâmica |
| **R, representação e orçamento** | quantas defasagens, quantas entradas, quantos experimentos ao mesmo tempo | candidata, com cuidado com o custo |

Uma regra dinâmica só é admissível se usar **apenas o passado** (é previsível). Pela nota formal F1, isso mantém a
validade dos e-processes para qualquer aprendiz previsível. A M1 e a M2 não participam dos testes de estrutura; nelas, a
validade dos testes não é afetada de modo algum.

## 3. Inventário do código congelado (protótipo `LEBRE-V0.56-PROTO-01`, igual à v0.55)

| Constante | Valor | Onde | O que faz | Classe | Evidência de que rouba resultado | Dinâmica possível |
|---|---|---|---|---|---|---|
| EVERY da M1 (frequência da regressão) | 8 (C5: 4) | M1 | a cada quantos alvos a regressão da M1 aprende | A | **forte**: `DIAG-02` e `DIAG-03` (a cada 1–2 passos: +7% a +10% nas bacias; a cada 4: nada no Chile) | **estudo sob demanda**: atualizar quando o erro surpreende (filtragem com seleção de dados) |
| MU (passo do NLMS) | 0,05 | estrutura de nível s e de inovação | velocidade de aprendizado da estrutura | A | **forte, indireta**: no ARX, NLMS em vez de RLS custa 41% (`DIAG-01`); a diferença é maior no início | passo variável (NLMS de passo variável) ou atualização de segunda ordem onde há uso |
| passo e taxas da memória (mu, a_prof, a_mean) | 0,05; 0,1; 0,01 | memória M | aprendizado da memória do próprio alvo | A | **forte**: a memória sozinha erra 2,35× e 1,93× mais que um AR(3) por RLS (`DIAG-01`) | passo variável ou RLS de baixa dimensão |
| defasagens do alvo na M1 (ylags) | 2 (C5: 3) | M1 | ordem autorregressiva da M1 | R | moderada: tirar a ordem do ARX custa 9% (`DIAG-01`) | escolha online da ordem por mínimos quadrados preditivos |
| bandas de defasagem da M1 | 5 (C5: 3) | M1 | até que defasagem a M1 olha as entradas | R | fraca: 3 bandas iguais ou melhores no Chile (`DIAG-03`) | escolha online, como a ordem |
| entradas da M1 (M_MAX) | 5 | M1 | quantas entradas a M1 usa | R | sem medição | — (depois) |
| esquecimento do RLS da M1 | 0,999 | M1 | memória da regressão da M1 | A | fraca: no ARX, λ fixo custa 1,6% (`DIAG-01`) | esquecimento variável (depois de P1–P3) |
| LAM e ETA da média dinâmica (wS, wI) | 0,99; 0,5 | núcleo | quão rápido a combinação muda de peso | A | sem medição | sensibilidade primeiro |
| EVERY do núcleo (pesos wS, wI, escalas, intervalo) | 8 | núcleo | a cada quantos passos esses pesos são recalculados | A | sem medição | sensibilidade primeiro |
| M_SLOTS (experimentos simultâneos) | 2 | núcleo | quantos testes de estrutura rodam ao mesmo tempo | R | indireta: a v0.55 registra relações reais fracas mais devagar | orçamento de experimentos por demanda (mais vagas quando há candidatas fortes na triagem) |
| SCREEN_EVERY (triagem) | 4 | núcleo | a cada quantos passos a triagem roda | R | sem medição | — (depois) |
| dormência (OMEGA_MIN, D_SLEEP, J, J_RLS) | 1e-3; 2.000; 8; 64 | M1 | quando a M1 dorme e quanto estuda dormindo | A | sem medição; o estudo sob demanda a substitui em parte | absorvida por P1 |
| ALPHA, EPS, GATE_ALPHA, GATE_EPS, orçamento do e-LOND | 0,05; ±0,002; 0,01; 0,002 | testes | controle de mudanças falsas | **G** | — | **não mexer** |
| N_MIN, T_MAX, COOLDOWN, REM_PERIOD, CHAL_WARM, N_REM_MIN | 100; 5.000; 2.000; 2.000; 250; 5.000 | testes | durações mínimas e máximas dos episódios | G/R | indireta (velocidade de registro) | só depois, e só regras previsíveis |
| CLIP_X, OUT_MARGIN, OUT_RHO | 8; 0,5; 1e-3 | entrada e saída | contrato de entradas e envelope da saída | **S** | sem evidência | não mexer agora |
| CLIP_K, SCALE_FLOOR | 2; 0,1 | escala dos testes | escala da perda recortada | G | — | não mexer (já corrigido na v0.55) |
| ALPHA_COV, GAMMA_Q | 0,1; 0,1 | intervalo | intervalo de 90% (já adaptativo) | — | — | — |
| POLES do estado residual | 0,8; 0,95 | núcleo | memória do estado residual | R | sem medição | — (depois) |
| ciclo declarado | pelo usuário | memória | período sazonal | R | tentado na v0.54 (M6, ficou de fora) | fora deste ciclo |

## 4. Programa priorizado

| Ordem | Peça | Por quê primeiro | Referências (não originais) |
|---|---|---|---|
| **P1** | **M1 com estudo sob demanda** | evidência mais forte, medida e replicada; não toca os testes de estrutura | filtragem adaptativa por pertinência a conjunto, com atualizações esparsas (família BEACON: Nagaraj, Gollamudi, Kapoor e Huang, 1999, *a conferir*); regressão online com censura de dados pouco informativos (Berberidis, Kekatos e Giannakis, 2016, *IEEE Trans. Signal Processing* 64(15)) |
| **P2** | passo variável na estrutura e na memória | evidência forte; toca a referência dos testes, mas a regra é previsível | NLMS de passo variável não paramétrico (Benesty, Rey, Rey Vega e Tressens, 2006, *IEEE Signal Processing Letters* 13(10), 581–584) |
| **P3** | ordem autorregressiva da M1 escolhida online | evidência moderada; barato | mínimos quadrados preditivos (Rissanen) |
| P4 | cadências e velocidades da combinação do núcleo | sem medição: medir a sensibilidade antes de desenhar | — |
| P5 | orçamento de experimentos por demanda | ligado ao limite de registro lento da v0.55 | — |
| P6 | esquecimento variável | evidência fraca | RLS com fator de esquecimento variável (família de métodos; referência específica *a conferir*) |

**Primeiro passo deste ciclo:** P1, com uma **triagem de sensibilidade** de P2, P3 e P4 na mesma rodada. A triagem é
exploratória: só diz se o fixo rouba resultado antes de desenhar cada peça. Cada medição terá plano commitado antes.

## 5. Dados de desenvolvimento deste ciclo

Só dados já usados:
- o banco da `LEBRE-V0.56-DEV-01` (E20, prédios das posições 115–144, bacias brasileiras 110–169);
- os rios do ONS (reserva 1 e desenvolvimento);
- as 20 bacias chilenas da validação da v0.56 (posições 30–49), agora gastas.

**Para a candidata que sair deste ciclo:**
- validação nova em bacias chilenas nunca tocadas (das 53 restantes, posições 50–102 do sorteio) e prédios inéditos, com
  regras commitadas antes;
- a reserva final da v0.56 (`SPLIT_V056.json`, posições 0–29 do CAMELS-CL e as demais famílias) continua lacrada, com o
  pré-registro da final mantido.
