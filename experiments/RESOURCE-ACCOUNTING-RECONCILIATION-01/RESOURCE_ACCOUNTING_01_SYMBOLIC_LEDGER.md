# RESOURCE-ACCOUNTING-RECONCILIATION-01: Static Symbolic Ledger & Complexity Derivation

**Stage:** `RESOURCE-ACCOUNTING-RECONCILIATION-01`  
**Status:** `FROZEN_PRE_EXPERIMENTAL`  
**Governing Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  

---

## 1. Dimensional Parameters

All complexity derivations are parameterized by:
- $D \in \mathbb{N}$: Observable input dimensionality ($D = 5$).
- $L_{\max} \in \mathbb{N}$: Maximum history delay horizon ($L_{\max} = 32$).
- $M \in \mathbb{N}$: Rotating candidate probes evaluated per step ($M = 2$).
- $K \in [0, K_{\max}]$: Number of currently active sparse delay taps ($K \le 4$).
- $C \in [0, C_{\max}]$: Number of currently provisional shadow candidates ($C \le 8$).
- $N \in \mathbb{N}$: Recurrent state dimension ($N = 1$).

---

## 2. Symbolic Derivation by Component

### A. Base Linear Filter
- **Inference (`BASE_LINEAR`):**
  $$y_{\text{base}} = \mathbf{w}_{\text{base}}^T \mathbf{x}_t$$
  - Multiplications: $D$
  - Additions: $D$
  - $\text{FP\_FLOPS} = 2D$ (MAC Count = $D$)
  - Memory: $D \times 4$ B read ($w_{\text{base}}$), $D \times 4$ B read ($x_t$) $\implies 8D$ Bytes read.
- **Normalization & Weight Update (`BASE_UPDATE`):**
  $$\text{denom} = \mathbf{x}_t^T \mathbf{x}_t + 10^{-4}, \quad \mathbf{w}_{\text{base}} \leftarrow \mathbf{w}_{\text{base}} + \frac{\mu_{\text{base}}}{\text{denom}} e_t \mathbf{x}_t$$
  - $\mathbf{x}^T \mathbf{x}$: $D$ muls, $D$ adds $\implies 2D$ FLOPs.
  - Scale step: 1 add ($+10^{-4}$), 1 div ($\mu / \text{denom}$), 1 mul ($\times e_t$) $\implies 3$ FLOPs.
  - Vector update: $D$ muls, $D$ adds $\implies 2D$ FLOPs.
  - Subtotal: $4D + 3$ FP FLOPs.
  - Memory: $D \times 4$ B written ($w_{\text{base}}$).

### B. Recurrent Unit (`RECURRENT_UPDATE`)
- **State Drive & Transition:**
  $$u_t = 0.1 x_{0, t} - 0.1 x_{1, t}, \quad s_t = \tanh(\lambda s_{t-1} + u_t), \quad y_{\text{rec}} = w_{\text{out}} s_t$$
  - Input drive: 2 muls, 1 sub $\implies 3$ FLOPs.
  - State step: 1 mul ($\lambda s$), 1 add ($+ u_t$), 1 $\tanh$ (priced at 8 FLOPs in BENCH-01B, or 1 transcendental) $\implies 10$ FLOPs.
  - Output projection: 1 mul $\implies 1$ FLOP.
  - Weight update: $w_{\text{out}} \leftarrow w_{\text{out}} + 0.05 e_t s_t$ $\implies 2$ muls, 1 add $\implies 3$ FLOPs.
  - Subtotal: $17$ FP FLOPs.
  - Memory: 8 B read ($w_{\text{out}}, s_{t-1}$), 8 B written ($w_{\text{out}}, s_t$).

### C. History Ring Buffer (`HISTORY_WRITE`)
- **Exact FP32 (H0 / B7):**
  $$\text{history}[:, \text{head}] = \mathbf{x}_t$$
  - Arithmetic FLOPs: $0$
  - Integer Ops: 1 modulo increment ($\text{head} = (\text{head} + 1) \pmod{L_{\max} + 1}$).
  - Memory Traffic: $D \times 4$ Bytes written.
