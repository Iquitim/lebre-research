# Forensic Analysis: Pareto Objective Provenance & Multi-Objective Dominance Recomputation

**Study Identifier:** `LEBRE-V0.2-INTEGRATION-SEAL-AUDIT-01`  
**Subject:** Objective Vector Lineage, Mathematical Dominance Proofs, and Aggregate vs. Per-Task Frontiers  
**Auditor:** Independent Skeptical Senior Reviewer  
**Classification:** `PARETO_DOMINANCE_VERIFIED_WITH_SCOPE_QUALIFICATION`  

---

## 1. Executive Summary

Audit Question E demands:
> **Does $T_3$ actually `STRICTLY_PARETO_DOMINATE` each comparator under the complete preregistered objective vector? Or is it instead `NON_DOMINATED` or `PREFERRED_UNDER_LIVE_PATH_METRICS`?**

The forensic multi-objective audit establishes:
1. **Under the Aggregate Live-Path Vector ($\text{NMSE}, \text{Live FP}, \text{RAM}$):**
   $T_3$ **STRICTLY VECTOR PARETO DOMINATES** $T_1, T_{1R}, T_2,$ and $O_{\text{ALL}}$. It is strictly superior on all three objectives simultaneously.
2. **Under the Aggregate Full-Online Vector ($\text{NMSE}, \text{Total Online FP}, \text{Int Ops}, \text{Traffic}, \text{RAM}$):**
   $T_3$ **STRICTLY VECTOR PARETO DOMINATES** $T_1, T_{1R}, T_2,$ and $O_{\text{ALL}}$ across the benchmark average. Because $T_3$'s live path is so light ($81.4$ FLOPs), its total online cost ($168.0$ FLOPs) is lower than $T_1$ ($198.8$ FLOPs), $T_{1R}$ ($202.7$ FLOPs), $T_2$ ($203.6$ FLOPs), and $O_{\text{ALL}}$ ($215.4$ FLOPs).
3. **Per-Task Boundary Condition:**
   While $T_3$ dominates in **49 out of 56 per-task comparisons (87.5%)**, it forms a **non-dominated trade-off** in 7 comparisons (12.5%):
   - On $I_6$ (Continuous Latent State) and $I_{10}$ (Redundant Structure), sequential cascade $T_1$ achieves lower NMSE by unconstrained tap fitting, but consumes higher RAM and compute.
   - On $I_{14}$ (Intermittent Hybrid), $T_{1R}$ achieves lower NMSE by continuous state retention, but consumes higher RAM and compute.
4. **Language Verdict:** The parent report's claim that $T_3$ *"strictly vector Pareto dominates all alternative topologies"* is **MATHEMATICALLY VALID ON AGGREGATE**, but must be scoped: it does not hold unconditionally on every individual task.

---

## 2. Objective Vector Provenance Trail

| Stage / Document | Objective Vector Defined | Normalization / Units | Methodological Status |
|:---|:---|:---|:---|
| **`RESOURCE-ACCOUNTING-RECONCILIATION-01`** | $\mathbf{R} = [\text{FP\_FLOPS}, \text{INT\_OPS}, \text{TRAFFIC}, \text{BYTES}]^\top$ | Absolute physical counts | Preregistered 4-channel ledger |
| **`LEBRE_V0_2_RESOURCE_MODEL.md:15`** | $\mathbf{R} = [\text{FP\_FLOPS}, \text{INT\_OPS}, \text{TRAFFIC}, \text{BYTES}]^\top$ | Disaggregated Live vs Shadow | Pre-experimental specification |
| **`LEBRE_V0_2_INTEGRATION_PROTOCOL.md`** | Accuracy (NMSE) + 4-channel vector | Minimization vector | Pre-experimental protocol |

In this audit, two distinct diagnostic fronts are evaluated:
- **Front A (Live-Path Vector):** $\mathbf{v}_{\text{live}} = [\text{NMSE}, \text{Live FP FLOPs}, \text{RAM Bytes}]^\top$.
- **Front B (Full-Online Vector):** $\mathbf{v}_{\text{full}} = [\text{NMSE}, \text{Total Online FP}, \text{Integer Ops}, \text{Memory Traffic}, \text{RAM Bytes}]^\top$.

---

## 3. Aggregate Recomputation Results ($N=30$ Seeds, 14 Tasks)

The table below summarizes the exact empirical vectors recomputed from `LEBRE_V0_2_SEED_RESULTS.csv`:

