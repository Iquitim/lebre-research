# Errata Claim Dependency Graph & Surviving Evidence Evaluation

**Audit Identifier:** `LEBRE-V0.2-SEAL-AUDIT-ERRATA-01`  
**Focus:** Causal Impact of Errata (H7 Order Sensitivity & I10 48.2% Double-Payment) on Architectural Selection of Topology $T_3$  
**Author:** Independent Skeptical Scientific Auditor  
**Date:** September 2026  

---

## 1. Claim Dependency Mapping

The diagram below tracks how the headline claims identified as erroneous or overstated connect to the central architectural decision to select $T_3$ (Resource-Aware Conditional Arbitration):

```mermaid
graph TD
    subgraph S1["Cascade Order Sensitivity Claims"]
        H7_OLD["CLAIM: T1 vs T1R has max discrepancy 0.1654 on I4 (p < 1e-6)<br/>[OVERSTATED & ERRONEOUS]"]
        H7_NEW["CORRECTED: Order sensitivity is descriptive (max on I8 = 0.1654; I4 diff = 0.0007, p=0.887)<br/>[DESCRIPTIVE_ONLY]"]
        REJ_CASCADE["Rejection of Fixed Sequential Cascades (T1, T1R)"]
    end

    subgraph S2["Symmetric Evaluation Property"]
        T3_INV["CLAIM: T3 has internal evaluation order invariance (D->R == R->D)<br/>[INDEPENDENTLY VERIFIED BY MICROTEST]"]
        SYM_EVAL["Symmetric Shadow Evaluation Architecture"]
    end

    subgraph S3["Double Payment / Redundancy Claims"]
        I10_OLD["CLAIM: T2 suffers 48.2% redundant dual allocation on I10<br/>[LINEAGE ERRATUM: Copy-forward from DEV]"]
        I10_NEW["CORRECTED: T2 suffers 100.0% steady-state dual occupancy on I10<br/>Burns 118.8 vs 92.4 FLOPs (+28.6% waste) for worse NMSE<br/>[CONFIRMATORY DATA SUPPORTED]"]
        REJ_T2["Rejection of Unarbitrated Symmetric Competition (T2)"]
    end

    subgraph S4["Surviving Primary Evidence"]
        AGG_NMSE["Aggregate Confirmatory NMSE:<br/>T3 = 0.2876 vs T1 = 0.3592, T2 = 0.3833, O_ALL = 0.4258<br/>(p = 1.86e-9 vs cascades)<br/>[CONFIRMED]"]
        HYBRID_COMPL["Hybrid Complementarity on I9:<br/>Both G_D|BR and G_R|BD > 0.01 (p = 2.33e-8)<br/>[CONFIRMED]"]
        FAMILY_SPEC["Memory Family Specialization on I3, I4, I6, I7<br/>[CONFIRMED]"]
        NEG_CTRL["Negative Control Safety on I1, I2<br/>[CONFIRMED]"]
        PARETO_VEC["Aggregate Vector Pareto Dominance over all comparators<br/>[CONFIRMED]"]
    end

    subgraph S5["Final Decision"]
        T3_SELECT["Architectural Selection of T3 Candidate<br/>(EXPERIMENTAL_NON_CANONICAL)"]
    end

    H7_OLD -.->|Replaced by| H7_NEW
    H7_NEW -->|Provides auxiliary rationale for| REJ_CASCADE
    T3_INV -->|Directly justifies| SYM_EVAL
    SYM_EVAL --> T3_SELECT

    I10_OLD -.->|Replaced by| I10_NEW
    I10_NEW -->|Strictly justifies| REJ_T2
    REJ_CASCADE --> T3_SELECT
    REJ_T2 --> T3_SELECT

    AGG_NMSE ==> T3_SELECT
    HYBRID_COMPL ==> T3_SELECT
    FAMILY_SPEC ==> T3_SELECT
    NEG_CTRL ==> T3_SELECT
    PARETO_VEC ==> T3_SELECT
```

---

## 2. Impact Analysis: Does Correcting H7 and 48.2% Weaken the Selection of $T_3$?

### 2.1 Impact of Repairing H7 (Order Sensitivity)
- **Original Claim:** The report claimed that reversing the cascade order ($T_1 \to T_{1R}$) produced a universal, statistically devastating failure on $I_4$ ($p < 10^{-6}, \Delta = 0.1654$).
- **Errata Finding:** On $I_4$, $T_1$ and $T_{1R}$ are statistically indistinguishable ($p = 0.8872, \Delta = 0.0007$). However, descriptive order discrepancies exist on other tasks ($I_8$ has mean absolute paired difference $0.1654$; $I_3$ has $0.1586$).
- **Architectural Impact:** The primary rejection of sequential cascades ($T_1$ and $T_{1R}$) **does not rely on H7**. Cascades are rejected primarily because:
  1. Both $T_1$ and $T_{1R}$ achieve significantly worse aggregate NMSE ($0.3592$ and $0.3418$) than $T_3$ ($0.2876$, $p = 1.86 \times 10^{-9}$);
  2. Cascades permanently allocate both modules on tasks like $I_{10}$ and $I_2$ due to directional residual leakage;
  3. $T_3$'s internal evaluation symmetry is independently proven by construction and microtesting, regardless of whether $T_1$ and $T_{1R}$ diverge.
