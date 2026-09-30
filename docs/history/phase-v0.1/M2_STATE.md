# M2_STATE.md

## Milestone M2: Temporal and Sequential Learning Under Fixed Compute

### Status: CERTIFIED / FROZEN WITH SCOPE LIMITS (M2-R1 Complete — M2_SINGLE_STATE_CORE FROZEN)

---

## 1. Governance & Milestone Isolation
- **M1 Freeze**: Milestone M1 is formally frozen and closed under `M1_SPEC.md`. No modifications to `M1_SPEC.md` or frozen M1 production logic are permitted.
- **Scope of Milestone M2**: Investigate whether the validated M1 sparse online structure discovery principles transfer to temporal and sequential environments without requiring recurrent neural network architectures (no RNN, LSTM, GRU, Transformer, attention, or learned embeddings).
- **Current Milestone Status**:
  - `M2_EXP_0001_STATUS = STRONG_GO`
  - `M2_EXP_0002_STATUS = STRONG_GO`
  - `M2_EXP_0003_STATUS = STRONG_GO`
  - `M2_EXP_0004_STATUS = STRONG_GO`
  - `M2_EXP_0005_STATUS = PARTIAL_GO (Revised via M2-EXP-0005R)`
  - `M2_EXP_0005R_STATUS = AUDIT_COMPLETE`
  - `M2_EXP_0006_STATUS = STRONG_GO`
  - `M2_R1_STATUS = FROZEN_WITH_SCOPE_LIMITS`
  - `QUIESCENT_RETENTION = VALIDATED`
  - `OBSOLETE_STATE_EVICTION = VALIDATED_WITH_SCOPE_LIMITS`
  - `EVICTION_COST_ASYMMETRY = ROBUST`
  - `STATE_UTILITY_PRINCIPLE = TEMPORAL_CO_PLUS_POSITIVE_OBSOLESCENCE`
  - `MULTI_STATE_CAPACITY_JUSTIFIED = NOT_YET`
  - `ARCHITECTURE_EVIDENCE = EMERGING_STRONGLY`
  - `M2_SINGLE_STATE_CORE = FROZEN_WITH_SCOPE_LIMITS`
  - `SPECIFICATION = M2_SINGLE_STATE_SPEC.md`
  - `SECTION_131_HARD_STOP = ENFORCED`

---

## 2. Frozen M1 Reference Baseline
The baseline learner deployed in M2 is the frozen Track B causal learner established across EXP-0001 through EXP-0010 and certified in M1-R1:
- **Optimizer**: Sparse Normalized Least Mean Squares (NLMS) with structural slack ($K_{\max} = \max(4, 2M)$).
- **Candidate Filtering**: Explore/Confirm two-phase screening with Forced Coverage.
- **Rate Allocation**: Queue-based multi-rate scheduling with tier decay.
- **Support Maintenance**: Age-normalized victim scoring (eliminating post-promotion churn).
- **Probing Budget**: Fixed, error-adaptive probe bank with strictly bounded compute.

---

## 3. Core M2 Temporal Architecture

