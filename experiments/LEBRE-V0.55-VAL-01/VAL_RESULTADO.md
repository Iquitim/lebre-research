# Validação da v0.55 em séries reais nunca usadas: resultado

**Pré-registro:** `PREREG_V055_VAL.md` (commit `07795c2`, antes de carregar qualquer valor). **Candidata:** B10, congelada
em `b0522a0`. **Execução:** única, 17/10/2026, sem falhas (50 de 50 séries). Números em `VAL_RESULTADO.json`. As
previsões ficam em `preds/`, fora do git.

## Decisão: B10 PASSA na validação

| Critério | Resultado |
|---|---|
| V-a sem piora (limite superior ≤ 1,02 por família) | passa: camels 1,003 (0,991–1,018); bdg2 0,993 (0,984–1,002) |
| V-b sem falha numérica | passa: 0 previsões não finitas |
| V-c custo (mediana ≤ 1,25) | passa: 1,022 |

Pelo pré-registro, **B10 é a candidata da v0.55 para a avaliação final**, que terá pré-registro próprio, reserva nova e
regra de promoção vinculante.

## Descritivo (não muda a decisão)

**Por série:**
- piores: bdg2 Eagle_office_Mandi 1,148; bdg2 Bull_lodging_Perry 1,059; camels 64810000 1,057;
- melhores: camels 64771500 0,922; camels 12700000 0,925; bdg2 Bull_education_Miquel 0,929;
- a estrutura de inovação ganhou peso (wI > 0,5 no fim) em 5 de 20 bacias e em 12 de 30 medidores.

**B10 registra muito menos entradas externas como estrutura** (séries com alguma no fim):

| Família | v0.54 | B10 |
|---|---|---|
| camels | 6 de 20 | 0 de 20 |
| bdg2 | 16 de 30 | 3 de 30 |

Diagnóstico em duas bacias, feito depois do resultado:

- **64810000.** A precipitação acumula evidência parecida nas duas versões: 5,05 contra 4,30 no primeiro episódio longo.
  - Na v0.54, ela foi aceita no segundo episódio (passo 8.320).
  - Em B10, os episódios iniciais foram fechados cedo pela regra de varredura, o primeiro episódio longo só começou no
    passo 11.760, e a série acabou antes de outro.
  - É descoberta **mais lenta**, não recusa.
- **12700000.** A precipitação não foi aceita em nenhuma das duas versões, e B10 é 7,5% melhor nessa série.

**Limite declarado da candidata:** em dados reais, B10 não piora a precisão, mas registra relações reais fracas como
estrutura mais devagar que a v0.54. Não se sabe ainda que parte das entradas aceitas pela v0.54 nessas famílias era
genuína e que parte era espúria. A avaliação final deve medir o atraso de aceitação e a fração de séries com entradas
aceitas, com séries mais longas se possível.
