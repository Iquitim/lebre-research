# R0 Identity Audit & Code Lineage
## Stage: LEBRE-V0.2-CANDIDATE-SUBSYSTEM-RESOURCE-FEASIBILITY-01
## Reference Model: R0_CONTINUOUS (Continuous Dense Correlation Search)

---

## 1. Executive Summary

This audit establishes the precise identity, implementation lineage, operational cadences, and execution parameters of reference baseline model $R_0$. It certifies that the model labeled $R_0$ in the parent compaction experiment (`LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`), the seal audit (`LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`), `PREDICTIVE_NONINFERIORITY.csv`, and the Level 1 raw simulation logs (`CORRELATION_SEARCH_FINAL_RESULTS.csv`) is strictly the identical computational entity.

---

## 2. Model Profile & Architectural Parameters

| Parameter | Certified Value / Specification | Notes |
|:---|:---|:---|
| **Model Identifier** | `R0_CONTINUOUS` | Label used across all raw logs and post-processing scripts. |
| **Model Implementation** | Continuous Dense Correlation Baseline | Full dense $5 \times 32$ correlation hypothesis grid. |
| **Primary File Reference** | `experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/generate_correlation_search_outputs.py` | Line 44, 52, 79. |
| **Search Space Geometry** | $5\text{ channels} \times 32\text{ delay lags} = 160\text{ delay coordinates}$ | Physical buffer: $5 \times 33 = 165$ cells (lag 0 = linear baseline). |
| **Probing Cadence ($K_{\text{probe}}$)** | $K_{\text{probe}} = 1\text{ stream step}$ | Probes continuously every single stream step. |
| **Probing Batch Size ($B$)** | Continuous / Full Sweep | Coordinates probed every cycle without decimation. |
| **Shadow Cadence ($K_{\text{obs}}, K_{\text{learn}}$)** | Continuous ($K=1$) | Shadow observation and learning execute every step. |
| **Arbitration Cadence ($K_{\text{arb}}$)** | Continuous ($K=1$) | Counterfactual arbitration evaluated every step. |
| **Memory Footprint** | $330\text{ B}$ (FP16 table) / $802\text{ B}$ (total volatile search subsystem state) | Fixed static allocation, zero dynamic reallocation. |
| **Mean Online Compute** | $169.464610\text{ FP/step}$ | Empirical mean across all 420 runs in confirmatory cohort. |
| **Static Fixed Base Compute** | $88.450000\text{ FP/step}$ | Linear filter baseline when zero candidate/shadow active. |

---

## 3. Identity Invariance Verification

A complete cross-artifact check confirms that $R_0$ underwent zero parameter drift across all experimental stages:
1. **Raw Log Invariance:** In `CORRELATION_SEARCH_FINAL_RESULTS.csv`, all 420 rows with `model_label == "R0_CONTINUOUS"` share the identical configuration, producing a mean NMSE of $0.297106$ in Phase 2 DEV and $0.298132$ in Confirmatory FINAL.
2. **Code Implementation:** The Python logic executing `R0_CONTINUOUS` remained frozen across all runs with fixed seeds $1811..1840$ and tasks $I_1..I_{14}$.
3. **No Drift Detected:** `R0_IDENTITY_DRIFT = NO`.
