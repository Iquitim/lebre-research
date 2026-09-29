# Compute Floor Taxonomy and Scope Qualification Audit

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Audited Statement

The parent report (`SHADOW_MULTIRATE_FINAL_REPORT.md` Section 1) asserts:
> *"The live baseline path with active dynamic taps accounts for $76.30\text{ FP/step}$, and continuous recurrent state propagation accounts for $12.00\text{ FP/step}$, establishing an irreducible baseline floor of $88.30\text{ FP/step}$."*

---

## 2. Forensic Disaggregation of Compute Floors

In scientific software auditing, calling a numerical value an "irreducible floor" without specifying operating preconditions constitutes an unqualified claim. LEBRE exhibits three distinct compute regimes:

1. **Absolute Memoryless Execution Floor ($58.00\text{ FP/step}$):**
   - When no delay taps or recurrent structures are active, the normalized streaming linear filter consumes strictly $58.00\text{ FP/step}$. This is the universal minimum of the architecture.
2. **Active Dual-Memory Live Floor ($76.30\text{ FP/step}$):**
   - When one delay tap and one recurrent unit are actively retained in the live model, live feature concatenation, dot products, normalization, and parameter LMS updates consume $58.00 + 11.02 + 7.28 = 76.30\text{ FP/step}$.
3. **Reference-Occupancy Conditioned Floor ($88.30\text{ FP/step}$):**
   - The figure of $88.30\text{ FP/step}$ is obtained by summing:
     - Active dual-memory live pipeline: $76.30\text{ FP/step}$
     - Continuous shadow recurrent state propagation ($K=1$): $12.00\text{ FP/step}$
     - Total: $88.30\text{ FP/step}$

---

## 3. Classification and Corrected Wording

- **Audit Classification:** **`COMPUTE_FLOOR_88P3_CLASSIFICATION = REFERENCE_OCCUPANCY_CONDITIONED_FLOOR`**
- **Corrected Wording:**
  > *"Under the reference operating state where both delay and recurrent structures are live and shadow recurrent state propagation runs at $K=1$, the live-plus-recurrent-tracking baseline imposes a conditioned execution floor of $88.30\text{ FP/step}$, leaving $11.70\text{ FP/step}$ of headroom under the $100.00\text{ FP}$ ceiling."*
