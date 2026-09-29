# Specification: Recurrent Skip Semantics & Path-Continuity Invariants

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. The Path-Dependence Dilemma

In adaptive filtering, skipping a parameter update (`SKIP_PARAMETER_UPDATE`) is benign because frozen weights simply persist:
$$w_t = w_{t-1}$$
In recurrent dynamical systems, however, the state $h_t$ is an evolving latent memory. Skipping a state update (`SKIP_STATE_UPDATE`) introduces structural divergence:

| Candidate Semantics | Mathematical Operationalization | Path Distortion | Memory Traffic | FLOPs per Skipped Step | Viability for M1* |
|:---|:---|:---:|:---:|:---:|:---:|
| `1. HOLD_STATE` | $h_t = h_{t-1}$ (State frozen in register; downstream uses stale $h$) | Moderate step distortion; introduces phase lag | ZERO | **0.0 FP** | **ADOPTED IN D9F & FROZEN** |
| `2. DECAY_ONLY` | $h_t = a h_{t-1}$ (Autonomous decay; ignores inputs) | High amplitude distortion during active input | Low | 1.0 FP | REJECTED (Distorts active signals) |
| `3. BATCHED_PROP` | Buffer inputs; step $K$ steps sequentially at step $K$ | ZERO path distortion | High | 12.0 FP / K | REJECTED (Zero FLOP saving) |
| `4. FAST_FORWARD` | Analytical convolution $h_t = a^K h_{t-K} + \sum a^j b x_{t-j}$ | ZERO path distortion | High | $pprox 2.4	ext{ FP/step}$ | REJECTED (Complexity / sensitivity issue) |

---

## 2. Certified D9F Historical Semantics

Audit of `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01` confirms that condition `D9F` executed:
$$\mathbf{D9F\_SKIP\_SEMANTICS = HOLD\_STATE}$$

- When $t 
ot\equiv 0 \pmod K$, the recurrent unit does not execute `forward()`.
- The cached prediction register $\hat{y}_{	ext{rec\_shadow}}$ and hidden state register $h_t$ retain their previous values:
  $$\hat{y}_{	ext{rec\_shadow}}(t) = \hat{y}_{	ext{rec\_shadow}}(t - (t mod K))$$
- Downstream arbitration uses the stale cached value with zero floating point recomputation.
- **Invariance Rule:** For this stage, `HOLD_STATE` is strictly frozen to preserve causal consistency with historical D9F evidence.
