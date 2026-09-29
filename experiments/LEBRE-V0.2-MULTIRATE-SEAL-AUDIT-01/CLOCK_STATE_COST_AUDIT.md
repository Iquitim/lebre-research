# Algorithmic Clock State and Compute Cost Audit

**Study:** `LEBRE-V0.2-MULTIRATE-SEAL-AUDIT-01`  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  

---

## 1. Audited Statement

The parent report asserts:
> *"Modular integer clocks cost $0\text{ FP/step}$ and $0\text{ persistent bytes}$."*

---

## 2. Implementation Inspection

In `scratch/run_v02_multirate_experiments.py`, lines 340–350:
```python
is_probe_step = (self.step_count % self.K_probe == 0)
is_obs_step = (self.step_count % self.K_obs == 0)
is_learn_step = (self.step_count % self.K_learn == 0)
is_arb_step = (self.step_count % self.K_arb == 0)
```

### Resource Breakdown:
1. **Floating-Point Operations (FP/step):**
   - The modulo operations are evaluated strictly on integer quantities (`self.step_count` and integer constants $K$).
   - **`CLOCK_FP_COST = 0.0`**
2. **Integer Arithmetic Operations (INT ops/step):**
   - Each clock condition requires one integer modulo/division and one comparison.
   - For 4 to 6 decoupled stages, this consumes **$6.0\text{ to }12.0\text{ INT ops/step}$**.
   - These are integer ALU operations on an ARM Cortex-M or RISC-V core. While not FP, they are not "free".
   - **`CLOCK_INTEGER_OP_COST = 6.0`**
3. **Persistent Memory State (Bytes):**
   - The variable `self.step_count` already exists in canonical LEBRE v0.1 as a required 32-bit (4-byte) stream sequence counter in the base filter.
   - The modular checks do NOT instantiate new state variables or counter arrays.
   - **`CLOCK_ADDITIONAL_PERSISTENT_BYTES = 0`**

---

## 3. Audit Classification

- The claim that clocks cost $0\text{ FP}$ and $0\text{ additional persistent bytes}$ is **empirically and statically verified**.
- However, for complete accounting integrity, the integer ALU burden ($6\text{ INT ops/step}$) is documented to prevent conflating "zero FP" with "zero cost".
