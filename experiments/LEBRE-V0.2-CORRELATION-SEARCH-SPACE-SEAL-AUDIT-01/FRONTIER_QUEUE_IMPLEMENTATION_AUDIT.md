# Frontier Queue Implementation & Revisit Audit

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Queue Semantics Audit  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **AUDITED AND RECONCILED**  

---

## 1. Queue Code Structure & Execution Path

In `scratch/run_v02_correlation_search_compaction.py` (lines 664–684), the exploration queue is implemented as a simple circular buffer over all 160 searchable coordinate pairs:
```python
self.exploration_queue: List[Tuple[int, int]] = list(ALL_160_PAIRS) # len = 160
self.queue_ptr = 0

if self.step_count % self.K_probe == 0: # K_probe = 2
    for _ in range(self.B_batch):       # B_batch = 4 for M1*
        i_p, k_p = self.exploration_queue[self.queue_ptr]
        self.queue_ptr = (self.queue_ptr + 1) % len(self.exploration_queue)
        just_probed.append((i_p, k_p))
```

### Deterministic Mechanics:
1. **Total Queue Length ($L$):** $|`ALL_160_PAIRS`| = 160$ coordinates.
2. **Advance per Probe Event ($\Delta_{\text{ptr}}$):** Advances by exactly $B$ positions every probe tick.
3. **Probe Cadence ($K_{\text{probe}}$):** Executes once every $K_{\text{probe}} = 2$ stream steps.
4. **Circulation Period ($P_{\text{circ}}$):**
   $$P_{\text{circ}} = \frac{L}{B} \times K_{\text{probe}} = \frac{160}{4} \times 2 = \mathbf{80\text{ stream steps}}$$
5. **Observed Silence:** Exactly $80.00\text{ stream steps}$ between consecutive visits for every coordinate in the queue.

---

## 2. Forensic Reconciliation of the "272 Steps" Value

In the parent documents (`SPARSE_FRONTIER_SPEC.md` Section 4 and `SEARCH_SPACE_COMPUTE_MODEL.md` Section 2.3), the text reported an analytical exploration revisit time of:
$$T_{\text{explore}} = \frac{136}{1.0} \times 2 = \mathbf{272\text{ steps}}$$

### Reconciliation Matrix:
| Cited Value | Context / Document | Origin & Semantic Classification | Code Reality | Status |
| :--- | :--- | :--- | :--- | :--- |
| **80 steps** | Observed FINAL Max Silence | Implemented queue ($B=4, K=2, L=160$) | $\frac{160}{4} \times 2 = 80$ | **EXACT IMPLEMENTATION MATCH** |
| **160 steps** | DEV Table for $B=2$ | Implemented queue ($B=2, K=2, L=160$) | $\frac{160}{2} \times 2 = 160$ | **EXACT IMPLEMENTATION MATCH** |
| **272 steps** | Specification Narrative | Analytical model for partitioned design: $H_{\text{track}}=24, B_{\text{explore}}=1, L_{\text{explore}}=136$ | Never executed in code | **STALE_INTERMEDIATE / HYPOTHETICAL_SPEC** |
| **544 steps** | DEV Spec for $H=32, B=2$ | Partitioned design: $H_{\text{track}}=24, B_{\text{explore}}=0.5$ | Never executed in code | **STALE_INTERMEDIATE / HYPOTHETICAL_SPEC** |

### Audit Finding:
The narrative author derived $272\text{ steps}$ by assuming a hybrid architecture where 24 cells were locked in a tracking set and the remaining 136 cells were probed at $1\text{ cell}$ per probe tick. In the actual simulation runner (`scratch/run_v02_correlation_search_compaction.py`), the queue uniformly iterates over all 160 coordinates in batches of $B=4$. Therefore, the implemented queue period is **strictly and deterministically 80 steps**.
