# PRA-01: Deep Technical Profiles of the Top 10 Closest Prior Art Papers

**Audit ID:** PRA-01  
**Auditor:** Adversarial Literature Reviewer & Novelty Analyst  
**Date:** September 19, 2026  

---

## 1. MUSE-RNN (Das, Pratama, Savitri, & Zhang, 2019)

- **Title**: *MUSE-RNN: A Multilayer Self-Evolving Recurrent Neural Network for Data Stream Classification*
- **Authors**: Monidipa Das, Mahardhika Pratama, Septiviana Savitri, Jie Zhang
- **Year**: 2019
- **Venue / Status**: IEEE International Conference on Data Mining (ICDM 2019), Peer-Reviewed Conference Paper
- **URL / DOI**: [https://doi.org/10.1109/ICDM.2019.00021](https://doi.org/10.1109/ICDM.2019.00021)
- **Core Method**: An evolving recurrent neural network that automatically grows and prunes hidden recurrent nodes and hidden layers in real-time streaming data using statistical error bounds.
- **Task Setting**: Online continuous data stream classification under non-stationary environments (concept drift).
- **Training Regime**: Online single-pass streaming with a teacher-forcing recurrent policy across a small window; updates occur sequentially per incoming sample.
- **Structural Plasticity Mechanism**:
  - *Growth*: Driven by the **Network Significance (NS)** metric derived from a bias-variance decomposition of model prediction error. When bias exceeds a statistical threshold, a new recurrent hidden node is instantiated.
  - *Pruning*: When a hidden node's variance or statistical contribution to network output drops below a threshold, the node and its recurrent weights are pruned.
  - *Depth Evolution*: Drift detection scenario (DDS) adds layers; Maximum Information Compression Index (MICI) prunes redundant layers.
- **Memory / State Mechanism**: Standard multi-unit recurrent hidden layers ($h_t = \tanh(W_x x_t + W_h h_{t-1} + b)$).
- **Resource Mechanism**: Structural pruning keeps network size bounded in memory; runs within an empirical time window per sample.
- **Similarities to Track B**:
  - Single-pass online streaming with zero offline replay buffers and no task labels.
  - Dynamically creates and destroys recurrent hidden units online based on prediction error.
  - True physical resource reclamation (pruned nodes are deleted to save memory and compute).
- **Differences from Track B**:
  - *No Sparse Input / Lag Discovery*: Observes all $D$ features every step; does not discover sparse feature-lag pairs or maintain an active probe bank.
  - *No Probation Window*: New nodes immediately influence live predictions upon birth; lacks a shadow probation window to evaluate parameter viability before promotion.
  - *No State Type Selection*: Recurrent nodes are fixed standard tanh units; cannot parsimoniously select cheaper linear state vs selective gated state.
  - *No Quiescent Protection*: Pruning depends on continuous activity/variance. During quiescent intervals ($s_t = 0$), nodes face premature pruning unless protected by ad-hoc thresholds. Lacks structural observability ($O_{\text{struct}}$) and positive obsolescence confirmation ($O_{\text{obs}}$).
  - *Credit Assignment*: Uses teacher forcing / short window approximations rather than exact $O(1)$ forward sensitivity traces.
- **Novelty Threat Level**: **HIGH**. This is the closest published prior method in the literature combining online streaming, recurrent state creation, and recurrent state pruning.

---

## 2. SkipE-RNN (Das, Pratama, Zhang, & Ong, 2020)

- **Title**: *A Skip-Connected Evolving Recurrent Neural Network for Data Stream Classification under Label Latency Scenario*
- **Authors**: Monidipa Das, Mahardhika Pratama, Jie Zhang, Yew Soon Ong
- **Year**: 2020
- **Venue / Status**: Proceedings of the AAAI Conference on Artificial Intelligence (AAAI-20), Peer-Reviewed Conference Paper
- **URL / DOI**: [https://doi.org/10.1609/aaai.v34i04.5781](https://doi.org/10.1609/aaai.v34i04.5781)
- **Core Method**: Self-evolving recurrent neural network capable of dynamically evolving skip-connections across historical time lags to bridge delayed labels in streaming data.
- **Task Setting**: Streaming data classification where ground-truth labels arrive with variable temporal delay (label latency).
- **Training Regime**: Online streaming with auto-learned pseudo-label mapping and retrospective parameter regularization when true labels arrive.
- **Structural Plasticity Mechanism**: Autonomously adds and prunes hidden nodes while simultaneously creating and pruning skip-recurrent connections between non-adjacent time steps.
- **Memory / State Mechanism**: Recurrent hidden layers augmented with dynamic skip-lags.
- **Resource Mechanism**: Parsimonious network growth/pruning bounds memory footprint.
- **Similarities to Track B**:
  - Dynamically learns temporal lag structures (skip connections) in an online stream.
  - Integrates structural plasticity with temporal memory.
- **Differences from Track B**:
  - *Purpose of Lags*: Skip connections in SkipE-RNN are designed to route *delayed label feedback* rather than discovering sparse feature-lag interactions ($x_{j, t-d}$).
  - *No Explicit Compute Budgeting*: Does not enforce a strict sub-linear probe budget ($Q \ll D$).
  - *No Parsimonious State Lifecycle*: Lacks Track B's linear-first probation hierarchy, forward sensitivity traces, and obsolescence accumulation.
- **Novelty Threat Level**: **HIGH**. Directly explores dynamic temporal lag creation and recurrent node plasticity online.

---

## 3. Minimal Resource Allocation Network — MRAN (Kadirkamanathan & Niranjan 1993; Sundararajan et al. 1999)

- **Title**: *A Function Estimation Approach to Sequential Learning with Neural Networks* / *Minimal Resource Allocation Network for Function Approximation*
- **Authors**: Visakan Kadirkamanathan & Mahesan Niranjan (1993); N. Sundararajan, S. Lu, & P. Saratchandran (1999)
- **Year**: 1993 / 1999
- **Venue / Status**: Neural Computation (1993); IEEE Transactions on Neural Networks (1999), Peer-Reviewed Journal Papers
- **URL / DOI**: [https://doi.org/10.1162/neco.1993.5.6.954](https://doi.org/10.1162/neco.1993.5.6.954)
- **Core Method**: Sequential learning algorithm for Radial Basis Function (RBF) networks that dynamically allocates new hidden units when prediction error and input novelty are high, and prunes units whose normalized output contribution over a sliding window falls below a threshold.
- **Task Setting**: Online sequential regression, time-series forecasting, and adaptive filtering.
- **Training Regime**: Strictly online, single-pass sequential learning; updates hidden center parameters and output weights via an Extended Kalman Filter (EKF).
- **Structural Plasticity Mechanism**:
  - *Birth Criterion*: Allocates a new unit if: 1) $|e_t| > \epsilon_1$; 2) $\|x_t - c_{\text{nearest}}\| > \epsilon_2$; and 3) root-mean-square error over a sliding window $> \epsilon_3$.
  - *Pruning Criterion*: Removes unit $k$ if its normalized output contribution $o_k / \sum_j o_j < \delta$ for $M$ consecutive observations.
