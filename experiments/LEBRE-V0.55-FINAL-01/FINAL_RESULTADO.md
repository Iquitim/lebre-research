# Avaliação final da v0.55: resultado

**Pré-registro:** `PREREG_V055_FINAL.md` (commit `abd4080`, antes da execução). **Reserva:** `experiments/LEBRE-V0.55-DATA-02`.
**Candidata:** B10 (commit `b0522a0`). **Comparação:** v0.54 canônica.

**Execução:** única, 17/10/2026. 84 de 84 séries, 4 execuções cada, sem nenhuma falha (`RUN_NOTAS.md`). Números em
`FINAL_RESULTADO.json`. As previsões ficam em `preds/`, fora do git.

## Decisão: v0.55 PROMOVIDA (regra vinculante, §3 do pré-registro)

| Critério | Resultado | Passa |
|---|---|---|
| R1 sem piora (limite superior ≤ 1,02 em cada família) | camels 1,008 (1,003–1,014); bdg2 0,998 (0,988–1,009); eólica 0,994 (0,992–0,997); solar 0,993 (0,988–0,998); níveis do BCE 1,000 (1,000–1,000) | sim |
| R2 controle negativo (placebo na estrutura final) | B10: 0/84 (limite superior 0,043); v0.54: 4/84 (até 0,117) | sim |
| R3 sem falha numérica | 0 previsões não finitas, em todas as execuções | sim |
| R4 custo (mediana ≤ 1,25) | 0,989: B10 ficou **mais barata** que a v0.54 | sim |
| R5 memória (≤ 131.072 B) | 86.180 B, estimado, não medido | sim |

## Por família (descritivo)

| Família | Séries | B10 ÷ v0.54 | Janela curta (passos 200–2.000) | Séries com entrada externa no fim (v0.54 / B10) | Placebo no fim (v0.54 / B10) | Inovação com peso > 0,5 |
|---|---|---|---|---|---|---|
| camels | 30 | 1,008 (1,003–1,014) | 1,052 (0,998–1,058) | 13 / 7 | 0 / 0 | 7 |
| bdg2 | 30 | 0,998 (0,988–1,009) | 1,007 (0,979–1,041) | 18 / 1 | 3 / 0 | 11 |
| eolica | 8 | 0,994 (0,992–0,997) | 0,992 | 2 / 0 | 0 / 0 | 7 |
| solar | 8 | 0,993 (0,988–0,998) | 1,020 (1,013–1,028) | 1 / 0 | 0 / 0 | 6 |
| niveis_ecb | 8 | 1,000 (1,000–1,000) | 1,000 | **8 / 0** | 1 / 0 | 1 |

**Séries extremas:**
- piores: bdg2 Moose_education_Ricardo 1,162; bdg2 Eagle_education_Cassie 1,139; camels 58573000 1,072;
- melhores: bdg2 Cockatoo_assembly_Fernanda 0,949; bdg2 Bull_education_Mario 0,950; camels 55560000 0,950.

**Placebos aceitos pela v0.54:**
- bdg2: Eagle_education_Cassie, Cockatoo_assembly_Rodger, Hog_services_Adrianna;
- níveis do BCE: HUF.

## Leitura

1. **Interpretação.** Pela primeira vez, a estrutura falsa foi medida em dados reais, com placebos sabidamente sem
   relação:
   - a v0.54 terminou com placebo na estrutura em 4 de 84 séries; a v0.55, em nenhuma;
   - nas séries de níveis, a v0.54 terminou com entrada externa nas 8 moedas, e a v0.55 em nenhuma, com precisão
     idêntica.

   É o defeito que motivou a v0.55, agora corrigido em dados reais.
2. **Precisão.** A v0.55 não piora além da margem, mas não é uniformemente melhor:
   - **piora pequena e estatisticamente clara nas bacias:** 0,8%, IC de 1,003 a 1,014;
   - melhora pequena na eólica (0,6%) e na solar (0,7%);
   - nada nos prédios e nos níveis.
   - No começo das séries, a v0.55 é pior nas bacias (5,2%, IC cruzando 1) e na solar (2,0%).
3. **O ganho em séries integradas da validação sintética não apareceu nos níveis reais** do BCE (1,000). Aqui, as
   entradas (outras taxas do euro com um dia de atraso) não parecem trazer informação incremental. A afirmação de ganho
   em séries integradas continua apoiada só em dados sintéticos.
4. **Descoberta mais lenta**, já vista na validação: nas bacias, 7 de 30 terminam com entrada externa, contra 13 de 30 na
   v0.54. Não se sabe quantas das aceitas pela v0.54 eram genuínas.
5. **Custo:** 1,1% menor na mediana.

## Limites declarados da v0.55

- **Bacias:** piora pequena e significativa (0,8%), maior no início das séries.
- **Relações reais fracas:** são registradas como estrutura mais devagar.
- **Séries integradas:** ganho demonstrado só em sintéticos; não houve ganho nos níveis reais testados.
- **Comparações externas:** não houve com SARIMAX-X nem Chronos-2 (declarado antes).
- **Memória e custo:** estimados pelo modelo analítico, não medidos em microcontrolador.
- **Nota formal F1:** prova com autor único, ainda sem conferência independente, com a errata 01.
