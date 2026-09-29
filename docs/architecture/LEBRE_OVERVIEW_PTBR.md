<p align="center">
  <img src="../../logo/LEBRE Logo.png" alt="Logotipo da Arquitetura LEBRE" width="700">
</p>

# Arquitetura LEBRE: Visão Geral Executiva
**Expansão Oficial:** Lifecycle-governed Evidence-Based Resource Evolution  
*(Evolução de Recursos Baseada em Evidência e Governada por Ciclo de Vida)*  
**Versão da Especificação:** 0.1 | **Status:** CONGELADA_COM_LIMITES_DE_ESCOPO  
**Proveniência Histórica:** Organização de Estado Único Track B (*Codinome Lebre*)  

---

## 1. Sumário Executivo

A **LEBRE** é uma arquitetura de aprendizado online adaptativo, projetada para regressão streaming contínua sob restrições de computação e memória em dispositivos micro-edge. Em vez de manter uma rede estática densa ou um reservatório fixo, a LEBRE trata features observáveis, atrasos temporais (lags) e estados recorrentes internos como **estruturas computacionais adaptativas com custo**. Cada componente estrutural está submetido a um ciclo de vida unificado e orientado por evidência ($\text{DORMANT} \to \text{PROVISIONAL} \to \text{ACTIVE} \to \text{MATURE} \to \text{EVICTED}$). Ao isolar candidatos em estágio probatório em sombra (sem interferência no modelo ativo), desacoplar atividade rápida de relevância estrutural lenta durante fases de quiescência, e exigir evidência positiva de obsolescência antes da remoção, a LEBRE atinge adaptação contínua e estável com pegada média observada de 440,0 bytes de estado persistente do modelo (em conformidade com o teto R2-MEM $\le 1024$ bytes; excluindo stack e runtime de hardware) e custo computacional médio observado dentro do limiar R2-FLOP de 100 FLOPs/passo (média de 90,44 FLOPs/passo, pico transitório observado de $\approx 206$ FLOPs/passo).

---

## 2. O Ciclo de Vida Estrutural Central

Cada elemento adaptativo na LEBRE é governado por uma máquina de estados explícita de 5 estágios:

$$\text{DORMENTE} \xrightarrow{\text{Gatilho de Erro Residual}} \text{PROVISÓRIO} \xrightarrow{\text{Utilidade Probatória}} \text{ATIVO} \xrightarrow{\text{Idade } \ge \tau_{\text{mature}}} \text{MADURO} \xrightarrow{\text{Obsolescência Positiva}} \text{REMOVIDO / RECLAMADO}$$

- **DORMANT (Dormente):** Estrutura latente consumindo 0 FLOPs e 0 bytes de memória ativa.
- **PROVISIONAL (Estágio Probatório em Sombra):** O candidato aprende parâmetros em paralelo sem conexão com a predição ativa, blindando o sistema contra choques transitórios.
- **ACTIVE (Ativo):** Estrutura promovida e conectada à inferência em tempo real ($\hat{y}_t = \hat{y}_{\text{base}, t} + \hat{y}_{\text{rec}, t}$), protegida por um período de maturação inicial.
- **MATURE (Maduro):** Estrutura estabelecida que deve continuamente "pagar aluguel" através de utilidade preditiva ou estrutural sustentada ($U_{\text{ret}}$).
- **EVICTED & RECLAIMED (Removido e Reclamado):** Estrutura fisicamente excisada cujos arrays são desalocados e laços de computação eliminados, liberando recursos para o orçamento ativo.

---

## 3. Principais Resultados Empíricos (Benchmark Selado BENCH-01B)

A LEBRE foi avaliada em 15 cargas de trabalho contínuas (diagnósticos mecanicistas do Bloco A, testes de generalização e fluxos físicos/sensores reais do Bloco B) ao longo de 30 sementes independentes ($N=30$, totalizando 6.750 execuções competitivas) contra 14 arquiteturas de referência:

