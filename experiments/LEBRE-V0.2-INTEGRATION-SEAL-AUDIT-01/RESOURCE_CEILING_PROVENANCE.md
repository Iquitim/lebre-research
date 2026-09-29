# Forensic Provenance Audit: Resource Ceiling Evolution (1024 B vs. 2048 B)

**Study Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Subject:** Historical Lineage and Mutation Analysis of Gate 11 Memory Ceiling  
**Auditor:** Independent Skeptical Senior Reviewer  
**Classification:** `POST_RESULT_GATE_RELAXATION`  

---

## 1. Executive Forensic Summary

Audit Question B demands an exact determination of:
> **WHEN, WHERE, WHY, and BEFORE OR AFTER RESULT INSPECTION the 2048-byte criterion entered the protocol.**

The forensic investigation reveals:
1. **The Historical Baseline (LEBRE v0.1):** The normative R2 memory ceiling was strictly locked at **1024 persistent bytes** across all specification documents (`bench_01_locked_config.json`, `LEBRE_CONSTANT_TRACEABILITY.md`, `LEBRE_SPEC_FREEZE_AUDIT.md`).
2. **The Preregistered Integration Plan:** Prior to executing experiments, both `LEBRE_V0_2_RESOURCE_MODEL.md` and `LEBRE_V0_2_INTEGRATION_PROTOCOL.md` explicitly preregistered the **1024-byte ceiling** for Gate 11 ("total persistent memory must not exceed 1024 Bytes").
3. **The Implementation Defect / Inflation:** The analytical resource model estimated persistent memory at $540$ Bytes (live) and $716$ Bytes (live + shadow), assuming an $80$-byte compact correlation grid. However, the simulation code in `scratch/run_v02_integration_experiments.py` allocated `self.corr_grid = np.zeros((5, 33), dtype=np.float32)`, which consumed $660$ Bytes. Added to the ring buffer ($332$ B), scaler ($80$ B), base weights ($40$ B), recurrent unit ($48$ B), shadow unit ($48$ B), and arbitrator ($64$ B), the total persistent state reached **$1,306$ Bytes**.
4. **The Timing of Gate Mutation:** The substitution of `RAM <= 2048 Bytes` occurred **POST-CONFIRMATORY RESULT INSPECTION**. It was introduced during the drafting of `LEBRE_V0_2_INTEGRATION_DECISION.md` and `LEBRE_V0_2_FINAL_REPORT.md` to convert what would have been a Gate 11 failure ($1,306\text{ B} > 1,024\text{ B}$) into a reported "PASS".
5. **Regulatory Conclusion:** Gate 11 compliance under the preregistered 1024-byte ceiling is **FAILED**. The 2048-byte limit constitutes an unpreregistered post-hoc relaxation (`POST_HOC_GATE_RELAXATION`).

---

## 2. Chronological Provenance Trail

```
[2026-09-19] LEBRE v0.1 Specification Freeze
  │  File: docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md:49
  │  Requirement: "R2-MEM Ceiling: 1024.0 Bytes | Standard requiring persistent model RAM <= 1024 bytes."
  │
  ▼
[2026-09-20 T09:00] LEBRE v0.2 Integration Resource Model Authored
  │  File: experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_RESOURCE_MODEL.md:84
  │  Statement: "R2-MEM Ceiling (1024 Bytes): Total persistent RAM footprint is 540 Bytes (live)
  │             and 716 Bytes (including full shadow candidate buffers), strictly COMPLIANT with the 1024-byte ceiling."
  │
  ▼
[2026-09-20 T09:30] LEBRE v0.2 Integration Protocol Locked
  │  File: experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_INTEGRATION_PROTOCOL.md:71
  │  Text: "GATE 11 — Resource Feasibility: Mean live compute on single-memory regimes must not exceed
  │        100 FP FLOPs/step; total persistent memory must not exceed 1024 Bytes."
  │
  ▼
[2026-09-20 T10:00] Execution of Confirmatory Experiments (N=30 seeds)
  │  Script: scratch/run_v02_integration_experiments.py
  │  Observation: Output column 'persistent_bytes' = 1306 Bytes across all seeds.
  │  Root Cause: corr_grid allocated as 660-byte float32 matrix rather than compact 80-byte structure.
  │
  ▼
[2026-09-20 T10:11] Drafting of Integration Decision & Final Report
  │  File: experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_INTEGRATION_DECISION.md:38
  │  Text: "GATE 11: Single-regime FLOPs <= 100 or RAM <= 2048 B | RAM = 1306 <= 2048 B: PASS"
  │  File: experiments/LEBRE-V0.2-INTEGRATION-DESIGN-01/LEBRE_V0_2_FINAL_REPORT.md:Table 6
  │  Text: "Single-regime FLOPs <= 100, RAM <= 2048 B | PASS | RAM = 1,306 <= 2048 B"
  │  Status: Silent post-hoc gate relaxation without registered protocol amendment.
```

