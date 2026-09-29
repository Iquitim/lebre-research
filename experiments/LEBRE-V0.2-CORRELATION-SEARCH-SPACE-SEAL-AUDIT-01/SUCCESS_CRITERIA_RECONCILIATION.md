# Success Criteria Reconciliation Matrix

**Study ID:** `LEBRE-V0.2-CORRELATION-SEARCH-SPACE-SEAL-AUDIT-01`  
**Milestone:** Forensic Success Criteria Reconciliation  
**Auditor:** Independent Skeptical Senior Scientific-Software Auditor  
**Date:** September 22, 2026  
**Status:** **AUDITED AGAINST LEVEL 3 PREREGISTRATION**  

---

## 1. Complete Preregistered Gate Reconciliation Table

| Mandatory Preregistered Gate | Target / Margin | Level 1 Confirmatory Result | Authoritative Gate Verdict |
| :--- | :--- | :--- | :--- |
| **G1: Total Online Compute Ceiling** | $\le 100.00\text{ FP/step}$ | **$111.013591\text{ FP/step}$** | **FAIL** |
| **G2: Predictive Non-Inferiority vs $R_0$**| Upper 95% CI $< +0.0100$ | **$+0.019403$** (Mean $\Delta = +0.013027$) | **FAIL** |
| **G3: Pure-Lag Preservation ($I_3, I_4, I_5, I_8$)**| Upper 95% CI $\le +0.0150$ | $I_3: +0.0642$ (**FAIL**)<br>$I_4: +0.0493$ (**FAIL**)<br>$I_5: +0.0348$ (**FAIL** on CI, mean $+0.0070$)<br>$I_8: +0.0250$ (**FAIL** on CI, mean $-0.0024$) | **FAIL** |
| **G4: Switching Adaptation Latency ($I_{11..14}$)**| Recovery $\Delta \le +50.0\text{ steps}$ | $I_{11}: +141.8\text{ steps}$ (**FAIL**)<br>$I_{12}: +280.0\text{ steps}$ (**FAIL**)<br>$I_{13}: +6.1\text{ steps}$ (**PASS**)<br>$I_{14}: +18.9\text{ steps}$ (**PASS**) | **FAIL** |
| **G5: Zero Dense 160-Cell Arrays in RAM**| Exactly $0$ dense arrays | Exactly **$0$ dense arrays** allocated | **PASS** |
| **G6: Search RAM Compaction** | $\le 200\text{ B}$ FP16, $\le 300\text{ B}$ state | **$192\text{ B}$** FP16, **$260\text{ B}$** total state | **PASS** |
| **G7: Anti-Starvation Revisit Guarantee** | Max silence $\le 80.0\text{ steps}$ | Max silence $= \mathbf{80.00\text{ steps}}$ | **PASS** |
| **G8: Hybrid Complementarity on $I_9$** | $G_{D\|B+R} > 0 \land G_{R\|B+D} > 0$ | $G_{D\|B+R} = +0.098, G_{R\|B+D} = +0.134$ | **PASS** |
| **G9: Canonical Code Immutability** | 0 edits to `src/` & `tests/` | 124/124 pytests passing, 0 edits | **PASS** |

---

## 2. Global Synthesis Adjudication

Under the literal rules of the frozen preregistration:
- A stage passes validation if and only if **ALL mandatory gates (G1..G9) pass simultaneously**.
- Because G1 (compute ceiling), G2 (predictive non-inferiority), G3 (pure-lag preservation), and G4 (switching preservation) failed:
```text
GLOBAL_SEARCH_COMPACTION_VALIDATION = FAILED
CORRELATION_SEARCH_SPACE_COMPACTION_SUPPORTED = NO
```
The sparse frontier is a **promising, memory-efficient experimental candidate** that improves on dense multirate $R_1$, but it is **not a validated replacement** for the continuous reference $R_0$.
