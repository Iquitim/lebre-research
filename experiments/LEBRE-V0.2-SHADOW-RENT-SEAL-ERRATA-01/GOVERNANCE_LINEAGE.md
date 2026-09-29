# Governance Lineage & Regulatory Evolution of LEBRE v0.2

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Audit Context:** Cryptographic and Normative Traceability Across Milestones M1, M2, and Post-M2 Stabilization  

---

## 1. Executive Summary & Regulatory Purpose

The LEBRE (Low-complexity Edge-adaptive Bounded-history Recurrent Engine) architecture has evolved across multiple experimental cycles under strict confirmatory protocols. To maintain scientific integrity, every gate, budget threshold, and validation rule must trace back to an authorized preregistration. 

This document traces the complete governance lineage leading to `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`, cataloging the historical definitions of all resource, structural, and behavioral gates, and identifying when and where semantic drift or metric substitutions occurred.

---

## 2. Chronological Stage Progression

```
+-------------------------------------------------------------------------------------------------------------+
| Stage Identifier                                    | Primary Scope & Milestone Role                         |
+-------------------------------------------------------------------------------------------------------------+
| ARCH-SPEC-01R2 / 01R2a                              | M1 Core Spec: Classical Linear Baseline + Ring Buffer   |
| LEBRE-V0.2-INTEGRATION-DESIGN-01                    | Integration Study: T0, T1, T1R, T2, T3 (12 Gates)      |
| LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01                | Forensic Seal Audit: Detected 1024->2048 B relaxation  |
| LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01          | Reconciled Seed 1301 pasting & confirmed Gate 6 = FAIL  |
| LEBRE-V0.2-RESOURCE-COMPACTION-01                   | FP16 correlation grid compaction exploratory study     |
| LEBRE-V0.2-RESOURCE-COMPACTION-CORRECTIVE-CONFIRM-01| Pre-registered confirmatory run (Seeds 1511..1540)      |
| LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01              | Reconciled C1 memory (Mean=976 B, Max=1054 B)          |
| LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01                | Shadow scheduling evaluation: S0, S1, S2, S3 (M2 Seal) |
| LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01 (Current)     | Forensic micro-errata & whole-shadow scheduling seal   |
+-------------------------------------------------------------------------------------------------------------+
```

---

## 3. The 12 Integration Gates: Historical Evolution

