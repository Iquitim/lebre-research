# LEBRE v0.54 — Rascunho 0 da especificação da M6 (ciclo como hipótese)

**Data:** 11/10/2026 · **Status:** critérios fixados antes de qualquer medição registrada; aprovado para medição (M6_E1)
pelo responsável pelo projeto, que delegou a condução até o fim mantendo as regras do projeto. Sem resultado ainda.
**Protótipo:** `experiments/LEBRE-V0.54-PROTO-01`, commit `3a62898` (`lebre054/cycle.py`, parâmetro `m6=True` de
`Lebre054`).

## O problema

A memória da LEBRE só usa um ciclo (por exemplo, 24 passos em dados horários) se o usuário o declarar. Sem declarar, o
erro chega a 2,87 vezes o da v0.53 com o ciclo certo na carga elétrica e a 1,44 vez na solar (linha de base E23), e a
referência trivial da M2 (persistência) não compensa.

## O desenho

O ciclo vira uma hipótese do mecanismo de experimentos, com a mesma evidência sempre válida das adições de estrutura.

- **Candidatos:** ciclos de 7, 12, 24 e 168 passos que o usuário não declarou. Com dois ciclos na memória (declarados ou
  aceitos), a M6 para.
- **Perfil por fase:** para cada candidato s, mantém-se G_s[fase], a média exponencial (taxa 0,1) de y − último valor
  naquela fase do ciclo, como no perfil da memória com ciclo declarado.
- **Evidência específica do ciclo:** o perfil é o componente que só um ciclo explica. Atributos de defasagem, como y(t−s),
  ajudam a prever qualquer série autocorrelacionada e não servem de evidência de ciclo.
- **Triagem:** correlação, em média exponencial, entre o resíduo da memória (y − m) e G_s[fase], feita como a triagem das
  entradas (peso 0,02; um candidato a cada 4 passos). Sem ciclo, a estatística é aproximadamente χ²(1); o limiar é 6,63
  (quantil 0,99), o mesmo das divisões de segmento.
- **Teste (um por vez):** o desafiante m + c·G_s[fase], com c aprendido por NLMS a partir de zero, compete com a memória
  m. A perda é recortada com a escala do próprio resíduo da memória: 2 × raiz da média exponencial (taxa 0,01) de
  (y − m)², só do passado. O e-process é o do núcleo, com hipótese persistente por candidato, no orçamento e-LOND das
  adições. Valem a margem de 0,002, o aquecimento de 250 passos, a regra de varredura, a duração máxima de 5.000 passos e
  a nova tentativa só depois de 2.000 passos, como nas adições.
- **Ação quando aceito:** a memória passa a ser a de um ciclo declarado, Memory(s) ou a memória com os dois ciclos (o
  menor primeiro). Ela roda como sombra durante o teste, aquecida no início com a história guardada (últimos 338 valores,
  só passado), e por isso não parte a frio. Se o usuário não declarou ciclo nem escolheu referência, a referência da M2
  passa a ser a sazonal do menor ciclo aceito, como acontece quando o ciclo é declarado.
- **Custo:** os perfis, a triagem e a história custam ~35 a 50 operações por passo enquanto há candidatos (zero com os dois
  ciclos declarados). Durante um teste, soma-se a memória sombra.

**Consequência:** sem ciclo aceito, as previsões são idênticas às da v0.54 sem M6. Só o custo muda.

## Exploração antes de medir (sementes 20261335 a 20261339, fora de qualquer medição registrada)

1. **Primeiro desenho (memória sazonal completa contra memória comum):** aceitou ciclos falsos em 4 de 5 séries AR(1).
   Descartado.
2. **Perfil como evidência, com a escala do resíduo estrutural:** as perdas saturavam e nenhum ciclo era aceito. A escala
   passou a ser a do resíduo da memória.
3. **NLMS de c normalizado pela potência instantânea:** instável. A normalização passou a usar a potência média.
4. **Termo de perfil como ação:** ganho pequeno, às vezes negativo. A ação passou a ser a memória sazonal completa, em
   sombra.

No desenho final:

