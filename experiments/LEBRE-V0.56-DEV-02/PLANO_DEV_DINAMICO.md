# LEBRE v0.56 — M1 com estudo sob demanda e triagem do que é fixo: plano (commitado antes de qualquer medição)

**Data:** 25/10/2026 · **Etapa:** `LEBRE-V0.56-DEV-02` · **Natureza:** desenvolvimento, só com dados já usados.
**Base:** `LEBRE-V0.56-DESIGN-NOTE-01/NOTA_FIXOS_DINAMICOS.md` (P1 e a triagem de P2, P3 e P4).

## 1. Parte A — M1 com estudo sob demanda (P1)

A cada alvo aprendido, a M1 tem a sua previsão E (antes de aprender com esse alvo) e o erro a priori e = y − E. Em vez
de atualizar a regressão num período fixo, ela decide **se este alvo vale uma atualização**, usando só o passado.

**Representação comum a todas as variantes** (a que funcionou no Brasil e no Chile): 3 defasagens do alvo, 3 bandas de
defasagem das entradas ([0], [1], [2–3]), sem recorte. A triagem e a escolha das entradas seguem a cada 8 alvos. A
dormência é a da v0.55.

**Guardas comuns:**
- toda atualização acontece enquanto a regressão ainda não foi determinada (n_RLS < k) e nas primeiras 100 atualizações
  depois de cada troca das entradas escolhidas (o aquecimento);
- nunca se passam mais de 8 alvos aprendidos sem atualização (o pior caso é o período da v0.55).

**Estatística de surpresa:** σ̂²_E é a média exponencial (taxa 0,01) de e², atualizada **depois** da decisão (só o
passado entra na decisão).

| Código | Regra de decisão | Referência |
|---|---|---|
| D1 | atualizar se \|e\| > 1,0·σ̂_E | pertinência a conjunto: atualiza quando o erro sai da faixa esperada |
| D2 | atualizar se e² / (σ̂²_E·(1 + zᵀPz)) > 1,0 (a inovação normalizada pela incerteza da própria regressão) | censura de observações pouco informativas |
| D3 | orçamento médio de 1/2: atualizar se a surpresa e²/σ̂²_E passar de um limiar q̂ ajustado online para que, em média, metade dos alvos atualize (q̂ ← q̂ + 0,01·(1{surpresa > q̂} − 1/2)) | contrato de complexidade: custo médio fixado, gasto onde há surpresa |
| D4 | o mesmo, com orçamento de 1/4 | idem, mais barato |

**Comparadores fixos** (do `DEV-01` e do `DIAG-03`, mesmo código, conferido bit a bit):
- A: a v0.55;
- C3: a cada 1, 3 bandas;
- C4: a cada 2, 3 bandas;
- C5: a cada 4, 3 bandas.

O custo de cada variante é contado operação a operação, inclusive o da decisão (D2 calcula zᵀPz).

## 2. Parte B — triagem de sensibilidade (P2, P3, P4)

Cada variante muda **um** número fixo da v0.55, para outro valor fixo. A pergunta é só: "o resultado é sensível a esse
número, e o melhor valor muda de uma família para outra?" Se sim, há espaço para torná-lo dinâmico. Nada aqui escolhe uma
candidata.

| Código | Mudança em relação à v0.55 | Peça |
|---|---|---|
| S1, S2 | passo do NLMS da estrutura e da inovação: 0,02 e 0,2 (v0.55: 0,05) | P2 |
| S3, S4 | passo do NLMS da memória: 0,02 e 0,2 (v0.55: 0,05) | P2 |
| S5, S6 | defasagens do alvo na M1: 1 e 5 (v0.55: 2) | P3 |
| S7, S8 | cadência dos pesos do núcleo (wS, wI, escalas, intervalo): a cada 4 e a cada 16 (v0.55: 8) | P4 |
| S9, S10 | esquecimento da média dinâmica do núcleo: 0,98 e 0,995 (v0.55: 0,99) | P4 |

S1 a S4 mudam o aprendizado da estrutura, que é a referência dos testes, então as decisões de estrutura também podem
mudar. Isso é registrado (estrutura final, entradas aceitas), mas não decide nada.

## 3. Banco (só dados já usados)

| Parte | Séries | Parte A | Parte B |
|---|---|---|---|
| E20 do LEBRE Lab (64 famílias) | 728 | sim | não (custo de tempo) |
| prédios BDG2, posições 115–144 | 30 | sim | sim |
| bacias brasileiras D-A (140–169) e D-B (110–139) | 60 | sim | sim |
| bacias chilenas CL-V (posições 30–49 do sorteio da v0.56) | 20 | sim | sim |
| rios do ONS (reserva 1 e desenvolvimento) | 56 | sim | sim |

As previsões de A, C3, C4 e C5 já gravadas são reaproveitadas; as que faltam (C3 e C4 em D-B e nos rios; C3, C4 e C5 onde
faltarem) rodam com o mesmo código. Travas: as dos carregadores do `DEV-01`, do `DIAG-01` e da v0.56 (só as séries
declaradas).

## 4. Medidas

- Razão de MSE de cada variante contra A, por série: no E20, a função e a janela do E20 (como no `DEV-01`); nas demais
  partes, `reps`, a partir de 30% da série, blocos de 30 (bacias), 168 (prédios) e 56 (rios).
- Custo por passo: mediana e percentil 95 por família.
- Fração de alvos com atualização da M1 (Parte A).
- Sementes do bootstrap: 2026102904 (Parte A) e 2026102905 (Parte B), conferidas como não usadas.

## 5. Regra de escolha da Parte A (fixada antes)

Entre {C4, D1, D2, D3, D4}, uma variante é **admissível** se:
- **K1, nenhuma piora:** em nenhuma família do E20, nem nos prédios, nem em cada grupo de rios, o limite superior do IC 95%
  da razão contra A passa de 1,02;
- **K2, ganho nas bacias dos dois países:** em **cada** um de D-A, D-B e CL-V, log(MSE A ÷ MSE variante) ≥ 0,8 ·
  log(MSE A ÷ MSE C3), com limite inferior do IC acima de zero (pelo menos 80% do ganho da atualização a cada passo);
- **K3, custo:** mediana do custo no banco ≤ 1,25 vez a v0.55;
- **K4:** nenhuma previsão não finita a mais que A.

**Escolha:** a admissível de menor custo mediano; empate (diferença < 0,02), a de maior ganho mínimo entre D-A, D-B e
CL-V. **Se nenhuma for admissível**, o resultado é registrado com o critério que falhou e volta ao responsável pelo
projeto. Nenhuma regra nova é criada depois de ver os resultados.

**Leitura da Parte B (descritiva):** para cada número, a razão contra A por família, nos dois valores testados. Ele é
marcado como **"rouba resultado"** se, em pelo menos uma família, um dos valores alternativos melhorar com IC abaixo de
0,98 **e**, em outra família, o mesmo valor piorar com IC acima de 1,02 (o melhor valor depende do contexto: indício de
que um valor dinâmico ajudaria). Também é marcado se um valor alternativo melhorar em quase todas as famílias (o fixo está
só mal calibrado; aí basta outro fixo).

## 6. O que vem depois

A variante escolhida na Parte A é congelada como nova candidata. Ela passa por:
- uma validação nova em dados nunca tocados: bacias chilenas das posições 50–69 do sorteio da v0.56 e prédios BDG2 das
  posições 265–294, com regras e pré-registro commitados antes;
- a avaliação final, com a reserva já sorteada e o pré-registro já commitado (R1–R6).

Os números marcados na Parte B viram as próximas peças (P2 a P4), cada uma com plano próprio.
