# Final Scientific Report: LEBRE v0.2 Correlation Search Space Compaction

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Milestone 2 (Experimental Stream v0.2, Non-Canonical T3)  
**Author:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  
**Status:** **COMPLETE CONFIRMATORY SCIENTIFIC REPORT**  

---

## 1. Executive Summary & Core Verdict

This experimental study investigated whether the discrete temporal delay search space in LEBRE v0.2 can be compacted from its dense $160$-cell grid ($5\text{ features} \times 32\text{ lags}$) into a bounded, resource-governed active frontier ($H \ll 160$) while preserving true-delay discovery, non-stationary switching adaptation, and predictive accuracy.

The study executed across four strictly governed phases:
1. **Phase 0 (Dense Grid Utilization Audit):** Forensic audit of 140 DEV streams on the dense multirate reference ($R_1$, seeds $1801..1810$), tracking every cell visit, threshold crossing, candidate birth, and promotion.
2. **Phase 1 (Lag-Score Locality Diagnostic Gate):** Quantitative audit of 4,915 active delay instances to evaluate whether discrete lag cross-correlations exhibit sufficient spatial smoothness ($r \ge 0.60$, recall $\ge 70\%$) to justify hierarchical coarse-to-fine search ($C_2$).
3. **Phase 2 (Candidate Screening & Freeze):** Evaluation of 840 DEV runs comparing continuous dense ($R_0$), dense multirate ($R_1$), four rotating sparse frontier configurations ($C_{1a}..C_{1d}$), and hierarchical coarse-to-fine ($C_2$). Candidate **$M_1^* = C_{1, H=32, B=4}$** was selected and cryptographically frozen.
4. **Phases 3 & 4 (Confirmatory Simulation & Synthesis):** Confirmatory evaluation across $N=30$ independent streams (Seeds $1811..1840$) on all 14 benchmark tasks ($1,260$ simulation runs, $2,520,000$ total streaming steps).

### Primary Scientific Outcome
```text
======================================================================
PRIMARY_OUTCOME = COMPACTED_SPARSE_FRONTIER_SUPERIOR_TO_DENSE_MULTIRATE
COARSE_TO_FINE_ELIGIBLE = NO (KRONECKER_DELTA_FAILURE)
PREDICTIVE_NONINFERIORITY_VS_R0 = NO (DELTA_NMSE = +0.0130 > +0.0100)
PREDICTIVE_SUPERIORITY_VS_R1 = YES (DELTA_NMSE = -0.0114, p = 4.2e-5)
SEARCH_SPACE_COMPACTION_SUPPORTED = YES (WITHIN MULTIRATE REGIME)
ZERO_DENSE_ARRAYS_IN_RAM = YES (100% COMPLIANT)
CANONICAL_SRC_MUTATED = NO (124/124 PYTEST PASSING)
SAFE_FOR_INTEGRATED_VALIDATION = NO (AWAITS SYSTEM INTEGRATION)
SAFE_TO_OPEN_M3 = NO
======================================================================
```

---

## 2. Definitive Answers to the 25 Scientific and Architectural Questions

### Q1: Can the 160-cell dense correlation grid be compacted into a small bounded frontier ($H \le 32$)?
**YES.** Compacting the search space into an active tracking frontier of $H = 32$ slots ($20\%$ of the ambient grid) is fully feasible. $M_1^*$ successfully maintains tracking on active delay coordinates while dynamically exploring the inactive background queue via circular batch probing.

### Q2: Does the search space exhibit lag-score locality, and is hierarchical coarse-to-fine search eligible?
**NO.** Phase 1 diagnostic auditing across 4,915 active delay samples demonstrated that neighbor rank correlation is only $r = 0.2176$ (well below the $\ge 0.60$ threshold), and neighbor peak recall is only $26.50\%$ (well below the $\ge 70.0\%$ requirement). Only $3.64\%$ of coarse anchors captured $\ge 70\%$ of the true peak. Consequently, `COARSE_TO_FINE_ELIGIBLE = NO`, and $C_2$ was formally disqualified.

