# 10 — B3: o conjunto ativo saturou?

## Mecânica (código autoritativo)
1. **Capacidade:** M_max = 4 átomos estruturais. O latente e o acionamento contam; as entradas atuais da base não contam.
2. **Átomos verdadeiros do B3:** lag(3,12), latente com polo 0,8 e acionamento x0 → latente(0,8).
3. **Dependência de elegibilidade:** o acionamento só é testado depois que um latente é promovido, e herda o polo **desse** latente.
4. **Latente único:** enquanto um latente está ativo, nenhum outro polo é testado.
5. **Conjunto cheio:** existe substituição, mas só de vítimas com R ≥ h/2.

## Linha do tempo por semente (`10_B3_ACTIVE_SET_TIMELINES.png`, `RUN_MAIN_B3_TIMELINE.csv`)
- Em **10 de 10 sementes** o primeiro latente promovido tem polo **0,0 ou 0,5**. O polo 0,8 **nunca** fica ativo: tempo ativo com polo 0,0 = 46,6%, polo 0,5 = 50,2%, nenhum = 3,1%.
- O orçamento fica cheio (4 átomos) em só **3,5%** dos instantes de decisão. Houve **0** cruzamentos de limiar bloqueados por orçamento cheio.
- O lag(3,12) verdadeiro é encontrado em 10/10 sementes. Aparecem atrasos aproximados de x0 (1 e 2 passos), mas raramente, em 1–2 sementes.
- **Sensibilidade a τ:** o res(0,8) chega a ser promovido quando o prior é conservador (ρ = 1/1000: 5/10 sementes). Mesmo assim, a estrutura exata continua 0, porque os outros átomos deixam de ser encontrados.

## Resposta
**A estrutura verdadeira é representável, mas inalcançável pela política atual de busca e seleção.**
- O latente de polo 0,8 com acionamento x0 reproduz o processo z exatamente, então não falta representação.
- O que falta é um caminho até essa estrutura: o polo que primeiro acumula evidência (o mais simples) ocupa a única vaga de latente, e o acionamento correto nunca fica elegível.

A hipótese da crítica ("atrasos aproximados enchem as vagas") **não** é o mecanismo no código original. A ausência de troca é uma escolha da réplica, porque o código tem troca.

- `B3_ACTIVE_SET_SATURATION = NOT_SUPPORTED` (como mecanismo no código original).
- `B3_FAILURE_EXPOSES_SPECIFICATION_GAP = YES`: nem a regra de troca nem o limite de um latente estão na especificação.
- Mecanismo real: `WRONG_ATOM_PROMOTION + ELIGIBILITY_DEPENDENCY` (latente único, polo definido pelo primeiro que cruza o limiar).
