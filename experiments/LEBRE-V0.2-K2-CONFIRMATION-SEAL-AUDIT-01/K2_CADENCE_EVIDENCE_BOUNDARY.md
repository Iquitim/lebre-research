# Cadence Evidence Boundary & Epistemic Mapping

| Cadence ($K$) | Status in Experimental Stream v0.2 | Sample Size ($N$) | Predictive Non-Inferiority | Temporal Mechanism Preservation | Strict Compute Budget (<=100 FP) | Epistemic Classification |
|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **$K=1$** | Confirmatory Baseline | $N=30$ | REFERENCE | REFERENCE | FAIL (111.24 FP) | CONFIRMED_PARENT_REFERENCE |
| **$K=2$** | Confirmed Behavioral Boundary | $N=30$ | SUPPORTED (+0.0027) | ALL PASS (I6, I7, I9, I11..I14) | FAIL (101.02 FP) | CONFIRMED_LOCAL_BEHAVIORAL_BOUNDARY |
| **$K=3$** | Not Evaluated in Current Topology | $N=0$ | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| **$K=4$** | Not Evaluated in Current Topology | $N=0$ | UNTESTED | UNTESTED | UNTESTED | UNTESTED |
| **$K=5$** | Refuted Under HOLD_STATE | $N=30$ (M2-Exp) | FAILED (+0.0382) | FAILED (I6, I11..I14 broken) | PASS (91.80 FP) | REFUTED_UNDER_HOLD_STATE |
| **$K=10$** | Historical Refutation | Legacy | FAILED | FAILED | PASS | HISTORICAL_REFUTATION |

---

## Epistemic Audit of Generalization Claims (F13 / F14 / F44 / F45)
1. **Parent Claim:** The report stated that "as established in the seal audit, $K \ge 3$ creates unrecoverable phase distortion and breaks state tracking."
2. **Audit Finding:** $K=3$ and $K=4$ were never simulated or evaluated in the current $T_3$ topology with $M_1^*$ rotating sparse frontier ($H=32, B=4$).
3. **Correct Boundary:** The empirical evidence refutes $K=5$ and confirms $K=2$. It does **not** prove that $K=3$ or $K=4$ must universally fail.
4. **Governance Invariant:** No $K=3$ or $K=4$ simulation is authorized or recommended in this audit. Claims generalizing to all $K \ge 3$ are unsupported interpolations and must be corrected.
