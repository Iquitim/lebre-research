# LEBRE v0.54 — Rascunho 0 da especificação da M4 (remoções que acontecem)

**Data:** 11/10/2026 · **Status:** critérios fixados antes de qualquer medição registrada; aprovado para medição (M4_E1)
pelo responsável pelo projeto, que delegou a condução até o fim mantendo as regras do projeto. Sem resultado ainda.
**Protótipo:** `experiments/LEBRE-V0.54-PROTO-01`, commit `438ac08` (`lebre054/removal.py`, parâmetro `m4=True` de
`Lebre054`).

## O problema

Na LEBRE, a estrutura só cresce. Uma unidade aceita (por exemplo, uma entrada com suas faixas de atraso) é testada para
remoção periodicamente, a cada 2.000 passos. A remoção é aceita quando o e-process acumula evidência de que tirar a unidade
não piora a perda recortada em mais que a margem de 0,002. Na linha de base (E23), depois de uma troca de regime, a
entrada antiga nunca foi removida (0 de 20 séries de A05).

## Por que as remoções não acontecem (exploração antes de medir)

Exploração com o gerador de A05 (sementes 20261310 a 20261319, nenhuma de medição registrada). Foram encontradas três
causas, nesta ordem.

1. **Evidência persistente.** A hipótese de remoção de uma unidade é uma só desde a aceitação e acumula todos os
   episódios de teste. Antes da troca de regime, remover era claramente pior, e a log-evidência chega à troca em cerca de
   −2,7. Depois da troca, mesmo um episódio de 5.000 passos com a remoção à frente termina abaixo de zero. Em série não
   estacionária, a nula "em média sobre todo o passado testado" é a nula errada para remover.
2. **Orçamento gasto à toa.** Com uma hipótese nova por episódio, cada teste periódico consome um nível e-LOND. Os 8 a 10
   testes inúteis antes da troca levam o limiar a 8,3 a 8,7 (log da evidência), contra 3,5 no primeiro teste.
3. **Efeito pequeno na escala da perda.** Depois da troca, o ganho por passo de remover é ~0,0018, mais a margem de 0,002.
   O λ ótimo (~2,3) fica acima da grade do e-process (máximo 0,9), e a evidência cresce ~0,0011 por passo. Em 5.000
   passos (o limite de duração de um episódio) chega a 5,4 a 6,5.

## O desenho

Mudanças só no ciclo de vida das remoções; adições, trocas e divisões ficam como estão.

- **Evidência por episódio:** cada teste de remoção é uma hipótese nova: "nos passos deste episódio, remover a unidade não
  melhora a perda recortada em mais que a margem" (a margem de 0,002 fica como está). O e-process começa do zero.
- **Orçamento próprio:** nível e-LOND α × γ_k × (remoções aceitas + 1), limitado a 0,5, com α = 0,05 e
  γ_k = C / (k · log²(k+1)) (a mesma sequência do núcleo, com soma ≤ 1), k contando só os testes de remoção. As
  hipóteses de adição, troca e divisão continuam com o orçamento original, sem contar remoções. A garantia sobre remoções
  falsas (remover o que piora mais que a margem) é separada da garantia sobre adições falsas.
- **Abertura por queda da contribuição:** um teste de remoção só abre quando a contribuição média da unidade (média
  exponencial de |w·b| com taxa 0,01, que o núcleo já mantém) fica abaixo de **FRAC_REM = 0,5** × a referência. A
  referência é o pico desde a aceitação e volta ao valor atual a cada teste, então cada novo teste exige mais uma queda
  pela metade. A regra usa só o passado, o que mantém a validade. Continuam valendo o intervalo mínimo de 2.000 passos
  entre testes da mesma unidade e a regra de varredura (fecha depois de 100 passos se não estiver à frente).
- **Duração do episódio:** até **T_MAX_REM = 10.000** passos (os demais testes continuam com 5.000). A validade do
  e-process não depende de quando o episódio termina.
- **Custo:** a referência custa 2 operações por unidade ativa a cada decisão (a cada 10 passos). Testes de remoção
  inúteis deixam de abrir, o que economiza.

**Consequência:** enquanto nenhuma unidade é aceita, a v0.54 com M4 é idêntica à v0.54 sem M4. Depois, as trajetórias
podem diferir mesmo sem remoção, porque os testes de remoção deixam de ocupar slots no calendário antigo.

**Exploração (as mesmas sementes):**

- **Gerador de A05:** a entrada antiga foi removida em 10 de 10 séries, de 1.700 a 7.550 passos depois da troca. O MSE
  depois da troca, comparado à v0.54 sem M4, ficou entre 0,981 e 1,022 (média geométrica ~1,00). As duas piores séries
  pioraram por efeitos de caminho: uma aceitação atrasada em 310 passos e outro atraso de pico escolhido.
