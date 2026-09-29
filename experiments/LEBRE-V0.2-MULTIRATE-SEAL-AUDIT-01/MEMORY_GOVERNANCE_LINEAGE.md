# Memory Governance Lineage: Historical R2 vs. Peak Working SRAM

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Problem Statement

In `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`, the final machine-readable block reported:
```text
HISTORICAL_R2_PERSISTENT_MEMORY_STATUS = FAIL
```
because maximum occupied memory reached $1064\text{ B}$.

This audit reconciles the historical governance of memory limits across LEBRE v0.1 and v0.2 to determine whether historical R2 compliance was operationalized as mean persistent memory, max persistent memory, static capacity, or peak working SRAM.

---

## 2. Historical Document Reconstruction

1. **Canonical v0.1 Specification (`docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md:409`):**
   > *"Persistent Model Memory: 440.0 Bytes (compliant with R2-MEM $\le 1024$)."*
   > *"Across evaluated benchmarks, LEBRE exhibited an observed mean persistent model-state footprint of 440.0 bytes of RAM (under the R2-MEM ceiling of 1024 bytes; this figure does not represent total device RAM in a hardware implementation)."*
2. **Benchmark Resource Accounting Specification (`experiments/BENCH-01A/BENCH_01A_RESOURCE_ACCOUNTING_SPEC.md:24`):**
   > *"`R2-MEM`: $\le 1{,}024\text{ Bytes}$ (calibrated against Track B's deployment memory of $\approx 200$–$400$ Bytes)."*
   The metric was defined as the persistent state allocated to model parameters and history buffers, excluding stack frames and hardware FPU registers.
3. **Compaction Milestone (`RESOURCE_COMPACTION_RESOURCE_REPORT.md:77`):**
   > *"Gate 11A (Legacy R2-MEM): Persistent RAM $\le 1024\text{ Bytes}$ | PASS ($976 \le 1024$) | RECOVERED: C1 restores historical 1-KiB compliance."*
   Here, the model with $976\text{ B}$ mean persistent state passed Gate 11A, even though its peak transient memory was higher.
4. **Shadow-Rent Gate Milestone (`LEBRE-V0.2-SHADOW-RENT-GATE-01`):**
   - Introduced a new, much stricter gate: **Gate 3: Peak Working SRAM $\le 1024\text{ B}$**.
   - Gate 3 accounts for hardware FPU registers ($8\text{ B}$), circular buffer state, candidate parameter vectors, and concurrent dual-structure occupancy.
   - Under Gate 3, $S_0$ reached $1064\text{ B}$ (Hardware FPU) and $1072\text{ B}$ (Conservative Stack), failing Gate 3.

---

## 3. The Conflation in the Multirate Report

The parent report conflated:
- **Historical Metric (R2-MEM):** Mean persistent model-state RAM (Ceiling: $1024\text{ B}$).
- **New Experimental Gate (Gate 3):** Peak instantaneous working SRAM (Ceiling: $1024\text{ B}$).

Under the historical R2-MEM metric:
- $M_0$ Mean Persistent Bytes: $973.85\text{ B}$ (Observed) / $976.32\text{ B}$ (Ledger) $\le 1024\text{ B} \implies$ **PASS**.
- $M_1$ Mean Persistent Bytes: $970.34\text{ B}$ (Observed) / $974.18\text{ B}$ (Ledger) $\le 1024\text{ B} \implies$ **PASS**.

Under the Shadow-Rent Peak Working SRAM Gate:
- $M_1$ Peak Working SRAM: $1064\text{ B}$ (Hardware FPU) / $1072\text{ B}$ (Stack) $> 1024\text{ B} \implies$ **FAIL**.

---

## 4. Reconciled Verdict

- **`HISTORICAL_R2_MEMORY_METRIC`:** `MEAN_PERSISTENT_BYTES`
- **`HISTORICAL_R2_MEMORY_STATUS`:** **`PASS`**
- **`PEAK_WORKING_1K_STATUS`:** **`FAIL`**

These two metrics must not be conflated into a single monolithic memory status. LEBRE $M_1$ complies with its historical v0.1 R2 persistent memory contract, but fails the stricter v0.2 peak-working SRAM constraint.
