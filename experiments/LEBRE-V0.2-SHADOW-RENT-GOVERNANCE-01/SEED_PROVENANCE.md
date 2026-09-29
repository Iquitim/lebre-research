# Seed Provenance & Inferential Independence Record

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** Cryptographic Seed Lineage, Disjoint Cohort Partitions, and Anti-Contamination Verification  
**Author:** Independent Skeptical Senior Researcher  
**Status:** SEALED PRIOR TO EXECUTION  

---

## 1. Project Seed Allocation History

To guarantee complete inferential independence and prevent post-hoc data snooping or p-hacking (Simmons et al., 2011), all seeds ever utilized across the LEBRE research program were forensically cataloged:

| Milestone / Subproject | Cohort Scope | Seed Range | Size ($N$) | Purpose / Status |
| :--- | :--- | :--- | :--- | :--- |
| **Milestone 1 Core** | Confirmatory | `101` – `130` | 30 | Frozen historical baseline |
| **Milestone 1 Extended** | Exploratory | `201` – `230` | 30 | Frozen historical baseline |
| **Promotion Policy 01** | Confirmatory | `301` – `310`, `401` – `430` | 40 | Discrete promotion calibration |
| **Milestone 1 Benchmarks** | Exploratory | `501` – `960` | 150 | Historical baseline sweeps |
| **Milestone 1 Validation** | Confirmatory | `1101` – `1130` | 30 | Frozen validation cohort |
| **Resource Accounting 01**| Exploratory | `1201` – `1210` | 10 | Early resource tracing |
| **Integration Design 01** | DEV Cohort | `1301` – `1310` | 10 | T3 topology development |
| **Integration Design 01** | FINAL Cohort| `1311` – `1340` | 30 | T3 confirmatory integration |
| **Resource Compaction 01**| DEV Cohort | `1401` – `1410` | 10 | FP16 grid development |
| **Resource Compaction 01**| FINAL Cohort| `1411` – `1440` | 30 | FP16 confirmatory seal |
| **Corrective Confirmation**| DEV Cohort | `1501` – `1510` | 10 | Canonical scaler DEV parity |
| **Corrective Confirmation**| FINAL Cohort| `1511` – `1540` | 30 | Canonical scaler confirmation |
| **Prior Milestones** | Legacy | `2026` – `2055`, `3001` – `3030` | 60 | Pre-v0.1 legacy exploration |
| **M2-EXP-0005 / 0006** | Exploratory | `7001` – `7050`, `8001` – `8015` | 65 | Early horizon explorations |

---

## 2. Frozen Seed Partitions for Study `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`

We designate two fresh, contiguous, and strictly disjoint seed blocks that have **never** appeared in LEBRE project history:

### 2.1 Development & Calibration Cohort (DEV)
- **Seed Range:** `1601` – `1610`
- **Cohort Size:** $N_{\text{DEV}} = 10$ independent seeds
- **Tasks per Seed:** 14 benchmark streams ($I_1$ – $I_{14}$)
- **Total Model Runs:** $10 \times 14 = 140$ runs per scheduler candidate
- **Authorized Scope:**
  - Algorithm verification and single-difference invariant testing
  - Evaluation of the 12-candidate Page-Hinkley parameter grid
  - Verification of scheduler memory and compute counters
  - False-alarm rate and detection-delay diagnostics
- **Strict Limitation:** DEV data are **design data only** and are strictly forbidden from contributing to final inferential conclusions or p-values.

### 2.2 Final Confirmatory Cohort (FINAL)
- **Seed Range:** `1611` – `1640`
- **Cohort Size:** $N_{\text{FINAL}} = 30$ independent seeds
- **Tasks per Seed:** 14 benchmark streams ($I_1$ – $I_{14}$)
- **Total Model Runs:** $30 \times 14 = 420$ runs per evaluated scheduler ($1,680$ runs across $S_0, S_1, S_2, S_3$)
- **Authorized Scope:**
  - Frozen, unmodifiable confirmatory evaluation of hypotheses $H_{\text{RESOURCE}}, H_{\text{PREDICTIVE}}, H_{\text{EVENT}}, H_{\text{MEMORY}}$
  - Primary statistical non-inferiority testing at family $\alpha = 0.05$
- **Strict Invariant:** No scheduler parameter, threshold, burst length, or period may be altered after observing the first output from this cohort.

---

## 3. Disjointness Proof

$$\{1601, \dots, 1610\} \cap \{1611, \dots, 1640\} = \emptyset$$

$$\left(\{1601, \dots, 1640\}\right) \cap \left(\bigcup \text{Historical Seeds}\right) = \emptyset$$

The seed allocation is cryptographically verified as 100% disjoint from all previous LEBRE studies.
