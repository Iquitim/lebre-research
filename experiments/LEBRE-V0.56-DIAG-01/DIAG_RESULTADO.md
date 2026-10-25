# LEBRE v0.56 — Diagnóstico das bacias: resultado

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DIAG-01` · **Plano:** `PLANO_DIAG_BACIAS.md` (commit `d245c2a`, antes de
qualquer medição) · **Natureza:** exploratório, em reservas já consumidas. Números: `DIAG_RESULTADO_A.json` e
`DIAG_RESULTADO_B.json` (gerados por `diag_analise.py`). Notas e a checagem suplementar post hoc: `RUN_NOTAS.md`.

## 1. Conclusão pela regra fixada (§5 do plano)

A vantagem do ARX-RLS **se reproduz** nas reservas consumidas, e **dois ingredientes explicam parte substancial dela,
ambos replicados em D-B**:

- **(a) o algoritmo de adaptação:** a segunda ordem (RLS) em vez do gradiente normalizado (NLMS);
- **(b) a dinâmica autorregressiva da memória:** a memória do núcleo, sozinha, é um modelo autorregressivo muito mais
  fraco que um AR(3) ajustado por RLS, e a ordem autorregressiva importa para o ARX.

**Rejeitados:**
- **(c) o atraso de aceitação:** a v0.55 com todas as unidades ligadas desde o início, sem testes, empata com a v0.55;
- **(d) o rastreamento de mudanças:** o esquecimento quase não pesa.

As entradas (sobretudo a precipitação, com as suas defasagens de 1 a 3 dias) são o que o ARX usa. A LEBRE as tem
disponíveis, mas não extrai delas o mesmo valor: a v0.55 aceitou a precipitação em só 4 das 30 bacias de cada conjunto,
e ligar tudo não ajudou.

## 2. Números

Razões de MSE na janela da comparação externa (de 30% da série até o fim), média geométrica sobre as séries, IC 95%
por bootstrap pareado de blocos de 30 dias; "Holm" = significativo pela correção de Holm sobre a família de contrastes.

| Contraste | O que mede | D-A (posições 140–169) | D-B (110–139) |
|---|---|---|---|
| G = v0.55 ÷ ARX-RLS | a vantagem do ARX | **1,124** [1,104; 1,146] | **1,053** [1,028; 1,092] |
| R1 ÷ R0 (sem entradas) | as entradas | 1,281 ✓ | 1,262 ✓ |
| R2 ÷ R0 (só precipitação) | evapotranspiração e temperatura | 1,014 (abaixo de 0,5·G) | não replicado (fora do escopo) |
| R3 ÷ R0 (entradas só em t) | as defasagens das entradas | 1,136 ✓ | 1,127 ✓ |
| R4 ÷ R0 (só y(t−1)) | a ordem autorregressiva | 1,087 ✓ | 1,066 ✓ |
| R5 ÷ R0 (λ = 1) | o rastreamento | 1,016 (abaixo de 0,5·G) | — |
| R6 ÷ R0 (NLMS) | o algoritmo de adaptação | 1,412 ✓ | 1,390 ✓ |
| v0.55 ÷ "tudo ligado" | o atraso de aceitação | 0,997 [0,984; 1,012], não significativo | — |
| memória sozinha ÷ AR(3)-RLS | a memória como modelo AR | **2,348** ✓ | **1,929** ✓ |
| núcleo ÷ v0.55 | o papel de M1 e M2 | 1,135 | 1,142 |

✓ = parte substancial (Δ ≥ 0,5·G, Holm, sinal certo); na coluna D-B, ✓ = replicado (mesmo sinal, IC acima de zero e
pelo menos metade da magnitude de D-A). Os efeitos dos degraus não somam: os ingredientes interagem.

**Checagem suplementar (post hoc, fora da regra).** O μ do NLMS de R6 ficou na borda da grade (0,2) em 25/30 (D-A) e
28/30 (D-B) bacias. Com μ ∈ {0,5; 1,0}, o NLMS ficou ainda pior: 1,41 (D-A) e 1,29 (D-B) vez o R6. O ótimo do NLMS
está perto de 0,2, e a desvantagem dele contra o RLS **não é artefato da grade**.

## 3. Onde a diferença está

| | D-A | D-B |
|---|---|---|
| G nos passos 200–2.000 | 1,35 | 1,38 |
| G nos passos 2.000–5.000 | 1,29 | 1,23 |
| G depois do passo 5.000 | 1,12 | 1,05 |
| dias de chuva (~12% dos passos): razão; parte mediana da diferença | 1,12; 58% | 1,06; 54% |
| recessão (~70% dos passos) | 1,29; 50% | 1,01; 36% |
| subida fora de chuva | 1,00; −3% | 1,04; 18% |

A diferença é maior no início (convergência: o RLS acerta os coeficientes em centenas de passos; o NLMS precisa de
milhares) e se concentra na resposta à chuva e, em D-A, na recessão (a dinâmica autorregressiva). Nenhuma
característica simples da bacia (fração de dias de chuva, variabilidade da vazão, instante de aceitação da
precipitação) se correlaciona com a perda (Spearman, todos p > 0,2).

**Q2 (v0.55 ÷ v0.54, só D-A):** 1,016 [1,007; 1,024]. A diferença fica nos dias de chuva (67%) e na recessão (40%).
Nos passos 200–2.000 não há diferença (1,001), ao contrário da avaliação final, onde a perda era maior no início.

## 4. Evidência anterior que converge

No desenvolvimento da v0.52 (29 séries reusadas em sete rodadas, exploratório), a mesma representação da LEBRE com tudo
ligado e aprendida por RLS melhorou as bacias (0,889 contra 0,937 da versão completa), mas piorou o ONS (0,595 contra
0,508). O ARX-RLS denso foi muito melhor nas bacias (0,668). Junto com o resultado de hoje, isso indica que **trocar só
o aprendiz da estrutura não basta e tem custo em outros domínios**: a parte grande que falta é um modelo autorregressivo
ajustado **junto** com as entradas, rápido. Isso também é o que o rascunho 1 do protótipo da v0.55 já tinha apontado
(coeficientes da memória ajustados só com o passado do alvo saem enviesados quando o alvo depende das entradas).

## 5. Limites

- Exploratório: as duas reservas já tinham sido consumidas. A replicação em D-B reduz, mas não elimina, o risco de uma
  explicação ajustada aos dados.
- A escada é subtrativa sobre o ARX. Ela diz o que o ARX precisa, não prova o que falta à LEBRE; os testes diretos do
  lado da LEBRE foram dois (tudo ligado e memória sozinha).
- Só bacias. Nada aqui diz que a mesma mudança ajudaria, ou não prejudicaria, as outras famílias (a evidência da v0.52
  sugere risco no ONS).
- Restam 17 bacias inéditas no CAMELS-BR, o que não basta para uma família de avaliação final.

## 6. O que isso sugere para a v0.56 (não decidido aqui)

Uma candidata deveria ser testada, com plano próprio, como **um especialista autorregressivo com entradas, de baixa
dimensão e ajustado por RLS** (por exemplo, constante, y(t−1..t−3) e as entradas aceitas com defasagens curtas; com n ≈
8 a 16 atributos, cerca de 450 a 1.700 operações por passo). Esse especialista entraria pelo mesmo mecanismo de evidência
que a LEBRE usa para tudo: só ganha peso onde ajuda, e a sua entrada como estrutura é testada. O desenho precisa:
- proteger as famílias onde o RLS denso falhou (prédios na v0.52) e onde o RLS piorou (ONS);
- caber no contrato de custo;
- respeitar a validade dos testes (aprendiz previsível, nota formal F1).
Antes de qualquer medição da candidata, a fonte de bacias novas para a avaliação final precisa ser decidida e
registrada.
