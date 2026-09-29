# Gate 6 Threshold Lineage, Semantic Reconstruction & Forensic Audit

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus Inquiry:** Issue A — Forensic Reconstruction of the Gate 6 Redundancy Threshold Drift  

---

## 1. Executive Summary

In `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`, Section 5, Table 5.1, and Section 6.5 of `SHADOW_RENT_FINAL_REPORT.md` evaluate candidates $S_2$ and $S_3$ against a redundancy ceiling of **$\le 10.0\%$**, labeling $S_2$ ($9.2\%$) and $S_3$ ($8.4\%$) as **`PASS Gate 6`**.

This forensic audit traces the source documentation of Gate 6 from its original preregistration through subsequent reconciliation cycles. The audit confirms:
1. The **preregistered, binding Gate 6 threshold is $\le 0.05$ ($5.0\%$)**, defined as `frac_both` on stream $I_{10}$ over steady-state steps $t \in [1000, 6000)$.
2. **No authorized pre-confirmatory protocol amendment** ever raised the Gate 6 ceiling to $0.10$.
3. Under the binding $0.05$ threshold, **both $S_2$ (mean $0.0918$, $13/30$ seeds $> 0.05$) and $S_3$ (mean $0.0837$, $18/30$ seeds $> 0.05$) strictly FAIL Gate 6**.
4. The parent study's claim that duty-cycling *"resolves the legacy Gate 6 failure"* constitutes an unpreregistered post-hoc threshold relaxation.
5. While literal gate compliance is **`FAIL`**, the algorithmic mitigation of redundant co-activation ($49.4\%$ reduction for $S_2$, $53.9\%$ reduction for $S_3$ relative to $S_0$) is a factually verified descriptive result.

---

## 2. Textual Source Recovery Across Study Lineage

### 2.1 Frozen Integration Protocol (`LEBRE_V0_2_INTEGRATION_PROTOCOL.md`)
> **Line 61:**  
> `GATE 6 — Redundant Temporal Discrimination (I10): frac_both on t in [1000, 6000) <= 0.05.`  
> *Requirement:* In stationary linear delay environments, the model must not sustain spurious continuous recurrent activation. Steady-state co-activation of delay taps and recurrent units (`frac_both`) must not exceed $5.0\%$.

### 2.2 Frozen Integration Hypotheses (`LEBRE_V0_2_INTEGRATION_HYPOTHESES.md`)
> **Lines 68–71:**  
> `H6: Redundancy Control on Task I10.`  
> $$\rho_{\text{dual}, I10} = \frac{1}{5000} \sum_{t=1000}^{5999} \mathbb{I}(\text{State}_t = \text{BOTH}) \le 0.05$$  
> Confirmatory standard: One-sample ceiling test at $\alpha = 0.05$.

### 2.3 Gate 6 Preregistered Definition (`GATE6_PREREGISTERED_DEFINITION.md`)
In `LEBRE-V0.2-SEAL-ARTIFACT-RECONCILIATION-01`:
> **Binding Audit Rule (Line 58):**  
> *"Substituting redundant_dual_rate (which was 0.0000 for T3) for frac_both to declare Gate 6 a PASS is a post-hoc metric substitution. The audit must evaluate Gate 6 strictly against frac_both <= 0.05."*  
> Confirmatory Result: $T_3$ exhibited mean `frac_both` of $0.108467$ ($10.85\%$). Gate 6 was formally sealed as **`GATE_6_PREREGISTERED_STATUS = FAIL`**.

### 2.4 Resource Compaction Protocol (`RESOURCE_COMPACTION_PROTOCOL.md`)
> **Lines 104–105:**  
> *"Gate 6 (Redundancy Ceiling <= 0.05 on I10): This stage does NOT attempt to fix Gate 6. The historical status remains FAIL."*

### 2.5 Shadow-Rent Preregistration (`SHADOW_RENT_PREREGISTRATION.md`)
> **Line 31 (Table 1):**  
> `| Gate 6 Redundancy Status | Carried forward as FAIL (not intentionally repaired) |`  
> *Audit Significance:* The preregistration explicitly acknowledged that Gate 6 was carried forward as FAIL and that no repair hypothesis or threshold change was preregistered.

### 2.6 Shadow-Rent Protocol Drift (`SHADOW_RENT_PROTOCOL.md`)
> **Line 85:**  
> `### Gate 6: Quiescent Reactivation`  
> In `SHADOW_RENT_PROTOCOL.md`, Section 4 re-titled Gate 6 as "Quiescent Reactivation" (evaluating sleep efficiency on $I_7/I_8$), creating a numbering collision with legacy Gate 6 (Redundancy Control on $I_{10}$).

---

## 3. Provenance of the Post-Hoc 10% Ceiling

