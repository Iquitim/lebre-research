# BENCH-01A-R: Cryptographic Hash Reconciliation & Immutability Chain

**Document ID:** BENCH-01A-R-HASHES  
**Auditor:** Reproducibility Auditor & Security Officer  
**Date:** September 19, 2026  
**Status:** HASH CHAIN RECONCILED & RE-LOCKED  
**Governing Standard:** Sections 51–53 of Protocol BENCH-01A-R  

---

## 1. Intentional Hash Invalidation Rationale (Section 51)

During the methodological audit of BENCH-01A, three protocol risks and one baseline documentation risk were identified:
1. Canonical task identity for ELEC2 required qualification and explicit relabeling to `NSW_ELECTRICITY_DERIVED_REGRESSION`;
2. Universal resource matching in Regime R2 required decoupling from Track B's internal structural parameters ($K \le 10, N \le 1$) and grounding in observable FLOP and memory envelopes;
3. The arbitrary $1.5\times$ numerical divergence penalty required complete excision in favor of neutral categorical failure reporting;
4. Baseline B3 (MUSE-RNN) required formal verification and qualification as `MUSE_RNN_REGRESSION_MINIMAL_ADAPTATION`.

Because these corrections required surgical modifications to `BENCH_01_SPEC.md` and `bench_01_locked_config.json`, the initial cryptographic hashes generated in BENCH-01A were intentionally superseded.

---

## 2. Cryptographic Hash Chain (Sections 52 & 53)

```
========================================================================================
                               CRYPTOGRAPHIC HASH CHAIN
========================================================================================
SPECIFICATION DOCUMENT: BENCH_01_SPEC.md
  OLD_SPEC_HASH:   27d09209a8f073c0146e65f2241bd337d66ffc38638e3d53a13c9d25ce0e98cd
  NEW_SPEC_HASH:   f516914da4d511e9ed58c2eb575d628bf3e01ebaab9f8bf63f9da0ebfe0e0c28
  MODIFIED_SECTIONS: Section 6 (ELEC2 Relabel), Section 13 (MUSE-RNN Adaptation),
                     Section 16 (Architecture-Neutral R2), Section 31 (Failure Policy)

CONFIGURATION FILE: experiments/BENCH-01A/bench_01_locked_config.json
  OLD_CONFIG_HASH: e1139bd5d82051f06289e1725f5e46ee23d3604ef663ce1c19abcd0d202a5475
  NEW_CONFIG_HASH: cb0d696e3e2775afa802a5a037ddf58ad3887252e4ac302e62b7e6162d334f7a
  MODIFIED_FIELDS: dataset B1 id and metadata, baseline B3 adaptation_status,
                   r2_resource_matched_limits (observable FLOP and memory ceilings),
                   failure_handling_protocol (arbitrary penalty disabled)

REASON: BENCH_01A_R_METHODOLOGICAL_CORRECTION
========================================================================================
```

---

## 3. Verification & Immutability Certification

Both files have been regenerated, formatted, and locked. The new SHA-256 hashes are integrated into the automated protocol test suite (`tests/test_bench_01_protocol.py`), ensuring that any subsequent unauthorized tampering or silent modification will immediately fail regression testing.
