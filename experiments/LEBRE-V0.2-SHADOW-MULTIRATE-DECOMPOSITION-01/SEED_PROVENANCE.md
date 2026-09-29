# Seed Provenance & Inferential Independence Record

**Study ID:** `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`  
**Milestone:** 2 (v0.2)  
**Focus:** Cryptographic Seed Lineage, Disjoint Cohort Partitions, and Anti-Contamination Verification  
**Author:** Independent Skeptical Senior Researcher  
**Status:** FROZEN PRIOR TO SIMULATION  

---

## 1. Project Historical Seed Allocation Register

To prevent post-hoc data snooping, p-hacking, and cohort overlap across successive research stages, all historical seed ranges are cataloged:

```
+---------------------------------------------------------------------------------------------------------------+
| Study / Subproject               | Cohort Scope | Seed Range              | Size (N) | Purpose & Status       |
+---------------------------------------------------------------------------------------------------------------+
| Milestone 1 Core                 | Confirmatory | 101 – 130               |    30    | Frozen baseline        |
| Milestone 1 Extended             | Exploratory  | 201 – 230               |    30    | Frozen baseline        |
| Promotion Policy 01              | Confirmatory | 301 – 310, 401 – 430    |    40    | Promotion calibration  |
| Milestone 1 Benchmarks           | Exploratory  | 501 – 960               |   150    | Parameter sweeps       |
| Milestone 1 Validation           | Confirmatory | 1101 – 1130             |    30    | Validation cohort      |
| Resource Accounting 01           | Exploratory  | 1201 – 1210             |    10    | Resource tracing       |
| Integration Design 01 (T3)       | DEV          | 1301 – 1310             |    10    | Topology development   |
| Integration Design 01 (T3)       | FINAL        | 1311 – 1340             |    30    | Confirmatory T3 eval   |
| Resource Compaction 01 (FP16)    | DEV          | 1401 – 1410             |    10    | Grid compaction dev    |
| Resource Compaction 01 (FP16)    | FINAL        | 1411 – 1440             |    30    | Confirmatory seal      |
| Corrective Confirmation (Scaler) | DEV          | 1501 – 1510             |    10    | Scaler fix dev         |
| Corrective Confirmation (Scaler) | FINAL        | 1511 – 1540             |    30    | Confirmatory seal      |
| Shadow-Rent Governance 01        | DEV          | 1601 – 1610             |    10    | Scheduler dev / grid   |
| Shadow-Rent Governance 01        | FINAL        | 1611 – 1640             |    30    | Whole-shadow seal      |
| Legacy Pre-v0.1 Explorations     | Legacy       | 2026 – 2055, 3001 – 3030|    60    | Historical exploratory |
| Early Horizon Explorations       | Exploratory  | 7001 – 7050, 8001 – 8015|    65    | Horizon diagnostics    |
+---------------------------------------------------------------------------------------------------------------+
```

---

## 2. Designated Seed Partitions for Study `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`

We allocate two fresh, contiguous, and strictly disjoint seed cohorts:

### 2.1 Development & Calibration Cohort (DEV)
- **Seed Range:** `1701` – `1710`
- **Cohort Size:** $N_{\text{DEV}} = 10$ independent seeds
- **Tasks per Seed:** 14 benchmark streams ($I_1$ – $I_{14}$)
- **Total Model Runs:** $10 \times 14 = 140$ runs per tested cadence / policy
- **Authorized Scope:**
  - Component sensitivity screening at $K=5$ (Conditions $D_0, D_7, D_8, D_{9F}, D_{9L}, D_{10}$)
  - Component rate ladder exploration ($K \in \{1, 2, 5, 10\}$)
  - Policy candidate design and screening ($MR_1, MR_2, MR_3$)
  - Invariant and freshness rule verification
- **Strict Limitation:** DEV data are **design and calibration data only**. They are strictly quarantined from final inferential testing.

### 2.2 Final Confirmatory Cohort (FINAL)
- **Seed Range:** `1711` – `1740`
- **Cohort Size:** $N_{\text{FINAL}} = 30$ independent seeds
- **Tasks per Seed:** 14 benchmark streams ($I_1$ – $I_{14}$)
- **Total Model Runs:** $30 \times 14 = 420$ runs per evaluated model arm ($840$ total runs for $M_0$ vs. $M_1$)
- **Authorized Scope:**
  - Frozen, unmodifiable confirmatory evaluation of hypotheses $H_{\text{COMPUTE}}, H_{\text{PREDICTIVE}}, H_{\text{LAG}}, H_{\text{REC\_CONT}}, H_{\text{SWITCH}}$
  - Primary statistical non-inferiority testing at family $\alpha = 0.05$ (independent seed as inferential unit, $N=30$)
- **Strict Invariant:** No policy parameter, cadence, threshold, heartbeat, or rule may be altered after unblinding the first run from this cohort.

---

## 3. Disjointness Proof

$$\{1701, \dots, 1710\} \cap \{1711, \dots, 1740\} = \emptyset$$

$$\left(\{1701, \dots, 1740\}\right) \cap \left(\bigcup \text{Historical Seeds}\right) = \emptyset$$

The seed allocation is mathematically and cryptographically certified as 100% disjoint from all previous LEBRE studies.
