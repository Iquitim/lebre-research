# LEBRE Architecture Specification v0.1 — Formal Freeze Record

**Architecture Name:** LEBRE  
**Canonical Expansion:** Lifecycle-governed Evidence-Based Resource Evolution  
**Specification Version:** 0.1  
**Status:** `FROZEN_WITH_SCOPE_LIMITS`  
**Freeze Stage:** `LEBRE-SPEC-FREEZE-01`  
**Freeze Date:** September 19, 2026  
**Governance Authority:** Project Codinome Lebre Scientific Direction  

---

## 1. Provenance & Identity Statement

The architecture specified herein was empirically developed, benchmarked, and validated under the pre-publication research codename **"Track B Single-State Organization"** (*Codinome Lebre*). Upon successful completion and reconciliation of experimental protocols **M1**, **M2**, **BENCH-01B**, and **CAR-01**, the architecture was formally designated **LEBRE** (*Lifecycle-governed Evidence-Based Resource Evolution*).

All historical references to Track B across internal logs, calibration matrices, and benchmark summaries represent legitimate and verified developmental provenance for LEBRE v0.1.

---

## 2. Scientific Contribution & Evidence Classification

- **Architecture Evidence Classification:** `VALIDATED_WITH_SCOPE_LIMITS`
- **Primary Scientific Contribution:**
  - `RESOURCE_GOVERNED_STRUCTURAL_LIFECYCLE`: An agile online structural learning architecture that treats observable features, temporal delay taps, and recurrent internal state as cost-bearing adaptive computational structures governed by a unified, evidence-driven five-state lifecycle under strict micro-resource budgets.
- **Supporting Contributions:**
  1. `TWO_TIMESCALE_QUIESCENT_RETENTION`: Decouples instantaneous signal energy from structural necessity ($U_{\text{ret}}$), ensuring retention across extended Poisson silence intervals.
  2. `POSITIVE_OBSOLESCENCE_ASYMMETRIC_EVICTION`: Governs structural eviction via an asymmetric dual-gate ($U_{\text{ret}} < 0.02$ AND $O_{\text{obs}} > 0.80$, sustained over 30 steps of patience), establishing an empirical cost-loss protection ratio of $\approx 300:1$ against premature eviction.

---

## 3. Implementation Scope & Normative Invariants

LEBRE v0.1 is bounded by the following frozen structural constants:

| Parameter | Symbol | Frozen Value | Implementation Unit | Governed Role |
| :--- | :---: | :---: | :--- | :--- |
| `max_recurrent_states` | $N_{\text{rec}}$ | **1** | `src/models/recurrent.py` | Maximum active recurrent units (scalar recurrence only, $N \le 1$) |
| `max_features` | $K_{\text{max}}$ | **10** | `src/models/linear.py` | Maximum concurrently active linear/lag features |
| `probation_horizon` | $T_{\text{prob}}$ | **50** | `src/controllers/shadow.py` | Steps in isolated shadow probation before promotion decision |
| `promotion_threshold` | $\theta_{\text{promote}}$ | **0.05** | `src/controllers/shadow.py` | Minimum counterfactual MSE reduction required ($> 5\%$) |
| `maturation_age` | $\tau_{\text{mature}}$ | **100** | `src/controllers/lifecycle.py` | Operational steps required to transition from ACTIVE to MATURE |
| `birth_threshold` | $\theta_{\text{birth}}$ | **0.15** | `src/controllers/birth.py` | Smoothed linear residual error required to trigger shadow birth |
| `birth_patience` | $N_{\text{birth}}$ | **30** | `src/controllers/birth.py` | Consecutive steps above threshold required to trigger birth |
| `slow_decay` | $\alpha_{\text{slow}}$ | **0.005** | `src/controllers/retention.py` | Exponential decay factor for structural relevance ($\tau_{1/2} \approx 140$ steps) |
| `retention_threshold` | $\theta_{\text{ret}}$ | **0.02** | `src/controllers/retention.py` | Relevance ceiling below which a unit becomes vulnerable to eviction |
| `obsolescence_threshold` | $\theta_{\text{obs}}$ | **0.80** | `src/controllers/retention.py` | Obsolescence accumulator ceiling required for eviction |
| `eviction_patience` | $N_{\text{pat}}$ | **30** | `src/controllers/lifecycle.py` | Consecutive steps satisfying dual-gate condition before physical eviction |

---

## 4. Benchmark Provenance & Sealed Evidence

