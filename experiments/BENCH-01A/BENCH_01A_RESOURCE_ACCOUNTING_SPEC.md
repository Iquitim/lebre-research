# BENCH-01A: Standardized Resource Accounting Specification (FLOPs, Memory, Runtime)

**Document ID:** BENCH-01A-RESOURCE  
**Auditor:** Systems Performance Auditor & Computational Systems Architect  
**Date:** September 19, 2026  
**Status:** ACCOUNTING SPECIFICATION LOCKED  
**Governing Standard:** Sections 114–135, 204, 205, 213 of BENCH-01A Protocol  

---

## 1. Governance Principles for Resource Measurement

Per Sections 115–118 of the protocol:
1. **Mathematical Objectivity:** High-level algorithmic claims of "computational efficiency" must be grounded in precise, deterministic operation counts rather than implementation artifacts or compiler optimizations.
2. **Dual-Perspective Accounting (Section 117):** Evaluation requires both:
   - *Perspective A (Algorithmic Operation Count):* Exact deterministic FLOP and memory counts independent of hardware;
   - *Perspective B (Empirical Wall-Clock Timing):* Standardized physical execution benchmarks on identical hardware.
3. **Symmetric Transcendental Pricing (Section 116):**  
   > *"Do not quietly count sigmoid/tanh as one FLOP while matrix multiply receives full accounting."*  
   Non-linear activations require iterative series or polynomial approximations and must be charged realistic computational costs.
