# Recurrent Shadow Seal Root Cause Analysis

### Identified Discrepancies & Forensics:

| Issue ID | Artifact Containing Issue | Higher-Authority Source | Root Cause | Impact | Requires New Data |
|:---|:---|:---|:---|:---|:---:|
| **RCA-01** | `FINAL_RECURRENT_CANDIDATE_FREEZE.md` | `RECURRENT_DEV_RESULTS.csv` | Template hardcoding of "PASS" based on prior D9F expectation | Narrative arithmetic contradiction; corrected by errata | **NO** |
| **RCA-02** | Narrative summaries / `walkthrough.md` | `RECURRENT_FINAL_RESULTS.csv` | Intermediate offset copy ($0.1746 / 0.2066$) in narrative table | Level-1 raw CSV was always $0.3170 / 0.3491$; deltas identical | **NO** |
| **RCA-03** | Final report narrative | `RECURRENT_FINAL_RESULTS.csv` | Cohort variance ($111.01$ historical vs $110.89$ concurrent C0) | Reconciled to use concurrent C0 cohort for causal deltas | **NO** |
| **RCA-04** | Final report narrative | `RECURRENT_FINAL_RESULTS.csv` | Legacy R0 compute ($128.52$) cited instead of full continuous ($169.42$) | Reconciled R0 candidate descendant accounting | **NO** |
| **RCA-05** | Final report narrative | `RECURRENT_FINAL_RESULTS.csv` | Failure to report that $10.5\text{ FP}$ of K5 saving came from live structure loss | Dissected as pathological structure loss | **NO** |
| **RCA-06** | Final report narrative | `RECURRENT_SWITCHING_ANALYSIS.csv` | Narrative cited $+39.7$ on $I_{11}$; actual Level-1 was $+246.2$ steps | Switching gate correctly adjudicated as FAIL | **NO** |
