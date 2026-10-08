# Reflexão sobre a M2 depois de seis rascunhos (08/10/2026)

**Decisão do responsável pelo projeto:** a v0.53 não é promovida sem a M2. Volta-se à literatura, à reflexão e à
experimentação, com o mesmo rigor. Este documento organiza o que se sabe antes de qualquer novo experimento.

## 1. O problema, em uma frase

Combinar a referência trivial R e a LEBRE L de modo que a saída fique a no máximo 1% de R onde R é melhor (critério 1) e
a no máximo 2% de L onde L é melhor (critério 2), com intervalo de 95%, em séries longas e curtas.

## 2. O que as seis tentativas mostram: duas dificuldades diferentes

| | D1: a LEBRE aprende (competência não estacionária) | D2: diferenças pequenas com pouca informação |
|---|---|---|
| Casos | C05 (rascunho 1), B02 curto (2), Arinos (4) | C04 juros de 2 anos (6), VC05 serviços (6), negativas (5) |
| Mecanismo | L começa muito pior e fica melhor; quem pesa todo o passado igualmente demora a trocar | R e L ficam a poucos % um do outro; qualquer hesitação aparece no intervalo |
| O que resolveu | esquecer o passado (compartilhamento, rascunhos 5 e 6) | concentrar rápido no líder acumulado (rascunho 4) |
| O que quebrou | esquecer faz hesitar nas diferenças pequenas (D2) | concentrar no acumulado não esquece a fase de aprendizado (D1) |

As soluções de D1 e de D2 puxam em direções opostas quando o algoritmo trata R e L de forma **simétrica**.

## 3. O que a teoria diz (PRA-09)

- **Não há almoço grátis:** para dois previsores, ficar muito perto de um em toda sequência obriga a ficar longe do outro
  em alguma sequência (Koolen, 2013; Even-Dar et al., 2008). A troca é quantificada exatamente pela fronteira de Pareto.
- Logo, em séries curtas com diferença pequena (D2), **alguma** sequência sempre derruba um dos critérios. A pergunta útil
  não é "existe um algoritmo que passe sempre" (não existe), e sim "qual ponto da fronteira os nossos dados e critérios
  pedem, e com que informação a mais".

## 4. Três saídas possíveis

1. **Informação a mais, declarada (prioridade assimétrica).** A v0.52 já recebe do usuário o tipo do alvo: "variação"
   (retornos, mudanças de juros), em que a referência declarada é zero, ou nível/medida física. Para variações, a teoria de
   mercados eficientes sugere que R é difícil de bater (prioridade em R); para o resto, a v0.52 venceu a referência em
   quase todas as famílias (prioridade em L). Uma prioridade assimétrica por tipo declarado escolhe pontos diferentes da
   fronteira para casos diferentes **com informação dada antes dos dados**. Ponto em aberto: o valor da prioridade é uma
   escolha; precisa vir de um princípio, não de ajuste (candidato: o ponto da fronteira de Koolen cuja razão de
   arrependimentos corresponda à razão das margens dos critérios, 1% contra 2%).
2. **Tratar a LEBRE como previsor que aprende (D1 diretamente).** A "switch distribution" (van Erven et al., 2012) foi
   desenhada para o caso "modelo simples primeiro, complexo depois": mistura sobre o instante da troca de R para L, num só
   sentido. Ela esquece a fase de aprendizado de L sem dar a L a liberdade de voltar e hesitar, que foi o que custou nos
   rascunhos 5 e 6. Ainda não foi testada.
3. **Rever os critérios, por princípio e antes de novos dados.** Em séries curtas, o limite superior <= 1,02 só aprova,
   na prática, uma saída idêntica à da v0.52; famílias sem poder estatístico para decidir deveriam ser declaradas
   "inconclusivas", não "falhas", com uma análise de poder feita **antes**. Isso muda a régua, então é decisão do
   responsável pelo projeto, vale só para medições futuras e não pode ser usado para reaproveitar resultados já vistos.

## 5. Disciplina daqui em diante

- O banco de desenvolvimento e a validação 1 passam a ser **dados de desenvolvimento**: podem ser usados à vontade para
  diagnóstico e desenho, mas já não servem como evidência de seleção.
- A evidência de seleção virá de uma **validação 2 nova**, montada e congelada antes da escolha, usada uma vez; depois, a
  reserva final, uma vez.
- Toda tentativa é registrada e o relatório final declara o número total (seis até aqui).
