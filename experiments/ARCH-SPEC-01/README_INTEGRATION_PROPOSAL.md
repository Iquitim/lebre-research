# Root README Integration Proposal: LEBRE Architecture v0.1
**Stage:** ARCH-SPEC-01 / ARCH-SPEC-01R  
**Target:** Non-invasive proposed insertion block for repository root `README.md`  
**Governing Rule:** Do NOT overwrite or modify the root README unless explicitly authorized.

---

## 1. English Integration Block (Proposed for root `README.md`)

```markdown
---

<p align="center">
  <img src="logo/LEBRE Logo.png" alt="LEBRE Architecture logo" width="600">
</p>

## LEBRE Architecture (v0.1)
**Lifecycle-governed Evidence-Based Resource Evolution**  
*Formerly designated as "Track B Single-State Organization" (Codinome Lebre)*

LEBRE is an online adaptive learning architecture for streaming regression under micro-edge compute constraints (mean algorithmic compute below the 100-FLOP R2 threshold and $\le 1024$ bytes of persistent model RAM). Instead of maintaining static dense networks, LEBRE treats observable features, temporal delay taps, and internal recurrent states as **cost-bearing adaptive computational structures** governed by an evidence-driven lifecycle:

$$\text{DORMANT} \longrightarrow \text{PROVISIONAL} \longrightarrow \text{ACTIVE} \longrightarrow \text{MATURE} \longrightarrow \text{EVICTED / RECLAIMED}$$

### Key Characteristics:
- **Non-Interfering Shadow Probation:** Candidate structures learn in shadow mode without coupling to live predictions, completely shielding active inference from candidate shock.
- **Two-Timescale Quiescent Retention:** Decouples fast activity from slow structural relevance ($U_{\text{ret}}$), preserving memory across extended silence intervals.
- **Asymmetric Obsolescence Governance:** Positive obsolescence evidence ($O_{\text{obs}}$) prevents cyclic eviction churn.
- **Micro-Edge Efficiency:** Measured **90.44 mean FLOPs/step** (observed transient peak $\approx 206$ FLOPs/step) and **440.0 bytes persistent model RAM** across 15 benchmark workloads (BENCH-01B) with **zero observed numerical divergences** across 450 evaluation runs.

### Documentation & Specifications:
- 📖 [Executive Overview (English)](docs/architecture/LEBRE_OVERVIEW_EN.md) | [Visão Geral Executiva (Português)](docs/architecture/LEBRE_OVERVIEW_PTBR.md)
- 📐 [Full Specification v0.1 (EN)](docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md) | [Especificação Formal v0.1 (PT-BR)](docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md)
- 📄 [Condensed Publication PDF (EN)](docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf) | [PDF Condensado de Publicação (PT-BR)](docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf)
- 📊 [Architectural Diagrams](docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md) | [Architectural Decision Records (ADRs)](docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md)
- 🔍 [Traceability Matrix](docs/architecture/LEBRE_TRACEABILITY_MATRIX.csv) | [Constant Traceability](docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md) | [Manifest (YAML)](docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml)

---
```

---

## 2. Brazilian Portuguese Integration Block (Proposta para o `README.md`)

```markdown
---

<p align="center">
  <img src="logo/LEBRE Logo.png" alt="Logotipo da Arquitetura LEBRE" width="600">
</p>

## Arquitetura LEBRE (v0.1)
**Lifecycle-governed Evidence-Based Resource Evolution**  
*(Evolução de Recursos Baseada em Evidência e Governada por Ciclo de Vida)*  
*Designação experimental anterior: "Organização de Estado Único Track B" (Codinome Lebre)*

A LEBRE é uma arquitetura online de aprendizado adaptativo para regressão em streaming contínuo sob restrições de micro-recursos (computação algorítmica média abaixo do limiar R2 de 100 FLOPs e $\le 1024$ bytes de RAM persistente de modelo). Em vez de manter redes estáticas densas ou reservatórios fixos, a LEBRE trata atributos observáveis, atrasos temporais (lags) e estados recorrentes internos como **estruturas computacionais adaptativas com custo**, governadas por um ciclo de vida orientado por evidência:

$$\text{DORMENTE} \longrightarrow \text{PROVISÓRIO} \longrightarrow \text{ATIVO} \longrightarrow \text{MADURO} \longrightarrow \text{REMOVIDO / RECLAMADO}$$

### Características Centrais:
- **Estágio Probatório em Sombra:** Candidatos aprendem em paralelo sem conexão à predição ativa, blindando o sistema contra choques transitórios.
- **Retenção Quiescente em Duas Escalas:** Desacopla a atividade rápida da relevância lenta ($U_{\text{ret}}$), preservando a memória durante longos períodos de silêncio.
- **Governança de Obsolescência Assimétrica:** Acumula evidência positiva ($O_{\text{obs}}$) para eliminar oscilações cíclicas de despejo e renascimento.
- **Eficiência Micro-Edge:** Operou com média de **90,44 FLOPs/passo** (pico transitório observado $\approx 206$ FLOPs/passo) e **440,0 bytes de RAM persistente de modelo** ao longo de 15 fluxos contínuos (BENCH-01B), com **zero divergências numéricas observadas** em 450 execuções avaliadas.

### Documentação e Especificações:
- 📖 [Visão Geral Executiva (Português)](docs/architecture/LEBRE_OVERVIEW_PTBR.md) | [Executive Overview (English)](docs/architecture/LEBRE_OVERVIEW_EN.md)
- 📐 [Especificação Formal v0.1 (PT-BR)](docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md) | [Full Specification v0.1 (EN)](docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md)
- 📄 [PDF Condensado de Publicação (PT-BR)](docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf) | [Condensed Publication PDF (EN)](docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf)
- 📊 [Diagramas Arquiteturais](docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md) | [Registros de Decisão (ADRs)](docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md)
- 🔍 [Matriz de Rastreabilidade](docs/architecture/LEBRE_TRACEABILITY_MATRIX.csv) | [Rastreabilidade de Constantes](docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md) | [Manifesto (YAML)](docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml)

---
```
