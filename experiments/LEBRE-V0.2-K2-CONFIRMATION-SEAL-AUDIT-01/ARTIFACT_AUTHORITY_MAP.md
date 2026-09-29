# Artifact Authority Map: Forensic Seal Audit

| Hierarchy Level | Artifact Name | Scope / Role | Authority Rule |
|:---|:---|:---|:---|
| **LEVEL 1** | `K2_FINAL_RESULTS.csv`, `K2_STATE_TRAJECTORY_ANALYSIS.csv` | Raw prequential telemetry & synchronized state traces | Supreme empirical ground truth. Overrides all lower levels. |
| **LEVEL 2** | `run_k2_confirmation.py`, `generate_k2_confirmation_outputs.py` | Executable simulation & calculation code | Mechanistic truth for FLOP/int-op logging and statistical recipes. |
| **LEVEL 3** | `K2_CONFIRMATION_PREREGISTRATION.md`, `K2_CONFIRMATION_PROTOCOL.md` | Preregistered hypotheses, margins, and decision gates | Frozen inferential rules and gate definitions. |
| **LEVEL 4** | `K2_CONFIRMATORY_FREEZE.md` | Freezing declaration and invariant commitments | Architectural boundaries and frozen parameters. |
| **LEVEL 5** | Deterministic analysis CSVs (`K2_SEED_LEVEL_NONINFERIORITY.csv`, etc.) | Derived analytical tables | Subordinate to Level 1. Must reproduce Level 1 exactly. |
| **LEVEL 6** | `K2_CONFIRMATION_FINAL_REPORT.md`, Decision MDs | Narrative summary reports | Textual reporting. Subordinate to Level 1 & 5. Subject to corrigenda. |
| **LEVEL 7** | Walkthrough & Executive Summaries | High-level synthesis | Explanatory context. |
| **LEVEL 8** | Audit Prompt & User Requests | External audit instructions | Targets for verification, not pre-assumed facts. |
| **LEVEL 9** | Informal Assumptions / Uncited Sketches | Heuristic commentary | Zero evidentiary weight. |
