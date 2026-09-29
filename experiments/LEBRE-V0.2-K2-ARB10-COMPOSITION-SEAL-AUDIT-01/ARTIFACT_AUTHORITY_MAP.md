# Artifact Authority Map

This audit strictly enforces the following 9-level authority hierarchy:

- **LEVEL 1:** `K2_ARB10_FINAL_RESULTS.csv` and raw event telemetry caches.
- **LEVEL 2:** Exact executable simulation and accounting code (`run_k2_arb10_composition.py`).
- **LEVEL 3:** Frozen `K2_ARB10_PREREGISTRATION.md`.
- **LEVEL 4:** Confirmatory configuration freeze (`K2_ARB10_CONFIRMATORY_FREEZE.md`).
- **LEVEL 5:** Deterministically generated analysis CSVs.
- **LEVEL 6:** `K2_ARB10_FINAL_REPORT.md`.
- **LEVEL 7:** Walkthroughs, executive summaries, and machine-readable summaries.
- **LEVEL 8:** Audit prompt.
- **LEVEL 9:** Informal assumptions.

A lower authority level can NEVER silently override a higher authority level.
