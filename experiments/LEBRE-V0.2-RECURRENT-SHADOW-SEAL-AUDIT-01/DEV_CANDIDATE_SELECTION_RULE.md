# DEV Candidate Selection Rule Reconstruction

**Audited Issue:** Forensic Flag F01 and F02 (DEV Margin Arithmetic & Governance).

### 1. The Discrepancy
In `FINAL_RECURRENT_CANDIDATE_FREEZE.md`:
- Candidate $C_1$ ($K=5$) achieved $\Delta \text{NMSE} = +0.031155$.
- Practical margin stated: $+0.0100$.
- Status column labeled: **PASS**.
- Narrative stated: *"+0.031155, well below the practical margin of $+0.0100$."*

### 2. Mathematical Truth
$$0.031155 > 0.010000 \implies \text{The statement '+0.031155 is well below +0.0100' is mathematically FALSE.}$$

### 3. Root Cause Analysis
Code inspection of `run_phase_b_experiments.py` (lines 388–405) reveals:
```python
content = (
    "| **$C_1$ (Primary)** | **$K=5$** | **{c1_tot_dev:.3f}** | **PASS** (Surplus: {100 - c1_tot_dev:.3f} FP) | **{mean_d_c1:+.6f}** | **PASS** | **SELECTED FOR FINAL FREEZE** |\n"
    f"   - On the 10 DEV seeds, $C_1$ incurs an aggregate $\Delta \text{NMSE}$ of only **{mean_d_c1:+.6f}**, well below the practical margin of $+0.0100$.\n"
)
```
The string literal `"PASS"` and `"well below the practical margin of $+0.0100$"` was **hardcoded into the reporting template**. The author expected $K=5$ to reproduce historical D9F performance ($+0.002858 < +0.0100$) and did not write a dynamic boolean condition `if mean_d_c1 <= 0.0100`.

### 4. Classification:
`DEV_FREEZE_STATUS_ROOT_CAUSE = MANUAL_TRANSCRIPTION_ERROR / TEMPLATE_HARDCODING_ERROR`.
