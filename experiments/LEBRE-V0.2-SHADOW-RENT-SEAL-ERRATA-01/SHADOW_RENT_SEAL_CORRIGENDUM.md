# Formal Seal Corrigendum: LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Document Status:** Binding Additive Correction & Formal Registry of Errata  
**Governing Authority:** Level 1 & Level 3 Confirmatory Preregistration Standards  

---

## 1. Preamble & Corrigendum Policy

In accordance with confirmatory reproducibility standards (Simmons et al., 2011; Nosek et al., 2018), when post-hoc threshold drift, metric conflations, or reporting misstatements are discovered in sealed experimental artifacts, they must be formally corrected via an additive, immutable corrigendum.

The parent artifacts in `experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/` remain physically intact to maintain cryptographic reproducibility. This corrigendum serves as the binding normative authority governing the interpretation of all results from that study.

---

## 2. Master Errata Register

```
+-----------------------------------------------------------------------------------------------------------------------------------+
| Errata ID | Document & Location | Original Reporting               | Audited Corrected Reporting        | Severity & Classification   |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-01    | FINAL_REPORT.md:110 | Gate 6 Redundancy <= 10.0%:      | Gate 6 Redundancy <= 5.0%:         | CRITICAL                    |
|           | (Table 5.1)         | S2: PASS (9.2%), S3: PASS (8.4%) | S2: FAIL (9.18%), S3: FAIL (8.37%) | Post-hoc threshold drift    |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-02    | FINAL_REPORT.md:152 | "Duty-cycling resolves the legacy| "Duty-cycling mitigates co-occupancy| SUBSTANTIVE                 |
|           | (Section 6.5)       | Gate 6 failure on I10."          | by 49.4% (S2) and 53.9% (S3), but  | Overstatement of resolution |
|           |                     |                                  | fails the preregistered ceiling."  |                             |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-03    | FINAL_REPORT.md:107 | "Peak RAM <= 1024 B":            | "Mean Occupied Persistent RAM":    | CRITICAL                    |
|           | (Table 5.1)         | PASS (976 B, 980 B, 992 B)       | 976.3 B, 980.3 B, 992.3 B.         | Metric conflation           |
|           |                     |                                  | True Peak is 1064 B, 1068 B, 1080 B| (Mean reported as Peak)     |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-04    | FINAL_REPORT.md:22  | "The theoretical compute floor is| "The behavior-preserving reference | MODERATE                    |
|           | (Section 1.2)       | F_min = 83.17 FLOPs/step."       | floor is 83.17 FP; the absolute    | Scope qualification         |
|           |                     |                                  | minimal execution floor is 58.00." |                             |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-05    | FINAL_REPORT.md:150 | "...virtually extinguishing      | "...virtually extinguishing shadow | MINOR                       |
|           | (Section 6.5)       | energy waste during silence..."  | compute and execution overhead..." | Terminology defect          |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-06    | FINAL_REPORT.md:182 | "Reducing background exploration | "Under the evaluated periodic      | MODERATE                    |
|           | (Section 7.1)       | inherently slows correlation     | downsampling policy (K=5), slower  | Overbroad generalization    |
|           |                     | statistics convergence."         | convergence was observed."         |                             |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-07    | FINAL_REPORT.md:184 | "In indefinitely long streams... | "Analytical extrapolation suggests | MODERATE                    |
|           | (Section 7.1)       | duty cycle would be < 5%."       | longer streams may amortize further| Unverified extrapolation    |
|           |                     |                                  | (HYPOTHETICAL_EXTRAPOLATION)."     |                             |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-08    | FINAL_REPORT.md:207 | PRIMARY_OUTCOME =                | PRIMARY_OUTCOME =                  | MODERATE                    |
|           | (Section 8)         | COMPUTE_RECOVERED_PREDICTIVE_    | COMPUTE_RECOVERED_BEHAVIOR_        | Taxonomy label mismatch     |
|           |                     | DEGRADED                         | DEGRADED                           |                             |
+-----------------------------------------------------------------------------------------------------------------------------------+
| ERR-09    | FINAL_REPORT.md:195 | "Candidate S2 satisfies Gate 1   | "Candidate S2 satisfies Gate 1 and | SUBSTANTIVE                 |
|           | (Section 7.2)       | and physical memory (PASS)."     | mean memory, but FAILS Gate 2 and  | Incomplete gate disclosure  |
|           |                     |                                  | Gate 4. Whole-block not validated."|                             |
+-----------------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Specific Textual Corrigenda & Replacement Text

### Corrigendum 1: Table 5.1 (Final Report Page 6)
**Original Text:**
```markdown
| **Gate 3** | Peak RAM $\le 1024\text{ B}$ | `PASS` ($976\text{ B}$) | `PASS` ($904\text{ B}$) | **`PASS` ($980\text{ B}$)** | **`PASS` ($992\text{ B}$)** |
| **Gate 6** | Redundancy Gate $\le 10.0\%$ | `FAIL` ($18.2\%$) | `PASS` ($0.0\%$) | **`PASS` ($9.2\%$)** | **`PASS` ($8.4\%$)** |
```
**Replacement Text:**
```markdown
| **Gate 3 (Mean)** | Mean Persistent RAM $\le 1024\text{ B}$ | `PASS` ($976.3\text{ B}$) | `PASS` ($904.0\text{ B}$) | `PASS` ($980.3\text{ B}$) | `PASS` ($992.3\text{ B}$) |
| **Gate 3 (Peak)** | Peak Persistent SRAM $\le 1024\text{ B}$ | `FAIL` ($1064\text{ B}$)  | `PASS` ($904\text{ B}$)   | `FAIL` ($1068\text{ B}$)  | `FAIL` ($1080\text{ B}$)  |
| **Gate 6**        | Redundancy Gate $\le 5.0\%$ (Binding)    | `FAIL` ($18.15\%$)        | `PASS`* ($0.00\%$)        | `FAIL` ($9.18\%$)         | `FAIL` ($8.37\%$)         |
```
*\* Note: S1 passes Gate 6 trivially because all temporal feature discovery is disabled, causing complete predictive failure.*

---

### Corrigendum 2: Section 6.5 (Redundancy Mitigation Claim)
**Original Text:**
> *"Duty-cycling resolves the legacy Gate 6 failure on $I_{10}$. Under $S_0$, redundant co-activation occupied $18.2\%$ of steps; under $S_2$ and $S_3$, occupancy drops to $9.2\%$ and $8.4\%$ ($\le 10.0\%$, **PASS Gate 6**)."*

**Replacement Text:**
> *"Duty-cycling significantly suppresses redundant co-activation on $I_{10}$, cutting steady-state dual occupancy from $18.15\%$ ($S_0$) to $9.18\%$ ($S_2$, a $49.4\%$ relative reduction) and $8.37\%$ ($S_3$, a $53.9\%$ relative reduction). However, because the binding preregistered ceiling is $5.0\%$, both configurations strictly **FAIL Gate 6**. The descriptive mitigation of dual occupancy is confirmed, but the legacy Gate 6 failure remains formally unclosed."*

---

### Corrigendum 3: Section 1.2 (Compute Floor Claim)
**Original Text:**
> *"The theoretical compute floor is $F_{\text{min}} = 81.17 + 2.00 = 83.17\text{ FLOPs/step} \le 100.0$."*

**Replacement Text:**
> *"The behavior-preserving reference floor—conditioned on executing the average structural mixture recruited by continuous baseline $S_0$ with shadow exploration silenced—is $F_{\text{ref\_floor}} = 81.17 + 2.00 = 83.17\text{ FLOPs/step}$. The absolute minimal execution floor of the memoryless linear base path (Structural State `NONE`) is $58.00\text{ FLOPs/step}$, as empirically confirmed by control $S_1$."*

---

### Corrigendum 4: Section 7.2 (Integration Authorization & Governance Ruling)
**Original Text:**
> *"Candidate $S_2$ rigorously satisfies the $100\text{-FLOP}$ ceiling ($89.53\text{ FLOPs/step}$, Gate 1 PASS) and physical memory budget ($980\text{ Bytes}$, Gate 3 PASS)... Candidate $S_2$ is selected as the provisional M2 candidate."*

**Replacement Text:**
> *"While Candidate $S_2$ successfully recovers total online compute below $100\text{ FLOPs/step}$ ($89.53\text{ FP}$, Gate 1 PASS) and satisfies mean memory budgets, it fails Gate 2 predictive non-inferiority ($\Delta \text{NMSE} = +0.0567 > 0.0100$) and Gate 4 switching latency ($+763\text{ steps} > +50\text{ steps}$). Candidate $S_3$ satisfies switching latency on $I_{12}$ but fails compute ($110.07\text{ FP} > 100.0$) and predictive non-inferiority ($+0.0159 > 0.0100$).*  
> *Consequently, **`WHOLE_BLOCK_SHADOW_GOVERNANCE = NOT_VALIDATED`**. Neither whole-block scheduler is authorized for integrated validation. However, because the single-difference invariant and causal mechanisms are fully understood, the study is **`SAFE_FOR_NEXT_RESEARCH_STAGE`**, authorizing fine-grained shadow multirate research (decoupling slow background correlation estimation from fast dynamic tap execution)."*

---

## 4. Certification of Corrigendum

This document represents the final, authoritative reconciliation of `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`. All downstream stages referencing Milestone M2 must incorporate these corrected values and governance classifications.
