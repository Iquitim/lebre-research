# Mathematical Model: Multirate Computational Feasibility & Budget Constraints

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2)  
**Author:** Independent Skeptical Senior Researcher  
**Date:** September 22, 2026  

---

## 1. Algorithmic Budget Equation

Total streaming computational burden per timestep is defined by the linear combination:

$$F_{\text{total}} = F_{\text{live}} + d_{\text{probe}} F_{\text{probe}} + d_{\text{cand\_obs}} F_{\text{cand\_obs}} + d_{\text{cand\_learn}} F_{\text{cand\_learn}} + d_{\text{rec\_prop}} F_{\text{rec\_prop}} + d_{\text{rec\_learn}} F_{\text{rec\_learn}} + d_{\text{arb}} F_{\text{arb}} + F_{\text{router}}$$

Where:
- $F_{\text{live}}$: Baseline live prediction and update burden ($\approx 81.17\text{ FP FLOPs/step}$ under continuous structural mixture).
- $d_i \in [0, 1]$: Execution duty cycle of atomic component $i$ ($d = 1/K$ for periodic schedules with period $K$).
- $F_i$: Cost per execution of component $i$ derived from the atomic ledger:
  - $F_{\text{probe}} = 8.0\text{ FP}$ (2 pairs $\times 4\text{ FP/probe}$)
  - $F_{\text{cand\_obs}} = 2.0\text{ FP}$ (candidate forward prediction)
  - $F_{\text{cand\_learn}} = 8.0\text{ FP}$ (LMS update and evidence EMA across active candidates)
  - $F_{\text{rec\_prop}} = 12.0\text{ FP}$ (recurrent hidden state propagation)
  - $F_{\text{rec\_learn}} = 22.0\text{ FP}$ (RTRL sensitivity update [$8\text{ FP}$] + weight update [$8\text{ FP}$] + evidence EMA [$6\text{ FP}$])
  - $F_{\text{arb}} = 28.0\text{ FP}$ (counterfactual loss grid [$8\text{ FP}$] + raw gains [$4\text{ FP}$] + gain EMA filtering [$16\text{ FP}$])
  - $F_{\text{router}}$: Computational overhead of the temporal router / scheduling logic.

Nominal continuous shadow cost:
$$F_{\text{shadow, full}} = 8.0 + 2.0 + 8.0 + 12.0 + 22.0 + 28.0 = \mathbf{80.0\text{ FP/step}}$$
Nominal full online continuous cost:
$$F_{\text{total, full}} = 81.17 + 80.00 = \mathbf{161.17\text{ FP/step}} \quad (> 100.0\text{ FP, Gate 1 FAIL})$$

---

## 2. Derivation of the Feasible Duty Polytope ($\bar{F}_{\text{total}} \le 100.0$)

The mandatory primary resource gate requires:
$$\bar{F}_{\text{total}} \le 100.00\text{ FP FLOPs/step}$$

Subtracting the live baseline burden ($F_{\text{live}} \approx 81.17\text{ FP}$):
$$\sum_{i} d_i F_i + F_{\text{router}} \le 100.00 - 81.17 = \mathbf{18.83\text{ FP FLOPs/step}}$$

### 2.1 The Recurrent Continuity Constraint
Because the recurrent hidden state is path-dependent, recurrent state propagation must execute continuously to prevent dynamical collapse:
$$d_{\text{rec\_prop}} = 1.0 \implies 1.0 \times 12.0 = 12.00\text{ FP FLOPs/step}$$

This leaves an available remaining margin of:
$$F_{\text{margin, rem}} = 18.83 - 12.00 = \mathbf{6.83\text{ FP FLOPs/step}}$$

### 2.2 Analytical Budget Allocation for Remaining Components
With $6.83\text{ FP/step}$ remaining, we derive the allowed duty combinations for probing, candidate adaptation, recurrent learning, and arbitration:

```
+---------------+----------------+-----------------+-------------+------------------+---------------+---------------+--------------------+
| Policy Regime | d_probe (FP)   | d_cand (FP)     | d_rec (FP)  | d_arb (FP)       | F_router (FP) | F_shadow (FP) | F_total (FP/step)  |
+---------------+----------------+-----------------+-------------+------------------+---------------+---------------+--------------------+
| Unfeasible A  | 1.0 (8.0 FP)   | 0.5 (5.0 FP)    | 0.5 (11 FP) | 0.5 (14 FP)      | 0.0 FP        | 50.0 FP       | 131.17 FP (FAIL)   |
| Unfeasible B  | 0.5 (4.0 FP)   | 0.5 (5.0 FP)    | 0.2 (4.4 FP)| 0.2 (5.6 FP)     | 0.0 FP        | 31.0 FP       | 112.17 FP (FAIL)   |
+---------------+----------------+-----------------+-------------+------------------+---------------+---------------+--------------------+
| Feasible P1   | 0.5 (K=2: 4 FP)| 0.2 (K=5: 2 FP) | 0.1 (K=10:2)| 0.05 (K=20: 1.4) | 0.0 FP        | 21.4 FP       | 102.57 FP (BORDER) |
| Feasible P2   | 0.2 (K=5: 1.6) | 0.2 (K=5: 2 FP) | 0.1 (K=10:2)| 0.10 (K=10: 2.8) | 0.0 FP        | 20.4 FP       | 101.57 FP (BORDER) |
| Feasible MR1  | 0.2 (K=5: 1.6) | 0.1 (K=10: 1 FP)| 0.05 (K=20) | 0.10 (K=10: 2.8) | 0.0 FP        | 18.5 FP       | 99.67 FP (PASS)    |
| Feasible MR2  | Data-selective | Innovation-gated| Error-gated | Fresh-evidence   | 1.0 FP        | 12.0 + 4.8 FP | 98.00 FP (PASS)    |
+---------------+----------------+-----------------+-------------+------------------+---------------+---------------+--------------------+
```

### 2.3 Hard Pre-Simulation Feasibility Constraint
Any policy proposal where:
$$8.0 d_{\text{probe}} + 10.0 d_{\text{cand}} + 12.0 d_{\text{rec\_prop}} + 22.0 d_{\text{rec\_learn}} + 28.0 d_{\text{arb}} + F_{\text{router}} > 18.83\text{ FP}$$
is mathematically guaranteed to fail Gate 1 ($\bar{F}_{\text{total}} \le 100.0$) and **shall not be simulated**.