- **Quantized INT8 (H3):**
  - Scale Check & Update: For each $d \in [0, D-1]$:
    - $|x_d|$: 1 float abs.
    - If $|x_d| > S_d$: $S_d \leftarrow \max(1.0, 0.99 S_d + 0.01 (|x_d| \times 1.2))$: 2 muls, 1 add, 1 max.
  - Quantize:
    $$q_d = \text{clip}\left(\text{round}\left(\frac{x_d}{S_d} \times 127.0\right), -127, 127\right)$$
    - 1 div (or mul by inv scale), 1 mul ($\times 127.0$), 1 round, 1 clip (2 compares), 1 float $\to$ int8 cast.
  - Total INT8 Write per step:
    - $\text{FP\_FLOPS} = 2D$ (div/mul by scale, mul by 127.0)
    - $\text{INTEGER\_OPS} = 4D$ (round, 2 clip compares, cast) + 1 modulo
    - Memory Traffic: $D \times 1$ Byte written.

### D. Active Lag Taps
- **Inference (`ACTIVE_TAP_FORWARD`):**
  $$y_{\text{lag}} = \sum_{j=1}^K w_j x_{i_j, t-k_j}$$
  - Per Tap Query: 1 history read.
  - Multiplication: $K$ muls.
  - Accumulation: $K$ adds.
  - $\text{FP\_FLOPS} = 2K$.
  - Memory: $K \times 4$ B read ($w_j$), $K$ delay loads ($4K$ B for FP32, $1K$ B for INT8).
- **Weight Adaptation (`ACTIVE_TAP_UPDATE`):**
  $$w_j \leftarrow \text{clip}\left(w_j + \frac{\mu_{\text{lag}}}{x_{\text{del}}^2 + 1.0} e_t x_{\text{del}}, -5.0, 5.0\right)$$
  - Denominator: 1 mul, 1 add $\implies 2$ FLOPs.
  - Update term: 1 div, 2 muls, 1 add $\implies 4$ FLOPs.
  - Clipping: 2 comparisons.
  - Total per tap: $6 \text{ FLOPs} + 2 \text{ compares}$. For $K$ taps: $6K$ FLOPs.
- **Two-Timescale Obsolescence & Relevance (`RELEVANCE_UPDATE`):**
  $$e_{-j} = y_t - (y_{\text{hat}} - w_j x_{\text{del}}), \quad \Delta_{\text{gain}} = e_{-j}^2 - e_{\text{live}}^2$$
  $$R_j \leftarrow 0.999 R_j + 0.001 \Delta_{\text{gain}} \quad (\text{if } |x_{\text{del}}| > 0.1)$$
  - Counterfactual error: 1 mul, 1 sub, 1 sub $\implies 3$ FLOPs.
  - Marginal gain: 2 muls, 1 sub $\implies 3$ FLOPs.
  - Relevance EMA: 2 muls, 1 add $\implies 3$ FLOPs.
  - Total per tap: $9 \text{ FLOPs} + 1 \text{ abs} + 1 \text{ compare}$. For $K$ taps: $9K$ FLOPs.

### E. Candidate Probing & Shadow Probation
- **Rotating Candidate Probing (`CANDIDATE_PROBING`):**
  $$\text{corr}_{i, k} \leftarrow 0.95 \text{corr}_{i, k} + 0.05 (e_{\text{live}} \times x_{i, t-k})$$
  - For $M$ candidate pairs: $M$ queries.
  - Correlation update: 2 muls, 1 add $\implies 3M$ FLOPs.
  - Absolute magnitude check: $|\text{corr}| > \theta_{\text{prob}}$: 1 abs, 1 compare.
