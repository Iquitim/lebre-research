# Coarse-to-Fine Mechanism & Kronecker Delta Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Mechanistic Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **SCOPED & RECONCILED**  

---

## 1. Audit of the "Kronecker Delta" Language

### The Narrative Claim:
In `CORRELATION_SEARCH_FINAL_REPORT.md` and `LAG_SCORE_LOCALITY_REPORT.md`, the text stated:
> "Consequently, the correlation landscape over lag index is a Kronecker delta spike $\delta(k - k^*)$, not a smoothed Gaussian or Lorentzian peak."

### Forensic Analysis:
1. **Mathematical Population Ground Truth:**
   In LEBRE benchmarks, input features $X_{i}(t)$ are generated as independent Gaussian white innovations:
   $$\mathbb{E}[X_i(t) X_i(t - \tau)] = \sigma_X^2 \delta(\tau)$$
   When the target $y(t)$ contains an exact discrete delay $y(t) = w X_i(t - k^*) + \dots$, the cross-correlation with base residual $e_{\text{base}}(t) = y(t) - \hat{y}_{\text{base}}(t)$ evaluates asymptotically to:
   $$\lim_{T \to \infty} \hat{\rho}(k) = \begin{cases} \frac{w}{\sigma_{\text{base}}}, & k = k^* \\ 0, & k \ne k^* \end{cases}$$
   Thus, in the infinite-sample population limit, the landscape is indeed a pure Kronecker delta.
2. **Finite-Sample Physical Reality:**
   In finite prequential streaming with tracking memory ($\lambda_{\text{corr}} = 0.95$), the cross-correlation accumulator exhibits a non-zero estimation noise floor:
   $$\hat{\rho}(k \ne k^*) \sim \mathcal{N}\left(0, \frac{1 - \lambda}{1 + \lambda}\right) \approx 0.04 \dots 0.14$$
   Immediate neighbors $k^* \pm 1$ averaged $0.1398$ and $0.1388$, not zero.
3. **Audited Claim Standard:**
   The claim is **conceptually valid but overgeneralized**. It should be formally scoped as:
   *"approximately isolated delta-like lag-correlation peak under the tested white-innovation generators."*
   It cannot be generalized to streaming environments with temporally colored or autocorrelated inputs without empirical validation.

---

## 2. Audit of the "Odd-Lag Blindness" Mechanism

### Code Verification:
In `scratch/run_v02_correlation_search_compaction.py` (lines 800–850), Candidate $C_2$ instantiates coarse anchors:
$$\mathcal{K}_{\text{coarse}} = \{2, 4, 8, 12, 16, 24\}$$
The refinement rule states:
```python
if abs(c_val) >= 0.20:
    # Activate neighbors k - 1 and k + 1
```

### Empirical Trace:
1. Benchmark task $I_4$ (`I4_Multi_Sparse_Delay`) has true delays at $(0, 3)$, $(2, 14)$, and $(4, 27)$.
2. For the true delay $k^* = 3$:
   - The nearest coarse anchors are $k = 2$ and $k = 4$.
   - At lag $k=2$ and $k=4$, the observed correlation is in the noise floor ($\approx 0.139$).
   - Because $0.139 < \tau_{\text{refine}} = 0.20$, the coarse anchor never crosses the threshold.
   - Consequently, neighbors $k = 3$ are never added to the fine refinement set.
   - $k^* = 3$ is **permanently ignored** throughout the entire 6,000 steps.
3. On DEV, $C_2$ achieved only $38.10\%$ true delay recall and an NMSE of $0.3563$ ($\Delta\text{NMSE} = +0.0592$).
4. **Audit Finding:** The odd-lag blindness mechanism is **EMPIRICALLY CONFIRMED AND REPRODUCED** for the evaluated hierarchical structure.
