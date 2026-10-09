# M2 da v0.53: candidata D e régua por decidibilidade (pré-registro antes da validação 2)

**Data:** 08/10/2026. **Status:** candidata congelada e régua decidida pelo responsável pelo projeto, **antes** de montar
ou ver a validação 2. Base: `REFLEXAO_M2.md`, experimentos E1 e E2 (LEBRE Lab).

## 1. A candidata D (congelada)

- **Saída:** média ponderada de R (referência trivial declarada) e L (LEBRE v0.52), com pesos do AdaHedge (de Rooij et
  al., 2014, Figura 1) sobre o **erro quadrático** de cada previsor, prioridade uniforme, sem parâmetros livres.
- **Comparação só com a referência definida:** enquanto a referência declarada não está definida (a sazonal precisa de um
  ciclo completo de alvos), a saída é L e os pesos não aprendem.
- **Auditoria:** a porta do rascunho 1 (motor de evidência próprio, α_porta = 0,01) roda só para registrar eventos; não
  decide a saída. **Estrutura:** idêntica à da v0.52.
- **Código:** protótipo `lebre053`, `saida="adahedge_ref_definida"`, commit `a0e20e1` do lebre-research (o script da
  medição registra o commit e o hash de `model053.py`). Custo medido no desenvolvimento: ~66 FP por passo.
- **Histórico declarado:** é a sétima configuração da M2 medida (rascunhos 0 a 6 e esta).

## 2. Régua por decidibilidade (vale para a validação 2 e a reserva; não reaproveita nenhum resultado já visto)

**Classificação de cada série, feita só com v0.52 e referência (sem olhar a M2):** razão de MSE v0.52 ÷ referência na
janela de avaliação, com intervalo de 95% por bootstrap de blocos pareado (B = 2000; blocos 168, 20 ou 12 como antes; nas
famílias curtas 24, 20 ou 12; semente própria, declarada no plano):

- **"v0.52 melhor":** limite superior < 1.
- **"referência melhor":** limite inferior > 1.
- **"indecidível":** o intervalo contém 1.

**Critérios:**

1. Em cada família, nas séries "referência melhor": limite superior do IC 95% de M2 ÷ referência <= 1,01.
2. Em cada família, nas séries "v0.52 melhor": limite superior do IC 95% de M2 ÷ v0.52 <= 1,02.
3. (Alternância) não se aplica.
4. Séries com entrada externa aceita não mais que na v0.52, nas famílias análogas a A02, C01 e C04.
5. Acréscimo médio de custo <= 75 FP por passo, em cada família.
6. Caminho estrutural idêntico ao da v0.52, em todas as séries.
7. Famílias curtas: limite superior do IC 95% de M2 ÷ melhor(v0.52, referência) <= 1,05 (inalterado, todas as séries).

**Séries indecidíveis** são reportadas (M2 ÷ v0.52, M2 ÷ referência, M2 ÷ melhor), sem aprovar nem reprovar. Os critérios
1 e 2 valem por família sobre as séries da classe correspondente (agregação como antes: média geométrica e IC pela média
dos log-razões das réplicas); família sem série da classe não entra naquele critério. O relatório informa quantas séries
caíram em cada classe.

**Por que é por princípio:** a régua exige que a M2 acompanhe o melhor previsor **onde os dados mostram qual é o
melhor**, nos dois sentidos, com as mesmas margens de antes; onde os dados não decidem, nenhum algoritmo pode ser cobrado
por uma escolha que os próprios dados não sustentam (PRA-09). A classificação não depende da M2.

## 3. Próximas etapas

1. Validação 2: regras de escolha commitadas antes de baixar dados; congelamento com hashes; uma única medição de D com a
   régua acima. Se D falhar: falhas declaradas, nada ajustado.
2. Se D passar: a M2 fica resolvida no desenvolvimento e na validação. A reserva final avalia a v0.53 completa (M1 a M6),
   uma vez, com esta régua para a M2.

## 4. Resultado na validação 2 (08/10/2026)

