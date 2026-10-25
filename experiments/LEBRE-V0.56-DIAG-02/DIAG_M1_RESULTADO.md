# LEBRE v0.56 — Diagnóstico da M1 nas bacias: resultado

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DIAG-02` · **Plano:** `PLANO_DIAG_M1.md` (commit `37ec776`, antes de
qualquer medição) · **Natureza:** exploratório, nas mesmas reservas consumidas do `DIAG-01`. Números:
`DIAG_M1_RESULTADO_A.json` e `DIAG_M1_RESULTADO_B.json`.

## 1. Conclusão pela regra fixada

A M1 já tem a forma certa: é um ARX ajustado por RLS. O que a impede de chegar ao ARX-RLS é **como ela é atualizada e
entregue**. Três limitações, **juntas**, explicam quase toda a diferença, e o efeito replicou em D-B:
- a regressão atualizada só a cada 8 alvos;
- o recorte de E em torno da previsão do núcleo;
- duas defasagens do alvo em vez de três.

Sozinha, nenhuma passa do limiar. O RLS a cada passo fica logo abaixo (5,3% contra o limiar de 5,8%), e o recorte e a
terceira defasagem não mudam nada isoladamente. Só com a regressão atualizada a cada passo é que o recorte e a ordem
autorregressiva passam a pesar.

| | D-A (posições 140–169) | D-B (110–139) |
|---|---|---|
| v0.55 ÷ ARX-RLS (G) | 1,124 | 1,053 |
| v0.55 ÷ M5 (as três juntas) | **1,106** [1,087; 1,126] ✓ | **1,098** [1,084; 1,112] ✓ replicado |
| M5 ÷ ARX-RLS | 1,016 [1,005; 1,029] | **0,959** [0,939; 0,993] |
| especialista da M1 sozinho (E sem recorte) em M5 ÷ ARX-RLS | 1,018 | 0,958 |
| especialista da M1 sozinho em M0 (v0.55) ÷ ARX-RLS | 1,098 | 1,027 |
| custo por passo de M5 ÷ v0.55 (mediana) | 2,73 | 2,72 |

Variantes isoladas, só em D-A (v0.55 ÷ variante; Holm sobre M1 a M5):

| Variante | Razão [IC 95%] | Classificação |
|---|---|---|
| M1: RLS a cada alvo | 1,053 [1,045; 1,063] | significativo, abaixo de 0,5·G |
| M2: sem recorte | 1,000 [0,985; 1,018] | nada |
| M3: três defasagens | 1,002 [0,997; 1,006] | nada |
| M4: sem dormência | 0,990 [0,984; 0,993] | pior (só 2 de 30 bacias dormem) |
| M5: M1 + M2 + M3 | 1,106 | ✓ |

**Outros números (D-A; D-B igual a menos de 0,01):**
- a M1 melhora a previsão do núcleo em 13% (L' ÷ núcleo = 0,871);
- a M2 custa 1,1% nas bacias (saída ÷ L' = 1,011), o preço do ponto de partida na persistência;
- o recorte age em 1,9% dos passos, mas em 10,8% dos dias de chuva;
- a M1 quase nunca dorme nas bacias.

## 2. Leitura

- O `DIAG-01` apontou a adaptação de segunda ordem e a dinâmica autorregressiva. Este diagnóstico localiza as duas na
  M1: o RLS dela existe, mas aprende com 1/8 dos dados, e a dinâmica autorregressiva dela é curta e recortada. Isso
  explica também por que a diferença era maior no início das séries.
- **A diferença para o ARX-RLS pode ser fechada sem um componente novo**, só mudando três parâmetros da M1.
- **O obstáculo é o custo:** o RLS de 18 atributos a cada passo multiplica o custo por ~2,7 (de ~870 para ~2.350
  operações por passo), muito acima do limite de 1,25 vez a versão anterior usado na promoção da v0.55.

## 3. Limites

- Exploratório, em reservas já consumidas; só bacias.
- As três mudanças valem para a M1 em **todas** as famílias. O efeito nos prédios, nas usinas, nos níveis e nos
  sintéticos não foi medido: na v0.52, um RLS denso foi catastrófico nos prédios, e aqui o recorte, que protege contra
  isso, foi removido.
- A dormência perde parte do sentido se a M1 ficar mais cara justamente onde não ajuda.

## 4. Consequência para a v0.56

A candidata natural é a **M1 com as três mudanças**, desenvolvida no banco de todas as famílias, com o controle placebo e
uma decisão explícita sobre o custo. Duas formas de tratar o custo, a decidir antes do plano da candidata:
1. aceitar um teto de custo maior para a v0.56, declarado antes;
2. procurar uma versão barata, cujo efeito precisa ser medido: RLS a cada 2 ou 4 passos, menos bandas de defasagem, ou
   menos entradas na M1.
