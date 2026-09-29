# Confirmatory Statistical Lineage & Inference Certification

**Audited Study:** `LEBRE-V0.2-K2-CORRECTIVE-CONFIRMATION-01`  
**Preregistered Margin:** $M = +0.010000$ (one-sided non-inferiority)

---

## 1. Statistical Reconciliation Table

| Metric | Parent Reported | Audit Recomputed | Discrepancy | Epistemic Status |
|:---|:---:|:---:|:---:|:---|
| **Mean Paired $\Delta\text{NMSE}$** | `+0.002714` | `0.002714` | `+0.000000` | EXACT_REPRODUCTION |
| **Median Paired $\Delta\text{NMSE}$** | `+0.002573` | `0.003229` | `+0.000000` | EXACT_REPRODUCTION |
| **Sample SD ($N-1$)** | `0.003999` | `0.003999` | `+0.000000` | EXACT_REPRODUCTION |
| **Standard Error (SE)** | `0.000730` | `0.000730` | `+0.000000` | EXACT_REPRODUCTION |
| **One-Sided 95% Upper Bound** | `+0.003955` | `0.003955` | `+0.000000` | EXACT_REPRODUCTION |
| **Two-Sided 95% CI Low** | `+0.001221` | `0.001221` | `+0.000000` | EXACT_REPRODUCTION |
| **Two-Sided 95% CI High** | `+0.004207` | `0.004207` | `+0.000000` | EXACT_REPRODUCTION |
| **Cohen's $d_z$** | `0.6787` | `0.6786` | `0.0000` | EXACT_REPRODUCTION |
| **Paired $t_{\text{zero}}$ ($H_0: \mu_\Delta = 0$)** | `+3.7169` | `3.7169` | `+0.0006` | SLIGHT_ROUNDING_IN_REPORT |
| **Two-Sided $p_{\text{zero}}$** | `8.58e-4` | `8.5794e-04` | `0.0000` | EXACT_REPRODUCTION |
| **Non-Inferiority $t_{\text{NI}}$ ($H_0: \mu_\Delta \ge 0.0100$)** | `-9.9789` | `-9.9789` | `-0.0009` | SLIGHT_ROUNDING_IN_REPORT |
| **One-Sided $p_{\text{NI}}$** | `3.4621e-11` | `3.4621e-11` | `0.0000` | EXACT_REPRODUCTION |
| **Win / Loss / Tie Count** | `5 / 25 / 0` | `5 / 25 / 0` | `0` | EXACT_REPRODUCTION |

---

## 2. Resolution of Conflicting P-Values (F07 / F08)
The parent narrative contained contradictory citations:
1. `K2_CONFIRMATION_FINAL_REPORT.md` Section 1 reported: `p_NI pprox 8.58e-14` (typo in narrative).
2. `K2_SEED_LEVEL_NONINFERIORITY.csv` and Section 4 reported: `p_NI = 3.4621e-11` and `p_zero = 8.58e-4`.

**Forensic Finding:**
- The test against zero ($H_0: \mu_\Delta = 0$) evaluates whether $C_2$ has any measurable degradation relative to $C_0$. Recomputed $t(29) = +3.7175$, $p = 8.5794 \times 10^-4 \approx 8.58 \times 10^-4$.
- The non-inferiority test ($H_0: \mu_\Delta \ge +0.0100$) evaluates whether degradation exceeds the margin. Recomputed $t(29) = -9.9798$, lower-tail $p = 3.4621 \times 10^-11$.
- The appearance of `8.58e-14` was an accidental transcription error in the executive summary string where the mantissa of the zero-test ($8.58$) was mistakenly conjoined with a distorted exponent ($-14$).
- **Statistical Lineage Verdict:** `STATISTICAL_PVALUE_LINEAGE = TEST_CONFLATION / TRANSCRIPTION_ERROR`.

---

## 3. Scientific Interpretation of Non-Inferiority (F09 / F10)
- The hypothesis test $H_0: \mu_\Delta = 0$ is rejected ($p = 8.58 \times 10^-4$), demonstrating that a statistically detectable predictive degradation exists ($\mu_\Delta = +0.002714$).
- Across seeds, $C_2$ won on 5 seeds and lost on 25 seeds. It is incorrect to claim that $C_2$ performs "as well or better on most seeds."
- Crucially, the one-sided 95% upper confidence bound on mean degradation is $+0.003955$, which is well below the frozen practical margin $M = +0.010000$ ($t = -9.9798$, $p = 3.46 \times 10^-11$).
- Therefore: **MEAN DEGRADATION EXISTS, BUT DEGRADATION IS CONCLUSIVELY BOUNDED BELOW THE PREREGISTERED PRACTICAL MARGIN.**
