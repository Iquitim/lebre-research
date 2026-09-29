# Search Space Memory Model

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Phase 0 Analytical Modeling  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  

---

## 1. Scope and Target Architecture Constraints

LEBRE is engineered for resource-governed edge streaming inference and TinyML microcontrollers (e.g., ARM Cortex-M4 / Cortex-M33 with $\le 64\text{ KB}$ SRAM).

A central design deficiency of the parent architecture ($R_0$ and $R_1$) is the allocation and retention of a **dense $160$-cell correlation state array** in volatile RAM, regardless of how few cells contain actual predictive signal.

This document formally specifies:
1. The byte-level memory accounting of the dense grid references ($R_0, R_1$);
2. The compacted sparse frontier state representation ($C_1$);
3. Formal proof that $C_1$ retains **zero dense 160-cell arrays in RAM**.

---

## 2. Memory Layout and Data Precision Specifications

All correlation accumulators and tracking statistics conform to the following data precision rules:
- **Lag Index / Feature Index:** `uint8` ($1\text{ byte}$ each, range $0..255$).
- **Correlation Accumulator ($\hat{C}_{i,k}$):** `float16` ($2\text{ bytes}$, IEEE 754 half-precision).
- **Residual Energy Accumulator ($\hat{E}_{\text{base}}$):** `float16` ($2\text{ bytes}$).
- **Feature Energy Accumulator ($\hat{E}_{X_{i,k}}$):** `float16` ($2\text{ bytes}$).
- **Slot Visit Counter / Age:** `uint8` ($1\text{ byte}$).

---

## 3. Byte Accounting Across Architectures

### 3.1 Dense Correlation Matrix ($R_0$ and $R_1$)
The dense baseline maintains state accumulators for all $N_{\text{cells}} = 5 \times 32 = 160$ pairs simultaneously:
- Correlation accumulator table: $160 \times 2\text{ bytes} = 320\text{ bytes}$.
- Feature energy accumulator table: $160 \times 2\text{ bytes} = 320\text{ bytes}$.
- Residual energy accumulator: $1 \times 2\text{ bytes} = 2\text{ bytes}$.
- Dense visit / tracking metadata: $160 \times 1\text{ byte} = 160\text{ bytes}$.
- **Total Search Space RAM Footprint ($R_0, R_1$):** **$802\text{ bytes}$**.

### 3.2 Rotating Sparse Frontier ($C_1$)
Instead of instantiating all 160 cells, $C_1$ dynamically maintains a bounded sparse table of exactly $H$ slots in RAM:

Each slot structure contains:
```c
struct SparseFrontierSlot {
    uint8_t  feature_idx;   // 1 byte
    uint8_t  lag_idx;       // 1 byte
    uint8_t  is_active;     // 1 byte (bitfield flag: tracking vs explore)
    uint8_t  age;           // 1 byte (steps since promotion/reset)
    float16_t corr_acc;     // 2 bytes (EWMA cross-correlation)
    float16_t energy_acc;   // 2 bytes (EWMA feature energy)
}; // Total: 8 bytes per active slot
```

Auxiliary rotation control state:
- `uint16_t explore_cursor`: $2\text{ bytes}$ (circular queue pointer over the $160$ virtual coordinates).
- `float16_t shared_res_energy`: $2\text{ bytes}$ (shared linear base residual energy).
- Active slot map (lookup table of size $H$): $H \times 1\text{ byte}$.

#### Total Search RAM Footprint for $C_1$:
$$\text{RAM}(C_1) = H \times (8 + 1) + 4\text{ bytes} = 9H + 4\text{ bytes}$$

| Configuration | Active Slots ($H$) | Slot Array | Lookup Map | Control State | Total Search RAM | Memory Reduction vs. Dense |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dense Grid ($R_1$)** | 160 | 800 bytes | N/A | 2 bytes | **802 bytes** | Baseline ($0.0\%$) |
| **$C_1$ ($H=32$)** | 32 | 256 bytes | 32 bytes | 4 bytes | **292 bytes** | **$63.59\%$ reduction** |
| **$C_1$ ($H=16$)** | 16 | 128 bytes | 16 bytes | 4 bytes | **148 bytes** | **$81.55\%$ reduction** |

---

## 4. Invariant Verification: Elimination of Dense Memory Footprint

### Formal Invariant:
$$\text{Allocated Cells in RAM} \le H \ll 160$$

### Proof of Compliance:
1. In $C_1$, at no point in initialization, execution, or candidate spawning is an array of dimension $160$, $5 \times 32$, or $5 \times 33$ allocated in heap, stack, or static memory.
2. The virtual coordinate space $(i, k) \in \{0..4\} \times \{1..32\}$ is indexed procedurally via integer arithmetic:
   $$\text{pair}(\text{cursor}) = (\lfloor \text{cursor} / 32 \rfloor, (\text{cursor} \pmod{32}) + 1)$$
   requiring exactly zero array storage.
3. High-evidence tracking cells are stored exclusively in the $H$-element array. When an exploration slot encounters evidence exceeding threshold, it is promoted into the tracking partition of the $H$-slot array; if the tracking partition is full, the lowest-evidence tracking slot is evicted back to the virtual queue.
4. Therefore, the physical RAM footprint is bounded strictly by $O(H)$, satisfying the zero dense correlation array invariant.
