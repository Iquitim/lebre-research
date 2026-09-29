# B7 vs B7_E0: Static Configuration & Source Code Diff Audit
## Audit of Variant Construction, Execution Logic, and Mapping

**Stage:** `DYNAMIC-LAG-LIFECYCLE-01A`  
**Inspected Source Files:**
- `scratch/run_dynamic_lag_lifecycle_01.py`
- `scratch/generate_dynamic_lag_reports.py`
- `experiments/DYNAMIC-LAG-LIFECYCLE-01/DYNAMIC_LAG_LIFECYCLE_01_VARIANT_SPECS.md`

---

## 1. Line-by-Line Configuration Diff

In `scratch/run_dynamic_lag_lifecycle_01.py`:

```python
# Lines 571-577:
elif variant in ["B7_PROPOSED_DYNAMIC_LAG_LIFECYCLE", "B7_E0_MAGNITUDE_EVICTION"]:
    evict_mode = "E0_MAGNITUDE" if variant == "B7_E0_MAGNITUDE_EVICTION" else "E2_TWO_TIMESCALE_OBSOLESCENCE"
    model = DynamicLagLifecycleModel(
        d_features=D, l_max=L_MAX, k_max=K_MAX,
        probe_rate=2, eviction_mode=evict_mode,
        include_recurrence=True
    )
```

### Exact Parameter Differences:
| Hyperparameter / Field | Variant B7 (`B7_PROPOSED_DYNAMIC_LAG_LIFECYCLE`) | Variant B7_E0 (`B7_E0_MAGNITUDE_EVICTION`) | Difference Status |
| :--- | :--- | :--- | :--- |
| `variant` string | `"B7_PROPOSED_DYNAMIC_LAG_LIFECYCLE"` | `"B7_E0_MAGNITUDE_EVICTION"` | Distinct |
| `eviction_mode` | `"E2_TWO_TIMESCALE_OBSOLESCENCE"` | `"E0_MAGNITUDE"` | **The Single Configuration Difference** |
| `d_features` ($D$) | 5 | 5 | Identical |
| `l_max` ($L_{\max}$) | 32 | 32 | Identical |
| `k_max` ($K_{\max}$) | 2 | 2 | Identical |
| `probe_rate` ($M$) | 2 | 2 | Identical |
| `include_recurrence` | True | True | Identical |
| `mu_base` | 0.05 | 0.05 | Identical |
| `mu_lag` | 0.05 | 0.05 | Identical |
| `theta_promote` | 0.15 | 0.15 | Identical |
| `theta_evict` | 0.015 | 0.015 | Identical |

---

## 2. Answers to the 10 Required Static Audit Questions

1. **Which parameter/configuration value distinguishes them?**  
   The constructor parameter `eviction_mode: str`. B7 receives `"E2_TWO_TIMESCALE_OBSOLESCENCE"`, while B7_E0 receives `"E0_MAGNITUDE"`.

2. **Which source branch consumes that value?**  
   In `DynamicLagLifecycleModel.step()`, lines 221–242:
   ```python
   # Eviction check
   if self.eviction_mode == "E0_MAGNITUDE":
       if abs(tap['w']) < 0.05:
           tap['zero_count'] += 1
       else:
           tap['zero_count'] = 0
       if tap['zero_count'] > 50 and tap['age'] > 100:
           self.events.append({
               'step': t, 'event_type': 'ACTIVE_TO_EVICTED',
               'i': tap['i'], 'k': tap['k'], 'evidence': tap['R']
           })
           tap['evict'] = True
   else: # E2 Two-Timescale Relevance + Obsolescence Gate
       if tap['R'] < self.theta_evict and tap['age'] > 300:
           # Check signal presence (obsolescence vs quiescence)
           if abs(val) > 0.1: # non-quiescent, truly obsolete
               self.events.append({
                   'step': t, 'event_type': 'ACTIVE_TO_EVICTED',
                   'i': tap['i'], 'k': tap['k'], 'evidence': tap['R']
               })
               tap['evict'] = True
   ```

3. **Does execution actually enter different eviction logic?**  
   **YES.** Execution executes the `if self.eviction_mode == "E0_MAGNITUDE":` branch for B7_E0 and the `else:` branch for B7.

4. **Are relevance statistics updated differently?**  
   **NO.** In lines 215–218, both variants execute:
   ```python
   if abs(val) > 0.1:
       tap['R'] = 0.999 * tap['R'] + 0.001 * marginal_gain
   ```
   Relevance $R$ is tracked identically in both variants; however, B7 uses $R$ and $|val| > 0.1$ for eviction, whereas B7_E0 checks $|w| < 0.05$ and `zero_count > 50`.

5. **Are eviction counters updated differently?**  
   **YES.** B7_E0 increments and resets `tap['zero_count']` based on $|w| < 0.05$. B7 does not maintain `zero_count`.

6. **Are active-tap deletion conditions different?**  
   **YES.** B7_E0 evicts when `tap['zero_count'] > 50 and tap['age'] > 100`. B7 evicts when `tap['R'] < 0.015 and tap['age'] > 300 and abs(val) > 0.1`.

7. **Are both variants accidentally mapped to the same class/config?**  
   **NO.** They instantiate `DynamicLagLifecycleModel` with different `eviction_mode` arguments.

8. **Is B7_E0 merely a renamed B7 instance?**  
   **NO.** The source code contains distinct conditional logic for B7_E0.

9. **Does aggregation accidentally read B7 results for B7_E0?**  
   **NO.** In `DYNAMIC_LAG_LIFECYCLE_01_SEED_RESULTS.csv`, B7 and B7_E0 have distinct rows with distinct values on D7 (4 seeds differ in raw NMSE).

10. **Does report generation map two variant labels to the same result row?**  
    **YES.** In `scratch/generate_dynamic_lag_reports.py`, line 547:
    The markdown table generation hardcoded the formatted string for B7 into the B7_E0 row:
    ```python
    | **B7: Proposed Dynamic Lag** | Structural Lifecycle | **0.4164** [0.407, 0.426] | **0.5820** | **0.7544** | **0.4091** | **0.9120** | **82.0** | **984 B** | **1.25** | **Edge-Compliant Winner** |
    | **B7: Magnitude Eviction** | Instantaneous Pruning | 0.4164 [0.407, 0.426] | 0.5820 | 0.7544 | 0.4091 | 0.9120 | 82.0 | 984 B | 1.25 | Eviction Control |
    ```
    This was an explicit string copy-paste in report generation, completely masking the actual computed seed results of B7_E0.
