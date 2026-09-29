# Final Search Candidate Freeze: Compacted Sparse Frontier ($M_1^*$)

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Phase 2 Candidate Selection and Freeze  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Status:** **FROZEN AND SEALED PRIOR TO FINAL CONFIRMATORY EVALUATION**  

---

## 1. Candidate Selection Decision

Following Phase 0 utilization auditing (140 runs), Phase 1 locality auditing (4,915 active delay instances), and Phase 2 DEV candidate screening (840 runs), **Candidate $C_{1d}$ (`C1_H32_B4`)** is selected as the primary confirmatory compacted architecture:

```text
FROZEN CONFIRMATORY SEARCH CANDIDATE: M1* = C1_H32_B4
```

### 1.1 Rationales for Selection over Alternates:
1. **Dominant Predictive Performance:**
   - On the 14-task DEV benchmark suite ($N=10$, seeds $1801..1810$), $C_{1d}$ achieved a mean NMSE of **$0.3135$** ($\Delta\text{NMSE} = +0.0164$ vs continuous $R_0$).
   - This outperforms the dense multirate reference $R_1$ ($\text{NMSE} = 0.3268$, $\Delta\text{NMSE} = +0.0297$), reducing predictive error by **$+0.0133$ NMSE** through aggressive suppression of spurious probation noise.
2. **Superior Delay Discovery & Recall:**
   - Achieved **$76.31\%$** true delay promotion recall on DEV, vs $66.55\%$ for $R_1$ and $38.10\%$ for disqualified $C_2$.
   - Slashes maximum silence interval to **$80\text{ steps}$** (vs $160\text{ steps}$ for $R_1$).
3. **RAM Compaction & Invariant Compliance:**
   - Active search table memory is strictly bounded to **$192\text{ bytes}$** ($32\text{ slots} \times 6\text{ bytes}$), achieving a **$63.6\%$ reduction** relative to the dense grid ($330\text{ bytes}$ FP16 / $802\text{ bytes}$ state).
   - **Zero dense 160-cell arrays** are instantiated or retained in RAM.
4. **Disqualification of Alternate Families:**
   - $C_2$ (Hierarchical Coarse-to-Fine) suffered catastrophic structural blindness on discrete delays ($3.64\%$ locality capture, NMSE = $0.3563$, pure-lag $\Delta\text{NMSE} = +0.1227$).
   - $C_{1a}, C_{1c}$ ($B=2$) suffered from longer revisit intervals ($160\text{ steps}$), yielding lower discovery recall ($63.0\% - 63.3\%$).

---

## 2. Frozen Architectural Specifications for $M_1^*$

| Parameter / Dimension | Frozen Specification | Semantic Role |
| :--- | :--- | :--- |
| **Search Space Policy** | `ROTATING_SPARSE_FRONTIER` | Compaction mechanism |
| **Frontier Capacity ($H$)** | 32 slots | Total RAM-allocated slots |
| **Tracking Partition ($H_{\text{track}}$)** | $\le 24$ slots ($75\%$) | High-evidence & active probation tracking |
| **Exploration Partition ($H_{\text{explore}}$)** | $\ge 8$ slots ($25\%$) | Procedural circular traversal of inactive coordinates |
| **Batch Probe Size ($B$)** | 4 cells | Cells interrogated per probe tick |
| **Probe Clock ($K_{\text{probe}}$)** | 2 stream steps | Decimated sensing cadence (frozen parent clock) |
| **Probe Computation** | $4\text{ FLOPs}$ / probed cell | EWMA cross-correlation & energy update |
| **Direct Probe Cost** | $8.00\text{ FP/step}$ | Sustained probe throughput |
| **Data Precision** | FP16 (IEEE 754 half) | 2 bytes/accumulator |
| **Peak Search RAM** | $192\text{ bytes}$ | Total volatile memory for search accumulators |
| **Dense Array Retention** | **0 bytes** | Zero dense arrays allocated |

---

## 3. Pre-Simulation Cryptographic Signatures

The code, protocols, and data models are cryptographically sealed prior to initiating confirmatory runs:

```text
115d47f48f625910e74af4f97d549f68b6cdf636c5c094f83369c7a704a999cd  scratch/run_v02_correlation_search_compaction.py
79605e6727c3c6579efc33465c8b06607c2b1fc4b24fb3a36df93b2841dfe07b  scratch/run_phase0_phase1_audit.py
61123be3d83dd1000157a4e1b28bf261dadad3c76b43e4b60c61571dc858af3f  scratch/run_phase2_dev_screening.py
9ab865aea3727bcb3d9f82303788157e7e1bc836fc7412e9cc8894a5b9cdcc28  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/CORRELATION_SEARCH_PROTOCOL.md
2ad0ef49cb8c3f04f10a75ed65cd8bd8dd99e69c02169bcf88c211230581dbca  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/CORRELATION_SEARCH_PREREGISTRATION.md
80744ea687a462bd4a705869e5da65ae821a2af3c4586327cd32f43b0af611ae  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SPARSE_FRONTIER_SPEC.md
087ea859b8a380f0c2e4ddcda3730f1c1a3177dbe0d41d0108bf916ad37c43b7  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/HIERARCHICAL_SEARCH_SPEC.md
5daa40a8e13bee280649527c2d2c0a244d1b8a47c0b83bf4a3434365543c8cda  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SEARCH_SPACE_COMPUTE_MODEL.md
00ef8011b89734dcd6fa9e67ab30c1682ed2daf76dcfe9abd0d258fbce93b72e  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SEARCH_SPACE_MEMORY_MODEL.md
9237b6aca71542b8f9d9a6cc820ed42349df8efb9b968449e9318975ba4f6b0b  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/HIERARCHICAL_SEARCH_ELIGIBILITY.md
```

---

## 4. Confirmatory Evaluation Plan (Phases 3 & 4)

- **Cohort Size:** $N = 30$ independent streams.
- **Seed Range:** `1811..1840` (Certified zero collisions).
- **Benchmark Tasks:** Full 14-task suite ($I_1..I_{14}$, 6,000 steps each).
- **Total Confirmatory Runs:** $30\text{ seeds} \times 14\text{ tasks} \times 3\text{ models} = 1,260\text{ runs}$.
- **Comparators:**
  1. $R_0$: Continuous dense correlation reference ($K=1, H=160$).
  2. $R_1$: Dense multirate reference ($K_{\text{probe}}=2, B=1, H=160$).
  3. $M_1^*$: Frozen compacted sparse frontier ($K_{\text{probe}}=2, B=4, H=32$).
- **Success Criteria:** Evaluated strictly against the preregistered hypotheses (H1..H7).