- **Protocol:** `BENCH-01B` (Sealed)
- **Evaluation Workloads:** 15 streaming environments (8 synthetic unit tests A1–A8; 5 real-world continuous streams B1–B5: NSW Electricity, Jena Weather Temperature, Gas Dynamic Mixture, Silverbox System ID, Household Active Power).
- **Statistical Power:** 30 independent pseudo-random seeds per workload; 450 total evaluated runs for LEBRE; 6,750 competitive runs across baselines (Sparse Online Linear LMS, RZA-LMS, Cascade Correlation CCN, Minimal GRU, Online ESN, Fast & Deep Resilient RNN).
- **Numerical Stability:** **0.00% divergence rate** (0 divergences in 450 runs).
- **Resource Footprint (Observed):**
  - **Mean Algorithmic Compute:** **90.44 FLOPs/step** (compliant with the $R_2\text{-FLOP} \le 100$ FLOPs/step mean benchmark threshold; transient shadow evaluation peak $\approx 206$ FLOPs/step for 50 steps).
  - **Persistent Model State:** **440.0 Bytes** (compliant with the $R_2\text{-MEM} \le 1024$ Bytes ceiling; excludes C stack, runtime, and I/O ring buffers).
- **Hardware Boundary:** All measurements reflect strict bit-exact software simulation. Physical deployment to bare-metal microcontrollers (ARM Cortex-M) represents unexecuted future work.

---

## 5. Known Empirical Limitations (v0.1 Boundary)

LEBRE v0.1 has well-documented empirical performance frontiers:
1. **Dispersed & Long Delays (Tasks A3, A4):** Dense reservoir networks (ESN) and gated architectures (GRU) outperform scalar recurrence when high-order temporal memory is required without clear linear residual correlation.
2. **Multi-Frequency Nonlinear Dynamics (Task B4 - Silverbox):** High-dimensional continuous nonlinear dynamics benefit from wide randomized projection matrices (Online ESN NMSE 0.91359 vs LEBRE NMSE 0.99320).
3. **Multi-State Recurrence ($N > 1$):** Unvalidated in v0.1; reserved for future milestones.
4. **Non-Regression Paradigms:** Sequence classification, autoregressive language modeling, and reinforcement learning are explicitly out of scope.

---

## 6. Novelty & Milestone Governance Boundaries

- `NOVELTY_CLAIM_READY = NO`: This freeze establishes specification rigor and reproducibility. It does not assert or claim novelty.
- `M3_STATUS = UNOPENED`: Milestone M3 (Multi-State Recurrence) remains unopened. LEBRE v0.1 is strictly a single-state architecture ($N_{\text{rec}} \le 1$).

---

## 7. Frozen Specification Artifacts & SHA-256 Checksums

