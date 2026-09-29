# LEBRE v0.51 — arquitetura mínima: fundamentação (revisão 1)

> **Revisão 1 (25/09/2026):** o código, os parâmetros e os resultados são os mesmos da versão congelada (`ARQUITETURA_V051.md`). Esta revisão incorpora a Errata 01 da especificação: alcance da garantia de promoção; memória *inspirada* no airline/Holt-Winters, não equivalente; reversão à média ≠ suavização exponencial simples; controle de erro só por episódio. Corrige também a frase sobre alarmes do CUSUM (§5), que contradizia a própria especificação.

## 1. Princípios exigidos pelo responsável do projeto

1. **Custo:** ≤ 150 FP/passo em média e pico ≤ 500.
2. **Arquitetura mínima:** cada componente precisa se justificar.
3. **Desempenho competitivo** frente a modelos modernos.
4. **Observabilidade e explicabilidade.**

## 2. Ponto de partida matemático: decomposição do processo gerador

Modelamos a série como y_t = ℓ_t + c_{t mod s} + f(x_{t−·}) + η_t, onde:
- ℓ é o nível local;
- c é o ciclo de período s;
- f é a dinâmica guiada por entradas, com atrasos e estado latente;
- η é o ruído, com possível autocorrelação curta.

É o **modelo estrutural** de séries temporais (Harvey 1989; filtro de Kalman). Tem como casos particulares a **suavização exponencial em espaço de estados**
(ETS; Hyndman, Koehler, Ord & Snyder 2008; Muth 1960 mostrou que a suavização exponencial é ótima para o nível local) e o **modelo airline**
SARIMA(0,1,1)(0,1,1)ₛ (Box & Jenkins).

Métodos leves recentes usam a mesma decomposição:
- **CycleNet** (Lin et al., NeurIPS 2024): ciclos recorrentes aprendíveis, com previsão sobre o resíduo;
- **SparseTSF** (Lin et al., ICML 2024): < 1k parâmetros via periodicidade;
- **FITS** (Xu et al., ICLR 2024): ~10k parâmetros;
- o vencedor do **M4** (Smyl 2020): suavização exponencial por série, com modelo sobre o resíduo normalizado.

## 3. Duas hipóteses em conflito, logo dois especialistas

- **H_S (guiada por entradas):** f domina, e ℓ e c são constantes ou fracos. É o domínio da LEBRE estrutural:
  - atrasos esparsos e estado latente;
  - testes de evidência por martingales;
  - alarmes CUSUM.
- **H_M (guiada pela própria memória):** ℓ e c dominam. A informação decisiva é relativa ao último valor
  (normalização do NLinear; Zeng et al., AAAI 2023).

No DEV, as duas representações **não se somam**:
- impor a âncora do último valor piora os sistemas guiados por entradas em até +30%;
- aprender o nível pelo viés torna as decisões estruturais dependentes do ponto de partida;
- a cascata, o aprendizado conjunto e o empilhamento falharam (§6).

Por isso a arquitetura mínima tem **dois especialistas e um combinador**.

## 4. Componentes e respaldo

### S — especialista estrutural (LEBRE v0.4.5 com duas mudanças)

Na média, ~85–100 FP para d = 5.
- Aprendizado NLMS: o LMS é ótimo em H∞ (Hassibi, Sayed & Kailath 1996). Sem IPNLMS: na agregação ele não compra nada e custa ~10 FP.
- **Partida a frio dos estados de acionamento.** Começar os estados de acionamento em zero mantém o regressor previsível, então a estatística de promoção continua sendo a mesma mistura (de la Peña; Howard et al. 2021; Ville), e o pico de 3(L+1)d FP desaparece.
- **Alcance da garantia de promoção.** O limite de erro tipo I (≤ α/p por episódio) vale sob H₀ = "sem o candidato, S já fornece a média condicional correta e o ruído é condicionalmente simétrico". Fora de H₀ (átomos faltando, pesos em convergência), não há garantia: uma promoção indica **relevância preditiva para o resíduo atual de S**, não estrutura verdadeira. Não há prova formal da propriedade de e-process sob a filtração efetiva do algoritmo. O controle é por episódio; com retestes, o erro acumulado não é limitado (métodos globais existentes: alpha-investing, e-LOND, e-processes, *dynamic e-closure*; não usados). A triagem só decide quando o teste começa: as estatísticas partem de zero e nenhum dado da triagem entra no martingale.
- **Dormência da evidência** quando o peso posterior de S é < 0,01:
  - pausa só a acumulação de evidência; previsão, aprendizado de pesos e escala σ² continuam;
  - a regra é previsível, então a pausa preserva a propriedade de supermartingale (optional skipping);
  - relaciona-se aos *sleeping experts* (Freund, Schapire, Singer & Warmuth 1997);
  - economiza ~25 FP quando a memória domina, e a dormência sozinha não custa desempenho.

