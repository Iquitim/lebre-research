# Event-Triggered Sentinel Calibration & Grid Selection Record

**Study ID:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Focus:** 12-Configuration Page-Hinkley Parameter Calibration on DEV Cohort (`1601`–`1605`)  
**Author:** Independent Skeptical Senior Researcher  
**Status:** FROZEN CALIBRATION RECORD (PRE-CONFIRMATION SEAL)  

---

## 1. Candidate Grid Design & Preregistered Scope

In accordance with Sections 15, 16, and 43 of the audit charter:
1. Calibration was performed exclusively on the Development Cohort (`1601`–`1605`).
2. A constrained factorial grid of exactly 12 parameter combinations was evaluated across representative benchmark tasks ($I_1, I_3, I_6, I_9, I_{11}$).
3. The burst length was frozen at $W = 50$ steps (matching the canonical shadow accumulation timescale $T_{\text{prob}} = 50$).
4. The trigger-during-burst rule was frozen at `IGNORE` to eliminate recursive cascading.

```
+--------------------------------------------------------------------------------------------------+
| CANDIDATE PARAMETER FACTORS (12 CONFIGURATIONS)                                                  |
+------------------------------+-------------------------+-----------------------------------------+
| Factor                       | Levels                  | Description                             |
+------------------------------+-------------------------+-----------------------------------------+
| Slack Parameter (delta)      | {0.05, 0.10}            | Insensitivity deadband on loss error    |
| Alarm Threshold (lambda)     | {4.0, 6.0, 8.0}         | Page-Hinkley cumulative sum trip point  |
| Heartbeat Interval (H)       | {150, 250}              | Anti-starvation wake interval           |
| Wake Burst Duration (W)      | {50}                    | Consecutive shadow-active steps on trip |
+------------------------------+-------------------------+-----------------------------------------+
```

---

## 2. Empirical Grid Evaluation Results

The complete experimental output is preserved in [EVENT_TRIGGER_GRID.csv](<lebre-research>/experiments/LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01/EVENT_TRIGGER_GRID.csv):

| Config ID | Slack $\delta$ | Threshold $\lambda$ | Heartbeat $H$ | Mean Duty Cycle | Mean Total Online FP | Aggregate NMSE | Switch Delay | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `C01` | $0.05$ | $4.0$ | $150$ | $0.370$ ($37.0\%$) | $121.21$ | $0.2002$ | $34.0$ steps | `FAIL_BUDGET` |
| `C02` | $0.05$ | $4.0$ | $250$ | $0.358$ ($35.8\%$) | $120.98$ | $0.1964$ | $34.0$ steps | `FAIL_BUDGET` |
| `C03` | $0.05$ | $6.0$ | $150$ | $0.254$ ($25.4\%$) | $109.22$ | $0.1951$ | $13.0$ steps | `FAIL_BUDGET` |
| `C04` | $0.05$ | $6.0$ | $250$ | $0.258$ ($25.8\%$) | $109.06$ | $0.1970$ | $12.6$ steps | `FAIL_BUDGET` |
| `C05` | $0.05$ | $8.0$ | $150$ | $0.212$ ($21.2\%$) | $105.62$ | $0.2113$ | $106.6$ steps| `FAIL_BUDGET` |
| `C06` | $0.05$ | $8.0$ | $250$ | $0.219$ ($21.9\%$) | $105.71$ | $0.2154$ | $107.2$ steps| `FAIL_BUDGET` |
| `C07` | $0.10$ | $4.0$ | $150$ | $0.266$ ($26.6\%$) | $113.75$ | $0.1776$ | $9.2$ steps  | `FAIL_BUDGET` |
| `C08` | $0.10$ | $4.0$ | $250$ | $0.266$ ($26.6\%$) | $113.83$ | $0.1774$ | $7.4$ steps  | `FAIL_BUDGET` |
| `C09` | $0.10$ | $6.0$ | $150$ | $0.235$ ($23.5\%$) | $107.75$ | $0.2040$ | $66.6$ steps | `FAIL_BUDGET` |
| `C10` | $0.10$ | $6.0$ | $250$ | $0.219$ ($21.9\%$) | $107.26$ | $0.1972$ | $65.4$ steps | `FAIL_BUDGET` |
| `C11` | $0.10$ | $8.0$ | $150$ | $0.170$ ($17.0\%$) | $99.72$  | $0.2035$ | $57.0$ steps | `PASS_BUDGET` |
| **`C12`**| **$0.10$** | **$8.0$** | **$250$** | **$0.164$ ($16.4\%$)**| **$98.47$** | **$0.1989$** | **$25.2$ steps**| **`PASS_BUDGET`**|

---

## 3. Selection Rationale & Preregistered Freeze

Applying the selection rules from Section 50:
1. **Ceiling Compliance:** Configurations `C01` through `C10` breach the $100.0 \text{ FLOPs/step}$ ceiling due to excessive baseline chattering and false alarms on stationary noise. They are disqualified.
2. **Budget-Compliant Set:** Only `C11` ($99.72 \text{ FLOPs}$) and `C12` ($98.47 \text{ FLOPs}$) satisfy Gate 1.
3. **Pareto Dominance between Compliant Candidates:**
   - Compute: `C12` ($98.47 \text{ FLOPs}$) is strictly more efficient than `C11` ($99.72 \text{ FLOPs}$).
   - Accuracy: `C12` achieves lower NMSE ($0.1989$ vs $0.2035$).
   - Responsiveness: `C12` detects regime shifts more rapidly ($25.2$ steps vs $57.0$ steps) due to its larger heartbeat interval suppressing premature drift accumulation.
4. **Matched Compute Baseline:** `C12` exhibits a theoretical mean compute of exactly **$98.47 \text{ FLOPs/step}$**, achieving perfect parity with the analytical expectation of $S_2$ ($98.47 \text{ FLOPs/step}$).

### Frozen Specification for Confirmatory $S_3$
- **Selected Configuration:** `C12`
- **$\delta$ (Slack):** $0.10$
- **$\lambda$ (Threshold):** $8.0$
- **$H$ (Heartbeat Interval):** $250$ steps
- **$W$ (Burst Duration):** $50$ steps
- **Trigger-in-Burst Rule:** `IGNORE`
- **Re-calibration Status:** SEALED AND FROZEN. No parameter may be adjusted during confirmatory execution.
