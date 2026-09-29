# Resource Field Semantics & Double-Counting Audit

## 1. Field Lineage & Inclusive Definitions
An audit of `run_k2_arb10_composition.py` and `K2_ARB10_FINAL_RESULTS.csv` establishes:
```python
candidate_descendant_fp = candidate_direct_fp + arbitration_fp
```
- For Arm A0: $1.842212 + 5.600000 = 7.442212\text{ FP/step}$.
- For Arm A1: $1.832203 + 5.600000 = 7.432203\text{ FP/step}$.
- For Arm A2: $1.838008 + 2.800000 = 4.638008\text{ FP/step}$.

Therefore, `candidate_descendant_fp` is an **INCLUSIVE** field.

## 2. Prevention of Double Counting
If an accounting ledger sums:
$$\text{live\_fp} + \text{search\_fp} + \text{recurrent\_shadow\_fp} + \text{candidate\_direct\_fp} + \text{candidate\_descendant\_fp} + \text{arbitration\_fp}$$
both `candidate_direct_fp` and `arbitration_fp` would be double-counted!

The unique orthogonal identity that covers total model compute with **zero residual** is:
$$\mathbf{\text{TOTAL\_FP}} = \mathbf{\text{LIVE\_LINEAR\_FP}} + \mathbf{\text{SEARCH\_PROBE\_FP}} + \mathbf{\text{RECURRENT\_SHADOW\_FP}} + \mathbf{\text{CANDIDATE\_DESCENDANT\_FP}}$$

## 3. Residual Verification
- Arm A0: $111.188662 - (75.644861 + 7.901589 + 20.200000 + 7.442212) = \mathbf{0.000000\text{ FP}}$.
- Arm A1: $100.674818 - (74.141956 + 7.900659 + 11.200000 + 7.432203) = \mathbf{0.000000\text{ FP}}$.
- Arm A2: $96.957851 - (73.222214 + 7.897629 + 11.200000 + 4.638008) = \mathbf{0.000000\text{ FP}}$.

Accounting Status: **`PASS`** (Zero unexplained residual).