4. **Architecture-Neutral Regime R2 Matching (BENCH-01A-R):**  
   Resource matching operates strictly on observable physical quantities rather than internal architectural topology. Universal ceilings are fixed at:
   - **`R2-FLOP`:** $\le 100\text{ FLOPs/step}$ (calibrated against Track B's measured peak of 72 FLOPs/step);
   - **`R2-MEM`:** $\le 1{,}024\text{ Bytes}$ (calibrated against Track B's deployment memory of $\approx 200$–$400$ Bytes).  
   Zero universal constraints on internal parameters ($K, N$, columns, nodes) are imposed on external baselines.

---

## 2. Standardized FLOP Accounting Standard (Sections 115 & 116)

Every elementary arithmetic operation executed in inference or online parameter learning is charged according to the immutable standard:

| Arithmetic Operation | Symbol / Function | Standard FLOP Cost | Technical Justification |
| :--- | :---: | :---: | :--- |
| **Addition / Subtraction** | $a + b$, $a - b$ | **1 FLOP** | Single ALU cycle. |
| **Multiplication** | $a \cdot b$ | **1 FLOP** | Single multiplier unit cycle. |
| **Multiply-Accumulate (MAC)** | $a \cdot b + c$ | **2 FLOPs** | Standard IEEE-754 fused MAC operation (1 mult + 1 add). |
| **Division** | $a / b$ | **4 FLOPs** | Iterative hardware SRT or Newton-Raphson division step. |
| **Square Root** | $\sqrt{a}$ | **4 FLOPs** | Hardware iterative square root extraction. |
| **Exponential / Logarithm** | $\exp(x)$, $\ln(x)$ | **8 FLOPs** | 7th-order polynomial / Padé approximation. |
| **Sigmoid / Hyperbolic Tangent**| $\sigma(x)$, $\tanh(x)$ | **8 FLOPs** | Exponential evaluation plus scaling and inversion. |
| **Comparison / Branch** | $a > b$, $\text{sign}(a)$ | **1 FLOP** | Comparator execution. |

---

## 3. Explicit Algorithmic FLOP Formulations by Model

### 3.1 Track B (Frozen Single-State Core)
1. **Sparse Linear Predictor (Phase 1):**  
   $\hat{y}_{\text{lin}} = \sum_{k=1}^K w_k x_{j_k, t-d_k} \implies 2K$ FLOPs.
2. **Probe Bank Screening (Phase 2):**  
   $Q$ candidate probes: Each probe computes correlation $\implies 2Q$ FLOPs.
3. **Recurrent State Execution (When Active):**  
   - *Linear State:* $s_t = \lambda s_{t-1} + u_{t-1} \implies 1\text{ mult} + 1\text{ add} = 2$ FLOPs.  
     Sensitivity trace: $S_t = \lambda S_{t-1} + u_{t-1} \implies 2$ FLOPs.  
     Prediction contribution: $w_{\text{rec}} s_t \implies 2$ FLOPs.  
     Total linear state cost = **6 FLOPs/step**.
   - *Gated State:* Gate evaluation $g_t = \sigma(w_g x_t + b_g) \implies 2 + 8 = 10$ FLOPs.  
     State update $s_t = (1-g_t) s_{t-1} + g_t \tilde{s}_t \implies 4$ FLOPs.  
     Sensitivities $\frac{\partial s_t}{\partial w_g}, \frac{\partial s_t}{\partial w_{\text{rec}}} \implies 12$ FLOPs.  
     Total gated state cost = **28 FLOPs/step**.
4. **Online Parameter Updates (Phase 5):**  
   Weight updates: $w \leftarrow w + \eta e_t x \implies 2K$ FLOPs.
- **Total Operational FLOP Envelope:**  
  $$\text{FLOPs}_{\text{Track\_B}} = \begin{cases} 4K + 2Q, & \text{if State is DORMANT/EVICTED} \\ 4K + 2Q + 6, & \text{if Linear State is ACTIVE} \\ 4K + 2Q + 28, & \text{if Gated State is ACTIVE} \end{cases}$$
  With $K \le 10, Q = 2$, compute ranges from **44 FLOPs/step** (state-free) to **72 FLOPs/step** (gated active).

### 3.2 Baseline B1: RZA-LMS
- Dense dot product: $2D$ FLOPs.
- Error calculation: $1$ FLOP.
- Weight gradient update + reweighted zero-attraction penalty: $4D$ FLOPs.
- **Total:** $\mathbf{6D + 1\text{ FLOPs/step}}$ (e.g., 301 FLOPs/step for $D=50$).

### 3.3 Baseline B2: CCN (C Columns)
- Column activations: $C \times (2D + 8)$ FLOPs.
- Scalar RTRL sensitivity traces: $C \times 6$ FLOPs.
- Linear readout prediction & LMS update: $4C$ FLOPs.
- Column parameter updates: $C \times (2D + 4)$ FLOPs.
- **Total for $C=1$:** $\mathbf{4D + 22\text{ FLOPs/step}}$ (222 FLOPs for $D=50$).

### 3.4 Baseline B3: MUSE-RNN ($N_t$ Hidden Nodes)
- Dense input projection: $2D N_t$ FLOPs.
- Recurrent matrix multiply: $2 N_t^2$ FLOPs.
- Tanh activations: $8 N_t$ FLOPs.
- Readout & online update: $4 N_t$ FLOPs.
- Sensitivity & variance checks: $4 N_t$ FLOPs.
- **Total:** $\mathbf{2D N_t + 2 N_t^2 + 16 N_t\text{ FLOPs/step}}$ (for $N_t=3, D=50$: $300 + 18 + 48 = \mathbf{366\text{ FLOPs/step}}$).

### 3.5 Baseline B4: Minimal GRU ($N=1$)
- Reset and update gates: $2 \times (2D + 2 + 8) = 4D + 20$ FLOPs.
- Candidate hidden state: $2D + 2 + 8 = 2D + 10$ FLOPs.
- State interpolation: $4$ FLOPs.
- RTRL sensitivities (9 scalar parameters): $36$ FLOPs.
- Parameter updates: $18$ FLOPs.
- **Total:** $\mathbf{6D + 88\text{ FLOPs/step}}$ (388 FLOPs for $D=50$).

### 3.6 Baseline B5: Online ESN ($N_{\text{res}}$ Nodes)
- Fixed reservoir update: $2D N_{\text{res}} + 2 N_{\text{res}}^2$ FLOPs.
- Tanh non-linearities: $8 N_{\text{res}}$ FLOPs.
- Readout LMS update: $4 N_{\text{res}}$ FLOPs.
- **Total:** $\mathbf{2D N_{\text{res}} + 2 N_{\text{res}}^2 + 12 N_{\text{res}}\text{ FLOPs/step}}$ (for $N_{\text{res}}=20, D=50$: $2000 + 800 + 240 = \mathbf{3040\text{ FLOPs/step}}$).

---

## 4. Standardized Memory Accounting Specification (Sections 127–131)

Model memory is partitioned into four distinct physical categories, reported in exact bytes (assuming IEEE-754 64-bit double precision, 8 bytes/value):

```
+-------------------------------------------------------------------------------+
|                       FOUR-TIER MEMORY ACCOUNTING STANDARD                    |
|                                                                               |
|  1. M_STATIC (Persistent Parameters):  Trainable weights + biases             |
|  2. M_STATE  (Dynamic State Memory):   Recurrent hidden state vectors s_t     |
|  3. M_AUX    (Optimizer / Traces):     Sensitivity traces, variance stats     |
|  4. M_TEMP   (Scratch Workspace):      Transient activation buffers           |
+-------------------------------------------------------------------------------+
```

### 4.1 Primary Deployment Footprint Metric (Section 128)
$$\mathbf{M_{\text{DEPLOY}} = M_{\text{STATIC}} + M_{\text{STATE}} + M_{\text{AUX}} \quad \text{(in Bytes)}}$$

### 4.2 Resource Reclamation Measurement Protocol (Section 129)
To rigorously test Track B's claim of physical resource reclamation:
1. **$M_{\text{pre}}$:** Allocated memory during initial state-free operation ($t \le t_{\text{birth}}$);
2. **$M_{\text{peak}}$:** Peak memory allocated while recurrent state is active ($t \in [t_{\text{birth}}, t_{\text{evict}}]$);
3. **$M_{\text{post}}$:** Allocated memory following confirmed obsolescence and state eviction ($t \ge t_{\text{evict}} + 1$).
- **Success Condition for Reclamation:** $M_{\text{post}} \equiv M_{\text{pre}}$. All state buffers and sensitivity structures must be physically deallocated and returned to system memory.

---

## 5. Standardized Wall-Clock Benchmarking Protocol (Sections 119–126)

- **Execution Environment:** Dedicated single-thread CPU pinning (`taskset -c 0` on Linux / processor affinity mask on Windows). Zero hyperthreading contention.
- **Warm-Up Phase (Section 120):** Exactly 100 streaming steps executed prior to timing measurement to warm instruction caches and initialize memory allocators.
- **I/O Exclusion (Section 134):** Disk reading and CSV parsing are executed upfront into RAM buffers; timers wrap *only* the causal `predict` and `update` loop.
- **Timing Repetitions (Sections 165 & 166):** 5 repeated runs per configuration with alternating model execution order; reported metric is median step latency ($\mu s$) and throughput (samples/sec).

---

## 6. Formal Certification of Questions 12 & 13 (Sections 204 & 205)

- **Audit Question 12:** *Is FLOP accounting consistent across linear operations, gating, nonlinearities, probe operations, and state lifecycle operations?*  
  **Audit Verdict:** **`YES`**. Every operation is priced using an explicit mathematical schedule (MAC = 2, division = 4, transcendental = 8).
- **Audit Question 13:** *Is memory accounting consistent across parameters, optimizer states, recurrent states, sensitivity traces, replay, and auxiliary statistics?*  
  **Audit Verdict:** **`YES`**. Memory is rigorously tracked across all four tiers ($M_{\text{STATIC}}, M_{\text{STATE}}, M_{\text{AUX}}, M_{\text{TEMP}}$) in exact bytes.
