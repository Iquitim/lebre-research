# Hierarchical Search Eligibility Adjudication

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-COMPACTION-01`  
**Milestone:** Phase 1 Governance Decision  
**Auditor:** Independent Skeptical Senior Researcher and Scientific Software Auditor  
**Date:** September 22, 2026  

---

## 1. Formal Adjudication

In accordance with Section 19 of `CORRELATION_SEARCH_PROTOCOL.md` and Section 1 (Hypothesis 2) of `CORRELATION_SEARCH_PREREGISTRATION.md`:

```text
COARSE_TO_FINE_ELIGIBLE = NO
```

### Justification:
The DEV lag-score locality audit demonstrated that the observed neighbor rank correlation is $r = 0.2176 < 0.60$, and the fraction of true-delay regimes where a coarse neighbor captures $\ge 70\%$ of the peak correlation magnitude is only $3.64\% < 70.0\%$.

Because exact discrete delays in white-input streaming systems manifest as isolated Kronecker delta spikes, coarse-to-fine search suffers from structural blindness, systematically failing to detect true delays that fall between coarse anchors.

### Governance Impact:
1. Candidate family $C_2$ (`HIERARCHICAL_COARSE_TO_FINE`) is disqualified from consideration as a deployable candidate.
2. In Phase 2 DEV screening, $C_2$ will be reported as a comparative negative result to document why hierarchical search fails.
3. The candidate frozen for FINAL confirmatory evaluation must be selected from the $C_1$ (`ROTATING_SPARSE_FRONTIER`) family.