| Métrica / Carga de Trabalho | LEBRE (Track B Congelada) | Baseline Minimal GRU | Baseline Online ESN | Contexto do Benchmark Selado |
| :--- | :---: | :---: | :---: | :--- |
| **Média de FLOPs / Passo** | **90,44** (Pico $\approx 206$) | 281,80 | 1.683,67 | **APROVADA** (Média abaixo do limiar R2-FLOP $\le 100$) |
| **RAM Persistente de Modelo** | **440,0 Bytes** | 569,6 Bytes | 6.112,0 Bytes | **APROVADA** (Teto R2-MEM $\le 1024$; exclui stack/SO) |
| **NMSE Médio no Benchmark** | **0,7023** | 0,8730 | 0,8161 | Avaliado em todas as 15 cargas contínuas |
| **Divergências Observadas** | **0 / 450 (0,00%)** | 0 / 450 (0,00%) | 0 / 450 (0,00%) | Nenhuma divergência numérica observada na LEBRE |
| **Real B1 (NSW Eletricidade)** | 0,8364 NMSE | 2,4146 NMSE | 1,4238 NMSE | CCN obteve menor erro (0,4632); LEBRE operou a 24,0 FLOPs |
| **Real B2 (Clima de Jena)** | **0,0248 NMSE** | 0,0742 NMSE | 0,3284 NMSE | LEBRE liderou baselines; RZA-LMS e CCN divergiram |
| **Real B3 (Sensor de Gás)** | **0,00203 NMSE** | 0,02410 NMSE | 0,26080 NMSE | LEBRE obteve menor erro global (79,9 FLOPs) |
| **Real B4 (Silverbox ID)** | 0,9932 NMSE | 0,9999 NMSE | **0,9136 NMSE** | Fronteira documentada: reservatório denso ESN superou estado escalar |
| **Real B5 (Demanda Elétrica)**| **0,00403 NMSE** | 0,09240 NMSE | 0.11290 NMSE | LEBRE obteve menor erro (CCN: 0,0120, RZA: 0,0912) |

---

## 4. Limitações e Fronteiras Conhecidas

A LEBRE v0.1 é documentada sob fronteiras operacionais explícitas:
1. **Teto de Recorrência Escalar ($N \le 1$):** Validada estritamente para no máximo um estado escalar recorrente ativo. A capacidade multi-estado ($N > 1$) está reservada para o futuro Marco M3 (não aberto).
2. **Registradores de Deslocamento de Alta Ordem (Tarefas A2–A4):** Um único estado escalar não pode representar linhas de atraso puro sem bancos explícitos de features defasadas.
3. **Identificação Não Linear Contínua (Tarefa B4 Silverbox):** Dinâmicas físicas complexas favorecem reservatórios aleatórios multidimensionais densos (Online ESN).
4. **Micro-Regimes ($< 200$ passos):** O mecanismo de histerese assimétrica exige evidência sustentada de obsolescência, retendo temporariamente estruturas através de transientes ultracurtos.
5. **Status de Implantação em Hardware:** A LEBRE é candidata para futura implantação em sistemas embarcados restritos com base em sua baixa computação algorítmica medida e reduzida pegada de estado persistente; a implantação física em hardware (latência de relógio, consumo de energia, memória total de runtime) ainda não foi validada.

---

## 5. Não-Objetivos Arquiteturais

A LEBRE **não é**:
- Um modelo de linguagem (LLM) ou substituto para Transformers.
- Uma simulação biológica do cérebro ou rede neuromórfica estrita.
- Um framework de treinamento em lote (offline batch learning).
- Uma arquitetura para aprender representações latentes profundas e arbitrárias.

---

## 6. Links da Documentação (Relativos)

- **Especificação Formal Completa (Inglês):** [LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md](LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md)
- **Especificação Formal Completa (Português):** [LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md](LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md)
- **Diagramas Arquiteturais:** [LEBRE_ARCHITECTURE_DIAGRAMS.md](LEBRE_ARCHITECTURE_DIAGRAMS.md)
- **Registros de Decisão Arquitetural (ADRs):** [LEBRE_ARCHITECTURAL_DECISIONS.md](LEBRE_ARCHITECTURAL_DECISIONS.md)
- **Matriz de Rastreabilidade:** [LEBRE_TRACEABILITY_MATRIX.csv](LEBRE_TRACEABILITY_MATRIX.csv)
- **Auditoria de Rastreabilidade de Constantes:** [LEBRE_CONSTANT_TRACEABILITY.md](LEBRE_CONSTANT_TRACEABILITY.md)
- **Manifesto em YAML:** [LEBRE_ARCHITECTURE_MANIFEST.yaml](LEBRE_ARCHITECTURE_MANIFEST.yaml)
