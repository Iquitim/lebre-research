# Rotating Sparse Frontier Specification

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Candidate Architecture Specification  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  

---

## 1. Architectural Motivation and Principles

The **Rotating Sparse Frontier** ($C_1$) replaces the static, globally instantiated $160$-cell correlation matrix with an active, bounded memory structure of capacity $H \ll 160$ slots. 

This design is founded on two physical observations:
1. In sparse dynamical systems, true predictive delays occupy a tiny subset of the lag space ($\le 5\%$ of cells).
2. Probing unpromoted, low-correlation cells continuously creates severe noise amplification and spurious candidate generation.

---

## 2. Mathematical State Definition

The frontier maintains exactly $H$ physical slots in RAM, partitioned dynamically into:
1. **Tracking Set ($\mathcal{F}_{\text{track}}$):** Up to $H_{\text{track}} = \lfloor 0.75 \times H \rfloor$ cells. Contains coordinates that currently exhibit elevated correlation ($|\hat{\rho}| \ge 0.15$) or are currently undergoing probation in the candidate tier.
2. **Exploration Set ($\mathcal{F}_{\text{explore}}$):** Remaining $H_{\text{explore}} = H - |\mathcal{F}_{\text{track}}|$ slots. Populated dynamically from a procedural circular traversal of all 160 coordinate pairs.

### Frontier Slot Structure:
For each slot $j \in \{0, \dots, H-1\}$:
- Coordinate: $(i_j, k_j) \in \{0..4\} \times \{1..32\}$.
- State: $\hat{C}_j$ (cross-correlation accumulator), $\hat{E}_{X,j}$ (feature energy accumulator).
- Status flag: $\text{TRACKING}$ vs. $\text{EXPLORATION}$.
- Age counter: $a_j$ (steps since slot assignment).

---

## 3. Algorithmic Workflow at Probe Clock ($t \pmod{K_{\text{probe}}} == 0$)

At each search probe tick ($K_{\text{probe}} = 2$ steps):
1. **Batch Selection:** Select $B$ slots to probe:
   - Proportions: approximately $\lceil 0.75 \times B \rceil$ slots from $\mathcal{F}_{\text{track}}$, and the remainder from $\mathcal{F}_{\text{explore}}$.
2. **Online Interrogation (4 FLOPs/slot):**
   For each selected slot $j$:
   $$\hat{C}_j \leftarrow \lambda_{\text{corr}} \hat{C}_j + (1 - \lambda_{\text{corr}}) e_{\text{base}}(t) X_{i_j}(t - k_j)$$
   $$\hat{E}_{X,j} \leftarrow \lambda_{\text{corr}} \hat{E}_{X,j} + (1 - \lambda_{\text{corr}}) X_{i_j}^2(t - k_j)$$
   $$\hat{\rho}_j \leftarrow \frac{\hat{C}_j}{\sqrt{\hat{E}_{\text{base}} \hat{E}_{X,j} + 10^{-8}}}$$
3. **Threshold Check & Escalation:**
   - If $|\hat{\rho}_j| \ge \tau_{\text{birth}} = 0.25$ and no candidate exists for $(i_j, k_j)$:
     - Spawn candidate structure in probation tier.
     - Lock slot $j$ into $\mathcal{F}_{\text{track}}$.
4. **Frontier Refresh and Eviction:**
   - For exploration slots that have been probed $\ge 2$ consecutive rounds without crossing $|\hat{\rho}| \ge 0.15$:
     - Reset slot accumulators.
     - Advance circular cursor to the next coordinate in $\{0..4\} \times \{1..32\}$ that is not currently in $\mathcal{F}_{\text{track}}$.
   - For tracking slots where the associated candidate was purged and $|\hat{\rho}_j| < 0.15$:
     - Demote slot back to $\mathcal{F}_{\text{explore}}$.

---

## 4. Parameter Grid for DEV Screening

In Phase 2 DEV screening, four candidate configurations of $C_1$ are evaluated:

| Variant | Frontier Capacity ($H$) | Batch Probes ($B$) | Probe FLOPs/step | Peak RAM (Bytes) | Mean Revisit Time ($T_{\text{explore}}$) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **$C_{1a}$** | 16 | 2 | 4.00 FP/step | 148 bytes | 592 steps |
| **$C_{1b}$** | 16 | 4 | 8.00 FP/step | 148 bytes | 296 steps |
| **$C_{1c}$** | 32 | 2 | 4.00 FP/step | 292 bytes | 544 steps |
| **$C_{1d}$** | 32 | 4 | 8.00 FP/step | 292 bytes | 272 steps |

All variants satisfy the TinyML budget ceiling ($\le 100.00\text{ FP/step}$) and maintain zero dense correlation arrays in RAM.