- **Memory / State Mechanism**: **Zero recurrent state**. Operates strictly on spatial RBF kernels $e^{-\|x - c\|^2 / 2\sigma^2}$ over static input vectors.
- **Resource Mechanism**: Bounded network capacity through continuous active pruning.
- **Similarities to Track B**:
  - Establishes the foundational sequential lifecycle: *Error-triggered birth $\to$ parameter adaptation $\to$ contribution-based eviction*.
  - Strictly online, single-pass, no task labels, no replay buffers.
- **Differences from Track B**:
  - *Purely Spatial / Feedforward*: MRAN adds and removes local basis functions in $\mathbb{R}^D$; it has no concept of recurrence, temporal state $h_t$, decay $\lambda$, or gating $g_t$.
  - *No Temporal Lag Discovery*: Cannot discover sparse feature-lag dependencies.
  - *Compute Cost*: Uses an Extended Kalman Filter ($O(N^2)$ in unit parameters), which is substantially more expensive than Track B's Normalized LMS ($O(N)$).
- **Novelty Threat Level**: **HIGH**. Foundational ancestor for the "error-triggered birth + sliding-window eviction" structural lifecycle.

---

## 4. AIRE-Prune (Padhy, Camacho, & Mukhopadhyay, 2026)

- **Title**: *Asymptotic Impulse-Response Energy for State Pruning (AIRE-Prune)*
- **Authors**: Apurba Prasad Padhy, Fernando F. Camacho, Saibal Mukhopadhyay
- **Year**: 2026
- **Venue / Status**: International Conference on Learning Representations (ICLR 2026), Peer-Reviewed Conference Paper
- **URL / DOI**: OpenReview / arXiv
- **Core Method**: Structured state pruning for State Space Models (SSMs) by assigning an analytical score to each recurrent state based on its **Asymptotic Impulse-Response Energy**—the total energy the state transmits to the output over an infinite horizon.
- **Task Setting**: Model compression of pre-trained deep state space models (e.g., S4, Mamba) on language and audio benchmarks.
- **Training Regime**: **Post-training offline compression**. Evaluates closed-form system-theoretic metrics on pre-trained weights without fine-tuning.
- **Structural Plasticity Mechanism**: One-shot offline contraction of state dimension. Cannot grow or restore states.
- **Memory / State Mechanism**: Continuous-time and discretized state space model equations ($h_t = \bar{A} h_{t-1} + \bar{B} x_t, y_t = \bar{C} h_t$).
- **Resource Mechanism**: Reduces runtime memory footprint and FLOPs of pre-trained SSMs.
- **Similarities to Track B**:
  - Focuses explicitly on the **controllability/observability energy of recurrent states** to determine whether a state is obsolete or essential.
  - Mathematical core directly parallels Track B's structural observability metric ($O_{\text{struct}} = w_s^2 (|h| + \sigma_h)$).