Medição única no LEBRE Lab (`M2_VAL2_PLANO.md`, `M2_VAL2_RESULTADO.md`). **D não passa**: falha o critério 2 em W-B01,
por uma série (Abaiara 230 kV, M2 ÷ v0.52 = 1,46), uma usina que começa a gerar no meio da série; a LEBRE leva ~800 passos
para aprendê-la e o déficit dessa fase prende os pesos na referência até ~2.500 passos dentro da janela de avaliação
(dificuldade D1). **Passa em todas as outras 9 famílias**, inclusive W-C05 (grupos do IPCA, análoga a C05: 1,004, limite
superior 1,019), as negativas (1,000) e as séries curtas (1,000, limite superior 1,005). Pela regra: falha declarada,
nada ajustado; a validação 2 está gasta.

## Adendo de 09/10/2026: séries dominadas por um choque (decisão do responsável pelo projeto)

Vale **só para medições futuras** (validação 5 e reserva final), e foi decidido **depois** de ver a validação 4 (em que a
regra teria retirado o baht e o dólar de Singapura de Y-C01). Base: PRA-10 (`PRA_10_ESCALA.md`, seção 3): com um choque
imprevisível que responde por grande parte do erro, nenhum combinador online tem garantia de excesso <= 1% contra a
referência.

**Regra:** antes de rodar a LEBRE, calcula-se, só com a referência R, a fração do erro quadrático total de R no período de
avaliação que vem do maior passo isolado. Se for **maior que 5%**, a série é **"indecidível" no critério 1**: reportada,
sem aprovar nem reprovar. Os critérios 2, 4, 6 e 7 não mudam. No desenvolvimento e nas validações 1 a 4, a regra atinge 32
séries (LEBRE Lab, `diagnosticos/E15_RESULTADO.md`).

## Adendo 2, de 09/10/2026: a regra do choque vale também no critério 2 (decisão do responsável pelo projeto)

Decidido **depois** de ver o E16 (LEBRE Lab, `analises/E16_RESULTADO.md`), em que a candidata Q falhou só em Y-C02, por uma
série de choque (abs_baht_1990, maior passo 21,6% do erro da referência). Base: o argumento do PRA-10, seção 3, é
simétrico: num choque imprevisível, nenhum combinador online garante ficar a uma margem fixa de nenhum dos dois
previsores. **Regra:** a mesma medida e o mesmo limite do adendo 1 (fração do erro quadrático da referência vinda do maior
passo isolado > 5%, calculada antes de rodar a LEBRE); a série "v0.52 melhor" nessa condição fica "indecidível (choque)" no
critério 2: reportada, sem aprovar nem reprovar. Vale para medições futuras (validação 5 e reserva final); a releitura do
E16 com esta regra é só desenvolvimento.

## Adendo 3, de 09/10/2026: limite do choque dependente do tamanho do trecho avaliado (decisão do responsável pelo projeto)

Decidido **depois** de ver o E18b (LEBRE Lab, `analises/E18B_RESULTADO.md`), em que o limite fixo de 5% tornava
"indecidíveis" ~35% das séries curtas sem choque real: com n passos avaliados e erros sem choque, o maior passo pesa cerca
de 2 ln(n)/n do total (~3,9% com n = 288). **Regra (substitui o limite dos adendos 1 e 2):** com n = número de passos do
período de avaliação com erro da referência finito, a série é "indecidível (choque)" nos critérios 1 e 2 se a fração do
erro quadrático da referência vinda do maior passo isolado for **> máx(5%, 5 × 2 ln(n)/n)** (~20% com n = 288; 5% com
n >= ~1.300). O fator 5 é margem de julgamento para caudas mais pesadas que a normal, não um teorema.

Esclarecimento: a régua é de **avaliação** (aplicada a um trecho já observado, cujo tamanho é sempre conhecido; num uso
real, o trecho observado até o momento); o modelo não a usa e não precisa conhecer o tamanho da série. Vale para medições
futuras (validação 5 e reserva final); releituras do desenvolvimento com esta regra são só desenvolvimento.
