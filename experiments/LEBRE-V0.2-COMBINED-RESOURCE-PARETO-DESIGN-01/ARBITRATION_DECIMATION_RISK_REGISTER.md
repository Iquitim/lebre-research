# Arbitration Decimation Risk Register

## Literature-Aligned Risk Register (D14)

| Risk ID | Risk Name | Theoretical Mechanism | Affected Tasks | Severity | Mitigation & Monitoring |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **R-01** | `DECISION_STALENESS` | Decision age doubles ($4 \to 9$ steps), delaying structural adaptations | All tasks | Low-Med | Monitored via off-policy oracle telemetry |
| **R-02** | `TRANSIENT_SWITCHING_DELAY` | Latency floor adds up to $+5$ stream steps at changepoints ($t=3000$) | $I_{11}, I_{12}, I_{13}, I_{14}$ | Moderate | Guarded by $+50$-step switching gate |
| **R-03** | `EXPERT_SELECTION_LAG` | Delayed eviction of stale linear/recurrent expert during regime shift | $I_{11}, I_{12}$ | Moderate | Monitored via task-level MSE rollouts |
| **R-04** | `DUAL_OCCUPANCY_PERSISTENCE` | Redundant dual structure remains active for up to 5 additional steps | $I_{10}$ | Low | Monitored via `frac_both` telemetry (Gate 6 remains FAIL) |
| **R-05** | `PROMOTION_DELAY` | Fully qualified candidates wait up to 5 steps for next evaluation | $I_3, I_4, I_5$ | Low | Monitored via candidate probation duration |
| **R-06** | `EVICTION_DELAY` | Unproductive modules consume live FP for up to 5 extra steps | $I_2, I_{13}$ | Low | Monitored via live compute breakdown |
| **R-07** | `CHURN_REDUCTION` | Slower evaluation filters transient noise, reducing chattering | All tasks | **Beneficial** | Monitored via promotion/eviction frequency |
| **R-08** | `CHURN_INCREASE` | Delayed eviction causes accumulated error bursts triggering churn | $I_{14}$ | Low | Monitored via candidate births and discards |
| **R-09** | `SAVING_ERASED_BY_LIVE_OCCUPANCY`| Delayed eviction increases live tap mass, eroding the 2.8 FP saving | $I_{10}, I_{14}$ | Moderate | Guarded by strict $\le 100.0\text{ FP}$ total compute gate |
| **R-10** | `UNEXPECTED_BEHAVIORAL_HYSTERESIS`| Discrete decimation creates unintended hysteresis loops in weights | $I_9, I_{14}$ | Low-Med | Monitored via weight trajectories and complementarity |