- **Série sintética tipo carga** (ciclo de 24 com amplitude persistente e semana): sem declarar, a M6 ficou entre 0,998 e
  1,038 da versão com os ciclos declarados, contra até 1,657 sem a M6.
- **Nulos (5 AR(1) e 5 passeios aleatórios):** nenhum ciclo aceito e previsões idênticas.
- **Limitação vista:** o ciclo semanal (168) quase nunca é aceito depois do diário. O perfil de incrementos semanais é
  evidência fraca de um padrão de nível no fim de semana.

## Critérios (fixados antes da medição M6_E1)

Banco: as 64 famílias do E20. Protótipo no commit `3a62898`. Bootstrap de blocos pareado como no E20, semente 20261341.

1. **Sem piora com o ciclo declarado:** com os argumentos de cada série (ciclo e referência como no E20), `m6=True` contra
   `m6=False`. Em cada família, limite superior do IC 95% da razão de MSE ≤ 1,01; nenhuma previsão não finita.
2. **Sem declarar, nas séries de D02 (B01 e B02):** `m6=True` sem ciclo e sem referência declarados, contra `m6=False`
   com o ciclo declarado. Razão de MSE (média geométrica) ≤ 1,05 em cada uma das duas famílias. As demais famílias com
   ciclo são reportadas.
3. **Nenhum ciclo falso:** nas famílias sintéticas sem ciclo (A01 a A12), sem ciclo declarado e com `m6=True`: nenhuma
   série de A02 com ciclo aceito, e no máximo 5% das séries de A01 a A12 juntas.

Reportados: custo por passo, ciclos aceitos por família e passo da aceitação.

**Regra:** a M6 (rascunho 0) segue para validação em dados novos se atender a 1, 2 e 3; se não, as falhas são declaradas
e nada é ajustado.

## Decisão depois da medição M6_E1 (11/10/2026)

Resultado (LEBRE Lab, `analises/M6_E1_RESULTADO.md`, commits `c1ad4c4` e `9dfcef8`): **não segue**. Atendeu ao critério 1
(sem piora com o ciclo declarado; ganhos na maré) e ao 3 (nenhum ciclo falso em 311 séries sintéticas sem ciclo). Falhou
no 2: sem declarar, B01 1,23 e B02 1,41 (limite 1,05). Sem a M6, esses valores eram 1,44 e 2,87 no E23. Causas vistas:
na carga, o harmônico de 12 passos era aceito primeiro e a memória virava (12, 24); na solar, o múltiplo 168 vencia a
triagem, e as aceitações saíam tarde.

## Rascunho 1 (11/10/2026, depois da M6_E1)

- **Candidatos 7, 24 e 168**, sem o 12 (harmônico de 24 em dados horários). Ciclos mensais (12) ficam fora da M6, o que é
  declarado; as séries mensais do banco têm 300 a 360 passos, curtas demais para a M6 agir.
- **Parcimônia:** entre os candidatos que passam na triagem, testa-se o de menor período.
- **Perfil na sua constante de tempo:** um candidato só abre teste depois de 10 visitas por fase (1/0,1), ou seja, 240
  passos para 24 e 1.680 para 168. Antes disso, o perfil ainda não representa o ciclo, e um teste aberto cedo demais
  fecha e espera 2.000 passos.
- Explorado e descartado: perfis do resíduo da memória em vez dos incrementos.

Exploração (sementes 20261335 a 20261339):

- **Tipo carga:** o ciclo diário foi aceito em 5 de 5 séries. A razão contra a versão declarada ficou entre 1,005 e
  1,199 em 4 delas. Na quinta, o teste do 24 fechou cedo, o 168 entrou sozinho, e a razão foi 1,91.
- **Nulos:** nenhum ciclo aceito em 10 séries.
- **Limitações declaradas:** o ciclo semanal quase nunca entra depois do diário, e quando um teste do ciclo diário fecha
  cedo, o 168 pode entrar sozinho.

Critérios da medição M6_E2 no banco: os da M6_E1, sem mudança. O rascunho 1 só é aceito se também atender a eles numa
validação em dados novos.