**Detalhes operacionais (código congelado):**
- **Dicionário:** atrasos x_{i,t−k} com 1 ≤ k ≤ L = 32 por entrada, 4 estados latentes (polos {0; 0,5; 0,8; 0,95}) e d acionamentos. p_dict = dL + 4 + d (169 com d = 5), limiar log(p_dict/α) ≈ 8,1 nats.
- **Triagem:** 2 atrasos sondados por passo, em rodízio; escore = média exponencial (peso 0,2) de e_t·x_{i,t−k}. A cada 10 passos, as vagas livres (no máximo 4 atrasos em teste simultâneo) recebem os atrasos de maior escore.
- **Teste:** 1 amostra de evidência a cada 2 passos; decisões a cada 10 passos; futilidade após T_max = 200 amostras (400 passos), e o candidato volta ao dicionário.
- **Prior da mistura:** τ = ρ/(σ̂²·m_φ), com ρ = 1 (informação unitária) e m_φ a potência de projeto do regressor.
- **Estado latente:** no máximo **um** ativo. Enquanto não há latente, um candidato por polo é testado em paralelo; o primeiro a cruzar o limiar é promovido e os outros polos deixam de ser testados. Só então os d acionamentos são testados, com o polo do latente promovido.
- **Orçamento:** M_max = 4 átomos estruturais (latente e acionamento contam; a base densa não). Com o orçamento cheio, um candidato que cruza o limiar substitui o átomo de maior CUSUM se esse CUSUM for ≥ h/2; senão, a promoção é adiada.
- **Regularização do NLMS de S:** ε = 10⁻⁶ fixo no denominador.

### M — especialista de memória (~25–40 FP)

É uma memória linear nos parâmetros com features **inspiradas** na função de previsão do modelo airline e no Holt-Winters (analogia, não equivalência):

ŷ = y_{t−1} + w·φ, com φ =
- **m − y_{t−1}:** reversão à média. Com peso w₁, a previsão é (1−w₁)·y_{t−1} + w₁·m_{t−1}: uma mistura aprendida entre o último valor e uma média exponencial lenta de taxa fixa (0,01). Aproxima o efeito de um nível local suavizado (Muth), mas **não é** a suavização exponencial simples com α aprendido.
- **y_{t−1} − y_{t−2}:** incremento recente, a parte MA/AR não sazonal.
- **y_{t−s} − y_{t−1}:** a informação do sazonal ingênuo.
- **y_{t−s+1} − y_{t−s}:** o incremento que se seguiu um ciclo atrás.
- **G[t mod s]:** perfil sazonal de incrementos, com suavização exponencial por fase.
  - G é uma média exponencial (fator 0,9 por ciclo) dos incrementos da mesma fase em ciclos anteriores.
  - É inspirado na componente sazonal do airline e no estado sazonal do Holt-Winters, e análogo ao "ciclo recorrente" do CycleNet; não é equivalente a nenhum deles (o Holt-Winters aditivo corresponde a um ARIMA restrito, não genericamente ao airline).

Detalhes:
- Os pesos w são aprendidos por NLMS sobre as **diferenças brutas**. O NLMS é invariante à escala das features, então nenhuma padronização é necessária.
- **Contrato numérico:** a atualização de M não tem ε no denominador; só é pulada quando ‖φ‖² = 0 exatamente. Isso preserva a invariância à escala exata, mas depois de um trecho longo exatamente constante seguido de um salto o passo fica enorme, e num teste sintético "constante seguido de degrau" os pesos divergiram. O caso não ocorreu nas séries reais avaliadas, mas séries com platôs longos e saltos estão fora do contrato numérico desta versão.
- Sem período declarado, φ = [m − y_{t−1}, y_{t−1} − y_{t−2}].
- Em DEV, a memória sozinha (~55 FP) empata com uma janela densa de 96–288 defasagens.
  O perfil G é o ingrediente decisivo: sem ele, o erro sobe de 0,96 para 1,12× o NLinear.

