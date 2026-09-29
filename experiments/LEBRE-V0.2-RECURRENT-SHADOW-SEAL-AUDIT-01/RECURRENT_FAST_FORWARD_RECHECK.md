# Recurrent Fast-Forward Recheck & Mathematical Equivalence

**Audited Issue:** Flags F15 & F16 (Exact multi-step unrolling vs sequential complexity).

### 1. Mathematical Derivation
For linear-state recurrence $h_t = a h_{t-1} + b x_t$, unrolling over $K$ steps yields:
$$h_t = a^K h_{t-K} + \sum_{j=0}^{K-1} a^j b x_{t-j}$$

### 2. Operation Accounting
| Step / Component | Multiplications | Additions | Memory Reads |
|:---|:---:|:---:|:---:|
| Sequential Stepping ($K$ steps) | $2K$ | $K$ | $K$ inputs |
| Exact Jump State Formula | $K + 1$ | $K - 1$ | $K$ inputs + $K$ weights |

### 3. RTRL Sensitivity Complexity
Under Real-Time Recurrent Learning (RTRL), sensitivities evolve as:
$$\frac{\partial h_t}{\partial \alpha} = a \frac{\partial h_{t-1}}{\partial \alpha} + (1 - a^2) h_{t-1}$$
Unrolling sensitivities over $K$ steps requires either step-by-step intermediate evaluations or storing and computing higher-order polynomial coefficients.

### 4. Epistemic Conclusion:
`FAST_FORWARD_STATE_EQUIVALENCE = SUPPORTED`  
`FAST_FORWARD_RESOURCE_ADVANTAGE = NONE (in non-quiescent streams)`  
`FAST_FORWARD_FULL_RTRL_EQUIVALENCE = NOT_SUPPORTED`