- **Verdict:** Rationale for symmetric evaluation is **fully preserved**.

### 2.2 Impact of Repairing the 48.2% Metric on Task $I_{10}$
- **Original Claim:** $T_2$ suffered a "48.2% redundant dual allocation rate".
- **Errata Finding:** 48.2% was a copy-forward error from developmental screening logs. In truth, $T_2$ spent **100.0% of steady-state evaluation time in the `BOTH` state**.
- **Architectural Impact:** Rather than weakening the rejection of $T_2$, the true confirmatory evidence **strengthens it**:
  - $T_2$ does not merely suffer intermittent 48.2% dual occupancy; it suffers **permanent 100.0% dual co-allocation**!
  - It burns $118.8$ live FLOPs (compared to $92.4$ for $T_3$, a $+28.6\%$ overhead) with worse predictive accuracy ($NMSE = 0.4940$ vs. $0.4173$ for $T_3$).
  - $T_3$ successfully arbitrates the ambiguity, spending only $10.8\%$ of time in transient dual allocation and achieving $0.000\%$ redundant dual rate.
- **Verdict:** Rationale for conditional arbitration is **strengthened**.

---

## 3. Surviving Evidence Matrix

Every piece of empirical evidence supporting the selection of Topology $T_3$ is evaluated below strictly on whether it survives the errata audit:

| Evidence Stream | Valid Level 1 Source? | Dependent on H7? | Dependent on 48.2%? | Supports $T_3$? | Evidential Strength |
|:---|:---:|:---:|:---:|:---:|:---|
| **Aggregate Prequential NMSE** | **YES** (`LEBRE_V0_2_SEED_RESULTS.csv`) | NO | NO | **YES** | **DECISIVE** ($T_3=0.2876$ beats all, $p < 10^{-8}$) |
| **Hybrid Complementarity ($I_9$)** | **YES** (`LEBRE_V0_2_CONDITIONAL_GAINS.csv`) | NO | NO | **YES** | **DECISIVE** ($p = 2.33 \times 10^{-8}$) |
| **Negative Control Safety ($I_1, I_2$)** | **YES** (`LEBRE_V0_2_SEED_RESULTS.csv`) | NO | NO | **YES** | **STRONG** ($\bar{K}=0.019, \bar{S}=0.058$) |
| **Memory Family Specialization** | **YES** (`LEBRE_V0_2_SEED_RESULTS.csv`) | NO | NO | **YES** | **STRONG** (Lag on $I_3/I_4$, Rec on $I_6/I_7$) |
| **Redundancy Elimination ($I_{10}$)** | **YES** (`LEBRE_V0_2_SEED_RESULTS.csv`) | NO | NO | **YES** | **STRONG** ($T_3$ 10.8% dual vs. $T_2$ 100.0%) |
| **Aggregate Vector Pareto Dominance**| **YES** (`LEBRE_V0_2_SEED_RESULTS.csv`) | NO | NO | **YES** | **STRONG** (Dominates all on live & full online) |
| **$T_3$ Internal Evaluation Invariance**| **YES** (Permutation microtest) | NO | NO | **YES** | **ANALYTIC & EMPIRICAL** (Identical decisions) |
| **Regime Tracking Plasticity** | **YES** (`LEBRE_V0_2_STRUCTURAL_EVENTS.csv`) | NO | NO | **YES** | **MODERATE** (Discovery 206 steps, retire 69 steps) |
| **Cascade Order Sensitivity ($T_1/T_{1R}$)**| **PARTIAL** (Descriptive on $I_8, I_3$) | **YES** | NO | **QUALIFIED** | **DESCRIPTIVE ONLY** (Withdrawn as confirmatory test) |

---

## 4. Final Architectural Selection Verdict

Following the removal and correction of all contaminated quantities, the selection of **$T_3$ (Resource-Aware Conditional Arbitration)** as the leading architectural candidate remains **SUPPORTED WITH SCOPE LIMITS**.

The core innovations of $T_3$—symmetric shadow candidate evaluation, conditional loss grid arbitration, and structural dormancy—are robustly vindicated by the surviving confirmatory data.