---

## 3. Forensic Breakdown of Memory Allocation

The table below disaggregates the actual measured persistent footprint of $T_3$ in `scratch/run_v02_integration_experiments.py`:

| Subsystem Component | Code Source | Modeled Size (`RESOURCE_MODEL.md`) | Actual Implemented Size | Discrepancy Cause |
|:---|:---|:---:|:---:|:---|
| `CausalStandardScaler` | `scaler.d * 16` | 40 B | 80 B | $D=5$, Mean (40B) + Var (40B) float64 |
| `FP16HistoryRingBuffer` | `D * (L_max + 1) * 2 + 2` | 332 B | 332 B | Exact FP16 match ($5 \times 33 \times 2 + 2$) |
| `LinearBasePredictor` | `base.d * 8` | 40 B | 40 B | Exact float64 match ($5 \times 8$) |
| **Shadow Correlation Grid** | `corr_grid.nbytes` | **80 B** | **660 B** | **Allocated as full $5 \times 33$ float32 matrix!** |
| Active Tap Metadata | `len(active_taps) * 16` | 48 B (4 taps) | 0–64 B | 16 B per active tap ($i, k, w, R$) |
| Provisional Candidate Metadata | `len(prov_cands) * 16` | 48 B (3 cands) | 0–48 B | 16 B per candidate |
| Recurrent Unit (Active) | `active_rec.get_memory_bytes()` | 48 B | 48 B | $s, \alpha, b, c, p_\alpha, p_b$ |
| Recurrent Unit (Shadow) | `shadow_rec.get_memory_bytes()` | 48 B | 48 B | $s, \alpha, b, c, p_\alpha, p_b$ |
| Capacity Arbitrator Registers | Fixed constant | 32 B | 64 B | EMA gain filters and hysteresis |
| **Total Persistent Memory** | | **716 B** | **1,306 B** | **+$590$ B implementation bloat** |

### Critical Root-Cause Analysis:
The analytical model in `LEBRE_V0_2_RESOURCE_MODEL.md` (line 39) assumed that candidate probing ($M=2$) would maintain an 80-byte active grid. Instead, the simulation script instantiated the full $5 \times 33 = 165$-cell grid in `float32` ($165 \times 4 = 660$ Bytes). 
Had the correlation grid been implemented as an 8-bit integer array (`int8`, 165 Bytes) or as a sparse hash map of 10 probed pairs (80 Bytes), the total memory would have been:
$$\text{Compacted Memory} = 1,306 - 660 + 80 = \mathbf{726 \text{ Bytes}} \le 1,024 \text{ Bytes}$$
However, the audit cannot evaluate hypothetical unexecuted code. Under the sealed code, memory is $1,306$ Bytes.

---

## 4. Formal Regulatory Classification

1. **Under `LEGACY_R2_CLASS` ($\le 1,024$ Bytes):**
   $$\text{Compliance Verdict: } \mathbf{FAIL} \quad (1,306\text{ B} > 1,024\text{ B})$$
2. **Under `PROPOSED_V0_2_2KB_CLASS` ($\le 2,048$ Bytes):**
   $$\text{Compliance Verdict: } \mathbf{PASS} \quad (1,306\text{ B} \le 2,048\text{ B})$$
3. **Preregistration Status of 2048 B:**
   $$\mathbf{UNPREREGISTERED\ (POST\text{-}HOC\ RELAXATION)}$$

The parent study erred scientifically by silently updating Gate 11 from 1024 B to 2048 B rather than acknowledging that the experimental prototype exceeded the legacy 1024 B ceiling and formulating a formal governance request for a 2KB resource tier.
