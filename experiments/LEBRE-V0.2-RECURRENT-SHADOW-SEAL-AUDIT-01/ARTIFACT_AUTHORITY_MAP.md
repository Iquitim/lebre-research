# Artifact Authority Map & Epistemic Hierarchy

**Stage ID:** `LEBRE-V0.2-RECURRENT-SHADOW-SEAL-AUDIT-01`  
**Milestone:** Forensic Seal Audit Authority Specification  

```mermaid
graph TD
    L1[Level 1: Sealed Raw Telemetry CSVs / JSON Logs] --> L2[Level 2: Executable Analysis & Simulation Code]
    L2 --> L3[Level 3: Frozen Preregistrations]
    L3 --> L4[Level 4: Frozen Selection Decisions]
    L4 --> L5[Level 5: Phase A Feasibility Artifacts]
    L5 --> L6[Level 6: Sealed Parent Final Reports]
    L6 --> L7[Level 7: Narrative Summaries & Walkthroughs]
    L7 --> L8[Level 8: Audit Prompt Assertions]
    L8 --> L9[Level 9: Ad-Hoc Interpretive Assumptions]
```

### Hierarchy Rules:
1. **Level 1 Overrides All:** Level-1 raw CSV telemetry (`RECURRENT_FINAL_RESULTS.csv`, `RECURRENT_DEV_RESULTS.csv`) represents physical stream truth. Narrative summaries, prompt text, or derived tables cannot alter raw execution values.
2. **Level 3 Binds Governance:** The pre-DEV frozen preregistration defines valid hypotheses and success criteria. Selection decisions at Level 4 that breach Level 3 criteria are invalid as confirmatory steps regardless of narrative text.
3. **No Retroactive Reinterpretation:** Higher levels cannot be modified retroactively to conform with lower-level narrative statements.
