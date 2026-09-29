# Mathematical Derivation: Analytical Fast-Forward for Scalar Recurrence

**Study ID:** `LEBRE-V0.2-RECURRENT-SHADOW-COST-RECONCILIATION-01`  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Governing State Equation

In LEBRE, the continuous recurrent shadow unit (`RecurrentScalarUnit`) maintains a scalar latent state $h_t$ driven by normalized input $x_t \in \mathbb{R}$:
$$h_t = a h_{t-1} + b x_t, \quad 	ext{where } a = 	anh(lpha) \in (-1, 1)$$

---

## 2. K-Step Analytical Fast-Forward Unrolling

Suppose the system decimates recurrent evaluation by skipping $K-1$ steps between evaluations, observing inputs at steps $t-K+1, \dots, t$. Expanding the linear state recurrence across $K$ consecutive steps:

$$egin{aligned}
h_{t-K+1} &= a h_{t-K} + b x_{t-K+1} \
h_{t-K+2} &= a h_{t-K+1} + b x_{t-K+2} = a^2 h_{t-K} + a b x_{t-K+1} + b x_{t-K+2} \
&\;\;dots \
h_t &= a^K h_{t-K} + \sum_{j=0}^{K-1} a^j b x_{t-j}
\end{aligned}$$

---

## 3. Algorithmic Resource Accounting of Fast-Forward

To compute $h_t$ exactly from $h_{t-K}$ without sequential stepping:
1. **Transition Exponentiation:** Compute $a^K$. This requires $\log_2(K)$ scalar multiplications (or 1 power op). Cost: $pprox 2	ext{ FP}$.
2. **State Transition:** Compute $a^K h_{t-K}$. Cost: $1	ext{ FP}$.
3. **Convolutional Input Summation:** Compute $\sum_{j=0}^{K-1} a^j b x_{t-j}$.
   - Requires querying past inputs $x_{t-j}$ for $j \in \{0, \dots, K-1\}$ from the ring buffer.
   - Requires $K$ multiplications and $K-1$ additions. Cost: $2K - 1	ext{ FP}$.
4. **Total Fast-Forward Compute Cost:**
   $$	ext{FP}_{	ext{fast\_forward}} = 2 + 1 + (2K - 1) = 2K + 2	ext{ FP}$$
5. **Amortized Per-Step Cost:**
   $$rac{	ext{FP}_{	ext{fast\_forward}}}{K} = 2 + rac{2}{K}	ext{ FP/step}$$

### Crucial Scientific Software Finding:
Sequential stepping of $h_t = a h_{t-1} + b x_t$ costs $3	ext{ FP/step}$ ($1$ mul, $1$ mul, $1$ add).
Evaluating the exact fast-forward formula amortizes to $2 + rac{2}{K}	ext{ FP/step}$.
For $K=5$: $2 + 2/5 = 2.4	ext{ FP/step}$.
Moreover, the sensitivities $p_lpha$ and $p_b$ involve nonlinear terms ($dtanh = 1 - a^2$), which do NOT admit a trivial linear summation without integrating state path history.

Therefore:
$$\mathbf{ANALYTICAL\_FAST\_FORWARD\_RESOURCE\_GAIN = NONE / LOW}$$
Exact closed-form fast-forwarding provides negligible computational advantage over standard decimation because the past inputs must still be summed!

---

## 4. Quiescent Silence Special Case (Exact Zero-Cost Fast-Forward)

A critical mathematical boundary arises when the recurrent input is identically zero ($x_	au = 0$ for all $	au \in [t-K, t]$).
Under true quiescence:
$$h_{t+\Delta} = a^{\Delta} h_t$$
The input summation collapses to exactly ZERO.
- State propagation requires only $1$ power computation ($a^{\Delta}$) and $1$ multiplication!
- For an arbitrary silent window of length $\Delta = 1000$ steps, computing $h_{t+\Delta}$ requires only $2	ext{ FP}$ total, yielding an amortized cost of:
  $$rac{2}{1000} = 0.002	ext{ FP/step}$$

**Conclusion:** Lazy quiescent fast-forwarding is mathematically viable and nearly free on true silence (e.g. $I_7$), but does NOT generalize to active non-quiescent inputs.