- **Gerador de A01 (d = 10):** nenhuma entrada verdadeira removida em 10 de 10 séries.
- **Passeios aleatórios independentes** (substituto sintético de níveis, sementes 20261323 a 20261333): entradas externas
  espúrias aceitas em 5 de 11 séries, e nenhuma removida. A contribuição delas não cai, então a M4 sozinha não resolve a
  interpretação em níveis (isso é a M3).

## Critérios (fixados antes da medição M4_E1)

Comparação: protótipo no commit `438ac08`, `Lebre054` com `m4=True` contra `m4=False` (os dois com a M5a, sem a M5b), nos
mesmos argumentos de cada série. Banco: as 64 famílias do E20.

1. **A05:** entrada antiga (x0) removida entre a troca e 10.000 passos depois em pelo menos 14 de 20 séries.
2. **Sem remoções falsas:** em A01 (30 séries), nenhuma entrada verdadeira (x0, x1) removida. Em A02, nenhuma série com
   entrada falsa na estrutura final (como na v0.53).
3. **Sem piora:** em cada família, razão de MSE com M4 ÷ sem M4 (média geométrica), IC 95% por bootstrap de blocos
   pareado (blocos como no E20; semente 20261340): limite superior ≤ 1,02. Nenhuma previsão não finita no trecho
   avaliado.
4. **Identidade:** onde nenhuma unidade foi aceita, previsões idênticas.

Reportados sem critério: C03 (entrada externa na estrutura final; aceita em algum momento), número de remoções por
família e custo.

**Regra:** a M4 (rascunho 0) segue para validação em dados novos se atender a 1 a 4; se não, as falhas são declaradas e
nada é ajustado.

## Decisão depois da medição M4_E1 (11/10/2026)

Resultado (LEBRE Lab, `analises/M4_E1_RESULTADO.md`, commit `6e30c47`): **não segue**. Atendeu ao critério 1 (A05: 17 de
20 no prazo), ao 2 (nenhuma remoção falsa) e ao 4 (identidade). Falhou no 3:

- **A07** (relação que liga e desliga em blocos de 5.000 passos): +14%. A M4 removia a entrada nos blocos desligados e
  precisava redetectá-la depois.
- **B03:** limite superior 1,0214 **sem nenhuma remoção**, só porque o calendário de testes mudou.

## Rascunho 1 (11/10/2026, depois da M4_E1)

- **O teste disparado é acrescentado ao calendário original, não o substitui.** Os testes periódicos com hipótese
  persistente continuam como no núcleo; enquanto nenhum disparo acontece, as previsões são idênticas às do núcleo.
- **Prioridade do disparado:** se o disparo vale e a unidade só está ocupada por um teste periódico de remoção, esse teste
  é encerrado (a hipótese persistente fica guardada; encerrar um episódio é sempre válido) e o disparado assume. Sem
  isso, os testes periódicos de 5.000 passos, sem chance de aceitar, bloqueavam o disparado (visto num teste do
  protótipo).
- **Duração mínima para aceitar:** a remoção disparada só é aceita depois de pelo menos **N_REM_MIN = 5.000** passos de
  evidência no episódio, o mesmo limite de duração de um episódio de adição. A remoção passa a exigir pelo menos o tempo
  que uma adição pode usar. Aceitar só depois de um mínimo de amostras é um tempo de parada válido.

Exploração (as mesmas sementes de antes, fora do banco):

- **Tipo A05:** x0 removida em 10 de 10 séries, todas até 7.600 passos depois da troca; média geométrica do MSE 0,9997.
- **Tipo A07:** nenhuma remoção, previsões idênticas.
- **Tipo A01:** previsões idênticas.

Critérios da medição M4_E2 no banco: os da M4_E1, sem mudança. Como o banco já foi visto pela M4, o rascunho 1 só é
aceito se também atender aos mesmos critérios numa validação em dados novos, com plano fixado antes e usada uma única vez.

## Aceite na validação 7 (11/10/2026)

Validação 7 do LEBRE Lab (plano `analises/VALIDACAO7_PLANO.md`, commit `1b78d47`; resultado `VALIDACAO7_RESULTADO.md`),
usada uma única vez: **a M4 (rascunho 1) é aceita**. T-A05: x0 removida em 20 de 20 séries até 10.000 passos depois da
troca; nenhuma remoção falsa (T-A01, T-A02); pior limite superior 1,0048 (T-A07); identidade onde nada foi aceito.
**Ressalva declarada:** em 2 de 20 séries de T-A07, a remoção aconteceu no retorno da relação intermitente (a duração
mínima de 5.000 passos coincide com o bloco desligado do gerador). A M4 não resolve a interpretação em níveis (M3), e a
evidência vinculante continua sendo a avaliação final pré-registrada da v0.54.
