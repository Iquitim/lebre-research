# BOUNDED-HISTORY-LAG-INTEGRATION-01: Preregistered Hypotheses & Falsification Matrix
## Formal Evaluation Criteria for Bounded-History Representations

**Stage:** `BOUNDED-HISTORY-LAG-INTEGRATION-01`  
**Parent State:** `AUDIT-SEAL-01` (SEALED)  
**Governing Architecture:** LEBRE v0.1 (`FROZEN_WITH_SCOPE_LIMITS`)  
**Auditor Roles:** Skeptical Senior ML Researcher, Statistical Reviewer.

---

## 1. Formal Hypotheses Specification

### Hypothesis P1: Reduced Precision Feasibility
- **Formal Statement:** Storing history in IEEE 754 half-precision float16 (H1) or properly scaled 16-bit integer (H2) preserves sparse-lag discovery performance without significant degradation relative to float32 (H0).
- **Confirmation Threshold:**
  $$\Delta \text{NMSE} = \text{NMSE}_{H1} - \text{NMSE}_{H0} \le 0.015, \quad \text{Support Recall}_{H1} \ge 90\% \text{ of } \text{Recall}_{H0}$$
- **Falsification Threshold:** $\Delta \text{NMSE} > 0.050$ or Support Recall drops by $\ge 20\%$.

### Hypothesis P2: Age-Dependent Precision (Mixed-Precision Hierarchy)
- **Formal Statement:** Storing recent lags ($k \le 8$) in FP16 and older lags ($k > 8$) in INT8 (H4) maintains discovery latency and prediction accuracy superior to uniform INT8 (H3).
- **Confirmation Threshold:**
  $$\text{Discovery Latency}_{H4} \le \text{Discovery Latency}_{H3}, \quad \text{NMSE}_{H4} \le \text{NMSE}_{H3}$$
- **Falsification Threshold:** H4 performs identically to or worse than H3 on discovery latency.

### Hypothesis P3: Multirate History Is Signal-Dependent
- **Formal Statement:** Multirate decimation (H5) succeeds on temporally compressible, bandlimited streams (Regime B) but fails severely on high-entropy, independent exact-delay streams (Regime A) where decimated lags are unrecoverable.
- **Confirmation Threshold:**
  $$\text{Recall}_{H5, \text{Regime B}} \ge 0.70, \quad \text{Recall}_{H5, \text{Regime A}} \le 0.40, \quad p < 0.001$$
- **Falsification Threshold:** Multirate decimation achieves high recall on arbitrary IID streams.

### Hypothesis P4: Projected History Fails on Sharp Discrete Delays
- **Formal Statement:** Continuous polynomial projection (H7: HiPPO / LMU) provides smooth long-term memory but attenuates isolated high-frequency discrete delays on IID white noise streams, failing support localization.
- **Confirmation Threshold:**
  $$\text{Lag Localization Error}_{H7} > 2.0 \text{ steps on IID tasks}, \quad \text{Support Recall}_{H7} \le 0.50$$
- **Falsification Threshold:** Order-6 polynomial projection localizes arbitrary single-step discrete delays on white noise with recall $\ge 80\%$.

### Hypothesis P5: Exact Addressability Imposes a Non-Negotiable Memory Cost
- **Formal Statement:** On high-entropy IID streams, memory compression below 16 bits/sample produces a measurable degradation in exact support recall and prediction error.
- **Confirmation Threshold:** Monotonic increase in discovery error as bits/sample decreases ($32 \to 16 \to 8$).
- **Falsification Threshold:** INT8 matches FP32 on all high-entropy tasks with zero recall loss.

### Hypothesis P6: History Compression Preserves Recurrence Coexistence
- **Formal Statement:** Bounded-history providers do not degrade the performance of the scalar recurrent unit ($N=1$) on continuous-state tasks (BH11).
- **Confirmation Threshold:**
  $$\text{NMSE}_{H1, BH11} \le \text{NMSE}_{B0, BH11} + 0.010$$
- **Falsification Threshold:** Bounded history destabilizes scalar recurrence, increasing error by $\ge 0.10$.

### Hypothesis P7: Resource Scaling Feasibility
- **Formal Statement:** Reduced-precision history providers (H1, H3) enable scaling to wider channels ($D=10, L_{\max}=32$) or longer horizons ($D=5, L_{\max}=64$) while strictly adhering to the micro-edge ceiling ($\le 1024$ Bytes).
- **Confirmation Threshold:** Total persistent state for $D=10, L_{\max}=32$ under H1 $\le 1024$ Bytes.
- **Falsification Threshold:** No configuration beyond $(D=5, L_{\max}=32)$ fits in 1024 Bytes.
