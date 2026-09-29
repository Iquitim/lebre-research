# Formal Seal Corrigendum: Recurrent Shadow Reconciliation

### ERRATA CATALOGUE

#### ERRATA-01 (Candidate Freeze Labeling Error)
- **Original Artifact:** `FINAL_RECURRENT_CANDIDATE_FREEZE.md`
- **Original Text:** `| C1 (Primary) | K=5 | 86.021 | PASS | +0.031155 | PASS | SELECTED FOR FINAL FREEZE |`
- **Corrected Text:** `| C1 (Primary) | K=5 | 86.021 | PASS | +0.031155 | FAIL (exceeds +0.0100 margin) | SELECTED FOR FALSIFICATION / CONFIRMATORY EVALUATION |`
- **Error Class:** `ARITHMETIC_LABEL_ERROR` / `MANUAL_TRANSCRIPTION_ERROR`
- **Scientific Consequence:** None. Confirmatory run proved hypothesis false.

#### ERRATA-02 (Absolute NMSE Narrative Lineage)
- **Original Artifact:** Narrative summary tables / `walkthrough.md`
- **Original Text:** `C0 = 0.174582, C1 = 0.206646, R0 = 0.153214`
- **Corrected Text:** `C0 = 0.317009, C1 = 0.349072, R0 = 0.295640`
- **Error Class:** `DEV_FINAL_CONFLATION`
- **Scientific Consequence:** Level-1 raw CSV was always correct; pairwise deltas are identical to within $10^{-6}$.

#### ERRATA-03 (Switching Latency Narrative Correction)
- **Original Artifact:** `RECURRENT_SHADOW_FINAL_REPORT.md` (Question 26)
- **Original Text:** `Regime switching recovery latency degraded by +39.7 steps on I11 and +42.5 steps on I12.`
- **Corrected Text:** `Regime switching recovery latency degraded by +246.2 steps on I11 and +15.2 steps on I12.`
- **Error Class:** `REPORTING_ERROR`
- **Scientific Consequence:** Reaffirms that the switching gate FAILED.
