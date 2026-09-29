# LEBRE Architecture: Architectural Decision Records (ADRs)
**Specification Version:** 0.1  
**Status:** Frozen Reference Specification with Scope Limits  
**Project:** LEBRE (*Lifecycle-governed Evidence-Based Resource Evolution*)  
**Historical Provenance:** Track B Single-State Organization  

This document formally records the fundamental architectural decisions that govern the LEBRE architecture, linking each decision to empirical evidence, operational trade-offs, and boundary conditions.

---

## ADR-001: Computational Structure is Explicitly Cost-Bearing and Resource-Governed

### Context
Classical neural networks, reservoir computing systems, and dense adaptive filters operate with fixed dense parameter topologies where every parameter, hidden state, or delay tap permanently consumes compute and memory, regardless of environmental relevance. Conversely, classical structural learning algorithms often modify topology without rigorous, causal accounting of the computational overhead introduced by exploration and retention.

### Decision
Treat every feature weight, temporal lag tap, and recurrent state as an explicit, cost-bearing `StructuralObject`. Any addition to active structure must be formally accounted for in compute (FLOPs/step) and persistent memory (bytes). A structure must continuously demonstrate predictive or structural utility to justify its active resource footprint ("paying rent").

### Evidence
- **Benchmark BENCH-01B:** Track B achieved a mean algorithmic compute of 90.44 FLOPs/step (with an observed transient peak of approximately 206 FLOPs/step during simultaneous probe and shadow candidate updates) and 440.0 bytes of persistent model RAM, complying with the mean R2-FLOP threshold ($\le 100$ FLOPs/step) while operating below heavy dense baselines (Minimal GRU: 281.8 FLOPs; Online ESN: 1,683.7 FLOPs).
- **Ablation M1-R1 & M2-R1:** Unbounded structural growth led to compute exhaustion, whereas resource-governed allocation maintained near-oracle accuracy.

### Consequences
- **Positive:** Enables predictable mean execution bounds, making the architecture a strong candidate for future constrained embedded deployment based on low measured algorithmic compute and persistent state footprint (hardware deployment has not yet been validated).
- **Negative:** Highly complex environments requiring hundreds of simultaneous latent dimensions cannot be represented under strict single-state micro-budgets.

### Status
**CORE_INVARIANT (Frozen)**

---

## ADR-002: Candidate Structures Undergo Non-Interfering Shadow Probation

### Context
When constructive networks (such as Cascade-Correlation) or dynamic pruning algorithms introduce new structural units directly into the active predictive path, the untrained parameters inject severe transient shocks, causing sharp spikes in predictive error.

### Decision
New structural candidates must be initialized in a `PROVISIONAL` lifecycle state (shadow mode). During the canonical probation window ($T_{\text{prob}} = 50$ steps; historical development explored 20 to 80 steps), the candidate updates its internal parameters and computes counterfactual predictions in parallel, but remains strictly disconnected from the live output prediction $\hat{y}_t$. Promotion to `ACTIVE` occurs only after demonstrating statistically significant predictive gain ($> 5\%$ relative MSE improvement, $\theta_{\text{promote}} = 0.05$) over the linear baseline.

### Evidence
- **Experiment EXP-0004 & EXP-0005:** Direct insertion caused transient error surges exceeding $3.5\times$ baseline error. Shadow probation prevented transient promotion shock, achieving monotonic convergence.
- **BENCH-01B Divergence Rate:** Track B exhibited zero observed numerical divergences across 450 evaluated runs (450/450 completed runs) across all 15 continuous workloads, whereas unbuffered constructive baselines experienced frequent instability.

### Consequences
- **Positive:** Zero candidate shock to live predictions; live stream is completely isolated from experimental instability.
- **Negative:** Introduces a non-zero structural activation latency equal to the probation window ($T_{\text{prob}}$ steps).

### Status
**CORE_INVARIANT (Frozen)**

---

## ADR-003: Quiescent Silence Does Not Constitute Structural Obsolescence

### Context
In streaming environments with non-Poisson or sparse bursty dynamics (e.g., alarm triggers, bistable latches, event sensors), an internal recurrent state may remain dormant or silent for extended intervals. Naive L1 pruning, weight decay, or instantaneous utility metrics quickly evict such silent states, destroying stored state memory right before the next critical event occurs.

### Decision
Decouple fast instantaneous activity from slow structural relevance via a two-timescale metric ($U_{\text{ret}}$ with $\alpha_{\text{slow}} = 0.005$, $\tau_{\text{ret}} \approx 140$ steps). Temporary inactivity alone is explicitly rejected as grounds for structural eviction.

### Evidence
- **Task A5 (Bistable Latch) & Task A7 (Quiescent Memory):** In streams featuring 200+ steps of silence between set/reset pulses, naive LMS-style pruning suffered $100\%$ state extinction and memory loss. The two-timescale relevance metric preserved recurrent latch memory across Poisson gaps with $P(\text{retention}) > 99.0\%$.
- **BENCH-01B Task B3 (Gas Dynamic Sensor Array):** Sensor recovery phases exhibiting long flat quiescence were tracked with $\text{NMSE} = 0.00203$, outperforming Minimal GRU ($0.0241$) and ESN ($0.2608$).

