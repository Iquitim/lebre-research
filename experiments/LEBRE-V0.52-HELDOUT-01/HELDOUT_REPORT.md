# LEBRE v0.52 — Avaliação em dados reservados: relatório

**Data:** 27/09/2026 · **Pré-registro:** `PREREG_V052_HELDOUT.md` (registrado antes de qualquer acesso) · **Execução:** única; 125/125 séries sem erro de modelo. O Chronos precisou ser relançado uma vez por falha de infraestrutura, antes de produzir qualquer previsão (a primeira instância foi encerrada).

## 1. O que foi avaliado

125 séries reais **nunca vistas por nenhum modelo**:
- 45 usinas do ONS em 10 rios diferentes do rio de desenvolvimento;
- 50 bacias do CAMELS-BR;
- 30 medidores de prédios do BDG2.

A LEBRE v0.52 entrou **congelada**, na configuração da última medição de desenvolvimento, sem nenhuma alteração. Foi comparada com ablações de si mesma, com comparadores lineares online, com modelos estatísticos clássicos e com modelos de fundação sem treino. Métrica: erro quadrático médio relativo ao NLinear online (menor é melhor; 1 = igual ao NLinear).

## 2. Resultado pré-registrado (máscara completa, média geométrica, IC 95% por bootstrap estratificado)

| Modelo | ONS | CAMELS | BDG2 | Todas [IC 95%] | Séries > 1,5 | Custo (FP/passo) |
|---|---|---|---|---|---|---|
| **LEBRE v0.52** | 1,180 | **55,1** | 0,940 | **5,20** [0,81; 137] | 4,8% | 365 |
| v0.52 sem divisões | 1,192 | 55,1 | 0,944 | 5,22 | 4,8% | 344 |
| v0.52 tudo ligado (sem testes) | 7,30 | 67,1 | 0,947 | 10,9 | 4,8% | 347 |
| v0.52 atômica | 8,42 | 73,0 | 0,919 | 11,7 | 5,6% | 165 |
| LEBRE v0.51 | 0,706 | 1,864 | 0,959 | 1,120 [1,00; 1,27] | 23,2% | 111 |
| ARX por mínimos quadrados, ordem online | **0,574** | **0,610** | 3,856 | 0,929 [0,75; 1,20] | 10,4% | 38.944 |
| **SARIMAX com entradas** | 0,866 | 0,766 | **0,872** | **0,826** [0,78; 0,87] | **0,0%** | — |
| SARIMA (airline) | 0,973 | 0,897 | 0,881 | 0,919 | 0,8% | — |
| LASSO online | 1,077 | 0,938 | 5,091 | 1,479 | 26,4% | 622 |
| ARX denso NLMS | 1,006 | 0,943 | 4,929 | 1,435 | 23,2% | 419 |

**1.000 pontos com os modelos de fundação:** v0.52 **0,911** (CAMELS 1,334); **Chronos-2 com covariáveis 0,675**; Chronos-2 0,844; Chronos-Bolt small 0,906; SARIMAX-X 0,841; ARX por mínimos quadrados 0,936.

## 3. Falha revelada: instabilidade da memória durante lacunas do alvo

Em **6 das 125 séries** a v0.52 explode (erro relativo de 13 até 10⁷⁹), e esses valores dominam a média geométrica.

**Causa** (diagnóstico posterior): quando o alvo falta por vários passos seguidos, o especialista de memória preenche o próprio histórico com as próprias previsões e continua em malha aberta. Os pesos aprendidos podem tornar essa recursão instável (por exemplo, reversão à média com sinal negativo; raiz característica ~1,75), e a previsão cresce exponencialmente durante a lacuna. Exemplo: numa bacia, −1,5·10⁴² depois de uma lacuna.

- **A v0.51 não tem o defeito,** porque só processa os passos com alvo observado.
- **No desenvolvimento as lacunas eram curtas,** e o defeito não apareceu.
- **A memória isolada** diverge em 18 das 125 séries. Em parte delas a combinação M/S contém a divergência, mas não em todas.

**O defeito não foi corrigido nesta avaliação,** por pré-registro.

## 4. Vistas exploratórias (posteriores, NÃO pré-registradas)

Servem para localizar o desempenho **fora do defeito**. Não substituem o resultado pré-registrado.