| Artifact Path | Size (Bytes) | SHA-256 Checksum |
| :--- | :---: | :--- |
| `docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_EN.md` | 40,791 | `088b43e74a14d2b0143eec7a41183dbeaa6ce1d5737d26879e9fda6d9e3a8cba` |
| `docs/architecture/LEBRE_ARCHITECTURE_SPEC_v0.1_PTBR.md` | 44,715 | `7b032604b014f95f4dea1b8a9676bfd44677e0537d10b4b88c8e00adb29a7ee4` |
| `docs/architecture/LEBRE_OVERVIEW_EN.md` | 6,519 | `1e458e95350f072967b559f3d943c940eb62138ae1e0c67b0848e9b339473a86` |
| `docs/architecture/LEBRE_OVERVIEW_PTBR.md` | 7,194 | `fc4b09e1b67ecd61fc197b7696ffcede7516c663533ec29600b8047e5b68b5d1` |
| `docs/architecture/LEBRE_ARCHITECTURE_DIAGRAMS.md` | 21,671 | `7f962fc92f3a10520c3760e4df87037c14f6e41fd3a1c05e60ae4fae648a3f57` |
| `docs/architecture/LEBRE_ARCHITECTURAL_DECISIONS.md` | 10,727 | `4be84990c4c6c400af8bec7cf9a5d1557c5667ec50b41788feb7144dd1d4e440` |
| `docs/architecture/LEBRE_ARCHITECTURE_MANIFEST.yaml` | 4,067 | `3db70e17a959273a3155d5253e8014399ae94597fd764cb0643639ef1fd3b2ce` |
| `docs/architecture/LEBRE_TRACEABILITY_MATRIX.csv` | 3,565 | `67a60f6019de9503a5dcdd36a3e26bbcb545cb100f83c94169e1487893ffd42c` |
| `docs/architecture/LEBRE_CONSTANT_TRACEABILITY.md` | 8,179 | `614800a7c5368e2eadd27f9a3a776f9a6812dd3c37f4328e1367c26d1328011a` |
| `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_EN.pdf` | 1,504,935 | `50168bcadea4ac75afe4f952c624d4a4bfdf1b8b79f252abeb6d74d152df9133` |
| `docs/architecture/pdf/LEBRE_ARCHITECTURE_v0.1_CONDENSED_PTBR.pdf` | 1,515,323 | `3f3d6e5778d3ea24a56f23de8937c20953c672725601c89f2ed08cb2f73a8d46` |
| `docs/architecture/pdf_source/LEBRE_CONDENSED_EN.html` | 758,874 | `f1f8f3b57254dcf4b54bf7a9c55bbda8389f0577c5314b3463d4492eef334673` |
| `docs/architecture/pdf_source/LEBRE_CONDENSED_PTBR.html` | 761,166 | `ffd487007cec461c2caee241cafd644d003584b77c3edd9335dcae8b01c37743` |
| `logo/LEBRE Logo.png` | 491,487 | `bc0f818a90841cccfa659c662bf27c2b9dbbdeb90102e7163caf5cd8124b0f8b` |
| `docs/architecture/assets/diagrams/lebre_high_level_architecture.svg` | 7,371 | `a89960f181173a4ccfc22ff48dca637edaa96c9b3f051dbe964a4688c406b9c0` |
| `docs/architecture/assets/diagrams/lebre_lifecycle.svg` | 6,096 | `0fb2c8d8b9cdc3c3c0e2bd15a60e59790dd9da6b80660b5a65f2b3177f075727` |
| `docs/architecture/assets/diagrams/lebre_data_control_flow.svg` | 5,176 | `8b9bde6e1954c2452d863a85877e472d88bed133a86d7e749e9bab9605c952ae` |
| `docs/architecture/assets/diagrams/lebre_shadow_probation.svg` | 9,425 | `fe909b451a120983c9b5938d281f7cbe790fcf73391fc649d42fc6bf6d1bf164` |
| `docs/architecture/assets/diagrams/lebre_shadow_probation_ptbr.svg` | 9,413 | `5db4b97df96fe9d4d206863ca40bfd91f50c40757d150c20a0fb3475b0a9ae68` |
| `docs/architecture/assets/diagrams/lebre_quiescent_retention.svg` | 3,699 | `2d1af797e0106386858b810e86df7c90ca266d836a2dfddd316dce6742f453fd` |
| `docs/architecture/assets/diagrams/lebre_resource_elasticity.svg` | 5,295 | `7aeb9f1f23f3a69afa2a0a3f46f1dacef912110d52e09bd1dba62a8ab0ed34d7` |
| `docs/architecture/assets/diagrams/lebre_v01_scope.svg` | 3,634 | `2e96472e6c31d3478a1938b72b4ac66e5bcf9a588251b825a59e58bf61a16cce` |
| `docs/architecture/assets/diagrams/lebre_prequential_cycle.svg` | 7,511 | `124e2ee5959d87cbf0c514533bfa57d98405065bcbb88fd793884f609ca4bf26` |

---

## 8. Regression Suite & Source Code Audit

- **Command:** `uv run --with pytest --with pandas --with scipy --with matplotlib --with torch pytest tests/`
- **Result:** **124 passed in 7.56s** (124/124, 100% pass rate).
- **Source Code Status:** `src/` unchanged; zero lines of code modified during documentation and freeze stages.
- **Git State:** Unversioned workspace. Recommended release tag: `v0.1-architecture-spec`.

---

## 9. Immutability & Governance Policy

1. **Version Freezing:** LEBRE v0.1 is an immutable reference specification. Any substantive change to mechanisms, lifecycle rules, constants, or behavioral semantics requires a new version (e.g., v0.2 or v1.0).
2. **Errata Policy:** Post-freeze typographical corrections must be issued as an errata log or minor editorial patch (v0.1.1) and may not silently overwrite these frozen hashes.
3. **M3 Independence:** Subsequent exploration of multi-state recurrence ($N \ge 2$) under Milestone M3 shall proceed under its own experimental protocol without altering LEBRE v0.1.
