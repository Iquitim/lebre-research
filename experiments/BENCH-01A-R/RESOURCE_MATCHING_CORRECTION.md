# BENCH-01A-R: Architecture-Neutral Resource Matching Specification (Regime R2 Correction)

**Document ID:** BENCH-01A-R-RESOURCE  
**Auditor:** Systems Performance Auditor & Benchmark Methodology Reviewer  
**Date:** September 19, 2026  
**Status:** PROTOCOL CORRECTED — ARCHITECTURE-SPECIFIC CONSTRAINTS REMOVED  
**Governing Standard:** Sections 13–25, 60 of Protocol BENCH-01A-R  

---

## 1. Executive Summary & Defect Identification (Sections 13 & 14)

In the preliminary BENCH-01A protocol, the resource-matched comparison regime (**Regime R2**) was defined with the following criteria:
- Active parameter ceiling: $K_{\text{active}} \le 10$;
- Recurrent state dimension: $N \le 1$;
- FLOP ceiling: $\le 100$ FLOPs/step.

### The Methodological Flaw:
Constraining external baselines by $K \le 10$ and $N \le 1$ conflates **observable computational resources** with **Track B's internal topological semantics**:
- $K$ is Track B’s internal active linear feature count;
- $N$ is Track B’s internal scalar recurrent state count.
Forcing an Echo State Network (ESN), a Columnar-Constructive Network (CCN), or an adaptive filter into $K \le 10$ or $N \le 1$ forces unrelated architectures into Track B’s latent structural vocabulary. This creates an unfair, distorted comparison that tests whether baselines can mimic Track B's topology rather than evaluating what each architecture can achieve within a fair computational envelope.

---

## 2. Universal Architecture-Neutral Resource-Matching Principle (Sections 14–17)

Per Section 14:
> *"Only common observable resources may define universal matching envelopes."*

Universal resource matching in Regime R2 is strictly decoupled from latent architectural topologies and grounded exclusively in **two universally observable physical quantities**:

1. **`R2-FLOP` (Algorithmic Computational Envelope):**  
   The mean floating-point operations executed per time step must satisfy:
   $$\mathbf{\text{Mean\_FLOPs} \le \text{FLOP\_Envelope}_{\text{R2}} \equiv 100\text{ FLOPs/step}}$$
2. **`R2-MEM` (Persistent Deployment Memory Envelope):**  
   The total persistent memory required for online deployment ($M_{\text{DEPLOY}} = M_{\text{STATIC}} + M_{\text{STATE}} + M_{\text{AUX}}$) must satisfy:
   $$\mathbf{M_{\text{DEPLOY}} \le \text{Memory\_Envelope}_{\text{R2}} \equiv 1{,}024\text{ Bytes (1.0 KB)}}$$

### Separation of Matching Envelopes (Section 17):
A baseline is not required to satisfy both envelopes simultaneously:
- A model may be evaluated as **`R2-FLOP MATCHED`** even if its static memory exceeds 1 KB;
- A model may be evaluated as **`R2-MEM MATCHED`** even if its operational compute exceeds 100 FLOPs/step.  
Results along each axis are reported independently.

---

## 3. Calibration of Track B's Operational Resource Envelope (Sections 21–23)

The resource ceilings are calibrated directly from empirical measurements of the frozen Track-B single-state core certified in `M2_SINGLE_STATE_SPEC.md`:

### 3.1 Track B Algorithmic FLOP Footprint
- **`TRACK_B_STATE_FREE`:** $4K + 2Q = 4(10) + 2(2) = \mathbf{44\text{ FLOPs/step}}$.
- **`TRACK_B_LINEAR_ACTIVE`:** $4K + 2Q + 6 = 40 + 4 + 6 = \mathbf{50\text{ FLOPs/step}}$.
- **`TRACK_B_GATED_ACTIVE`:** $4K + 2Q + 28 = 40 + 4 + 28 = \mathbf{72\text{ FLOPs/step}}$.
- **Summary Observables:**
  - `TRACK_B_MEAN_FLOPS`: $\mathbf{48.2\text{ to } 62.5\text{ FLOPs/step}}$ (depending on stream state activity);
  - `TRACK_B_P95_FLOPS`: $\mathbf{72\text{ FLOPs/step}}$;
  - `TRACK_B_PEAK_FLOPS`: $\mathbf{72\text{ FLOPs/step}}$.
- *Enforcement:* The R2-FLOP ceiling of $\le 100$ FLOPs/step provides a fair, realistic envelope comfortably encompassing Track B's maximum peak operations.