```
+-------------------------------------------------------------------------------------------------------------------+
| Gate Identifier | Preregistered Criterion (Integration) | Reconciled Baseline (Seal-01) | Shadow-Rent Adaptation   |
+-------------------------------------------------------------------------------------------------------------------+
| Gate 1: Compute | Live FP <= 100.0 FLOPs/step           | Live FP = 81.17 FLOPs/step     | Total FP <= 100.0 FLOPs  |
| Gate 2: Non-Inf | Delta NMSE <= +0.0100 (vs T1)         | Delta NMSE = -0.0716 (PASS)    | Delta NMSE <= +0.0100(S0)|
| Gate 3: Memory  | Persistent Capacity <= 1024 Bytes     | Mean=976 B, Max=1054 B (C1)    | Capacity <= 1024 B (S3)  |
| Gate 4: Latency | Switch Latency <= +50.0 steps         | Median Delta = -15.5 to +582 s | Switch Latency <= +50.0 s|
| Gate 5: Hybrid  | G_cond > 0.0150 on I9                 | G_D=0.256, G_R=0.140 (PASS)    | Qualitative G > 0.0150   |
| Gate 6: Redund  | frac_both <= 0.05 on I10 (t in 1k..6k)| frac_both = 0.1085 (FAIL)      | Drifted to 0.10 in Report|
| Gate 7: S_bar   | Stationary Churn S_bar <= 0.10        | S_bar = 0.0214 (PASS)          | Inherited from T3 Base   |
| Gate 8: Support | Exact Lag Recall >= 70% (I3, I4)      | Recall = 87.2%, Prec = 30.1%   | Inherited from T3 Base   |
| Gate 9: Order   | Sequential Order Invariance           | Invariance = 0.0000 (PASS)     | Preserved Bitwise        |
| Gate 10: State  | Correct Structural State on I1..I14   | State Accuracy = 91.4% (PASS)  | Evaluated per scheduler  |
| Gate 11: Budget | Peak Persistent <= 1024 B (Relaxed)   | 1306 B (C0 FAIL), 976 B (C1)   | Evaluated in Gate 3      |
| Gate 12: Pareto | Multi-objective Vector Dominance      | T3 Dominates T1, T2, O_ALL     | Evaluated across S0..S3  |
+-------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Key Governance Transitions & Lineage Tracking

### 4.1 Memory Governance Transition: Legacy R2 vs. Proposed 2048 B
- **The Legacy R2 Constraint:** Preregistered in `LEBRE_V0_2_RESOURCE_MODEL.md` (line 84) and `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` (line 71) as `RAM <= 1024 Bytes`.
- **The First Breach:** In `LEBRE-V0.2-INTEGRATION-DESIGN-01`, implementation of `corr_grid` as a $5 \times 33$ float32 matrix caused persistent memory to reach $1,306$ Bytes, failing Gate 11.
- **The Post-Hoc Relaxation:** The integration final report silently relaxed Gate 11 to $2,048$ Bytes without an amendment.
- **The Compaction Correction:** `RESOURCE-COMPACTION-01` and `RESOURCE-COMPACTION-SEAL-01` successfully compressed `corr_grid` to FP16 ($330$ Bytes), bringing **Mean Occupied Memory** to **$976.32$ Bytes** ($\le 1024$ B).
- **The Persistent Capacity Caveat:** However, **Maximum Occupied Persistent Capacity** (with all taps, candidates, and active recurrent units held simultaneously) remains **$1,054$ Bytes** ($+30$ B over legacy 1024 B).
- **Shadow-Rent Status:** Adding scheduler state ($4$ B for $S_2$, $16$ B for $S_3$) shifts mean occupied memory to $980.32$ B and $992.32$ B (PASS $\le 1024$ B), while peak capacity reaches $1,068$ B and $1,080$ B (FAILS legacy $1024$ B; PASSES proposed $2048$ B).

### 4.2 Compute Governance Transition: Live Path vs. Total Online
- **The Live Path Allocation:** In integration design, $T_3$ lived within budget by evaluating only live-path execution against the $100$-FLOP ceiling ($81.17$ FLOPs/step).
- **The Unbudgeted Shadow Reality:** Continuous shadow exploration added $86.42$ FLOPs/step in background probing, pushing total online compute to $169.06$ FLOPs/step.
- **The Shadow-Rent Mandate:** Milestone M2 mandated bringing **Total Online Compute (Live + Shadow + Scheduler)** under the strict **$100.0\text{ FLOPs/step}$** ceiling.

### 4.3 Gate 6 Redundancy Lineage: The 5% Binding Ceiling
- **Integration Preregistration:** Gate 6 was preregistered as $\rho_{\text{dual}} = \text{frac\_both} \le 0.05$ on $I_{10}$ across $t \in [1000, 6000)$.
- **Integration Outcome:** Confirmatory cohort exhibited mean `frac_both` of $0.1085$, with 22 of 30 seeds breaching $0.05$. Official status: `FAIL`.
- **Compaction Protocol:** Preregistration explicitly stated: *"This stage does NOT attempt to fix Gate 6. The historical status remains FAIL."*
- **Shadow-Rent Preregistration:** Preregistration line 31 explicitly recorded: *"Gate 6 Redundancy Status: Carried forward as FAIL (not intentionally repaired)."*
- **The Report Drift:** In `SHADOW_RENT_FINAL_REPORT.md`, the author evaluated $S_2$ ($9.2\%$) and $S_3$ ($8.4\%$) against a post-hoc $10.0\%$ ceiling and declared "PASS Gate 6".
- **The Errata Ruling:** In the absence of a pre-confirmatory amendment, the $5.0\%$ threshold remains legally binding. Gate 6 compliance remains `FAIL`. The algorithmic reduction of dual occupancy ($49.4\%$ for $S_2$, $53.9\%$ for $S_3$) is confirmed as a valid descriptive mitigation.
