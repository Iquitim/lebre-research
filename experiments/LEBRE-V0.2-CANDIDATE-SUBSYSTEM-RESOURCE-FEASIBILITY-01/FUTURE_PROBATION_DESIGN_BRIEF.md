# Future Candidate Probation Design Brief: Architectural Families, Parsimony Principles & Governance Invariants
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Context: Non-Authorized Secondary Optimization Framework

---

## 1. Executive Summary & Design Scope

Although stage `LEBRE-V0.2-CANDIDATE-PROBATION-COST-01` has been denied authorization as a primary compute-restoration stage (because candidate probation cannot close the 100 FP gap), candidate probation optimization remains a scientifically viable **secondary refinement** for reducing candidate churn and eliminating $\approx 0.88\text{ FP/step}$ of spurious probation waste.

This design brief establishes three candidate architectural families, enforces strict parsimony constraints, and locks critical governance invariants for any future study targeting candidate lifecycle policies.

---

## 2. Permitted Architectural Design Families

A future candidate lifecycle intervention must restrict its design space to one of the following three families:

### Family P1: Fixed Early Futility Check (Deterministic Gate)
- **Mechanism:** A single, deterministic checkpoint at exposure $n = 7\text{ shadow observations}$ ($35\text{ stream steps}$).
- **Logic:** If running counterfactual utility $U_{\text{cand}}(n) \le 0.0$, the candidate is evicted immediately without completing the remaining $8$ shadow observations.
- **Resource Overhead:** Exactly $1$ floating-point comparison and $1$ branch instruction every $7$ shadow observations ($\approx 0.002\text{ FP/step}$).
- **Parsimony Advantage:** Zero additional persistent RAM, zero statistical accumulators, zero complex math.
- **Projected Saving:** Evicts $\approx 58\%$ of eventual failures, saving $\approx 0.88\text{ FP/step}$ with zero false rejection of eventually promoted true delays.

### Family P2: Sequential Evidence Boundaries (Anytime-Valid SPRT)
- **Mechanism:** Continuous sequential checking against dual adaptive boundaries:
  - Upper acceptance boundary $B_{\text{accept}}(n)$ (early promotion);
  - Lower rejection boundary $B_{\text{reject}}(n)$ (early discard).
- **Logic:** Evaluates cumulative likelihood or e-value process $E_n = \prod_{i=1}^n (1 + \lambda (e_{\text{base}}^2(i) - e_{\text{cand}}^2(i)))$.
- **Resource Overhead:** Requires 3 multiplies, 1 division, and logarithm/exponential lookups per observation ($\approx 0.25\text{ FP/step}$, plus 8 bytes of state per candidate).
- **Evaluation:** High risk of computational self-defeat. The algorithmic overhead of computing sequential bounds ($+0.25\text{ FP/step}$) erodes $\approx 30\%$ of the maximum possible savings ($0.88\text{ FP/step}$).

### Family P3: Two-Stage Hierarchical Probation
- **Mechanism:**
  - Stage 1 (Screening): $n \in [1, 5]$ shadow observations with loose threshold $\theta_{\text{screen}} = 0.0$.
  - Stage 2 (Confirmation): Candidates with $U_{\text{cand}}(5) > 0.0$ proceed to full probation ($n = 15$) under standard $\theta_{\text{promote}}$.
- **Resource Overhead:** Modest ($\approx 0.004\text{ FP/step}$).
- **Projected Saving:** Evicts $\approx 32\%$ of failures at $n=5$, saving $\approx 0.62\text{ FP/step}$.

---

## 3. The Parsimony Invariant: Simple Determinism Over Complex Statistics

Any future proposal must follow the **Parsimony Principle**:
$$\mathbf{Prefer \ One \ Deterministic \ Early \ Check \ (P1) \ Over \ Complex \ Sequential \ Statistics \ (P2)}$$

A sequential test that consumes $+0.25\text{ FP/step}$ in floating-point operations, requires dynamic logarithms, and adds $8\text{ bytes}$ of volatile RAM per candidate to save $0.88\text{ FP/step}$ yields an unacceptably poor engineering return. Complexity itself is a resource cost.

---

## 4. Governance Invariants for Future Investigations

If candidate probation is revisited in future stages, the following invariants are binding:

1. **Promotion Threshold Invariant ($\theta_{\text{promote}}$ Frozen):**
   - The promotion threshold $\theta_{\text{promote}}$ must **remain frozen**.
   - Changing $\theta_{\text{promote}}$ alters model-selection semantics and structural bias.
   - The purpose of candidate probation optimization is to alter **WHEN** sufficient evidence is recognized, not **WHAT** level of evidence qualifies as structurally useful.
2. **Horizon Invariant ($T_{\text{prob}} = 15$ Shadow Observations):**
   - The maximum probation horizon remains locked at $15$ shadow observations ($75$ stream steps).
3. **No Peeking with Conventional p-Values:**
   - Repeatedly peeking at standard fixed-sample statistical metrics online is forbidden.
4. **DEV/FINAL Separation:**
   - Any early rejection threshold must be tuned strictly on DEV tasks ($10\text{ seeds}$) and validated on fresh confirmatory seeds.