### Consequences
- **Positive:** Enables robust continual learning in event-driven streaming without catastrophic forgetting of quiescent state.
- **Negative:** Stale parameters are retained longer when an environment undergoes a genuine permanent shift (eviction latency $\approx 250 - 350$ steps).

### Status
**CORE_INVARIANT (Frozen)**

---

## ADR-004: Asymmetric Evidence Thresholds for Structural Eviction

### Context
In continuous online learning, the operational cost of a **false eviction** (destroying an active recurrent state that is still structurally necessary, requiring costly re-discovery, re-instantiation, and re-training) is orders of magnitude higher than the cost of a **stale retention** (temporarily carrying an inactive scalar state that consumes a modest ~12 bytes of RAM and ~15 FLOPs).

### Decision
Eviction requires positive evidence of obsolescence ($O_{\text{obs}} > \theta_{\text{obs}}$ AND $U_{\text{ret}} < \theta_{\text{ret}}$ held over a sustained hysteresis patience window of 30–40 steps). Empirical analysis found false-eviction cost to exceed stale-retention cost by more than 300× under evaluated conditions, motivating a conservative asymmetric eviction policy. The policy is realized through the hysteresis patience counter and dual gating rather than a hardcoded 300:1 mathematical multiplier in the code.

### Evidence
- **Ablation M2-EXP-0005 & M2-R1:** Symmetrical eviction policies caused catastrophic cyclic churning (rapid birth $\to$ premature eviction $\to$ immediate rebirth), consuming $4\times$ compute and degrading prediction. Asymmetric hysteresis stabilized the lifecycle.
- **BENCH-01B Task A8 (Regime Switching):** Transition from Recurrent (Regime 3) to Linear (Regime 4) was executed with $< 10\%$ total stale-retention overhead over a 2,000-step phase.

### Consequences
- **Positive:** Prevented cyclic churn in evaluated benchmarks; ensures stable online state transitions.
- **Negative:** When a regime permanently loses recurrent dependencies, resources are reclaimed with a slight delay ($250 - 350$ steps).

### Status
**CURRENT_EMPIRICALLY_SELECTED_POLICY (Frozen in v0.1)**

---

## ADR-005: Parsimonious Linear-First Representation Escalation

### Context
Online learning systems often over-parameterize by deploying complex recurrent or non-linear units to solve simple linear or low-order delay tasks, inflating computational load and risking gradient instability.

### Decision
Enforce a strict hierarchical escalation of representation:
1. First, satisfy predictive demand using a sparse feedforward linear predictor.
2. If residual error persists, evaluate explicit temporal lag candidates.
3. If temporal residual error remains unresolved, provision a minimal linear recurrent scalar state ($h_t = \lambda h_{t-1} + u_t$).
4. Only if linear recurrence fails probation may a gated scalar state ($h_t = (1-g_t)h_{t-1} + g_t c_t$) be provisionally instantiated.

### Evidence
- **Task A1 (Sparse Linear Shift):** Handled purely at ~38 FLOPs/step without triggering spurious recurrence.
- **Task A8 (Graduated Escalation):** Dynamically scaled compute from 40 FLOPs (Regime 1) to 65 FLOPs (Regime 2) to 92 FLOPs (Regime 3), then dropped back to 40 FLOPs (Regime 4).
- **Stability:** Zero numerical divergences were observed across 450 evaluated runs, whereas full gated models (Minimal GRU, Continual Backprop) suffered numerical instability.

### Consequences
- **Positive:** Minimizes energy, compute, and memory consumption; achieves maximum parsimony.
- **Negative:** Environments requiring complex nonlinear state dynamics from step $t=1$ incur an initial exploration latency while linear models are tested first.

### Status
**CORE_INVARIANT (Frozen)**

---

## ADR-006: Current v0.1 Recurrent State Capacity is Constrained to Scalar Recurrence ($N \le 1$)

### Context
Empirical validation of Milestone M1 and M2 was conducted with a single scalar recurrent state ($N=1$, dimension $= 1$). Generalizing to $N > 1$ simultaneous recurrent states introduces non-trivial coupling, inter-state orthogonalization, and cubic sensitivity scaling ($\mathcal{O}(N^3)$ or $\mathcal{O}(N^2)$).

### Decision
The LEBRE v0.1 specification formally documents and bounds recurrent capacity to at most one active recurrent scalar state ($N \le 1$) and one provisional candidate ($N_{\text{prov}} \le 1$). Milestone M3 (multi-state generalization) remains explicitly **UNOPENED**.

### Evidence
- **M2-SINGLE-STATE-SPEC Documentation:** The single scalar core is fully verified, closed, and reproducible across 124 unit tests and 6,750 benchmark runs.
- **CAR-01 Review:** Multi-state claims without empirical certification violate scientific integrity; v0.1 must be bounded to its validated envelope.

### Consequences
- **Positive:** Eliminates RTRL computational explosion; keeps forward sensitivity tracking strictly $\mathcal{O}(1)$ FLOPs.
- **Negative:** Tasks requiring high-order delay lines (Tasks A2–A4) or complex multi-frequency dynamical systems (Task B4 Silverbox) encounter representational bottlenecks.

### Status
**CURRENT_SINGLE_STATE_POLICY (Scope Limit for v0.1; Future Work M3 Unopened)**
