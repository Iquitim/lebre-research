# A LEBRE v0.3.2 pode ser considerada uma arquitetura?

**Método.** Os critérios vêm de quatro tradições em que o termo "arquitetura" tem definição publicada. A LEBRE v0.3.2 é avaliada contra cada um,
e as objeções mais fortes são registradas. As fontes foram localizadas por busca nesta sessão.

## 1. O que a literatura chama de "arquitetura"

| Tradição | Definição / uso | Fonte |
|---|---|---|
| Engenharia de sistemas | "conceitos ou propriedades fundamentais de uma entidade em seu ambiente e princípios que governam sua realização e evolução" — cobre elementos, relações, comportamento, estrutura e princípios de projeto e evolução. Distingue arquitetura (a coisa) de descrição de arquitetura (o documento) | ISO/IEC/IEEE 42010:2022 |
| Arquiteturas cognitivas | "estruturas fixas" (processos, memórias, controle) que, com o conhecimento adquirido, produzem comportamento; é infraestrutura independente de tarefa, não um algoritmo para um problema | Newell; Laird (Soar); Rosenbloom, *Thoughts on Architecture* (arXiv 2306.13572) |
| Arquiteturas de aprendizado | organização de componentes de aprendizado com regras de mudança estrutural: *Cascade-Correlation Learning Architecture* (Fahlman & Lebiere, NIPS 1990) cresce a própria topologia; *Dyna* (Sutton 1990) integra aprendizado, planejamento e reação; *Horde* (Sutton et al., AAMAS 2011) organiza muitos aprendizes online em tempo real | citados |
| Busca de arquitetura neural | arquitetura = topologia do grafo computacional (operações e conexões) dentro de um espaço de busca | Elsken, Metzen & Hutter, JMLR 20 (2019) |

## 2. Critérios operacionais derivados

| # | Critério | Origem |
|---|---|---|
| K1 | Elementos distintos, com papéis e interfaces definidos | 42010 |
| K2 | Relações explícitas: separação entre fluxo de dados e fluxo de controle | 42010, cognitivas |
| K3 | Princípios que governam a realização e a **evolução** (inclusive em tempo de execução) | 42010 |
| K4 | Infraestrutura fixa e independente de tarefa; o conteúdo é aprendido | cognitivas |
| K5 | Família parametrizada, especificável independentemente da implementação | 42010, NAS |
| K6 | Composição não trivial: as interações importam (ablações) | CAR-01 do projeto; resposta à crítica "bag of tricks" |
| K7 | Espaço de topologias com uma regra que o percorre | NAS; Cascade-Correlation |

## 3. Avaliação da LEBRE v0.3.2

| Critério | Veredito | Evidência |
|---|---|---|
| K1 | ✅ | nove elementos com interface própria: base, atrasos, latente (inovação + acionamento), triagem, testes provisórios, supervisor de ciclo de vida, monitor de remoção (CUSUM), governador de recursos (orçamento + aluguel), portão de excitação, e a interface de explicação |
| K2 | ✅ | o fluxo de dados (predição) não depende do fluxo de controle (decisões) exceto pelo conjunto ativo; os candidatos nunca tocam a predição (probação em sombra) |
| K3 | ✅ | invariantes: toda decisão é um teste com erro controlado; toda evidência corre em tempo de fluxo; toda estrutura é cara e precisa pagar aluguel; silêncio não é evidência; equivariância de escala |
| K4 | ✅ | a mesma maquinaria serve D = 1..50 e 25 tarefas externas sem nenhuma calibração; muda só o conteúdo aprendido (quais átomos e quais coeficientes) |
| K5 | ✅ | parâmetros de família (d, L, banco de polos, M_max, α, ARL, T_idle); a especificação independe de linguagem e há implementação de referência congelada por hash |
| K6 | ✅ (com evidência nesta revisão) | sem auto-normalização há 0,21–0,26 falsas promoções por fluxo; sem portão de excitação, promoções espúrias no silêncio; sem aluguel, átomos ociosos permanecem; sem aquecimento (v0.3.1), descoberta bloqueada por centenas de passos; sem o átomo de acionamento, cadeias de atrasos |
| K7 | ✅ | o preditor instanciado é um grafo linear-dinâmico esparso (linear + atrasos + filtros IIR de 1ª ordem) cuja topologia muda online sob uma regra estatística |

## 4. Objeções mais fortes (e resposta)

1. **"É um algoritmo, não uma arquitetura."** Cada primitivo é arte anterior (Kalman, NLMS, martingales de mistura, CUSUM). *Resposta:* o mesmo vale
   para Cascade-Correlation, Dyna e Horde. O que se reivindica é a **organização** (K1–K3, K6), não um primitivo novo. A LEBRE não reivindica uma nova regra de aprendizado.
2. **"A classe de modelos é só linear nos parâmetros."** É verdade: a expressividade é a de um ARX/OBF esparso com estado latente de 1ª ordem. *Consequência:*
   ela é uma arquitetura de **aprendizado estrutural online para modelos lineares-dinâmicos esparsos**, não uma arquitetura neural genérica.
3. **"Arquitetura exige desempenho que a justifique."** Isso não é critério de definição, mas é critério de relevância. Ver o BENCH-02 (`BENCH02_REPORT.md`).
4. **Governança do projeto.** A v0.1 canônica (organização do Track B) está congelada. A v0.3.2 não a substitui; ela é uma **especificação de pesquisa**
   de uma nova versão da família LEBRE.

## 5. Veredito

**SIM**, no sentido da ISO/IEC/IEEE 42010 e da tradição de "arquiteturas de aprendizado" (Cascade-Correlation, Dyna, Horde): todos os critérios K1–K7 são satisfeitos.
**Classificação proposta:** `PRINCIPLED_ONLINE_STRUCTURAL_LEARNING_ARCHITECTURE` — status `RESEARCH_SPECIFICATION_NON_CANONICAL`.
**Não é:** uma arquitetura de rede neural, uma nova regra de aprendizado, nem um modelo universal de sequências.
