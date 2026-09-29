# Switching Latency Unit Audit & Corrigendum

**Stage Identifier:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01/microcorrection`  
**Parent Study:** `LEBRE-V0.2-SHADOW-RENT-GOVERNANCE-01`  
**Errata Reference:** `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`  
**Focus Inquiry:** Rectification of Erroneous "Seconds" ("s") Unit Labels in Regime Switching Latency Reporting  
**Author:** Independent Skeptical Senior Reviewer  
**Date:** September 22, 2026  

---

## 1. Executive Summary & Audit Mandate

In `LEBRE-V0.2-SHADOW-RENT-SEAL-ERRATA-01`, several analytical summaries and narrative tables labeled regime-switching recovery delays using the unit **seconds ("s")**:
- `SHADOW_RENT_SEAL_ERRATA_FINAL_REPORT.md` (line 177, Table 6.1):  
  `| Gate 4: Switching Latency | Delta Lat <= +50 s | FAIL (+763.0 s) | FAIL on I11 (+290.5 s) |`
- `SHADOW_RENT_CLAIM_DEPENDENCY_GRAPH.md` (line 65):  
  `S3 passes on I12 (-15.5 s), but fails on I11 (+290.5 s). Omits I11 failure.`

This audit examines the exact Python simulation code generating these metrics and determines:
1. Whether physical execution time (seconds) was ever measured or if the metric represents integer stream timesteps.
2. The exact mathematical definition of regime-switching latency in LEBRE.
3. The normative correction replacing all instances of "s" with "steps".

---

## 2. Source Code & Simulation Evidence

In `scratch/bench_v02_integration.py` and `scratch/run_v02_shadow_rent_governance.py`:

```python
# Task I11, I12, I13, I14 Simulation Loop:
for t in range(T_STEPS): # T_STEPS = 6000 discrete integer steps
    x_t, y_t = stream.get_sample(t)
    out = model.step(x_t, y_t)
```

In `scratch/run_v02_shadow_rent_governance.py` (line 782):
```python
# Switching latency calculation:
# t_switch = 3000 (the exact discrete timestep where the regime abruptly changes)
# Recovery is defined as the first timestep t >= t_switch where post-switch rolling NMSE drops below threshold.
recovery_step = find_recovery_step(errors, t_switch=3000)
latency = recovery_step - 3000 # Measured strictly in discrete stream iterations
```

### Forensic Finding:
1. All streaming benchmark experiments execute in a simulated, discrete-time synchronous loop ($t = 0, 1, 2, \dots, 5999$).
2. The change-point occurs precisely at integer timestep $t_{\text{switch}} = 3000$.
3. Recovery latency is measured as the number of **discrete stream steps** elapsed after $t=3000$ before tracking is re-established.
4. **No physical clock or wall-time seconds were ever recorded or calculated for this metric.**
5. The suffix "s" was accidentally introduced by the author as an abbreviation for "steps" (or by cognitive drift associating latency with physical time).

---

## 3. Register of Defective Labels & Exact Replacement Text

```
+-------------------------------------------------------------------------------------------------------------------------------+
| Document & Location               | Erroneous Text                     | Binding Corrected Text           | Defect Type       |
+-------------------------------------------------------------------------------------------------------------------------------+
| SHADOW_RENT_SEAL_ERRATA_FINAL_    | Delta Lat <= +50 s                 | Delta Lat <= +50 steps           | Unit symbol drift |
| REPORT.md:177 (Table 6.1)         |                                    |                                  | ("s" -> "steps")  |
+-------------------------------------------------------------------------------------------------------------------------------+
| SHADOW_RENT_SEAL_ERRATA_FINAL_    | FAIL (+763.0 s)                    | FAIL (+763.0 steps)              | Unit symbol drift |
| REPORT.md:177 (Table 6.1)         |                                    |                                  | ("s" -> "steps")  |
+-------------------------------------------------------------------------------------------------------------------------------+
| SHADOW_RENT_SEAL_ERRATA_FINAL_    | FAIL on I11 (+290.5 s)             | FAIL on I11 (+290.5 steps)       | Unit symbol drift |
| REPORT.md:177 (Table 6.1)         |                                    |                                  | ("s" -> "steps")  |
+-------------------------------------------------------------------------------------------------------------------------------+
| SHADOW_RENT_CLAIM_DEPENDENCY_     | I12 (-15.5 s) vs I11 (+290.5 s)    | I12 (-15.5 steps) vs             | Unit symbol drift |
| GRAPH.md:65                       |                                    | I11 (+290.5 steps)               | ("s" -> "steps")  |
+-------------------------------------------------------------------------------------------------------------------------------+
```

---

## 4. Arithmetic Equivalence & Conversion Rule

$$\text{Conversion Factor} = 1.000000 \quad (\text{Identity})$$

Because $1\text{ unit of reported latency} \equiv 1\text{ streaming step}$:
- $+50\text{ s} \longrightarrow \mathbf{+50\text{ steps}}$
- $+763.0\text{ s} \longrightarrow \mathbf{+763.0\text{ steps}}$
- $+290.5\text{ s} \longrightarrow \mathbf{+290.5\text{ steps}}$
- $-15.5\text{ s} \longrightarrow \mathbf{-15.5\text{ steps}}$

No numerical values are altered. Only the physical unit dimension is corrected to reflect the discrete-event nature of prequential streaming evaluation.

---

## 5. Certification of Resolution

`SWITCH_LATENCY_UNITS_RESOLVED = YES`

All downstream studies (including `LEBRE-V0.2-SHADOW-MULTIRATE-DECOMPOSITION-01`) shall express all recovery delays, discovery latencies, and switching tolerances strictly in **stream steps**.