- **Counterfactual Shadow Scoring (`SHADOW_SCORING`):**
  For each of $C$ provisional candidates:
  $$e_{\text{cand}} = y_t - (y_{\text{hat}} + w_{\text{shadow}} x_{\text{cand}}), \quad \Delta_m = e_{\text{live}}^2 - e_{\text{cand}}^2$$
  $$E_m \leftarrow 0.95 E_m + 0.05 \Delta_m, \quad w_{\text{shadow}} \leftarrow w_{\text{shadow}} + \frac{0.05}{x_{\text{cand}}^2 + 1.0} e_{\text{cand}} x_{\text{cand}}$$
  - Counterfactual error: 1 mul, 1 add, 1 sub $\implies 3$ FLOPs.
  - Variance gain: 2 muls, 1 sub $\implies 3$ FLOPs.
  - Evidence EMA: 2 muls, 1 add $\implies 3$ FLOPs.
  - Shadow gradient: 1 mul, 1 add (denom), 1 div, 2 muls, 1 add $\implies 6$ FLOPs.
  - Total per candidate: $15 \text{ FLOPs}$. For $C$ candidates: $15C$ FLOPs.

---

## 3. Grand Symbolic Comparison Table

| Component | Standardized FP FLOPs | Standardized Integer Ops | Bytes Read (FP32) | Bytes Written (FP32) | Bytes Read (INT8) | Bytes Written (INT8) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **History Write** | $0$ (FP32) / $2D$ (INT8) | $1$ (FP32) / $4D+1$ (INT8) | $0$ | $4D$ | $0$ | $D$ |
| **Base Forward** | $2D$ | $0$ | $8D$ | $0$ | $8D$ | $0$ |
| **Active Forward** | $2K$ | $0$ | $8K$ | $0$ | $5K$ | $0$ |
| **Recurrent Forward** | $14$ | $0$ | $8$ | $4$ | $8$ | $4$ |
| **Prediction Error** | $1$ | $0$ | $0$ | $0$ | $0$ | $0$ |
| **Candidate Scoring** | $15C$ | $0$ | $16C$ | $12C$ | $13C$ | $12C$ |
| **Base Update** | $4D + 3$ | $0$ | $0$ | $4D$ | $0$ | $4D$ |
| **Tap Weight Update** | $6K$ | $2K$ (clipping) | $0$ | $4K$ | $0$ | $4K$ |
| **Relevance Update** | $9K$ | $2K$ (gate) | $4K$ | $4K$ | $4K$ | $4K$ |
| **Recurrent Update** | $3$ | $0$ | $0$ | $4$ | $0$ | $4$ |
| **Candidate Probing** | $3M$ | $2M$ (gate) | $4M$ | $4M$ | $1M$ | $4M$ |
| **Total Symbolic Formula** | $\mathbf{6D + 17K + 15C + 3M + 21}$ | $\mathbf{4K + 2M + 1}$ | $\mathbf{8D + 12K + 16C + 4M + 8}$ | $\mathbf{8D + 8K + 12C + 4M + 12}$ | *(traffic reduced by up to 3.3x)* | |

---

## 4. Evaluation on Reference Parameter Values

For $D = 5$, $M = 2$, with typical steady-state active taps $K = 2$ and provisional candidates $C = 1$:
$$\text{Standardized FP FLOPs} = 6(5) + 17(2) + 15(1) + 3(2) + 21 = 30 + 34 + 15 + 6 + 21 = \mathbf{106.0 \text{ FLOPs}}$$
$$\text{Standardized Integer Ops} = 4(2) + 2(2) + 1 = \mathbf{13 \text{ Ops}}$$
$$\text{Memory Traffic (FP32)} = (40 + 24 + 16 + 8 + 8) + (40 + 16 + 12 + 8 + 12) = 96 + 88 = \mathbf{184 \text{ Bytes Moved}}$$

This formula proves that when provider query indexing ($2 \text{ FLOPs}$ per query) is removed from arithmetic FLOPs and placed into integer indexing, the true FP arithmetic cost of exact-history LEBRE sits naturally right at the micro-edge boundary.