### 3.1 Bounded Representational Memory
Rather than using large recurrent neural networks, temporal history is retained in a minimal, explicit ring buffer or a 1D scalar recurrent state:
- **Explicit Component**: [`TemporalRingBuffer`](file:///d:/Projetos/Codinome%20Lebre/src/utils/temporal_buffer.py) ($D \times (L_{\max} + 1) \times 8$ bytes).
- **Minimal Learned State Component**: [`LinearScalarState`](file:///d:/Projetos/Codinome%20Lebre/src/models/minimal_state.py) ($48\text{ bytes}$, $18\text{ FLOPs}$), [`GatedScalarState`](file:///d:/Projetos/Codinome%20Lebre/src/models/minimal_state.py) ($104\text{ bytes}$, $28\text{ FLOPs}$).
- **Autonomous Lifecycle Component**: [`AdaptiveStateLifecycleManager`](file:///d:/Projetos/Codinome%20Lebre/src/models/state_lifecycle.py) controlling `DORMANT`, `PROVISIONAL`, `ACTIVE`, `MATURE`, and `EVICTED` transitions with decoupled Normalized LMS readout updates.
- **Causality Guarantee**: Zero future leakage. Read pointer strictly restricts candidates at lag $\ell$ to historical steps $\le t - \ell$. Online forward sensitivity propagates gradient credit causally forward.

---

## 4. Completed Experiments in Milestone M2

### M2-EXP-0001: Delayed Dependency Discovery
- **Outcome**: Validated that frozen M1 principles transfer directly to single-delay dependencies without neural recurrence. 99.55%–100% exact pair recovery at 8.00% compute.

### M2-EXP-0002: Multi-Delay + Temporal Aliasing Discovery
- **Outcome**: Evaluated across 780 runs on 30 fresh seeds (`[4001..4030]`).
  - **Multi-Delay Discovery**: Recovered multiple independent delays simultaneously (100% at $M=1$, 92.7% at $M=5$, 72.9% at $M=2$) at $\le 10.75\%$ Temporal Dense compute.
  - **Same-Feature Multi-Lag**: Successfully resolved multiple historical positions of the same feature ($x_{j^*, t-d_1}$ and $x_{j^*, t-d_2}$) with 0.0 median lag error and negligible redundancy ($0.05 - 0.11$).
  - **Temporal Aliasing Frontier**: 100% exact lag identification for $\rho \le 0.75$. At $\rho = 0.90$, exact lag drops to 70.0% due to adjacent lag aliasing ($d^* \pm 1$), but predictive MSE remains low ($0.1009$, capturing 90% signal energy). Classified as `ALIASING_DEGRADES_STRUCTURE_ONLY`.

### M2-EXP-0003: Hidden State Necessity Diagnostic
- **Outcome**: Evaluated across 30 fresh seeds (`[5001..5030]`) across 4 task stages:
  - Explicit lag enumeration becomes search-inefficient for long delays and fails completely for exponential tails (IIR) and finite-state memory (SET/RESET).
  - Gate Decision: `HIDDEN_STATE_NECESSITY = SUPPORTED`.

### M2-EXP-0004: Minimal Learned State Mechanism
- **Outcome**: Evaluated across 30 fresh seeds (`[6001..6030]`).
  - **Task A (Continuous Integration)**: Linear scalar recurrence ($s_t = a_t s_{t-1} + b_t x_t$) recovers true decay $\lambda$ with $r \ge 0.9999$ correlation, achieving MSE $0.0105$ (matching oracle $0.0098$), completely replacing explicit lag candidates with $86\times$ less memory and $5.8\times$ less compute.
  - **Task B (SET/RESET Persistent Memory)**: Linear recurrence fails unconditionally ($\text{MSE} \approx 0.46 - 0.48$). Gated scalar recurrence ($s_t = (1 - g_t) s_{t-1} + g_t v_t$) achieves $99.1\times$ gate selectivity ratio ($\bar{g}_{\text{SET}} = 0.3892$ vs $\bar{g}_{\text{NONE}} = 0.0039$), successfully maintaining state across long event-free horizons ($10, 50, 100$ steps) where explicit buffers fail completely ($\text{MSE} \approx 0.52$).
  - **Task C (Context Lag Routing)**: Router R4 with forward sensitivity trace achieves $97.55\%$ mode accuracy and $14\times$ lower MSE ($0.0439$) than explicit dense tracking ($0.6180$).
  - **Ablations**: Forward sensitivity trace (R4) outperforms instantaneous gradients (R3) by preventing vanishing credit across temporal intervals.

### M2-EXP-0005: Adaptive State-Structure Integration
- **Outcome**: Evaluated across 30 fresh seeds (`[7001..7030]`) on mixed-regime continuous streams. Autonomous birth, probation, and eviction proved functional, but active recall plateaued at $65.0\%$, and continuous correct type occupancy reached $0.606$. Revised to `PARTIAL_GO` following M2-EXP-0005R audit.

### M2-EXP-0005R: State Lifecycle Reconciliation & Bottleneck Diagnosis
- **Outcome**: Evaluated across 30 evaluation seeds (`[7001..7030]`) and 20 fresh confirmation seeds (`[7031..7050]`):
  - **Metric Discrepancy Resolved**: Reconciled executive summary claim ($92.5\%$) as `TYPE_EVENT_ACCURACY` and table value ($0.606$) as `TYPE_OCCUPANCY_ACCURACY` ($= \text{Active Recall } 0.650 \times P(\text{Correct} \mid \text{Active}) 0.932$).
  - **Dominant Bottleneck Isolated**: Premature eviction during quiescent state periods ($s_t = 0$) in SET/RESET accounted for $64.2\%$ of missing active coverage. Counterfactual Q4 (Oracle Eviction Only) closed **$47.67\%$ of total adaptive regret**, surging active recall to $0.878$.
  - **Capacity Verdict**: Single scalar state ($\text{STATE\_DIM}=1$) remains mathematically sufficient ($Q7 \implies \text{MSE}=0.2310$ matching oracle baseline). `MULTI_STATE_CAPACITY_JUSTIFIED = NOT_YET`.

### M2-EXP-0006: Quiescent State Utility & Eviction Diagnostic
- **Outcome**: Evaluated across 30 strictly fresh seeds (`[8001..8030]`):
  - **Causal Signal Identified**: Resolved silent-necessary (Q2) vs silent-obsolete (Q3) discrimination via **Structural Observability ($O_{\text{struct}} = w_{\text{state}}^2$)** and **Temporal $C \times O$**, achieving **ROC-AUC = 0.913** and **PR-AUC = 0.999**.
  - **Asymmetric Cost Validated**: Proved that False Eviction cost ($C_{\text{FE}} = 9.225$, 205 rebirth steps) is $9,225\times$ more punitive than False Retention ($C_{\text{FR}} = 0.001$, 34 FLOPs, 52 bytes). State deletion requires positive evidence of obsolescence ($O_{\text{obs}}$).
  - **Causal Policy C2 Deployment**: Active recall surged to **90.66%** (exceeding 90% target), premature evictions collapsed by **95.7%** (0.10 / seed vs 2.33 in C0), compute remained strictly bounded at **50.4 FLOPs/step**, and regret vs oracle was essentially eliminated to **+0.000053** ($99.86\%$ regret reduction).
  - **Capacity Confirmed**: One scalar state remains completely sufficient. `MULTI_STATE_CAPACITY_JUSTIFIED = NOT_YET`.

---

### M2-R1: Single-State Lifecycle Pareto Freeze Review
- **Outcome**: Evaluated across 70 total seeds (10 calibration, 30 validation, 30 holdout) and 6 stream families.
  - **Empirical Pareto Frontier**: Mapped the complete non-dominated trade-off curve across 12 causal policies between Premature Eviction, Stale Retention, Global MSE, and Compute.
  - **Information-Theoretic Bound Isolated**: Proved mathematically and empirically that causal detection delay (150-300 steps) creates a fundamental trade-off: distinguishing silent Poisson gaps from true state-free regimes mechanically requires 15-35% retention during 1,000-step phases, which collapses to 5.72% on 4,000-step phases.
  - **Cost Asymmetry Robustness**: Empirically confirmed $C_{\text{FE}} / C_{\text{FR}} > 300 : 1$ across all 6 stream families (up to $235,454 : 1$ under frequent switching).
  - **Freeze Decision**: Formal certification of `M2_SINGLE_STATE_CORE = FROZEN_WITH_SCOPE_LIMITS` under specification [`M2_SINGLE_STATE_SPEC.md`](file:///d:/Projetos/Codinome%20Lebre/M2_SINGLE_STATE_SPEC.md).

---

## 5. Milestone M2 Roadmap

| Experiment ID | Title | Core Focus | Status |
| :--- | :--- | :--- | :---: |
| **M2-EXP-0001** | Delayed Dependency Discovery | Single-delay identification without neural recurrence | **COMPLETE (STRONG_GO)** |
| **M2-EXP-0002** | Multi-Delay + Temporal Aliasing | Multi-delay, same-feature lags, and AR(1) aliasing | **COMPLETE (STRONG_GO)** |
| **M2-EXP-0003** | Hidden State Necessity Diagnostic | Rigorous causal proof of where explicit lags fail | **COMPLETE (STRONG_GO)** |
| **M2-EXP-0004** | Minimal Learned State Mechanism | Smallest scalar recurrence $s_t = a_t s_{t-1} + b_t x_t$ with online sensitivity | **COMPLETE (STRONG_GO)** |
| **M2-EXP-0005** | State-Structure Integration Test | Autonomous lifecycle (birth, probation, eviction) of scalar states | **COMPLETE (PARTIAL_GO)** |
| **M2-EXP-0005R**| Lifecycle Reconciliation Diagnostic | Metric semantics audit & failure decomposition | **COMPLETE (AUDIT_COMPLETE)** |
| **M2-EXP-0006** | Quiescent State Utility Diagnostic | Resolving premature eviction during quiescent states | **COMPLETE (STRONG_GO)** |
| **M2-R1**       | Single-State Pareto Freeze Review  | Adversarial milestone review & core specification freeze | **COMPLETE (FROZEN_WITH_SCOPE_LIMITS)** |

---

## 6. Current Gate: Section 131 Hard Stop Enforced
Under Section 131 of the M2-R1 specification, execution is halted immediately upon completion of the freeze review. The canonical single-state core is frozen in [`M2_SINGLE_STATE_SPEC.md`](file:///d:/Projetos/Codinome%20Lebre/M2_SINGLE_STATE_SPEC.md). No further tuning or unrequested changes are executed.