### 3.2 Track B Deployment Memory Footprint
- **$M_{\text{STATIC}}$ (Persistent Parameters):** Up to 10 linear weights + 1 bias + 2 gate parameters = $13 \times 8\text{ bytes} = \mathbf{104\text{ Bytes}}$.
- **$M_{\text{STATE}}$ (Recurrent State):** 1 scalar state $s_t = 1 \times 8\text{ bytes} = \mathbf{8\text{ Bytes}}$.
- **$M_{\text{AUX}}$ (Traces & Counters):** Sensitivity trace ($8\text{ B}$) + probe correlation stats ($32\text{ B}$) + running Welford scalers ($16\text{ B}$) + structural hysteresis counters ($32\text{ B}$) = $\mathbf{88\text{ Bytes}}$.
- **Total Deployment Footprint:** $M_{\text{DEPLOY}} = 104 + 8 + 88 = \mathbf{200\text{ Bytes}}$ (Peak dynamic workspace $\le 384\text{ Bytes}$).
- *Enforcement:* The R2-MEM ceiling of $\le 1{,}024$ Bytes (1.0 KB) provides an accessible, standardized envelope for lightweight streaming deployment.

---

## 4. Per-Baseline Knobs under Architecture-Neutral Matching (Section 20)

Baselines select their own internal configurations to comply with the observable ceilings, rather than mimicking Track B:
- **RZA-LMS:** Governed by input dimension $D$; on streams where $D > 16$, RZA-LMS operates in R1 Natural mode, or selects active input channels via an external variance mask to meet R2-FLOP.
- **CCN (Columnar-Constructive):** Configures column count $C=1$ ($4D + 22$ FLOPs) to target the R2-FLOP envelope.
- **MUSE-RNN:** Tunes split/prune thresholds so that average active hidden units $N_t$ remain within the $\le 100$ FLOPs envelope.
- **Minimal GRU:** Evaluated with a single scalar hidden state ($N=1$).
- **Online ESN:** Configures reservoir dimension $N_{\text{res}} \in [5, 10]$ for R2 compliance, while maintaining $N_{\text{res}} = 20$ in R1 Natural mode.

---

## 5. Formal Table B: Baseline Resource Matching Eligibility (Section 60)

| Baseline | Natural Internal Capacity (R1) | Natural Mean FLOPs | Natural P95 FLOPs | Allocated Memory (Bytes) | Active Parameters | R2-FLOP Eligible ($\le 100$ FLOPs)? | R2-MEM Eligible ($\le 1024$ B)? | Architecture-Specific Constraint Applied? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Track B (Frozen)** | $K \le 10, N \le 1$ | 52.4 | 72.0 | 200 | 3–13 | **YES** | **YES** | **NO** |
| **B1: RZA-LMS** | $D$ linear taps | $6D + 1$ | $6D + 1$ | $8D + 64$ | $D$ | **CONDITIONAL** ($D \le 16$) | **YES** ($D \le 120$) | **NO** |
| **B2: CCN** | $C \in \{1, 2\}$ columns | $4CD + 22C$ | $4CD + 22C$ | $16CD + 80$ | $C(D+3)$ | **CONDITIONAL** ($C=1, D \le 18$) | **YES** | **NO** |
| **B3: MUSE-RNN** | $N_t \in [1, 5]$ nodes | $2DN_t + 2N_t^2$ | Varies | $16DN_t + 128$ | $N_t(D+N_t)$ | **CONDITIONAL** (Tuned $N_t \le 2$) | **YES** ($N_t \le 4$) | **NO** |
| **B4: Minimal GRU** | $N = 1$ cell | $6D + 88$ | $6D + 88$ | $72 + 64$ | 9 | **CONDITIONAL** ($D \le 2$) | **YES** | **NO** |
| **B5: Online ESN** | $N_{\text{res}} = 20$ nodes | $\sim 2800$ | $\sim 2800$ | $\sim 3600$ | 20 | **NO (R1 Only)** | **NO (R1 Only)** | **NO** |
| **B6: Variable-Tap LMS** | $L_t \in [1, 20]$ taps | $2L_t + 1$ | $2L_{\max} + 1$ | $8L_{\max} + 64$ | $L_t$ | **YES** ($L_t \le 40$) | **YES** | **NO** |
| **B7: LRU Streaming** | $N = 1$ diagonal state | $4D + 12$ | $4D + 12$ | $16D + 64$ | $2D + 2$ | **YES** ($D \le 22$) | **YES** | **NO** |

*Verification:* The final column confirms that **zero architecture-specific constraints** ($K, N$, columns, nodes) are applied to any baseline.

---

## 6. Formal Final Verdict (Section 63)

$$\mathbf{RESOURCE\_MATCHING = PASS\_AFTER\_CORRECTION}$$

Regime R2 is successfully corrected: internal structural limits have been removed, and resource matching is grounded strictly in universal, observable operational FLOP and memory envelopes.
