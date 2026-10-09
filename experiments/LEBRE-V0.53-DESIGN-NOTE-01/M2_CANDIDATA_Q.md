# M2 da v0.53: candidata Q (a P com perdas do Prod normalizadas pelo maior erro já visto), especificação antes do código

**Data:** 09/10/2026. **13ª configuração da M2.** Base: validação 4 (P falha no critério 1 em Y-C01 e Y-B07, também sem a
M1) e diagnósticos E13 a E15 (LEBRE Lab): o excesso vem do Prod, que mede as perdas recortadas em B = CLIP_K × σ (2σ
recente). Erros acima de 2σ, frequentes em choques e caudas pesadas, viram todos perda 1: o Prod não distingue o erro
grande do absurdo, mas o MSE distingue. PRA-10 (`PRA_10_ESCALA.md`): as garantias disponíveis para perdas sem limite
valem em unidades da maior perda; a meta de 1% não é garantível em séries dominadas por um choque (por isso o adendo da
régua em `M2_CANDIDATA_D.md`).

## 1. A única mudança em relação à P

Perdas do Prod: f_t(x) = (y_t − x)² / N_t, com **N_t = máx_{τ <= t} máx((y_τ − D_τ)², (y_τ − M_τ)²)** (o maior erro
quadrático já visto das duas saídas combinadas, incluindo o passo atual, que só é usado na atualização depois de ver y_t;
a previsão em t + 1 usa só o passado). As perdas ficam em [0, 1] e |δ| <= 1, como o Prod exige, mas só saturam num
recorde, não a cada passo acima de 2σ. Se N_t = 0, o passo não atualiza o Prod. D, M, saída, auditoria e estrutura: como
na P.

## 2. Garantias e limites (declarados antes)

- Para a sequência normalizada, valem as do Teorema 6 de Sani, Neu e Lazaric (2014) (P, seção 3). Na escala original, a
  normalização muda com o tempo e não provei um limite limpo; espera-se a forma "constante × maior perda" do PRA-10, sem
  garantia formal. A medição decide.
- **Risco conhecido:** um único erro enorme (por exemplo, um valor impossível nos dados, como os do ONS em Y-B01) fixa N_t
  num nível alto para sempre; depois disso, as perdas normalizadas ficam pequenas e o Prod aprende devagar. Não há
  correção nesta candidata (seria outra escolha a declarar).
- Custo: o da P mais ~3 FP por passo (duas comparações e uma divisão a mais, sem o recorte): ~132-137 FP, abaixo de 150.

## 3. Medição

E16 (desenvolvimento ampliado: as 59 famílias do desenvolvimento e das validações 1 a 4, todas já gastas, mais as cinco
famílias curtas), régua por decidibilidade **com o adendo de 09/10** (choque > 5% → indecidível no critério 1), limite de
150 FP. Se atender, validação 5 nova, congelada, usada uma vez, junto com a M1 rascunho 3.

## 4. Resultado no desenvolvimento ampliado (E16, 09/10/2026)

LEBRE Lab, `analises/E16_RESULTADO.md`. **Não atende pela regra**, por uma única família: Y-C02 no critério 2 (1,011,
limite superior 1,021 > 1,02), vindo de uma série (abs_baht_1990, 1,046) cujo maior passo é 21,6% do erro da referência,
o mesmo tipo de choque do adendo de 09/10, que vale só para o critério 1. As outras 63 famílias atendem; as falhas da P
na validação 4 (critério 1 em Y-C01 e Y-B07) não aparecem (Y-B07: 0,976). Custo 118-137 FP por passo.
