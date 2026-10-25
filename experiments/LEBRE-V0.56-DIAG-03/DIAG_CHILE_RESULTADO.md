# LEBRE v0.56 — Por que o ganho da C5 caiu nas bacias do Chile: resultado

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DIAG-03` · **Plano:** `PLANO_DIAG_CHILE.md` (commit `4d1df13`) ·
**Natureza:** exploratório, nas 20 bacias chilenas já gastas pela validação (CL-V) e nas 30 brasileiras consumidas
(D-A). A reserva final da v0.56 continua lacrada. Números: `DIAG_CHILE_RESULTADO.json` e `DIAG_CHILE_ADENDO.json`.

## 1. Conclusão

**A falha da C5 no Chile vem da economia escolhida, e não da correção da M1.** A correção completa melhora a v0.55 em
7,5% nas bacias chilenas. A versão barata perdeu o ganho porque atualiza a regressão a cada 4 passos. Atualizando a cada
1 ou 2 passos, o ganho volta, com 3 ou com 5 bandas.

A escolha da C5 foi feita num banco cujas bacias (todas brasileiras) toleravam a atualização a cada 4 passos. O Chile
não tolera. É exatamente o risco de "direção achada em dados já olhados" registrado na verificação da `DEV-01`.

## 2. Hipóteses do plano

| Hipótese | Medida | Brasil (referência) | Leitura |
|---|---|---|---|
| H1: não havia o que ganhar (a v0.55 já perto do ARX-RLS) | v0.55 ÷ ARX-RLS em CL-V: **0,971** [0,929; 1,042] | 1,124 (D-A), 1,053 (D-B) | **sustentada** para o ARX: no Chile, ele não é melhor que a v0.55 |
| H2: as entradas informam menos | ARX sem entradas ÷ ARX: 1,243 [1,173; 1,269] | 1,281, 1,262 | não sustentada |
| H3: evapotranspiração potencial em vez da real | D-A com a potencial: v0.55 ÷ C5 = 1,074 [1,050; 1,097] | 1,072 com a real | não sustentada |
| H4: a M1 não entra | peso mediano da M1 na C5: 0,99; 9 de 20 bacias dormem em algum momento (mediana do tempo dormente: 0) | 1,0 | não sustentada |

H1 vale para o ARX-RLS, mas **não** para a M1 corrigida. O especialista da correção completa, sozinho, erra 11,6% menos
que o ARX-RLS no Chile (0,884 [0,825; 0,938]). O ganho existe; o ARX-RLS da comparação é que não era a referência certa
para o Chile.

## 3. Adendo (declarado antes de rodar): qual economia derruba o ganho

| Variante (3 defasagens do alvo, sem recorte) | Chile: v0.55 ÷ variante [IC 95%] | Custo no Chile | Fração do ganho de C0 nas bacias BR (`DEV-01`) | Custo no banco da `DEV-01` |
|---|---|---|---|---|
| C0: a cada 1, 5 bandas | 1,075 [1,057; 1,099] | 2,72 | 100% | 2,28 |
| C3: a cada 1, 3 bandas | **1,102** [1,085; 1,125] | 1,66 | 97% | 1,51 |
| C1: a cada 2, 5 bandas | 1,044 [1,026; 1,069] | 1,75 | 91% | 1,55 |
| **C4: a cada 2, 3 bandas** | **1,071** [1,051; 1,096] | **1,19** | **89%** | **1,15** |
| C2: a cada 4, 5 bandas | 1,003 [0,986; 1,026] | 1,25 | 53% | 1,18 |
| C5: a cada 4, 3 bandas | 1,010 [0,993; 1,032] | 0,96 | 69% | 0,985 |

- **A frequência decide:** a cada 4 passos, o ganho some no Chile (1,003 e 1,010), com 5 ou com 3 bandas. A cada 2 ou a
  cada 1, ele aparece.
- **As bandas longas não fazem falta:** com 3 bandas (defasagens 0 a 3), o ganho é igual ou maior que com 5. A hipótese
  que levantei antes de medir, de que o Chile precisaria das defasagens 4 a 15, **estava errada**.
- **A C4** (a cada 2, 3 bandas) preserva o ganho nos dois países a um custo de 1,15 a 1,19 vez a v0.55, dentro do teto de
  1,25. No banco da `DEV-01`, ela passou em ganho, custo e falhas e falhou na não piora por 0,0009: na família YC01
  (retornos diários, 4 séries), o limite superior foi 1,0209 contra 1,02, com estimativa 1,006 e IC incluindo 1.

## 4. Descritivo por bacia (CL-V, n = 20; só indicação)

A vantagem do ARX-RLS sobre a v0.55 encolhe em bacias mais áridas (Spearman −0,63), com mais escoamento de base (−0,57) e
com mais neve (−0,44), e cresce com a frequência de chuvas fortes (+0,51). O ganho da C5 não se correlaciona com nenhum
desses atributos.

## 5. Limites

- Exploratório. As 20 bacias de CL-V já foram gastas, e **agora também informaram a escolha entre as variantes**. Uma
  candidata escolhida com base neste adendo precisa de uma validação nova, em bacias chilenas ainda não usadas.
- Restam 53 bacias chilenas elegíveis e nunca usadas (posições 50–102 do sorteio da v0.56), além das 30 da reserva final.
- O adendo compara variantes já definidas antes; nenhuma variante nova foi criada.