### Combinador — média dinâmica de modelos (~17 FP)

Raftery, Kárný & Ettler (2010, *Technometrics*) propuseram a DMA com fator de esquecimento λ = 0,99:

w_S = σ(−η D), D ← λD + (e_S² − e_M²)/σ̂², com **η = 1/2**, derivado da verossimilhança preditiva gaussiana.

- Com dois especialistas, os pesos dependem só da diferença das perdas.
- É o agregador de pesos exponenciais (Vovk 1990; Cesa-Bianchi & Lugosi 2006); λ < 1 dá acompanhamento de regime, como o fixed-share (Herbster & Warmuth 1998).
- σ̂² é compartilhado com o intervalo. A inversa, a raiz e a exponencial são recalculadas a cada 8 passos, com a taxa preservada, como a C6 da v0.4.
- **Por que não combinação por regressão** (Granger & Ramanathan 1984; empilhamento):
  - reproduzir a previsão estrutural exige manter o peso em 1 sobre (ŷ_S − y_{t−1}), e o desajuste do NLMS vira ruído;
  - no DEV, o interno piorou 8,6%.

### Intervalo — rastreamento de quantil (~2 FP)

Rastreamento de quantil do |erro| combinado (Gibbs & Candès 2021; Angelopoulos, Candès & Tibshirani 2023).
Com atualização a cada passo, a cobertura de longo prazo é garantida sem supor distribuição.

**Implementação na v0.51:** o quantil é atualizado só a cada 8 passos, usando apenas o indicador de erro do passo da atualização, com passo × 8.
- A taxa média se preserva, mas a garantia não se transfere integralmente.
- Quando o período é múltiplo de 8 (24, 48, 144), a atualização só observa algumas fases do ciclo (3 de 24, por exemplo).
- Nas 20 séries reais avaliadas, a cobertura por série variou de 0,85 a 0,97.
- Numa análise posterior, acumular os 8 indicadores do bloco (mesma cadência) levou todas as séries a 0,900–0,906. Essa variante não faz parte da v0.51.

## 5. Observabilidade e explicabilidade

- **Explicação exata e aditiva:** ŷ = w_S·Σ(partes de S) + (1 − w_S)·[y_{t−1} + Σ w_k φ_k].
  - As partes de S são nomeadas (viés, entradas, "x1 atrasado 6 passos", estado latente).
  - As partes de M também são nomeadas (reversão à média, incremento recente, sazonal, perfil).
- **Peso w_S:** diz qual hipótese está valendo.
- **Sinais de perda de utilidade:** vêm do CUSUM de S enquanto S está ativo. Por causa do aluguel de parcimônia, **não** têm taxa de alarme falso garantida.
- **Intervalo adaptativo** com alvo de cobertura de 90% (cobertura por série de 0,85–0,97 na implementação atual; §4) e custo contabilizado por componente.

## 6. Ablações de DEV que justificam a arquitetura mínima (`dev_lean.py`, `dev_arch.py`; só dados já usados)

Razão geométrica de NMSE contra o NLinear denso nas séries reais:

| Remover / trocar | Séries reais | Interno | Conclusão |
|---|---|---|---|
| sem M (só S = v0.4.5) | 2,07 | 0,221 | M é necessária |
| sem S (só M) | 0,96 | ~0,97 | S é necessário |
| M sem perfil G | 1,12 | — | G é necessário |
| cascata M → S | 0,97 | 0,304 | o combinador é necessário |
| S → M sobre o resíduo | 1,47 | 0,255 | idem |
| empilhamento (regressão) | 0,94 | 0,240 | DMA preferível |
| **v0.51** | **0,976** | **0,220** | — |
| v0.5 (3 especialistas + janela densa) | 0,91 | 0,199 | ~6× mais cara |

## 7. Custo medido em DEV

- **Interno (d = 5):** média ≤ 148, pico ≤ 217 FP.
- **Séries reais com d ≤ 7:** média 105–154, pico ≤ 241.
- **Escala com d:** +~8 FP por entrada, por causa da base densa de S.
- **Com 25 entradas:** média de 259 e pico de 523. **É a fronteira declarada:** o orçamento vale para d ≲ 6.
- **Fora da contagem:** a padronização causal das entradas é feita pelo ambiente (médias e variâncias exponenciais com fator 10⁻⁴, iniciadas em média 0 e variância 1), igual para todos os modelos. Num dispositivo, custaria ~12 FP por entrada e por passo.