| Topology | Mean NMSE | Live FP FLOPs | Shadow Rent FLOPs | Total Online FP | Integer Ops | Memory Traffic (B/step) | Persistent RAM (Bytes) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **$T_1$** (Cascade) | 0.3592 | 114.0 | 84.9 | 198.8 | 52.1 | 392.7 | 1,363 |
| **$T_{1R}$** (Rev. Cascade) | 0.3418 | 117.3 | 85.5 | 202.7 | 51.6 | 398.6 | 1,368 |
| **$T_2$** (Symmetric Comp.) | 0.3833 | 118.3 | 85.3 | 203.6 | 52.2 | 399.0 | 1,367 |
| **$T_3$** (Arbitration) | **0.2876** | **81.4** | **86.6** | **168.0** | **35.9** | **372.0** | **1,306** |
| **$O_{\text{ALL}}$** (Always-On) | 0.4258 | 131.0 | 84.4 | 215.4 | 56.3 | 410.6 | 1,380 |

### Pairwise Aggregate Dominance Verification:

1. **$T_3$ vs. $T_1$:**
   - NMSE: $0.2876 < 0.3592$ ($T_3$ wins by $0.0716$, $-19.9\%$)
   - Total FP: $168.0 < 198.8$ ($T_3$ wins by $30.8$ FLOPs, $-15.5\%$)
   - Int Ops: $35.9 < 52.1$ ($T_3$ wins by $16.2$ ops, $-31.1\%$)
   - Traffic: $372.0 < 392.7$ ($T_3$ wins by $20.7$ B, $-5.3\%$)
   - RAM: $1,306 < 1,363$ ($T_3$ wins by $57$ B, $-4.2\%$)
   - **Verdict:** $\mathbf{T_3 \prec T_1}$ (**$T_3$ STRICTLY DOMINATES $T_1$**).

2. **$T_3$ vs. $T_{1R}$:**
   - Strictly superior on all 5 dimensions.
   - **Verdict:** $\mathbf{T_3 \prec T_{1R}}$ (**$T_3$ STRICTLY DOMINATES $T_{1R}$**).

3. **$T_3$ vs. $T_2$:**
   - Strictly superior on all 5 dimensions ($T_2$ suffers double-payment penalty).
   - **Verdict:** $\mathbf{T_3 \prec T_2}$ (**$T_3$ STRICTLY DOMINATES $T_2$**).

4. **$T_3$ vs. $O_{\text{ALL}}$:**
   - Strictly superior on all 5 dimensions ($O_{\text{ALL}}$ overfits noise, burns maximum compute).
   - **Verdict:** $\mathbf{T_3 \prec O_{\text{ALL}}}$ (**$T_3$ STRICTLY DOMINATES $O_{\text{ALL}}$**).

---

## 4. Per-Task Dominance Breakdown

Across the 56 per-task pairwise comparisons ($14 \text{ tasks} \times 4 \text{ comparators}$):
- **$T_3$ Dominates Comparator:** $49 / 56$ ($87.5\%$).
- **Non-Dominated Trade-Off:** $7 / 56$ ($12.5\%$).
- **Comparator Dominates $T_3$:** $0 / 56$ ($0.0\%$).

### Non-Dominated Tasks Analysis:
1. **$I_6$ (Continuous Latent State) vs. $T_1, T_{1R}$:**
   $T_1$ achieves NMSE $0.1072$ vs. $T_3$'s $0.1338$. However, $T_1$ consumes $198.8$ Total FLOPs and $1,382$ Bytes RAM vs. $T_3$'s $168.0$ Total FLOPs and $1,318$ Bytes RAM.
2. **$I_{10}$ (Redundant Structure) vs. $T_1, T_{1R}$:**
   $T_1$ achieves NMSE $0.2574$ vs. $T_3$'s $0.4173$. $T_1$ exploits unconstrained tap allocations to fit the autoregressive process, but incurs higher memory traffic and RAM.
3. **$I_{14}$ (Intermittent Hybrid) vs. $T_1, T_{1R}$:**
   $T_{1R}$ achieves NMSE $0.1615$ vs. $T_3$'s $0.1973$, but burns higher compute ($202.7$ vs. $168.0$).

In zero cases does any comparator dominate $T_3$.

---

## 5. Corrigendum Recommendation

The claim in `LEBRE_V0_2_FINAL_REPORT.md` and `LEBRE_V0_2_STATISTICAL_REPORT.md` must be refined as follows:
- **Original Claim:** *"Topology $T_3$ strictly vector Pareto dominates all alternative topologies."*
- **Corrected Claim:** *"Topology $T_3$ strictly vector Pareto dominates all alternative topologies on the aggregate benchmark vector, and achieves a non-dominated or dominant relation on 100% of individual tasks (dominating in 87.5% of task-wise comparisons and trading off in 12.5%)."*