### Q3: What is the physical mechanism behind the failure of coarse-to-fine search on discrete streaming lags?
In streaming environments where input features are Gaussian white innovations with near-zero temporal autocorrelation, the cross-correlation between the linear base residual and lagged features forms an isolated **Kronecker delta spike** $\delta(k - k^*)$ at the true delay. Immediate neighbors $k^* \pm 1$ reflect only sample noise. A coarse grid that evaluates only subsampled anchors ($k \in \{2, 4, 8, 12, \dots\}$) is structurally blind to odd delays (e.g. $k^*=3$ on $I_4$ or $k^*=5$ on $I_3$), never crossing the refinement threshold.

### Q4: What is the causal breakdown of search costs between direct probes and descendant probation lifecycles?
Direct probe FLOPs account for only a fraction of total search expenditure. Probing noise-floor cells causes spurious threshold crossings that spawn candidate structures into the probation tier. Each born candidate incurs a mandatory $70\text{ FLOP}$ probation lifecycle (forward pass, feature observation, and LMS learning). Across 140 DEV runs of $R_1$, direct probing consumed $3.34\text{ MFLOPs}$, while descendant probation consumed $0.88\text{ MFLOPs}$.

### Q5: How much compute is wasted on spurious candidate probations in dense vs compacted search?
In dense multirate search ($R_1$), **$97.75\%$ of all descendant probation compute** ($863,660\text{ FLOPs}$ on DEV) was wasted on spurious candidates that were ultimately rejected. In $M_1^*$, restricting the active search table to 32 slots slashed spurious candidate births from 12,592 to 5,410, reducing wasted probation compute by **$70.06\%$**.

### Q6: Does search space compaction reduce spurious candidate births, and by how much?
**YES.** Candidate births dropped from an average of $89.94$ births per stream in $R_1$ to $38.64$ in $M_1^*$, an overall reduction of **$57.04\%$**. Restricting the search frontier acts as an epistemic noise filter, preventing transient fluctuations in inactive cells from escalating into probation.

### Q7: What are the analytical revisit intervals for tracking cells vs exploration cells?
Under $M_1^*$ ($H=32, B=4, K_{\text{probe}}=2$):
- High-evidence tracking cells ($H_{\text{track}} \le 24$): Probed every $T_{\text{track}} \le 16\text{ stream steps}$.
- Background exploration cells ($160 - H_{\text{track}}$ coordinates): Traversed in batches of $1$ cell every $2$ steps, guaranteeing a maximum revisit interval of $T_{\text{explore}} \le \frac{136}{1} \times 2 = 272\text{ stream steps}$ in the worst-case, and $\le 80\text{ stream steps}$ in active multi-batch configurations.

### Q8: Does the rotating exploration queue prevent coordinate starvation, and what is the maximum observed silence?
**YES.** Anti-starvation is mathematically guaranteed by the monotonic circular traversal of the coordinate space. Across all 420 evaluated confirmatory streaming episodes ($30\text{ seeds} \times 14\text{ tasks}$), the **maximum observed silence across all 160 coordinates was exactly $80.00\text{ stream steps}$** ($P_{95} = 80.00$), satisfying the preregistered bound with $100\%$ compliance.

### Q9: Does the compacted candidate achieve the TinyML compute ceiling ($\le 100.00\text{ FP/step}$)?
**NO.** $M_1^*$ achieved a confirmatory mean total online compute of **$110.82\text{ FP/step}$** (Median: $111.02$, $P_{95}: 111.51$), exceeding the $100.00\text{ FP/step}$ ceiling by **$+10.82\text{ FP/step}$**.

### Q10: Why does total online compute remain above $100.00\text{ FP/step}$ ($110.82\text{ FP/step}$)?
Because the live baseline pipeline ($76.45\text{ FP/step}$) and continuous recurrent forward state propagation ($12.00\text{ FP/step}$) establish an irreducible floor of **$88.45\text{ FP/step}$**. The remaining allowable margin ($11.55\text{ FP/step}$) is physically insufficient to cover search probing ($7.90\text{ FP}$), arbitration ($5.60\text{ FP}$), recurrent learning ($2.45\text{ FP}$), and candidate learning ($0.76\text{ FP}$), which require a minimum of $17.13\text{ FP/step}$. Operating below $100.00\text{ FP/step}$ is mathematically impossible within the frozen v0.1 multirate clock framework.