### Memória de estado

Em precisão simples, o estado é ≈ **196·d + 12·s + 190 bytes** (sem período: 196·d + 180); em Python, com precisão dupla, o dobro. O "~1,3 KB" é a mediana do held-out, não um limite.

| d | sem período | s = 24 | s = 144 | s = 1440 | maior s com ≤ 1,3 KB (1 331 B) |
|---|---|---|---|---|---|
| 1 | 0,4 KB | 0,7 KB | 2,1 KB | 17 KB | 78 |
| 3 | 0,8 KB | 1,0 KB | 2,4 KB | 18 KB | 46 |
| 5 | 1,1 KB | 1,4 KB | 2,8 KB | 18 KB | 13 |
| 6 | 1,3 KB | 1,6 KB | 3,0 KB | 18 KB | nenhum |

## 8. Alcance verificado da descoberta estrutural (diagnóstico sintético pós-hoc)

Código congelado, d = 5 entradas gaussianas independentes, ruído unitário, 20 000 passos (salvo indicação), 10 sementes. "Estrutura exata" = fração das verificações (a cada 100 passos, a partir de t = 1000) em que o conjunto ativo é a estrutura verdadeira.

| Processo | Estrutura exata | 1ª promoção (mediana, passos) |
|---|---|---|
| Nulos gaussiano e t₃ (100 000 passos) | — | 0 promoções falsas em 17 686 episódios de teste (limite superior de 95%: 1,7·10⁻⁴ < α/p = 3,0·10⁻⁴) |
| 0,8·x₁(t−3) (100 000 passos) | 98% | 1 680 (3 remoções, todas redescobertas) |
| 0,8·x₁(t−12) | 93% | 2 255 |
| 0,8·x₀(t−3) + 0,6·x₂(t−7) + 0,5·x₄(t−20) | 57% | 2 565 / 2 990 / 8 635 |
| x₃(t−12) + z, z(t) = 0,8·z(t−1) + x₀(t) + ruído | 0% | 2 820 / latente correto nunca |
| três atrasos com ruído t₃ | 27% | 2 635 / 3 285 / 4 705 (30 remoções) |

- **Um atraso:** confiável.
- **Latência:** o teste em si leva ~200–300 passos depois da proposta. A demora está na busca: as vagas ficam ocupadas por candidatos sem sinal até a futilidade, e cada atraso só é sondado a cada ~80 passos.
- **Vários atrasos:** parcial, e sensível ao prior τ (ρ = 1/50 → 58%; 1/200 → 28%; 1/1000 → 0%).
- **Latente acionado por entrada:** falha em 10/10 sementes para todo τ. O primeiro latente promovido tem polo 0 ou 0,5; com um só latente ativo e o acionamento herdando o polo dele, a estrutura correta é representável, mas inalcançável. O orçamento não é o gargalo: fica cheio em 3,5% das decisões, e nenhuma promoção foi bloqueada.
- **Caudas pesadas:** o CUSUM com verossimilhança gaussiana remove átomos verdadeiros com frequência.
- **Combinação:** a LEBRE fica a ≤ 0,3% do especialista estrutural sozinho, exceto no processo com latente (1,020×).

## 9. Limites conhecidos e escopo das afirmações

- **Previsão:** melhor entre os comparadores online pré-registrados (0,84× o NLinear). Um modelo airline ajustado por máxima verossimilhança série a série, avaliado depois, é ~5% mais preciso; o Chronos-2 é ~1,37× mais preciso.
- **Origem do desempenho real:** em 15 das 20 séries reais não houve nenhuma promoção estrutural, e em 16 o peso médio de S ficou abaixo de 0,01. O desempenho em dados reais vem principalmente de M. A descoberta estrutural não tem evidência em séries reais guiadas por entradas.
- **"Estabilidade":** mede sensibilidade ao ponto de partida (0–450 passos descartados, mesma janela de teste), não estabilidade entre trechos diferentes da série.
- **Conjuntos de avaliação:** só o conjunto principal é held-out genuíno. O segundo conjunto de 10 séries já tinha sido usado para avaliar uma versão anterior.
- **Pré-registro:** o pré-registro e os hashes são registros internos do projeto.
- **Prior art:** nenhum componente é novo isoladamente (alpha-investing/IIC; CVFDT, FIMT-DD, AMRules; testes sempre válidos para regressão; bancos de modelos dinâmicos). Sem afirmação de novidade.