- **Differences from Track B**:
  - *Offline vs Online*: AIRE-Prune is a post-training compression tool. Track B is an online, streaming learner that creates, learns, retains, and evicts states dynamically.
  - *No Online State Birth*: Cannot discover when a state is needed from an error stream.
  - *No Active Compute Budgeting*: Does not discover input features or lags.
- **Novelty Threat Level**: **MEDIUM**. Threatens the novelty of the mathematical state-utility principle (proving that evaluating recurrent states by long-horizon output influence is established in SSM literature), but does NOT implement an online adaptive lifecycle.

---

## 5. LAST — Layer-Adaptive State Pruning (Padhy et al., 2025)

- **Title**: *LAST: Layer-Adaptive STate pruning for Deep State Space Models*
- **Authors**: Apurba Prasad Padhy, et al.
- **Year**: 2025
- **Venue / Status**: International Conference on Learning Representations (ICLR 2025), Peer-Reviewed Conference Paper
- **URL / DOI**: [https://doi.org/10.48550/arXiv.2410.04505](https://doi.org/10.48550/arXiv.2410.04505)
- **Core Method**: System-theoretic model reduction for deep SSMs using $\mathcal{H}_\infty$ subsystem norms and modal truncation to score and prune states layer-adaptively under a fixed compute budget.
- **Task Setting**: Structured pruning of deep sequence models (MIMO SSMs).
- **Training Regime**: Post-training offline reduction; zero retraining.
- **Structural Plasticity Mechanism**: Modal truncation; static pruning of pre-trained state dimensions.
- **Memory / State Mechanism**: SSM state vectors across deep layers.
- **Resource Mechanism**: Pruning state dimensions to fit target hardware FLOP/memory budgets.
- **Similarities to Track B**:
  - Uses control-theoretic system norms to identify and discard unobservable/uncontrollable recurrent states.
- **Differences from Track B**:
  - Strictly offline post-training; no online birth, probation, or single-pass learning.
- **Novelty Threat Level**: **MEDIUM**. Further confirms control-theoretic state pruning precedent in SSMs.

---

## 6. Elastic Neural Networks (Kong & Sutton, 2026)

- **Title**: *Plasticity of Growing and Elastic Neural Networks in Online Continual Learning*
- **Authors**: Jeong Min Kong & Richard S. Sutton
- **Year**: 2026 (August)
- **Venue / Status**: arXiv preprint arXiv:2608.01475
- **URL / DOI**: [https://doi.org/10.48550/arXiv.2608.01475](https://doi.org/10.48550/arXiv.2608.01475)
- **Core Method**: Investigates the loss of plasticity in online continual learning. Proposes "Elastic Neural Networks" that incrementally introduce randomly initialized units and prune estimated "dead" hidden units at the beginning of each task to maintain a compact, near-constant size.
- **Task Setting**: Online continual learning across shifting tasks without catastrophic loss of plasticity.
- **Training Regime**: Online stream of tasks; standard gradient descent on active weights.
- **Structural Plasticity Mechanism**:
  - *Growth*: Randomly adds new hidden units at regular intervals.
  - *Pruning*: Identifies dead units (low activation/gradient) and prunes them at task boundaries.
- **Memory / State Mechanism**: Feedforward hidden units; no recurrence or temporal states.
- **Resource Mechanism**: Bounded network capacity by matching growth rate to dead-unit pruning rate.
- **Similarities to Track B**:
  - Emphasizes maintaining a bounded, compact model capacity in continuous online learning.
  - Reclaims compute and memory by eliminating obsolete units.
- **Differences from Track B**:
  - *Requires Task Boundaries*: Pruning is tied to task transitions; Track B operates in continuous streams with zero task labels or boundary signals.
  - *No Temporal Recurrence*: Does not manage recurrent memory states, feature lags, or forward sensitivity.
  - *Heuristic Growth*: Adds random units blindly, whereas Track B uses residual error correlation to trigger targeted hypothesis creation.
- **Novelty Threat Level**: **MEDIUM**. Closely aligned in philosophy (continual plasticity via bounded growth/pruning), but restricted to feedforward networks with task boundaries.

---

## 7. SMGrNN (Jia & Zhou, 2025/2026)

- **Title**: *Self-Motivated Growing Neural Network for Adaptive Architecture via Local Structural Plasticity*
- **Authors**: Yiyang Jia & Chengxu Zhou
- **Year**: 2025 (arXiv) / 2026 (Neurocomputing)
- **Venue / Status**: Neurocomputing / arXiv:2512.18342, Peer-Reviewed Journal Paper
- **URL / DOI**: [https://doi.org/10.1016/j.neucom.2026.01.045](https://doi.org/10.1016/j.neucom.2026.01.045)
- **Core Method**: An online growing MLP architecture for reinforcement learning that monitors local synaptic weight updates over short temporal windows to autonomously add and prune neurons.
- **Task Setting**: Online continuous control and reinforcement learning.
- **Training Regime**: Streaming policy/value function estimation using local gradient statistics.
- **Structural Plasticity Mechanism**: Local Structural Plasticity Module (SPM) tracks edge-level gradient variance to trigger neuron insertion or deletion without global coordination.
- **Memory / State Mechanism**: Feedforward MLP; no recurrent memory.
- **Resource Mechanism**: Compact task-appropriate network growth.
- **Similarities to Track B**:
  - Local evidence-based online unit birth and death without human intervention.
- **Differences from Track B**:
  - Operates on static feedforward connections; zero temporal state, zero lag discovery, zero sensitivity credit assignment.
- **Novelty Threat Level**: **MEDIUM**.

---

## 8. Stability of Growth in Structural Plasticity (Lillo & Cheney, 2026)

- **Title**: *On the Stability of Growth in Structural Plasticity*
- **Authors**: Lute Lillo & Nick Cheney
- **Year**: 2026 (May)
- **Venue / Status**: arXiv preprint arXiv:2605.15435
- **URL / DOI**: [https://doi.org/10.48550/arXiv.2605.15435](https://doi.org/10.48550/arXiv.2605.15435)
- **Core Method**: Rigorous empirical and theoretical study of why structural growth fails to match pruning stability in deep networks. Identifies the "Newborn Bottleneck": newly born units are forward-active but receive weak gradient credit compared to specialized incumbent units.
- **Task Setting**: Continual learning and image classification under distribution shift.
- **Training Regime**: Deep neural network training via mini-batch SGD.
- **Structural Plasticity Mechanism**: Evaluates various unit addition and integration rules.
- **Similarities to Track B**:
  - Directly investigates the exact failure mode Track B solved via its **20-step Probation Period** (where candidate states train parameters in shadow before participating in primary predictions).
- **Differences from Track B**:
  - Diagnostic study on deep vision models; does not propose an online temporal state lifecycle.
- **Novelty Threat Level**: **LOW** (threat to claim); **HIGH** (confirmatory prior art validating Track B's probation mechanism).

---

## 9. Real-Time Recurrent Learning — RTRL (Williams & Zipser, 1989)

- **Title**: *A Learning Algorithm for Continually Running Fully Recurrent Neural Networks*
- **Authors**: Ronald J. Williams & David Zipser
- **Year**: 1989
- **Venue / Status**: Neural Computation, 1(2), 270–280, Foundational Peer-Reviewed Paper
- **URL / DOI**: [https://doi.org/10.1162/neco.1989.1.2.270](https://doi.org/10.1162/neco.1989.1.2.270)
- **Core Method**: The foundational algorithm for calculating exact online gradients for recurrent neural networks without unrolling in time (no BPTT). Maintains a forward sensitivity tensor $\frac{\partial h_t}{\partial \theta}$ propagated forward in real time.
- **Task Setting**: Continual sequence learning, temporal pattern generation.
- **Training Regime**: Strictly online, streaming, single-pass; updates parameters every time step.
- **Structural Plasticity Mechanism**: **None**. Topology is completely fixed.
- **Memory / State Mechanism**: Fully connected recurrent hidden states.
- **Similarities to Track B**:
  - **Identical Credit Assignment**: Track B's forward sensitivity trace ($S_t = \lambda S_{t-1} + u_{t-1}$) is the exact algebraic specialization of Williams & Zipser's forward sensitivity equation for a 1D scalar state ($N=1$).
- **Differences from Track B**:
  - RTRL has no structural lifecycle, no state birth, no probation, no eviction, and no sparse feature probing.
- **Novelty Threat Level**: **CRITICAL for Credit Assignment**. Proves conclusively that Track B's forward sensitivity credit assignment has zero algorithmic novelty.

---

## 10. Sparse LMS / Reweighted Zero-Attracting LMS (Chen et al., 2009; Gu et al., 2009)

- **Title**: *Sparse LMS for System Identification with Zero-Attracting Sign Algorithm* / *$\ell_0$ Norm Constraint LMS for Sparse System Identification*
- **Authors**: Yuantao Chen, Yuantao Gu, & Alfred O. Hero (2009); Yuantao Gu, Jian Jin, & Shenghua Mei (2009)
- **Year**: 2009
- **Venue / Status**: IEEE Transactions on Signal Processing / IEEE Signal Processing Letters, Peer-Reviewed Papers
- **URL / DOI**: [https://doi.org/10.1109/TSP.2009.2028112](https://doi.org/10.1109/TSP.2009.2028112)
- **Core Method**: Incorporates $\ell_1$ and log-penalty zero-attraction terms into standard LMS updates ($\Delta w = \mu e_t x_t - \rho \operatorname{sgn}(w_t)$) to accelerate convergence in sparse system identification.
- **Task Setting**: Online sparse system identification and channel estimation.
- **Training Regime**: Streaming online adaptive filtering.
- **Structural Plasticity Mechanism**: Continuous shrinkage pulls inactive weights to zero, creating effective support sparsity.
- **Resource Mechanism**: Mathematical sparsity in weights; however, compute remains $O(D)$ because all features must be computed every step.
- **Similarities to Track B**:
  - Online continuous sparse regression without batch optimization.
- **Differences from Track B**:
  - *No Probing / Active Budgeting*: Observes all $D$ features every step ($O(D)$ FLOPs). Track B restricts observations to $K_{\max} + Q \ll D$.
  - *No Temporal Recurrence*: Only models static FIR linear coefficients.
- **Novelty Threat Level**: **HIGH for basic sparse LMS**; establishes that online sparse parameter recovery is well-known.
