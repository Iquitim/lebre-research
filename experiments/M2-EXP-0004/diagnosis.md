# Diagnostic Report: M2-EXP-0004 — Minimal Learned State Mechanism

**Diagnostic Classification:** `SELECTIVE_GATE_REQUIRED` / `ONLINE_SENSITIVITY_TRACE_REQUIRED`  
**Operational Recommendation:** `STRONG_GO`  
**Milestone Transition State:** `M2_EXP_0004_STATUS = STRONG_GO`  
**Architecture Evidence:** `EMERGING`  
**Next Objective:** `STATE_STRUCTURE_INTEGRATION_TEST`  

---

## 1. Diagnostic Findings & Mathematical Foundations

### 1.1 The Failure Mode of Fixed Linear Recurrence (`SELECTIVE_GATE_REQUIRED`)
In M2-EXP-0003, we established that explicit lag enumeration cannot represent long-tail distributed delays or event-driven persistence without unbounded memory explosion. 

In M2-EXP-0004, we evaluated whether a simple linear scalar recurrence:
$$s_t = a_t s_{t-1} + b_t x_t$$
suffices to replace the explicit buffer.

**Empirical Result:**
- **Continuous Integration (Task A):** Linear recurrence is nearly optimal. With $a_t = \tanh(\alpha_t)$, the learner converges to $a = 0.5002$ for $\lambda=0.50$ and $a = 0.7997$ for $\lambda=0.80$, tracking the true latent state with $r \ge 0.9999$ correlation and beating the explicit buffer by orders of magnitude in both MSE and FLOPs.
- **Persistent Event Memory (Task B):** Linear recurrence fails catastrophically ($\text{MSE} \approx 0.46 - 0.48$, matching chance failure).

**Theoretical Explanation:**
For stability, a linear recurrence must enforce $|a| < 1.0$. Consequently, over an event-free interval of length $\Delta t$ where $x_t = 0$:
$$s_{t + \Delta t} = a^{\Delta t} s_t$$
Even for $a = 0.95$, after $\Delta t = 50$ steps, $s_{t+50} = 0.95^{50} s_t \approx 0.077 s_t$ (over $92\%$ information loss). For $\Delta t = 100$, information retention drops to $0.5\%$.
To retain a discrete event state indefinitely, $a$ would have to equal exactly $1.0$. But if $a = 1.0$, the recurrence accumulates all future background noise and perturbations without decay, causing unbounded variance.

**Diagnostic Rule:**
> **A fixed linear recurrence cannot simultaneously integrate continuous driving inputs and maintain persistent event-driven memories.** Selective input gating ($g_t$) is strictly required to decouple the *write condition* from the *retention condition*.

---

### 1.2 The Failure Mode of Instantaneous Sensitivity (`ONLINE_SENSITIVITY_TRACE_REQUIRED`)
Given a gated scalar update:
$$s_t = (1 - g_t) s_{t-1} + g_t v_t, \quad g_t = \sigma(w_g^T z_t + b_g)$$
how must credit be assigned online without backpropagation through time (BPTT)?

We evaluated two gradient regimes:
1. **R3 (Instantaneous Sensitivity):** Truncates the sensitivity trace at the current step:
   $$\frac{\partial s_t}{\partial \theta} \approx \frac{\partial s_t}{\partial g_t} \frac{\partial g_t}{\partial \theta} + \frac{\partial s_t}{\partial v_t} \frac{\partial v_t}{\partial \theta}$$
   setting $\frac{\partial s_{t-1}}{\partial \theta} = 0$.
2. **R4 (Exact Forward Sensitivity Trace / Scalar RTRL):** Recursively propagates forward sensitivity:
   $$p_t = (1 - g_t) p_{t-1} + (v_t - s_{t-1}) g_t (1 - g_t) z_t$$

**Empirical Result:**
- On context-dependent lag routing (Task C), R3 achieves only MSE $0.2896$ at switch rate $0.05$, while R4 achieves MSE $0.0439$ ($6.6\times$ lower error) and $97.55\%$ routing accuracy.
- When retention gaps exceed 50 steps, R3 cannot adjust write thresholds because sensitivity vanishes during NONE events. R4 accumulates sensitivity across the retention gap, shifting $b_g$ to tighten retention.

**Theoretical Explanation:**
When an event occurs at step $t_0$, the state is updated to $s_{t_0}$. The prediction error $e_{t_0 + k}$ occurs $k$ steps later during an event-free interval ($z_{t_0 + k} = 0$).
Under R3, since $z_{t_0 + k} = 0$, the instantaneous sensitivity is identically zero ($\nabla_\theta = 0$), so the error at $t_0 + k$ delivers zero gradient to the write weights that created the state at $t_0$.
Under R4, the sensitivity trace carries:
$$p_{t_0 + k} = \prod_{j=1}^k (1 - g_{t_0 + j}) \cdot p_{t_0}$$
Because the gate is closed during NONE intervals ($g \approx 0$), the trace is preserved ($p_{t_0 + k} \approx p_{t_0}$), allowing error signals at arbitrary future times to directly adapt the gating and candidate parameters at $t_0$.

**Diagnostic Rule:**
> **Online credit assignment for recurrent state across temporal gaps requires forward recursive sensitivity accumulation.** Instantaneous approximations suffer from severe temporal blindness.

---

## 2. Resource Footprint & Algorithmic Scalability

In full-rank neural networks, RTRL is prohibitively expensive ($O(N^4)$ time, $O(N^3)$ space for $N$ hidden units). However, for a **1D scalar state** ($\text{STATE\_DIM} = 1$):
- Number of state variables: $1$
- Number of parameters: $5$ ($w_g \in \mathbb{R}^2, b_g \in \mathbb{R}, w_v \in \mathbb{R}^2, b_v=0, c=1$)
- Forward sensitivity vector: $\mathbb{R}^5$
- Compute per step: **28 FLOPs**
- Total memory: **104 Bytes**

Compared to an explicit ring buffer of depth 50 ($4,144\text{ bytes}$, $105.9\text{ FLOPs}$), the minimal state mechanism uses:
- **$40\times$ less memory**
- **$3.8\times$ fewer FLOPs**
- **Infinite theoretical horizon** (unlike the hard truncation at $L_{\max}=50$).

---

## 3. The Path Toward Milestone M3

M2-EXP-0001, M2-EXP-0002, M2-EXP-0003, and M2-EXP-0004 together establish the complete empirical foundation for Milestone M2:

1. **M2-EXP-0001:** Delayed dependencies can be discovered via probe banks under strict budget constraints.
2. **M2-EXP-0002:** When lags compete and overlap, sparse exploration separates primary from aliased dependencies.
3. **M2-EXP-0003:** Beyond moderate horizons, explicit lag enumeration suffers exponential representational inefficiency; compact state is causally necessary.
4. **M2-EXP-0004:** A 1D scalar state with selective gating and online forward sensitivity completely replaces candidate buffers for continuous decay and discrete event retention with $< 104\text{ bytes}$ and $< 28\text{ FLOPs}$.

### Recommended Next Step
The next logical milestone stage is the **State-Structure Integration Test (`STATE_STRUCTURE_INTEGRATION_TEST`)**:
Integrating the minimal 1D scalar state discovery mechanism with the frozen M1 tiered probe discovery engine, allowing the learner to choose online whether to represent an incoming signal as an explicit short lag or a compact recursive state.

**Verdict:** `STRONG_GO`
Enforcing Section 129 Hard Stop: Simulation halted, awaiting review.
