# Matching Pursuit & Literature Analogy Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Literature-Analogy Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **RECLASSIFIED TO CONCEPTUAL ANALOGY**  

---

## 1. Audit of the "Identical to Matching Pursuit" Claim

### The Narrative Claim:
In `CORRELATION_SEARCH_FINAL_REPORT.md` Q22:
> "The active tracking partition ($\mathcal{F}_{\text{track}}$) operates identically to an online Matching Pursuit active set (Mallat & Zhang 1993), while the circular exploration partition ensures global exploration."

### Algorithmic Comparison:

| Algorithmic Dimension | Canonical Matching Pursuit (Mallat & Zhang 1993) | LEBRE Rotating Sparse Frontier ($M_1^*$) |
| :--- | :--- | :--- |
| **Dictionary Selection** | Global search over complete dictionary for atom with maximum inner product $|\langle R^k f, \phi_\gamma \rangle|$ | Subsampled round-robin batch evaluation ($B=4$) from a circular queue |
| **Active Set Evolution** | Greedy addition of the single optimal atom at each decomposition step | Threshold-based admission ($|\hat{\rho}| \ge 0.20$) into bounded table of size $H=32$ |
| **Residual Update** | Orthogonal projection / Gram-Schmidt subtraction: $R^{k+1} f = R^k f - \langle R^k f, \phi_{\gamma_k} \rangle \phi_{\gamma_k}$ | Base LMS residual $e_{\text{base}}(t) = y(t) - \hat{y}_{\text{base}}(t)$ shared across all probes |
| **Eviction Mechanism** | Sparsity threshold or backward elimination (in adaptive variants) | Linear scan for minimum correlation magnitude ($|\hat{\rho}_{\text{new}}| > |\hat{\rho}_{\text{min}}| + 0.02$) |
| **Orthogonalization** | Essential to prevent selecting collinear atoms (in OMP) | None (candidates adapt weights independently via LMS) |

---

## 2. Epistemic Verdict & Corrected Phrasing

- **Algorithmic Equivalence:** **`NOT_SUPPORTED`**. The algorithms differ in selection rule, residual calculation, dictionary coverage, and absence of orthogonalization.
- **Classification:** **`LITERATURE_ANALOGY_OVERREACH`**.
- **Corrected Scientific Phrasing:**
  *"The rotating sparse frontier shares a conceptual active-set analogy with Matching Pursuit in that a small subset of candidate atoms is maintained in high-priority tracking while the wider dictionary is interrogated incrementally; however, LEBRE does not perform greedy orthogonal projections."*
- **Variable Tap-Length FIR Adaptation:** Similarly, claims stating that LEBRE is "ideally suited" for variable tap-length filtering (Q22) are classified as **`SPECULATIVE`** / **`CONCEPTUAL_COMPATIBILITY`** because no variable tap-length FIR baseline was experimentally evaluated in this stage.
