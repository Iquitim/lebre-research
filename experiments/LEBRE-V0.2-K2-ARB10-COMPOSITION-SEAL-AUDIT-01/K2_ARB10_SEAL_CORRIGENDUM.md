# Authoritative Errata Corrigendum: LEBRE-V0.2-K2-ARBITRATION-COMPOSITION-01

| ERRATA_ID | TARGET_ARTIFACT | ORIGINAL_TEXT / VALUE | CORRECTED_TEXT / VALUE | ERROR_CLASS | SCIENTIFIC_CONSEQUENCE | REQUIRES_NEW_DATA |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **ERR-01** | `K2_ARB10_FINAL_REPORT.md`, Q22 | "Did all I11-I14 pass? FAIL. Task I12 latency delta was +213.63 > +50." | "Both Task I11 (+76.17) and Task I12 (+213.63) fail the preregistered end-to-end switching gate (<= +50 steps)." | `CONTRAST_CONFLATION` | Expands switching failure to two tasks | **NO** |
| **ERR-02** | `K2_ARB10_TEMPORAL_MECHANISM_DECISION.md` | I11 Switching Recovery marked "PASS" with +76.17 in table | I11 Switching Recovery marked "FAIL" (+76.17 > +50) | `CONTRAST_CONFLATION` | Reporting consistency restored | **NO** |
| **ERR-03** | `K2_ARB10_FINAL_REPORT.md`, Q16 | Live linear compute $74.25$ and $73.34$ | Exact Level-1 means: $74.141956$ and $73.222214\text{ FP/step}$ | `STALE_INTERMEDIATE` | Exact arithmetic restored | **NO** |
| **ERR-04** | `K2_ARB10_FINAL_REPORT.md`, Q5 | $\tau_{\text{events}} = 49.4965$ | $\tau_{\text{events}} = 49.498316\text{ events}$ | `ROUNDING_APPROXIMATION` | Exact double-precision restored | **NO** |
| **ERR-05** | `K2_ARB10_MECHANISM_ATTRIBUTION.md` | "Causal mechanism isolated" | "Coupled EMA timescale distortion and decision staleness strongly supported" | `COUPLED_MECHANISM_MISLABELED_AS_ISOLATED` | Epistemic rigor restored | **NO** |
| **ERR-06** | `K2_ARB10_FINAL_REPORT.md`, Section 17 | `I11_GATE_STATUS = PASS` | `I11_GATE_STATUS = FAIL` | `CONTRAST_CONFLATION` | Machine-readable accuracy restored | **NO** |
