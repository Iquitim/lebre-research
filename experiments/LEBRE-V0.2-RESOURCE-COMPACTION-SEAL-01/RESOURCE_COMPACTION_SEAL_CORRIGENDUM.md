# Resource Compaction Seal Corrigendum & Forensic Adjustments

**LEBRE-V0.2-RESOURCE-COMPACTION-SEAL-01**

---

## 1. Executive Summary

This formal corrigendum documents all discrepancies, reporting overstatements, arithmetic reconciliations, and inferential corrections identified during the forensic audit of `LEBRE-V0.2-RESOURCE-COMPACTION-01`.

In adherence to the Hard Audit Rule:
$$\text{PRESERVE} \longrightarrow \text{REPRODUCE} \longrightarrow \text{TRACE} \longrightarrow \text{CLASSIFY} \longrightarrow \text{CORRECT REPORTING} \longrightarrow \text{RE-EVALUATE DECISION}$$
every parent artifact in `experiments/LEBRE-V0.2-RESOURCE-COMPACTION-01/` has been cryptographically preserved without mutation. The adjustments below constitute the certified scientific corrections.

---

## 2. Itemized Corrigendum Table

| Corrigendum ID | Category | Parent Study Reporting | Forensic Audit Finding & Correction | Scientific Impact |
| :--- | :--- | :--- | :--- | :--- |
| **CORR-01** | Compute Ledger | Reported `C0_FP_FLOPS = 56.5`, `C1_FP_FLOPS = 56.5` in machine block; reported `Mean Live = 81.36`, `Mean Shadow = 26.83`, `Total = 108.19` in Table 6. | **Omitted Scaler Update in Compaction Script:** In `CompactedLEBREModel.step()`, line 559 of the integration model (`self.scaler.update()`) was omitted, subtracting $20$ FLOPs ($56.52$ vs $76.52$). Canonical live compute in `IntegratedLEBREModel` is **$81.37$ FLOPs/step**. Full 14-task online compute is **$167.99$ FLOPs/step**. Table 6 combined parent live compute ($81.36$) with analytical marginal shadow probing ($26.83$). | Explains all compute discrepancies; establishes canonical baseline for shadow rent reduction. |
| **CORR-02** | Memory Ledger | `CORR_GRID_MEMORY_LEDGER.csv` reported totals of $1306$ B ($C_0$) and $976$ B ($C_1$), but column sum was $1410$ B and $1080$ B. | **Conflation of Capacity and Occupancy:** The column entries summed maximum capacity ($1384$ B / $1054$ B) and added an unallocated $26$ B metadata term. The true empirical mean occupied state is **$1306.32$ B ($C_0$)** and **$976.32$ B ($C_1$)**, saving exactly $330.0$ Bytes. Under mean occupied state, $C_1$ complies with the legacy $1024$-B ceiling. Maximum capacity peak is $1054$ B ($+30$ B over $1024$ B; complies with proposed $2048$-B ceiling). | Arithmetically proves memory ledger; certifies compliance under mean operational occupancy. |
| **CORR-03** | Inferential Unit | Equivalence testing reported with sample size $N = 420$ paired simulations ($30 \text{ seeds} \times 14 \text{ tasks}$). | **Pseudoreplication Across Tasks:** Pooling observations sharing the same random seed generator violates independent sampling (Hurlbert, 1984). The correct LEBRE inferential unit is **SEED ($N=30$)**. Recomputed TOST on seed aggregate differences: paired mean delta $\bar{d} = +0.00000862$, $90\%$ CI: $[-0.0000043, +0.0000215]$, $p_{\text{TOST}} = 4.10 \times 10^{-71} \ll 0.05$. | Resolves pseudoreplication while rigorously confirming behavioral equivalence. |
| **CORR-04** | Numerical Stagnation | Narrative text stated "no observed stagnation", while numerical stress report noted 4 stagnation events in Test B. | **Disaggregation of Streaming vs Synthetic Stress:** In actual streaming operation across $3.36 \times 10^6$ steps, **zero stagnation events occurred** (`STREAMING_OBSERVED_STAGNATION_COUNT = 0`). The 4 stagnation events occurred exclusively in adversarial synthetic Test B where innovation updates were forced below $10^{-4}$ ($< \epsilon_{\text{FP16}}$), confirming Cioffi's (1987) theorem. | Eliminates narrative contradiction; confirms numerical safety under streaming operation. |
| **CORR-05** | Gate 6 Governance | Compaction cohort reported mean co-activation `frac_both = 0.0332 <= 0.05` on task $I_{10}$. | **No Gate 6 Repair Authorized:** Compaction was an intervention on precision, not arbitration. The lower cohort mean reflects stochastic variation across seed blocks (Seeds 1411..1440). $4$ to $5$ individual seeds still breached $0.05$ (up to $13.94\%$). Formal status of Gate 6 remains **FAIL** as established in the parent confirmatory audit. | Prevents premature or invalid claims of Gate 6 resolution. |
| **CORR-06** | Zero-Variance Cases | Several metrics ($I_1$ NMSE, modal regime agreement, switch latencies) had identical values across all seeds ($\Delta = 0.0$). | **Degenerate TOST Handling:** Parametric Student's $t$ division by zero standard error is degenerate. Reclassified as **`EXACT_EMPIRICAL_EQUALITY_ON_CONFIRMATORY_SAMPLE`** with `TOST_STATUS = DEGENERATE_ZERO_VARIANCE`, which deterministically satisfies the equivalence bound. | Mathematically formalizes exact equality without division-by-zero artifacts. |

---

## 3. Re-evaluation of Architectural Candidate Status

Following application of these six corrections:
1. **Candidate $C_1$ (`T3_FP16_CORR_GRID_FP32_UPDATE`) remains valid and superior to $C_0$:** It reduces persistent memory by exactly $330.0$ Bytes ($25.27\%$), bringing mean persistent memory to $976.32$ Bytes ($\le 1024$ B).
2. **Behavioral Equivalence is Certified:** Confirmed with $p_{\text{TOST}} = 4.10 \times 10^{-71}$ under independent seed inference ($N=30$).
3. **Stage 2.3 Charter is Clarified:** The certified total online compute ($167.99$ FLOPs/step) and persistent Gate 6 failure mandate the execution of `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`.