| Modelo | Todas, sem as 6 séries | Pior grupo (sem as 6) | Mediana (125 séries) | 1.000 pontos, sem as 6 |
|---|---|---|---|---|
| **LEBRE v0.52** | **0,706** | **0,810** | 0,804 | 0,712 |
| v0.52 tudo ligado | 0,713 | 0,817 | — | 0,739 |
| ARX por mínimos quadrados | 0,950 | 4,05 (BDG2) | **0,669** | 0,960 |
| SARIMAX com entradas | 0,823 | 0,866 | 0,852 | 0,839 |
| LEBRE v0.51 | 1,132 | 1,911 | 1,027 | — |
| **Chronos-2 com covariáveis** | — | — | 0,711 (1.000 pontos) | **0,674** |

## 5. Respostas às perguntas pré-registradas

- **Q1 — O mecanismo de testes melhora a precisão fora da amostra?** **Não há evidência.** Razão v0.52 / tudo ligado = 0,479, com IC [0,10; 1,20], que cruza 1. Sem as séries catastróficas, 0,99 (a v0.52 vence 55 de 119). No desenvolvimento havia vantagem de 3%, que não se confirmou.
- **Q2 — Contra o ARX por mínimos quadrados?** Ele é **melhor no ONS e no CAMELS** (0,574 e 0,610 contra 1,180 e 55,1; sem as séries catastróficas, 0,598 e 0,606 contra ~0,57 e ~0,80) e **muito pior nos prédios** (3,86 contra 0,94). No total, a razão pareada cruza 1. Ele vence a maioria das séries (80 de 125) e custa ~100× mais.
- **Q3 — Contra o Chronos-2 com covariáveis?** **O Chronos-2 com covariáveis é melhor:** 0,675 contra 0,911 nos 1.000 pontos; mesmo sem as séries catastróficas, 0,674 contra 0,712, e ele vence 72 de 119. No desenvolvimento a v0.52 parecia melhor (0,669 contra 0,701); **fora da amostra, isso se inverte.**
- **Q4 — A robustez se mantém?** **Não, no sentido pré-registrado.** A fração de séries com erro relativo > 1,5 é menor que a dos lineares online (4,8% contra 10–26%), mas as 6 falhas são **explosões sem limite**. O modelo mais robusto é o **SARIMAX com entradas**: nenhuma série acima de 1,5 e pior grupo 0,87.
- **Q5 — As divisões hierárquicas fazem diferença?** **Não:** razão 0,996, IC [0,988; 1,001].
- **Q6 — O custo se mantém?** **Sim:** média de 365 FP/passo e máximo de **974** por passo (contrato: média ≤ 400, pico ≤ 1.000), inclusive com até 5 entradas.

**Estrutura e intervalo:** 79 de 125 séries aceitaram ao menos uma entrada, com primeira aceitação mediana no passo 3.515. A cobertura do intervalo de 90% foi 0,904.

## 6. Onde a v0.52 fica (leitura)

1. **Como está congelada, a v0.52 não é confiável em dados novos.** Uma falha de engenharia (a memória em malha aberta durante lacunas) produz explosões em ~5% das séries. Isso é desqualificante para uso e precisa ser corrigido antes de qualquer outra afirmação.
2. **Fora desse defeito**, o desempenho se manteve igual ao desenvolvimento (0,706 contra 0,709), sem a degradação esperada. Ela fica à frente do SARIMAX com entradas, da v0.51 e dos lineares online, e atrás do Chronos-2 com covariáveis (≈ 5% no total), com custo de ~365 FP/passo.
3. **O mecanismo de testes não se paga em precisão fora da amostra.** A versão "tudo ligado" empata. O valor dele fica restrito a **estrutura certificada e explicada** e ao controle de mudanças falsas (verificado em nulos). Isso tem de ser o argumento central, não a precisão.
4. **As divisões hierárquicas não se justificam em dados reais.**
5. **A precisão vem das entradas** e de um aprendiz linear simples. O ARX clássico com mínimos quadrados mostra que ainda há espaço em rios e bacias, ao custo de falhas graves nos prédios.

## 7. Implicações para os próximos passos

- A reserva desta divisão **foi consumida**. Qualquer correção (por exemplo, do defeito das lacunas) precisa de **outra avaliação em dados nunca vistos**. Ainda há séries elegíveis não usadas: ~177 bacias do CAMELS-BR e ~730 medidores do BDG2. No ONS, todos os rios elegíveis já foram usados.
- A revisão de literatura e o congelamento devem partir **desta** leitura: a contribuição defensável é o mecanismo de mudança estrutural com garantia a qualquer momento, sua condição de uso (referência com desajuste pequeno) e o limite de informação em entradas suaves; não a precisão.