### 3.1 Code Origin in Execution Script
In `scratch/run_v02_shadow_rent_governance.py`, line 919:
```python
i10_rows.append({
    'scheduler_id': sch,
    'nmse': nmse_m,
    'frac_both': both_frac,
    'frac_redundant_dual': redundant_frac,
    'gate6_redundancy_status': 'FAIL' if both_frac > 0.10 else 'PASS',
})
```
The script author hardcoded `both_frac > 0.10` as the decision boundary. 

### 3.2 Visual Inscription in Figure F10
In `scratch/generate_shadow_rent_figures.py`, line 286:
```python
ax.axhline(
    10.0, color='red', linestyle='--', label='Gate 6 Redundancy Ceiling (10%)'
)
```
This inscribed the $10.0\%$ line as a visual ceiling in `figures/F10_i10_redundancy_mitigation.png`. Because $S_2$ ($9.2\%$) and $S_3$ ($8.4\%$) fell below $10.0\%$, they were visually and narratively declared to pass Gate 6.

### 3.3 Regulatory Finding
There is no preregistered document, protocol amendment, or decision memo authorizing the relaxation of the Gate 6 ceiling from $0.05$ to $0.10$. In accordance with Level 3 data authority, the $0.05$ ceiling remains strictly binding.

---

## 4. Recomputed Gate 6 Metrics on Task $I_{10}$ ($N=30$)

```
+-------------------------------------------------------------------------------------------------------------------------+
| Scheduler ID        | Mean frac_both | Median  | Min - Max     | 95% Conf Int   | Seeds >0.05 | Seeds >0.10 | Prereg Status |
+-------------------------------------------------------------------------------------------------------------------------+
| S0_CONTINUOUS       |    0.181517    | 0.0738  | 0.0175-0.9685 | [0.0203,0.8144]| 20/30 (67%) | 14/30 (47%) |     FAIL      |
| S1_SHADOW_OFF       |    0.000000    | 0.0000  | 0.0000-0.0000 | [0.0000,0.0000]|  0/30 ( 0%) |  0/30 ( 0%) |     PASS*     |
| S2_PERIODIC         |    0.091767    | 0.0400  | 0.0000-0.4092 | [0.0000,0.3628]| 13/30 (43%) | 10/30 (33%) |     FAIL      |
| S3_EVENT_TRIGGERED  |    0.083678    | 0.0596  | 0.0062-0.3537 | [0.0132,0.3276]| 18/30 (60%) |  6/30 (20%) |     FAIL      |
+-------------------------------------------------------------------------------------------------------------------------+
* Note: S1 passes trivially because all temporal structure discovery is disabled; S1 fails predictive tasks.
```

### 4.1 Seed Breach Analysis
- **$S_2$ (Periodic $K=5$):** $13$ out of $30$ seeds violate the $0.05$ ceiling. The distribution is heavily right-skewed (median $0.0400$, mean $0.0918$, max $0.4092$).
- **$S_3$ (Event-Triggered):** $18$ out of $30$ seeds ($60.0\%$) violate the $0.05$ ceiling. The median ($0.0596$) itself exceeds the $0.05$ ceiling.

---

## 5. Disaggregation: Compliance vs. Descriptive Mitigation

To uphold scientific objectivity, we must separate rigid gate compliance from genuine algorithmic improvements:

1. **Gate Compliance (`GATE_6_PREREGISTERED_COMPLIANCE = FAIL`):**
   Neither $S_2$ nor $S_3$ meets the preregistered confirmatory requirement ($\rho_{\text{dual}} \le 0.05$). The reported "PASS Gate 6" verdict is formally revoked.

2. **Descriptive Algorithmic Mitigation (`DUAL_OCCUPANCY_MITIGATION = SUPPORTED`):**
   Duty-cycling substantially suppresses unneeded co-activation relative to continuous baseline $S_0$:
   - $S_2$ cuts mean dual occupancy from $18.15\%$ to $9.18\%$ (a **$49.4\%$ relative reduction**).
   - $S_3$ cuts mean dual occupancy from $18.15\%$ to $8.37\%$ (a **$53.9\%$ relative reduction**).
   - Both schedulers eliminate severe runaway redundancy observed in worst-case $S_0$ seeds ($S_0$ max was $96.85\%$; $S_2$ max was $40.92\%$; $S_3$ max was $35.37\%$).

3. **Formal Retest Status (`GATE6_FORMAL_RETEST = NOT_PERFORMED`):**
   Because `SHADOW_RENT_PREREGISTRATION.md` carried Gate 6 forward as an unrepaired failure without a formal retest hypothesis, Gate 6 in this study serves as an **informative observational diagnostic**, not an authorized confirmatory retest.
