# Memory Lifetime Audit & Simultaneity Mapping

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01/microcorrection`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Errata Reference:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Focus Inquiry:** Deterministic Resolution of Transient Workspace Lifetime, Hardware Register vs. Stack SRAM Allocation, and Peak Working Memory Arithmetic  
**Author:** Independent Skeptical Senior Reviewer  
**Date:** September 22, 2026  

---

## 1. Executive Summary & Problem Formulation

In `SHADOW_RENT_SEAL_ERRATA-01` (`MEMORY_METRIC_DICTIONARY.md`, Table 4, and `generate_shadow_rent_seal_errata.py`), the reconciled memory ledger reported:

- `MAX_OCCUPIED_PERSISTENT`: $S_0 = 1064\text{ B}$, $S_1 = 904\text{ B}$, $S_2 = 1068\text{ B}$, $S_3 = 1080\text{ B}$.
- `TRANSIENT_WORKSPACE_BYTES`: $8\text{ B}$ for all configurations.
- `PEAK_WORKING_BYTES`: $S_0 = 1064\text{ B}$, $S_1 = 904\text{ B}$, $S_2 = 1068\text{ B}$, $S_3 = 1080\text{ B}$.

The report defined:
$$\text{PEAK\_WORKING\_BYTES} = \text{MAX\_OCCUPIED\_PERSISTENT} + \text{TRANSIENT\_WORKSPACE}$$
yet the reported values for Peak Working Bytes were **identical** to Max Occupied Persistent Bytes, completely omitting the $+8\text{ Bytes}$ transient term from the arithmetic sum.

This audit deterministically resolves:
1. Exactly where the $8\text{ B}$ transient workspace resides physically (CPU/FPU registers vs. stack SRAM vs. heap).
2. Whether the transient workspace is active simultaneously with maximum persistent state occupancy.
3. The exact, uncompromised value of `PEAK_WORKING_SRAM_BYTES` under both embedded hardware register semantics and conservative stack SRAM frame semantics.

---

## 2. Component Inventory & Lifetime Decomposition

The LEBRE $T_3$ runtime maintains eight distinct classes of memory during online streaming execution:

```
+-------------------------------------------------------------------------------------------------------------------------------+
| Memory Class                      | Physical Location    | Lifetime / Scope               | Bytes (S0) | Bytes (S2) | Bytes (S3) |
+-------------------------------------------------------------------------------------------------------------------------------+
| 1. Static Persistent Base         | Global BSS / Heap    | Boot to stream termination     |   904 B    |   904 B    |   904 B    |
| 2. Scheduler Persistent State     | Global BSS / Heap    | Boot to stream termination     |     0 B    |     4 B    |    16 B    |
| 3. Dynamic Active Lag Taps        | Preallocated Slab    | Active while promoted (varies) | 0 - 64 B   | 0 - 64 B   | 0 - 64 B   |
| 4. Dynamic Provisional Candidates | Preallocated Slab    | Active during probation (varies| 0 - 48 B   | 0 - 48 B   | 0 - 48 B   |
| 5. Dynamic Active Recurrent Unit  | Preallocated Slab    | Active while promoted (varies) | 0 - 48 B   | 0 - 48 B   | 0 - 48 B   |
| 6. Temporary FP32 Casts & Scratch | FPU Regs / Call Stack| Sub-step probe loop iteration  |     8 B    |     8 B    |     8 B    |
| 7. Prediction Scalars             | CPU/FPU Registers    | Step lifetime (reused)         |    16 B    |    16 B    |    16 B    |
| 8. Dot-Product Accumulators       | FPU Accumulator Regs | Inner loop execution           |     8 B    |     8 B    |     8 B    |
+-------------------------------------------------------------------------------------------------------------------------------+
```

---

## 3. Detailed Lifetime & Simultaneity Map

Below is the step-by-step execution timeline for a single timestep $t$ of `IntegratedLEBREModel.step()` / `GovernedLEBREModel.step()`, detailing the active memory footprint at each phase:

```mermaid
gantt
    title LEBRE Step Memory Lifetime & Simultaneity Map
    dateFormat  X
    axisFormat %s
    section Persistent State
    Static Base (904 B)            :active, 0, 100
    Scheduler State (0-16 B)       :active, 0, 100
    Dynamic Recruited State (0-160 B) :active, 0, 100
    section Live Inference & Update
    Input Standardization x_norm   :crit, 5, 15
    Base Prediction y_base         :crit, 15, 25
    Active Tap Prediction y_lag    :crit, 25, 35
    Active Rec Forward y_rec       :crit, 35, 45
    Prequential Residual e_live    :crit, 45, 55
    Base LMS Weight Update         :crit, 55, 65
    Causal Scaler Update           :crit, 65, 75
    section Shadow Exploration
    Shadow Recurrent Forward       :done, 75, 85
    Counterfactual Loss Evaluation :done, 80, 90
    Correlation Grid Probing (8 B) :active, 85, 95
```

### 3.1 Peak State Co-Occurrence (Simultaneity Proof)
- The maximum dynamic state ($\mathcal{D}_{\max} = 160\text{ Bytes}$: 4 active delay taps $\times 16\text{ B} = 64\text{ B}$, 3 provisional candidates $\times 16\text{ B} = 48\text{ B}$, and 1 active recurrent unit $= 48\text{ B}$) is sustained during complex hybrid tracking episodes (such as Tasks $I_9$ and $I_{14}$).
- During these exact timesteps, when the model is in structural state `BOTH` with maximum structural recruitment:
  - If shadow exploration is awake (`is_shadow_awake == True`), Stage 7 (Probing) executes.
  - In Stage 7, two correlation pairs are probed per step.
  - For each probe, `val_fp32 = float(self.corr_grid[i, k])` (4 Bytes IEEE 754 float32) and `upd_fp32 = 0.95 * val_fp32 + 0.05 * (e * c)` (4 Bytes float32) are instantiated simultaneously.
- **Proof of Simultaneity:** The transient workspace variables exist **at the exact same micro-second** that the maximum persistent memory ($1064\text{ B}$ for $S_0$, $1068\text{ B}$ for $S_2$, $1080\text{ B}$ for $S_3$) is resident in memory.
- Therefore, the transient workspace **does not alias or reuse already-counted persistent memory**. It represents distinct physical operands.

---

## 4. Hardware Allocation Analysis: CPU/FPU Registers vs. Stack SRAM

The critical architectural question is whether these $8\text{ Bytes}$ occupy physical **SRAM** (system memory) or reside strictly within **CPU/FPU hardware registers**.

### 4.1 Target Embedded Architecture: ARM Cortex-M4F / Cortex-M33 (Hardware FPU)
In an embedded deployment targeting an MCU with a hardware single-precision Floating Point Unit (VFPv4 / FPv5, e.g., STM32F4 / NRF5340):
1. The processor provides 32 dedicated 32-bit hardware floating point registers (`s0` through `s31`).
2. When compiling the probing loop with standard embedded optimization (`-O2` / `-O3`):
   ```assembly
   // Probing inner loop assembly representation:
   VLDR.16    S0, [R4, R2]         // Load 16-bit half from corr_grid into S0 (transient cast to FP32)
   VCVT.F32.F16 S0, S0             // Hardware FP16 -> FP32 expansion in register
   VMUL.F32   S1, S2, S3           // S1 = e_for_probe * c_val (evaluated in register)
   VMLA.F32   S1, S0, S4           // S1 = 0.95 * S0 + 0.05 * S1 (FPU fused multiply-accumulate)
   VCVT.F16.F32 S0, S1             // Hardware FP32 -> FP16 rounding in register
   VSTR.16    S0, [R4, R2]         // Store updated 16-bit half back to SRAM corr_grid
   ```
3. **Register Audit Conclusion:**  
   In hardware with an FPU, `val_fp32` resides in `S0`, `upd_fp32` resides in `S1`, and the accumulator resides in `S2`.  
   **Zero bytes of stack SRAM are pushed or popped.** The values exist purely in the processor's register file, which is architecturally and physically distinct from system SRAM.
   - `TRANSIENT_REGISTER_BYTES = 8`
   - `TRANSIENT_STACK_SRAM_BYTES = 0`
   - `TRANSIENT_HEAP_BYTES = 0`
   - `PEAK_WORKING_SRAM_BYTES = MAX_OCCUPIED_PERSISTENT + 0 = MAX_OCCUPIED_PERSISTENT`.

### 4.2 Alternative Architecture: Software Emulation / Conservative Stack Frame
If LEBRE is deployed on a resource-constrained microcontroller lacking a hardware FPU (e.g. ARM Cortex-M0+ running software floating-point emulation), or under an unoptimized ABI calling convention where subroutines reserve local stack frames:
1. The compiler must allocate local stack memory on the system stack (`SP - 8`) to hold `val_fp32` and `upd_fp32` across soft-float library calls (`__aeabi_fadd`, `__aeabi_fmul`).
2. **Stack Audit Conclusion:**  
   Under software float emulation or formal ABI stack frame allocation:
   - `TRANSIENT_REGISTER_BYTES = 0`
   - `TRANSIENT_STACK_SRAM_BYTES = 8`
   - `TRANSIENT_HEAP_BYTES = 0`
   - `PEAK_WORKING_SRAM_BYTES = MAX_OCCUPIED_PERSISTENT + 8`.

---

## 5. Reconciled Memory Ledger & Disaggregated Values

To eliminate ambiguity, both architectural implementations are fully reported:

```
+--------------------------------------------------------------------------------------------------------------------+
| Architecture Variant / Metric        | S0_CONTINUOUS | S1_SHADOW_OFF | S2_PERIODIC (K=5) | S3_EVENT_TRIGGERED      |
+--------------------------------------------------------------------------------------------------------------------+
| STATIC_PREALLOCATED_BYTES            |     904 B     |     904 B     |       908 B       |       920 B             |
| MEAN_OCCUPIED_PERSISTENT_BYTES       |   976.32 B    |    904.00 B   |     980.32 B      |     992.32 B            |
| MAX_OCCUPIED_PERSISTENT_BYTES        |    1064 B     |     904 B     |      1068 B       |      1080 B             |
+--------------------------------------------------------------------------------------------------------------------+
| [PRIMARY] Hardware FPU Register Model:                                                                             |
| TRANSIENT_REGISTER_BYTES             |       8 B     |       0 B*    |         8 B       |         8 B             |
| TRANSIENT_STACK_SRAM_BYTES           |       0 B     |       0 B     |         0 B       |         0 B             |
| TRANSIENT_HEAP_BYTES                 |       0 B     |       0 B     |         0 B       |         0 B             |
| PEAK_WORKING_SRAM_BYTES              |    1064 B     |     904 B     |      1068 B       |      1080 B             |
+--------------------------------------------------------------------------------------------------------------------+
| [SECONDARY] Conservative Stack Frame Model:                                                                        |
| TRANSIENT_REGISTER_BYTES             |       0 B     |       0 B     |         0 B       |         0 B             |
| TRANSIENT_STACK_SRAM_BYTES           |       8 B     |       0 B*    |         8 B       |         8 B             |
| TRANSIENT_HEAP_BYTES                 |       0 B     |       0 B     |         0 B       |         0 B             |
| PEAK_WORKING_SRAM_BYTES              |    1072 B     |     904 B     |      1076 B       |      1088 B             |
+--------------------------------------------------------------------------------------------------------------------+
* In S1, probing is disabled by protocol; zero transient registers or stack bytes are allocated.
```

---

## 6. Audit Finding on Gate 3 Compliance

Regardless of whether `PEAK_WORKING_SRAM_BYTES` is evaluated as $1064 / 1068 / 1080\text{ B}$ (Hardware Register Model) or $1072 / 1076 / 1088\text{ B}$ (Stack Frame Model):

1. **Strict 1-KiB Peak Gate ($\le 1024\text{ Bytes}$):**  
   - $S_0$: **FAIL** ($1064\text{ B} > 1024\text{ B}$ or $1072\text{ B} > 1024\text{ B}$).
   - $S_1$: **PASS** ($904\text{ B} \le 1024\text{ B}$).
   - $S_2$: **FAIL** ($1068\text{ B} > 1024\text{ B}$ or $1076\text{ B} > 1024\text{ B}$).
   - $S_3$: **FAIL** ($1080\text{ B} > 1024\text{ B}$ or $1088\text{ B} > 1024\text{ B}$).
2. **Mean Occupied Memory Gate ($\le 1024\text{ Bytes}$):**  
   - All configurations **PASS** ($976.32\text{ B}, 904.00\text{ B}, 980.32\text{ B}, 992.32\text{ B}$).
3. **Proposed 2-KiB Memory Class ($\le 2048\text{ Bytes}$):**  
   - All configurations **PASS**.

The arithmetic ambiguity between the narrative report and the data files is thus completely resolved.