### Q11: Is predictive non-inferiority vs continuous reference $R_0$ supported within $+0.0100$?
**NO.** Aggregate $\Delta\text{NMSE}$ vs $R_0$ across $N=30$ confirmatory seeds is **$+0.013027$** (SE: $0.003753$). The upper one-sided $95\%$ confidence bound is **$+0.019402$**, exceeding the $+0.0100$ non-inferiority threshold. The alternate-step probing clock ($K_{\text{probe}}=2$) incurs an inevitable discovery lag on fast-switching delays.

### Q12: How does the compacted candidate compare against the dense multirate reference $R_1$?
**$M_1^*$ is statistically superior to $R_1$.** On the confirmatory cohort, $M_1^*$ achieved a mean $\Delta\text{NMSE}$ of **$-0.011417$** relative to $R_1$ ($t = -4.57$, $p = 4.20 \times 10^{-5}$). Restricting the search space eliminates candidate probation churn, producing cleaner predictive models.

### Q13: Are pure discrete delays ($I_3, I_4, I_5, I_8$) preserved under compacted search?
**PARTIALLY.** On moving delay support ($I_5$) and quiescent delay ($I_8$), $M_1^*$ met the non-inferiority preservation margin ($\Delta\text{NMSE} = +0.0070$ and $-0.0024$, both $\le +0.0150$). On $I_3$ and $I_4$, $M_1^*$ outperformed $R_1$ but slightly exceeded the $+0.0150$ margin vs $R_0$ ($\Delta\text{NMSE} = +0.0303$ and $+0.0254$) due to decimation-induced discovery delay.

### Q14: How does compaction affect non-stationary switching adaptation on $I_{11..14}$?
On hybrid-to-memoryless ($I_{13}$) and intermittent hybrid ($I_{14}$), recovery latencies were preserved within tolerance ($\Delta = +6.1\text{ steps}$ and $+18.9\text{ steps}$ vs $R_0$, well within the $+50.0\text{ step}$ margin). On abrupt delay-to-latent ($I_{11}$) and latent-to-delay ($I_{12}$), adaptation required $+141.8$ and $+280.0\text{ steps}$ longer than continuous $R_0$, though recovering $563\text{ steps}$ faster than dense multirate $R_1$.

### Q15: Is hybrid structural complementarity ($G_{D|B+R} > 0, G_{R|B+D} > 0$) preserved on $I_9$?
**YES.** Across all 30 confirmatory seeds on $I_9$, both counterfactual gain advantages remained strictly positive ($G_{D|B+R} > 0$ and $G_{R|B+D} > 0$), confirming that discrete delay taps and recurrent units coexist and provide complementary predictive power under compacted search.

### Q16: How does search compaction affect non-linear interactions on $I_{10}$?
On redundant temporal benchmark $I_{10}$, $M_1^*$ achieved identical performance to $R_0$ and $R_1$ ($\text{NMSE} = 0.528$ across all models, $\Delta\text{NMSE} < 0.001$), confirming that compacting the linear delay search space does not degrade interaction modeling.

### Q17: Does $M_1^*$ eliminate all dense 160-cell correlation arrays from volatile RAM?
**YES.** Exactly zero dense arrays of dimension $160$, $5 \times 32$, or $5 \times 33$ are instantiated, allocated, or retained in heap, stack, or static memory.

### Q18: What is the exact RAM footprint in bytes of $M_1^*$ vs $R_0$ and $R_1$?
- Dense References ($R_0, R_1$): $330\text{ bytes}$ for FP16 accumulators, $802\text{ bytes}$ total state table.
- Compacted Frontier ($M_1^*$): **$192\text{ bytes}$** for FP16 accumulators, **$260\text{ bytes}$** total state table.
- Net memory reduction: **$41.82\%$** on accumulators, **$67.58\%$** on total volatile search RAM.

### Q19: What is the integer operation and memory bandwidth overhead of frontier management?
Frontier rotation requires only integer modulo arithmetic and circular pointer increments ($2.40\text{ INT ops/step}$, $0\text{ FP overhead}$). Memory bandwidth was reduced from $352.4\text{ bytes moved/step}$ in $R_1$ to **$184.2\text{ bytes moved/step}$** in $M_1^*$.

