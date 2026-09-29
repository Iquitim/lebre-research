# EXP-0003: Experimental Diagnosis and Component Status

## 1. Primary Diagnosis

```
PRIMARY_DIAGNOSIS = FORCED_COVERAGE_REQUIRED
```

### Technical Evidence:
1. **Failure of Pure Exploration/Confirmation (F3)**:
   In F3, allocating all candidate probes to confirmed candidates starved the unconfirmed candidate pool. On Seed 1024, initial probe latency ($T_{\text{wait\_probe}}$) surged to **$205.4$ steps**, leading to the starvation of an omitted true candidate and causing final recall to fail ($96\%$) and Regime-2 MSE to spike to **$0.3289$**.
2. **Success of Forced Coverage Reservation (F4)**:
   Reserving $40\%$ of probe capacity strictly for circular round-robin coverage restored $T_{\text{wait\_probe}}$ to **$5.64$ steps** across all seeds, guaranteed $100\%$ final recall, and enabled the system to reach a Regime-2 MSE of **$0.01638$**, closing **$96.3\%$ of the Oracle MSE gap** at only **$17.2\%$ of Dense compute**.
3. **Conclusion**:
   Causal screening cannot rely solely on confirmation greediness. Broad forced coverage is non-negotiable to prevent true candidate starvation.

---

## 2. Component Status

```
PERSISTENCE_SCORE = KEEP
EXPLORE_CONFIRM = KEEP
FORCED_COVERAGE = KEEP
PROBE_BANK = KEEP
CURRENT_PRIORITY_SCORE = REMOVE
```

### Rationale:
- **`CURRENT_PRIORITY_SCORE` (E1/F1) -> REMOVE**:
  Computes scores over all inactive candidates and sorts all 95 candidates every step, consuming $446.4$ FLOPs/step ($74.2\%$ of Dense compute). Completely unviable for constrained online learning.
- **`PERSISTENCE_SCORE` (F2) -> KEEP**:
  Cheap directional sign consistency ($\ge 75\%$) over minimum evidence count ($n \ge 3$) successfully filters out one-shot noise spikes.
- **`EXPLORE_CONFIRM` (F3/F4) -> KEEP**:
  Two-stage screening with bounded capacity ($C_{\max} = 3$) and explicit drop/timeout conditions concentrates evidence efficiently without permanent noise lock-in, cutting $T_{\text{evidence}}$ by up to $42.9\%$.
- **`FORCED_COVERAGE` (F4) -> KEEP**:
  Reserving $40\%$ of probe budget for oldest-unprobed candidates prevents confirmation sets from monopolizing probe bandwidth and eliminates candidate starvation.
- **`PROBE_BANK` -> KEEP**:
  Guarantees exact matched 10,000 probe budget ($\Delta = 0$) and adjusts $q_t \in [1, 8]$ adaptively based on causal prediction error.

---

## 3. Experiment Status

```
EXP_0003_STATUS = PARTIAL_GO
```

### Evaluation Against Criteria:
- **Regime-2 MSE $\le 0.10$**: **PASSED** ($0.01638 \ll 0.10$).
- **Compute $\le 25\%$ Dense**: **PASSED** ($17.2\% \ll 25\%$).
- **Probe budget unchanged**: **PASSED** ($10,000$ exact, $\Delta = 0$).
- **$T_{\text{evidence}}$ reduction**: **PASSED** ($203.7 \to 153.9$ steps, $24.4\%$ reduction in F4; $116.4$ steps, $42.9\%$ reduction in F3).
- **Full-Support Occupancy $\ge 70\%$**: **FAILED** ($47.70\%$ achieved vs $39.26\%$ in F0).
  The failure to meet the $70\%$ occupancy threshold is directly caused by **post-promotion instability ($T_{\text{post\_promotion}} = 208.8$ steps)**, where promoted true features are displaced before they can grow sufficient weight.

---

## 4. Next Step Taxonomy

```
NEXT = READY_FOR_EXP_0004
```

### Justification Under Section 104 Gate:
All 5 prerequisite conditions for `READY_FOR_EXP_0004` are satisfied:
1. **Causal targeting materially improves occupancy**: Occupancy increased from $39.3\%$ to $47.7\%$ (closing $15.1\%$ of the oracle gap).
2. **MSE materially approaches sparse-oracle behavior**: Regime-2 MSE reached $0.01638$ (vs Oracle $0.01374$ and Sparse Oracle $0.01480$), closing $96.3\%$ of the MSE gap.
3. **Compute remains $\le 25\%$ Dense**: $103.6$ FLOPs/step ($17.2\%$ of Dense, limit is $150.5$).
4. **Total probe budget remains unchanged**: Exactly 10,000 probes across all seeds.
5. **No catastrophic seed-specific noise lock-in remains**: 100% final recall achieved on every evaluation seed.

The candidate screening bottleneck is resolved. The new dominant failure mechanism is clearly isolated: **stabilizing newly promoted features against premature eviction while retaining noise-resistant eviction of spurious entrants**.