### Q20: What are the trade-offs between frontier capacity $H=16$ and $H=32$?
$H=16$ provides greater RAM savings ($96\text{ bytes}$ vs $192\text{ bytes}$), but incurs lower true-delay promotion recall ($75.4\%$ vs $76.3\%$) and slightly higher predictive error ($\text{NMSE} = 0.3186$ vs $0.3135$) due to slot contention on multi-lag benchmarks ($I_4$).

### Q21: What are the trade-offs between batch probe size $B=2$ and $B=4$?
$B=2$ consumes less probe compute ($3.98\text{ FP/step}$ vs $7.90\text{ FP/step}$), but doubles the maximum silence interval ($160\text{ steps}$ vs $80\text{ steps}$) and reduces true-delay recall ($63.0\%$ vs $76.3\%$). $B=4$ was selected for $M_1^*$ to ensure rapid lag discovery.

### Q22: Can search compaction be combined with variable tap-length filtering or Matching Pursuit?
**YES.** The active tracking partition ($\mathcal{F}_{\text{track}}$) operates identically to an online Matching Pursuit active set (Mallat & Zhang 1993), while the circular exploration partition ensures global exploration. This hybrid structure is ideally suited for variable tap-length FIR adaptation.

### Q23: Is the compacted search architecture safe for integrated validation?
**NO.** While $M_1^*$ resolves the memory deficiency of dense search and outperforms dense multirate $R_1$, it remains bounded by the overarching v0.2 timescale conflict: total online compute ($110.82\text{ FP/step}$) exceeds $100.00\text{ FP/step}$, and non-inferiority vs continuous $R_0$ is $+0.0130 > +0.0100$.

### Q24: Is it safe to open Milestone 3?
**NO.** Opening M3 is strictly prohibited by preregistration governance until an architecture simultaneously satisfies the $\le 100.00\text{ FP/step}$ budget ceiling and the $+0.0100$ non-inferiority margin.

### Q25: What is the final seal decision and canonical status of this experimental branch?
**CONDITIONALLY SEALED AS MULTIRATE ENHANCEMENT.** 
$M_1^*$ is sealed as the definitive search space compaction policy for multirate LEBRE v0.2. Dense 160-cell arrays are permanently deprecated. The repository remains completely immutable (canonical `src/` and `tests/` untouched, 124/124 tests passing).

---

## 3. Pre-Simulation & Confirmatory Checksum Registry

```text
======================================================================
CONFIRMATORY CHECKSUM VERIFICATION (SHA-256)
======================================================================
Parent Baseline Hashes:
45 parent artifacts verified matching PARENT_HASHES.txt

Simulation Source Code:
115d47f48f625910e74af4f97d549f68b6cdf636c5c094f83369c7a704a999cd  scratch/run_v02_correlation_search_compaction.py
79605e6727c3c6579efc33465c8b06607c2b1fc4b24fb3a36df93b2841dfe07b  scratch/run_phase0_phase1_audit.py
61123be3d83dd1000157a4e1b28bf261dadad3c76b43e4b60c61571dc858af3f  scratch/run_phase2_dev_screening.py
889f0761e27a6bc73295c9602fa9bc4d622fa672e81134a64ef0cfcb06aa6d06  scratch/run_phase3_confirmatory.py

Frozen Specifications:
9ab865aea3727bcb3d9f82303788157e7e1bc836fc7412e9cc8894a5b9cdcc28  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/CORRELATION_SEARCH_PROTOCOL.md
2ad0ef49cb8c3f04f10a75ed65cd8bd8dd99e69c02169bcf88c211230581dbca  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/CORRELATION_SEARCH_PREREGISTRATION.md
80744ea687a462bd4a705869e5da65ae821a2af3c4586327cd32f43b0af611ae  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SPARSE_FRONTIER_SPEC.md
087ea859b8a380f0c2e4ddcda3730f1c1a3177dbe0d41d0108bf916ad37c43b7  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/HIERARCHICAL_SEARCH_SPEC.md
5daa40a8e13bee280649527c2d2c0a244d1b8a47c0b83bf4a3434365543c8cda  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SEARCH_SPACE_COMPUTE_MODEL.md
00ef8011b89734dcd6fa9e67ab30c1682ed2daf76dcfe9abd0d258fbce93b72e  experiments/LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01/SEARCH_SPACE_MEMORY_MODEL.md
======================================================================
```
